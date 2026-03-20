from __future__ import annotations

from typing import Dict, Any

import requests


def vivino(email: str) -> Dict[str, Any]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json",
        "Referer": "https://www.vivino.com/",
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
    }

    result: Dict[str, Any] = {
        "exists": None,
        "rate_limited": False,
        "raw": None,
    }

    try:
        with requests.Session() as session:
            r = session.post(
                "https://www.vivino.com/api/login",
                headers=headers,
                json={"email": email, "password": "x"},
                timeout=10,
            )
    except Exception as e:
        result["rate_limited"] = True
        result["raw"] = {"error": str(e)}
        return result

    if r.status_code == 429:
        result["rate_limited"] = True
        return result

    try:
        data = r.json()
    except Exception:
        result["rate_limited"] = True
        result["raw"] = r.text
        return result

    result["raw"] = data

    if data.get("error") == "The supplied email does not exist":
        result["exists"] = False
    else:
        result["exists"] = True

    return result
