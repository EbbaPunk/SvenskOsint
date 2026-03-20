from __future__ import annotations

import json
import re

import requests

CLIENT_ID        = "52454d279eaf7ced5d000000"
AUTHN_HOST       = "https://login.schibsted.com"
ENTRY_URL        = "https://www.omni.se/"
EMAIL_STATUS_URL = f"{AUTHN_HOST}/authn/api/identity/email-status?client_id={CLIENT_ID}"
CSRF_URL         = f"{AUTHN_HOST}/authn/api/settings/csrf?client_id={CLIENT_ID}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Upgrade-Insecure-Requests": "1",
}

DEVICE_DATA = {
    "fonts": [
        "Arial", "Arial Black", "Cambria Math", "Consolas", "Courier",
        "Courier New", "Georgia", "Helvetica", "Lucida Console", "MS Gothic",
        "MS PGothic", "MS Serif", "Segoe UI", "Segoe UI Light", "Segoe UI Semibold",
        "Tahoma", "Times", "Times New Roman", "Verdana",
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


def _extract_csrf(html: str) -> str | None:
    m = re.search(r'<div[^>]+id=["\']bffData["\'][^>]*>(.*?)</div>', html, re.DOTALL | re.IGNORECASE)
    if m:
        try:
            data = json.loads(m.group(1))
            token = data.get("csrfToken") or (data.get("initialData") or {}).get("csrfToken")
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


def omni(email: str) -> dict:
    s = requests.Session()
    s.headers.update(HEADERS)

    r = s.get(ENTRY_URL, allow_redirects=True, timeout=15)
    authn_url = r.url

    if AUTHN_HOST not in authn_url:
        authn_url = f"{AUTHN_HOST}/authn/email-login?client_id={CLIENT_ID}"
        r = s.get(authn_url, allow_redirects=True, timeout=15)
        authn_url = r.url

    csrf = _extract_csrf(r.text)

    if not csrf:
        r_csrf = s.get(
            CSRF_URL,
            headers={
                "Accept": "application/json",
                "Accept-Encoding": "gzip, deflate",
                "Origin": AUTHN_HOST,
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
        return {"found": False, "error": "CSRF token not found"}

    r2 = s.post(
        EMAIL_STATUS_URL,
        json={"email": email, "deviceData": DEVICE_DATA},
        headers={
            "X-CSRF-Token":    csrf,
            "Origin":          AUTHN_HOST,
            "Referer":         authn_url,
            "Accept":          "application/json",
            "Accept-Encoding": "gzip, deflate",
            "Content-Type":    "application/json",
            "Sec-Fetch-Dest":  "empty",
            "Sec-Fetch-Mode":  "cors",
            "Sec-Fetch-Site":  "same-origin",
        },
        timeout=10,
    )

    try:
        data = r2.json()
    except Exception:
        return {"found": False, "error": "non-JSON response", "body": r2.text[:300]}
  
    attrs = (data.get("data") or {}).get("attributes", {})
    found = bool(attrs.get("isExistingUser"))
    return {"found": found, "email": email, "raw": data} if found else {"found": False}


if __name__ == "__main__":
    import sys
    email = sys.argv[1] if len(sys.argv) > 1 else input("Email: ").strip()
    print(json.dumps(omni(email), ensure_ascii=False, indent=2))
