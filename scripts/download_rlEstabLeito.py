#!/usr/bin/env python3
"""
Baixa LT (Leitos por UF) do DATASUS e gera data/tbLeito<SNAPSHOT>.csv unificado.

Ordem de fontes:
  1. Espelho S3 (se disponível)
  2. FTP DATASUS (lista diretórios conhecidos e baixa LT??<YYMM>.dbc)

Leitura dos .dbc (opcional):
  Ordem: pyreaddbc (Linux/mac) → dbc-to-dbf + dbfread (Python puro, Windows) → pysus.
  No Windows, use: python -m pip install dbc-to-dbf dbfread  (evita compilar C).

Mapeamento de colunas (flexível):
  CNES: CO_CNES | CO_UNIDADE | CNES
  Tipo de leito: CO_TIPO_LEITO | TP_LEITO | COD_TIPO_LEITO | COD_LEITO
  Quantidade: QT_LEITOS | QT_EXIST | QT_TOTAL | TOTAL_LEITOS

Uso:
  # Windows (Python puro, sem compilador C):
  python -m pip install dbc-to-dbf dbfread
  # Linux/mac (opcional, mais rápido): python -m pip install pyreaddbc
  python scripts/download_rlEstabLeito.py --snapshot 202512
"""
import argparse
import ftplib
import re
import sys
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA = BASE_DIR / "data"
RAW = DATA / "raw"
OUT_CSV = "tbLeito{snap}.csv"

UFS = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS",
    "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC",
    "SP", "SE", "TO",
]

# Snapshot 202512 → YYMM = 2512 (DATASUS usa YYMM no nome do arquivo)
def snapshot_to_yymm(snap: str) -> str:
    if len(snap) == 6 and snap.isdigit():
        return snap[2:4] + snap[4:6]  # 202512 → 2512
    if len(snap) == 4 and snap.isdigit():
        return snap
    return "2512"

S3_DIRS = [
    "https://datasus-ftp-mirror.nyc3.cdn.digitaloceanspaces.com/dissemin/publicos/CNES/200508_/Dados/LT",
    "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br",
]
S3_SUB = "CNES/Leitos"

FTP_HOST = "ftp.datasus.gov.br"
FTP_LT_DIRS = [
    "/dissemin/publicos/CNES/200508_/Dados/LT",
    "/dissemin/publicos/CNES/201501_/Dados/LT",
    "/dissemin/publicos/CNES/201508_/Dados/LT",
    "/dissemin/publicos/CNES/200801_/Dados/LT",
]


