from __future__ import annotations

import json
import sys
from typing import Any, Dict

import requests

LOOKUP_URL = "https://bn-valvet-prod.bnu.bn.nr/user-lookup"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Origin": "https://registrera.di.se",
    "Referer": "https://registrera.di.se/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
}


def di(email: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "accountExists": False,
        "userId": None,
        "firstName": None,
        "lastName": None,
        "lastLogin": None,
        "lastActive": None,
        "raw": None,
    }

    try:
        r = requests.post(
            LOOKUP_URL,
            json={"email": email, "namespace": "di"},
            headers=HEADERS,
            timeout=10,
        )
        data = r.json()
        result["raw"] = data

        resp = data.get("response")
        if not resp:
            return result

        result["accountExists"] = True
        result["userId"] = resp.get("userId")
        result["lastLogin"] = resp.get("lastLogin")
        result["lastActive"] = resp.get("lastActive")

        props = resp.get("properties") or {}
        result["firstName"] = props.get("firstName")
        result["lastName"] = props.get("lastName")

        return result

    except Exception as e:
        result["raw"] = {"error": str(e)}
        return result


if __name__ == "__main__":
    email = sys.argv[1] if len(sys.argv) > 1 else "test@example.com"
    print(json.dumps(di(email), indent=2))
