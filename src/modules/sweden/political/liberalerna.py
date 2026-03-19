from __future__ import annotations

from typing import Any, Dict

import requests

FORGOT_URL = (
    "https://medlem.liberalerna.se/backend/api/v1/controller/user/startForgotPassword"
)


BEARER = "8927478239HJAH"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-GB,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Authorization": f"Bearer {BEARER}",
    "Content-Type": "application/json",
    "Origin": "https://medlem.liberalerna.se",
    "Referer": "https://medlem.liberalerna.se/app/login",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}


def liberalerna(email: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "accountExists": False,
        "raw": None,
    }

    try:
        r = requests.post(
            FORGOT_URL,
            json={"username": email},
            headers=HEADERS,
            timeout=10,
        )

        data = r.json()
        result["raw"] = data

        if data.get("code") == 404 or "not found" in str(data.get("error", "")).lower():
            result["accountExists"] = False
        elif "error" not in data:
            result["accountExists"] = True

        return result

    except Exception as e:
        result["raw"] = {"error": str(e)}
        return result


if __name__ == "__main__":
    import sys
    import json

    email = sys.argv[1] if len(sys.argv) > 1 else "test@example.com"
    print(json.dumps(liberalerna(email), indent=2))
