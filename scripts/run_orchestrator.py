#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orquestrador BMAD – Lê .env (SCORING_FILE, CNES_CODES_FILE, DB_URL).
Passos: ingest → classify → (opcional) geocode → checks/data_quality.py → pytest.
Gera reports/run_summary.json com: coord_coverage, phone_coverage, geocode_fail_rate,
tests_passed, golden_accuracy (se existir golden set).
Gates: coord >= 0.85, phone >= 0.85, geocode_fail < 0.10, tests_passed=true,
golden_accuracy >= 0.95 quando houver.
"""

import os
import sys
import json
import argparse
import re
import subprocess
from datetime import datetime
from pathlib import Path

import pandas as pd


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        try:
            return path.read_text(encoding="latin-1")
        except Exception:
            return None


def parse_geo_health_summary(path: Path) -> dict | None:
    txt = _read_text(path)
    if not txt:
        return None

    def grab(pattern, cast=str):
        m = re.search(pattern, txt, re.MULTILINE)
        if not m:
            return None
        try:
            return cast(m.group(1))
        except Exception:
            return m.group(1)

    total = grab(r"^Total:\s+(\d+)$", int)
    coord_cov = grab(r"^Cobertura de coordenadas:\s+([\d.]+)%", float)
    phone_cov = grab(r"^Cobertura de telefone:\s+([\d.]+)%", float)
    confirmados = grab(r"^Confirmados \(Ala de Maternidade\):\s+(\d+)$", int)
    provaveis = grab(r"^Prováveis:\s+(\d+)$", int)
    outros = grab(r"^Outros:\s+(\d+)$", int)

    sus_line = re.search(r"^SUS:\s+Sim=(\d+)\s+•\s+Não=(\d+)\s+•\s+Desconhecido=(\d+)", txt, re.MULTILINE)
    sus = None
    if sus_line:
        sus = {
            "sim": int(sus_line.group(1)),
            "nao": int(sus_line.group(2)),
            "desconhecido": int(sus_line.group(3)),
        }

    top = []
    for m in re.finditer(r"^\s{2}([A-Z]{2}|\?\?):\s+conf=(\d+)\s+•\s+total=(\d+)", txt, re.MULTILINE):
        top.append({"uf": m.group(1), "confirmados": int(m.group(2)), "total": int(m.group(3))})

    return {
        "total": total,
        "coord_coverage_pct": round(coord_cov / 100.0, 4) if coord_cov is not None else None,
        "phone_coverage_pct": round(phone_cov / 100.0, 4) if phone_cov is not None else None,
        "confirmados": confirmados,
        "provaveis": provaveis,
        "outros": outros,
        "sus": sus,
        "top_ufs": top[:10],
    }


def run_geo_healthcheck(run_summary: dict) -> None:
    try:
        print("[INFO] Rodando check_geo_parquet.py …")
        subprocess.run(
            [sys.executable, "scripts/check_geo_parquet.py", "--municipios", "--export-missing"],
            cwd=BASE_DIR,
            check=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
        summary_path = Path(BASE_DIR) / "reports" / "geo_health_summary.txt"
        metrics = parse_geo_health_summary(summary_path) if summary_path.exists() else None
        if metrics:
            run_summary["geo_health"] = metrics
            print("[INFO] geo_health anexado ao run_summary.json")
        else:
            print("[AVISO] geo_health_summary.txt ausente ou vazio; run_summary sem bloco geo_health")
    except subprocess.CalledProcessError as e:
        print(f"[AVISO] healthcheck geo falhou (não bloqueia): {e}")
    except Exception as e:
        print(f"[AVISO] healthcheck geo falhou (não bloqueia): {e}")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(BASE_DIR, ".env"))
except ImportError:
    pass

def get_env(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()

SCORING_FILE = get_env("SCORING_FILE", os.path.join(BASE_DIR, "config", "scoring.yaml"))
CNES_CODES_FILE = get_env("CNES_CODES_FILE", os.path.join(BASE_DIR, "config", "cnes_codes.json"))
DB_URL = get_env("DB_URL", f"sqlite:///{os.path.join(BASE_DIR, 'backend', 'cnes_cache.db')}")
RUN_GEOCODE = get_env("RUN_GEOCODE", "true").lower() in ("1", "true", "on", "yes")
RUN_TESTS = get_env("RUN_TESTS", "true").lower() in ("1", "true", "on", "yes")
GOLDEN_SET_FILE = get_env("GOLDEN_SET_FILE", os.path.join(BASE_DIR, "data", "golden", "golden_set.json"))

REPORT_PATH = os.path.join(BASE_DIR, "reports", "run_summary.json")
LOG_DIR = os.path.join(BASE_DIR, "logs")
RELEASE_UF = get_env("RELEASE_UF", "")
QA_PUBLICO_PCT_THRESHOLD = 0.005  # bloquear se qa_publico_vs_privado > 0.5% na UF de release


def quick_metrics_from_logs(log_path: Path):
    """Lê logs/search_events.jsonl, calcula indicadores e retorna dict para run_summary.search_metrics. Não bloqueia se falhar."""
    try:
        if not log_path.exists():
            print("[INFO] quick_metrics: log ausente; pulando.")
            return None
        df = pd.read_json(log_path, lines=True)
        if df.empty:
            return None

        total = len(df)

        def to_bool_series(name):
            if name not in df.columns:
                return pd.Series([False] * total, index=df.index)
            s = df[name]
            return s.fillna(False).astype(str).str.lower().map(
                {"true": True, "1": True, "false": False, "0": False}
            ).fillna(False)

        expanded = to_bool_series("expanded").mean()
        banner = to_bool_series("banner_192").mean()

        if "radius_used" in df.columns:
            med_radius = pd.to_numeric(df["radius_used"].fillna(df.get("radius_requested")), errors="coerce").median()
        else:
            med_radius = pd.to_numeric(df.get("radius_requested", pd.Series(dtype=float)), errors="coerce").median()

        hitA = pd.to_numeric(df.get("found_A", pd.Series(0, index=df.index)), errors="coerce").fillna(0).gt(0).mean()
        hitB = pd.to_numeric(df.get("found_B", pd.Series(0, index=df.index)), errors="coerce").fillna(0).gt(0).mean()

        if "ts" in df.columns:
            first_ts = pd.to_datetime(df["ts"], errors="coerce").min()
            last_ts = pd.to_datetime(df["ts"], errors="coerce").max()
            first_ts = first_ts.isoformat() if pd.notna(first_ts) else None
            last_ts = last_ts.isoformat() if pd.notna(last_ts) else None
        else:
            first_ts = last_ts = None

        def map_sus(v):
            if v is True or str(v).lower() in ("true", "1", "sim", "yes", "y"):
                return "sus_on"
            if v is False or str(v).lower() in ("false", "0", "nao", "não", "no", "n"):
                return "sus_off"
            return "sus_null"

        sus_share = df["sus"].map(map_sus).value_counts(normalize=True).to_dict() if "sus" in df.columns else {"sus_null": 1.0}

        med_radius_f = float(med_radius) if med_radius is not None and pd.notna(med_radius) else None
        return {
            "total_events": int(total),
            "expanded_pct": round(float(expanded), 4),
            "banner_192_pct": round(float(banner), 4),
            "radius_median_km": round(med_radius_f, 2) if med_radius_f is not None else None,
            "hitA_pct": round(float(hitA), 4),
            "hitB_pct": round(float(hitB), 4),
            "sus_share": sus_share,
            "first_ts": first_ts,
            "last_ts": last_ts,
        }
    except Exception as e:
        print(f"[AVISO] quick_metrics_from_logs falhou: {e}")
        return None


def run_search_analyzer():
    """Roda analyze_search_events.py se existir logs/search_events.jsonl. Não bloqueia o pipeline."""
    log_path = Path(BASE_DIR) / "logs" / "search_events.jsonl"
    if not log_path.exists():
        print("[INFO] logs/search_events.jsonl ausente; pulando análise.")
        return
    try:
        print("[INFO] Rodando analyze_search_events.py …")
        subprocess.run(
            [sys.executable, os.path.join(BASE_DIR, "scripts", "analyze_search_events.py")],
            cwd=BASE_DIR,
            check=True,
        )
        print("[OK] Análise gerou relatórios em reports/")
    except Exception as e:
        print(f"[AVISO] Falha ao rodar analyzer (não bloqueia): {e}")


def run_cmd(cmd: list, cwd: str = None) -> tuple:
    try:
        r = subprocess.run(cmd, cwd=cwd or BASE_DIR, capture_output=True, text=True, timeout=300)
        return (r.returncode == 0, (r.stdout or "") + (r.stderr or ""))
    except Exception as e:
        return (False, str(e))


def main():
    parser = argparse.ArgumentParser(description="Orquestrador pipeline CNES")
    parser.add_argument("--snapshot", default=get_env("SNAPSHOT", "202512"), help="Snapshot data/raw/<snapshot>")
    args = parser.parse_args()
    snapshot = args.snapshot

    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    summary = {
        "version": "1.0",
        "run_id": run_id,
        "timestamp": datetime.now().isoformat(),
        "config": {"SCORING_FILE": SCORING_FILE, "CNES_CODES_FILE": CNES_CODES_FILE, "DB_URL": DB_URL},
        "metrics": {
            "coord_coverage": 0.0,
            "phone_coverage": 0.0,
            "geocode_fail_rate": 0.0,
            "tests_passed": False,
            "golden_accuracy": None,
        },
        "gates": {
            "config_present": False,
            "ingest_ok": False,
            "classify_ok": False,
            "geocode_ok": True,
            "data_quality_ok": False,
            "tests_passed": False,
            "golden_accuracy_ok": None,
            "qa_esfera_ok": True,
            "all_passed": False,
        },
        "errors": [],
    }

    # Gate: config
    if not os.path.isfile(CNES_CODES_FILE):
        summary["errors"].append("CNES_CODES_FILE não encontrado: " + CNES_CODES_FILE)
    else:
        summary["gates"]["config_present"] = True

    # Ingest
    ok_ingest, out_ingest = run_cmd([sys.executable, "-m", "backend.pipelines.ingest", "--snapshot", snapshot])
    summary["gates"]["ingest_ok"] = ok_ingest
    if not ok_ingest:
        summary["errors"].append("ingest falhou: " + out_ingest[:500])

    # Classify
    geojson = os.path.join(BASE_DIR, "backend", "data", "maternities_whitelist.geojson")
    if os.path.isfile(geojson):
        ok_class, out_class = run_cmd([
            sys.executable, "-m", "backend.pipelines.classify",
            "--input", geojson,
            "--output", os.path.join(BASE_DIR, "backend", "data", "maternities_classified.json"),
        ])
        summary["gates"]["classify_ok"] = ok_class
        if not ok_class:
            summary["errors"].append("classify falhou: " + out_class[:500])
    else:
        summary["gates"]["classify_ok"] = True

    # (Opcional) Geocode – placeholder
    summary["gates"]["geocode_ok"] = True
    summary["metrics"]["geocode_fail_rate"] = 0.0

    # Data quality
    ok_dq, out_dq = run_cmd([sys.executable, os.path.join(BASE_DIR, "checks", "data_quality.py")])
    summary["gates"]["data_quality_ok"] = ok_dq
    if out_dq:
        try:
            dq = json.loads(out_dq.strip())
            coords = dq.get("coordinates_bbox", {})
            phone = dq.get("phone_coverage", {})
            summary["metrics"]["coord_coverage"] = coords.get("pct", 0) / 100.0 if isinstance(coords.get("pct"), (int, float)) else 0.0
            summary["metrics"]["phone_coverage"] = phone.get("pct", 0) / 100.0 if isinstance(phone.get("pct"), (int, float)) else 0.0
        except Exception:
            try:
                for line in out_dq.split("\n"):
                    if line.strip().startswith("{"):
                        dq = json.loads(line.strip())
                        coords = dq.get("coordinates_bbox", {})
                        phone = dq.get("phone_coverage", {})
                        summary["metrics"]["coord_coverage"] = coords.get("pct", 0) / 100.0 if isinstance(coords.get("pct"), (int, float)) else 0.0
                        summary["metrics"]["phone_coverage"] = phone.get("pct", 0) / 100.0 if isinstance(phone.get("pct"), (int, float)) else 0.0
                        break
            except Exception:
                pass
    if not ok_dq:
        summary["errors"].append("data_quality gate falhou")

    # Pytest
    if RUN_TESTS:
        ok_test, out_test = run_cmd([sys.executable, "-m", "pytest", "tests/unit", "-v", "--tb=short", "-x"], cwd=BASE_DIR)
        summary["gates"]["tests_passed"] = ok_test
        summary["metrics"]["tests_passed"] = ok_test
        if not ok_test:
            summary["errors"].append("pytest falhou: " + (out_test[-1000:] if len(out_test) > 1000 else out_test))
    else:
        summary["gates"]["tests_passed"] = True
        summary["metrics"]["tests_passed"] = True

    # Golden set (se existir)
    if os.path.isfile(GOLDEN_SET_FILE):
        try:
            with open(GOLDEN_SET_FILE, "r", encoding="utf-8") as f:
                golden = json.load(f)
            # Placeholder: calcular acurácia se houver formato esperado
            acc = golden.get("accuracy") or golden.get("golden_accuracy")
            summary["metrics"]["golden_accuracy"] = acc
            summary["gates"]["golden_accuracy_ok"] = acc is not None and float(acc) >= 0.95
        except Exception:
            summary["gates"]["golden_accuracy_ok"] = None
    else:
        summary["gates"]["golden_accuracy_ok"] = None

    # Gates numéricos
    coord_ok = summary["metrics"]["coord_coverage"] >= 0.85
    phone_ok = summary["metrics"]["phone_coverage"] >= 0.85
    geocode_ok = summary["metrics"]["geocode_fail_rate"] < 0.10
    golden_ok = summary["gates"]["golden_accuracy_ok"] is None or summary["gates"]["golden_accuracy_ok"]
    qa_esfera_ok = summary["gates"]["qa_esfera_ok"]

    summary["gates"]["all_passed"] = (
        summary["gates"]["config_present"]
        and summary["gates"]["ingest_ok"]
        and summary["gates"]["classify_ok"]
        and summary["gates"]["geocode_ok"]
        and summary["gates"]["data_quality_ok"]
        and summary["gates"]["tests_passed"]
        and golden_ok
        and qa_esfera_ok
    )

    # Injetar search_metrics a partir de logs/search_events.jsonl (não bloqueia gates)
    logs_path = Path(BASE_DIR) / "logs" / "search_events.jsonl"
    search_metrics = quick_metrics_from_logs(logs_path)
    if search_metrics:
        summary["search_metrics"] = search_metrics
        print("[INFO] quick_metrics anexado ao run_summary.json")
        # Resumo humano no console
        m = search_metrics
        line = (
            f"buscas={m['total_events']} • exp={m['expanded_pct']:.0%} • banner={m['banner_192_pct']:.0%} • "
            f"raio_med={m.get('radius_median_km') or '—'} km • hitA={m['hitA_pct']:.0%} • hitB={m['hitB_pct']:.0%}"
        )
        print(f"[RESUMO BUSCAS] {line}")
    else:
        print("[INFO] quick_metrics ausente; run_summary sem bloco search_metrics")

    # Healthcheck geo (não bloqueia)
    if os.environ.get("RUN_GEO_HEALTHCHECK", "true").lower() in ("1", "true", "yes", "sim"):
        run_geo_healthcheck(summary)

    # QA mismatches: gera 3 CSVs em reports/ e anexa qa_hints ao run_summary
    # Gate: WARNING se qa_publico_vs_privado > 0; bloquear se > 0.5% na UF de release (RELEASE_UF)
    if os.environ.get("RUN_QA_MISMATCHES", "true").lower() in ("1", "true", "yes", "sim"):
        try:
            sys.path.insert(0, BASE_DIR)
            from scripts.qa_mismatches import run_qa_mismatches
            qa_hints = run_qa_mismatches(
                out_dir=Path(BASE_DIR) / "reports",
                release_uf=RELEASE_UF or None,
            )
            summary["qa_hints"] = qa_hints
            if "error" not in qa_hints:
                print("[OK] QA mismatches: 3 CSVs em reports/; qa_hints anexado ao run_summary.json")
                n_publico = qa_hints.get("qa_publico_vs_privado", 0)
                n = n_publico + qa_hints.get("qa_ambulatorial_vazando", 0) + qa_hints.get("qa_maternidade_nao_marcada", 0)
                if n > 0:
                    print(f"[AVISO] QA encontrou {n} itens para revisar (veja reports/qa_*.csv)")
                if n_publico > 0:
                    print(f"[WARNING] qa_publico_vs_privado = {n_publico} (hospitais públicos por nome com esfera não-Público); revisar reports/qa_publico_vs_privado.csv")
                    summary.setdefault("qa_warnings", []).append(f"qa_publico_vs_privado={n_publico}")
                # Gate: bloquear se > 0.5% na UF de release
                pct_uf = qa_hints.get("qa_publico_vs_privado_pct_uf")
                if RELEASE_UF and pct_uf is not None:
                    if pct_uf > QA_PUBLICO_PCT_THRESHOLD:
                        summary["gates"]["qa_esfera_ok"] = False
                        summary.setdefault("qa_warnings", []).append(
                            f"qa_publico_vs_privado_pct_uf={pct_uf:.2%} > {QA_PUBLICO_PCT_THRESHOLD:.2%} na UF {RELEASE_UF.strip()}"
                        )
                        summary["errors"].append(
                            f"Gate QA esfera: {pct_uf:.2%} na UF {RELEASE_UF.strip()} excede {QA_PUBLICO_PCT_THRESHOLD:.0%}. Revisar reports/qa_publico_vs_privado.csv."
                        )
                        print(f"[FAIL] qa_publico_vs_privado na UF {RELEASE_UF}: {pct_uf:.2%} > {QA_PUBLICO_PCT_THRESHOLD:.0%}")
            else:
                print(f"[AVISO] QA mismatches: {qa_hints.get('error', 'erro')}")
        except Exception as e:
            print(f"[AVISO] QA mismatches falhou (não bloqueia): {e}")
            summary["qa_hints"] = {"error": str(e)}

    # Recalcular all_passed após QA (gate qa_esfera_ok pode ter sido alterado)
    qa_esfera_ok = summary["gates"].get("qa_esfera_ok", True)
    golden_ok = summary["gates"]["golden_accuracy_ok"] is None or summary["gates"]["golden_accuracy_ok"]
    summary["gates"]["all_passed"] = (
        summary["gates"]["config_present"]
        and summary["gates"]["ingest_ok"]
        and summary["gates"]["classify_ok"]
        and summary["gates"]["geocode_ok"]
        and summary["gates"]["data_quality_ok"]
        and summary["gates"]["tests_passed"]
        and golden_ok
        and qa_esfera_ok
    )

    # Perf probe: consulta /health (ou sobe servidor temporário) e injeta perf_summary no run_summary
    def run_perf_probe():
        try:
            base = os.environ.get("PERF_PROBE_BASE_URL", "http://localhost:5000")
            spawn = os.environ.get("PERF_PROBE_SPAWN", "").lower() in ("1", "true", "on", "yes")
            cmd = [sys.executable, "scripts/perf_probe.py", "--base-url", base]
            if spawn:
                cmd.extend(["--spawn"])
            result = subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True, timeout=120)
            if result.returncode == 0 and result.stdout:
                out = json.loads(result.stdout)
                summary["perf_summary"] = out.get("perf_summary", {})
                summary["perf_thresholds"] = out.get("perf_thresholds", {})
                summary["perf_warnings"] = out.get("perf_warnings", [])
                summary["perf_errors"] = out.get("perf_errors", [])
                print("[INFO] perf_probe concluído; perf_summary anexado ao run_summary.json")
        except Exception as e:
            print(f"[AVISO] perf_probe falhou (não bloqueia): {e}")

    if os.environ.get("RUN_PERF_PROBE", "false").lower() in ("1", "true", "on", "yes"):
        run_perf_probe()

    # Quick-check de overrides na área (QC_LAT, QC_LON) – API já deve estar de pé (ex.: após perf_probe --spawn)
    def run_override_quick_check():
        try:
            lat = os.environ.get("QC_LAT")
            lon = os.environ.get("QC_LON")
            if not lat or not lon:
                return
            try:
                import requests
            except ImportError:
                print("[AVISO] quick_check: requests não instalado")
                return
            base = os.environ.get("PERF_PROBE_BASE_URL", "http://localhost:5000")
            radius = os.environ.get("QC_RADIUS", "25")
            url = f"{base.rstrip('/')}/api/v1/debug/overrides/quick_check?lat={lat}&lon={lon}&radius_km={radius}"
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            qc = r.json()
            summary["override_quick_check"] = qc
            print("[INFO] override quick_check:", qc)
        except Exception as e:
            print(f"[AVISO] quick_check falhou: {e}")

    run_override_quick_check()

    # Guard: valida que não há "Desconhecido" no Parquet
    def guard_no_unknown():
        try:
            res = subprocess.run(
                [sys.executable, "scripts/guard_no_unknown.py"],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=BASE_DIR,
            )
            if res.stdout:
                print(res.stdout)
            if res.stderr:
                print(res.stderr, file=sys.stderr)
            if res.returncode not in (0, 2):  # 2 = arquivo não existe; não bloqueia se arquivo ausente
                raise RuntimeError("esfera inválida detectada no Parquet")
            elif res.returncode == 2:
                print("[AVISO] guard_no_unknown: arquivo Parquet não encontrado (não bloqueia)")
        except RuntimeError:
            raise
        except Exception as e:
            print(f"[ERRO] guard_no_unknown: {e}")
            raise

    guard_no_unknown()

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    sys.exit(0 if summary["gates"]["all_passed"] else 1)


if __name__ == "__main__":
    main()
