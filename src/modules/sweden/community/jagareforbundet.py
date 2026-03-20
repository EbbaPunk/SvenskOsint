from __future__ import annotations

import re
from typing import Any, Dict

import requests

ENTRY_URL = "https://jagareforbundet.se/login/"
CHECK_URL = "https://login.jagareforbundet.se/Account/CheckUser"
LOGIN_HOST = "https://login.jagareforbundet.se"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
}


def _get_login_page(s: requests.Session) -> tuple[str, str, str]:
    r = s.get(ENTRY_URL, allow_redirects=True, timeout=15)
    login_url = r.url

    m = re.search(r"[?&]ReturnUrl=([^&]+)", login_url)
    return_url = m.group(1) if m else ""

    m = re.search(
        r'name=["\']__RequestVerificationToken["\'][^>]*value=["\']([^"\']+)["\']', r.text
    ) or re.search(
        r'value=["\']([^"\']+)["\'][^>]*name=["\']__RequestVerificationToken["\']', r.text
    )
    rvt = m.group(1) if m else ""

    return login_url, return_url, rvt


def _post(s: requests.Session, login_url: str, return_url: str, rvt: str, field: str, value: str) -> bool:
    r = s.post(
        CHECK_URL,
        data={
            "ReturnUrl": return_url,
            "button": field,
            "InputType": field,
            field: value,
            "__RequestVerificationToken": rvt,
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": LOGIN_HOST,
            "Referer": login_url,
            "Sec-Fetch-User": "?1",
        },
        allow_redirects=True,
        timeout=10,
    )
    return "Något blev fel" not in r.text


def jagareforbundet(value: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {"accountExists": False, "raw": None}

    if not value:
        result["raw"] = {"error": "no value provided"}
        return result

    try:
        s = requests.Session()
        s.headers.update(HEADERS)

        login_url, return_url, rvt = _get_login_page(s)
        if not rvt:
            result["raw"] = {"error": "RVT not found"}
            return result

        is_ssn = bool(re.match(r"^\d{6,8}-?\d{4}$", value))

        if is_ssn:
            found = _post(s, login_url, return_url, rvt, "PersonalIdentityNumber", value)
        else:
            found = _post(s, login_url, return_url, rvt, "Email", value)

        result["accountExists"] = found
        return result

    except Exception as e:
        result["raw"] = {"error": str(e)}
        return result


if __name__ == "__main__":
    import json
    import sys

    value = sys.argv[1] if len(sys.argv) > 1 else input("Email or SSN: ").strip()
    print(json.dumps(jagareforbundet(value), ensure_ascii=False, indent=2))
