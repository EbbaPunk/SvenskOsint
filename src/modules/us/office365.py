from __future__ import annotations

import random
import string
from typing import Dict, Any

import httpcloak


def office365(email: str) -> Dict[str, Any]:
    result = {
        "exists": None,
        "rate_limited": False,
        "raw": None,
    }

    headers = {
        "User-Agent": "Microsoft Office/16.0 (Windows NT 10.0; Microsoft Outlook 16.0.12026; Pro)",
        "Accept": "application/json",
    }

    def random_digits(length=30):
        return "".join(random.choice(string.digits) for _ in range(length))

    domain = email.split("@", 1)[1]
    fake_email = f"{random_digits()}@{domain}"

    url = (
        "https://outlook.office365.com/"
        "autodiscover/autodiscover.json/v1.0/{}"
        "?Protocol=Autodiscoverv1"
    )

    try:
        with httpcloak.Session(preset="chrome-144") as session:
            r = session.get(
                url.format(fake_email),
                headers=headers,
                allow_redirects=False,
                timeout=15,
            )
            result["raw"] = {"backup": r.status_code}

            if r.status_code != 200:
                r = session.get(
                    url.format(email),
                    headers=headers,
                    allow_redirects=False,
                    timeout=15,
                )
                result["raw"]["status"] = r.status_code
                result["exists"] = r.status_code == 200
            else:
                result["rate_limited"] = True
                result["exists"] = False

    except Exception as e:
        result["rate_limited"] = True
        result["raw"] = {"error": str(e)}

    return result
