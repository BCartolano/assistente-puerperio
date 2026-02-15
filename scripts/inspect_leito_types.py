#!/usr/bin/env python3
"""
Inspeciona tbLeito{snapshot} e sugere códigos/descrições de leitos obstétricos/neonatais.
Uso:
  python scripts/inspect_leito_types.py --snapshot 202512
Saída: imprime TOP valores de texto e código; gera config/leito_codes_suggestion.json
       com arrays leito_codes_obst e leito_codes_neonatal para colar em config/cnes_codes.json.
"""
import argparse
import json
import re
import sys
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA = BASE_DIR / "data"


def find_file(snapshot: str, base: str) -> Path:
    for p in [
        DATA / f"{base}{snapshot}.parquet",
        DATA / f"{base}{snapshot}.csv",
        BASE_DIR / "data" / "raw" / snapshot / f"{base}{snapshot}.parquet",
        BASE_DIR / "data" / "raw" / snapshot / f"{base}{snapshot}.csv",
    ]:
        if p.exists():
            return p
    raise FileNotFoundError(f"Arquivo não encontrado: {base}{snapshot}.csv|parquet")


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
    ap = argparse.ArgumentParser(description="Inspeciona tbLeito e sugere leito_codes_obst/neonatal")
    ap.add_argument("--snapshot", default="202512", help="Snapshot CNES (ex: 202512)")
    args = ap.parse_args()

    path = find_file(args.snapshot, "tbLeito")
    df = read_any(path)

    c_cnes = pick(df, ["CO_CNES", "CO_UNIDADE", "CNES", "CNES_ID"])
    c_code = pick(df, ["CO_TIPO_LEITO", "TP_LEITO", "COD_TIPO_LEITO"])
    c_text = pick(df, ["DS_TIPO_LEITO", "NO_TIPO_LEITO", "DS_LEITO", "TP_LEITO_DESC"])
    c_qt = pick(df, ["QT_LEITOS", "QT_EXIST", "QT_EXISTENTE", "QT_LEITO", "QT_SUS", "QT_TOTAL"])

    print("[INFO] colunas detectadas:")
    print("  CNES :", c_cnes)
    if not c_cnes:
        print("  [AVISO] Sem coluna CNES/CO_CNES: este arquivo pode ser só dicionário de tipos. Para Confirmados > 0, use tbLeito com estabelecimento (ex.: CO_CNES + tipo + quantidade).")
    print("  COD  :", c_code)
    print("  TEXTO:", c_text)
    print("  QT   :", c_qt)
    print("\n[AMOSTRA]")
    print(df.head(5).to_string(index=False))

    if c_text:
        print("\n[TOP descrições]")
        print(df[c_text].value_counts().head(30).to_string())
    if c_code:
        print("\n[TOP códigos]")
        print(df[c_code].value_counts().head(30).to_string())

    patt = re.compile(r"(obst|neonat|aloj|uti\s*neo|ucin)", re.I)
    sug_codes_obst, sug_codes_neo = set(), set()

    if c_text and c_code:
        sub = df[[c_code, c_text]].dropna().drop_duplicates()
        for _, row in sub.iterrows():
            code = str(row[c_code])
            text = str(row[c_text])
            if re.search(patt, text):
                if "neonat" in text.lower() or "uti" in text.lower() or "ucin" in text.lower():
                    sug_codes_neo.add(code)
                else:
                    sug_codes_obst.add(code)

    suggestion = {
        "leito_codes_obst": sorted(list(sug_codes_obst)),
        "leito_codes_neonatal": sorted(list(sug_codes_neo)),
        "notes": "Cole os arrays em config/cnes_codes.json se fizer sentido; revise os TOP valores impressos acima.",
    }
    (BASE_DIR / "config").mkdir(exist_ok=True, parents=True)
    out = BASE_DIR / "config" / "leito_codes_suggestion.json"
    out.write_text(json.dumps(suggestion, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[OK] Sugestão salva em {out}")
    print(json.dumps(suggestion, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
