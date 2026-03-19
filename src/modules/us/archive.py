from __future__ import annotations

from typing import Dict, Any

import httpcloak


def archive(email: str) -> Dict[str, Any]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Origin": "https://archive.org",
        "Referer": "https://archive.org/account/signup",
        "Accept-Language": "en-US,en;q=0.9",
    }

    data = {
        "input_name": "username",
        "input_value": email,
        "input_validator": "true",
        "submit_by_js": "true",
    }

    result: Dict[str, Any] = {
        "exists": None,
        "rate_limited": False,
        "raw": None,
    }

    try:
        with httpcloak.Session(preset="chrome-144") as session:
            r = session.post(
                "https://archive.org/account/signup",
                headers=headers,
                data=data,
                timeout=10,
            )
    except Exception as e:
        result["rate_limited"] = True
        result["raw"] = {"error": str(e)}
        return result

    result["raw"] = r.text

    if r.status_code != 200:
        result["exists"] = False
        return result

    if "is already taken" in r.text.lower():
        result["exists"] = True
        return result

    result["exists"] = False
    return result
