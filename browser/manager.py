import os
from pathlib import Path
from typing import Optional, Dict
from camoufox.sync_api import Camoufox


# Persistent profile directory — sits next to the project root
PROFILE_DIR = str(Path(__file__).resolve().parent.parent / ".browser_profile")


class BrowserManager:
    """Context manager for Camoufox stealth browser with persistent sessions.

    Uses a persistent browser profile so that cookies (including solved
    CAPTCHAs) survive across runs.  The first run may require you to
    solve a CAPTCHA manually in headful mode; subsequent runs will reuse
    the session.

    Args:
        headless: Run in headless mode.
        proxy: Optional proxy dict {"server": "...", "username": "...", "password": "..."}.
    """

    def __init__(self, headless: bool = True, proxy: Optional[Dict] = None):
        self.headless = headless
        self.proxy = proxy
        self._camoufox = None
        self.browser = None
        self.page = None

    def __enter__(self):
        kwargs = {
            "headless": self.headless,
            "humanize": True,
            "os": "windows",
            "block_webrtc": True,
            "persistent_context": True,
            "user_data_dir": PROFILE_DIR,
        }
        # if self.proxy:
        #     kwargs["proxy"] = self.proxy
        #     kwargs["geoip"] = True  # Auto-match locale/tz to proxy IP

        self._camoufox = Camoufox(**kwargs)
        # With persistent_context, __enter__ returns a BrowserContext (not Browser)
        self.browser = self._camoufox.__enter__()
        # Persistent context already has a default page; reuse or create one
        pages = self.browser.pages
        self.page = pages[0] if pages else self.browser.new_page()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._camoufox:
            self._camoufox.__exit__(exc_type, exc_val, exc_tb)
