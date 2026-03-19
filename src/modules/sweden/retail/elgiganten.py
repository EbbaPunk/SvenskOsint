from __future__ import annotations

import re
from typing import Any, Dict

import requests

LOGIN_ENTRY = "https://elgiganten.se/login?return-path=%2F&userOrigin=HOME"
B2C_BASE = "https://account.elgiganten.se/022d6ac2-09a5-4dc2-afdd-7f37b0bedfd6"
POLICY = "B2C_1A_SuSi_B2C"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
}


def elgiganten(email: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {"accountExists": False, "raw": None}

    try:
        s = requests.Session()
        s.headers.update(HEADERS)

        r = s.get(LOGIN_ENTRY, allow_redirects=True, timeout=15)

        tx_match = re.search(
            r'"transId"\s*:\s*"(StateProperties=[^"]+)"', r.text
        ) or re.search(r"[?&]tx=(StateProperties=[^&\"'\s]+)", r.url + " " + r.text)
        if not tx_match:
            result["raw"] = {"error": "tx param not found", "url": r.url}
            return result
        tx = tx_match.group(1)

        csrf = s.cookies.get("x-ms-cpim-csrf")
        if not csrf:
            csrf_match = re.search(r'"csrf"\s*:\s*"([^"]+)"', r.text)
            if csrf_match:
                csrf = csrf_match.group(1)
        if not csrf:
            result["raw"] = {"error": "x-ms-cpim-csrf cookie missing"}
            return result

        post_url = f"{B2C_BASE}/{POLICY}/SelfAsserted?tx={tx}&p={POLICY}"
        r2 = s.post(
            post_url,
            data={
                "request_type": "RESPONSE",
                "signInName": email,
                "password": "Dummy_pass1!",
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "X-CSRF-TOKEN": csrf,
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://account.elgiganten.se",
                "Referer": r.url,
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
            },
            timeout=10,
        )

        data = r2.json()
        result["raw"] = data

        code = data.get("errorCode", "")

        if (
            code in ("AADB2C90225", "AADB2C90286", "AADB2C90054")
            or data.get("status") == "200"
        ):
            result["accountExists"] = True

        return result

    except Exception as e:
        result["raw"] = {"error": str(e)}
        return result


if __name__ == "__main__":
    import json
    import sys

    email = sys.argv[1] if len(sys.argv) > 1 else input("Email: ").strip()
    print(json.dumps(elgiganten(email), ensure_ascii=False, indent=2))
