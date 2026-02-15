# -*- coding: utf-8 -*-
"""
CNES Overrides: carrega tbEstabelecimento e tbEstabPrestConv do CNES
e calcula esfera/SUS/convênios para sobrescrever no payload da API.
Versão performática: usecols, vetorização, lazy boot e cache .pkl.
"""
from __future__ import annotations

import os
import re
import pickle
import hashlib
import threading
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

import pandas as pd
import numpy as np

_FILE = Path(__file__).resolve()
BASE = _FILE.parents[2]  # backend/startup -> backend -> raiz
DATA = BASE / "data"
RAW = DATA / "raw"
CACHE_DIR = DATA / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

_LOCK = threading.Lock()

# Estado em memória
_OVR: Dict[str, Dict[str, Any]] = {}
_SNAPSHOT_USED: Optional[str] = None
_LOADED = False

# Colunas desejadas (case-insensitive no CSV)
USECOLS_EST = [
    "CO_CNES", "CO_UNIDADE", "CNES", "CNES_ID",
    "NO_RAZAO_SOCIAL", "NO_FANTASIA", "NOME", "NOME_FANTASIA",
    "ESFERA_ADMIN", "NO_ESFERA", "ESFERA",
    "CO_NATUREZA_JURIDICA", "NAT_JUR", "NO_NATUREZA", "NATUREZA_JURIDICA",
    "IND_SUS", "ATEND_SUS", "IND_ATEND_SUS",
]
USECOLS_CONV = ["CO_CNES", "CO_UNIDADE", "CNES", "CNES_ID", "NO_CONVENIO", "CONVENIO", "DS_CONVENIO"]


def _norm7(v: Any) -> str:
    """Normaliza CNES: remove não-dígitos, pega 7 primeiros, zfill."""
    s = re.sub(r"\D", "", str(v or ""))
    return (s[:7] if len(s) >= 7 else s).zfill(7) if s else ""


def _paths_for_snapshot(snapshot: str) -> Tuple[Optional[Path], Optional[Path]]:
    """Retorna (path_estabelecimento, path_convenios) se existirem."""
    cand_est = [
        DATA / f"tbEstabelecimento{snapshot}.csv",
        DATA / "raw" / snapshot / f"tbEstabelecimento{snapshot}.csv",
        BASE / f"BASE_DE_DADOS_CNES{snapshot}" / f"tbEstabelecimento{snapshot}.csv",
        BASE / f"BASE_DE_DADOS_CNES_{snapshot}" / f"tbEstabelecimento{snapshot}.csv",
    ]
    cand_conv = [
        DATA / f"tbEstabPrestConv{snapshot}.csv",
        DATA / "raw" / snapshot / f"tbEstabPrestConv{snapshot}.csv",
        BASE / f"BASE_DE_DADOS_CNES{snapshot}" / f"tbEstabPrestConv{snapshot}.csv",
        BASE / f"BASE_DE_DADOS_CNES_{snapshot}" / f"tbEstabPrestConv{snapshot}.csv",
        BASE / f"BASE_DE_DADOS_CNES_{snapshot}" / f"rlEstabPrestConv{snapshot}.csv",
    ]
    est = next((p for p in cand_est if p.exists()), None)
    conv = next((p for p in cand_conv if p.exists()), None)
    return est, conv


def _detect_snapshot() -> Optional[str]:
    """Detecta o snapshot mais recente (tbEstabelecimentoYYYYMM.csv)."""
    snaps = []
    for p in list(DATA.glob("tbEstabelecimento*.csv")):
        m = re.search(r"tbEstabelecimento(\d{6,}).csv$", p.name, re.IGNORECASE)
        if m and m.group(1).isdigit():
            snaps.append(m.group(1))
    if RAW.exists():
        for sub in RAW.iterdir():
            if sub.is_dir():
                for p in sub.glob("tbEstabelecimento*.csv"):
                    m = re.search(r"tbEstabelecimento(\d{6,}).csv$", p.name, re.IGNORECASE)
                    if m and m.group(1).isdigit():
                        snaps.append(m.group(1))
    for p in BASE.glob("BASE_DE_DADOS_CNES*/tbEstabelecimento*.csv"):
        m = re.search(r"tbEstabelecimento(\d{6,}).csv$", p.name, re.IGNORECASE)
        if m and m.group(1).isdigit():
            snaps.append(m.group(1))
    if not snaps:
        return None
    return sorted(set(snaps))[-1]


