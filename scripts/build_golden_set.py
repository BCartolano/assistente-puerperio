#!/usr/bin/env python3
"""
Gera data/golden/golden_set.json a partir do banco SQLite (v_maternity_status + v_establishments_core ou hospitals_cache).
- Positivos: has_maternity = true e score >= --min-score-pos
- Negativos: has_maternity = false ou score < --max-score-neg (exclui nomes com keywords)
- Exporta opcionalmente "prováveis" (score 0.4–0.59) para data/golden/provaveis_review.csv

Uso básico:
  python scripts/build_golden_set.py --uf SP --municipio "São Paulo" --positivos 15 --negativos 15

Se precisar apontar DB manualmente:
  python scripts/build_golden_set.py --db backend/cnes_cache.db --output data/golden/golden_set.json
"""

import argparse
import csv
import json
import os
import pathlib
import sqlite3
import sys

DEFAULT_DB_URL = os.environ.get("DB_URL", "sqlite:///backend/cnes_cache.db")
DEFAULT_DB_PATH = DEFAULT_DB_URL.replace("sqlite:///", "").replace("sqlite://", "")

DEFAULT_OUTPUT = "data/golden/golden_set.json"
DEFAULT_PROVAVEIS = "data/golden/provaveis_review.csv"

DEFAULT_MIN_SCORE_POS = 0.6
DEFAULT_MAX_SCORE_NEG = 0.39

DEFAULT_KEYWORDS = ["maternidade", "hospital da mulher", "obstétrico", "obstetrico"]


def ensure_dirs(path: str):
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)


def pick_table(conn: sqlite3.Connection, candidates: list) -> str | None:
    cur = conn.cursor()
    for name in candidates:
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type IN ('view','table') AND name = ?",
            (name,),
        )
        if cur.fetchone():
            return name
    return None


