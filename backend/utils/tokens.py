# -*- coding: utf-8 -*-
import base64
import hmac
import hashlib
import json
import time
from typing import Optional, Dict


def _b(s):
    return s if isinstance(s, (bytes, bytearray)) else str(s).encode("utf-8")


def sign_token(data: Dict, secret: str, expires_sec: int = 86400) -> str:
    now = int(time.time())
    payload = dict(data or {})
    payload["iat"] = now
    payload["exp"] = now + int(expires_sec)
    raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    b64 = base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")
    sig = base64.urlsafe_b64encode(hmac.new(_b(secret), _b(b64), hashlib.sha256).digest()).decode("ascii").rstrip("=")
    return f"{b64}.{sig}"


def verify_token(token: str, secret: str) -> Optional[Dict]:
    if not token or "." not in token:
        return None
    b64, sig = token.rsplit(".", 1)
    expected = base64.urlsafe_b64encode(hmac.new(_b(secret), _b(b64), hashlib.sha256).digest()).decode("ascii").rstrip("=")
    if not hmac.compare_digest(expected, sig):
        return None
    pad = "=" * (-len(b64) % 4)
    try:
        payload = json.loads(base64.urlsafe_b64decode((b64 + pad).encode("ascii")).decode("utf-8"))
    except Exception:
        return None
    if int(payload.get("exp", 0)) < int(time.time()):
        return None
    return payload
