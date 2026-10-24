"""
TenderLens - Celery Asynchronous Task Orchestration
===================================================
Manages background job queues for tender ingestion, recursive ATC crawling,
and intensive LLM / statutory verification pipelines.
"""

import os
import logging
from celery import Celery

logger = logging.getLogger("tenderlens.celery")

broker_url = os.getenv("CELERY_BROKER_URL", os.getenv("REDIS_URL", "redis://localhost:6379/0"))
result_backend = os.getenv("CELERY_RESULT_BACKEND", os.getenv("REDIS_URL", "redis://localhost:6379/1"))

celery_app = Celery(
    "tenderlens",
    broker=broker_url,
    backend=result_backend
)

# Resilient Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max
    task_soft_time_limit=240,
    task_always_eager=os.getenv("CELERY_ALWAYS_EAGER", "false").lower() in ("true", "1")
)


@celery_app.task(bind=True, name="tasks.async_evaluate_tender")
def async_evaluate_tender(self, payload: dict):
    """
    Executes the 5-step qualification evaluation asynchronously.
    Updates Celery task state for frontend progress tracking.
    """
    import asyncio
    from contracts.schema import BidderProfile
    from backend.engine.deterministic_gatekeeper import TenderStatutoryCriteria
    from backend.engine.qualification_engine import QualificationEngine

    self.update_state(state="PROGRESS", meta={"stage": "STAGE_1_INITIALIZING", "percent": 15})

    bidder = BidderProfile(**payload["bidder_profile"])
    criteria = TenderStatutoryCriteria(**payload["criteria"]) if payload.get("criteria") else None

    self.update_state(state="PROGRESS", meta={"stage": "STAGE_4_DETERMINISTIC_GATES", "percent": 65})

    scorecard = QualificationEngine.evaluate_tender(
        tender_id=payload.get("tender_id", "BID-ASYNC"),
        tender_title=payload.get("tender_title", "Async Tender"),
        source_portal=payload.get("source_portal", "GeM"),
        bidder_profile=bidder,
        chunks=[],
        explicit_criteria=criteria
    )

    self.update_state(state="SUCCESS", meta={"stage": "STAGE_5_COMPLETE", "percent": 100})
    return scorecard.model_dump()


@celery_app.task(bind=True, name="tasks.async_crawl_tender_documents")
def async_crawl_tender_documents(self, seed_url: str, max_depth: int = 2):
    """
    Asynchronously crawls seed tender and linked child ATCs via TinyFetch.
    """
    import asyncio
    from backend.services.tinyfish_service import TinyFishService

    self.update_state(state="PROGRESS", meta={"message": f"Fetching {seed_url} via TinyFetch..."})
    svc = TinyFishService()

    async def _crawl():
        return await svc.fetch_tender_recursive(seed_url=seed_url, max_depth=max_depth)

    docs = asyncio.run(_crawl())
    return [d.model_dump() for d in docs]