def load_keywords_from_config() -> list:
    try:
        with open("config/cnes_codes.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        kws = data.get("keywords_nome_fantasia") or []
        return [str(k).lower() for k in kws] or DEFAULT_KEYWORDS
    except Exception:
        return DEFAULT_KEYWORDS


def build_filters(args, alias="e", uf_col="uf", mun_col="municipio", name_col="nome"):
    clauses = []
    params = []
    pre = f"{alias}." if alias else ""

    if args.uf:
        clauses.append(f"{pre}{uf_col} = ?")
        params.append(args.uf)
    if args.municipio:
        clauses.append(f"LOWER({pre}{mun_col}) LIKE LOWER(?)")
        params.append(f"%{args.municipio}%")
    if args.nome_like:
        clauses.append(f"LOWER({pre}{name_col}) LIKE LOWER(?)")
        params.append(f"%{args.nome_like}%")
    return clauses, params


def query_positives(conn, m_table, e_table, args):
    id_col = "cnes_id"
    if e_table == "hospitals_cache":
        clauses, params = build_filters(args, alias="e", uf_col="state", mun_col="city", name_col="name")
        sql = f"""
            SELECT cnes_id, name, state, city, telefone, 0.6
            FROM hospitals_cache e
            WHERE e.has_maternity = 1
        """
        if clauses:
            sql += " AND " + " AND ".join(clauses)
        sql += " ORDER BY e.name LIMIT ?"
        params.append(args.positivos)
    else:
        clauses, params = build_filters(args)
        sql = f"""
            SELECT e.cnes_id, e.nome, e.uf, e.municipio, e.telefone, m.score
            FROM {m_table} m
            JOIN {e_table} e ON e.cnes_id = m.cnes_id
            WHERE (m.has_maternity = 1 OR m.has_maternity = TRUE) AND COALESCE(m.score, 0) >= ?
        """
        params = [args.min_score_pos] + params
        if clauses:
            sql += " AND " + " AND ".join(clauses)
        sql += " ORDER BY m.score DESC, e.nome LIMIT ?"
        params.append(args.positivos)

    cur = conn.cursor()
    cur.execute(sql, params)
    return cur.fetchall()


def query_negatives(conn, m_table, e_table, args, exclude_keywords):
    if e_table == "hospitals_cache":
        clauses, params = build_filters(args, alias="e", uf_col="state", mun_col="city", name_col="name")
        sql = """
            SELECT cnes_id, name, state, city, telefone, 0
            FROM hospitals_cache e
            WHERE e.has_maternity = 0
        """
        for kw in exclude_keywords:
            sql += " AND LOWER(e.name) NOT LIKE ?"
            params.append(f"%{kw}%")
        if clauses:
            sql += " AND " + " AND ".join(clauses)
        sql += " ORDER BY e.name LIMIT ?"
        params.append(args.negativos)
    else:
        clauses, params = build_filters(args)
        sql = f"""
            SELECT e.cnes_id, e.nome, e.uf, e.municipio, e.telefone, m.score
            FROM {m_table} m
            JOIN {e_table} e ON e.cnes_id = m.cnes_id
            WHERE (COALESCE(m.has_maternity,0) = 0 OR COALESCE(m.score,0) <= ?)
        """
        params = [args.max_score_neg]
        for kw in exclude_keywords:
            sql += " AND LOWER(e.nome) NOT LIKE ?"
            params.append(f"%{kw}%")
        if clauses:
            sql += " AND " + " AND ".join(clauses)
        sql += " ORDER BY m.score ASC, e.nome LIMIT ?"
        params.append(args.negativos)

    cur = conn.cursor()
    cur.execute(sql, params)
    return cur.fetchall()


def query_probables(conn, m_table, e_table, args):
    if m_table == "hospitals_cache":
        return []
    clauses, params = build_filters(args)
    sql = f"""
        SELECT e.cnes_id, e.nome, e.uf, e.municipio, e.telefone, m.score, m.evidence
        FROM {m_table} m
        JOIN {e_table} e USING (cnes_id)
        WHERE m.score BETWEEN 0.4 AND 0.59
    """
    if clauses:
        sql += " AND " + " AND ".join(clauses)
    sql += " ORDER BY m.score DESC, e.nome LIMIT ?"
    params.append(args.provaveis)
    cur = conn.cursor()
    cur.execute(sql, params)
    return cur.fetchall()


def write_golden(output_path, positives, negatives):
    ensure_dirs(output_path)
    items = []

    for row in positives:
        cnes_id = str(row[0])
        score = row[5] if len(row) > 5 else 0.6
        items.append({
            "cnes_id": cnes_id,
            "expected_has_maternity": True,
            "min_score": float(score) if score is not None else 0.6,
            "notes": "Gerado automaticamente (confirmado).",
        })

    for row in negatives:
        cnes_id = str(row[0])
        items.append({
            "cnes_id": cnes_id,
            "expected_has_maternity": False,
            "notes": "Gerado automaticamente (negativo seguro).",
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    return len(items)


def write_probables_csv(csv_path, rows):
    ensure_dirs(csv_path)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["cnes_id", "nome", "uf", "municipio", "telefone", "score", "evidence"])
        for r in rows:
            w.writerow([r[0], r[1], r[2], r[3], r[4], r[5], r[6]])
    return len(rows)


def main():
    parser = argparse.ArgumentParser(description="Gera golden_set.json a partir do banco SQLite.")
    parser.add_argument("--db", default=DEFAULT_DB_PATH, help="Caminho do SQLite (ex.: backend/cnes_cache.db)")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Saída JSON do golden set")
    parser.add_argument("--provaveis-out", default=DEFAULT_PROVAVEIS, help="CSV de prováveis para revisão")
    parser.add_argument("--uf", help="Filtro por UF (ex.: SP)")
    parser.add_argument("--municipio", help="Filtro por município (ex.: São Paulo)")
    parser.add_argument("--nome-like", help="Filtro por substring no nome (ex.: Maternidade)")
    parser.add_argument("--positivos", type=int, default=15, help="Quantidade de positivos")
    parser.add_argument("--negativos", type=int, default=15, help="Quantidade de negativos")
    parser.add_argument("--min-score-pos", type=float, default=DEFAULT_MIN_SCORE_POS, help="Score mínimo dos positivos")
    parser.add_argument("--max-score-neg", type=float, default=DEFAULT_MAX_SCORE_NEG, help="Score máximo dos negativos")
    parser.add_argument("--sem-provaveis", action="store_true", help="Não exportar CSV de prováveis")
    parser.add_argument("--provaveis", type=int, default=100, help="Limite de prováveis para CSV")
    args = parser.parse_args()

    if not os.path.exists(args.db):
        print(f"[ERRO] Banco não encontrado: {args.db}", file=sys.stderr)
        sys.exit(2)

    conn = sqlite3.connect(args.db)
    try:
        m_table = pick_table(conn, ["v_maternity_status", "maternity_classification", "hospitals_cache"])
        e_table = pick_table(conn, ["v_establishments_core", "establishments", "hospitals_cache"])
        if not m_table or not e_table:
            print("[ERRO] Views/tabelas necessárias não encontradas (v_maternity_status/v_establishments_core ou hospitals_cache).", file=sys.stderr)
            sys.exit(3)
        if e_table != "hospitals_cache" and m_table == "hospitals_cache":
            e_table = "hospitals_cache"

        keywords = load_keywords_from_config()

        pos = query_positives(conn, m_table, e_table, args)
        neg = query_negatives(conn, m_table, e_table, args, keywords)

        total = write_golden(args.output, pos, neg)

        print(f"[OK] golden_set salvo em {args.output} (pos={len(pos)}, neg={len(neg)}, total={total})")

        if not args.sem_provaveis and m_table != "hospitals_cache":
            prob = query_probables(conn, m_table, e_table, args)
            nprob = write_probables_csv(args.provaveis_out, prob)
            print(f"[OK] Prováveis para revisão: {nprob} linhas em {args.provaveis_out}")

        print("\nDica: pytest tests/golden/test_golden_set.py -v\n")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
