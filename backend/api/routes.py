#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rotas da API de Busca de Facilidades
Purpose: Endpoints FastAPI para busca de hospitais/UPAs/UBS
"""

import logging
import math
import os
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

try:
    from .models import SearchRequest, SearchResponse, SearchMeta, FacilityResult
    from ..services.facility_service import FacilityService
    from ..services.geo_service import haversine_distance
    from ..utils.phone import format_br_phone
    from ..utils.env import get_env
    from ..utils.travel_time import get_travel_times
except ImportError:
    from backend.api.models import SearchRequest, SearchResponse, SearchMeta, FacilityResult
    from backend.services.facility_service import FacilityService
    from backend.services.geo_service import haversine_distance
    from backend.utils.phone import format_br_phone
    from backend.utils.env import get_env
    from backend.utils.travel_time import get_travel_times

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
GEO_PARQUET_PATH = BASE_DIR / "data" / "geo" / "hospitals_geo.parquet"
GEO_PARQUET_MIN = BASE_DIR / "data" / "geo" / "hospitals_geo.min.parquet"
GEO_PARQUET = GEO_PARQUET_PATH  # compat; preferir min via load_geo_df

_geo_df_cache: Optional[pd.DataFrame] = None
_geo_df_mtime: Optional[float] = None
_geo_df_loaded_at: Optional[float] = None


def _geo_parquet_path() -> Path:
    """Prefere min.parquet se existir; senão o parquet completo."""
    return GEO_PARQUET_MIN if GEO_PARQUET_MIN.exists() else GEO_PARQUET_PATH


def load_geo_df() -> Optional[pd.DataFrame]:
    """Carrega geo parquet (preferindo .min) com cache por processo; recarrega se mtime mudar ou TTL expirado."""
    global _geo_df_cache, _geo_df_mtime, _geo_df_loaded_at
    p = _geo_parquet_path()
    if not p.exists():
        return None
    ttl_sec = 0
    try:
        ttl_sec = int(os.environ.get("EMERGENCY_CACHE_TTL_SECONDS", "0") or "0")
    except (TypeError, ValueError):
        pass
    if ttl_sec > 0 and _geo_df_loaded_at is not None and (time.time() - _geo_df_loaded_at) > ttl_sec:
        _geo_df_cache = None
        _geo_df_mtime = None
        _geo_df_loaded_at = None
    mtime = p.stat().st_mtime
    if _geo_df_cache is None or _geo_df_mtime != mtime:
        df = pd.read_parquet(p)
        _geo_df_cache = df
        _geo_df_mtime = mtime
        _geo_df_loaded_at = time.time()
        logger.info("[geo] cache carregado: %d linhas (src=%s)", len(df), p.name)
    return _geo_df_cache


def get_geo_data_info() -> Dict:
    """
    Retorna metadados da base geográfica (hospitais) em dict:
    - count: itens carregados
    - source_path: caminho do arquivo parquet/csv
    - mtime: timestamp da última modificação do arquivo
    - loaded_at: timestamp de quando foi carregado em memória
    - ttl_seconds / ttl_remaining
    
    Detecção heurística: não depende de nomes rígidos e não altera o comportamento do módulo.
    """
    import os
    import time
    
    def _get(*names, default=None):
        g = globals()
        for n in names:
            if n in g:
                return g[n]
        return default
    
    def _maybe_path():
        # função que devolve o caminho, se existir
        fn = _get("_geo_parquet_path", "get_geo_parquet_path", default=None)
        try:
            return fn() if callable(fn) else None
        except Exception:
            return None
    
    def _count(df):
        try:
            # pandas DataFrame
            try:
                import pandas as pd  # noqa
                import pandas
                if isinstance(df, pandas.core.generic.NDFrame):
                    return int(getattr(df, "shape", [0])[0])
            except Exception:
                pass
            if hasattr(df, "__len__"):
                return int(len(df))
        except Exception:
            return None
        return None
    
    # origem/df
    df = _get("_geo_df_cache", "_geo_df", "GEO_DF", default=None)
    count = _count(df)
    
    # caminho
    source_path = _maybe_path() or _get("_geo_df_path", "GEO_SOURCE_PATH", "EMERGENCY_SOURCE_PATH", default=None)
    if source_path and hasattr(source_path, "__str__"):
        source_path = str(source_path)
    
    # mtime do arquivo
    mtime = None
    if isinstance(source_path, str):
        try:
            mtime = int(os.path.getmtime(source_path))
        except Exception:
            mtime = None
    
    # se não achou mtime do arquivo, tenta variável global
    if mtime is None:
        mtime_val = _get("_geo_df_mtime", "GEO_DF_MTIME", default=None)
        if mtime_val is not None:
            try:
                mtime = int(mtime_val)
            except Exception:
                mtime = None
    
    # quando carregou
    loaded_at = _get("_geo_df_loaded_at", "GEO_DF_LOADED_AT", default=None)
    try:
        if loaded_at is not None:
            loaded_at = int(loaded_at)
    except Exception:
        loaded_at = None
    
    # TTL e restante
    ttl_seconds = _get("EMERGENCY_CACHE_TTL_SECONDS", "CACHE_TTL_SECONDS", default=None)
    if ttl_seconds is None:
        try:
            ttl_seconds = int(os.environ.get("EMERGENCY_CACHE_TTL_SECONDS", "0"))
        except Exception:
            ttl_seconds = None
    else:
        try:
            ttl_seconds = int(ttl_seconds)
        except Exception:
            ttl_seconds = None
    
    ttl_remaining = None
    try:
        if loaded_at and ttl_seconds:
            ttl_remaining = max(0, loaded_at + ttl_seconds - int(time.time()))
    except Exception:
        ttl_remaining = None
    
    out = {
        "count": count,
        "source_path": source_path,
        "mtime": mtime,
        "loaded_at": loaded_at,
        "ttl_seconds": ttl_seconds,
        "ttl_remaining": ttl_remaining,
    }
    
    # remove None para payload limpo
    return {k: v for k, v in out.items() if v is not None}


def refresh_geo_cache() -> tuple[bool, Optional[int], Optional[str]]:
    """Limpa cache geo e força re-load. Retorna (ok, rows, error)."""
    global _geo_df_cache, _geo_df_mtime, _geo_df_loaded_at
    _geo_df_cache = None
    _geo_df_mtime = None
    _geo_df_loaded_at = None
    try:
        df = load_geo_df()
        rows = len(df) if df is not None else 0
        return (True, rows, None)
    except Exception as e:
        return (False, None, str(e))


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    to_rad = math.radians
    dlat = to_rad(lat2 - lat1)
    dlon = to_rad(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(to_rad(lat1)) * math.cos(to_rad(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def _label(row: Dict) -> str:
    if bool(row.get("has_maternity")):
        return "Ala de Maternidade"
    if bool(row.get("is_probable")):
        return "Provável maternidade (ligue para confirmar)"
    return "Não listado"


def _normalize_esfera(esfera_raw: str | None, nome: str | None) -> str | None:
    """Normaliza esfera para um dos 3 valores válidos (Público/Privado/Filantrópico) ou None. NUNCA retorna 'Desconhecido'."""
    e = (esfera_raw or "").strip()
    # Rejeita explicitamente "Desconhecido" (case-insensitive)
    if e.lower() == "desconhecido":
        e = ""
    # Se já é um dos valores válidos, retorna direto
    if e in ("Público", "Privado", "Filantrópico"):
        return e
    # Tenta derivar por nome
    e2 = _esfera_override(nome, None)
    if e2 in ("Público", "Privado", "Filantrópico"):
        return e2
    # Se não conseguir determinar, retorna None (frontend não renderiza) ou 'Privado' como fallback
    # Escolhendo None para não mostrar badge quando não souber
    return None


def _esfera_override(nome: str | None, esfera: str | None) -> str:
    """Público/Privado/Filantrópico por nome (override para parquet antigo). Abreviações: mun., h mun, sec. saúde."""
    n = (nome or "").lower()
    if re.search(r"\b(municip(al)?|h\s+mun|estad|federal|prefeit|sec\.\s*sa[uú]de|secretaria)\b|\bmun\.?(?=\s|$)", n):
        return "Público"
    if re.search(r"santa casa|filantr|beneficen|miseric[oó]rdia|irmandade|fund(a|ação|acao)", n):
        return "Filantrópico"
    return (esfera or "").strip() or "Privado"


def _sus_badge(atende_sus_label: str | None, esfera: str | None) -> str:
    """Badge SUS canônico: sempre 'Aceita Cartão SUS' ou 'Não atende SUS' (nunca 'Aceita SUS')."""
    lab = (atende_sus_label or "").strip()
    if lab == "Sim":
        return "Aceita Cartão SUS"
    if (lab == "" or lab == "Desconhecido") and esfera == "Público":
        return "Aceita Cartão SUS"
    if lab == "Não":
        return "Não atende SUS"
    return ""


def _apply_cnes_overrides(cnes_id: str | None, esfera_final: str, sus_badge_val: str, nome: str | None = None) -> tuple[str, str, list, bool]:
    """Aplica overrides do CNES (esfera, sus_badge, convenios). Retorna (esfera, sus_badge, convenios, override_hit). NUNCA retorna 'Desconhecido'."""
    try:
        from backend.startup.cnes_overrides import get_overrides
    except Exception:
        get_overrides = lambda *_: None
    
    ovr = get_overrides(cnes_id) if cnes_id else None
    if ovr:
        esfera_ovr = ovr.get("esfera")
        # Normaliza esfera do override para garantir que nunca seja "Desconhecido"
        esfera_normalizada = _normalize_esfera(esfera_ovr or esfera_final, nome)
        esfera_final = esfera_normalizada or "Privado"  # Fallback seguro: nunca "Desconhecido"
        sus_badge_val = ovr.get("sus_badge") or sus_badge_val
        convenios = ovr.get("convenios") or []
        return esfera_final, sus_badge_val, convenios, True
    convenios = []
    # Garantir que esfera_final nunca seja "Desconhecido" mesmo sem override
    esfera_normalizada = _normalize_esfera(esfera_final, nome)
    esfera_final = esfera_normalizada or "Privado"  # Fallback seguro: nunca "Desconhecido"
    return esfera_final, sus_badge_val, convenios, False


def _routes_url(ulat: float, ulon: float, hlat: float, hlon: float) -> str:
    return f"https://www.google.com/maps/dir/?api=1&origin={ulat},{ulon}&destination={hlat},{hlon}"


# Hotfix: filtro estrito obstétrico (runtime) - bloqueia psicologia, fono, fisio, etc.
STRICT_OBST = (str(get_env("STRICT_OBST", "on")).lower() in ("1", "on", "true", "sim"))

# Nomes que nunca devem entrar como maternidade
EXCLUDE_NAME_RE = re.compile(
    r"(psicolog|psico\b|psiquiatr|fono|fonoaudiol|fisioter|terapia\socup|nutri(ç|c)ão|consult[óo]rio|ambulat[óo]ri|cl[ií]nica\s+(?!obst|matern)|optica|oficina\sortop)",
    re.I
)

# Só consideramos "provável" com cara de OBSTETRÍCIA
INCLUDE_MATERN_RE = re.compile(
    r"(\bmaternidade\b|hospital\s+e\s+maternidade|casa\s+de\s+parto|centro\s+de\s+parto|cpn\b|parto\s+e\s+nascimento)",
    re.I
)


def _is_obstetric_relevant_name(name: str) -> bool:
    """Verifica se o nome indica obstetrícia (não ambulatorial)."""
    if not name:
        return False
    n = str(name).strip()
    if EXCLUDE_NAME_RE.search(n):
        return False
    return bool(INCLUDE_MATERN_RE.search(n))


def _filter_obstetric(df: pd.DataFrame) -> pd.DataFrame:
    """
    Mantém: has_maternity=True sempre; e is_probable só se o nome indicar obstetrícia.
    Remove: psicologia, fono, fisio, nutrição, consultório, ambulatorial, etc.
    """
    if df is None or len(df) == 0:
        return df
    df = df.copy()
    # Nomes: display_name > nome
    names = df.get("display_name", pd.Series("", index=df.index)).fillna("") + " " + df.get("nome", pd.Series("", index=df.index)).fillna("")
    mask = (df.get("has_maternity") == True) | (
        (df.get("is_probable") == True) & names.apply(_is_obstetric_relevant_name)
    )
    return df[mask]


def _apply_distance(df: pd.DataFrame, lat: float, lon: float) -> pd.DataFrame:
    df = df.copy()
    df["distancia_km"] = df.apply(lambda r: haversine_km(lat, lon, float(r["lat"]), float(r["lon"])), axis=1)
    return df


def _filter_radius(df: pd.DataFrame, radius_km: float) -> pd.DataFrame:
    return df[df["distancia_km"] <= radius_km]


def _rank(df: pd.DataFrame, lat: float, lon: float, use_travel: bool) -> pd.DataFrame:
    if use_travel and len(df) > 0:
        destinos = [(float(r["lat"]), float(r["lon"])) for _, r in df.iterrows()]
        times = get_travel_times((lat, lon), destinos)
        if times and len(times) == len(destinos):
            df = df.copy()
            df["tempo_estimado_seg"] = times
            return df.sort_values(["tempo_estimado_seg", "distancia_km"], ascending=[True, True])
    return df.sort_values("distancia_km")


def geo_v2_search_core(
    df_all: pd.DataFrame,
    lat: float,
    lon: float,
    sus: Optional[bool],
    radius_km: float,
    expand: bool,
    limit: int,
    min_results: int = 3,
) -> Tuple[List[Dict], bool, Dict[str, Any]]:
    df = df_all[(df_all["lat"].notna()) & (df_all["lon"].notna())].copy()
    if sus is True:
        df = df[df["atende_sus"] == "Sim"].copy()
    elif sus is False:
        df = df[df["atende_sus"] == "Não"].copy()

    A = df[df["has_maternity"] == True].copy()
    B = df[(df["has_maternity"] != True) & (df["is_probable"] == True)].copy()
    C = df[(df["has_maternity"] != True) & (df["is_probable"] != True)].copy()

    # Hotfix: filtro estrito obstétrico (runtime) - remove psicologia, fono, etc.
    if STRICT_OBST:
        A = _filter_obstetric(A)  # Não muda (já são confirmados, mas garante nome válido)
        B = _filter_obstetric(B)  # Remove "psicologia", "materno infantil" etc.

    for d in (A, B, C):
        if len(d) > 0:
            d.loc[:, "lat"] = pd.to_numeric(d["lat"], errors="coerce")
            d.loc[:, "lon"] = pd.to_numeric(d["lon"], errors="coerce")

    use_travel = (str(get_env("TRAVEL_TIME", "off")).lower() == "on")
    radii = [radius_km, 50.0, 100.0] if expand else [radius_km]

    results_rows = pd.DataFrame()
    banner_192 = False
    radius_used: Optional[float] = None
    foundA = 0
    foundB = 0

    for r in radii:
        a = _apply_distance(A, lat, lon) if len(A) > 0 else A
        b = _apply_distance(B, lat, lon) if len(B) > 0 else B
        a = _filter_radius(a, r) if len(a) > 0 else a
        b = _filter_radius(b, r) if len(b) > 0 else b
        foundA = int(len(a))
        foundB = int(len(b))
        if foundA + foundB > 0:
            pool = pd.concat([x for x in (a, b) if len(x) > 0], ignore_index=True)
            pool = _rank(pool, lat, lon, use_travel)
            results_rows = pool.head(max(limit, min_results))
            radius_used = r
            if len(results_rows) >= min_results:
                break

    # Regra de produto: banner_192 só fica True quando o resultado foi completado com grupo C (fallback).
    # Se encontrou A ou B (mesmo que seja menos que min_results), não complementa com C.
    if results_rows.empty and len(C) > 0:
        Cdist = _apply_distance(C, lat, lon)
        Cdist = _rank(Cdist, lat, lon, use_travel)
        results_rows = Cdist.head(max(limit, min_results))
        banner_192 = True
        if radius_used is None:
            radius_used = radii[-1] if radii else radius_km

    results = []
    for _, row in results_rows.iterrows():
        nome_raw = row.get("nome") or ""
        nome = (row.get("display_name") or nome_raw or "").strip() or nome_raw
        cnes_id = row.get("cnes_id")
        esfera_raw = row.get("esfera")
        atende_label = row.get("atende_sus_label") or row.get("atende_sus")
        esfera_final = _normalize_esfera(esfera_raw, nome) or "Privado"  # Fallback para Privado se None
        sus_badge_val = _sus_badge(atende_label, esfera_final)
        esfera_final, sus_badge_val, convenios, override_hit = _apply_cnes_overrides(cnes_id, esfera_final, sus_badge_val, nome)
        # Garantir que esfera_final nunca seja "Desconhecido" após overrides
        esfera_final = _normalize_esfera(esfera_final, nome) or "Privado"
        # Extrai componentes do endereço do parquet
        # O parquet tem: municipio, uf, endereco (formato: "logradouro, numero – bairro, municipio/uf • CEP")
        municipio_raw = row.get("municipio")
        uf_raw = row.get("uf")
        
        # Extrai componentes do endereço completo
        # Formato do parquet: "RUA SAIGIRO NAKAMURA, 800 – VILA INDUSTRIAL, / • CEP 12220280"
        # OU: "RUA EXEMPLO, s/n – BAIRRO, CIDADE/UF • CEP 12345-678"
        endereco_completo = str(row.get("endereco") or "").strip()
        logradouro = None
        numero = None
        bairro = None
        
        # Processa municipio e uf do parquet (pode ser pandas Series, numpy, string, etc)
        # Usa pd.isna() para verificar valores NaN do pandas corretamente
        municipio_val = None
        uf_val = None
        
        if municipio_raw is not None and not pd.isna(municipio_raw):
            municipio_str = str(municipio_raw).strip()
            if municipio_str and municipio_str.lower() not in ["nan", "none", "", "null"]:
                municipio_val = municipio_str
        
        if uf_raw is not None and not pd.isna(uf_raw):
            uf_str = str(uf_raw).strip()
            if uf_str and uf_str.lower() not in ["nan", "none", "", "null"]:
                uf_val = uf_str
        
        if endereco_completo and endereco_completo != "nan":
            try:
                # Formato: "LOGRADOURO, NUMERO – BAIRRO, CIDADE/UF • CEP"
                if " – " in endereco_completo:
                    parts = endereco_completo.split(" – ", 1)
                    
                    # Primeira parte: logradouro e número
                    if len(parts) >= 1:
                        log_num = parts[0].strip()
                        if "," in log_num:
                            log_parts = log_num.split(",", 1)
                            logradouro = log_parts[0].strip() if log_parts[0].strip() else None
                            numero_str = log_parts[1].strip() if len(log_parts) > 1 else ""
                            # Valida número (pode ser "s/n", "sn", número ou vazio)
                            if numero_str and numero_str.lower() not in ["s/n", "sn", "sem número", "nan", ""]:
                                numero = numero_str
                        else:
                            # Se não tem vírgula, é só logradouro
                            logradouro = log_num.strip() if log_num.strip() else None
                    
                    # Segunda parte: bairro, cidade/uf (ou apenas bairro se cidade/uf vazio)
                    if len(parts) >= 2:
                        resto = parts[1].strip()
                        # Remove CEP se presente: " • CEP 12345678" ou " • CEP 12345-678"
                        resto = re.sub(r'\s*•\s*CEP\s+\d{5}-?\d{3}?', '', resto).strip()
                        # Remove vírgulas finais e barras
                        resto = resto.rstrip(', /')
                        
                        # Separa bairro e cidade/uf
                        if "," in resto:
                            resto_parts = resto.split(",", 1)
                            bairro_str = resto_parts[0].strip() if resto_parts[0].strip() else ""
                            # Valida bairro (não pode ser vazio, "/", "nan")
                            if bairro_str and bairro_str.lower() not in ["nan", "none", "", "/"]:
                                bairro = bairro_str
                        else:
                            # Se não tem vírgula, pode ser só bairro ou cidade/uf
                            if resto and resto.lower() not in ["nan", "none", "", "/"]:
                                # Se não tem "/", provavelmente é bairro
                                if "/" not in resto:
                                    bairro = resto.strip()
                
                # Formato alternativo sem " – ": "logradouro, numero, bairro, cidade/uf"
                elif "," in endereco_completo:
                    parts = [p.strip() for p in endereco_completo.split(",")]
                    if len(parts) >= 1 and parts[0] and parts[0].lower() not in ["nan", "none", ""]:
                        logradouro = parts[0]
                    if len(parts) >= 2 and parts[1] and parts[1].lower() not in ["s/n", "sn", "sem número", "nan", "none", ""]:
                        numero = parts[1]
                    if len(parts) >= 3 and parts[2] and parts[2].lower() not in ["nan", "none", "", "/"]:
                        bairro = parts[2]
                        
            except Exception as e:
                logger.warning(f"[ROUTES] Erro ao extrair endereço '{endereco_completo}': {e}")
                # Em caso de erro, mantém None (usa endereco completo)
        
        # Debug: log primeiro hospital para verificar extração
        if len(results) == 0:
            logger.info(f"[ROUTES] 🔍 Extração endereço - endereco_completo: '{endereco_completo}'")
            logger.info(f"[ROUTES] 🔍 logradouro: '{logradouro}', numero: '{numero}', bairro: '{bairro}'")
            logger.info(f"[ROUTES] 🔍 municipio_val: '{municipio_val}', uf_val: '{uf_val}'")
            logger.info(f"[ROUTES] 🔍 municipio_raw type: {type(municipio_raw)}, value: '{municipio_raw}'")
            logger.info(f"[ROUTES] 🔍 uf_raw type: {type(uf_raw)}, value: '{uf_raw}'")
        
        # Garante que valores None sejam None (não string "None")
        logradouro_final = str(logradouro).strip() if logradouro else None
        numero_final = str(numero).strip() if numero else None
        bairro_final = str(bairro).strip() if bairro else None
        cidade_final = str(municipio_val).strip() if municipio_val else None
        estado_final = str(uf_val).strip() if uf_val else None
        
        item = {
            "cnes_id": str(cnes_id),
            "nome": nome,
            "esfera": esfera_final,
            "sus_badge": sus_badge_val,
            "atende_sus": str(atende_label).strip() if atende_label and str(atende_label).strip() not in ("", "nan") else None,
            "has_maternity": bool(row.get("has_maternity")),
            "label_maternidade": _label(row.to_dict()),
            "telefone": row.get("telefone"),
            "telefone_formatado": row.get("telefone_formatado"),
            "phone_e164": row.get("phone_e164"),
            "endereco": row.get("endereco"),
            # Componentes do endereço separados para melhor formatação no frontend
            "logradouro": logradouro_final,
            "numero": numero_final,
            "bairro": bairro_final,
            "cidade": cidade_final,
            "estado": estado_final,
            "lat": float(row.get("lat")) if pd.notna(row.get("lat")) else None,
            "lon": float(row.get("lon")) if pd.notna(row.get("lon")) else None,
            "distancia_km": float(row.get("distancia_km")) if pd.notna(row.get("distancia_km")) else None,
            "tempo_estimado_seg": int(row.get("tempo_estimado_seg")) if pd.notna(row.get("tempo_estimado_seg")) else None,
            "convenios": convenios,
            "has_convenios": len(convenios) > 0,
            "override_hit": override_hit,
        }
        # 0072: garantir telefone_formatado (fallback de format_br_phone se parquet não tiver)
        if not item.get("telefone_formatado") and item.get("telefone"):
            disp, e164 = format_br_phone(item["telefone"])
            if disp:
                item["telefone_formatado"] = disp
            if e164:
                item["phone_e164"] = e164
        if item["lat"] is not None and item["lon"] is not None:
            item["rotas_url"] = _routes_url(lat, lon, item["lat"], item["lon"])
        else:
            item["rotas_url"] = None
        results.append(item)

    meta = {
        "radius_requested": float(radius_km),
        "radius_used": float(radius_used) if radius_used is not None else None,
        "expanded": bool(radius_used is not None and radius_used > radius_km),
        "found_A": foundA,
        "found_B": foundB,
        "used_travel_time": use_travel,
        "completed_with_group_C": banner_192,
    }

    nearby_confirmed: List[Dict[str, Any]] = []
    try:
        if not any(x.get("has_maternity") for x in results):
            Aall = df_all[df_all.get("has_maternity") == True].copy()
            if len(Aall) > 0:
                Aall = Aall[(Aall["lat"].notna()) & (Aall["lon"].notna())].copy()
                Aall = _apply_distance(Aall, lat, lon)
                Aall = Aall.sort_values("distancia_km")
                sug = Aall[Aall["distancia_km"] <= 100.0].head(3)
                for _, row in sug.iterrows():
                    nome_raw = row.get("nome") or ""
                    nome = (row.get("display_name") or nome_raw or "").strip() or nome_raw
                    cnes_id = row.get("cnes_id")
                    esfera_raw = row.get("esfera")
                    atende_label = row.get("atende_sus_label") or row.get("atende_sus")
                    esfera_final = _normalize_esfera(esfera_raw, nome) or "Privado"  # Fallback para Privado se None
                    sus_badge_val = _sus_badge(atende_label, esfera_final)
                    esfera_final, sus_badge_val, convenios, override_hit = _apply_cnes_overrides(cnes_id, esfera_final, sus_badge_val, nome)
                    # Garantir que esfera_final nunca seja "Desconhecido" após overrides
                    esfera_final = _normalize_esfera(esfera_final, nome) or "Privado"
                    # Extrai componentes do endereço do parquet para nearby_confirmed também (mesma lógica)
                    municipio_nearby = row.get("municipio")
                    uf_nearby = row.get("uf")
                    
                    # Usa municipio e uf do parquet diretamente
                    municipio_nearby_val = municipio_nearby if municipio_nearby and str(municipio_nearby).strip() and str(municipio_nearby).lower() not in ["nan", "none", ""] else None
                    uf_nearby_val = uf_nearby if uf_nearby and str(uf_nearby).strip() and str(uf_nearby).lower() not in ["nan", "none", ""] else None
                    
                    endereco_completo_nearby = str(row.get("endereco") or "").strip()
                    logradouro_nearby = None
                    numero_nearby = None
                    bairro_nearby = None
                    
                    if endereco_completo_nearby and endereco_completo_nearby != "nan":
                        try:
                            # Formato: "LOGRADOURO, NUMERO – BAIRRO, CIDADE/UF • CEP"
                            if " – " in endereco_completo_nearby:
                                parts = endereco_completo_nearby.split(" – ", 1)
                                
                                # Primeira parte: logradouro e número
                                if len(parts) >= 1:
                                    log_num = parts[0].strip()
                                    if "," in log_num:
                                        log_parts = log_num.split(",", 1)
                                        logradouro_nearby = log_parts[0].strip() if log_parts[0].strip() else None
                                        numero_str = log_parts[1].strip() if len(log_parts) > 1 else ""
                                        if numero_str and numero_str.lower() not in ["s/n", "sn", "sem número", "nan", ""]:
                                            numero_nearby = numero_str
                                    else:
                                        logradouro_nearby = log_num.strip() if log_num.strip() else None
                                
                                # Segunda parte: bairro, cidade/uf (ou apenas bairro se cidade/uf vazio)
                                if len(parts) >= 2:
                                    resto = parts[1].strip()
                                    resto = re.sub(r'\s*•\s*CEP\s+\d{5}-?\d{3}?', '', resto).strip()
                                    resto = resto.rstrip(', /')
                                    
                                    if "," in resto:
                                        resto_parts = resto.split(",", 1)
                                        bairro_str = resto_parts[0].strip() if resto_parts[0].strip() else ""
                                        if bairro_str and bairro_str.lower() not in ["nan", "none", "", "/"]:
                                            bairro_nearby = bairro_str
                                    else:
                                        if resto and resto.lower() not in ["nan", "none", "", "/"]:
                                            if "/" not in resto:
                                                bairro_nearby = resto.strip()
                            
                            # Formato alternativo sem " – "
                            elif "," in endereco_completo_nearby:
                                parts = [p.strip() for p in endereco_completo_nearby.split(",")]
                                if len(parts) >= 1 and parts[0] and parts[0].lower() not in ["nan", "none", ""]:
                                    logradouro_nearby = parts[0]
                                if len(parts) >= 2 and parts[1] and parts[1].lower() not in ["s/n", "sn", "sem número", "nan", "none", ""]:
                                    numero_nearby = parts[1]
                                if len(parts) >= 3 and parts[2] and parts[2].lower() not in ["nan", "none", "", "/"]:
                                    bairro_nearby = parts[2]
                        except Exception as e:
                            logger.warning(f"[ROUTES] Erro ao extrair endereço nearby '{endereco_completo_nearby}': {e}")
                    
                    nearby_confirmed.append({
                        "cnes_id": str(cnes_id),
                        "nome": nome,
                        "distancia_km": float(row.get("distancia_km")),
                        "lat": float(row.get("lat")),
                        "lon": float(row.get("lon")),
                        "rotas_url": _routes_url(lat, lon, float(row.get("lat")), float(row.get("lon"))),
                        "esfera": esfera_final,
                        "sus_badge": sus_badge_val,
                        "atende_sus": str(atende_label).strip() if atende_label and str(atende_label).strip() not in ("", "nan") else None,
                        "label_maternidade": "Ala de Maternidade",
                        "convenios": convenios,
                        "has_convenios": len(convenios) > 0,
                        "override_hit": override_hit,
                        # Componentes do endereço separados
                        "endereco": row.get("endereco"),
                        "logradouro": str(logradouro_nearby).strip() if logradouro_nearby else None,
                        "numero": str(numero_nearby).strip() if numero_nearby else None,
                        "bairro": str(bairro_nearby).strip() if bairro_nearby else None,
                        "cidade": str(municipio_nearby_val).strip() if municipio_nearby_val else None,
                        "estado": str(uf_nearby_val).strip() if uf_nearby_val else None,
                        "telefone": row.get("telefone"),
                        "telefone_formatado": row.get("telefone_formatado"),
                    })
                    # 0072: fallback telefone_formatado para nearby_confirmed
                    if not nearby_confirmed[-1].get("telefone_formatado") and nearby_confirmed[-1].get("telefone"):
                        disp, _ = format_br_phone(nearby_confirmed[-1]["telefone"])
                        if disp:
                            nearby_confirmed[-1]["telefone_formatado"] = disp
    except Exception:
        pass

    return results, banner_192, meta, nearby_confirmed


def geo_v2_search_driver(
    lat: float, lon: float, sus: Optional[bool], radius_km: float, expand: bool, limit: int, min_results: int = 3
) -> Tuple[Optional[pd.DataFrame], Optional[List[Dict]], bool, Optional[Dict[str, Any]], List[Dict]]:
    df = load_geo_df()
    if df is None:
        return None, None, False, None, []
    res, banner, meta, nearby = geo_v2_search_core(df, lat, lon, sus, radius_km, expand, limit, min_results)
    return df, res, banner, meta, nearby

router = APIRouter(prefix="/api/v1", tags=["facilities"])

# Instância do serviço (pode ser injetada via dependency injection)
facility_service = FacilityService()

# Aviso legal obrigatório (UX Expert + PM)
LEGAL_DISCLAIMER_EMERGENCY = (
    "🚨 EMERGÊNCIA: Em caso de risco imediato à vida (sangramento intenso, perda de consciência, convulsão), "
    "ligue 192 (SAMU) ou dirija-se ao Hospital mais próximo. A Lei Federal obriga o atendimento de "
    "emergência para estabilização, independente de convênio. Não aguarde validação do aplicativo."
)

LEGAL_DISCLAIMER_GENERAL = (
    "⚠️ Aviso: Em caso de emergência médica, dirija-se ao Pronto Socorro mais próximo. "
    "A Lei Federal obriga o atendimento de emergência para estabilização, independente de convênio."
)


@router.post("/facilities/search", response_model=SearchResponse)
async def search_facilities(request: SearchRequest):
    """
    Busca facilidades de saúde puerperal
    
    **Regras de Negócio:**
    - Se `is_emergency=true`: Ignora filtros de convênio, retorna unidades mais próximas
    - Se `filter_type=MATERNITY`: Apenas hospitais com maternidade
    - Se `filter_type=SUS`: Apenas unidades que atendem SUS
    - Se `filter_type=PRIVATE`: Apenas unidades privadas
    - Se `filter_type=EMERGENCY_ONLY`: Apenas UPAs
    
    **Aviso Legal:** 
    Sempre incluído na resposta (Lei 11.634/2008)
    """
    try:
        # Buscar facilidades (state/city: filtro Brasil todo — 5570 municípios, 27 estados + DF)
        results, data_source_date, is_cache_fallback = facility_service.search_facilities(
            latitude=request.latitude,
            longitude=request.longitude,
            radius_km=request.radius_km,
            filter_type=request.filter_type,
            is_emergency=request.is_emergency,
            search_mode=request.search_mode,
            state=request.state,
            city=request.city
        )
        
        # Escolher disclaimer baseado no modo de busca
        if request.search_mode == "emergency":
            base_disclaimer = LEGAL_DISCLAIMER_EMERGENCY
        else:
            base_disclaimer = LEGAL_DISCLAIMER_GENERAL
        
        # Formatar aviso de cache (se aplicável)
        if is_cache_fallback and data_source_date:
            additional_warning = (
                f"\n\n⚠️ Dados baseados no registro oficial de {data_source_date}. "
                "API CNES está offline. Confirme informações por telefone."
            )
            legal_disclaimer = base_disclaimer + additional_warning
        else:
            legal_disclaimer = base_disclaimer
        
        # Construir resposta
        response = SearchResponse(
            meta=SearchMeta(
                legal_disclaimer=legal_disclaimer,
                total_results=len(results),
                data_source_date=data_source_date,
                is_cache_fallback=is_cache_fallback
            ),
            results=[FacilityResult(**result) for result in results]
        )
        
        return response
        
    except FileNotFoundError as e:
        logger.error(f"❌ Banco de dados não encontrado: {e}")
        raise HTTPException(
            status_code=503,
            detail=(
                "Serviço temporariamente indisponível. "
                "Banco de dados CNES não foi inicializado. "
                "Contate o administrador do sistema."
            )
        )
    except Exception as e:
        logger.error(f"❌ Erro ao buscar facilidades: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=(
                "Erro interno do servidor ao processar busca. "
                "Por favor, tente novamente. Se o problema persistir, contate o suporte."
            )
        )


def _enrich_travel_time_and_sort(results: List[Dict], origin_lat: float, origin_lon: float) -> List[Dict]:
    """Se TRAVEL_TIME=on e token válido, preenche tempo_estimado_seg e ordena por ele; senão mantém ordem por distancia_km."""
    if not results:
        return results
    try:
        from backend.utils.travel_time import get_travel_times
        destinos = [(r.get("lat"), r.get("lon")) for r in results if r.get("lat") is not None and r.get("lon") is not None]
        times = get_travel_times((origin_lat, origin_lon), destinos) if destinos else None
        if times and len(times) == len(results):
            for i, r in enumerate(results):
                if i < len(times) and times[i] is not None:
                    r["tempo_estimado_seg"] = times[i]
            results.sort(key=lambda x: (x.get("tempo_estimado_seg") or float("inf"), x.get("distancia_km") or float("inf")))
    except Exception:
        pass
    return results


def _emergency_search_geo_v2(
    lat: float, lon: float, radius_km: float, expand: bool, limit: int, sus_only: bool
) -> tuple:
    """
    Busca em 3 camadas a partir de hospitals_geo.parquet.
    Grupo A: has_maternity==True; B: is_probable==True; C: demais.
    Parâmetros: lat, lon, radius_km=25, expand=true, limit=3.
    Busca A no raio; se vazio e expand, inclui B; se vazio, raio 50 e 100; se ainda vazio, top 3 de C e banner_192=true.
    Ranking: Confirmados > Prováveis > Outros; dentro do grupo por travel_time (se TRAVEL_TIME=on) senão Haversine.
    rotas_url: https://www.google.com/maps/dir/?api=1&origin={lat_user},{lon_user}&destination={lat_hosp},{lon_hosp}
    """
    import pandas as pd
    df = load_geo_df()
    if df is None:
        return None, None, False
    df = df[df["lat"].notna() & df["lon"].notna()]
    if sus_only:
        df = df[df["atende_sus"] == "Sim"]
    group_a = df[df["has_maternity"] == True].to_dict("records")
    group_b = df[(df["is_probable"] == True) & (df["has_maternity"] == False)].to_dict("records")
    group_c = df[(df["has_maternity"] == False) & (df["is_probable"] == False)].to_dict("records")

    def in_radius(rows: List[Dict], r_km: float) -> List[Dict]:
        out = []
        for row in rows:
            la, lo = row.get("lat"), row.get("lon")
            if la is None or lo is None or (isinstance(la, float) and math.isnan(la)):
                continue
            d = haversine_distance(lat, lon, float(la), float(lo))
            if d <= r_km:
                r = dict(row)
                r["distancia_km"] = round(d, 2)
                out.append(r)
        out.sort(key=lambda x: x["distancia_km"])
        return out

    def format_item(row: Dict, banner_192: bool = False) -> Dict:
        nome_raw = row.get("nome") or row.get("name") or ""
        nome = (row.get("display_name") or nome_raw or "").strip() or nome_raw
        nome_lower = (nome or "").lower()
        telefone = row.get("telefone")
        disp, e164 = format_br_phone(telefone)
        has_mat = row.get("has_maternity") in (True, 1)
        prob = row.get("is_probable") in (True, 1)
        if has_mat:
            label_maternidade = "Ala de Maternidade"
        elif prob and not any(k in nome_lower for k in ("psicologia", "psicólogo", "clínica psicol")):
            label_maternidade = "Provável maternidade (ligue para confirmar)"
        else:
            label_maternidade = "Hospital"
        esfera_raw = row.get("esfera")
        atende_label = row.get("atende_sus_label") or row.get("atende_sus")
        esfera_final = _normalize_esfera(esfera_raw, nome) or "Privado"  # Fallback para Privado se None
        sus_badge_val = _sus_badge(atende_label, esfera_final)
        cnes_id = row.get("cnes_id")
        esfera_final, sus_badge_val, convenios, override_hit = _apply_cnes_overrides(cnes_id, esfera_final, sus_badge_val, nome)
        # Garantir que esfera_final nunca seja "Desconhecido" após overrides
        esfera_final = _normalize_esfera(esfera_final, nome) or "Privado"
        lat_f, lon_f = row.get("lat"), row.get("lon")
        dist = row.get("distancia_km")
        if dist is None and lat_f is not None and lon_f is not None:
            dist = round(haversine_distance(lat, lon, float(lat_f), float(lon_f)), 2)
        origin = f"{lat},{lon}"
        dest = f"{lat_f},{lon_f}" if (lat_f is not None and lon_f is not None) else ""
        rotas_url = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={dest}" if dest else None
        return {
            "nome": nome,
            "cnes_id": cnes_id,
            "esfera": esfera_final,
            "sus_badge": sus_badge_val or None,
            "atende_sus": str(atende_label).strip() if atende_label and str(atende_label).strip() not in ("", "nan") else None,
            "has_maternity": bool(has_mat),
            "label_maternidade": label_maternidade,
            "telefone": telefone,
            "telefone_formatado": disp,
            "phone_e164": e164,
            "endereco": row.get("endereco"),
            "lat": lat_f,
            "lon": lon_f,
            "distancia_km": dist,
            "tempo_estimado_seg": row.get("tempo_estimado_seg"),
            "rotas_url": rotas_url,
            "banner_192": banner_192,
            "convenios": convenios,  # Lista de convênios do CNES (até 3, sem SUS)
            "has_convenios": len(convenios) > 0,  # Flag booleana
            "override_hit": override_hit,
        }

    results = []
    banner_192 = False
    radii = [radius_km, 50.0, 100.0] if expand else [radius_km]
    for r_km in radii:
        a_in = in_radius(group_a, r_km)
        if a_in:
            results = [format_item(x) for x in a_in[:limit]]
            results = _enrich_travel_time_and_sort(results, lat, lon)
            return results, "2025-02", banner_192
        b_in = in_radius(group_b, r_km)
        if b_in:
            results = [format_item(x) for x in b_in[:limit]]
            results = _enrich_travel_time_and_sort(results, lat, lon)
            return results, "2025-02", banner_192
    # Nada no raio até 100 km: top 3 do grupo C (ou todos) com banner_192
    all_c = []
    for row in group_c:
        la, lo = row.get("lat"), row.get("lon")
        if la is None or lo is None:
            continue
        row["distancia_km"] = round(haversine_distance(lat, lon, float(la), float(lo)), 2)
        all_c.append(row)
    all_c.sort(key=lambda x: x["distancia_km"])
    if all_c:
        results = [format_item(x, banner_192=True) for x in all_c[: min(3, limit)]]
        results = _enrich_travel_time_and_sort(results, lat, lon)
        return results, "2025-02", True
    # Fallback: top 3 de qualquer grupo (sempre retorna algo no país)
    combined = group_a + group_b + group_c
    for row in combined:
        la, lo = row.get("lat"), row.get("lon")
        if la is None or lo is None:
            continue
        row["distancia_km"] = round(haversine_distance(lat, lon, float(la), float(lo)), 2)
    combined.sort(key=lambda x: x.get("distancia_km", float("inf")))
    results = [format_item(combined[i], banner_192=True) for i in range(min(3, len(combined)))]
    results = _enrich_travel_time_and_sort(results, lat, lon)
    return results, "2025-02", True


@router.get("/emergency/search")
async def emergency_search(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    sus: Optional[bool] = Query(None, description="Filtrar apenas quem atende SUS"),
    radius_km: float = Query(25.0, ge=1, le=200, description="Raio em km"),
    expand: bool = Query(True, description="Expandir raio e incluir prováveis/outros se vazio"),
    limit: int = Query(10, ge=1, le=50, description="Máximo de resultados (top N)"),
    min_results: int = Query(3, ge=1, le=50, description="Mínimo de resultados (expande raio até atingir)"),
    debug: bool = Query(False, description="Incluir meta de debug (radius_used, found_A, found_B, etc.)"),
):
    """
    GET /v1/emergency/search – Busca em 3 camadas (A confirmados, B prováveis, C outros).
    Parâmetros: lat, lon, sus (opcional), radius_km=25, expand=true, limit=10, min_results=3, debug=false.
    """
    df, results, banner, meta, nearby_confirmed = geo_v2_search_driver(lat, lon, sus, radius_km, expand, limit, min_results)
    if df is None:
        raise HTTPException(
            status_code=503,
            detail="Dataset geográfico indisponível. Rode prepare_geo_v2 e geocode_ready.",
        )
    results_out = (results or [])[:limit]
    nearby_out = nearby_confirmed or []
    
    # Guard final: garantir que nenhum resultado tenha "Desconhecido" em esfera
    # Normaliza TODOS os valores de esfera (não só "Desconhecido") para garantir canonicidade
    for r in results_out:
        esfera_val = r.get("esfera")
        if esfera_val:
            esfera_str = str(esfera_val).strip()
            if esfera_str.lower() == "desconhecido" or esfera_str not in ("Público", "Privado", "Filantrópico"):
                # Normaliza qualquer valor inválido
                r["esfera"] = _normalize_esfera(esfera_str, r.get("nome")) or "Privado"
    for r in nearby_out:
        esfera_val = r.get("esfera")
        if esfera_val:
            esfera_str = str(esfera_val).strip()
            if esfera_str.lower() == "desconhecido" or esfera_str not in ("Público", "Privado", "Filantrópico"):
                # Normaliza qualquer valor inválido
                r["esfera"] = _normalize_esfera(esfera_str, r.get("nome")) or "Privado"
    
    if not debug:
        for r in results_out:
            r.pop("override_hit", None)
            r.pop("override_reason", None)
        for r in nearby_out:
            r.pop("override_hit", None)
            r.pop("override_reason", None)
    else:
        try:
            from backend.startup.cnes_overrides import has_cnes
        except Exception:
            has_cnes = lambda *_: False
        for r in results_out:
            ovr = r.get("override_hit")
            cid = r.get("cnes_id")
            r["override_reason"] = "applied" if ovr else ("no_match" if (cid and not has_cnes(cid)) else "not_applied")
        for r in nearby_out:
            ovr = r.get("override_hit")
            cid = r.get("cnes_id")
            r["override_reason"] = "applied" if ovr else ("no_match" if (cid and not has_cnes(cid)) else "not_applied")
        hits = sum(1 for r in results_out if r.get("override_hit"))
        total = len(results_out)
        if meta is None:
            meta = {}
        meta = dict(meta)
        meta["override_hits"] = hits
        meta["override_total"] = total
        meta["override_coverage_pct"] = round(hits / total, 4) if total else 0.0
    body = {
        "results": results_out,
        "nearby_confirmed": nearby_out,
        "banner_192": bool(banner),
        "generated_at": pd.Timestamp.utcnow().isoformat(),
    }
    if debug and meta:
        body["debug"] = meta
    info = get_geo_data_info()
    if isinstance(info, dict):
        src = info.get("source_path") or info.get("source")
        mtime = info.get("mtime")
    elif isinstance(info, (tuple, list)) and len(info) >= 2:
        src, mtime = info[0], info[1]
    else:
        src, mtime = None, None
    headers = {}
    if src:
        headers["X-Data-Source"] = src
    if mtime is not None:
        headers["X-Data-Mtime"] = str(int(mtime))
    return JSONResponse(content=body, headers=headers)


@router.post("/emergency/reload")
async def emergency_reload():
    """
    POST /v1/emergency/reload – Limpa cache do dataset geo e força recarga na próxima busca.
    Útil após atualizar a base (parquet) para não reiniciar o processo.
    """
    ok, rows, err = refresh_geo_cache()
    if not ok:
        raise HTTPException(status_code=500, detail=err or "Falha ao recarregar cache")
    return {"ok": True, "rows": rows}


@router.get("/establishments/{cnes_id}")
async def get_establishment(cnes_id: str):
    """
    GET /v1/establishments/{cnes_id} – Detalhe de um estabelecimento por CNES ID.
    Contrato: backend/api/contracts/get_establishment_by_id.json
    """
    try:
        conn = facility_service._get_connection()
        row = conn.execute(
            "SELECT cnes_id, name, fantasy_name, address, city, state, telefone AS phone, "
            "lat, long, has_maternity, is_sus, management, data_source_date FROM hospitals_cache WHERE cnes_id = ?",
            (cnes_id.strip(),),
        ).fetchone()
        conn.close()
        if not row:
            raise HTTPException(status_code=404, detail="Estabelecimento não encontrado.")
        r = {k: row[k] for k in row.keys()}
        phone_raw = r.get("phone")
        telefone_formatado, phone_e164 = format_br_phone(phone_raw)
        nome = (r.get("fantasy_name") or r.get("name") or "").strip() or r.get("name")
        esfera_map = {"MUNICIPAL": "Público", "ESTADUAL": "Público", "FEDERAL": "Público", "PRIVADO": "Privado", "DUPLA": "Público"}
        esfera_raw = esfera_map.get(str(r.get("management") or "").upper(), None)
        atende_label = "Sim" if r.get("is_sus") else "Não"
        esfera_final = _normalize_esfera(esfera_raw, nome) or "Privado"  # Fallback para Privado se None
        sus_badge_val = _sus_badge(atende_label, esfera_final)
        esfera_final, sus_badge_val, convenios, _ = _apply_cnes_overrides(cnes_id.strip(), esfera_final, sus_badge_val, nome)
        # Garantir que esfera_final nunca seja "Desconhecido" após overrides
        esfera_final = _normalize_esfera(esfera_final, nome) or "Privado"
        return {
            "id": r["cnes_id"],
            "name": r["name"] or r.get("fantasy_name"),
            "fantasy_name": r.get("fantasy_name"),
            "address": r.get("address"),
            "city": r.get("city"),
            "state": r.get("state"),
            "phone": r.get("phone"),
            "telefone_formatado": telefone_formatado,
            "phone_e164": phone_e164,
            "lat": r.get("lat"),
            "long": r.get("long"),
            "maternity_status": "Sim" if r.get("has_maternity") else "Não listado",
            "score": 0.6 if r.get("has_maternity") else 0.0,
            "evidence": [],
            "atende_sus": atende_label,
            "esfera": esfera_final,
            "sus_badge": sus_badge_val or None,
            "has_convenios": len(convenios) > 0,
            "convenios": convenios,
            "data_version": r.get("data_source_date"),
        }
    except HTTPException:
        raise
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="Serviço indisponível. Banco CNES não inicializado.")
    except Exception as e:
        logger.error(f"❌ Erro establishments/{cnes_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro ao buscar estabelecimento.")


@router.get("/establishments/{cnes_id}/evidence")
async def get_establishment_evidence(cnes_id: str):
    """
    GET /v1/establishments/{cnes_id}/evidence – Evidências de classificação maternidade (tipo, código, fonte).
    Contrato: backend/api/contracts/get_evidence.json
    """
    try:
        conn = facility_service._get_connection()
        row = conn.execute(
            "SELECT cnes_id, has_maternity, data_source_date FROM hospitals_cache WHERE cnes_id = ?",
            (cnes_id.strip(),),
        ).fetchone()
        conn.close()
        if not row:
            raise HTTPException(status_code=404, detail="Estabelecimento não encontrado.")
        r = {k: row[k] for k in row.keys()}
        # Evidências: v_maternity_status/maternity_classification quando existir; senão derivado de hospitals_cache
        evidence = []
        if r.get("has_maternity"):
            evidence = [{"type": "keyword", "code": "has_maternity", "source": "keyword"}]
        return {
            "cnes_id": r["cnes_id"],
            "has_maternity": bool(r.get("has_maternity")),
            "score": 0.6 if r.get("has_maternity") else 0.0,
            "evidence": evidence,
            "data_version": r.get("data_source_date"),
        }
    except HTTPException:
        raise
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="Serviço indisponível. Banco CNES não inicializado.")
    except Exception as e:
        logger.error(f"❌ Erro establishments/{cnes_id}/evidence: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro ao buscar evidências.")


@router.get("/debug/overrides/coverage")
async def debug_overrides_coverage():
    """
    GET /v1/debug/overrides/coverage – Cobertura dos overrides CNES (para diagnóstico).
    Responde: total_loaded, snapshot_usado.
    """
    try:
        from backend.startup.cnes_overrides import get_snapshot_used, get_overrides_count
    except Exception:
        return {"total_loaded": 0, "snapshot_usado": None, "error": "Overrides não carregados"}
    return {
        "total_loaded": get_overrides_count(),
        "snapshot_usado": get_snapshot_used(),
    }


@router.post("/debug/overrides/refresh")
async def debug_overrides_refresh():
    """POST /v1/debug/overrides/refresh – Recarrega overrides do CNES sem reiniciar."""
    try:
        from backend.startup.cnes_overrides import boot as ovr_boot, get_snapshot_used, get_overrides_count
    except Exception:
        raise HTTPException(status_code=500, detail="Overrides indisponíveis")
    import os
    snap = os.getenv("SNAPSHOT", "202512")
    try:
        ovr_boot(snap, force=True)
        return {"ok": True, "snapshot": get_snapshot_used(), "count": get_overrides_count()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/debug/geo/refresh")
async def debug_geo_refresh():
    """POST /v1/debug/geo/refresh – Limpa cache geo e força re-load do Parquet."""
    ok, rows, error = refresh_geo_cache()
    if ok:
        return {"ok": True, "rows": rows}
    else:
        raise HTTPException(status_code=500, detail=error or "Erro ao recarregar geo")


@router.get("/facilities/health")
async def health_check():
    """Health check do serviço de facilidades (GET /v1/facilities/health e contrato healthcheck/version)"""
    try:
        conn = facility_service._get_connection()
        conn.close()
        return {"status": "ok", "service": "facilities_search", "database": "connected"}
    except Exception as e:
        logger.warning(f"⚠️ Health check falhou: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "error", "service": "facilities_search", "database": "disconnected", "error": str(e)},
        )


@router.get("/version")
async def version():
    """GET /v1/version – Versão da API e data_version dos dados."""
    return {"version": "1.0.0", "api_name": "API Emergência Obstétrica / Facilidades Puerperais", "data_version": "2025-02"}


