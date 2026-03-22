from __future__ import annotations

import json
from typing import Any, Dict

from curl_cffi import requests

CHECK_URL = "https://nelly.com/api/app/signup-status/"
HOME_URL = "https://nelly.com/se/login/?redirectTo=/se/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Referer": HOME_URL,
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}


def nelly(email: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {"accountExists": False, "raw": None}

    try:
        s = requests.Session(impersonate="chrome")
        s.headers.update(HEADERS)

        s.get(HOME_URL, timeout=15)

        r = s.get(CHECK_URL, params={"email": email}, timeout=10)

        data = r.json()
        result["raw"] = data

        if data.get("existsInCognito") or data.get("existsInVoyado") or data.get("isMember"):
            result["accountExists"] = True

        return result

    except Exception as e:
        result["raw"] = {"error": str(e)}
        return result


if __name__ == "__main__":
    import sys
    email = sys.argv[1] if len(sys.argv) > 1 else input("Email: ").strip()
    print(json.dumps(nelly(email), ensure_ascii=False, indent=2))
