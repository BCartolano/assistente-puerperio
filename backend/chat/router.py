#!/usr/bin/env python3
"""Router Flask para intents do chatbot."""
from __future__ import annotations
import json
import logging
import os
import time
import traceback
from pathlib import Path
from typing import Any, Dict
from logging.handlers import RotatingFileHandler

from flask import Blueprint, request, jsonify

# Importa os handlers do chatbot
try:
    from chatbot.handlers import handle_intent, INTENT_MAP  # você já tem isso
except Exception as e:
    handle_intent = None
    INTENT_MAP = {}

CHAT_BP = Blueprint("chat", __name__, url_prefix="/api/v1/chat")

LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "chat_events.jsonl"

# Logger com rotação (max 5MB x 5 arquivos)
_chat_logger = logging.getLogger("chat.events")
_chat_logger.setLevel(logging.INFO)
_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=5 * 1024 * 1024,  # 5MB
    backupCount=5,
    encoding="utf-8"
)
_chat_logger.addHandler(_handler)
_chat_logger.propagate = False  # Evita duplicar logs no root logger

# Rate limit (opcional)
_RATE = {}
_RATE_WINDOW = 60  # s
_RATE_MAX = int(os.getenv("CHAT_RATE_MAX", "60"))


def _log_event(payload: Dict[str, Any], intent: str, text: str, ok: bool, meta: Dict[str, Any] | None = None):
    """Loga evento do chat em JSONL com rotação automática."""
    try:
        rec = {
            "ts": time.time(),
            "intent": intent,
            "ok": ok,
            "text": text,
            "meta": meta or {},
            "req": payload,
            "ip": request.headers.get("X-Forwarded-For", request.remote_addr),
            "user_id": request.headers.get("X-User-Id"),
        }
        _chat_logger.info(json.dumps(rec, ensure_ascii=False))
    except Exception:
        pass


@CHAT_BP.before_request
def rate_limit():
    """Rate limit simples por IP (opcional)."""
    if _RATE_MAX <= 0:
        return
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "")
    now = int(time.time())
    key = f"{ip}:{now//_RATE_WINDOW}"
    _RATE[key] = _RATE.get(key, 0) + 1
    if _RATE[key] > _RATE_MAX:
        return jsonify({"ok": False, "error": "rate limit"}), 429


@CHAT_BP.get("/ping")
def chat_ping():
    """Health check do chatbot."""
    return jsonify({
        "ok": True,
        "version": "sophia-chat-v1",
        "intents": sorted(list(INTENT_MAP.keys())) if INTENT_MAP else []
    })


@CHAT_BP.get("/intents")
def chat_intents():
    """Lista intents disponíveis."""
    return jsonify({
        "ok": True,
        "intents": sorted(list(INTENT_MAP.keys())) if INTENT_MAP else []
    })


@CHAT_BP.post("/intent")
def chat_intent():
    """Processa uma intent do chatbot."""
    if handle_intent is None:
        return jsonify({"ok": False, "error": "handlers indisponíveis"}), 500
    try:
        payload = request.get_json(force=True, silent=False) or {}
        intent = (payload.get("intent") or "").strip()
        slots = payload.get("slots") or {}

        if not intent:
            return jsonify({"ok": False, "error": "campo 'intent' é obrigatório"}), 400
        if intent not in INTENT_MAP:
            return jsonify({"ok": False, "error": f"intent desconhecida: {intent}"}), 400

        # slots de lat/lon (normalização simples)
        if "lat" in slots:
            try:
                slots["lat"] = float(slots["lat"])
            except Exception:
                pass
        if "lon" in slots:
            try:
                slots["lon"] = float(slots["lon"])
            except Exception:
                pass

        text = handle_intent(intent, slots)
        _log_event(payload, intent, text, ok=True)
        return jsonify({"ok": True, "intent": intent, "text": text})
    except Exception as e:
        tb = traceback.format_exc()
        _log_event(request.get_json(silent=True) or {}, "error", str(e), ok=False, meta={"trace": tb})
        return jsonify({"ok": False, "error": "erro ao processar a intent"}), 500
