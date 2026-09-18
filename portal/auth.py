from __future__ import annotations

import base64
import hashlib
import hmac
import os
from dataclasses import dataclass

ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 260_000


@dataclass(frozen=True)
class Viewer:
    user_id: str
    player_name: str
    character_name: str | None
    role: str

    @property
    def is_dm(self) -> bool:
        return self.role == "dm"


def hash_pin(pin: str, *, salt: bytes | None = None, iterations: int = ITERATIONS) -> str:
    if not pin or len(pin) < 4:
        raise ValueError("PIN must contain at least 4 characters")
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", pin.encode("utf-8"), salt, iterations)
    return f"{ALGORITHM}${iterations}${base64.urlsafe_b64encode(salt).decode()}${base64.urlsafe_b64encode(digest).decode()}"


def verify_pin(pin: str, encoded: str) -> bool:
    try:
        algorithm, iterations_text, salt_text, expected_text = encoded.split("$", 3)
        if algorithm != ALGORITHM:
            return False
        iterations = int(iterations_text)
        salt = base64.urlsafe_b64decode(salt_text.encode())
        expected = base64.urlsafe_b64decode(expected_text.encode())
    except (ValueError, TypeError):
        return False
    actual = hashlib.pbkdf2_hmac("sha256", pin.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(actual, expected)
