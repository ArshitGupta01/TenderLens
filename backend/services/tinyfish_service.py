"""
TenderLens - Web Intelligence Layer: TinyFish Service
=====================================================
Orchestrates TinySearch, TinyFetch Recursive, and TinyAgent Stealth SSE
following exact production specifications and cost circuit breakers.
"""

import os
import json
import logging
import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator, Set
from pydantic import BaseModel, Field
import httpx

from backend.config import settings

logger = logging.getLogger("tenderlens.tinyfish")

SEARCH_ENDPOINT = "https://api.search.tinyfish.ai"
FETCH_ENDPOINT = "https://api.fetch.tinyfish.ai"
AGENT_SSE_ENDPOINT = "https://agent.tinyfish.ai/v1/automation/run-sse"


class DiscoveredTender(BaseModel):
    title: str
    url: str
    snippet: str
    source_portal: str
    bid_number: Optional[str] = None
    published_date: Optional[str] = None


class FetchedDocument(BaseModel):
    url: str
    content_markdown: str
    extracted_child_urls: List[str] = Field(default_factory=list)
    status_code: int = 200
    etag: Optional[str] = None
    last_modified: Optional[str] = None
    is_not_modified: bool = False
    error: Optional[str] = None


class TinyFishService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.TINYFISH_API_KEY
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": "TenderLens-Orchestrator/2.0"
        }

    async def search_tenders(
        self,
        query: str,
        purpose: Optional[str] = None,
        include_domains: Optional[str] = None,
        recency_minutes: Optional[int] = None,
        limit: int = 15
    ) -> List[DiscoveredTender]:
        """
        Stage 1: TinySearch API ($0.00 / call).
        Queries Indian public procurement portals.
        Production rules:
        - Never use 'site:' or '-site:' inside query. Use include_domains instead.
        - Rich 'purpose' parameter describing search intent.
        - Location strictly set to 'IN'.
        """
        params: Dict[str, Any] = {
            "query": query.replace("site:", ""),  # Enforce deprecation fix
            "location": settings.DEFAULT_LOCATION,
            "language": settings.DEFAULT_LANGUAGE,
            "include_domains": include_domains or settings.ALLOWED_DOMAINS
        }

        if purpose:
            params["purpose"] = purpose[:2000]

        if recency_minutes:
            params["recency_minutes"] = recency_minutes

        async with httpx.AsyncClient(timeout=25.0) as client:
            try:
                response = await client.get(
                    SEARCH_ENDPOINT,
                    headers={"X-API-Key": self.api_key, "User-Agent": "TenderLens-Orchestrator/2.0"},
                    params=params
                )
                if response.status_code == 401:
                    logger.error("TinySearch API returned 401 Unauthorized. Verify TINYFISH_API_KEY.")
                    return []
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                logger.error(f"TinySearch request failed: {e}")
                return []

        results: List[DiscoveredTender] = []
        for item in data.get("results", [])[:limit]:
            raw_url = item.get("url", "")
            portal = "Unknown"
            for domain in settings.ALLOWED_DOMAINS.split(","):
                if domain.strip() in raw_url:
                    portal = domain.strip()
                    break

            results.append(DiscoveredTender(
                title=item.get("title", ""),
                url=raw_url,
                snippet=item.get("snippet", ""),
                source_portal=portal
            ))
        return results

    async def fetch_batch(
        self,
        urls: List[str],
        etag_cache: Optional[Dict[str, str]] = None
    ) -> List[FetchedDocument]:
        """
        Fetches up to 10 URLs in a single stateless batch request via TinyFetch.
        Supports HTTP 304 TTL caching with etag/last_modified.
        """
        if not urls:
            return []

        batch_urls = urls[:settings.MAX_BATCH_URLS]
        payload: Dict[str, Any] = {
            "urls": batch_urls,
            "format": "markdown",
            "iframe_links": True,
            "include_etag_and_last_modified": True
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(FETCH_ENDPOINT, headers=self.headers, json=payload)
                if response.status_code == 401:
                    logger.error("TinyFetch API returned 401 Unauthorized.")
                    return [FetchedDocument(url=u, content_markdown="", error="401_UNAUTHORIZED") for u in batch_urls]
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                logger.error(f"TinyFetch batch request failed: {e}")
                return [FetchedDocument(url=u, content_markdown="", error=str(e)) for u in batch_urls]

        fetched_docs: List[FetchedDocument] = []
        atc_indicators = ["atc", "additional", "terms", "corrigendum", "amendment", "specification", ".pdf"]

        for item in data.get("results", []):
            url = item.get("url", "")
            markdown = item.get("markdown", "")
            raw_links = item.get("links", [])
            etag = item.get("etag")
            last_mod = item.get("last_modified")

            # Extract child URLs matching ATC / Corrigenda patterns
            child_atc_urls = [
                link for link in raw_links
                if any(ind in link.lower() for ind in atc_indicators) and link != url
            ]

            fetched_docs.append(FetchedDocument(
                url=url,
                content_markdown=markdown,
                extracted_child_urls=list(set(child_atc_urls)),
                status_code=item.get("status", 200),
                etag=etag,
                last_modified=last_mod,
                is_not_modified=item.get("not_modified", False)
            ))

        return fetched_docs

    async def fetch_tender_recursive(
        self,
        seed_url: str,
        max_depth: int = 2
    ) -> List[FetchedDocument]:
        """
        Stage 2: Recursive URL Queue ($0.00 / call).
        Retrieves seed tender and crawls discovered child ATCs and Corrigenda up to depth d <= max_depth.
        Deduplicates visited URLs and respects batch limit.
        """
        visited: Set[str] = set()
        queue: List[tuple[str, int]] = [(seed_url, 0)]
        all_documents: List[FetchedDocument] = []

        while queue:
            # Pop up to MAX_BATCH_URLS from the queue
            current_batch: List[tuple[str, int]] = []
            while queue and len(current_batch) < settings.MAX_BATCH_URLS:
                u, d = queue.pop(0)
                if u not in visited:
                    visited.add(u)
                    current_batch.append((u, d))

            if not current_batch:
                break

            urls_to_fetch = [item[0] for item in current_batch]
            batch_results = await self.fetch_batch(urls_to_fetch)
            all_documents.extend(batch_results)

            # Discover next hop links if within max_depth limit
            for doc, (_, depth) in zip(batch_results, current_batch):
                if depth < max_depth:
                    for child_url in doc.extracted_child_urls:
                        if child_url not in visited:
                            queue.append((child_url, depth + 1))

        return all_documents

    async def run_stealth_agent_stream(
        self,
        url: str,
        goal: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stage 3: TinyAgent Stealth SSE ($0.016 / step).
        Autonomous browser fallback with cost circuit breakers:
        - mode='strict'
        - max_steps=10
        - max_duration_seconds=60
        - proxy country_code='IN'
        Streams SSE events directly to client.
        """
        payload = {
            "url": url,
            "goal": goal,
            "browser_profile": "stealth",
            "proxy_config": {
                "enabled": True,
                "type": "tinyfish",
                "country_code": "IN"
            },
            "agent_config": {
                "mode": "strict",
                "max_steps": settings.TINYAGENT_MAX_STEPS,
                "max_duration_seconds": settings.TINYAGENT_MAX_DURATION_SECONDS
            }
        }

        async with httpx.AsyncClient(timeout=90.0) as client:
            try:
                async with client.stream("POST", AGENT_SSE_ENDPOINT, headers=self.headers, json=payload) as response:
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            raw_data = line[6:].strip()
                            if raw_data:
                                try:
                                    yield json.loads(raw_data)
                                except json.JSONDecodeError:
                                    yield {"type": "RAW_EVENT", "data": raw_data}
            except Exception as e:
                logger.error(f"TinyAgent SSE stream encountered error: {e}")
                yield {"type": "ERROR", "message": str(e)}
