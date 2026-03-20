from __future__ import annotations

import random
import string
import time
from typing import Any, Dict

import requests

CHECK_URL = "https://www.foodora.se/login/new/api/email-check"
HOME_URL = "https://www.foodora.se/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Accept-Language": "en-GB,en;q=0.9",
    "Origin": "https://www.foodora.se",
    "Referer": "https://www.foodora.se/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}


def _perseus_id() -> str:
    ts = int(time.time() * 1000)
    big = random.randint(10**17, 10**18 - 1)
    short = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return f"{ts}.{big}.{short}"


def foodora(email: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {"accountExists": False, "raw": None}

    try:
        s = requests.Session()
        s.headers.update(HEADERS)
        s.get(HOME_URL, timeout=15)

        r = s.post(
            CHECK_URL,
            json={"email": email},
            headers={
                "Accept": "application/json, text/plain, */*",
                "Content-Type": "application/json;charset=UTF-8",
                "perseus-client-id": _perseus_id(),
                "perseus-session-id": _perseus_id(),
            },
            timeout=10,
        )

        data = r.json()
        result["raw"] = data

        if "is_known" not in data:
            result["raw"] = {"error": "captcha or unexpected response"}
            return result

        if data.get("is_known") or data.get("has_password") or data.get("has_social_login"):
            result["accountExists"] = True

        return result

    except Exception as e:
        result["raw"] = {"error": str(e)}
        return result


if __name__ == "__main__":
    import json
    import sys

    email = sys.argv[1] if len(sys.argv) > 1 else input("Email: ").strip()
    print(json.dumps(foodora(email), ensure_ascii=False, indent=2))
