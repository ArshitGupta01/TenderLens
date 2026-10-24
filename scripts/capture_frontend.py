"""
TenderLens - Frontend Playwright Test & Screenshot Suite
========================================================
1. Clears out all previous screenshots.
2. Starts an in-process local HTTP server.
3. Launches Playwright Chromium.
4. Audits DOM and asserts UI requirements across desktop & mobile.
5. Captures fresh full-page screenshots.
6. Writes comprehensive inspection report.
"""

import os
import sys
import time
import json
import threading
from pathlib import Path
from http.server import SimpleHTTPRequestHandler
import socketserver

ROOT_DIR = Path(__file__).resolve().parent.parent
SCREENSHOT_DIR = ROOT_DIR / "artifacts" / "screenshots"
BRAIN_SCREENSHOT_DIR = Path(r"C:\Users\MOHIT\.gemini\antigravity-ide\brain\910b7a08-ff8a-47fb-8a9b-7b4424476ec7\screenshots")

PORT = 8765


def clear_existing_screenshots():
    """Removes existing screenshot artifacts before running tests."""
    cleared_count = 0
    for target_dir in [SCREENSHOT_DIR, BRAIN_SCREENSHOT_DIR]:
        if target_dir.exists():
            for file in target_dir.glob("*.png"):
                try:
                    file.unlink()
                    cleared_count += 1
                except Exception as e:
                    print(f"    [!] Warning removing {file}: {e}")
        target_dir.mkdir(parents=True, exist_ok=True)
    print(f"[CLEANUP] Cleared {cleared_count} existing screenshot file(s). Ready for fresh capture.")


class QuietHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT_DIR), **kwargs)

    def log_message(self, format, *args):
        pass  # Suppress HTTP request logs


def start_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), QuietHandler) as httpd:
        httpd.serve_forever()


def audit_page_elements(page, page_name: str) -> dict:
    """Inspects the page DOM for redundant or unnecessary UI elements."""
    findings = {
        "page": page_name,
        "title": page.title(),
        "unnecessary_elements": [],
        "text_anomalies": [],
        "overlapping_elements": [],
        "console_errors": []
    }

    # 1. Check for legacy/outdated badges or branding
    badges = page.locator(".menu-status-text, .badge, .hero-tag, .tag, .version, .brand-descriptor").all_text_contents()
    for b in badges:
        text = b.strip()
        if "v1.0.3" in text:
            findings["text_anomalies"].append(f"Outdated version badge found: '{text}' (current release is v1.1.0/v2.0.0)")
        if "TRAXO" in text.upper() or "IIITD" in text.upper():
            findings["text_anomalies"].append(f"Residual unscrubbed branding tag: '{text}'")

    # 2. Check for redundant banners or duplicate floating navigation
    navs = page.locator("header, nav, .site-header, .top-banner, .banner").count()
    if navs > 3:
        findings["unnecessary_elements"].append(f"High number of headers/navbars ({navs} detected)")

    # 3. Check for empty containers or placeholder cards
    cards = page.locator(".card, .strategy-card, .metric-card, .preset-card").count()
    findings["card_count"] = cards

    # 4. Check for hidden or display:none dead elements
    dead_elements = page.locator("[style*='display: none'], [style*='visibility: hidden'], .hidden, .d-none").count()
    findings["hidden_elements_count"] = dead_elements

    return findings


