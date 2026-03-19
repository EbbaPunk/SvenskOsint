from __future__ import annotations

import random
import string
from typing import Dict, Any

import httpcloak


def random_username(length=10):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def devrant(email: str) -> Dict[str, Any]:
    result = {
        "exists": None,
        "rate_limited": False,
        "raw": None,
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://devrant.com",
        "Referer": "https://devrant.com/",
    }

    post_data = {
        "app": "3",
        "type": "1",
        "email": email,
        "username": random_username(),
        "password": "Password123!",
        "guid": "",
        "plat": "3",
        "sid": "",
        "seid": "",
    }

    try:
        with httpcloak.Session(preset="chrome-144") as session:
            r = session.post(
                "https://devrant.com/api/users",
                headers=headers,
                data=post_data,
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
        result["raw"] = {"error": "json_parse_failed"}
        return result

    result["raw"] = data

    if "already registered" in data.get("error", "").lower():
        result["exists"] = True
    else:
        result["exists"] = False

    return result
