# backend/pipelines/prepare_geo_v2.py
import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA = BASE_DIR / "data"
OUT = DATA / "geo"
OUT.mkdir(parents=True, exist_ok=True)

try:
    from backend.utils.phone import format_br_phone
except ImportError:
    sys.path.insert(0, str(BASE_DIR))
    from backend.utils.phone import format_br_phone

INCLUDE_KWS = ["hospital", "matern", "materno", "casa de parto"]

# Exclusões mais agressivas (serviços de apoio, antipólvora: psicologia/ambulatoriais)
EXCLUDE_KWS_DEFAULT = [
    "odonto", "dent", "laborat", "diagnost", "imagem", "radiolog", "ultra", "tomograf", "resson",
    "ambulatório", "ambulatorio", "farmac", "upa", "caps", "policlin", "psf", "esf",
    "agência transfusional", "agencia transfusional", "hemocentro", "banco de leite",
    "psicolog", "psico", "fono", "fonoaudiol", "fisioter", "terapia ocup", "nutri",
    "optica", "oficina ortop", "consultório", "consultorio",
]


def _digits(s) -> str:
    return re.sub(r"\D", "", str(s or ""))


def _norm_cnes(s) -> str:
    t = _digits(s)
    if not t:
        return ""
    return t[:7].zfill(7) if len(t) >= 7 else t.zfill(7)


def _load_filters_from_config() -> list:
    try:
        cfg = json.loads((BASE_DIR / "config" / "cnes_codes.json").read_text(encoding="utf-8"))
        extra = [str(x).lower() for x in cfg.get("extra_exclude_keywords", [])]
    except Exception:
        extra = []
    return list(dict.fromkeys(EXCLUDE_KWS_DEFAULT + extra))


