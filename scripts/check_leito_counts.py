#!/usr/bin/env python3
"""
Conta leitos obstétricos/neonatais por CNES e por UF a partir do CSV unificado (tbLeito<snapshot>.csv).
- Usa os códigos de config/cnes_codes.json (fallback: obst={"4"}, neonatal={"2","3"})
- Considera QT_EXIST > 0 (ajustável por --min-qt)
- Mapeia UF via:
  1) data/geo/hospitals_ready.parquet (se existir)
  2) tbEstabelecimento<snapshot>.csv (se existir)
Saídas:
  - reports/leito_counts_summary.csv
  - reports/leito_counts_by_uf.csv
  - (opcional) reports/leito_counts_cnes.csv (com --export-cnes)
Uso:
  python scripts/check_leito_counts.py --snapshot 202512
  python scripts/check_leito_counts.py --snapshot 202512 --export-cnes
"""
import argparse
import json
import re
import sys
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"
RAW = DATA / "raw"
OUT = BASE / "reports"
OUT.mkdir(parents=True, exist_ok=True)


def norm_digits(s: str) -> str:
    return re.sub(r"\D", "", str(s or ""))


def norm_cnes(v) -> str:
    d = norm_digits(v)
    if len(d) >= 7:
        d = d[:7]
    return d.zfill(7) if d else ""


def norm_code(v) -> str:
    s = norm_digits(v)
    return str(int(s)) if s else ""


def pick(df: pd.DataFrame, names: list[str]) -> str | None:
    lower = {str(c).lower(): c for c in df.columns}
    for n in names:
        if n in df.columns:
            return n
        if n.lower() in lower:
            return lower[n.lower()]
    return None


