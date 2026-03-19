from __future__ import annotations

import json
import sys
from typing import Any, Dict

import requests

BASE_URL = "https://user.tv4.a2d.tv/v2/user/exists"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Origin": "https://auth.a2d.tv",
    "Referer": "https://auth.a2d.tv/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
}


def tv4(email: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {"accountExists": False, "raw": None}

    try:
        r = requests.get(BASE_URL, params={"email": email}, headers=HEADERS, timeout=10)
        data = r.json()
        result["raw"] = data
        result["accountExists"] = bool(data.get("exists"))
        return result

    except Exception as e:
        result["raw"] = {"error": str(e)}
        return result


if __name__ == "__main__":
    email = sys.argv[1] if len(sys.argv) > 1 else "test@example.com"
    print(json.dumps(tv4(email), indent=2))
