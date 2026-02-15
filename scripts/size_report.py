#!/usr/bin/env python3
"""Relatório de tamanho por diretório/arquivo na raiz do projeto."""
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent.parent
SKIP = {'.git', '__pycache__', 'node_modules', '.venv', 'logs', 'reports', '.pytest_cache'}


def dir_size(p: Path) -> int:
    total = 0
    for dp, _, files in os.walk(p):
        d = Path(dp)
        if any(part in SKIP for part in d.parts):
            continue
        for f in files:
            try:
                total += (d / f).stat().st_size
            except OSError:
                pass
    return total


def main() -> None:
    sizes = []
    for p in ROOT.iterdir():
        if p.name in SKIP:
            continue
        if p.is_dir():
            sizes.append((p, dir_size(p)))
        else:
            try:
                sizes.append((p, p.stat().st_size))
            except OSError:
                pass
    sizes.sort(key=lambda x: x[1], reverse=True)
    print("Top diretórios/arquivos por tamanho:")
    for p, s in sizes[:20]:
        print(f"{s / 1024 / 1024:8.1f} MB  {p}")


if __name__ == "__main__":
    main()
