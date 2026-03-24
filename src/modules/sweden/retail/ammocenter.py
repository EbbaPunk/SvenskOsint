from __future__ import annotations

import json
import re
from typing import Any, Dict

import requests

LOGIN_URL = "https://ammocenter.se/sv/account/login"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Origin": "https://ammocenter.se",
    "Referer": LOGIN_URL,
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
}


def ammocenter(email: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {"accountExists": False, "raw": None}

    try:
        s = requests.Session()
        s.headers.update(HEADERS)

        r = s.get(LOGIN_URL, timeout=15)

        m = re.search(r'name=["\']_token["\'][^>]*value=["\']([^"\']+)["\']', r.text) \
            or re.search(r'value=["\']([^"\']+)["\'][^>]*name=["\']_token["\']', r.text)
        if not m:
            result["raw"] = {"error": "_token not found"}
            return result
        token = m.group(1)

        r2 = s.post(
            LOGIN_URL,
            data={"_token": token, "email": email, "password": "Dummy_pass1!"},
            allow_redirects=True,
            timeout=10,
        )

        if "matchar inte" in r2.text:
            result["raw"] = {"error": "not found"}
            return result

        result["accountExists"] = True
        return result

    except Exception as e:
        result["raw"] = {"error": str(e)}
        return result


if __name__ == "__main__":
    import sys
    email = sys.argv[1] if len(sys.argv) > 1 else input("Email: ").strip()
    print(json.dumps(ammocenter(email), ensure_ascii=False, indent=2))
