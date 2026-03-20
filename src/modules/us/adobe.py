from __future__ import annotations

import random
from typing import Any, Dict

import requests

CHROME_UAS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]


def adobe(email: str) -> Dict[str, Any]:
    result = {
        "accountExists": False,
        "emailRecovery": None,
        "phoneNumber": None,
        "raw": None,
    }

    headers = {
        "User-Agent": random.choice(CHROME_UAS),
        "Accept": "application/json, text/plain, */*",
        "X-IMS-CLIENTID": "adobedotcom2",
        "Content-Type": "application/json;charset=utf-8",
        "Origin": "https://auth.services.adobe.com",
    }

    try:
        r = requests.post(
            "https://auth.services.adobe.com/signin/v1/authenticationstate",
            headers=headers,
            json={"username": email, "accountType": "individual"},
            timeout=10,
        )

        state = r.json()
        result["raw"] = {"authenticationState": state}

        if "errorCode" in state:
            return result

        headers["X-IMS-Authentication-State-Encrypted"] = r.headers.get(
            "x-ims-authentication-state-encrypted"
        )

        response = requests.get(
            "https://auth.services.adobe.com/signin/v2/challenges",
            headers=headers,
            params={"purpose": "passwordRecovery"},
            timeout=10,
        )

        challenges = response.json()
        result["raw"]["challenges"] = challenges

        result["accountExists"] = True
        result["emailRecovery"] = challenges.get("secondaryEmail")
        result["phoneNumber"] = challenges.get("securityPhoneNumber")

        return result

    except Exception as e:
        result["raw"] = {"error": str(e)}
        return result
