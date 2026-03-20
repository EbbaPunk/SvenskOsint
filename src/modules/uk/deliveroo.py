from __future__ import annotations

import uuid
from typing import Dict, Any

import requests


def deliveroo(email: str) -> Dict[str, Any]:
    result = {
        "exists": None,
        "rate_limited": False,
        "raw": None,
    }

    try:
        with requests.Session() as session:
            session.get(
                "https://deliveroo.co.uk/",
                headers={"User-Agent": "Mozilla/5.0", "Accept": "text/html"},
                timeout=15,
            )

            guid = str(uuid.uuid4())

            headers = {
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json, application/vnd.api+json",
                "Content-Type": "application/json",
                "Origin": "https://deliveroo.co.uk",
                "Referer": "https://deliveroo.co.uk/",
                "X-Roo-Client": "consumer-web-app",
                "X-Roo-Client-Referer": "https://deliveroo.co.uk/",
                "X-Roo-Country": "uk",
                "X-Roo-Guid": guid,
                "X-Roo-Platform": "web",
                "X-Roo-Session-Guid": str(uuid.uuid4()),
                "X-Roo-Sticky-Guid": guid,
            }

            r = session.post(
                "https://api.uk.deliveroo.com/consumer/accounts/check-email",
                headers=headers,
                json={
                    "email_address": email,
                    "redirect_path": "/",
                    "page_in_progress": "login",
                },
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

    if "registered" in data:
        result["exists"] = bool(data["registered"])
    else:
        result["rate_limited"] = True

    return result
