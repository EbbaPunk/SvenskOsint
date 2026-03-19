from __future__ import annotations

import re
from bs4 import BeautifulSoup
from typing import Dict, Any

import httpcloak

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


def vimeo(email: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "exists": None,
        "rate_limited": False,
        "raw": None,
    }

    try:
        with httpcloak.Session(preset="firefox-133") as session:

            try:
                get_resp = session.get(
                    "https://vimeo.com/join",
                    headers=_HEADERS,
                    timeout=15,
                )
            except Exception as e:
                result["rate_limited"] = True
                result["raw"] = {"error": str(e)}
                return result

            token = None

            try:
                soup = BeautifulSoup(get_resp.text, "html.parser")
                inp = soup.find("input", {"name": "token"})
                if inp:
                    token = inp.get("value")
            except Exception:
                pass

            if not token:
                for pattern in (r'"xsrft"\s*:\s*"([^"]+)"', r'"token"\s*:\s*"([^"]+)"'):
                    m = re.search(pattern, get_resp.text)
                    if m:
                        token = m.group(1)
                        break

            if not token:
                result["rate_limited"] = True
                result["raw"] = {"error": "xsrf_token_not_found"}
                return result

            post_headers = {
                **_HEADERS,
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://vimeo.com",
                "Referer": "https://vimeo.com/join",
            }

            try:
                post_resp = session.post(
                    "https://vimeo.com/join",
                    headers=post_headers,
                    data={
                        "email": email,
                        "token": token,
                        "action": "join",
                        "service": "vimeo",
                        "email_validation": "true",
                    },
                    timeout=15,
                )
            except Exception as e:
                result["rate_limited"] = True
                result["raw"] = {"error": str(e)}
                return result

            result["raw"] = {"status": post_resp.status_code}

            try:
                data = post_resp.json()
                result["raw"]["body"] = data
            except Exception:
                result["raw"]["body"] = post_resp.text[:300]
                result["rate_limited"] = True
                return result

            if post_resp.status_code == 429:
                result["rate_limited"] = True
                return result

            if isinstance(data, dict):
                err = data.get("err", "")
                if "already" in str(err).lower() or "taken" in str(err).lower():
                    result["exists"] = True
                elif data.get("success") or post_resp.status_code == 200 and not err:
                    result["exists"] = False
                elif "display_message" in data:
                    result["rate_limited"] = True

    except Exception as e:
        result["rate_limited"] = True
        result["raw"] = {"error": str(e)}

    return result
