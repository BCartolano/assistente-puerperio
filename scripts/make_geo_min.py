#!/usr/bin/env python3
"""Gera Parquet mínimo e bem comprimido a partir de hospitals_geo.parquet."""
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

BASE = Path(__file__).resolve().parent.parent
GEO = BASE / "data" / "geo"

ESSENTIAL = [
    "cnes_id", "nome", "display_name", "esfera", "atende_sus", "atende_sus_label", "sus_badge",
    "has_maternity", "is_probable", "score",
    "telefone", "telefone_formatado", "phone_e164",
    "endereco", "lat", "lon", "municipio", "uf",
]


def main() -> int:
    src = GEO / "hospitals_geo.parquet"
    if not src.exists():
        raise SystemExit(f"Fonte não encontrada: {src}")
    df = pd.read_parquet(src)
    cols = [c for c in ESSENTIAL if c in df.columns]
    df = df[cols].copy()

    # dtypes mais leves
    for c in ("has_maternity", "is_probable"):
        if c in df.columns:
            df[c] = df[c].fillna(False).astype("bool")
    if "score" in df.columns:
        df["score"] = pd.to_numeric(df["score"], errors="coerce").astype("float32")
    for c in ("uf", "esfera", "atende_sus"):
        if c in df.columns:
            df[c] = df[c].fillna("Desconhecido").astype("category")

    # grava com zstd e dict encoding
    table = pa.Table.from_pandas(df, preserve_index=False)
    out = GEO / "hospitals_geo.min.parquet"
    pq.write_table(
        table, out,
        compression="zstd", compression_level=9,
        use_dictionary=True,
    )
    print(f"[OK] salvo {out} ({len(df)} linhas)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
