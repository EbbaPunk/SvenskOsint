from __future__ import annotations

import json
import requests

CHECK_URL = "https://api.lovable.dev/auth/check-auth-provider"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://lovable.dev/",
    "X-Client-Git-SHA": "502c7efcc9ba4763c236efe388ccde4446ea1eea",
    "Origin": "https://lovable.dev",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
}


def loveable(email: str) -> dict:
    r = requests.post(
        CHECK_URL,
        json={"email": email},
        headers=HEADERS,
        timeout=10,
    )

    try:
        data = r.json()
    except Exception:
        return {"found": False, "error": "non-JSON response", "body": r.text[:300]}

    found = bool(
        data.get("has_email_password")
        or data.get("has_sso_provider")
        or data.get("firebase_providers")
    )

    if found:
        return {"found": True, "email": email, "raw": data}
    return {"found": False}


if __name__ == "__main__":
    import sys
    email = sys.argv[1] if len(sys.argv) > 1 else input("Email: ").strip()
    print(json.dumps(loveable(email), ensure_ascii=False, indent=2))
