from __future__ import annotations

from typing import Dict, Any

import httpcloak


def flickr(email: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "exists": None,
        "rate_limited": False,
        "raw": None,
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://identity.flickr.com/login",
        "Origin": "https://identity.flickr.com",
    }

    try:
        with httpcloak.Session(preset="chrome-144") as session:
            r = session.get(
                "https://identity-api.flickr.com/migration",
                params={"email": email},
                headers=headers,
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
        result["raw"] = r.text[:500]
        return result

    result["raw"] = data

    if data.get("state_code") == "5":
        result["exists"] = True
    else:
        result["exists"] = False

    return result