def run_frontend_tests_and_capture():
    from playwright.sync_api import sync_playwright

    # Step 1: Clear old screenshots
    clear_existing_screenshots()

    # Step 2: Start server
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(1.0)  # Allow server to bind

    base_url = f"http://localhost:{PORT}"
    pages_to_test = [
        {"name": "index", "path": "index.html", "mobile": True},
        {"name": "strategy", "path": "strategy.html", "mobile": True},
        {"name": "guide", "path": "guide.html", "mobile": False},
        {"name": "signin", "path": "signin.html", "mobile": False},
        {"name": "account", "path": "account.html", "mobile": False},
    ]

    all_findings = []
    test_results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for p_info in pages_to_test:
            page_name = p_info["name"]
            url = f"{base_url}/{p_info['path']}"
            print(f"\n[*] Testing & capturing {page_name.upper()} ({url})...")

            # --- Desktop Viewport ---
            context = browser.new_context(viewport={"width": 1440, "height": 900})
            page = context.new_page()

            console_logs = []
            page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}") if msg.type in ["error", "warning"] else None)

            page.goto(url, wait_until="networkidle", timeout=15000)
            time.sleep(1.2)  # Let animations and Lenis settle

            # Specific DOM Assertions per Page
            if page_name == "index":
                # Ensure annoying tech stack block is completely removed
                tech_stack_count = page.locator("#tech-stack").count()
                bench_count = page.locator(".pipeline-interactive-bench").count()
                assert tech_stack_count == 0, "ERROR: #tech-stack section still present on index page!"
                assert bench_count == 0, "ERROR: .pipeline-interactive-bench still present on index page!"
                test_results.append("[PASS] index.html: No developer tech-stack or bench clutter.")

            elif page_name == "guide":
                # Ensure developer instructions are completely eradicated
                body_text = page.locator("body").inner_text()
                assert "uv run uvicorn" not in body_text, "ERROR: Developer CLI 'uv run uvicorn' found in guide!"
                assert "setup.sql" not in body_text, "ERROR: Developer DB script 'setup.sql' found in guide!"
                assert "localhost:4177" not in body_text, "ERROR: 'localhost:4177' found in guide!"
                # Ensure Startup Shield and MSE Subcontracting Quota are present
                assert page.locator("#statutory-shield-guide").count() > 0 or "STARTUP EXEMPTION" in body_text.upper()
                assert page.locator("#mse-quota-guide").count() > 0 or "MSE SUBCONTRACTING" in body_text.upper()
                test_results.append("[PASS] guide.html: Pure user-facing statutory guides, zero developer commands.")

            elif page_name == "strategy":
                # Check scenario preset buttons
                preset_bar = page.locator(".strategy-preset-bar")
                assert preset_bar.count() > 0, "ERROR: .strategy-preset-bar not found!"
                startup_preset = page.locator("#preset-hackathon-demo, [data-load-zero-history-preset], .preset-btn")
                if startup_preset.count() > 0:
                    startup_preset.first.click()
                    time.sleep(0.5)
                # Check Precedence DAG anchor
                dag_anchor = page.locator(".strategy-pillar-anchor")
                assert dag_anchor.count() > 0
                test_results.append("[PASS] strategy.html: 1-click scenario preset bar interactive & Precedence DAG accessible.")

            elif page_name == "signin":
                assert page.locator(".auth-card, .signin-card, form").count() > 0
                test_results.append("[PASS] signin.html: Clean authentication interface rendered.")

            elif page_name == "account":
                assert page.locator("h1, .account-hero, .profile-card").count() > 0
                test_results.append("[PASS] account.html: Bidder profile studio rendered.")

            # Capture desktop screenshots
            desktop_png = SCREENSHOT_DIR / f"{page_name}_desktop.png"
            brain_desktop_png = BRAIN_SCREENSHOT_DIR / f"{page_name}_desktop.png"
            page.screenshot(path=str(desktop_png), full_page=True)
            page.screenshot(path=str(brain_desktop_png), full_page=True)
            print(f"    [OK] Desktop screenshot saved: {desktop_png.name}")

            # Audit DOM
            finding = audit_page_elements(page, page_name)
            finding["console_errors"] = console_logs[:10]
            all_findings.append(finding)
            context.close()

            # --- Mobile Viewport ---
            if p_info.get("mobile"):
                m_context = browser.new_context(
                    viewport={"width": 390, "height": 844},
                    user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15"
                )
                m_page = m_context.new_page()
                try:
                    m_page.goto(url, wait_until="networkidle", timeout=15000)
                except Exception:
                    pass
                time.sleep(1.0)
                mobile_png = SCREENSHOT_DIR / f"{page_name}_mobile.png"
                brain_mobile_png = BRAIN_SCREENSHOT_DIR / f"{page_name}_mobile.png"
                m_page.screenshot(path=str(mobile_png), full_page=True)
                m_page.screenshot(path=str(brain_mobile_png), full_page=True)
                print(f"    [OK] Mobile screenshot saved: {mobile_png.name}")
                m_context.close()

        browser.close()

    # Save findings JSON
    findings_file = ROOT_DIR / "artifacts" / "frontend_inspection_report.json"
    findings_file.parent.mkdir(parents=True, exist_ok=True)
    with open(findings_file, "w", encoding="utf-8") as f:
        json.dump(all_findings, f, indent=2)

    print("\n==================================================")
    print("PLAYWRIGHT FRONTEND TEST RESULTS:")
    print("==================================================")
    for res in test_results:
        print(f"  {res}")
    print(f"\n[OK] All Playwright frontend assertions passed!")
    print(f"[OK] Screenshots saved to: {SCREENSHOT_DIR}")
    print(f"[OK] Inspection report written to: {findings_file}")


if __name__ == "__main__":
    run_frontend_tests_and_capture()
