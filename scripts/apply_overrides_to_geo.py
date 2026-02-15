#!/usr/bin/env python3
"""Aplica overrides do CNES em massa no Parquet geo, normalizando esfera e SUS."""
from __future__ import annotations
import os
import re
import sys
from pathlib import Path
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

BASE = Path(__file__).resolve().parent.parent
GEO_DIR = BASE / "data" / "geo"
SRC = GEO_DIR / "hospitals_geo.parquet"
SRC_MIN = GEO_DIR / "hospitals_geo.min.parquet"
DST = GEO_DIR / "hospitals_geo.parquet"
DST_MIN = GEO_DIR / "hospitals_geo.min.parquet"

# Adiciona caminhos ao sys.path para importar backend
backend_path = str(BASE / "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))


def _norm7(v):
    """Normaliza CNES para 7 dígitos."""
    s = re.sub(r"\D", "", str(v or ""))
    return (s[:7] if len(s) >= 7 else s).zfill(7) if s else ""


def _normalize_esfera(esfera_raw: str | None, nome: str | None) -> str:
    """Normaliza esfera para um dos 3 valores válidos."""
    e = (esfera_raw or "").strip()
    if e in ("Público", "Privado", "Filantrópico"):
        return e
    n = (nome or "").lower()
    if re.search(r"\b(municip|mun\.|h\s+mun|estad|federal|prefeit|sec\.\s*sa[úu]de|secretaria)\b", n):
        return "Público"
    if re.search(r"santa casa|filantr|beneficen|misericord|irmandade|fund(a|ação|acao)", n):
        return "Filantrópico"
    return "Privado"  # política: fallback visual


def _sus_from(esfera: str | None, sus_badge_raw: str | None) -> str:
    """Deriva badge SUS a partir de esfera e sus_badge_raw."""
    s = (sus_badge_raw or "").strip()
    if s in ("Aceita Cartão SUS", "Não atende SUS"):
        return s
    if esfera == "Público":
        return "Aceita Cartão SUS"
    return ""  # sem badge


def main():
    # Fonte (min se não existir full)
    src = SRC if SRC.exists() else SRC_MIN
    if not src.exists():
        print(f"[ERRO] {src} não encontrado")
        return 1

    print(f"[INFO] Lendo {src}...")
    df = pd.read_parquet(src)
    print(f"[INFO] Carregado {len(df)} linhas")

    # Boot overrides
    get_overrides = None
    try:
        # Tenta importar de diferentes formas
        try:
            from backend.startup.cnes_overrides import ensure_boot, get_overrides
        except ImportError:
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location(
                    "cnes_overrides",
                    BASE / "backend" / "startup" / "cnes_overrides.py"
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    ensure_boot = module.ensure_boot
                    get_overrides = module.get_overrides
            except Exception:
                pass
        
        if get_overrides:
            ensure_boot()
            print("[INFO] Overrides carregados")
        else:
            raise ImportError("Não foi possível importar cnes_overrides")
    except Exception as e:
        print(f"[AVISO] Erro ao carregar overrides: {e}")
        print("[INFO] Continuando sem overrides (só normalização)")
        print("[INFO] Overrides serão aplicados apenas via normalização por nome")

    # Aplica overrides
    df = df.copy()
    if "cnes_id" not in df.columns:
        print("[ERRO] coluna cnes_id ausente")
        return 2

    df["cnes_id_norm"] = df["cnes_id"].map(_norm7)

    esfera_new = []
    sus_new = []
    conv_new = []

    print("[INFO] Aplicando overrides e normalizando...")
    for idx, r in df.iterrows():
        nome = r.get("display_name") or r.get("nome")
        esfera = _normalize_esfera(r.get("esfera"), nome)
        sus = _sus_from(esfera, r.get("sus_badge"))
        # Trata convenios (pode ser array NumPy, lista ou None)
        convs_raw = r.get("convenios")
        if convs_raw is None:
            convs = []
        elif isinstance(convs_raw, (list, tuple)):
            convs = list(convs_raw)
        elif hasattr(convs_raw, 'tolist'):  # Array NumPy
            try:
                convs = convs_raw.tolist()
            except Exception:
                convs = []
        elif hasattr(convs_raw, '__len__'):
            # Outro tipo iterável
            try:
                convs = list(convs_raw) if len(convs_raw) > 0 else []
            except Exception:
                convs = []
        else:
            convs = []

        if get_overrides:
            try:
                # Tenta com CNES normalizado e também com o original
                ovr = get_overrides(r["cnes_id_norm"]) or get_overrides(str(r.get("cnes_id") or ""))
                if ovr:
                    esfera_ovr = ovr.get("esfera")
                    if esfera_ovr:
                        esfera = _normalize_esfera(esfera_ovr, nome)
                    sus_ovr = ovr.get("sus_badge")
                    if sus_ovr:
                        sus = sus_ovr
                    else:
                        sus = _sus_from(esfera, sus)
                    convs_ovr = ovr.get("convenios")
                    if convs_ovr:
                        convs = convs_ovr
            except Exception:
                pass  # Continua sem override se falhar

        esfera_new.append(esfera)
        sus_new.append(sus)
        conv_new.append(convs)

        if (idx + 1) % 1000 == 0:
            print(f"[INFO] Processado {idx + 1}/{len(df)} linhas...")

    df["esfera"] = esfera_new
    df["sus_badge"] = sus_new
    df["convenios"] = conv_new
    df.drop(columns=["cnes_id_norm"], errors="ignore", inplace=True)

    # Salva full (se existia)
    if SRC.exists():
        df.to_parquet(DST, index=False)
        print(f"[OK] Regravado {DST} ({len(df)} linhas)")

    # Salva min
    cols = [
        "cnes_id", "nome", "display_name", "esfera", "sus_badge", "convenios",
        "has_maternity", "is_probable", "score",
        "telefone", "telefone_formatado", "phone_e164",
        "endereco", "lat", "lon", "municipio", "uf"
    ]
    cols = [c for c in cols if c in df.columns]
    table = pa.Table.from_pandas(df[cols], preserve_index=False)
    pq.write_table(
        table, DST_MIN,
        compression="zstd",
        compression_level=9,
        use_dictionary=True
    )
    print(f"[OK] Salvo {DST_MIN} ({len(df)} linhas)")

    # Estatísticas
    esfera_counts = pd.Series(esfera_new).value_counts()
    print("\n[ESTATÍSTICAS] Distribuição de esfera:")
    for esfera, count in esfera_counts.items():
        print(f"  {esfera}: {count}")

    sus_counts = pd.Series([s for s in sus_new if s]).value_counts()
    if len(sus_counts) > 0:
        print("\n[ESTATÍSTICAS] Distribuição de SUS badge:")
        for sus, count in sus_counts.items():
            print(f"  {sus}: {count}")

    print("\n[OK] Processo concluído!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
