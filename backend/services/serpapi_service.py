"""
TenderLens - SerpAPI Search Fallback Service
============================================
Provides public Google Search fallback for Indian government procurement portals
(gem.gov.in, eprocure.gov.in, bhel.com) using SerpAPI.
"""

import os
import logging
from typing import List, Optional
import httpx
from pydantic import BaseModel

logger = logging.getLogger("tenderlens.serpapi")


class DiscoveredTender(BaseModel):
    title: str
    url: str
    snippet: str
    source_portal: str
    bid_number: Optional[str] = None
    published_date: Optional[str] = None


class SerpAPIService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SERPAPI_API_KEY", "")
        self.endpoint = "https://serpapi.com/search.json"

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and not self.api_key.startswith("your-serpapi-key"))

    async def search_tenders(
        self,
        query: str,
        portal: str = "gem.gov.in",
        limit: int = 5
    ) -> List[DiscoveredTender]:
        """
        Executes Google search via SerpAPI targeted to Indian procurement portals.
        """
        if not self.is_configured:
            logger.debug("SerpAPI key not configured; skipping SerpAPI fallback.")
            return []

        search_query = f"{query} site:{portal}"
        params = {
            "q": search_query,
            "engine": "google",
            "gl": "in",
            "hl": "en",
            "num": limit,
            "api_key": self.api_key
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(self.endpoint, params=params)
                if resp.status_code != 200:
                    logger.warning("SerpAPI error status %s: %s", resp.status_code, resp.text[:200])
                    return []
                data = resp.json()

            results: List[DiscoveredTender] = []
            for item in data.get("organic_results", [])[:limit]:
                results.append(DiscoveredTender(
                    title=item.get("title", "Tender Document"),
                    url=item.get("link", ""),
                    snippet=item.get("snippet", ""),
                    source_portal=f"SerpAPI ({portal})"
                ))
            return results

        except Exception as e:
            logger.error("SerpAPI search failed: %s", e)
            return []


# Global singleton
serpapi_service = SerpAPIService()
