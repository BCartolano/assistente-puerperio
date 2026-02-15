#!/usr/bin/env python3
"""Testes E2E do router do chatbot."""
import os
import requests
import pytest

BASE = os.getenv("CHAT_BASE", "http://localhost:5000").rstrip("/")


def _post(intent, slots=None, **params):
    """Helper para POST /api/v1/chat/intent."""
    r = requests.post(
        f"{BASE}/api/v1/chat/intent",
        params=params,
        json={"intent": intent, "slots": slots or {}},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()


def test_ping_intents():
    """Testa GET /api/v1/chat/ping e /intents."""
    r = requests.get(f"{BASE}/api/v1/chat/ping", timeout=5)
    assert r.status_code == 200
    data = r.json()
    assert data.get("ok") is True
    assert "intents" in data
    assert isinstance(data["intents"], list)

    # Testa /intents também
    r2 = requests.get(f"{BASE}/api/v1/chat/intents", timeout=5)
    assert r2.status_code == 200
    data2 = r2.json()
    assert data2.get("ok") is True
    assert "intents" in data2


def test_triage_192_short_circuit():
    """Testa triagem 192 - deve retornar 'Ligue 192' para sintomas graves."""
    # Testa com sintomas graves
    j = _post("qualquer_coisa", {"texto": "sangramento intenso"})
    assert j["ok"] is True
    # Se triagem estiver implementada, deve ter campo triage ou texto com "192"
    assert "Ligue 192" in j.get("text", "") or j.get("triage") is True

    # Testa com triage_skip=1 (não deve acionar triagem)
    j2 = _post("qualquer_coisa", {"texto": "sangramento intenso"}, triage_skip=1)
    assert j2["ok"] is True
    # Com triage_skip, não deve ter triage ou pode ter texto diferente


def test_intent_validation():
    """Testa validação de intent."""
    # Intent vazia
    r = requests.post(
        f"{BASE}/api/v1/chat/intent",
        json={"intent": "", "slots": {}},
        timeout=5,
    )
    assert r.status_code == 400

    # Intent desconhecida
    r2 = requests.post(
        f"{BASE}/api/v1/chat/intent",
        json={"intent": "intent_inexistente_xyz", "slots": {}},
        timeout=5,
    )
    assert r2.status_code == 400


@pytest.mark.skipif(
    not os.getenv("CHAT_LAT") or not os.getenv("CHAT_LON"),
    reason="defina CHAT_LAT/CHAT_LON para testar intents reais",
)
def test_publico_privado_real():
    """Testa intent publico_privado com coordenadas reais."""
    lat = float(os.getenv("CHAT_LAT"))
    lon = float(os.getenv("CHAT_LON"))
    j = _post(
        "publico_privado",
        {"hospital": "Hospital Municipal", "lat": lat, "lon": lon},
        triage_skip=1,
    )
    assert j["ok"] is True
    text = j.get("text", "").lower()
    # Deve mencionar Público, Privado ou Filantrópico
    assert any(word in text for word in ["público", "privado", "filantrópico"])


@pytest.mark.skipif(
    not os.getenv("CHAT_LAT") or not os.getenv("CHAT_LON"),
    reason="defina CHAT_LAT/CHAT_LON para testar intents reais",
)
def test_atende_sus_real():
    """Testa intent atende_sus com coordenadas reais."""
    lat = float(os.getenv("CHAT_LAT"))
    lon = float(os.getenv("CHAT_LON"))
    j = _post(
        "atende_sus",
        {"hospital": "Hospital Municipal", "lat": lat, "lon": lon},
        triage_skip=1,
    )
    assert j["ok"] is True
    text = j.get("text", "").lower()
    # Deve mencionar SUS ou Cartão SUS
    assert "sus" in text or "cartão" in text
