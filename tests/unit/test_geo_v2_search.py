import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from backend.api.routes import geo_v2_search_core, _esfera_override, _sus_badge

# user em SP
U_LAT, U_LON = -23.55, -46.63


def _df_base():
    # A = confirmado perto; B = provável perto; C = geral longe
    rows = [
        # Confirmado (A) ~10km
        {"cnes_id": "A1", "nome": "Hospital Maternidade Alfa", "esfera": "Público", "atende_sus": "Sim",
         "has_maternity": True, "is_probable": False, "score": 0.7, "telefone": "1130456789", "telefone_formatado": "+55 (11) 3045-6789", "phone_e164": "+551130456789",
         "endereco": "Rua A, 100 – Centro, São Paulo/SP, CEP 01000-000", "lat": -23.62, "lon": -46.64},
        # Provável (B) ~10km
        {"cnes_id": "B1", "nome": "Hospital e Maternidade Beta", "esfera": "Privado", "atende_sus": "Não",
         "has_maternity": False, "is_probable": True, "score": 0.5, "telefone": "11987654321", "telefone_formatado": "+55 (11) 98765-4321", "phone_e164": "+5511987654321",
         "endereco": "Rua B, 200 – Centro, São Paulo/SP, CEP 01000-000", "lat": -23.62, "lon": -46.62},
        # Geral (C) longe ~150km
        {"cnes_id": "C1", "nome": "Hospital Geral Gama", "esfera": "Privado", "atende_sus": "Não",
         "has_maternity": False, "is_probable": False, "score": 0.1, "telefone": "1122223333", "telefone_formatado": "+55 (11) 2222-3333", "phone_e164": "+551122223333",
         "endereco": "Rua C, 300 – Centro, Campinas/SP, CEP 13000-000", "lat": -22.90, "lon": -47.06},
        {"cnes_id": "C2", "nome": "Hospital Geral Delta", "esfera": "Público", "atende_sus": "Sim",
         "has_maternity": False, "is_probable": False, "score": 0.1, "telefone": "1133334444", "telefone_formatado": "+55 (11) 3333-4444", "phone_e164": "+551133334444",
         "endereco": "Rua D, 400 – Centro, Campinas/SP, CEP 13000-000", "lat": -22.91, "lon": -47.06},
        {"cnes_id": "C3", "nome": "Hospital Geral Épsilon", "esfera": "Público", "atende_sus": "Sim",
         "has_maternity": False, "is_probable": False, "score": 0.1, "telefone": "1133335555", "telefone_formatado": "+55 (11) 3333-5555", "phone_e164": "+551133335555",
         "endereco": "Rua E, 500 – Centro, Campinas/SP, CEP 13000-000", "lat": -22.92, "lon": -47.06},
    ]
    return pd.DataFrame(rows)


def test_quando_ha_A_a_10_km_retorna_A():
    df = _df_base()
    res, banner, *rest = geo_v2_search_core(df, U_LAT, U_LON, None, 25, True, 3)
    assert len(res) >= 1
    assert res[0]["label_maternidade"] == "Ala de Maternidade"
    assert banner is False  # Não houve fallback C, só A/B
    if rest:
        meta = rest[0]
        assert meta.get("completed_with_group_C") == banner


def test_quando_so_B_a_10_km_retorna_B_provavel():
    df = _df_base()
    df = df[df["cnes_id"] != "A1"].copy()
    res, banner, *rest = geo_v2_search_core(df, U_LAT, U_LON, None, 25, True, 3)
    assert len(res) >= 1
    assert "Provável maternidade" in res[0]["label_maternidade"]
    assert banner is False  # Não houve fallback C, só B
    if rest:
        meta = rest[0]
        assert meta.get("completed_with_group_C") == banner


def test_nao_ha_AB_ate_25_mas_ha_A_a_60_expand_retorna_A():
    df = _df_base()
    df.loc[df["cnes_id"] == "A1", ["lat", "lon"]] = (-23.05, -46.30)
    df = df[df["cnes_id"] != "B1"].copy()
    res, banner, *rest = geo_v2_search_core(df, U_LAT, U_LON, None, 25, True, 3)
    assert any(r["cnes_id"] == "A1" for r in res)
    assert banner is False  # Não houve fallback C, expandiu raio e encontrou A
    if rest:
        meta = rest[0]
        assert meta.get("completed_with_group_C") == banner


def test_nada_ate_100_retorna_3_de_C_banner_192():
    df = _df_base()
    df = df[~df["cnes_id"].isin(["A1", "B1"])].copy()
    df.loc[:, ["lat", "lon"]] = (-10.0, -48.0)
    res, banner, *rest = geo_v2_search_core(df, U_LAT, U_LON, None, 25, True, 3)
    assert len(res) == 3
    assert banner is True  # Usou C para completar (fallback)
    if rest:
        meta = rest[0]
        assert meta.get("completed_with_group_C") == banner


def test_rotas_url_formato():
    df = _df_base()
    res, *_ = geo_v2_search_core(df, U_LAT, U_LON, None, 25, True, 3)
    assert "rotas_url" in res[0]
    assert "origin=" in res[0]["rotas_url"] and "destination=" in res[0]["rotas_url"]


def test_esfera_sus_payload_municipal():
    """Municipal por nome com esfera/atende_sus vazios → esfera 'Público' e sus_badge 'Aceita Cartão SUS'."""
    nome = "HOSPITAL MUNICIPAL SANTA MARIA"
    esfera_raw = None
    atende_sus_label = None
    esfera_final = _esfera_override(nome, esfera_raw)
    sus_badge = _sus_badge(atende_sus_label, esfera_final)
    assert esfera_final == "Público"
    assert sus_badge == "Aceita Cartão SUS"


def test_esfera_sus_hospital_mun_abbrev():
    """Nome 'HOSPITAL MUN. …' → esfera 'Público' e sus_badge 'Aceita Cartão SUS' (QA gate)."""
    nome = "HOSPITAL MUN. DR. JOÃO SILVEIRA"
    esfera_final = _esfera_override(nome, None)
    sus_badge = _sus_badge("", esfera_final)
    assert esfera_final == "Público"
    assert sus_badge == "Aceita Cartão SUS"
