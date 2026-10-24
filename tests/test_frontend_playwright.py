"""
TenderLens - Frontend Playwright Functional Verification Test
=============================================================
Tests that all core user-facing pages load with zero tech-stack clutter,
no developer installation guidelines, and that interactive scenario presets work.
"""

import time
import threading
from pathlib import Path
from http.server import SimpleHTTPRequestHandler
import socketserver
import pytest
from playwright.sync_api import sync_playwright

ROOT_DIR = Path(__file__).resolve().parent.parent
PORT = 8799


class QuietHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT_DIR), **kwargs)

    def log_message(self, format, *args):
        pass


@pytest.fixture(scope="session")
def frontend_server():
    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer(("", PORT), QuietHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(1.0)
    yield f"http://localhost:{PORT}"
    server.shutdown()


def test_index_clean_ux_no_tech_stack_clutter(frontend_server):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto(f"{frontend_server}/index.html", wait_until="networkidle", timeout=15000)

        # Assert no annoying tech stack section
        assert page.locator("#tech-stack").count() == 0, "Found unwanted #tech-stack section on index.html"
        assert page.locator(".pipeline-interactive-bench").count() == 0, "Found unwanted .pipeline-interactive-bench"

        # Assert clean user navigation
        assert page.locator("a[href='strategy.html']").count() > 0
        assert page.locator("a[href='guide.html']").count() > 0

        browser.close()


def test_guide_pure_user_tools_no_dev_commands(frontend_server):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto(f"{frontend_server}/guide.html", wait_until="networkidle", timeout=15000)

        body_text = page.locator("body").inner_text()
        # Assert complete absence of internal dev instructions
        assert "uv run uvicorn" not in body_text, "Found 'uv run uvicorn' in guide.html"
        assert "setup.sql" not in body_text, "Found 'setup.sql' in guide.html"
        assert "localhost:4177" not in body_text, "Found 'localhost:4177' in guide.html"

        # Assert presence of Statutory Startup Shield & MSE Quota sections
        assert "STARTUP EXEMPTION" in body_text.upper()
        assert "MSE SUBCONTRACTING" in body_text.upper()

        browser.close()


def test_strategy_preset_and_precedence_rag(frontend_server):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto(f"{frontend_server}/strategy.html", wait_until="networkidle", timeout=15000)

        # Assert preset scenario buttons exist and trigger cleanly
        preset_btn = page.locator("#preset-hackathon-demo, [data-load-zero-history-preset], .preset-btn")
        assert preset_btn.count() > 0, "Scenario preset buttons missing"
        preset_btn.first.click()
        time.sleep(0.5)

        # Assert Precedence DAG section exists
        assert page.locator("#precedence-rag-workbench").count() > 0

        browser.close()
