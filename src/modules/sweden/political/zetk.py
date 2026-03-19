from __future__ import annotations

from typing import Any, Dict

import requests

RESET_URL = "https://api.zetk.in/v1/password_reset_tokens"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Content-Type": "application/json",
    "Origin": "https://www.zetk.in",
    "Referer": "https://www.zetk.in/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
}


def zetk(email: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "accountExists": False,
        "raw": None,
    }

    try:
        r = requests.post(
            RESET_URL,
            json={"email": email},
            headers=HEADERS,
            timeout=10,
        )

        data = r.json()
        result["raw"] = data

        error = data.get("error", {})
        if "404" in str(error.get("title", "")):
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
    print(json.dumps(zetk(email), indent=2))
