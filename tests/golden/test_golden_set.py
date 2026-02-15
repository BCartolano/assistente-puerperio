import json
import os
import pathlib
import sqlite3
import pytest

GOLDEN_PATH = pathlib.Path("data/golden/golden_set.json")


def _sqlite_path_from_url(db_url: str) -> str:
    if db_url.startswith("sqlite:///"):
        return db_url.replace("sqlite:///", "", 1)
    if db_url.startswith("sqlite://"):
        return db_url.replace("sqlite://", "", 1)
    return db_url


@pytest.fixture(scope="module")
def golden_data():
    if not GOLDEN_PATH.exists():
        pytest.skip("golden_set.json não encontrado; pulando testes do golden set.")
    with GOLDEN_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list) or len(data) == 0:
        pytest.skip("golden_set.json vazio; pulando.")
    return data


@pytest.fixture(scope="module")
def db_conn():
    db_url = os.environ.get("DB_URL", "sqlite:///backend/cnes_cache.db")
    if not db_url.startswith("sqlite"):
        pytest.skip("DB_URL não aponta para sqlite; pulando testes do golden set.")
    db_path = _sqlite_path_from_url(db_url)
    if not os.path.exists(db_path):
        pytest.skip(f"Arquivo de banco não encontrado: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


def _pick_table(conn: sqlite3.Connection):
    cur = conn.cursor()
    for name in ("v_maternity_status", "maternity_classification", "hospitals_cache"):
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type IN ('view','table') AND name = ?",
            (name,),
        )
        if cur.fetchone():
            return name
    return None


def _has_maternity_col(conn: sqlite3.Connection, table: str) -> str:
    cur = conn.execute(f"PRAGMA table_info({table})")
    cols = [row[1] for row in cur.fetchall()]
    if "has_maternity" in cols:
        return "has_maternity"
    return "has_maternity"


def _score_col(conn: sqlite3.Connection, table: str) -> str:
    cur = conn.execute(f"PRAGMA table_info({table})")
    cols = [row[1] for row in cur.fetchall()]
    if "score" in cols:
        return "score"
    return None


def test_golden_set_matches_classification(db_conn, golden_data):
    table = _pick_table(db_conn)
    if not table:
        pytest.skip("Nem v_maternity_status nem maternity_classification nem hospitals_cache encontrados; pulando.")
    cur = db_conn.cursor()
    has_col = _has_maternity_col(db_conn, table)
    score_col = _score_col(db_conn, table)
    id_col = "cnes_id" if table != "hospitals_cache" else "cnes_id"

    missing = []
    mismatches = []
    low_scores = []

    for item in golden_data:
        cnes_id = str(item["cnes_id"])
        expected_has_maternity = bool(item.get("expected_has_maternity"))
        min_score = item.get("min_score")

        if score_col:
            cur.execute(f"SELECT cnes_id, {has_col}, {score_col} FROM {table} WHERE cnes_id = ?", (cnes_id,))
        else:
            cur.execute(f"SELECT cnes_id, {has_col} FROM {table} WHERE cnes_id = ?", (cnes_id,))
        row = cur.fetchone()
        if not row:
            missing.append(cnes_id)
            continue

        got_has = bool(row[has_col])
        got_score_raw = row[score_col] if score_col and len(row) > 2 else None
        try:
            got_score = float(got_score_raw) if got_score_raw is not None else None
        except Exception:
            got_score = None

        if got_has != expected_has_maternity:
            mismatches.append((cnes_id, expected_has_maternity, got_has))

        if min_score is not None and got_score is not None:
            if got_score < float(min_score):
                low_scores.append((cnes_id, min_score, got_score))

    assert not missing, f"IDs do golden_set ausentes no banco: {missing}"
    assert not mismatches, f"Divergências has_maternity: {mismatches}"
    assert not low_scores, f"Scores abaixo do mínimo: {low_scores}"
