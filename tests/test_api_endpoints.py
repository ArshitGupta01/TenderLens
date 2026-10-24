"""
TenderLens - Test Suite: FastAPI Endpoints
==========================================
Tests REST endpoints, health check, and scorecard evaluation payload contracts.
"""

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_check_endpoint():
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "TenderLens Backend Engine"


def test_audit_evaluation_endpoint():
    payload = {
        "tender_id": "GEM-2026-TEST",
        "tender_title": "Installation of 100kW Rooftop Solar System",
        "tender_url": "https://gem.gov.in/tender/sample",
        "source_portal": "GeM",
        "bidder_profile": {
            "company_name": "Bharat Renewable Energy Ltd",
            "entity_type": "OEM",
            "is_msme_registered": True,
            "msme_category": "SMALL",
            "turnover_year_1_lakhs": 150.0,
            "turnover_year_2_lakhs": 160.0,
            "turnover_year_3_lakhs": 170.0,
            "years_in_business": 4,
            "local_content_percentage": 75.0,
            "held_certifications": ["ISO-9001", "BIS"]
        },
        "explicit_criteria": {
            "min_annual_turnover_lakhs": 100.0,
            "min_experience_years": 3,
            "emd_amount_inr": 25000.0,
            "min_local_content_percentage": 50.0,
            "mandatory_certifications": ["ISO-9001"]
        }
    }

    response = client.post("/api/v1/audit/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["tender_id"] == "GEM-2026-TEST"
    assert data["recommendation"] == "STRONG_BID"
    assert data["score"] >= 4.0
    assert len(data["deterministic_gates"]) == 6
