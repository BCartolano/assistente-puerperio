#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI de status/warm/clear do cache de overrides do CNES (sem reiniciar o app).
Uso:
  python scripts/overrides_cache.py status
  python scripts/overrides_cache.py warm [--snapshot YYYYMM]
  python scripts/overrides_cache.py clear
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Garante raiz do projeto no path
BASE = Path(__file__).resolve().parent.parent
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))

from backend.startup.cnes_overrides import (
    boot,
    ensure_boot,
    get_overrides_count,
    get_snapshot_used,
)

CACHE_DIR = BASE / "data" / "cache"


def size_fmt(n: float) -> str:
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} TB"


def list_cache() -> list[Path]:
    if not CACHE_DIR.exists():
        return []
    return sorted(CACHE_DIR.glob("cnes_overrides_*.pkl"))


def main() -> int:
    ap = argparse.ArgumentParser(description="Status/warm/clear do cache de overrides CNES")
    ap.add_argument("action", choices=["status", "warm", "clear"])
    ap.add_argument("--snapshot", help="SNAPSHOT YYYYMM (ex.: 202512)")
    args = ap.parse_args()

    if args.action == "status":
        ensure_boot()
        print(
            json.dumps(
                {
                    "snapshot": get_snapshot_used(),
                    "count": get_overrides_count(),
                    "cache_files": [p.name for p in list_cache()],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if args.action == "warm":
        boot(args.snapshot or os.environ.get("SNAPSHOT", "202512"), force=True)
        print(
            json.dumps(
                {
                    "snapshot": get_snapshot_used(),
                    "count": get_overrides_count(),
                    "cache_files": [p.name for p in list_cache()],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if args.action == "clear":
        files = list_cache()
        for p in files:
            try:
                sz = p.stat().st_size
                p.unlink()
                print(f"[OK] removed {p.name} ({size_fmt(sz)})")
            except Exception as e:
                print(f"[ERRO] {p.name}: {e}", file=sys.stderr)
        if not files:
            print("[OK] no cache files to remove")
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