def ensure_dirs(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def http_get(url: str, dest: Path) -> bool:
    try:
        import urllib.request
        urllib.request.urlretrieve(url, dest)
        if dest.exists() and dest.stat().st_size > 0:
            print(f"[S3] OK {url} -> {dest.name}")
            return True
    except Exception as e:
        pass
    try:
        import requests
        r = requests.get(url, timeout=30)
        if r.status_code == 200 and r.content:
            ensure_dirs(dest)
            dest.write_bytes(r.content)
            print(f"[S3] OK {url} -> {dest.name}")
            return True
        print(f"[S3] {r.status_code} {url}")
    except Exception as e:
        print(f"[S3] ERRO {url}: {e}")
    return False


def ftp_listdir(ftp: ftplib.FTP, d: str) -> list:
    try:
        ftp.cwd(d)
        return ftp.nlst()
    except Exception as e:
        print(f"[FTP] falha ao listar {d}: {e}")
        return []


def ftp_download(ftp: ftplib.FTP, remote_path: str, dest: Path) -> bool:
    """Baixa arquivo via FTP. remote_path pode ser com ou sem barra inicial."""
    try:
        ensure_dirs(dest)
        with open(dest, "wb") as f:
            ftp.retrbinary(f"RETR {remote_path}", f.write)
        print(f"[FTP] OK {remote_path} -> {dest.name}")
        return True
    except Exception as e:
        # Alguns servidores no Windows aceitam só path sem barra inicial
        if remote_path.startswith("/"):
            try:
                with open(dest, "wb") as f:
                    ftp.retrbinary(f"RETR {remote_path[1:]}", f.write)
                print(f"[FTP] OK {remote_path[1:]} -> {dest.name}")
                return True
            except Exception:
                pass
        print(f"[FTP] ERRO {remote_path}: {e}")
        return False


def find_dbc_files_on_ftp(yymm: str) -> list[tuple[str, str]]:
    """Retorna lista [(dir, filename), ...] para LT??<yymm>.dbc."""
    patt = re.compile(rf"^LT([A-Z]{{2}}){re.escape(yymm)}\.dbc$", re.I)
    hits = []
    try:
        with ftplib.FTP(FTP_HOST) as ftp:
            ftp.login()
            ftp.set_pasv(True)
            for d in FTP_LT_DIRS:
                names = ftp_listdir(ftp, d)
                for n in names:
                    if patt.match(n.upper()):
                        hits.append((d, n))
    except Exception as e:
        print(f"[FTP] Conexão: {e}")
    return hits


def try_ftp_direct_download(yymm: str, target_dir: Path) -> list[Path]:
    """Baixa LT??<yymm>.dbc pelo FTP usando caminho fixo (não depende de nlst)."""
    saved = []
    # Caminho que existe no DATASUS (metadados: dados até mar/2025; 2512 pode não existir)
    base = "/dissemin/publicos/CNES/200508_/Dados/LT"
    try:
        with ftplib.FTP(FTP_HOST) as ftp:
            ftp.login()
            ftp.set_pasv(True)
            for uf in UFS:
                fname = f"LT{uf}{yymm}.dbc"
                remote = f"{base}/{fname}"
                dest = target_dir / fname
                if dest.exists() and dest.stat().st_size > 0:
                    saved.append(dest)
                    continue
                if ftp_download(ftp, remote, dest):
                    saved.append(dest)
    except Exception as e:
        print(f"[FTP] Download direto: {e}")
    return saved


def try_s3_download_all(yymm: str, target_dir: Path) -> list[Path]:
    saved = []
    for uf in UFS:
        fname = f"LT{uf}{yymm}.dbc"
        ok = False
        for base in S3_DIRS:
            if not base.endswith("/"):
                base = base.rstrip("/")
            url = f"{base}/{fname}"
            dest = target_dir / fname
            if http_get(url, dest):
                saved.append(dest)
                ok = True
                break
        if not ok:
            print(f"[S3] 404 provável para {fname} nos espelhos configurados")
    return saved


def read_dbc_any(path: Path) -> pd.DataFrame | None:
    """Lê .dbc: pyreaddbc (Linux/mac) → dbc-to-dbf+dbfread (Python puro, Windows) → pysus."""
    # 1) pyreaddbc (requer compilação C; no Windows falha com unistd.h)
    try:
        import pyreaddbc
        out = pyreaddbc.read_dbc(str(path))
        return pd.DataFrame(out) if out is not None else None
    except Exception:
        pass
    # 2) dbc-to-dbf + dbfread (Python puro — funciona no Windows sem Build Tools)
    try:
        import tempfile
        from dbctodbf import DBCDecompress
        import dbfread
        tmp = Path(tempfile.gettempdir()) / (path.stem + "_" + str(path.stat().st_mtime).replace(".", "") + ".dbf")
        DBCDecompress().decompressFile(str(path), str(tmp))
        table = dbfread.DBF(str(tmp), encoding="latin-1")
        out_df = pd.DataFrame(iter(table))
        try:
            tmp.unlink(missing_ok=True)
        except Exception:
            pass
        return out_df
    except Exception:
        pass
    # 3) pysus (pode depender de pyreaddbc)
    try:
        from pysus.utilities.readdbc import read_dbc as _read
        raw = _read(str(path))
        return pd.DataFrame(raw) if raw is not None and not isinstance(raw, pd.DataFrame) else raw
    except Exception:
        pass
    try:
        from pysus.preprocessing.decompress import dbc2dbf
        import tempfile
        import dbfread
        tmp = Path(tempfile.gettempdir()) / (path.stem + ".dbf")
        dbc2dbf(str(path), str(tmp))
        table = dbfread.DBF(str(tmp), encoding="latin-1")
        return pd.DataFrame(iter(table))
    except Exception:
        pass
    return None


def pick(df: pd.DataFrame, names: list[str]) -> str | None:
    cols = {str(c).lower(): c for c in df.columns}
    for n in names:
        if n in df.columns:
            return n
        if n.lower() in cols:
            return cols[n.lower()]
    return None


def norm_code(v) -> str:
    s = str(v or "").strip()
    try:
        return str(int(s))
    except Exception:
        return s


def norm_cnes(v) -> str:
    s = re.sub(r"\D", "", str(v or ""))
    return s[:7].zfill(7) if s else ""


def build_unified_csv(dbc_paths: list[Path], out_csv: Path) -> bool:
    dfs = []
    for p in dbc_paths:
        df = read_dbc_any(p)
        if df is None or df.empty:
            print(f"[LEITURA] pulando {p.name} (sem leitor .dbc ou vazio)")
            continue
        cnes = pick(df, ["CO_CNES", "CO_UNIDADE", "CNES"])
        tipo = pick(df, ["CO_TIPO_LEITO", "TP_LEITO", "COD_TIPO_LEITO", "COD_LEITO"])
        qt = pick(df, ["QT_LEITOS", "QT_EXIST", "QT_TOTAL", "TOTAL_LEITOS"])
        if not cnes or not tipo or not qt:
            print(f"[MAP] {p.name} sem colunas essenciais; cols={list(df.columns)[:10]}")
            continue
        slim = pd.DataFrame({
            "CO_CNES": df[cnes].map(norm_cnes),
            "CO_TIPO_LEITO": df[tipo].map(norm_code),
            "QT_EXIST": pd.to_numeric(df[qt], errors="coerce").fillna(0).astype(int),
        })
        slim = slim[slim["CO_CNES"] != ""]
        dfs.append(slim)

    if not dfs:
        print("[ERRO] nenhum DBC legível; instale pyreaddbc ou pysus, ou converta manualmente para CSV.")
        return False

    out = pd.concat(dfs, ignore_index=True)
    out = out.groupby(["CO_CNES", "CO_TIPO_LEITO"], as_index=False)["QT_EXIST"].sum()
    ensure_dirs(out_csv)
    out.to_csv(out_csv, sep=";", index=False, encoding="utf-8")
    print(f"[OK] CSV unificado salvo em {out_csv} ({len(out)} linhas)")
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description="Baixa CNES LT e gera tbLeito CSV unificado")
    ap.add_argument("--snapshot", default="202512", help="Snapshot AAAAMM (ex.: 202512)")
    ap.add_argument("--yymm", default=None, help="Força YYMM no nome do arquivo (ex.: 2511). Se omitido, usa snapshot (202512→2512)")
    args = ap.parse_args()

    snap = args.snapshot.strip()
    yymm = (args.yymm or snapshot_to_yymm(snap)).strip()
    target_dir = RAW / snap
    target_dir.mkdir(parents=True, exist_ok=True)

    # 1) Tenta S3
    dbc_paths = try_s3_download_all(yymm, target_dir)

    # 2) Se S3 falhou para muitos arquivos, tenta FTP (listdir e depois download direto)
    if len(dbc_paths) < 5:
        hits = find_dbc_files_on_ftp(yymm)
        if hits:
            try:
                with ftplib.FTP(FTP_HOST) as ftp:
                    ftp.login()
                    ftp.set_pasv(True)
                    for d, name in hits:
                        remote = f"{d}/{name}"
                        dest = target_dir / name
                        if not dest.exists() or dest.stat().st_size == 0:
                            if ftp_download(ftp, remote, dest):
                                dbc_paths.append(dest)
            except Exception as e:
                print(f"[FTP] Erro ao baixar: {e}")
        if len(dbc_paths) < 5:
            direct = try_ftp_direct_download(yymm, target_dir)
            dbc_paths = list(dict.fromkeys(dbc_paths + direct))  # sem duplicar

    if not dbc_paths:
        print(f"[ERRO] nenhum LT??*.dbc foi baixado para {yymm}.")
        print(f"       DATASUS pode ter dados até mar/2025. Tente um mês anterior:")
        print(f"       python scripts/download_rlEstabLeito.py --snapshot 202511")
        print(f"       Ou use FTP manual / CSV de outra fonte e salve como data/tbLeito{snap}.csv")
        return 2

    # 3) Tenta ler e unificar para CSV
    out_csv = DATA / OUT_CSV.format(snap=snap)
    ok = build_unified_csv(dbc_paths, out_csv)
    if not ok:
        print(f"[INFO] .dbc baixados em {target_dir}. Instale pyreaddbc ou pysus para converter, ou converta manualmente e salve como {out_csv}.")
        return 3

    return 0


if __name__ == "__main__":
    sys.exit(main())