def _read_csv_any(p: Optional[Path], usecols: list[str]) -> Optional[pd.DataFrame]:
    """Lê CSV com separador/encoding flexível; carrega só colunas em usecols (case-insensitive)."""
    if not p or not p.exists():
        return None
    if p.suffix.lower() == ".parquet":
        try:
            df = pd.read_parquet(p)
            cols_upper = {c.upper(): c for c in df.columns}
            sel = [cols_upper[u] for u in (x.upper() for x in usecols) if u in cols_upper]
            return df[sel] if sel else None
        except Exception:
            return None
    want_upper = {u.upper() for u in usecols}
    for sep in (";", ","):
        for enc in ("utf-8", "latin-1"):
            try:
                df = pd.read_csv(p, sep=sep, dtype=str, low_memory=False, encoding=enc)
                sel = [c for c in df.columns if c.upper() in want_upper]
                if not sel:
                    continue
                return df[sel].copy()
            except Exception:
                continue
    return None


def _pick(df: pd.DataFrame, names: list[str]) -> Optional[str]:
    """Retorna primeira coluna que exista (case-insensitive)."""
    cols = {c.lower(): c for c in df.columns}
    for n in names:
        if n in df.columns:
            return n
        if n.lower() in cols:
            return cols[n.lower()]
    return None


def _ser(df: pd.DataFrame, col: Optional[str]) -> pd.Series:
    """Coluna como Series ou vazia com mesmo index."""
    if col and col in df.columns:
        return df[col].fillna("")
    return pd.Series("", index=df.index)


def _esfera_from_cols(
    esfera_admin: pd.Series,
    co_nat: pd.Series,
    no_nat: pd.Series,
    nome: pd.Series,
) -> pd.Series:
    """Calcula esfera vetorizado."""
    ea = esfera_admin.astype(str).str.lower()
    co = co_nat.astype(str).str.strip()
    txt = (no_nat.astype(str) + " " + nome.astype(str)).str.lower()
    cond_pub = (
        ea.str.contains(r"municip|estad|federal", regex=True, na=False)
        | co.str.startswith("1")
        | txt.str.contains(
            r"administra|fund[aã]o p[úu]blica|autarquia|universidade p[úu]blica|municip|estad|federal",
            regex=True,
            na=False,
        )
    )
    cond_fil = (
        co.str.startswith("3")
        | txt.str.contains(
            r"santa casa|filantr|beneficen|misericord|irmandade|fund[aã]o|sem fins lucr",
            regex=True,
            na=False,
        )
    )
    return pd.Series(
        np.select([cond_pub, cond_fil], ["Público", "Filantrópico"], default="Privado"),
        index=nome.index,
    )


def _sus_badge_from_cols(ind: pd.Series, atend: pd.Series, esfera: pd.Series) -> pd.Series:
    """Calcula sus_badge vetorizado."""
    a = ind.astype(str).str.upper()
    b = atend.astype(str).str.upper()
    sim = a.isin(["S", "SIM", "1", "TRUE"]) | b.isin(["S", "SIM", "1", "TRUE"])
    nao = a.isin(["N", "NAO", "NÃO", "0", "FALSE"]) | b.isin(["N", "NAO", "NÃO", "0", "FALSE"])
    return pd.Series(
        np.select(
            [sim, nao, esfera.eq("Público")],
            ["Aceita Cartão SUS", "Não atende SUS", "Aceita Cartão SUS"],
            default="",
        ),
        index=esfera.index,
    )


def _build_overrides(est: pd.DataFrame, conv: Optional[pd.DataFrame]) -> Dict[str, Dict[str, Any]]:
    """Monta dict de overrides a partir dos DataFrames (vetorizado)."""
    c_cnes = _pick(est, ["CO_CNES", "CO_UNIDADE", "CNES", "CNES_ID"])
    if not c_cnes:
        return {}
    est = est.copy()
    est["_cnes"] = est[c_cnes].map(_norm7)
    c_nome = _pick(est, ["NO_RAZAO_SOCIAL", "NO_FANTASIA", "NOME", "NOME_FANTASIA"])
    c_esfa = _pick(est, ["ESFERA_ADMIN", "NO_ESFERA", "ESFERA"])
    c_conat = _pick(est, ["CO_NATUREZA_JURIDICA", "NAT_JUR"])
    c_nonat = _pick(est, ["NO_NATUREZA", "NATUREZA_JURIDICA"])
    c_sus1 = _pick(est, ["IND_SUS", "IND_ATEND_SUS"])
    c_sus2 = _pick(est, ["ATEND_SUS"])

    esfera = _esfera_from_cols(
        _ser(est, c_esfa),
        _ser(est, c_conat),
        _ser(est, c_nonat),
        _ser(est, c_nome),
    )
    sus = _sus_badge_from_cols(_ser(est, c_sus1), _ser(est, c_sus2), esfera)

    conv_map: Dict[str, list] = {}
    if conv is not None and len(conv.columns) > 0:
        cc = _pick(conv, ["CO_CNES", "CO_UNIDADE", "CNES", "CNES_ID"])
        cn = _pick(conv, ["NO_CONVENIO", "CONVENIO", "DS_CONVENIO"])
        if cc and cn:
            conv = conv.copy()
            conv["_cnes"] = conv[cc].map(_norm7)
            conv["_cv"] = conv[cn].astype(str).str.strip()
            mask = ~conv["_cv"].str.contains(r"\bSUS\b", case=False, na=False)
            valid = conv[mask]
            for cid, grp in valid.groupby("_cnes")["_cv"]:
                vals = [x for x in grp.unique() if x and str(x).strip()][:3]
                if vals:
                    conv_map[cid] = vals

    ovr: Dict[str, Dict[str, Any]] = {}
    for cid, e, s_ in zip(est["_cnes"], esfera, sus):
        if cid:
            ovr[cid] = {
                "esfera": str(e),
                "sus_badge": str(s_),
                "convenios": conv_map.get(cid, []),
            }
    return ovr


