#!/usr/bin/env python3
"""
QA automático: gera 3 CSVs em reports/ para revisar casos problemáticos.
1) Públicos por nome mas esfera não-Público (possível Público→Privado perdido)
2) Prováveis com palavras ambulatoriais (devem sair pelo filtro)
3) Nome indica maternidade mas não está classificado (has_maternity/is_probable)
Uso: python scripts/qa_mismatches.py
Ou importar run_qa_mismatches() para retornar dict e integrar no orquestrador.
"""
from pathlib import Path
import re
import sys

import pandas as pd

BASE = Path(__file__).resolve().parent.parent
GEO_DIR = BASE / "data" / "geo"
OUT = BASE / "reports"
OUT.mkdir(parents=True, exist_ok=True)


def _geo_path():
    """Prefere hospitals_geo.min.parquet; fallback para hospitals_geo.parquet."""
    p_min = GEO_DIR / "hospitals_geo.min.parquet"
    p_full = GEO_DIR / "hospitals_geo.parquet"
    if p_min.exists():
        return p_min
    if p_full.exists():
        return p_full
    return None


def run_qa_mismatches(
    geo_path: Path | None = None,
    out_dir: Path | None = None,
    release_uf: str | None = None,
) -> dict:
    """
    Lê parquet geo, gera os 3 CSVs em out_dir e retorna dict com contagens e caminhos.
    Útil para integrar no orquestrador (qa_hints no run_summary.json).
    release_uf: se informado, calcula qa_publico_vs_privado_pct_uf para gate (>0.5% = fail).
    """
    path = geo_path or _geo_path()
    out = out_dir or OUT
    out.mkdir(parents=True, exist_ok=True)

    if not path or not path.exists():
        return {
            "error": f"Parquet não encontrado em {GEO_DIR}",
            "qa_publico_vs_privado": 0,
            "qa_ambulatorial_vazando": 0,
            "qa_maternidade_nao_marcada": 0,
            "qa_reports_dir": str(out),
        }

    df = pd.read_parquet(path)
    uf_col = "uf" if "uf" in df.columns else ("state" if "state" in df.columns else None)
    if uf_col:
        df["_uf_norm"] = df[uf_col].fillna("").astype(str).str.strip().str.upper().str[:2]
    else:
        df["_uf_norm"] = ""

    # Campos seguros (colunas podem não existir em parquets antigos)
    df["nome_lc"] = df["nome"].fillna("").astype(str).str.lower()
    if "esfera" in df.columns:
        df["esfera"] = df["esfera"].fillna("").astype(str)
    else:
        df["esfera"] = ""
    if "sus_badge" in df.columns:
        df["sus_badge"] = df["sus_badge"].fillna("").astype(str)
    else:
        df["sus_badge"] = ""
    if "atende_sus_label" in df.columns:
        df["atende_sus_label"] = df["atende_sus_label"].fillna("").astype(str)
    else:
        df["atende_sus_label"] = ""
    if "is_probable" in df.columns:
        df["is_probable"] = df["is_probable"].fillna(False).astype(bool)
    else:
        df["is_probable"] = False
    if "has_maternity" in df.columns:
        df["has_maternity"] = df["has_maternity"].fillna(False).astype(bool)
    else:
        df["has_maternity"] = False

    # 1) Públicos por nome, mas esfera não-Público
    patt_pub = re.compile(r"\b(municip|estad|federal)\b", re.I)
    pub_name = df["nome_lc"].str.contains(patt_pub, na=False)
    bad_pub = df.loc[pub_name & (df["esfera"] != "Público")].copy()
    bad_pub.to_csv(out / "qa_publico_vs_privado.csv", index=False, encoding="utf-8")

    # 2) Prováveis com cara de ambulatorial (devem sair pelo filtro)
    amb_kw = re.compile(
        r"psicolog|psico\b|fono|fonoaudiol|fisioter|terapia ocup|nutri|consult[óo]rio|optica|oficina ortop",
        re.I,
    )
    amb_prob = df.loc[(df["is_probable"]) & df["nome_lc"].str.contains(amb_kw, na=False)].copy()
    amb_prob.to_csv(out / "qa_ambulatorial_vazando.csv", index=False, encoding="utf-8")

    # 3) Nome indica maternidade, mas não está classificado
    mat_kw = re.compile(r"\bmaternidade\b|hospital e maternidade|casa de parto", re.I)
    suspeitos = df.loc[
        ~df["has_maternity"] & ~df["is_probable"] & df["nome_lc"].str.contains(mat_kw, na=False)
    ].copy()
    suspeitos.to_csv(out / "qa_maternidade_nao_marcada.csv", index=False, encoding="utf-8")

    out_hints = {
        "qa_publico_vs_privado": len(bad_pub),
        "qa_ambulatorial_vazando": len(amb_prob),
        "qa_maternidade_nao_marcada": len(suspeitos),
        "qa_reports_dir": str(out),
        "qa_files": [
            str(out / "qa_publico_vs_privado.csv"),
            str(out / "qa_ambulatorial_vazando.csv"),
            str(out / "qa_maternidade_nao_marcada.csv"),
        ],
    }
    # Gate por UF de release: fail se >0.5% na UF
    if release_uf and release_uf.strip():
        uf_val = release_uf.strip().upper()[:2]
        df_uf = df.loc[df["_uf_norm"] == uf_val]
        total_uf = len(df_uf)
        bad_in_uf = int((bad_pub["_uf_norm"] == uf_val).sum())
        pct_uf = (bad_in_uf / total_uf) if total_uf else 0.0
        out_hints["qa_publico_vs_privado_uf"] = bad_in_uf
        out_hints["qa_publico_vs_privado_total_uf"] = total_uf
        out_hints["qa_publico_vs_privado_pct_uf"] = round(pct_uf, 4)
    return out_hints


def main() -> int:
    hints = run_qa_mismatches()
    if "error" in hints:
        print(hints["error"], file=sys.stderr)
        return 1
    print("[OK] Salvos:")
    print(" -", OUT / "qa_publico_vs_privado.csv", f"({hints['qa_publico_vs_privado']})")
    print(" -", OUT / "qa_ambulatorial_vazando.csv", f"({hints['qa_ambulatorial_vazando']})")
    print(" -", OUT / "qa_maternidade_nao_marcada.csv", f"({hints['qa_maternidade_nao_marcada']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
