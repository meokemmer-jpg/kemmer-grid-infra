#!/usr/bin/env python3
"""
Login-Workaround fuer notebooklm-py 0.3.4 Race-Condition.

Probleme im offiziellen `python -m notebooklm login`:
1. Nutzt Chromium-for-Testing (leeres Profil) statt echten Chrome (wo Martin schon eingeloggt ist)
2. Race-Condition bei goto(accounts.google.com) wenn Cookies teilweise vorhanden

Diese Workaround:
- Startet via Playwright den ECHTEN installierten Chrome (channel="chrome")
- Navigiert direkt zu notebooklm.google.com (nicht accounts.google.com)
- Laesst Martin manuell einloggen wenn noetig
- Speichert storage_state.json im erwarteten Pfad fuer AuthTokens.from_storage()

Usage:
    python login_workaround.py
    # Browser oeffnet sich (echter Chrome)
    # Falls eingeloggt: direkt NotebookLM-Seite sichtbar
    # Falls nicht: Google-Login machen
    # Enter druecken wenn bereit zum Speichern
"""

import asyncio
from pathlib import Path


# [CRUX-MK] Runtime-Gate (Layer 0)
try:
    import sys as _crux_sys, pathlib as _crux_path
    _crux_sys.path.insert(0, str(_crux_path.Path.home() / ".claude" / "scripts"))
    import crux_runtime as _crux_rt  # auto-checks kill-switch on import
except (ImportError, SystemExit):
    import sys as _crux_sys
    _crux_kf = _crux_path.Path.home() / ".kemmer-grid" / "killed.flag" if '_crux_path' in dir() else None
    if _crux_kf and _crux_kf.exists(): _crux_sys.exit(1)
# /[CRUX-MK] Runtime-Gate

# Must match DEFAULT_STORAGE_PATH in notebooklm-py auth.py
STORAGE_DIR = Path.home() / ".notebooklm"
PROFILE_DIR = STORAGE_DIR / "browser_profile"
STORAGE_FILE = STORAGE_DIR / "storage_state.json"

async def main():
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("ERROR: playwright not installed. Run: pip install 'notebooklm-py[browser]'")
        return

    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        # Try channel="chrome" first (uses real installed Chrome, inherits some cookies)
        # Fall back to chromium if chrome not available
        try:
            print("Starting real Chrome browser (channel='chrome')...")
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(PROFILE_DIR),
                channel="chrome",
                headless=False,
                args=["--start-maximized"],
                ignore_default_args=["--enable-automation"],
            )
        except Exception as exc_chrome:
            print(f"Real Chrome not available ({exc_chrome}), falling back to Chromium...")
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(PROFILE_DIR),
                headless=False,
                ignore_default_args=["--enable-automation"],
            )

        # Get or create page, navigate DIRECTLY to NotebookLM (avoid accounts.google.com race)
        pages = context.pages
        page = pages[0] if pages else await context.new_page()

        print("Navigating to notebooklm.google.com...")
        try:
            await page.goto("https://notebooklm.google.com/", wait_until="domcontentloaded", timeout=60000)
        except Exception as exc_goto:
            print(f"Navigation note (often harmless if already loaded): {exc_goto}")

        await asyncio.sleep(2)

        # Check current URL
        current_url = page.url
        print(f"Current URL: {current_url}")

        if "accounts.google.com" in current_url or "signin" in current_url.lower():
            print("\n=== LOGIN REQUIRED ===")
            print("Please log in with Martin's Google account (m.e.o.kemmer@gmail.com)")
            print("in the opened browser window.")
            print("AFTER you see notebooklm.google.com with your notebooks listed,")
            print("return to this terminal and press ENTER.")
        else:
            print("\n=== SESSION DETECTED ===")
            print("Looks like you're already logged in.")
            print("Verify the browser shows your notebooks, then press ENTER to save.")

        input("\nPress ENTER when ready to save session: ")

        # Verify we're on NotebookLM before saving
        final_url = page.url
        if "notebooklm.google.com" not in final_url:
            print(f"WARNING: Current URL is {final_url}, not notebooklm.google.com")
            print("Saving anyway, but storage may be incomplete.")

        # Save storage state to the file AuthTokens.from_storage() expects
        await context.storage_state(path=str(STORAGE_FILE))
        print(f"\nSaved storage state to: {STORAGE_FILE}")

        # Quick validation: how many cookies saved?
        import json
        state = json.loads(STORAGE_FILE.read_text())
        cookies_count = len(state.get("cookies", []))
        google_cookies = [c for c in state.get("cookies", []) if "google" in c.get("domain", "")]
        sid_present = any(c.get("name") == "SID" for c in google_cookies)
        print(f"Cookies saved: {cookies_count} total, {len(google_cookies)} google domain, SID={sid_present}")

        if not sid_present:
            print("\nWARNING: SID cookie not found. Auth likely failed. Re-run after full login.")
        else:
            print("\nSID cookie present. You can now run: python orchestrator.py --notebook X")

        await context.close()

if __name__ == "__main__":
    asyncio.run(main())
