from __future__ import annotations

import json
import re
import sys
from typing import Any, Dict

import requests

LOGIN_URL = "https://www.byggahus.se/forum/login/login"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Referer": LOGIN_URL,
    "Origin": "https://www.byggahus.se",
    "Content-Type": "application/x-www-form-urlencoded",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}


def byggahus(email: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {"accountExists": False, "raw": None}

    try:
        session = requests.Session()
        session.headers.update(HEADERS)

        r = session.get(LOGIN_URL, timeout=10)
        r.raise_for_status()

        m = re.search(r'name="_xfToken"\s+value="([^"]+)"', r.text)
        if not m:
            result["raw"] = {"error": "Could not extract _xfToken"}
            return result
        xf_token = m.group(1)

        data = {
            "_xfToken": xf_token,
            "login": email,
            "password": "dummy_password_osint",
            "remember": "1",
            "_xfRedirect": "https://www.byggahus.se/",
        }
        r2 = session.post(LOGIN_URL, data=data, timeout=10, allow_redirects=True)
        result["raw"] = {"status": r2.status_code}

        if "Hittar ingen" in r2.text:
            result["accountExists"] = False
        else:
            result["accountExists"] = True

        return result

    except Exception as e:
        result["raw"] = {"error": str(e)}
        return result


if __name__ == "__main__":
    email = sys.argv[1] if len(sys.argv) > 1 else "test@example.com"
    print(json.dumps(byggahus(email), indent=2))
