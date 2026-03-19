from __future__ import annotations

from typing import Any, Dict

import requests

FLOW_URL = "https://id.hemnet.se/self-service/login/browser"
LOGIN_URL = "https://id.hemnet.se/self-service/login"
RETURN_TO = "https://www.hemnet.se?authOrigin=navigation_menu"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Origin": "https://konto.hemnet.se",
    "Referer": "https://konto.hemnet.se/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
}

NOT_FOUND_MSG = "This account does not exist or has no login method configured."


def hemnet(email: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "accountExists": False,
        "raw": None,
    }

    try:
        session = requests.Session()
        session.headers.update(HEADERS)

        r1 = session.get(
            FLOW_URL,
            params={"return_to": RETURN_TO},
            headers={"Accept": "application/json"},
            allow_redirects=True,
            timeout=15,
        )
        r1.raise_for_status()
        flow = r1.json()

        flow_id = flow.get("id")
        if not flow_id:
            result["raw"] = {"error": "No flow ID in response", "body": flow}
            return result

        csrf_token = None
        for node in (flow.get("ui") or {}).get("nodes", []):
            attrs = node.get("attributes", {})
            if attrs.get("name") == "csrf_token" and attrs.get("type") == "hidden":
                csrf_token = attrs.get("value")
                break

        if not csrf_token:
            result["raw"] = {"error": "No csrf_token in flow nodes", "flow": flow}
            return result

        r2 = session.post(
            LOGIN_URL,
            params={"flow": flow_id},
            json={
                "csrf_token": csrf_token,
                "identifier": email,
                "method": "identifier_first",
            },
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            timeout=10,
        )

        data = r2.json()
        result["raw"] = data

        not_found = False
        for node in (data.get("ui") or {}).get("nodes", []):
            for msg in node.get("messages", []):
                if NOT_FOUND_MSG in msg.get("text", ""):
                    not_found = True
                    break

        result["accountExists"] = not not_found
        return result

    except Exception as e:
        result["raw"] = {"error": str(e)}
        return result


if __name__ == "__main__":
    import sys
    import json

    email = sys.argv[1] if len(sys.argv) > 1 else "test@example.com"
    print(json.dumps(hemnet(email), indent=2))
