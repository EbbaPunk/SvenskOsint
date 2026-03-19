from __future__ import annotations

import json
import re
import uuid
from typing import Any, Dict

import requests

CLIENT_ID = "680f71d5c7b4122547861e44"
CLIENT_SDRN = f"sdrn:schibsted.com:client:{CLIENT_ID}"
AUTHN_URL = "https://login.vend.se/authn/email-login"
EMAIL_STATUS_URL = (
    f"https://login.vend.se/authn/api/identity/email-status?client_id={CLIENT_ID}"
)
CSRF_URL = f"https://login.vend.se/authn/api/settings/csrf?client_id={CLIENT_ID}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Referer": "https://www.blocket.se/",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Upgrade-Insecure-Requests": "1",
}

_DEVICE_DATA_DICT = {
    "fonts": [
        "Arial",
        "Arial Black",
        "Cambria Math",
        "Consolas",
        "Courier",
        "Courier New",
        "Georgia",
        "Helvetica",
        "Lucida Console",
        "MS Gothic",
        "MS PGothic",
        "MS Serif",
        "Segoe UI",
        "Segoe UI Light",
        "Tahoma",
        "Times",
        "Times New Roman",
        "Verdana",
    ],
    "hasLiedBrowser": "0",
    "hasLiedOs": "0",
    "platform": "Windows",
    "plugins": [
        "PDF Viewer::Portable Document Format::application/pdf~pdf,text/pdf,pdf",
        "Chrome PDF Viewer::Portable Document Format::application/pdf~pdf,text/pdf,pdf",
        "Chromium PDF Viewer::Portable Document Format::application/pdf~pdf,text/pdf,pdf",
        "Microsoft Edge PDF Viewer::Portable Document Format::application/pdf~pdf,text/pdf,pdf",
        "WebKit built-in PDF::Portable Document Format::application/pdf~pdf,text/pdf,pdf",
    ],
    "userAgent": "Firefox",
    "userAgentVersion": "140.0",
}
DEVICE_DATA = json.dumps(_DEVICE_DATA_DICT)


def _get_authn_page(session: requests.Session) -> tuple[str, str]:
    nonce = str(uuid.uuid4())
    state = uuid.uuid4().hex + uuid.uuid4().hex

    authn_url = (
        f"{AUTHN_URL}"
        f"?client_sdrn={CLIENT_SDRN.replace(':', '%3A')}"
        f"&client_id={CLIENT_ID}"
        f"&one_step_login=false"
        f"&teaser=aurora_teaser_blocket_web"
        f"&acr_values=otp-email"
        f"&nonce={nonce}"
        f"&state={state}"
    )

    resp = session.get(authn_url, allow_redirects=True, timeout=15)
    return authn_url, resp.text


def _extract_csrf(html: str) -> str | None:
    m = re.search(
        r'<div[^>]+id=["\']bffData["\'][^>]*>(.*?)</div>',
        html,
        re.DOTALL | re.IGNORECASE,
    )
    if m:
        try:
            data = json.loads(m.group(1))
            token = data.get("csrfToken") or (data.get("initialData") or {}).get(
                "csrfToken"
            )
            if token:
                return token
        except (json.JSONDecodeError, AttributeError):
            pass

    for pattern in (
        r'"csrfToken"\s*:\s*"([^"]{10,})"',
        r'csrf[_\-]?token["\']?\s*[:=]\s*["\']([A-Za-z0-9_\-\.]{10,})["\']',
    ):
        m = re.search(pattern, html, re.IGNORECASE)
        if m:
            return m.group(1)
    return None


def blocket(email: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "accountExists": False,
        "userId": None,
        "raw": None,
    }

    session = requests.Session()
    session.headers.update(HEADERS)

    try:
        authn_url, html = _get_authn_page(session)

        csrf = _extract_csrf(html)

        if not csrf:
            r_csrf = session.get(
                CSRF_URL,
                headers={
                    "Accept": "application/json",
                    "Accept-Encoding": "gzip, deflate",
                    "Origin": "https://login.vend.se",
                    "Referer": authn_url,
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "same-origin",
                },
                timeout=10,
            )
            try:
                data_csrf = r_csrf.json()
                csrf = (
                    (data_csrf.get("data") or {}).get("attributes", {}).get("csrfToken")
                    or data_csrf.get("csrfToken")
                    or data_csrf.get("token")
                )
            except Exception:
                pass

        if not csrf:
            result["raw"] = {"error": "CSRF token not found"}
            return result

        r2 = session.post(
            EMAIL_STATUS_URL,
            json={"email": email, "deviceData": DEVICE_DATA},
            headers={
                "x-csrf-token": csrf,
                "Origin": "https://login.vend.se",
                "Referer": authn_url,
                "Accept": "application/json",
                "Accept-Encoding": "gzip, deflate",
                "Content-Type": "application/json",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
            },
            timeout=10,
        )

        data = r2.json()
        result["raw"] = data

        next_href = (data.get("links") or {}).get("next", {}).get("href", "")
        if next_href == "/login-password":
            result["accountExists"] = True
            uid = (data.get("meta") or {}).get("tracking", {}).get("userIdentifier")
            if uid:
                result["userId"] = uid

        return result

    except Exception as e:
        result["raw"] = {"error": str(e)}
        return result


if __name__ == "__main__":
    import sys

    email = sys.argv[1] if len(sys.argv) > 1 else "test@example.com"
    print(json.dumps(blocket(email), indent=2))
