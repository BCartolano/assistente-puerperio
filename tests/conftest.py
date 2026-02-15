# Fixtures compartilhadas para testes (classificador, API, data quality)
import os
import sys
import json

# Raiz do projeto
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(TESTS_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


def load_cnes_codes():
    path = os.path.join(BASE_DIR, "config", "cnes_codes.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# --- Fixtures QA (agente QA) ---

def fixture_hospital_com_leitos_obstetricos():
    """Hospital com leitos obstétricos → has_maternity true."""
    return {
        "cnes_id": "7000001",
        "fantasy_name": "Hospital Geral",
        "tipo_unidade": "07",
        "leitos": ["01", "02"],
        "servicos": ["125"],
        "classificacoes": ["001"],
        "habilitacoes": [],
    }


def fixture_hospital_so_ginecologia():
    """Hospital só com ginecologia (sem leito obstétrico) → false se não tiver serviço 125."""
    return {
        "cnes_id": "7000002",
        "fantasy_name": "Clínica Ginecológica",
        "tipo_unidade": "07",
        "leitos": [],
        "servicos": ["141"],
        "classificacoes": [],
        "habilitacoes": [],
    }


def fixture_hospital_da_mulher_sem_dados_fortes():
    """'Hospital da Mulher' sem dados fortes → provável (0.4–0.5)."""
    return {
        "cnes_id": "7000003",
        "fantasy_name": "Hospital da Mulher",
        "tipo_unidade": "07",
        "leitos": [],
        "servicos": [],
        "classificacoes": [],
        "habilitacoes": [],
    }


def fixture_maternidade_publica_sus():
    """Maternidade pública com SUS → atende_sus Sim."""
    return {
        "cnes_id": "7000004",
        "fantasy_name": "Maternidade Pública",
        "tipo_unidade": "05",
        "leitos": ["01", "02", "10"],
        "servicos": ["125"],
        "classificacoes": ["001"],
        "is_sus": True,
        "management": "MUNICIPAL",
    }


def fixture_privado_sem_sus():
    """Privado sem SUS → atende_sus Não."""
    return {
        "cnes_id": "7000005",
        "fantasy_name": "Hospital Privado",
        "tipo_unidade": "07",
        "leitos": ["01"],
        "servicos": ["125"],
        "classificacoes": ["001"],
        "is_sus": False,
        "management": "PRIVADO",
    }
