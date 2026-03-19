from __future__ import annotations

import base64
import hashlib
import re
import secrets
import urllib.parse
from typing import Any, Dict

import requests

TENANT = "ecomsystembolagetse.onmicrosoft.com"
CLIENT_ID = "70e74f97-9d41-4d59-b0f2-7300398e0173"
POLICY = "B2C_1A_SIGNINSIGNUP"
REDIRECT = "https://www.systembolaget.se/api/auth/callback/ecom"
SCOPE = f"https://{TENANT}/sb-web-ecom-api/ecommerce.api openid offline_access"
BASE = f"https://konto.systembolaget.se/{TENANT}/{POLICY}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
}


def _pkce() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(48)
    challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest())
        .rstrip(b"=")
        .decode()
    )
    return verifier, challenge


def systembolaget(email: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {"accountExists": False, "method": None, "raw": None}

    try:
        s = requests.Session()
        s.headers.update(HEADERS)

        _, challenge = _pkce()
        state = secrets.token_urlsafe(32)

        auth_url = (
            f"{BASE}/oauth2/v2.0/authorize"
            f"?client_id={CLIENT_ID}"
            f"&scope={urllib.parse.quote(SCOPE)}"
            f"&response_type=code"
            f"&redirect_uri={urllib.parse.quote(REDIRECT)}"
            f"&state={state}"
            f"&code_challenge={challenge}"
            f"&code_challenge_method=S256"
        )

        r = s.get(auth_url, allow_redirects=True, timeout=15)

        tx_match = re.search(
            r'"transId"\s*:\s*"(StateProperties=[^"]+)"', r.text
        ) or re.search(r"[?&]tx=(StateProperties=[^&\"'\s]+)", r.url + " " + r.text)
        if not tx_match:
            result["raw"] = {"error": "tx param not found", "url": r.url}
            return result
        tx = tx_match.group(1)

        csrf = s.cookies.get("x-ms-cpim-csrf")
        if not csrf:
            csrf_match = re.search(r'"csrf"\s*:\s*"([^"]+)"', r.text)
            if csrf_match:
                csrf = csrf_match.group(1)
        if not csrf:
            result["raw"] = {"error": "x-ms-cpim-csrf cookie missing"}
            return result

        post_url = f"{BASE}/SelfAsserted?tx={tx}&p={POLICY}"
        r2 = s.post(
            post_url,
            data={
                "request_type": "RESPONSE",
                "signInName": email,
                "password": "Dummy_pass1!",
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "X-CSRF-TOKEN": csrf,
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://konto.systembolaget.se",
                "Referer": r.url,
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
            },
            timeout=10,
        )

        data = r2.json()
        result["raw"] = data

        code = data.get("errorCode", "")

        if code == "AADB2C90053":
            result["accountExists"] = True
            result["method"] = "bankid"
        elif data.get("status") == "200" or code == "AADB2C90225":
            result["accountExists"] = True
            result["method"] = "password"

        return result

    except Exception as e:
        result["raw"] = {"error": str(e)}
        return result


if __name__ == "__main__":
    import sys
    import json

    email = sys.argv[1] if len(sys.argv) > 1 else input("Email: ").strip()
    print(json.dumps(systembolaget(email), ensure_ascii=False, indent=2))
