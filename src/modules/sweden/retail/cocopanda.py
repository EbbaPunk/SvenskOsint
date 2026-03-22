from __future__ import annotations

import json
from typing import Any, Dict

import requests

CHECK_URL = "https://www.cocopanda.se/loginDialogView"
HOME_URL = "https://www.cocopanda.se/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0",
    "Accept": "text/html",
    "Accept-Language": "en-US,en;q=0.5",
    "Content-Type": "application/json",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://www.cocopanda.se",
    "Referer": HOME_URL,
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}


def cocopanda(email: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {"accountExists": False, "raw": None}

    try:
        s = requests.Session()
        s.headers.update(HEADERS)

        s.get(HOME_URL, timeout=15)

        r = s.post(CHECK_URL, json={"email": email}, timeout=10)
        result["raw"] = r.text[:200]

        if "js-login-form" in r.text or "password-fields" in r.text:
            result["accountExists"] = True

        return result

    except Exception as e:
        result["raw"] = {"error": str(e)}
        return result


if __name__ == "__main__":
    import sys
    email = sys.argv[1] if len(sys.argv) > 1 else input("Email: ").strip()
    print(json.dumps(cocopanda(email), ensure_ascii=False, indent=2))
