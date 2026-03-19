from __future__ import annotations

import json
import re
import uuid
from typing import Any, Dict

import requests

CLIENT_ID = "5e4e6b8dba2d9d68e7f1ccdc"
REDIRECT_URI = "https://www.aftonbladet.se/callback"
AUTHORIZE_URL = "https://login.schibsted.com/oauth/authorize"
EMAIL_STATUS_URL = (
    "https://login.schibsted.com/authn/api/identity/email-status"
    f"?client_id={CLIENT_ID}"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.aftonbladet.se/",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Upgrade-Insecure-Requests": "1",
}

DEVICE_DATA = {
    "fonts": [
        "Arial",
        "Arial Black",
        "Arial Narrow",
        "Calibri",
        "Cambria",
        "Cambria Math",
        "Comic Sans MS",
        "Consolas",
        "Courier",
        "Courier New",
        "Georgia",
        "Helvetica",
        "Impact",
        "Lucida Console",
        "Lucida Sans Unicode",
        "Microsoft Sans Serif",
        "MS Gothic",
        "MS PGothic",
        "MS Sans Serif",
        "MS Serif",
        "Palatino Linotype",
        "Segoe Print",
        "Segoe Script",
        "Segoe UI",
        "Segoe UI Light",
        "Segoe UI Semibold",
        "Segoe UI Symbol",
        "Tahoma",
        "Times",
        "Times New Roman",
        "Trebuchet MS",
        "Verdana",
        "Wingdings",
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
    "userAgent": "Chrome",
    "userAgentVersion": "145.0.0.0",
}


def _oauth_flow(session: requests.Session) -> tuple[str, str]:
    """4-step OAuth redirect chain. Returns (authn_url, authn_html)."""
    state = str(uuid.uuid4())

    resp = session.get(
        AUTHORIZE_URL,
        params={
            "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
            "response_type": "code",
            "scope": "openid",
            "state": state,
            "prompt": "select_account",
        },
        allow_redirects=False,
        timeout=15,
    )
    resp.raise_for_status()

    resp = session.get(resp.headers["Location"], allow_redirects=False, timeout=15)
    resp = session.get(resp.headers["Location"], allow_redirects=False, timeout=15)

    authn_url = resp.headers["Location"]
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
        r"'csrfToken'\s*:\s*'([^']{10,})'",
        r'<meta[^>]+name=["\']csrf-token["\'][^>]+content=["\']([^"\']+)["\']',
        r'csrf[_\-]?token["\']?\s*[:=]\s*["\']([A-Za-z0-9_\-\.]{10,})["\']',
    ):
        m = re.search(pattern, html, re.IGNORECASE)
        if m:
            return m.group(1)

    return None


def aftonbladet(email: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "accountExists": False,
        "userId": None,
        "raw": None,
    }

    session = requests.Session()
    session.headers.update(HEADERS)

    try:
        authn_url, html = _oauth_flow(session)
        csrf = _extract_csrf(html)

        if not csrf:
            r_csrf = session.get(
                "https://login.schibsted.com/authn/api/settings/csrf",
                params={"client_id": CLIENT_ID},
                headers={
                    "Accept": "application/json",
                    "Accept-Encoding": "gzip, deflate",
                    "Origin": "https://login.schibsted.com",
                    "Referer": authn_url,
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "same-origin",
                },
                timeout=10,
            )
            try:
                data_csrf = r_csrf.json()
            except Exception:
                data_csrf = {}
            csrf = (
                (data_csrf.get("data") or {}).get("attributes", {}).get("csrfToken")
                or data_csrf.get("csrfToken")
                or data_csrf.get("token")
            )
            if not csrf:
                result["raw"] = {
                    "error": "CSRF token not found",
                    "csrf_status": r_csrf.status_code,
                    "csrf_body": r_csrf.text[:400],
                }
                return result

        r2 = session.post(
            EMAIL_STATUS_URL,
            json={"email": email, "deviceData": DEVICE_DATA},
            headers={
                "x-csrf-token": csrf,
                "Origin": "https://login.schibsted.com",
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
    print(json.dumps(aftonbladet(email), indent=2))
