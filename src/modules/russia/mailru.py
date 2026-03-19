from __future__ import annotations

import random
from typing import Dict, Any

import httpcloak


def mail_ru(email: str) -> Dict[str, Any]:
    result = {
        "exists": None,
        "rate_limited": False,
        "email_recovery": None,
        "phone_number": None,
        "raw": None,
    }

    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]

    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://account.mail.ru",
        "Referer": f"https://account.mail.ru/recovery?email={email}",
        "User-Agent": random.choice(user_agents),
        "Accept-Language": "ru",
    }

    try:
        with httpcloak.Session(preset="chrome-144") as session:
            r = session.post(
                "https://account.mail.ru/api/v1/user/password/restore",
                headers=headers,
                data={"email": email, "htmlencoded": "false"},
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

    if r.status_code != 200:
        result["rate_limited"] = True
        return result

    try:
        data = r.json()
    except Exception:
        result["rate_limited"] = True
        return result

    if data.get("status") == 200:
        result["exists"] = True
        phones = data.get("body", {}).get("phones", [])
        emails = data.get("body", {}).get("emails", [])
        result["phone_number"] = ", ".join(phones) if phones else None
        result["email_recovery"] = ", ".join(emails) if emails else None
    else:
        result["exists"] = False

    return result
