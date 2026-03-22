from __future__ import annotations

import json
import re
from typing import Any, Dict

import requests

ENTRY_URL = "https://allsvenskan.se/auth/login"
SIGN_IN_URL = "https://konto.svenskelitfotboll.se/Identity/SignIn"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
}


def allsvenskan(email: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {"accountExists": False, "raw": None}

    try:
        s = requests.Session()
        s.headers.update(HEADERS)

        r = s.get(ENTRY_URL, allow_redirects=True, timeout=15)
        login_url = r.url

        m = re.search(r"[?&]ReturnUrl=([^&\"]+)", login_url)
        return_url = m.group(1) if m else ""

        m = re.search(
            r'name=["\']__RequestVerificationToken["\'][^>]*value=["\']([^"\']+)["\']', r.text
        ) or re.search(
            r'value=["\']([^"\']+)["\'][^>]*name=["\']__RequestVerificationToken["\']', r.text
        )
        if not m:
            result["raw"] = {"error": "RVT not found"}
            return result
        rvt = m.group(1)

        r2 = s.post(
            SIGN_IN_URL,
            data={
                "ReturnUrl": return_url,
                "Stage": "Initial",
                "TwoFactorProvider": "Default",
                "Username": email,
                "UsernameConfirmed": "",
                "__RequestVerificationToken": rvt,
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": "https://konto.svenskelitfotboll.se",
                "Referer": login_url,
                "Sec-Fetch-User": "?1",
            },
            allow_redirects=True,
            timeout=10,
        )

        result["raw"] = r2.text[:200]

        if "Välkommen tillbaka" in r2.text or "Hej!" in r2.text:
            result["accountExists"] = True

        return result

    except Exception as e:
        result["raw"] = {"error": str(e)}
        return result


if __name__ == "__main__":
    import sys
    email = sys.argv[1] if len(sys.argv) > 1 else input("Email: ").strip()
    print(json.dumps(allsvenskan(email), ensure_ascii=False, indent=2))
