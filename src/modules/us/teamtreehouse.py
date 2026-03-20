from __future__ import annotations

from bs4 import BeautifulSoup
from typing import Dict, Any

import requests


def teamtreehouse(email: str) -> Dict[str, Any]:
    result = {
        "exists": None,
        "rate_limited": False,
        "raw": None,
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://teamtreehouse.com/subscribe/new?trial=yes",
        "Origin": "https://teamtreehouse.com",
        "X-Requested-With": "XMLHttpRequest",
    }

    try:
        with requests.Session() as session:
            r = session.get(
                "https://teamtreehouse.com/subscribe/new?trial=yes",
                headers=headers,
                timeout=15,
            )

            soup = BeautifulSoup(r.text, "html.parser")
            token = soup.find(attrs={"name": "csrf-token"})["content"]
            headers["X-CSRF-Token"] = token

            r = session.post(
                "https://teamtreehouse.com/account/email_address",
                headers=headers,
                data={"email": email},
                timeout=15,
            )

            result["raw"] = r.text

            if "that email address is taken" in r.text.lower():
                result["exists"] = True
            elif '"success":true' in r.text:
                result["exists"] = False
            else:
                result["rate_limited"] = True

    except Exception as e:
        result["rate_limited"] = True
        result["raw"] = {"error": str(e)}

    return result
