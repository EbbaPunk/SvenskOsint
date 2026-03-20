from __future__ import annotations

from typing import Any, Dict

import requests

API_KEY = "AIzaSyDq4VkZcvgecpz5sgWfqqDTTmPUySYoK3c"
CHECK_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-GB,en;q=0.9",
    "Content-Type": "application/json",
    "Origin": "https://kvitto.7-eleven.se",
    "x-client-version": "Chrome/JsCore/10.8.1/FirebaseCore-web",
    "x-firebase-gmpid": "1:362667218079:web:6c2aaf30cafc5beeccbeaa",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
}


def seven_eleven(email: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {"accountExists": False, "raw": None}

    try:
        r = requests.post(
            CHECK_URL,
            json={
                "returnSecureToken": True,
                "email": email,
                "password": "Dummy_pass1!",
                "clientType": "CLIENT_TYPE_WEB",
            },
            headers=HEADERS,
            timeout=10,
        )

        data = r.json()
        result["raw"] = data
        msg = (data.get("error") or {}).get("message", "")

        if msg == "TOO_MANY_ATTEMPTS_TRY_LATER":
            result["raw"] = {"error": "rate_limited"}
        elif msg not in ("EMAIL_NOT_FOUND", ""):
            result["accountExists"] = True
        elif data.get("idToken"):
            result["accountExists"] = True

        return result

    except Exception as e:
        result["raw"] = {"error": str(e)}
        return result


if __name__ == "__main__":
    import json
    import sys

    email = sys.argv[1] if len(sys.argv) > 1 else input("Email: ").strip()
    print(json.dumps(seven_eleven(email), ensure_ascii=False, indent=2))
