"""
TenderLens - TinyFish API Key Verification Script
==================================================
Tests the TINYFISH_API_KEY loaded from .env without exposing the secret key.
Uses standard library (no extra dependencies required).
"""

import os
import sys
import json
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path


def load_env_safely():
    """Loads .env into os.environ if present, without printing any secrets."""
    possible_paths = [
        Path(__file__).resolve().parent.parent / ".env",
        Path(".env"),
        Path.cwd() / ".env"
    ]
    for env_path in possible_paths:
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("'\"")
                        if k not in os.environ:
                            os.environ[k] = v
            break


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def mask_key(key: str) -> str:
    """Masks secret key so it never appears in terminal logs or outputs."""
    if not key:
        return "<EMPTY>"
    if len(key) <= 8:
        return "***"
    return f"{key[:4]}...{key[-4:]} (length: {len(key)})"


def verify_tinyfish():
    load_env_safely()
    api_key = os.environ.get("TINYFISH_API_KEY")

    if not api_key or api_key.startswith("sk-tinyfish-your-key"):
        print("[ERROR] TINYFISH_API_KEY not found in .env (or still set to placeholder).")
        print("        Please check that .env has TINYFISH_API_KEY=sk-tinyfish-...")
        return False

    # Clean key of any invisible characters/newlines/carriage returns
    api_key = api_key.strip()

    print(f"[KEY] Detected TINYFISH_API_KEY: {mask_key(api_key)}")
    print("[INFO] Endpoint 1: Testing TinyFish Search API (https://api.search.tinyfish.ai)...")

    params = urllib.parse.urlencode({
        "query": "site:gem.gov.in tender solar",
        "location": "IN",
        "language": "en"
    })
    search_url = f"https://api.search.tinyfish.ai?{params}"

    search_req = urllib.request.Request(
        search_url,
        headers={
            "X-API-Key": api_key,
            "User-Agent": "TenderLens-KeyCheck/1.0"
        },
        method="GET"
    )

    search_success = False
    try:
        with urllib.request.urlopen(search_req, timeout=15) as response:
            status_code = response.getcode()
            raw = response.read().decode("utf-8")
            data = json.loads(raw)
            results = data.get("results", [])
            print(f"[OK] Search API responded HTTP {status_code} OK")
            print(f"[INFO] Discovered {len(results)} live search items via TinySearch.")
            search_success = True
    except urllib.error.HTTPError as e:
        print(f"[ERROR] Search API HTTP {e.code}: {e.reason}")
        try:
            print(f"        Response: {e.read().decode('utf-8')}")
        except Exception:
            pass

    print("\n[INFO] Endpoint 2: Testing TinyFish Fetch API (https://api.fetch.tinyfish.ai)...")
    fetch_payload = json.dumps({"urls": ["https://example.com"]}).encode("utf-8")
    fetch_req = urllib.request.Request(
        "https://api.fetch.tinyfish.ai",
        data=fetch_payload,
        headers={
            "X-API-Key": api_key,
            "Content-Type": "application/json",
            "User-Agent": "TenderLens-KeyCheck/1.0"
        },
        method="POST"
    )

    fetch_success = False
    try:
        with urllib.request.urlopen(fetch_req, timeout=15) as response:
            status_code = response.getcode()
            print(f"[OK] Fetch API responded HTTP {status_code} OK")
            fetch_success = True
    except urllib.error.HTTPError as e:
        print(f"[ERROR] Fetch API HTTP {e.code}: {e.reason}")
        try:
            print(f"        Response: {e.read().decode('utf-8')}")
        except Exception:
            pass

    if search_success or fetch_success:
        print("\n[SUCCESS] TINYFISH_API_KEY is ACTIVE and FUNCTIONAL!")
        return True
    else:
        print("\n[FAILED] Key verification failed.")
        print("         -> Please verify that the key copied to .env is correct and active at:")
        print("            https://agent.tinyfish.ai/api-keys")
        return False


if __name__ == "__main__":
    success = verify_tinyfish()
    sys.exit(0 if success else 1)

