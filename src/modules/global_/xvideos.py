from __future__ import annotations

from typing import Dict, Any

import httpcloak


def xvideos(email: str) -> Dict[str, Any]:
    result = {
        "exists": None,
        "rate_limited": False,
        "raw": None,
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.xvideos.com/",
    }

    try:
        with httpcloak.Session(preset="chrome-144") as session:
            r = session.get(
                "https://www.xvideos.com/account/checkemail",
                headers=headers,
                params={"email": email},
                timeout=15,
            )
    except Exception as e:
        result["rate_limited"] = True
        result["raw"] = {"error": str(e)}
        return result

    try:
        data = r.json()
    except Exception:
        result["rate_limited"] = True
        result["raw"] = {"error": "json_parse_failed", "text": r.text[:300]}
        return result

    result["raw"] = data

    if data.get("result") is False and "already in use" in r.text.lower():
        result["exists"] = True
    else:
        result["exists"] = False

    return result
