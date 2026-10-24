"""
TenderLens - Supabase Cloud Database & Auth Service (Free Tier)
==============================================================
Provides server-side PostgreSQL database persistence for:
1. Bidder Profiles (financial capacity, MSME status, certifications)
2. Tender Qualification Audit Scorecards & Pre-Bid Strategy Reports
3. Saved Tenders Bookmarks

Designed specifically for Supabase Free Tier projects:
- Zero monolith PostgreSQL setup required
- Uses PostgREST REST API and Supabase-py client
- Respects Row Level Security (RLS) policies
"""

import logging
from typing import Optional, List, Dict, Any
from backend.config import settings
from contracts.schema import BidderProfile, QualificationScorecard

logger = logging.getLogger("tenderlens.supabase")


class SupabaseService:
    """Singleton service wrapping Supabase client operations."""

    def __init__(self):
        self._client = None
        self._initialized = False

    def get_client(self):
        """Lazily initialize and return Supabase Client."""
        if not self._initialized:
            self._initialized = True
            if settings.is_supabase_configured:
                try:
                    from supabase import create_client, Client
                    key = (settings.SUPABASE_SERVICE_ROLE_KEY or settings.supabase_public_key)
                    self._client: Optional[Client] = create_client(settings.SUPABASE_URL, key)
                    logger.info("Supabase client initialized successfully with project URL %s", settings.SUPABASE_URL)
                except Exception as e:
                    logger.warning("Failed to initialize Supabase client: %s", e)
                    self._client = None
            else:
                logger.info("Supabase is not configured yet. Set SUPABASE_URL and SUPABASE_ANON_KEY in .env")
                self._client = None
        return self._client

    @property
    def is_available(self) -> bool:
        """Returns True if Supabase is properly configured and reachable."""
        return self.get_client() is not None

    def get_status(self) -> Dict[str, Any]:
        """Returns diagnostic status of the Supabase connection."""
        configured = settings.is_supabase_configured
        has_client = self.is_available
        return {
            "configured": configured,
            "connected": has_client,
            "supabase_url": settings.SUPABASE_URL if configured else "",
            "has_service_key": bool(settings.SUPABASE_SERVICE_ROLE_KEY),
            "free_tier_ready": True
        }

    async def save_audit_scorecard(
        self,
        user_id: str,
        scorecard: QualificationScorecard,
        tender_title: str,
        tender_url: str,
        source_portal: str = "GeM"
    ) -> Optional[Dict[str, Any]]:
        """
        Persists a completed QualificationScorecard report into Supabase `tender_audits` table.
        """
        client = self.get_client()
        if not client:
            logger.debug("Skipping Supabase audit persistence (unconfigured)")
            return None

        try:
            row = {
                "user_id": user_id,
                "tender_id": scorecard.tender_id or "",
                "tender_title": (tender_title or scorecard.tender_title or "Untitled Tender")[:240],
                "tender_url": (tender_url or "")[:2048],
                "source_portal": (source_portal or scorecard.source_portal or "GeM")[:120],
                "recommendation": scorecard.recommendation,
                "qualification_score": float(scorecard.score),
                "scorecard_data": scorecard.model_dump(mode="json")
            }
            res = client.table("tender_audits").insert(row).execute()
            if res.data:
                logger.info("Successfully persisted audit scorecard for user %s to Supabase", user_id)
                return res.data[0]
            return None
        except Exception as e:
            logger.error("Failed to save audit scorecard to Supabase: %s", e)
            return None

    async def get_user_audits(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Retrieves historical saved audits for an authenticated user.
        """
        client = self.get_client()
        if not client:
            return []

        try:
            res = client.table("tender_audits") \
                .select("id, tender_id, tender_title, tender_url, source_portal, recommendation, qualification_score, created_at, scorecard_data") \
                .eq("user_id", user_id) \
                .order("created_at", desc=True) \
                .limit(limit) \
                .execute()
            return res.data or []
        except Exception as e:
            logger.error("Failed to query user audits from Supabase: %s", e)
            return []

    async def get_bidder_profile(self, user_id: str) -> Optional[BidderProfile]:
        """
        Loads the stored BidderProfile for an authenticated user from the `profiles` table.
        """
        client = self.get_client()
        if not client:
            return None

        try:
            res = client.table("profiles").select("*").eq("user_id", user_id).maybe_single().execute()
            if not res or not res.data:
                return None

            data = res.data
            return BidderProfile(
                company_name=data.get("organization") or data.get("full_name") or "Saved Bidder Profile",
                entity_type=data.get("bidder_type") or "System Integrator",
                is_msme_registered=bool(data.get("is_msme_registered", False)),
                msme_category=data.get("msme_category") or None,
                is_startup_recognized=bool(data.get("is_startup_recognized", False)),
                turnover_year_1_lakhs=float(data.get("turnover_year_1_lakhs") or 0.0),
                turnover_year_2_lakhs=float(data.get("turnover_year_2_lakhs") or 0.0),
                turnover_year_3_lakhs=float(data.get("turnover_year_3_lakhs") or 0.0),
                years_in_business=int(data.get("years_in_business") or 0),
                local_content_percentage=float(data.get("local_content_percentage") or 50.0),
                held_certifications=list(data.get("held_certifications") or []),
                past_similar_project_values_lakhs=list(data.get("past_similar_project_values_lakhs") or [])
            )
        except Exception as e:
            logger.error("Failed to fetch bidder profile from Supabase: %s", e)
            return None

    async def save_bidder_profile(
        self,
        user_id: str,
        profile: BidderProfile,
        full_name: str = "",
        region: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        Saves or updates a BidderProfile into Supabase `profiles` table.
        """
        client = self.get_client()
        if not client:
            return None

        try:
            row = {
                "user_id": user_id,
                "full_name": full_name[:100] if full_name else profile.company_name[:100],
                "organization": profile.company_name[:100],
                "bidder_type": profile.entity_type[:60],
                "years_active": f"{profile.years_in_business} years"[:40],
                "region": region[:60],
                "is_msme_registered": profile.is_msme_registered,
                "msme_category": profile.msme_category or "",
                "is_startup_recognized": profile.is_startup_recognized,
                "turnover_year_1_lakhs": profile.turnover_year_1_lakhs,
                "turnover_year_2_lakhs": profile.turnover_year_2_lakhs,
                "turnover_year_3_lakhs": profile.turnover_year_3_lakhs,
                "years_in_business": profile.years_in_business,
                "local_content_percentage": profile.local_content_percentage,
                "held_certifications": profile.held_certifications,
                "past_similar_project_values_lakhs": profile.past_similar_project_values_lakhs
            }
            res = client.table("profiles").upsert(row, on_conflict="user_id").execute()
            if res.data:
                logger.info("Successfully synced bidder profile for user %s to Supabase", user_id)
                return res.data[0]
            return None
        except Exception as e:
            logger.error("Failed to save bidder profile to Supabase: %s", e)
            return None
