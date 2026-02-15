#!/usr/bin/env python3
"""
Deriva códigos de leito obstétrico/neonatal a partir dos 'prováveis' (nome fantasia/keywords).
Uso:
  python scripts/derive_leito_codes_from_probables.py --snapshot 202512 --min-cnes 10 --min-ratio 0.2
Saída:
  config/leito_codes_candidate.json com arrays 'leito_codes_obst' e 'leito_codes_neonatal' (candidatos)
"""
import argparse
import json
import re
import sys
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"


def find_file(snapshot: str, base: str) -> Path:
    for p in [
        DATA / f"{base}{snapshot}.parquet",
        DATA / f"{base}{snapshot}.csv",
        DATA / "raw" / snapshot / f"{base}{snapshot}.parquet",
        DATA / "raw" / snapshot / f"{base}{snapshot}.csv",
    ]:
        if p.exists():
            return p
    raise FileNotFoundError(f"Não achei {base}{snapshot}.csv|parquet em data/ ou data/raw/{snapshot}/")


def read_any(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    try:
        return pd.read_csv(path, sep=";", dtype=str, low_memory=False)
    except Exception:
        return pd.read_csv(path, sep=",", dtype=str, low_memory=False)


def pick(df: pd.DataFrame, names: list) -> str | None:
    cols = {str(c).lower(): c for c in df.columns}
    for n in names:
        if n in df.columns:
            return n
        if str(n).lower() in cols:
            return cols[str(n).lower()]
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", default="202512")
    ap.add_argument("--min-cnes", type=int, default=10, help="mínimo de estabelecimentos distintos para considerar o código")
    ap.add_argument("--min-ratio", type=float, default=0.2, help="código aparece em pelo menos essa fração dos prováveis que têm leitos")
    args = ap.parse_args()

    ready = DATA / "geo" / "hospitals_ready.parquet"
    if not ready.exists():
        print("[ERRO] data/geo/hospitals_ready.parquet não encontrado. Rode prepare_geo_v2 primeiro.", file=sys.stderr)
        return 1

    dfh = pd.read_parquet(ready)
    if "is_probable" not in dfh.columns:
        print("[INFO] Coluna is_probable não encontrada em hospitals_ready; nada a derivar.", file=sys.stderr)
        return 0

    prob = dfh[dfh["is_probable"] == True].copy()
    if prob.empty:
        print("[INFO] não há 'prováveis' no dataset; nada a derivar.", file=sys.stderr)
        return 0

    lp = find_file(args.snapshot, "tbLeito")
    dl = read_any(lp)

    c_cnes = pick(dl, ["CO_CNES", "CO_UNIDADE", "CNES", "CNES_ID"])
    c_code = pick(dl, ["CO_TIPO_LEITO", "TP_LEITO", "COD_TIPO_LEITO"])
    c_text = pick(dl, ["DS_TIPO_LEITO", "NO_TIPO_LEITO", "DS_LEITO", "TP_LEITO_DESC"])
    c_qt = pick(dl, ["QT_LEITOS", "QT_EXIST", "QT_EXISTENTE", "QT_LEITO", "QT_SUS", "QT_TOTAL"])
    if not c_cnes or not c_code or not c_qt:
        print("[ERRO] tbLeito sem colunas essenciais (CNES/código/quantidade).", file=sys.stderr)
        return 1

    dl[c_qt] = pd.to_numeric(dl[c_qt], errors="coerce").fillna(0)

    prob_ids = set(prob["cnes_id"].astype(str))
    dl = dl[dl[c_cnes].astype(str).isin(prob_ids) & (dl[c_qt] > 0)].copy()

    by_code = dl.groupby(c_code).agg(
        cnes_count=(c_cnes, lambda s: len(set(s.astype(str)))),
        total_leitos=(c_qt, "sum"),
    ).reset_index().rename(columns={c_code: "code"})

    total_prob_with_leito = len(set(dl[c_cnes].astype(str)))
    by_code["cnes_ratio"] = by_code["cnes_count"] / max(total_prob_with_leito, 1)

    cand = by_code[(by_code["cnes_count"] >= args.min_cnes) & (by_code["cnes_ratio"] >= args.min_ratio)].copy()

    obst, neo = [], []
    if c_text and c_text in dl.columns:
        example = dl[[c_code, c_text]].dropna().drop_duplicates().groupby(c_code).first().reset_index()
        ex_map = dict(zip(example[c_code].astype(str), example[c_text].astype(str)))
        for _, r in cand.iterrows():
            code = str(r["code"])
            text = (ex_map.get(code) or "").lower()
            if any(k in text for k in ["neonat", "uti neo", "ucin"]):
                neo.append(code)
            elif any(k in text for k in ["obst", "aloj"]):
                obst.append(code)
            else:
                obst.append(code)
    else:
        obst = cand["code"].astype(str).tolist()

    out = {
        "summary": {
            "total_probables": int(len(prob_ids)),
            "probables_with_leito": int(total_prob_with_leito),
            "min_cnes": args.min_cnes,
            "min_ratio": args.min_ratio,
        },
        "leito_codes_obst": sorted(list(set(obst))),
        "leito_codes_neonatal": sorted(list(set(neo))),
    }
    (BASE / "config").mkdir(parents=True, exist_ok=True)
    p = BASE / "config" / "leito_codes_candidate.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("[OK] candidatos salvos em", p)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