def _find_file(snapshot: str, base: str) -> Path:
    candidates = [
        DATA / f"{base}{snapshot}.parquet",
        DATA / f"{base}{snapshot}.csv",
        DATA / "raw" / snapshot / f"{base}{snapshot}.parquet",
        DATA / "raw" / snapshot / f"{base}{snapshot}.csv",
    ]
    if base.lower() == "tbleito":
        candidates += [
            DATA / f"rlEstabLeito{snapshot}.csv",
            DATA / f"rlEstabLeito{snapshot}.parquet",
            DATA / "raw" / snapshot / f"rlEstabLeito{snapshot}.csv",
            DATA / "raw" / snapshot / f"rlEstabLeito{snapshot}.parquet",
            BASE_DIR / f"BASE_DE_DADOS_CNES_{snapshot}" / f"rlEstabLeito{snapshot}.csv",
            BASE_DIR / f"BASE_DE_DADOS_CNES_{snapshot}" / f"rlEstabLeito{snapshot}.parquet",
            BASE_DIR / "BASE_DE_DADOS_CNES_202512" / f"rlEstabLeito{snapshot}.csv",
            BASE_DIR / "BASE_DE_DADOS_CNES_202512" / f"rlEstabLeito{snapshot}.parquet",
        ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError(f"Arquivo não encontrado: {base}{snapshot}.csv|parquet em data/ ou data/raw/{snapshot}/")


def _find_servclass(snapshot: str) -> Path | None:
    """Procura rlEstabServClass (serviço por estabelecimento) para fallback 'sinal forte'."""
    candidates = [
        DATA / f"rlEstabServClass{snapshot}.csv",
        DATA / f"rlEstabServClass{snapshot}.parquet",
        DATA / "raw" / snapshot / f"rlEstabServClass{snapshot}.csv",
        BASE_DIR / f"BASE_DE_DADOS_CNES_{snapshot}" / f"rlEstabServClass{snapshot}.csv",
        BASE_DIR / "BASE_DE_DADOS_CNES_202512" / f"rlEstabServClass{snapshot}.csv",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def _load_servclass_cnes(snapshot: str) -> set:
    """Retorna set de cnes_id com serviço obst/neonatal (Urgência Obstétrica etc.) para marcar Confirmado."""
    path = _find_servclass(snapshot)
    if not path:
        return set()
    try:
        cfg = json.loads((BASE_DIR / "config" / "cnes_codes.json").read_text(encoding="utf-8"))
        services = set(str(x) for x in cfg.get("services_obst", []) or ["125", "141"])
        classif = set(str(x) for x in cfg.get("classif_obst", []) or ["001"])
    except Exception:
        services, classif = {"125", "141"}, {"001"}
    try:
        if path.suffix.lower() == ".parquet":
            df = pd.read_parquet(path)
        else:
            try:
                df = pd.read_csv(path, sep=";", dtype=str, low_memory=False, encoding="utf-8")
            except UnicodeDecodeError:
                df = pd.read_csv(path, sep=";", dtype=str, low_memory=False, encoding="ISO-8859-1", on_bad_lines="skip")
        col_cnes = _pick(df, ["CO_UNIDADE", "CO_CNES", "CNES", "CNES_ID"])
        col_serv = _pick(df, ["CO_SERVICO", "CO_SERVICO_ESPECIALIZADO", "CO_SERVICO_ESP"])
        col_class = _pick(df, ["CO_CLASSIFICACAO", "CO_CLASS", "CO_CLASSIFICACAO_SERVICO"])
        if not col_cnes or not col_serv or not col_class:
            return set()
        df["cnes_id"] = df[col_cnes].apply(_norm_cnes)
        mask = df[col_serv].astype(str).str.strip().isin(services) & df[col_class].astype(str).str.strip().isin(classif)
        ids = df.loc[mask, "cnes_id"].unique().tolist()
        return set(x for x in ids if x and len(x) == 7)
    except Exception:
        return set()


def _find_habilitacao(snapshot: str) -> Path | None:
    """Procura rlEstabHabilitacao (habilitação por estabelecimento) para fallback 'sinal forte'."""
    candidates = [
        DATA / f"rlEstabHabilitacao{snapshot}.csv",
        DATA / f"rlEstabHabilitacao{snapshot}.parquet",
        DATA / "raw" / snapshot / f"rlEstabHabilitacao{snapshot}.csv",
        DATA / "raw" / snapshot / f"rlEstabHabilitacao{snapshot}.parquet",
        BASE_DIR / f"BASE_DE_DADOS_CNES_{snapshot}" / f"rlEstabHabilitacao{snapshot}.csv",
        BASE_DIR / "BASE_DE_DADOS_CNES_202512" / f"rlEstabHabilitacao{snapshot}.csv",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def _load_habilitacao_cnes(snapshot: str) -> tuple[set, Path | None]:
    """Retorna (set de cnes_id com habilitação obst/neonat/CPN, path ou None)."""
    path = _find_habilitacao(snapshot)
    if not path:
        return set(), None
    try:
        if path.suffix.lower() == ".parquet":
            df = pd.read_parquet(path)
        else:
            try:
                df = pd.read_csv(path, sep=";", dtype=str, low_memory=False, encoding="utf-8")
            except UnicodeDecodeError:
                df = pd.read_csv(path, sep=";", dtype=str, low_memory=False, encoding="ISO-8859-1", on_bad_lines="skip")
    except Exception:
        return set(), None
    col_cnes = _pick(df, ["CO_UNIDADE", "CO_CNES", "CNES", "CNES_ID"])
    col_txt = _pick(df, ["DS_HABILITACAO", "NO_HABILITACAO", "HABILITACAO", "DS_HABIL"])
    col_cod = _pick(df, ["CO_HABILITACAO", "CO_HABILITA", "COD_HABILITACAO"])
    if not col_cnes or not (col_txt or col_cod):
        return set(), None
    df["cnes_id"] = df[col_cnes].apply(_norm_cnes)
    txt = df[col_txt].astype(str) if col_txt else (df[col_cod].astype(str) if col_cod else pd.Series([""] * len(df)))
    patt = re.compile(r"(obstet|neonat|cpn|parto|nascer)", re.I)
    mask = txt.str.contains(patt, na=False)
    hab = set(df.loc[mask & (df["cnes_id"].str.len() == 7), "cnes_id"].unique().tolist())
    return hab, path


def _read_any(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    try:
        return pd.read_csv(path, sep=";", dtype=str, low_memory=False, encoding="utf-8")
    except Exception:
        pass
    try:
        return pd.read_csv(path, sep=";", dtype=str, low_memory=False, encoding="ISO-8859-1", on_bad_lines="skip")
    except Exception:
        return pd.read_csv(path, sep=",", dtype=str, low_memory=False)


def _pick(df: pd.DataFrame, names: list) -> str | None:
    cols = {str(c).lower(): c for c in df.columns}
    for n in names:
        if n in df.columns:
            return n
        if str(n).lower() in cols:
            return cols[str(n).lower()]
    return None


def _contains_any(text, kws: list) -> bool:
    if not isinstance(text, str) or (isinstance(text, float) and np.isnan(text)):
        text = ""
    t = (text or "").lower()
    return any(k in t for k in kws)


def _derive_esfera(text) -> str:
    if not isinstance(text, str) or (isinstance(text, float) and np.isnan(text)):
        text = ""
    t = (text or "").lower()
    if any(k in t for k in ["municip", "estad", "federal", "públic", "public"]):
        return "Público"
    if "filantr" in t or "santa casa" in t:
        return "Filantrópico"
    if t:
        return "Privado"
    return "Privado"  # Fallback para Privado ao invés de "Desconhecido"


def _derive_esfera_v2(co_nat: str | None, no_nat: str | None, esfera_txt: str | None) -> str:
    """Esfera robusta: código IBGE (1xxx Público, 2xxx Privado, 3xxx Filantrópico) + texto."""
    co = (str(co_nat or "").strip()[:1] or "")
    txt = (str(no_nat or "") + " " + str(esfera_txt or "")).lower()
    if co == "1" or any(k in txt for k in ["administra", "municip", "estad", "federal", "públic", "public"]):
        return "Público"
    if co == "3" or any(k in txt for k in ["filantr", "santa casa", "sem fins lucr", "fundação", "fundacao", "oscip", "associação", "associacao"]):
        return "Filantrópico"
    return "Privado"


def _map_sus(v1: str | None, v2: str | None) -> str:
    vals = {(v1 or "").strip().upper(), (v2 or "").strip().upper()}
    if "SIM" in vals or "S" in vals or "1" in vals:
        return "Sim"
    if "NAO" in vals or "NÃO" in vals or "N" in vals or "0" in vals:
        return "Não"
    return ""  # Retorna vazio ao invés de "Desconhecido" (será tratado pelo _sus_badge)


def _map_sus_v2(ind: str | None, atend: str | None) -> tuple[str, bool | None]:
    """SUS efetivo: retorna (label, bool para badge)."""
    vals = {(ind or "").strip().upper(), (atend or "").strip().upper()}
    if {"S", "SIM", "1", "TRUE"} & vals:
        return "Sim", True
    if {"N", "NAO", "NÃO", "0", "FALSE"} & vals:
        return "Não", False
    return "", None  # Retorna vazio ao invés de "Desconhecido" (será tratado pelo _sus_badge)


def _clean_name(n: str) -> str:
    """Nome de exibição: title case, preservar siglas (SUS/UPA/UBS/SAMU), cortar sufixos jurídicos."""
    if not n:
        return ""
    s = str(n).strip()
    s = re.sub(r",?\s*(LTDA|EIRELI|S/A|S\.A\.)$", "", s, flags=re.I)
    parts = s.lower().title()
    for sig in ["SUS", "UPA", "UBS", "SAMU", "SJC", "SP"]:
        parts = re.sub(rf"\b{sig.title()}\b", sig, parts)
    return parts


def _load_codes():
    try:
        cfg = json.loads((BASE_DIR / "config" / "cnes_codes.json").read_text(encoding="utf-8"))
    except Exception:
        cfg = {}
    kw = [str(k).lower() for k in cfg.get("keywords_nome_fantasia", [])] or [
        "maternidade", "hospital da mulher", "obstétrico",
        "hospital e maternidade", "materno infantil", "materno-infantil", "casa de parto",
    ]
    def _norm_code(x):
        return (str(x).strip().lstrip("0") or "0") if x is not None and str(x).strip() else "0"
    codes_obs = set(_norm_code(x) for x in cfg.get("leito_codes_obst", []))
    codes_neo = set(_norm_code(x) for x in cfg.get("leito_codes_neonatal", []))
    patt = [re.compile(p, re.I) for p in [r"obst", r"neonat", r"aloj", r"uti\s*neo", r"ucin"]]
    return kw, codes_obs, codes_neo, patt


def _detect_leitos(df_leito: pd.DataFrame) -> pd.DataFrame:
    col_cnes = _pick(df_leito, ["CO_CNES", "CO_UNIDADE", "CNES", "CNES_ID"])
    col_code = _pick(df_leito, ["CO_TIPO_LEITO", "TP_LEITO", "COD_TIPO_LEITO", "CO_LEITO"])
    col_text = _pick(df_leito, ["DS_TIPO_LEITO", "NO_TIPO_LEITO", "DS_LEITO", "TP_LEITO_DESC"])
    col_qt = _pick(df_leito, ["QT_LEITOS", "QT_EXIST", "QT_EXISTENTE", "QT_LEITO", "QT_SUS", "QT_TOTAL", "NU_LEITOS"])
    if not col_cnes or (not col_code and not col_text):
        return pd.DataFrame(columns=["cnes_id", "qtd_obsneo", "leitos_evidence"])
    if not col_qt or col_qt not in df_leito.columns:
        col_qt = "_qt"
        df_leito = df_leito.copy()
        df_leito[col_qt] = 1

    kw, codes_obs, codes_neo, patt = _load_codes()

    leito = df_leito.copy()
    leito[col_cnes] = leito[col_cnes].astype(str).str.strip()
    leito[col_qt] = pd.to_numeric(leito[col_qt], errors="coerce").fillna(0)

    if col_text and col_text in leito.columns:
        txt = leito[col_text].astype(str)
        mask_txt = txt.str.contains(patt[0], na=False, regex=True)
        for rg in patt[1:]:
            mask_txt = mask_txt | txt.str.contains(rg, na=False, regex=True)
    else:
        mask_txt = pd.Series(False, index=leito.index)

    if col_code and col_code in leito.columns and (codes_obs or codes_neo):
        leito_codes_norm = leito[col_code].astype(str).str.strip().str.lstrip("0").replace("", "0")
        mask_code = leito_codes_norm.isin(codes_obs | codes_neo)
    else:
        mask_code = pd.Series(False, index=leito.index)

    mask = mask_txt | mask_code
    sel = leito[mask].copy()
    if sel.empty:
        return pd.DataFrame(columns=["cnes_id", "qtd_obsneo", "leitos_evidence"])

    sel["cnes_id"] = sel[col_cnes].apply(_norm_cnes)
    code_col = col_code if col_code and col_code in sel.columns else col_text

    def _ev(r):
        return {"type": "leito", "code": str(r.get(code_col, "") or ""), "source": "leito"}

    sel["leitos_evidence"] = sel.apply(_ev, axis=1)
    agg = sel.groupby("cnes_id").agg(
        qtd_obsneo=(col_qt, "sum"),
        leitos_evidence=("leitos_evidence", lambda x: list(x)),
    ).reset_index()
    return agg


def _sum_total_leitos(df_leito: pd.DataFrame) -> pd.DataFrame:
    """Soma leitos totais por estabelecimento (qualquer tipo) para flag tem_internacao."""
    col_cnes = _pick(df_leito, ["CO_CNES", "CO_UNIDADE", "CNES", "CNES_ID"])
    col_qt = _pick(df_leito, ["QT_LEITOS", "QT_EXIST", "QT_EXISTENTE", "QT_LEITO", "QT_SUS", "QT_TOTAL", "NU_LEITOS"])
    if not col_cnes or not col_qt:
        return pd.DataFrame(columns=["cnes_id", "total_leitos"])
    lt = df_leito.copy()
    lt["cnes_id"] = lt[col_cnes].apply(_norm_cnes)
    lt[col_qt] = pd.to_numeric(lt[col_qt], errors="coerce").fillna(0)
    agg = lt.groupby("cnes_id")[col_qt].sum().reset_index()
    agg.columns = ["cnes_id", "total_leitos"]
    return agg


def run(snapshot: str):
    est_path = _find_file(snapshot, "tbEstabelecimento")
    est = _read_any(est_path)

    c_cnes = _pick(est, ["CO_CNES", "CO_UNIDADE", "CNES", "CNES_ID"])
    if not c_cnes:
        raise ValueError("Coluna CNES não encontrada")
    # Nome de exibição: preferir nome fantasia (mais Google-like)
    c_nome = _pick(est, ["NO_FANTASIA", "NO_RAZAO_SOCIAL", "NOME_FANTASIA", "NOME"])
    c_tel = _pick(est, ["NU_TELEFONE", "TELEFONE", "NU_TELEFONE1"])
    c_lat = _pick(est, ["NU_LATITUDE", "LATITUDE", "LAT", "NU_LAT"])
    c_lon = _pick(est, ["NU_LONGITUDE", "LONGITUDE", "LON", "NU_LON"])
    c_tipo = _pick(est, ["NO_TIPO_UNIDADE", "TP_UNIDADE", "DS_TIPO_UNIDADE", "TP_ESTABELECIMENTO"])
    c_conat = _pick(est, ["CO_NATUREZA_JURIDICA", "NAT_JUR"])
    c_nonat = _pick(est, ["NO_NATUREZA", "NATUREZA_JURIDICA"])
    c_esft = _pick(est, ["ESFERA_ADMIN", "NO_ESFERA", "ESFERA"])
    c_sus1 = _pick(est, ["IND_SUS", "ATEND_SUS", "IND_ATEND_SUS"])
    c_sus2 = _pick(est, ["ATEND_SUS", "IND_SUS", "IND_ATEND_SUS"])
    c_cnpj = _pick(est, ["CNPJ", "NU_CNPJ"])
    c_log = _pick(est, ["NO_LOGRADOURO", "DS_LOGRADOURO", "LOGRADOURO", "ENDERECO"])
    c_num = _pick(est, ["NU_ENDERECO", "NUMERO", "NR_END"])
    c_bai = _pick(est, ["NO_BAIRRO", "BAIRRO"])
    c_mun = _pick(est, ["NO_MUNICIPIO", "MUNICIPIO"])
    c_uf = _pick(est, ["SG_UF", "UF"])
    c_cep = _pick(est, ["CO_CEP", "CEP"])

    df = pd.DataFrame()
    df["cnes_id"] = est[c_cnes].apply(_norm_cnes)
    df["nome"] = est[c_nome].astype(str).str.strip() if c_nome else ""
    df["telefone"] = est[c_tel].astype(str).str.strip() if c_tel else ""
    df["tipo"] = est[c_tipo].astype(str).str.strip() if c_tipo else ""
    df["esfera"] = [
        _derive_esfera_v2(
            est[c_conat].iloc[i] if c_conat else None,
            est[c_nonat].iloc[i] if c_nonat else None,
            est[c_esft].iloc[i] if c_esft else None,
        )
        for i in range(len(est))
    ]
    atende_sus_pairs = [
        _map_sus_v2(
            est[c_sus1].iloc[i] if c_sus1 else None,
            est[c_sus2].iloc[i] if c_sus2 else None,
        )
        for i in range(len(est))
    ]
    df["atende_sus_label"], df["atende_sus_bool"] = zip(*atende_sus_pairs)
    df["atende_sus"] = df["atende_sus_label"]
    df["cnpj"] = est[c_cnpj].astype(str).str.strip() if c_cnpj else ""
    df["lat"] = pd.to_numeric(est[c_lat], errors="coerce") if c_lat else np.nan
    df["lon"] = pd.to_numeric(est[c_lon], errors="coerce") if c_lon else np.nan

    log = est[c_log].astype(str).str.strip() if c_log else pd.Series("", index=est.index)
    num = est[c_num].astype(str).str.strip() if c_num else pd.Series("", index=est.index)
    num = num.replace("", "s/n").replace("nan", "s/n")
    bai = est[c_bai].astype(str).str.strip() if c_bai else pd.Series("", index=est.index)
    mun = est[c_mun].astype(str).str.strip() if c_mun else pd.Series("", index=est.index)
    uf = est[c_uf].astype(str).str.strip() if c_uf else pd.Series("", index=est.index)
    cep = est[c_cep].astype(str).str.strip() if c_cep else pd.Series("", index=est.index)
    cep_part = cep.fillna("").replace("nan", "").apply(lambda x: " • CEP " + x if x and str(x).strip() else "")
    df["endereco"] = (
        log.fillna("") + ", " + num.fillna("s/n") + " – " + bai.fillna("") + ", " + mun.fillna("") + "/" + uf.fillna("") + cep_part
    ).str.replace(r"\s+", " ", regex=True).str.strip(" ,–/")
    df["municipio"] = mun
    df["uf"] = uf
    # Fallback: nome com MUNICIPAL/ESTADUAL/FEDERAL → Público
    nome_upper = df["nome"].fillna("").astype(str).str.upper()
    mask_public_name = nome_upper.str.contains("MUNICIPAL", na=False) | nome_upper.str.contains("ESTADUAL", na=False) | nome_upper.str.contains("FEDERAL", na=False)
    df.loc[mask_public_name & (df["esfera"] == "Privado"), "esfera"] = "Público"
    # Badge SUS efetivo: Sim direto OU (Público e SUS desconhecido) → "Aceita SUS"
    df["sus_badge"] = np.where(
        (df["atende_sus_bool"] == True) | ((df["atende_sus_bool"].isna()) & (df["esfera"] == "Público")),
        "Aceita SUS",
        np.where(df["atende_sus_bool"] == False, "Não atende SUS", ""),
    )

    # Mapa cnes_id -> UF para backfill de UF vazia antes de salvar
    _uf_map = {}
    if c_uf:
        _est_uf = est.copy()
        _est_uf["_cnes_id"] = _est_uf[c_cnes].apply(_norm_cnes)
        _est_uf["_uf_val"] = _est_uf[c_uf].astype(str).str.strip()
        _est_uf.loc[_est_uf["_uf_val"].isin(["", "nan", "None"]), "_uf_val"] = np.nan
        _uf_map = _est_uf.drop_duplicates("_cnes_id").set_index("_cnes_id")["_uf_val"].to_dict()

    df["nome"] = df["nome"].fillna("").astype(str)
    df["tipo"] = df["tipo"].fillna("").astype(str)
    df["display_name"] = df["nome"].apply(_clean_name)

    EXCLUDE_KWS = _load_filters_from_config()

    try:
        leito_path = _find_file(snapshot, "tbLeito")
        leito = _read_any(leito_path)
        agg_obs = _detect_leitos(leito)
        agg_tot = _sum_total_leitos(leito)
        df = df.merge(agg_obs, how="left", on="cnes_id")
        df = df.merge(agg_tot, how="left", on="cnes_id")
        df["qtd_obsneo"] = pd.to_numeric(df.get("qtd_obsneo"), errors="coerce").fillna(0)
        df["total_leitos"] = pd.to_numeric(df.get("total_leitos"), errors="coerce").fillna(0)
        if "leitos_evidence" not in df.columns:
            df["leitos_evidence"] = [[] for _ in range(len(df))]
        df["leitos_evidence"] = df["leitos_evidence"].apply(lambda x: x if isinstance(x, list) else [])
    except Exception:
        df["qtd_obsneo"] = 0
        df["leitos_evidence"] = [[] for _ in range(len(df))]
        df["total_leitos"] = 0

    df["tem_internacao"] = df["total_leitos"] > 0

    try:
        cfg = json.loads((BASE_DIR / "config" / "cnes_codes.json").read_text(encoding="utf-8"))
        kw_list = [k.lower() for k in cfg.get("keywords_nome_fantasia", [])]
    except Exception:
        kw_list = ["maternidade", "hospital da mulher", "obstétrico", "hospital e maternidade", "materno infantil", "materno-infantil", "casa de parto"]

    def kw_hit(name: str) -> bool:
        t = (name or "").lower()
        return any(k in t for k in kw_list)

    incl = df["nome"].str.lower().apply(lambda x: _contains_any(x, INCLUDE_KWS)) | df["tipo"].str.lower().apply(lambda x: _contains_any(x, INCLUDE_KWS))
    excl = df["nome"].str.lower().apply(lambda x: _contains_any(x, EXCLUDE_KWS)) | df["tipo"].str.lower().apply(lambda x: _contains_any(x, EXCLUDE_KWS))
    matern_or_casa = df["nome"].apply(kw_hit) | df["tipo"].str.lower().str.contains("matern", na=False) | df["nome"].str.lower().str.contains("casa de parto", na=False)
    keep_final = incl & ~excl & (df["tem_internacao"] | matern_or_casa)
    df = df[keep_final].copy()

    df["has_maternity"] = df["qtd_obsneo"] > 0
    serv_cnes = _load_servclass_cnes(snapshot)
    if serv_cnes:
        df.loc[df["cnes_id"].isin(serv_cnes), "has_maternity"] = True
    hab_cnes, _hab_path = _load_habilitacao_cnes(snapshot)
    if hab_cnes:
        hit = df["cnes_id"].isin(hab_cnes)
        df.loc[hit, "has_maternity"] = True
    df["is_probable"] = (~df["has_maternity"]) & (df["nome"].apply(kw_hit) | df["tipo"].str.lower().str.contains("matern", na=False))
    df["score"] = 0.0
    df.loc[df["has_maternity"], "score"] += 0.6
    df.loc[df["tipo"].str.lower().str.contains("matern", na=False), "score"] += 0.3
    df.loc[df["nome"].apply(kw_hit), "score"] += 0.2

    df["_serv_sinal_forte"] = df["cnes_id"].isin(serv_cnes)
    df["_hab_sinal_forte"] = df["cnes_id"].isin(hab_cnes) if hab_cnes else False

    def build_evidence(row):
        ev = []
        if isinstance(row.get("leitos_evidence"), list) and row["leitos_evidence"]:
            ev.extend(row["leitos_evidence"])
        if row.get("_serv_sinal_forte"):
            ev.append({"type": "servico", "code": "obst_urg", "source": "rlEstabServClass"})
        if row.get("_hab_sinal_forte"):
            ev.append({"type": "habilitacao", "code": "obst_neonat_cpn", "source": "rlEstabHabilitacao"})
        if "matern" in (row.get("tipo") or "").lower():
            ev.append({"type": "tipo", "code": "matern", "source": "tipo_estabelecimento"})
        if kw_hit(row.get("nome") or ""):
            ev.append({"type": "keyword", "code": "nome_fantasia", "source": "keyword"})
        return ev

    df["evidence"] = df.apply(build_evidence, axis=1)
    df.drop(columns=["_serv_sinal_forte", "_hab_sinal_forte"], inplace=True, errors="ignore")

    # Backfill UF vazia a partir do tbEstabelecimento original (melhora relatórios por UF)
    _missing_uf = df["uf"].isna() | (df["uf"].astype(str).str.strip().isin(["", "nan"]))
    if _missing_uf.any():
        df.loc[_missing_uf, "uf"] = df.loc[_missing_uf, "cnes_id"].map(_uf_map)

    disp_e164 = [format_br_phone(str(x)) for x in df["telefone"].fillna("").astype(str)]
    df["telefone_formatado"] = [d[0] for d in disp_e164]
    df["phone_e164"] = [d[1] for d in disp_e164]

    out = OUT / "hospitals_ready.parquet"
    cols_out = ["cnes_id", "nome", "display_name", "esfera", "atende_sus", "atende_sus_label", "sus_badge",
                "has_maternity", "is_probable", "score", "evidence",
                "telefone", "telefone_formatado", "phone_e164", "endereco", "lat", "lon", "municipio", "uf", "cnpj"]
    df_out = df[[c for c in cols_out if c in df.columns]].copy()
    df_out["evidence"] = df_out["evidence"].apply(lambda x: json.dumps(x) if isinstance(x, list) else x)
    df_out.to_parquet(out, index=False)
    print(f"[OK] salvo {out} ({len(df_out)} linhas)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", default="202512")
    args = ap.parse_args()
    run(args.snapshot)
