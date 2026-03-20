from __future__ import annotations

from typing import Any, Dict

import requests

LOGIN_URL = "https://www.utsidan.se/login.htm"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Origin": "https://www.utsidan.se",
    "Referer": LOGIN_URL,
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
}


def utsidan(email: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {"accountExists": False, "raw": None}

    try:
        s = requests.Session()
        s.headers.update(HEADERS)
        s.get(LOGIN_URL, timeout=10)

        r = s.post(
            LOGIN_URL,
            data={
                "login": email,
                "password": "Dummy_pass1!",
                "persistent": "1",
                "_referer": "/",
            },
            allow_redirects=True,
            timeout=10,
        )
        with open("g.html", "w") as file:
            file.write(r.text)
        if "Anv&auml;ndaren finns ej" in r.text or "Användaren finns ej" in r.text:
            return result

        result["accountExists"] = True
        return result

    except Exception as e:
        result["raw"] = {"error": str(e)}
        return result


if __name__ == "__main__":
    import json
    import sys

    email = sys.argv[1] if len(sys.argv) > 1 else input("Email: ").strip()
    print(json.dumps(utsidan(email), ensure_ascii=False, indent=2))