def read_csv_any(p: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(p, sep=";", dtype=str, low_memory=False, encoding="utf-8")
    except Exception:
        try:
            return pd.read_csv(p, sep=",", dtype=str, low_memory=False, encoding="utf-8")
        except Exception:
            try:
                return pd.read_csv(p, sep=";", dtype=str, low_memory=False, encoding="latin-1")
            except Exception:
                return pd.read_csv(p, sep=",", dtype=str, low_memory=False, encoding="latin-1")


def find_leito_csv(snapshot: str) -> Path | None:
    candidates = [
        DATA / f"tbLeito{snapshot}.csv",
        DATA / f"rlEstabLeito{snapshot}.csv",
        RAW / snapshot / f"tbLeito{snapshot}.csv",
        RAW / snapshot / f"rlEstabLeito{snapshot}.csv",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def load_codes_from_config() -> tuple[set[str], set[str]]:
    cfg_path = BASE / "config" / "cnes_codes.json"
    try:
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        obst = {norm_code(x) for x in cfg.get("leito_codes_obst", []) if str(x).strip() != ""}
        neo = {norm_code(x) for x in cfg.get("leito_codes_neonatal", []) if str(x).strip() != ""}
    except Exception:
        obst, neo = set(), set()
    if not obst:
        obst = {"4"}
    if not neo:
        neo = {"2", "3"}
    obst |= {x.zfill(2) for x in obst}
    neo |= {x.zfill(2) for x in neo}
    return obst, neo


def load_uf_map(snapshot: str) -> dict[str, str]:
    ready = DATA / "geo" / "hospitals_ready.parquet"
    if ready.exists():
        df = pd.read_parquet(ready)
        if "cnes_id" in df.columns and "uf" in df.columns:
            c = df[["cnes_id", "uf"]].dropna()
            c["cnes_id"] = c["cnes_id"].map(norm_cnes)
            m = dict(zip(c["cnes_id"], c["uf"].astype(str)))
            if m:
                return m
    for p in [
        DATA / f"tbEstabelecimento{snapshot}.csv",
        RAW / snapshot / f"tbEstabelecimento{snapshot}.csv",
        BASE / f"BASE_DE_DADOS_CNES_{snapshot}" / f"tbEstabelecimento{snapshot}.csv",
    ]:
        if p.exists():
            df = read_csv_any(p)
            col_cnes = pick(df, ["CO_CNES", "CO_UNIDADE", "CNES", "CNES_ID"])
            col_uf = pick(df, ["SG_UF", "UF"])
            if col_cnes and col_uf:
                c = df[[col_cnes, col_uf]].dropna()
                c[col_cnes] = c[col_cnes].map(norm_cnes)
                m = dict(zip(c[col_cnes], c[col_uf].astype(str)))
                if m:
                    return m
    return {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", default="202512")
    ap.add_argument("--min-qt", type=int, default=1, help="mínimo de leitos para considerar (default 1)")
    ap.add_argument("--export-cnes", action="store_true", help="exportar planilha por CNES")
    args = ap.parse_args()

    leito_p = find_leito_csv(args.snapshot)
    if not leito_p:
        print(f"[ERRO] não achei CSV de leitos para snapshot {args.snapshot}. Coloque data/tbLeito{args.snapshot}.csv e rode de novo.")
        return 2

    df = read_csv_any(leito_p)
    col_cnes = pick(df, ["CO_CNES", "CO_UNIDADE", "CNES", "CNES_ID"])
    col_tipo = pick(df, ["CO_TIPO_LEITO", "TP_LEITO", "COD_TIPO_LEITO", "COD_LEITO"])
    col_qt = pick(df, ["QT_EXIST", "QT_LEITOS", "QT_TOTAL", "TOTAL_LEITOS"])
    if not (col_cnes and col_tipo and col_qt):
        print(f"[ERRO] colunas essenciais ausentes em {leito_p.name}. Precisa CNES + TIPO + QT_.")
        return 3

    slim = pd.DataFrame({
        "cnes_id": df[col_cnes].map(norm_cnes),
        "code": df[col_tipo].map(lambda x: norm_code(x) or str(x).strip()),
        "qt": pd.to_numeric(df[col_qt], errors="coerce").fillna(0).astype(int),
    })
    slim = slim[slim["cnes_id"] != ""].copy()

    obst, neo = load_codes_from_config()
    slim["is_obst"] = slim["code"].astype(str).isin(obst)
    slim["is_neo"] = slim["code"].astype(str).isin(neo)

    # Agrega por CNES: qt_obst = soma de qt onde is_obst; qt_neo onde is_neo; qt_total
    qt_total = slim.groupby("cnes_id")["qt"].sum()
    qt_obst = slim.loc[slim["is_obst"]].groupby("cnes_id")["qt"].sum()
    qt_neo = slim.loc[slim["is_neo"]].groupby("cnes_id")["qt"].sum()
    agg = qt_total.to_frame("qt_total")
    agg = agg.join(qt_obst.to_frame("qt_obst"), how="left").join(qt_neo.to_frame("qt_neo"), how="left")
    agg = agg.fillna(0).astype(int).reset_index()
    agg["has_obst"] = agg["qt_obst"] >= args.min_qt
    agg["has_neo"] = agg["qt_neo"] >= args.min_qt
    agg["has_any"] = (agg["qt_obst"] + agg["qt_neo"]) >= args.min_qt

    uf_map = load_uf_map(args.snapshot)
    agg["uf"] = agg["cnes_id"].map(uf_map).fillna("??")

    tot_cnes = len(agg)
    n_obst = int(agg["has_obst"].sum())
    n_neo = int(agg["has_neo"].sum())
    n_any = int(agg["has_any"].sum())

    print(f"[OK] {leito_p.name}: CNES distintos={tot_cnes} • com obst={n_obst} • com neo={n_neo} • com obst/neo={n_any}")

    by_uf = agg.groupby("uf").agg(
        cnes_total=("cnes_id", "nunique"),
        cnes_com_leito=("has_any", "sum"),
        com_obst=("has_obst", "sum"),
        com_neo=("has_neo", "sum"),
    ).reset_index().sort_values("cnes_com_leito", ascending=False)

    pd.DataFrame([{
        "snapshot": args.snapshot,
        "cnes_distintos": tot_cnes,
        "cnes_com_obst": n_obst,
        "cnes_com_neo": n_neo,
        "cnes_com_obst_ou_neo": n_any,
        "min_qt": args.min_qt,
    }]).to_csv(OUT / "leito_counts_summary.csv", index=False, encoding="utf-8")
    by_uf.to_csv(OUT / "leito_counts_by_uf.csv", index=False, encoding="utf-8")

    if args.export_cnes:
        cols = ["cnes_id", "uf", "qt_obst", "qt_neo", "qt_total", "has_obst", "has_neo", "has_any"]
        agg[cols].to_csv(OUT / "leito_counts_cnes.csv", index=False, encoding="utf-8")

    print("\nTop UFs por CNES com leito obst/neo:")
    print(by_uf.head(10).to_string(index=False))

    return 0


if __name__ == "__main__":
    sys.exit(main())
