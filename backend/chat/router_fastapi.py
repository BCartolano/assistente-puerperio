#!/usr/bin/env python3
"""Router FastAPI opcional para intents do chatbot."""
from __future__ import annotations
from typing import Optional, Dict, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Importa os handlers do chatbot
try:
    from chatbot.handlers import handle_intent, INTENT_MAP
except Exception:
    handle_intent = None
    INTENT_MAP = {}

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


class ChatReq(BaseModel):
    """Request model para chat intent."""
    intent: str
    slots: Optional[Dict[str, Any]] = {}


@router.get("/ping")
def ping():
    """Health check do chatbot."""
    return {
        "ok": True,
        "version": "sophia-chat-v1",
        "intents": sorted(list(INTENT_MAP.keys())) if INTENT_MAP else []
    }


@router.get("/intents")
def intents():
    """Lista intents disponíveis."""
    return {
        "ok": True,
        "intents": sorted(list(INTENT_MAP.keys())) if INTENT_MAP else []
    }


@router.post("/intent")
def chat_intent(req: ChatReq):
    """Processa uma intent do chatbot."""
    if handle_intent is None:
        raise HTTPException(status_code=500, detail="handlers indisponíveis")
    if req.intent not in INTENT_MAP:
        raise HTTPException(status_code=400, detail=f"intent desconhecida: {req.intent}")
    try:
        # Normaliza lat/lon se presente
        slots = req.slots or {}
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
        return {
            "ok": True,
            "intent": req.intent,
            "text": handle_intent(req.intent, slots)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="erro ao processar a intent")
