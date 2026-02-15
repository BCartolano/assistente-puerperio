# Contract tests para GET /v1/emergency/search e GET /v1/establishments/{cnes_id}
import os
import sys
import json

TESTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(TESTS_DIR)
sys.path.insert(0, BASE_DIR)

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from backend.api.main import app
    return TestClient(app)


def test_emergency_search_contract_meta_and_results(client):
    """GET /api/v1/emergency/search retorna meta e results."""
    # Pode falhar se não houver DB; então verificamos estrutura quando 200
    r = client.get("/api/v1/emergency/search", params={"lat": -23.55, "lon": -46.63, "limit": 3})
    if r.status_code == 200:
        data = r.json()
        assert "meta" in data
        assert "results" in data
        assert "legal_disclaimer" in data["meta"]
        assert "total_results" in data["meta"]
        assert isinstance(data["results"], list)
    else:
        # 503 sem DB é aceitável em ambiente de teste
        assert r.status_code in (200, 503)


def test_establishments_cnes_id_contract(client):
    """GET /api/v1/establishments/{cnes_id} retorna id, name, maternity_status, atende_sus, esfera."""
    r = client.get("/api/v1/establishments/1234567")
    if r.status_code == 200:
        data = r.json()
        assert "id" in data
        assert "name" in data
        assert "maternity_status" in data
        assert data["maternity_status"] in ("Sim", "Provável", "Não listado")
        assert "atende_sus" in data
        assert "esfera" in data
    else:
        assert r.status_code in (200, 404, 503)


def test_health_contract(client):
    """GET /api/v1/facilities/health retorna status."""
    r = client.get("/api/v1/facilities/health")
    assert r.status_code in (200, 503)
    if r.status_code == 200:
        assert r.json().get("status") in ("ok", "healthy")


def test_version_contract(client):
    """GET /api/v1/version retorna version e api_name."""
    r = client.get("/api/v1/version")
    assert r.status_code == 200
    data = r.json()
    assert "version" in data
    assert "api_name" in data
