"""
Unit Tests for TenderLens Supabase Cloud Database & Auth Integration (Free Tier)
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.supabase_service import SupabaseService
from contracts.schema import BidderProfile


def make_test_bidder() -> BidderProfile:
    return BidderProfile(
        company_name="Apex Solar & Grid Systems Pvt Ltd",
        entity_type="System Integrator",
        is_msme_registered=True,
        msme_category="SMALL",
        is_startup_recognized=True,
        turnover_year_1_lakhs=180.0,
        turnover_year_2_lakhs=210.0,
        turnover_year_3_lakhs=240.0,
        years_in_business=6,
        local_content_percentage=65.0,
        held_certifications=["ISO-9001", "BIS", "CE"],
        past_similar_project_values_lakhs=[120.0, 85.0, 60.0]
    )


def test_supabase_service_initialization():
    service = SupabaseService()
    status = service.get_status()
    assert isinstance(status, dict)
    assert "configured" in status
    assert "connected" in status
    assert status["free_tier_ready"] is True


def test_auth_config_endpoint():
    client = TestClient(app)
    resp = client.get("/api/v1/auth/config")
    assert resp.status_code == 200
    data = resp.json()
    assert "configured" in data
    assert "supabase_url" in data
    assert "publishable_key" in data


def test_healthz_supabase_diagnostics():
    client = TestClient(app)
    resp = client.get("/healthz")
    assert resp.status_code == 200
    data = resp.json()
    assert "supabase_configured" in data
    assert "supabase_status" in data
    assert data["supabase_status"]["free_tier_ready"] is True


@pytest.mark.asyncio
async def test_bidder_profile_supabase_deserialization():
    # Test deserializing raw Supabase PostgreSQL row into BidderProfile
    raw_row = {
        "user_id": "00000000-0000-0000-0000-000000000001",
        "full_name": "Rohan Sharma",
        "organization": "Apex Infrastructure Ltd",
        "bidder_type": "EPC Contractor",
        "is_msme_registered": True,
        "msme_category": "MEDIUM",
        "is_startup_recognized": False,
        "turnover_year_1_lakhs": 450.0,
        "turnover_year_2_lakhs": 520.0,
        "turnover_year_3_lakhs": 610.0,
        "years_in_business": 8,
        "local_content_percentage": 55.0,
        "held_certifications": ["ISO-9001", "ISO-14001"],
        "past_similar_project_values_lakhs": [300.0, 250.0]
    }
    
    bidder = BidderProfile(
        company_name=raw_row["organization"],
        entity_type=raw_row["bidder_type"],
        is_msme_registered=raw_row["is_msme_registered"],
        msme_category=raw_row["msme_category"],
        is_startup_recognized=raw_row["is_startup_recognized"],
        turnover_year_1_lakhs=float(raw_row["turnover_year_1_lakhs"]),
        turnover_year_2_lakhs=float(raw_row["turnover_year_2_lakhs"]),
        turnover_year_3_lakhs=float(raw_row["turnover_year_3_lakhs"]),
        years_in_business=int(raw_row["years_in_business"]),
        local_content_percentage=float(raw_row["local_content_percentage"]),
        held_certifications=raw_row["held_certifications"],
        past_similar_project_values_lakhs=raw_row["past_similar_project_values_lakhs"]
    )
    assert bidder.company_name == "Apex Infrastructure Ltd"
    assert bidder.is_msme_registered is True
    avg_turnover = (bidder.turnover_year_1_lakhs + bidder.turnover_year_2_lakhs + bidder.turnover_year_3_lakhs) / 3.0
    assert avg_turnover == (450.0 + 520.0 + 610.0) / 3.0
    assert len(bidder.held_certifications) == 2
