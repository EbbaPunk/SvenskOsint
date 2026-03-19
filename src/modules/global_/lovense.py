from __future__ import annotations

import re
from typing import Any, Dict

import httpcloak


def lovense(email: str) -> Dict[str, Any]:
    result = {
        "accountExists": False,
        "raw": None,
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "*/*",
    }

    signup_url = "https://www.lovense.com/signin?type=signUp"

    try:
        with httpcloak.Session(preset="chrome-144") as session:
            r = session.get(signup_url, headers=headers, timeout=5)

            m = re.search(r'crsf_token["\']?\s*[:=]\s*["\']([^"\']+)', r.text)
            if not m:
                return result

            csrf = m.group(1)

            resp = session.post(
                "https://www.lovense.com/ajaxCheckIdentityRegisted",
                headers={
                    **headers,
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "Origin": "https://www.lovense.com",
                    "Referer": signup_url,
                    "X-Requested-With": "XMLHttpRequest",
                },
                data={
                    "identity": email,
                    "type": "email",
                    "crsf_token": csrf,
                },
                timeout=5,
            )

            try:
                raw = resp.json()
            except Exception:
                return result

            result["raw"] = raw

            if (
                raw.get("result") is True
                and raw.get("code") == 2001
                and "already exists" in raw.get("message", "").lower()
            ):
                result["accountExists"] = True

    except Exception as e:
        result["raw"] = {"error": str(e)}

    return result
