from __future__ import annotations

import random
import string
from typing import Dict, Any

import requests


def lastpass(email: str) -> Dict[str, Any]:
    result = {
        "exists": None,
        "rate_limited": False,
        "raw": None,
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "*/*",
        "Accept-Language": "en,en-US;q=0.5",
        "Referer": "https://lastpass.com/",
        "X-Requested-With": "XMLHttpRequest",
        "DNT": "1",
        "Connection": "keep-alive",
    }

    def random_digits(length=30):
        return "".join(random.choice(string.digits) for _ in range(length))

    domain = email.split("@", 1)[1]
    fake_email = f"{random_digits()}@{domain}"
    url = "https://lastpass.com/create_account.php"

    try:
        with requests.Session() as session:
            r = session.get(
                url,
                params={
                    "check": "avail",
                    "skipcontent": "1",
                    "mistype": "1",
                    "username": fake_email,
                },
                headers=headers,
                timeout=15,
            )
            result["raw"] = {"backup": r.text}
            if r.text not in ("ok", "emailinvalid"):
                result["rate_limited"] = True
                result["exists"] = False
                return result

            r = session.get(
                url,
                params={
                    "check": "avail",
                    "skipcontent": "1",
                    "mistype": "1",
                    "username": email,
                },
                headers=headers,
                timeout=15,
            )
            result["raw"]["status"] = r.text
            if r.text == "no":
                result["exists"] = True
            elif r.text in ("ok", "emailinvalid"):
                result["exists"] = False
            else:
                result["rate_limited"] = True
                result["exists"] = False

    except Exception as e:
        result["rate_limited"] = True
        result["raw"] = {"error": str(e)}

    return result
