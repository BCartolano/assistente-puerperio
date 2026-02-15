#!/usr/bin/env python3
"""
Corrige encoding de requirements.txt: lê como UTF-16 (comum no Windows) e grava em UTF-8.
Execute na raiz do projeto: python scripts/fix_requirements_encoding.py
"""
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
REQ = BASE / "requirements.txt"


def main():
    if not REQ.exists():
        print(f"Arquivo não encontrado: {REQ}", file=sys.stderr)
        return 1
    raw = REQ.read_bytes()
    # Se já for UTF-8 válido (sem BOM), não altera
    try:
        text = raw.decode("utf-8")
        if "\x00" in text:
            raise ValueError("Null bytes (UTF-16?)")
    except Exception:
        try:
            text = raw.decode("utf-16")
        except Exception:
            text = raw.decode("utf-16-le")
    REQ.write_text(text, encoding="utf-8")
    print(f"[OK] {REQ} gravado em UTF-8.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
