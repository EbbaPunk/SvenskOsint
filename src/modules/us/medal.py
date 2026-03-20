from __future__ import annotations

import re
from typing import Any, Dict

import requests


def medal(email: str) -> Dict[str, Any]:
    result = {
        "accountExists": False,
        "raw": None,
    }

    base_headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) "
            "Gecko/20100101 Firefox/140.0"
        ),
        "Accept-Language": "en-US,en;q=0.5",
    }

    try:
        with requests.Session() as session:
            r = session.get("https://medal.tv/login", headers=base_headers, timeout=5)

            mua_match = re.search(r'Medal-User-Agent["\s:]+["\']([^"\']+)', r.text)
            medal_ua = mua_match.group(1) if mua_match else "Medal-web/1.0"

            resp = session.post(
                "https://medal.tv/api/users/email",
                headers={
                    **base_headers,
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Referer": "https://medal.tv/login",
                    "Origin": "https://medal.tv",
                    "Medal-User-Agent": medal_ua,
                },
                json={"email": email},
                timeout=5,
            )

            raw = resp.json()
            result["raw"] = raw

            if raw.get("exists") is True or raw.get("status") == "registered":
                result["accountExists"] = True

    except Exception as e:
        result["raw"] = {"error": str(e)}

    return result
