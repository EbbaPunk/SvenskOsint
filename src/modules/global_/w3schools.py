from __future__ import annotations

from typing import Dict, Any

import httpcloak


def w3schools(email: str) -> Dict[str, Any]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "*/*",
        "Content-Type": "application/json",
        "Origin": "https://www.w3schools.com",
        "Referer": "https://www.w3schools.com/",
    }

    result: Dict[str, Any] = {
        "exists": None,
        "extra": {},
        "raw": None,
    }

    try:
        with httpcloak.Session(preset="chrome-144") as session:
            response = session.post(
                "https://profile.w3schools.com/api/info",
                headers=headers,
                json={"email": email},
                timeout=15,
            )
    except Exception as e:
        result["raw"] = {"error": str(e)}
        return result

    if response.status_code != 200:
        result["exists"] = False
        result["raw"] = {"status_code": response.status_code}
        return result

    try:
        data = response.json()
    except Exception:
        result["rate_limited"] = True
        result["raw"] = {"error": "Invalid JSON"}
        return result

    result["raw"] = data

    if data.get("exists") == 1 and data.get("error.code") == "0":
        result["exists"] = True
        if data.get("username"):
            result["extra"]["username"] = data.get("username")
        if data.get("sub"):
            result["extra"]["user_id"] = data.get("sub")
        if data.get("status"):
            result["extra"]["status"] = data.get("status")
        if "email_verified" in data:
            result["extra"]["email_verified"] = data.get("email_verified")
        return result

    result["exists"] = False
    return result
