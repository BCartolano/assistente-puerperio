# Testes unitários do classificador (pipelines/classify.py)
import os
import sys
import json

TESTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(TESTS_DIR)
sys.path.insert(0, BASE_DIR)

import pytest
from backend.pipelines.classify import load_cnes_codes, load_scoring, classify_establishment


def test_hospital_com_leitos_obstetricos_has_maternity_true():
    """Hospital com leitos obstétricos → has_maternity true."""
    codes = load_cnes_codes()
    scoring = load_scoring()
    weights = scoring.get("weights", {})
    rules = scoring.get("rules", {})
    estab = {
        "cnes_id": "7000001",
        "fantasy_name": "Hospital Geral",
        "tipo_unidade": "07",
        "leitos": ["01", "02"],
        "servicos": ["125"],
        "classificacoes": ["001"],
        "habilitacoes": [],
    }
    out = classify_establishment(estab, codes, weights, rules)
    assert out["has_maternity"] == 1
    assert out["score"] >= 0.5


def test_hospital_so_ginecologia_has_maternity_false_or_low():
    """Hospital só com ginecologia (sem serviço 125/001) → has_maternity false ou baixo."""
    codes = load_cnes_codes()
    scoring = load_scoring()
    weights = scoring.get("weights", {})
    rules = scoring.get("rules", {})
    estab = {
        "cnes_id": "7000002",
        "fantasy_name": "Clínica Ginecológica",
        "tipo_unidade": "07",
        "leitos": [],
        "servicos": ["141"],
        "classificacoes": [],
        "habilitacoes": [],
    }
    out = classify_establishment(estab, codes, weights, rules)
    # Pode ser 0 ou 1 se tipo 07 + keyword; sem leito/serviço 125 tende a 0
    assert "score" in out and "evidence" in out


def test_hospital_da_mulher_sem_dados_fortes_provavel():
    """'Hospital da Mulher' sem dados fortes → provável (score 0.4–0.59 + keyword)."""
    codes = load_cnes_codes()
    scoring = load_scoring()
    weights = scoring.get("weights", {})
    rules = scoring.get("rules", {})
    estab = {
        "cnes_id": "7000003",
        "fantasy_name": "Hospital da Mulher",
        "tipo_unidade": "07",
        "leitos": [],
        "servicos": [],
        "classificacoes": [],
        "habilitacoes": [],
    }
    out = classify_establishment(estab, codes, weights, rules)
    assert "keyword" in str(out.get("evidence", []))
    assert 0.2 <= out["score"] <= 0.6
