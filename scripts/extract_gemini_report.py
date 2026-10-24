"""
TenderLens - Extract Gemini Shared Report
==========================================
Uses Playwright to render the client-side JavaScript page at:
https://share.gemini.google/1s2mmq1tTaM6
and saves the full report into research/argon_report.md
"""

import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

URL = "https://share.gemini.google/1s2mmq1tTaM6"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "research" / "argon_report.md"


def extract_report():
    print(f"[INFO] Launching browser to fetch: {URL}")
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        # Launch browser - try system Edge or Chrome first for instant execution
        browser = None
        for channel in ["msedge", "chrome", None]:
            try:
                if channel:
                    print(f"[INFO] Attempting to launch system browser (channel={channel})...")
                    browser = p.chromium.launch(headless=True, channel=channel)
                else:
                    print("[INFO] Attempting to launch default Playwright Chromium...")
                    browser = p.chromium.launch(headless=True)
                if browser:
                    break
            except Exception as e:
                print(f"[DEBUG] Failed to launch channel {channel}: {e}")

        if not browser:
            print("[ERROR] Could not launch any browser. Please run: playwright install chromium")
            return False

        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        print("[INFO] Navigating to URL...")
        page.goto(URL, wait_until="networkidle", timeout=60000)

        # Give client-side JS time to hydrate and render conversation
        print("[INFO] Waiting for conversation hydration...")
        time.sleep(5)

        # Attempt to find structured conversation / response elements
        content = ""
        
        # Check standard Gemini chat element selectors
        selectors = [
            ".conversation-container",
            "message-content",
            ".message-content",
            "model-response",
            "main",
            "article",
            "[data-test-id='conversation-turn']"
        ]

        found_elements = []
        for sel in selectors:
            elems = page.locator(sel).all()
            if elems:
                found_elements.extend(elems)

        if found_elements:
            print(f"[INFO] Found {len(found_elements)} conversation message elements.")
            texts = [elem.inner_text() for elem in found_elements if elem.inner_text().strip()]
            content = "\n\n---\n\n".join(texts)
        else:
            print("[INFO] Falling back to main text extraction...")
            content = page.locator("body").inner_text()

        browser.close()

    if not content or len(content.strip()) < 50:
        print("[ERROR] Extracted content appears empty or too short.")
        return False

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(f"# Argon Research Report\n\nSource: {URL}\n\n---\n\n")
        f.write(content)

    print(f"[SUCCESS] Report extracted successfully to: {OUTPUT_PATH}")
    print(f"[INFO] Total character count: {len(content):,}")
    return True


if __name__ == "__main__":
    success = extract_report()
    sys.exit(0 if success else 1)
