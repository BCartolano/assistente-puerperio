#!/usr/bin/env python3
"""
Confere interseção de CNES entre hospitals_ready.parquet e rlEstabServClass<SNAPSHOT>.csv
Uso:
  python scripts/check_cnes_intersection.py --snapshot 202512
"""
import argparse
import re
import sys
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"
GEO = DATA / "geo"


def digits(s) -> str:
    return re.sub(r"\D", "", str(s or ""))


def norm_cnes(s) -> str:
    t = digits(s)
    if not t:
        return ""
    return t[:7].zfill(7) if len(t) >= 7 else t.zfill(7)


def read_any(p: Path) -> pd.DataFrame:
    if p.suffix.lower() == ".parquet":
        return pd.read_parquet(p)
    try:
        return pd.read_csv(p, sep=";", dtype=str, low_memory=False, encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv(p, sep=";", dtype=str, low_memory=False, encoding="ISO-8859-1", on_bad_lines="skip")
    except Exception:
        return pd.read_csv(p, sep=";", dtype=str, low_memory=False, encoding="ISO-8859-1", on_bad_lines="skip")


def find_serv(snapshot: str) -> Path | None:
    for p in [
        DATA / f"rlEstabServClass{snapshot}.csv",
        DATA / f"rlEstabServClass{snapshot}.parquet",
        DATA / "raw" / snapshot / f"rlEstabServClass{snapshot}.csv",
        DATA / "raw" / snapshot / f"rlEstabServClass{snapshot}.parquet",
        BASE / f"BASE_DE_DADOS_CNES_{snapshot}" / f"rlEstabServClass{snapshot}.csv",
        BASE / "BASE_DE_DADOS_CNES_202512" / f"rlEstabServClass{snapshot}.csv",
    ]:
        if p.exists():
            return p
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Interseção CNES: hospitals_ready x rlEstabServClass")
    ap.add_argument("--snapshot", default="202512")
    args = ap.parse_args()

    ready = GEO / "hospitals_ready.parquet"
    if not ready.exists():
        print("[ERRO] gere o prepare_geo_v2 primeiro.", file=sys.stderr)
        return 2
    df = pd.read_parquet(ready)
    left = set(df["cnes_id"].astype(str).map(norm_cnes))
    left = set(x for x in left if x and len(x) == 7)

    sp = find_serv(args.snapshot)
    if not sp:
        print("[ERRO] rlEstabServClass não encontrado.", file=sys.stderr)
        return 3
    sv = read_any(sp)
    c_cnes = None
    for c in ["CO_UNIDADE", "CO_CNES", "CNES", "CNES_ID"]:
        if c in sv.columns:
            c_cnes = c
            break
    if not c_cnes:
        print("[ERRO] coluna CNES não encontrada em servclass.", file=sys.stderr)
        return 4
    right = set(sv[c_cnes].astype(str).map(norm_cnes))
    right = set(x for x in right if x and len(x) == 7)

    inter = left & right
    ratio = len(inter) / max(1, len(left))
    print(f"[INFO] establishments={len(left)} • servclass={len(right)} • intersec={len(inter)} • ratio={ratio:.1%}")
    if inter:
        sample = list(sorted(inter))[:10]
        print("[OK] exemplo de CNES em comum:", sample)
    else:
        print("[AVISO] Interseção 0 — tbEstabelecimento e rlEstabServClass podem ser de snapshots/fontes distintas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
