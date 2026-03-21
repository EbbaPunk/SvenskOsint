from __future__ import annotations

from typing import Any, Dict

import requests

CHECK_URL = "https://www.power.se/api/v2/mypower/customer/exists"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Content-Type": "application/json",
    "Origin": "https://www.power.se",
    "Referer": "https://www.power.se/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}


def power(email: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {"accountExists": False, "raw": None}

    try:
        r = requests.post(CHECK_URL, json={"input": email}, headers=HEADERS, timeout=10)
        result["raw"] = r.text.strip()
        result["accountExists"] = r.text.strip().lower() == "true"
        return result

    except Exception as e:
        result["raw"] = {"error": str(e)}
        return result


if __name__ == "__main__":
    import sys
    import json
    email = sys.argv[1] if len(sys.argv) > 1 else input("Email: ").strip()
    print(json.dumps(power(email), ensure_ascii=False, indent=2))
