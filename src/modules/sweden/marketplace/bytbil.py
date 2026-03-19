from __future__ import annotations

import json
import re
from typing import Any, Dict

import requests

CLIENT_ID = "5a37ad0b3791020e7966da23"
ENTRY_URL = "https://www.bytbil.com/logga-in"
AUTHN_HOST = "https://login.vend.se"
EMAIL_STATUS_URL = f"{AUTHN_HOST}/authn/api/identity/email-status?client_id={CLIENT_ID}"
CSRF_URL = f"{AUTHN_HOST}/authn/api/settings/csrf?client_id={CLIENT_ID}"

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


def bytbil(email: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {"accountExists": False, "raw": None}

    try:
        s = requests.Session()
        s.headers.update(HEADERS)

        r = s.get(ENTRY_URL, allow_redirects=True, timeout=15)
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
            result["raw"] = {"error": "CSRF token not found"}
            return result

        r2 = s.post(
            EMAIL_STATUS_URL,
            json={"email": email, "deviceData": DEVICE_DATA},
            headers={
                "x-csrf-token": csrf,
                "Origin": AUTHN_HOST,
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

        attrs = (data.get("data") or {}).get("attributes", {})
        result["accountExists"] = bool(attrs.get("isExistingUser"))

        return result

    except Exception as e:
        result["raw"] = {"error": str(e)}
        return result


if __name__ == "__main__":
    import sys

    email = sys.argv[1] if len(sys.argv) > 1 else input("Email: ").strip()
    print(json.dumps(bytbil(email), ensure_ascii=False, indent=2))