def _cache_path(snapshot: str, est: Path, conv: Optional[Path]) -> Path:
    """Path do cache .pkl baseado em snapshot e mtime dos arquivos."""
    m_est = est.stat().st_mtime_ns if est.exists() else 0
    m_conv = conv.stat().st_mtime_ns if conv and conv.exists() else 0
    key = f"{snapshot}_{m_est}_{m_conv}"
    h = hashlib.sha256(key.encode()).hexdigest()[:24]
    return CACHE_DIR / f"cnes_overrides_{h}.pkl"


def _load_cache(p: Path) -> Optional[Dict[str, Dict[str, Any]]]:
    try:
        with open(p, "rb") as f:
            return pickle.load(f)
    except Exception:
        return None


def _save_cache(p: Path, data: Dict[str, Dict[str, Any]]) -> None:
    try:
        with open(p, "wb") as f:
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception:
        pass


def _boot_inner(snapshot: str) -> Tuple[Dict[str, Dict[str, Any]], str]:
    """Carrega overrides (CSV ou cache). Retorna (ovr_dict, snapshot_usado)."""
    est_path, conv_path = _paths_for_snapshot(snapshot)
    if os.getenv("OVERRIDES_CONVENIOS", "on").lower() not in ("1", "true", "on", "yes"):
        conv_path = None  # start ultra-rápido: pula convênios
    if est_path is None:
        det = _detect_snapshot()
        if det:
            snapshot = det
            est_path, conv_path = _paths_for_snapshot(snapshot)
        if est_path is None:
            print("[CNES/OVR] tbEstabelecimento não encontrado; overrides desativados.")
            return {}, snapshot

    if est_path:
        print(f"[CNES/OVR] usando {est_path}")
    est_df = _read_csv_any(est_path, USECOLS_EST)
    if est_df is None or est_df.empty:
        print("[CNES/OVR] Falha ao ler tbEstabelecimento; overrides desativados.")
        return {}, snapshot
    conv_df = _read_csv_any(conv_path, USECOLS_CONV) if conv_path else None

    cache_p = _cache_path(snapshot, est_path, conv_path or est_path)
    cached = _load_cache(cache_p)
    if cached is not None:
        print(f"[CNES/OVR] cache carregado: {cache_p.name}")
        return cached, snapshot

    ovr = _build_overrides(est_df, conv_df)
    _save_cache(cache_p, ovr)
    return ovr, snapshot


def _boot_unlocked(snapshot: Optional[str] = None, force: bool = False) -> None:
    """Implementação do boot (chamar apenas com _LOCK segurado)."""
    global _OVR, _SNAPSHOT_USED, _LOADED
    if _LOADED and not force:
        return
    snap = (snapshot or os.environ.get("SNAPSHOT", "202512")).strip()
    ovr, used = _boot_inner(snap)
    _OVR = ovr
    _SNAPSHOT_USED = used
    _LOADED = True
    print(f"[CNES/OVR] overrides prontos: {len(_OVR)} CNES (snapshot={_SNAPSHOT_USED})")


def boot(snapshot: Optional[str] = None, force: bool = False) -> None:
    """Carrega overrides (lazy: só executa uma vez; force=True reprocessa). Thread-safe."""
    with _LOCK:
        _boot_unlocked(snapshot, force)


def ensure_boot() -> None:
    """Garante que overrides estão carregados (lock evita boot duplo na primeira requisição)."""
    if _LOADED:
        return
    with _LOCK:
        if not _LOADED:
            _boot_unlocked(None, False)


def get_overrides(cnes_id: str) -> Optional[Dict[str, Any]]:
    """Retorna override para um CNES (esfera, sus_badge, convenios) ou None."""
    ensure_boot()
    return _OVR.get(_norm7(cnes_id))


def has_cnes(cnes_id: str) -> bool:
    """Confere se o CNES existe no mapa de overrides."""
    ensure_boot()
    return _norm7(cnes_id) in _OVR


def get_snapshot_used() -> Optional[str]:
    """Snapshot efetivamente carregado (para debug/coverage)."""
    ensure_boot()
    return _SNAPSHOT_USED


def get_overrides_count() -> int:
    """Quantidade de CNES com override carregado (para debug/coverage)."""
    ensure_boot()
    return len(_OVR)
