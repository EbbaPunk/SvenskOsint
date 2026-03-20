from __future__ import annotations

import typing
from json import loads

import requests


def microsoft_recovery(target: str) -> dict[str, typing.Any]:
    result: dict[str, typing.Any] = {
        "accountExists": False,
        "backupEmail": None,
        "phones": [],
        "securityQuestion": None,
        "twoFA": False,
        "raw": [],
    }

    try:
        with requests.Session() as session:
            resp = session.get(
                "https://account.live.com/ResetPassword.aspx",
                params={"mn": target},
                headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "User-Agent": "Mozilla/5.0 (XboxReplay; XboxLiveAuth/3.0)",
                },
                timeout=5,
            )

            try:
                raw = loads(
                    f"""[{resp.text.split('"oProofList":[')[1].split("],")[0]}]"""
                )
            except Exception:
                return result

            result["accountExists"] = True
            result["raw"] = raw

            for item in raw:
                match item.get("type"):
                    case "Email":
                        if "*" in item["name"]:
                            result["backupEmail"] = item["name"]
                    case "Sms":
                        result["phones"].append(item["name"])
                    case "SQSA":
                        result["securityQuestion"] = item["name"]
                    case "TOTPAuthenticatorV2":
                        result["twoFA"] = True

    except Exception:
        pass

    return result
