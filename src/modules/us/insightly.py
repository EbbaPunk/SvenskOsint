from __future__ import annotations

from typing import Dict, Any

import httpcloak


def insightly(email: str) -> Dict[str, Any]:
    result = {
        "exists": None,
        "rate_limited": False,
        "raw": None,
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://accounts.insightly.com",
        "Referer": "https://accounts.insightly.com/?plan=trial",
    }

    try:
        with httpcloak.Session(preset="chrome-144") as session:
            r = session.post(
                "https://accounts.insightly.com/signup/isemailvalid",
                headers=headers,
                data={"emailaddress": email},
                timeout=15,
            )
    except Exception as e:
        result["rate_limited"] = True
        result["raw"] = {"error": str(e)}
        return result

    text = r.text.strip()
    result["raw"] = text

    if "account exists for this address" in text.lower():
        result["exists"] = True
    elif text == "true":
        result["exists"] = False
    else:
        result["rate_limited"] = True

    return result
