from __future__ import annotations

import random
from typing import Dict, Any

import httpcloak


def freelancer(email: str) -> Dict[str, Any]:
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
        "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/json",
        "Origin": "https://www.freelancer.com",
        "DNT": "1",
        "Connection": "keep-alive",
    }

    try:
        with httpcloak.Session(preset="chrome-144") as session:
            r = session.post(
                "https://www.freelancer.com/api/users/0.1/users/check?compact=true&new_errors=true",
                headers=headers,
                json={"user": {"email": email}},
                timeout=15,
            )

            result["raw"] = {
                "status_code": r.status_code,
                "body": r.text,
            }

    except Exception as e:
        result["rate_limited"] = True
        result["raw"] = {"error": str(e)}
        return result

    if r.status_code == 409 and "EMAIL_ALREADY_IN_USE" in r.text:
        result["exists"] = True
    elif r.status_code == 200:
        result["exists"] = False
    elif r.status_code == 429:
        result["rate_limited"] = True
    else:
        result["rate_limited"] = True

    return result
