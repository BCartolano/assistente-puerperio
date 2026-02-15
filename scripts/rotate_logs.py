#!/usr/bin/env python3
"""
Rota logs/search_events.jsonl quando ultrapassar --max-mb (default 10 MB).
Uso: python scripts/rotate_logs.py --max-mb 10
"""
import argparse
import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
LOG = BASE_DIR / "logs" / "search_events.jsonl"


def main() -> int:
    ap = argparse.ArgumentParser(description="Rotaciona search_events.jsonl ao ultrapassar tamanho")
    ap.add_argument("--max-mb", type=int, default=10, help="Tamanho máximo em MB antes de rotacionar")
    args = ap.parse_args()

    if not LOG.exists():
        print("[INFO] Log não existe; nada a fazer.")
        return 0

    size_mb = LOG.stat().st_size / (1024 * 1024)
    if size_mb <= args.max_mb:
        print(f"[OK] Tamanho atual {size_mb:.2f} MB <= {args.max_mb} MB")
        return 0

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = LOG.with_name(f"search_events-{ts}.jsonl")
    LOG.rename(dest)
    LOG.touch()
    print(f"[OK] Rotacionado para {dest.name}; novo search_events.jsonl criado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
