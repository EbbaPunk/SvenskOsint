from __future__ import annotations

from typing import Any, Dict

import httpcloak


def bibledotcom(email: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "accountExists": False,
        "raw": None,
    }

    try:
        r = httpcloak.post(
            "https://presentation.youversionapi.com/graphql",
            json={
                "query": """
                mutation ForgotPassword($email: String) {
                  forgotPassword(usersPasswordEmailInput: {email: $email}) {
                    response {
                      data {
                        email
                      }
                    }
                  }
                }
                """,
                "variables": {"email": email},
            },
            timeout=5,
        )

        raw = r.json()
        result["raw"] = raw

        if (
            raw.get("data")
            and raw["data"].get("forgotPassword")
            and raw["data"]["forgotPassword"]
            .get("response", {})
            .get("data", {})
            .get("email")
        ):
            result["accountExists"] = True

        elif raw.get("errors"):
            for err in raw["errors"]:
                response_body = (
                    err.get("extensions", {})
                    .get("responseBody", {})
                    .get("response", {})
                    .get("data", {})
                )
                errors = response_body.get("errors", [])
                if any(
                    e.get("key") == "users.email_or_username.not_found" for e in errors
                ):
                    result["accountExists"] = False

        return result

    except Exception as e:
        result["raw"] = {"error": str(e)}
        return result
