from __future__ import annotations

import base64
import os
import random
from typing import Any, Dict

import requests
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

CHECK_URL = "https://www.willys.se/login/pw/checkExistingCustomer"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-GB,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Content-Type": "application/json",
    "Origin": "https://www.willys.se",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}


def _js_random_chunk() -> str:
    digits = str(random.random())[2:]
    return (digits + "00000000")[:8]


def _encrypt(plaintext: str) -> tuple[str, str]:
    key = _js_random_chunk() + _js_random_chunk()
    iv = os.urandom(16)
    salt = os.urandom(16)

    kdf = PBKDF2HMAC(algorithm=hashes.SHA1(), length=16, salt=salt, iterations=1000)
    aes_key = kdf.derive(key.encode())

    padded = plaintext.encode()
    pad_len = 16 - (len(padded) % 16)
    padded += bytes([pad_len] * pad_len)

    encryptor = Cipher(algorithms.AES(aes_key), modes.CBC(iv)).encryptor()
    ciphertext_b64 = base64.b64encode(
        encryptor.update(padded) + encryptor.finalize()
    ).decode()

    aes_str = f"{iv.hex()}::{salt.hex()}::{ciphertext_b64}"
    encrypted = base64.b64encode(aes_str.encode()).decode()

    return key, encrypted


def willys(ssn: str) -> Dict[str, Any]:
    """Check if a Swedish personnummer is registered at Willys."""
    result: Dict[str, Any] = {
        "accountExists": False,
        "raw": None,
    }

    if not ssn:
        result["raw"] = {"error": "no personnummer provided"}
        return result

    try:
        key, encrypted_ssn = _encrypt(ssn)

        r = requests.post(
            CHECK_URL,
            json={
                "socialSecurityNumber": encrypted_ssn,
                "socialSecurityNumberKey": key,
            },
            headers=HEADERS,
            timeout=10,
        )

        data = r.json()
        result["raw"] = data

        if data.get("existingCustomer") or data.get("customerId") or data.get("email"):
            result["accountExists"] = True

        return result

    except Exception as e:
        result["raw"] = {"error": str(e)}
        return result


if __name__ == "__main__":
    import sys
    import json

    ssn = sys.argv[1] if len(sys.argv) > 1 else ""
    print(json.dumps(willys(ssn), indent=2))
