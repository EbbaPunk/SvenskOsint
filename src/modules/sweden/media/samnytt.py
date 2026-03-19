from __future__ import annotations

import json
import re
import sys
from typing import Any, Dict

import requests

FORGOT_PASSWORD_URL = "https://samnytt.se/forgot-password"


ROUTER_STATE_TREE = "%5B%22%22%2C%7B%22children%22%3A%5B%22(auth)%22%2C%7B%22children%22%3A%5B%22forgot-password%22%2C%7B%22children%22%3A%5B%22__PAGE__%22%2C%7B%7D%2Cnull%2Cnull%2Cfalse%5D%7D%2Cnull%2Cnull%2Cfalse%5D%7D%2Cnull%2Cnull%2Cfalse%5D%7D%2Cnull%2Cnull%2Ctrue%5D"

_PAGE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
}


def _fetch_next_action() -> str:
    """Fetch the forgot-password page and extract the current Next.js server action hash.
    Falls back to the last known hash if extraction fails."""
    fallback = "40dede16822d95ed1c431c76acbe666ec9c909e959"
    try:
        r = requests.get(FORGOT_PASSWORD_URL, headers=_PAGE_HEADERS, timeout=10)

        matches = re.findall(r"\b([0-9a-f]{40})\b", r.text)
        if matches:
            return matches[0]
    except Exception:
        pass
    return fallback


def _parse_next_action_response(text: str) -> Dict | None:
    """Next.js server action responses are a stream of numbered JSON lines.
    We want the object that contains 'profileExists'."""
    for line in text.splitlines():
        m = re.match(r"^\d+:(.*)", line)
        if not m:
            continue
        try:
            obj = json.loads(m.group(1))
            if isinstance(obj, dict) and "profileExists" in obj:
                return obj
        except (json.JSONDecodeError, ValueError):
            continue
    return None


def samnytt(email: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "accountExists": False,
        "raw": None,
    }

    try:
        action = _fetch_next_action()
        r = requests.post(
            FORGOT_PASSWORD_URL,
            data=json.dumps([email]),
            headers={
                **_PAGE_HEADERS,
                "Accept": "text/x-component",
                "next-action": action,
                "next-router-state-tree": ROUTER_STATE_TREE,
                "Content-Type": "text/plain;charset=UTF-8",
                "Origin": "https://samnytt.se",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
            },
            timeout=15,
        )
        result["raw"] = r.text[:500]

        parsed = _parse_next_action_response(r.text)
        if parsed is None:
            result["raw"] = {"error": "unexpected response", "body": r.text[:500]}
            return result

        result["accountExists"] = bool(parsed.get("profileExists"))
        return result

    except Exception as e:
        result["raw"] = {"error": str(e)}
        return result


if __name__ == "__main__":
    email = sys.argv[1] if len(sys.argv) > 1 else "test@example.com"
    print(json.dumps(samnytt(email), indent=2))
