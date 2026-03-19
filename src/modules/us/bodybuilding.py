from __future__ import annotations

import random
from typing import Dict, Any

import httpcloak


def bodybuilding(email: str) -> Dict[str, Any]:
    result = {
        "exists": None,
        "rate_limited": False,
        "raw": None,
    }

    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
    ]

    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en,en-US;q=0.5",
        "Origin": "https://www.bodybuilding.com",
        "Referer": "https://www.bodybuilding.com/",
        "DNT": "1",
        "Connection": "keep-alive",
    }

    try:
        with httpcloak.Session(preset="chrome-144") as session:
            r = session.head(
                f"https://api.bodybuilding.com/profile/email/{email}",
                headers=headers,
                timeout=15,
            )

            result["raw"] = {"status_code": r.status_code}

    except Exception as e:
        result["rate_limited"] = True
        result["raw"] = {"error": str(e)}
        return result

    if r.status_code == 200:
        result["exists"] = True
    elif r.status_code == 404:
        result["exists"] = False
    elif r.status_code == 429:
        result["rate_limited"] = True
    else:
        result["exists"] = False

    return result
