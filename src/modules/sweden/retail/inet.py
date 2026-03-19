from __future__ import annotations

from typing import Any, Dict

import requests

LOGIN_URL = "https://www.inet.se/api/user/login"
HOME_URL = "https://www.inet.se/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Origin": "https://www.inet.se",
    "Referer": "https://www.inet.se/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}


def inet(email: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {"accountExists": False, "raw": None}

    try:
        s = requests.Session()
        s.headers.update(HEADERS)
        s.get(HOME_URL, timeout=10)

        r = s.post(
            LOGIN_URL,
            json={"email": email, "password": "Dummy_pass1!", "isPersistent": False},
            headers={"Content-Type": "application/json", "Accept": "*/*"},
            timeout=10,
        )

        data = r.json()
        result["raw"] = data

        if data.get("error") != "EmailNotFound":
            result["accountExists"] = True

        return result

    except Exception as e:
        result["raw"] = {"error": str(e)}
        return result


if __name__ == "__main__":
    import json
    import sys

    email = sys.argv[1] if len(sys.argv) > 1 else input("Email: ").strip()
    print(json.dumps(inet(email), ensure_ascii=False, indent=2))
