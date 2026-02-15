# -*- coding: utf-8 -*-
"""
Testes de smoke da API Flask: /api/v1/health e /api/v1/emergency/search.
Evita regressão do 404 quando as rotas não estão registradas.
"""
import os
import sys

import pytest

# Raiz do projeto
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    from backend.app import app as flask_app
except Exception:
    flask_app = None


@pytest.mark.skipif(flask_app is None, reason="Flask app indisponível neste ambiente")
def test_health_ok():
    """GET /api/v1/health retorna 200 com dataset e geo_health."""
    cli = flask_app.test_client()
    r = cli.get("/api/v1/health")
    assert r.status_code == 200
    data = r.get_json()
    assert data is not None
    assert "dataset" in data
    assert "geo_health" in data


@pytest.mark.skipif(flask_app is None, reason="Flask app indisponível neste ambiente")
def test_emergency_search_ok():
    """GET /api/v1/emergency/search retorna 200 ou 503 (se dataset faltar)."""
    cli = flask_app.test_client()
    r = cli.get(
        "/api/v1/emergency/search?lat=-23.55&lon=-46.63&radius_km=25&expand=true&limit=3"
    )
    # Se dataset faltar, aceita 503; senão deve ser 200
    assert r.status_code in (200, 503)
