from __future__ import annotations

import re
from typing import Any, Dict

import requests

BASE_URL = "https://mp.upright.se/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Origin": "https://mp.upright.se",
    "Referer": "https://mp.upright.se/",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Upgrade-Insecure-Requests": "1",
}


def _extract_hidden(html: str, name: str) -> str:
    m = re.search(
        rf'<input[^>]+name=["\']?{re.escape(name)}["\']?[^>]+value=["\']([^"\']*)["\']',
        html,
        re.IGNORECASE,
    )
    if not m:
        m = re.search(
            rf'<input[^>]+value=["\']([^"\']*)["\'][^>]+name=["\']?{re.escape(name)}["\']?',
            html,
            re.IGNORECASE,
        )
    return m.group(1) if m else ""


def mp(email: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "accountExists": False,
        "raw": None,
    }

    try:
        session = requests.Session()
        session.headers.update(HEADERS)

        r_get = session.get(BASE_URL, timeout=10)
        r_get.raise_for_status()

        viewstate = _extract_hidden(r_get.text, "__VIEWSTATE")
        viewstate_gen = _extract_hidden(r_get.text, "__VIEWSTATEGENERATOR")
        event_validation = _extract_hidden(r_get.text, "__EVENTVALIDATION")

        if not viewstate:
            result["raw"] = {"error": "Could not extract __VIEWSTATE from page"}
            return result

        r_post = session.post(
            BASE_URL,
            data={
                "__EVENTTARGET": "",
                "__EVENTARGUMENT": "",
                "__VIEWSTATE": viewstate,
                "__VIEWSTATEGENERATOR": viewstate_gen,
                "__EVENTVALIDATION": event_validation,
                "txtPersonnumer": "",
                "TboxEmail": "",
                "TboxPass": "",
                "tboxEpost": email,
                "NewPasswordButton": "Skicka",
                "txtPersonnummerReg": "",
                "txtMobil": "",
                "txtEpost": "",
                "TabName": "forgot-password",
            },
            timeout=10,
        )

        html = r_post.text
        result["raw"] = html[:300]

        if any(
            kw in html
            for kw in ("skickats", "bekräftelse", "har skickats", "check your email")
        ):
            result["accountExists"] = True
        elif any(
            kw in html
            for kw in ("finns inte", "hittades inte", "not found", "ogiltigt")
        ):
            result["accountExists"] = False

        return result

    except Exception as e:
        result["raw"] = {"error": str(e)}
        return result


if __name__ == "__main__":
    import sys
    import json

    email = sys.argv[1] if len(sys.argv) > 1 else "test@example.com"
    print(json.dumps(mp(email), indent=2))
