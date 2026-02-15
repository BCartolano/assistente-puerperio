#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Probe de performance: consulta /api/v1/health (ou sobe Flask temporário),
extrai perf (startup_ms, overrides.boot_ms, first_request_ms), aplica thresholds
e opcionalmente injeta em reports/run_summary.json.
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)

DEF_URL = "http://localhost:5000"
DEF_PORT = 5001


def load_run_summary() -> dict:
    p = REPORTS / "run_summary.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_run_summary(data: dict) -> None:
    (REPORTS / "run_summary.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def wait_healthy(base_url: str, timeout: int = 60) -> bool:
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            r = requests.get(base_url.rstrip("/") + "/api/v1/health", timeout=5)
            if r.ok:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def start_temp_server(port: int) -> subprocess.Popen:
    env = os.environ.copy()
    env.setdefault("FLASK_APP", "backend.app")
    env.setdefault("PERF_EXPOSE", "on")
    env.setdefault("PERF_LOG", "on")
    env.setdefault("OVERRIDES_BOOT", env.get("OVERRIDES_BOOT", "background"))
    cmd = [sys.executable, "-m", "flask", "--app", "backend.app", "run", "-p", str(port)]
    proc = subprocess.Popen(
        cmd, cwd=str(ROOT), env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    return proc


def stop_proc(proc: subprocess.Popen | None) -> None:
    if proc is None or proc.poll() is not None:
        return
    try:
        if os.name == "nt":
            proc.terminate()
        else:
            proc.send_signal(signal.SIGINT)
        proc.wait(timeout=5)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass


def probe(base_url: str) -> dict:
    if requests is None:
        return {}
    r = requests.get(base_url.rstrip("/") + "/api/v1/health", timeout=10)
    r.raise_for_status()
    data = r.json()
    perf = data.get("perf") or {}
    overrides = perf.get("overrides") or {}
    return {
        "startup_ms": perf.get("startup_ms"),
        "first_request_ms": perf.get("first_request_ms"),
        "first_request_at": perf.get("first_request_at"),
        "overrides_boot_ms": overrides.get("boot_ms"),
        "overrides_boot_at": overrides.get("boot_at"),
        "overrides_snapshot": overrides.get("snapshot"),
        "overrides_count": overrides.get("count"),
        "overrides_mode": overrides.get("mode"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Probe de performance (/health)")
    ap.add_argument("--base-url", default=os.getenv("PERF_PROBE_BASE_URL", DEF_URL))
    ap.add_argument("--spawn", action="store_true", help="Subir Flask temporário (porta --port)")
    ap.add_argument("--port", type=int, default=DEF_PORT)
    ap.add_argument("--timeout", type=int, default=60)
    ap.add_argument("--update-run-summary", action="store_true")
    args = ap.parse_args()

    base = args.base_url.rstrip("/")
    spawned = None
    try:
        if args.spawn:
            spawned = start_temp_server(args.port)
            base = f"http://localhost:{args.port}"
            if not wait_healthy(base, timeout=args.timeout):
                raise RuntimeError("Timeout esperando /health no servidor temporário")

        if requests is None:
            print('{"error": "requests não instalado"}', file=sys.stderr)
            return 1

        metrics = probe(base)

        max_startup = float(os.getenv("PERF_MAX_STARTUP_MS", "2500"))
        max_ovr_boot = float(os.getenv("PERF_MAX_OVR_BOOT_MS", "2000"))
        max_first_req = float(os.getenv("PERF_MAX_FIRST_REQ_MS", "1500"))

        warnings = []
        errors = []

        if metrics.get("startup_ms") is not None and metrics["startup_ms"] > max_startup:
            warnings.append(f"startup_ms {metrics['startup_ms']} > {max_startup}ms")
        if metrics.get("overrides_boot_ms") is not None and metrics["overrides_boot_ms"] > max_ovr_boot:
            warnings.append(f"overrides_boot_ms {metrics['overrides_boot_ms']} > {max_ovr_boot}ms")
        if metrics.get("first_request_ms") is not None and metrics["first_request_ms"] > max_first_req:
            warnings.append(f"first_request_ms {metrics['first_request_ms']} > {max_first_req}ms")

        out = {
            "perf_summary": metrics,
            "perf_thresholds": {
                "startup_ms": max_startup,
                "overrides_boot_ms": max_ovr_boot,
                "first_request_ms": max_first_req,
            },
            "perf_warnings": warnings,
            "perf_errors": errors,
        }

        if args.update_run_summary:
            rs = load_run_summary()
            rs.update(out)
            save_run_summary(rs)

        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0
    finally:
        stop_proc(spawned)


if __name__ == "__main__":
    sys.exit(main())
