#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data quality checks – telefones válidos, coordenadas no bounding box Brasil,
% estabelecimentos com evidência, duplicidade por CNPJ/INE.
Gate: reprovar se % coordenadas < 85% ou 0.4–0.59 > 10% sem revisão pendente.
"""

import os
import sys
import sqlite3
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
DB_PATH = os.path.join(BASE_DIR, "backend", "cnes_cache.db")

# Bounding box Brasil (aproximado)
BR_LAT_MIN, BR_LAT_MAX = -35.0, 5.0
BR_LON_MIN, BR_LON_MAX = -75.0, -30.0

# Telefone: pelo menos 10 dígitos
PHONE_PATTERN = re.compile(r"[\d\s\-\(\)\+]{10,}")


def get_conn():
    if not os.path.exists(DB_PATH):
        return None
    return sqlite3.connect(DB_PATH)


def check_coordinates_bbox(conn) -> dict:
    """% estabelecimentos com coordenadas no bounding box do Brasil."""
    if not conn:
        return {"pct": 0.0, "total": 0, "valid": 0, "ok": False}
    cur = conn.execute(
        "SELECT COUNT(*) FROM hospitals_cache WHERE lat IS NOT NULL AND long IS NOT NULL "
        "AND lat BETWEEN ? AND ? AND long BETWEEN ? AND ?",
        (BR_LAT_MIN, BR_LAT_MAX, BR_LON_MIN, BR_LON_MAX),
    )
    valid = cur.fetchone()[0]
    cur = conn.execute("SELECT COUNT(*) FROM hospitals_cache")
    total = cur.fetchone()[0]
    pct = (valid / total * 100.0) if total else 0.0
    return {"pct": round(pct, 2), "total": total, "valid": valid, "ok": pct >= 85.0}


def check_phone_coverage(conn) -> dict:
    """% estabelecimentos com telefone válido (>= 10 dígitos)."""
    if not conn:
        return {"pct": 0.0, "total": 0, "with_phone": 0, "ok": False}
    cur = conn.execute("SELECT COUNT(*), SUM(CASE WHEN telefone IS NOT NULL AND LENGTH(TRIM(telefone)) >= 10 THEN 1 ELSE 0 END) FROM hospitals_cache")
    row = cur.fetchone()
    total, with_phone = row[0] or 0, row[1] or 0
    pct = (with_phone / total * 100.0) if total else 0.0
    return {"pct": round(pct, 2), "total": total, "with_phone": with_phone, "ok": pct >= 85.0}


def check_duplicates_cnpj(conn) -> dict:
    """Duplicidade por CNPJ (mesmo CNPJ, vários cnes_id)."""
    if not conn:
        return {"duplicates": 0, "ok": True}
    cur = conn.execute(
        "SELECT cnpj, COUNT(*) as c FROM hospitals_cache WHERE cnpj IS NOT NULL AND TRIM(cnpj) != '' GROUP BY cnpj HAVING c > 1"
    )
    rows = cur.fetchall()
    return {"duplicates": len(rows), "ok": len(rows) == 0}


def check_maternity_evidence(conn) -> dict:
    """% estabelecimentos com has_maternity=1 (evidência de maternidade)."""
    if not conn:
        return {"pct_maternity": 0.0, "total": 0, "ok": True}
    cur = conn.execute("SELECT COUNT(*), SUM(has_maternity) FROM hospitals_cache")
    row = cur.fetchone()
    total, maternity = row[0] or 0, row[1] or 0
    pct = (maternity / total * 100.0) if total else 0.0
    return {"pct_maternity": round(pct, 2), "total": total, "with_maternity": maternity, "ok": True}


def run_all_checks() -> dict:
    conn = get_conn()
    try:
        coords = check_coordinates_bbox(conn)
        phone = check_phone_coverage(conn)
        dup = check_duplicates_cnpj(conn)
        maternity = check_maternity_evidence(conn)
        gate_pass = coords["ok"] and (phone["pct"] >= 85.0 or not conn)  # Gate: coord >= 85%; phone alerta se < 85%
        return {
            "coordinates_bbox": coords,
            "phone_coverage": phone,
            "duplicates_cnpj": dup,
            "maternity_evidence": maternity,
            "gate_pass": gate_pass,
        }
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    result = run_all_checks()
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result.get("gate_pass") else 1)
