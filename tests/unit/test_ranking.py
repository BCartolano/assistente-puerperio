# Testes unitários do ranking (ranking/selector.py)
import os
import sys

TESTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(TESTS_DIR)
sys.path.insert(0, BASE_DIR)

import pytest
from backend.ranking.selector import select_top_n, haversine_km


def test_haversine_km():
    """Distância Haversine entre dois pontos."""
    # São Paulo ~ -23.55, -46.63
    d = haversine_km(-23.55, -46.63, -23.55, -46.64)
    assert d > 0 and d < 20


def test_select_top_n_prioriza_has_maternity():
    """Prioridade: has_maternity true > distância."""
    user_lat, user_lon = -23.55, -46.63
    establishments = [
        {"id": "2", "lat": -23.56, "long": -46.64, "has_maternity": False, "name": "Longe"},
        {"id": "1", "lat": -23.551, "long": -46.631, "has_maternity": True, "name": "Perto com maternidade"},
    ]
    top = select_top_n(establishments, user_lat, user_lon, n=2)
    assert len(top) == 2
    assert top[0].get("has_maternity") or top[0].get("name") == "Perto com maternidade"
    assert "distance_km" in top[0]


def test_select_top_n_respeita_limit():
    """Retorna no máximo n itens."""
    establishments = [
        {"id": str(i), "lat": -23.55 + i * 0.01, "long": -46.63, "has_maternity": True}
        for i in range(5)
    ]
    top = select_top_n(establishments, -23.55, -46.63, n=3)
    assert len(top) == 3
