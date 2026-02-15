#!/usr/bin/env python3
"""
Limpeza segura do workspace: remove dumps, raw, reports, logs e caches.
Dry-run por padrão. Use --no-dry-run para executar.
Uso:
  python scripts/clean_workspace.py              # simulado
  python scripts/clean_workspace.py --no-dry-run # executar
"""
import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGETS = [
    "BASE_DE_DADOS_CNES_*",
    "data/raw",
    "data/*.dbc",
    "data/*.dbf",
    "data/*.db",
    "data/*.sqlite",
    "data/*202*.csv",
    "reports",
    "logs",
    "__pycache__",
    ".pytest_cache",
    ".venv",
    "node_modules",
]
PROTECT = [
    "data/geo/hospitals_geo.parquet",
    "data/geo/hospitals_geo.min.parquet",
    "config/cnes_codes.json",
    "config/scoring.yaml",
]


def globmany() -> list:
    found = []
    for pat in TARGETS:
        found.extend(ROOT.glob(pat))
    prot = {(ROOT / p).resolve() for p in PROTECT}
    out = []
    for p in found:
        rp = p.resolve()
        if any(str(rp).startswith(str(pp)) for pp in prot):
            continue
        out.append(p)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Limpeza segura do workspace (dry-run por padrão)")
    ap.add_argument("--no-dry-run", action="store_true", help="Executar remoção de fato")
    args = ap.parse_args()
    dry_run = not args.no_dry_run

    to_del = globmany()
    print("[INFO] itens a remover:")
    for p in to_del:
        print(" -", p)
    if dry_run:
        print("\n[DRY-RUN] nada foi apagado. Rode com --no-dry-run para executar.")
        return 0
    for p in to_del:
        try:
            if p.is_dir():
                shutil.rmtree(p, ignore_errors=True)
            else:
                p.unlink(missing_ok=True)
            print("[OK] removido", p)
        except Exception as e:
            print("[ERRO]", p, e)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
