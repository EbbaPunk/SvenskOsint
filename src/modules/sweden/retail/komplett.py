from __future__ import annotations

import json
import re

import requests

ENTRY_URL  = "https://www.komplett.se/login?redirectTo=%2F"
LOGIN_URL  = "https://login.komplett.se/login/VerifyLogin"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Upgrade-Insecure-Requests": "1",
}


def komplett(email: str) -> dict:
    s = requests.Session()
    s.headers.update(HEADERS)

    r = s.get(ENTRY_URL, allow_redirects=True, timeout=15)
    login_page_url = r.url

    m = re.search(r'name=["\']__RequestVerificationToken["\'][^>]*value=["\']([^"\']+)["\']', r.text) \
        or re.search(r'value=["\']([^"\']+)["\'][^>]*name=["\']__RequestVerificationToken["\']', r.text)
    if not m:
        m = re.search(r'<meta[^>]+name=["\']RequestVerificationToken["\'][^>]*content=["\']([^"\']+)["\']', r.text)
    if not m:
        return {"found": False, "error": "RequestVerificationToken not found"}
    rvt = m.group(1)

    return_url_match = re.search(r'"returnUrl"\s*:\s*"([^"]+)"', r.text) \
        or re.search(r'[?&]returnUrl=([^&"\'\\]+)', r.text)
    return_url = return_url_match.group(1) if return_url_match else "/connect/authorize/callback"

    r2 = s.post(
        LOGIN_URL,
        json={
            "username": email,
            "password": "Dummy_pass1!",
            "returnUrl": return_url,
            "rememberLogin": True,
        },
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "requestverificationtoken": rvt,
            "Origin": "https://login.komplett.se",
            "Referer": login_page_url,
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        },
        timeout=10,
    )

    try:
        data = r2.json()
    except Exception:
        return {"found": False, "error": "non-JSON response", "body": r2.text[:300]}

    if data.get("invalidUsername"):
        return {"found": False}

    if data.get("isWrongPassword") or data.get("isUserLocked") or data.get("isAccountBlocked") or data.get("isSuccess"):
        return {"found": True, "email": email, "raw": data}

    return {"found": False, "raw": data}


if __name__ == "__main__":
    import sys
    email = sys.argv[1] if len(sys.argv) > 1 else input("Email: ").strip()
    print(json.dumps(komplett(email), ensure_ascii=False, indent=2))
