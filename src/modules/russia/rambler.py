from __future__ import annotations

from typing import Dict, Any

import httpcloak


def rambler(email: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "exists": None,
        "rate_limited": False,
        "raw": None,
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
        "Accept": "*/*",
        "Accept-Language": "en,en-US;q=0.5",
        "Referer": "https://id.rambler.ru/champ/registration",
        "Content-Type": "application/json",
        "Origin": "https://id.rambler.ru",
        "DNT": "1",
        "Connection": "keep-alive",
    }

    payload = {
        "method": "Rambler::Id::get_email_account_info",
        "params": [{"email": email}],
        "rpc": "2.0",
    }

    try:
        with httpcloak.Session(preset="chrome-144") as session:
            r = session.post(
                "https://id.rambler.ru/jsonrpc",
                headers=headers,
                json=payload,
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

    try:
        result["exists"] = bool(data["result"]["exists"])
    except Exception:
        result["rate_limited"] = True

    return result
