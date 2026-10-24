"""Find public references on explicit request; never invent historical rates or partners."""

import logging
from typing import Optional

from contracts.schema import CompetitorForensicsReport, HistoricalDisqualificationPattern
from backend.services.tinyfish_service import TinyFishService

logger = logging.getLogger("tenderlens.forensics")


class CompetitorForensicsEngine:
    @staticmethod
    def analyze_static_forensics(tender_title: str, source_portal: str) -> CompetitorForensicsReport:
        return CompetitorForensicsReport(
            target_authority=source_portal or "Not specified",
            source_portal=source_portal,
            historical_patterns=[],
            strategic_bid_advice=(
                "No verified historical evaluation dataset is connected. TenderLens makes no rejection-frequency claim. "
                "Use the official tender, corrigenda and published evaluation records as the source of truth."
            ),
        )

    @classmethod
    async def analyze_with_live_archives(
        cls,
        tender_title: str,
        source_portal: str,
        tinyfish: Optional[TinyFishService] = None,
    ) -> CompetitorForensicsReport:
        report = cls.analyze_static_forensics(tender_title, source_portal)
        if not tinyfish:
            return report

        try:
            query = f'"{tender_title[:80]}" tender technical evaluation result disqualification'
            results = await tinyfish.search_tenders(
                query=query,
                purpose="Find public procurement evaluation records for human review. Return source URLs; do not infer rejection statistics.",
                limit=5,
            )
            report.historical_patterns = [
                HistoricalDisqualificationPattern(
                    authority_or_portal=item.source_portal or source_portal,
                    common_rejection_trigger=(item.title[:140] or item.snippet[:140] or "Public search result"),
                    historical_frequency_weight="UNVERIFIED_SEARCH_RESULT",
                    defensive_countermeasure="Open the source, confirm it is an official evaluation record, and check its date and tender identity.",
                    reference_source=item.url,
                )
                for item in results[:5]
                if item.url.startswith("https://")
            ]
            report.strategic_bid_advice = (
                "These are public search results, not a verified historical dataset. Open each source and confirm the authority, tender identity and date before using it."
            )
        except Exception as error:
            logger.info("Public evaluation-record search unavailable: %s", error)

        return report
