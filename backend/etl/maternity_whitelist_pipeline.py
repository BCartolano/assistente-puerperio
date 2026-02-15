#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pipeline White List de Maternidades – Modo Flexível
Se rlEstabLeito não for encontrado, roda em contingência (apenas Serviços de Urgência).
Execute: python backend/etl/maternity_whitelist_pipeline.py (a partir da raiz do projeto)
"""

import json
import os
import numpy as np
import pandas as pd

# Raiz do projeto (backend/etl -> ../..)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))

SEARCH_PATHS = [
    os.path.join(BASE_DIR, "backend", "data", "raw"),
    os.path.join(BASE_DIR, "data"),
    os.path.join(BASE_DIR, "BASE_DE_DADOS_CNES_202512"),
    os.path.join(BASE_DIR, "data", "raw"),
    r"C:\Users\bruno\OneDrive\Documentos\chatbot-puerperio\BASE_DE_DADOS_CNES_202512",
    r"C:\Users\bruno\OneDrive\Documentos\chatbot-puerperio\data",
]


def find_file(keyword, exclude=None):
    for path in SEARCH_PATHS:
        full_path = os.path.abspath(path)
        if os.path.exists(full_path):
            try:
                files = os.listdir(full_path)
                for f in files:
                    if keyword.lower() in f.lower():
                        if exclude and exclude.lower() in f.lower():
                            continue
                        if f.endswith(".csv") or f.endswith(".txt") or "." not in f:
                            return os.path.join(full_path, f)
            except OSError:
                continue
    return None


def get_col_name(df, candidates):
    columns = [c.upper().strip() for c in df.columns]
    for cand in candidates:
        if cand.upper() in columns:
            return df.columns[columns.index(cand.upper())]
    return None


def run_pipeline():
    print("--- INICIANDO PIPELINE (MODO FLEXÍVEL) ---")

    file_estab = find_file("tbEstabelecimento")
    file_serv = find_file("rlEstabServClass")

    file_leito = find_file("rlEstabLeito")
    if not file_leito:
        file_leito = find_file("Leito", exclude="tbLeito")

    if not file_estab or not file_serv:
        print("ERRO FATAL: Faltando tbEstabelecimento ou rlEstabServClass.")
        return

    try:
        # --- PROCESSAMENTO DE SERVIÇOS (CRÍTICO) ---
        print(f"\n1. Lendo Serviços: {os.path.basename(file_serv)}")
        df_serv = pd.read_csv(file_serv, sep=";", encoding="latin1", dtype=str, on_bad_lines="skip")

        col_cnes_serv = get_col_name(df_serv, ["CO_UNIDADE", "CO_CNES", "CNES"])
        col_serv = get_col_name(df_serv, ["CO_SERVICO", "CO_SERVICO_ESPECIALIZADO"])
        col_class = get_col_name(df_serv, ["CO_CLASSIFICACAO", "CO_CLASS"])

        if not all([col_cnes_serv, col_serv, col_class]):
            print(f"ERRO: Colunas inválidas em Serviços. {df_serv.columns.tolist()}")
            return

        emergency_ids = df_serv[
            (df_serv[col_serv] == "125") & (df_serv[col_class] == "001")
        ][col_cnes_serv].unique()
        print(f"-> Hospitais com Urgência Obstétrica: {len(emergency_ids)}")

        # --- PROCESSAMENTO DE LEITOS (OPCIONAL) ---
        bed_ids = np.array([], dtype=object)
        nicu_ids = np.array([], dtype=object)

        if file_leito:
            print(f"\n2. Lendo Leitos: {os.path.basename(file_leito)}")
            df_leito = pd.read_csv(
                file_leito, sep=";", encoding="latin1", dtype=str, on_bad_lines="skip"
            )
            col_cnes_leito = get_col_name(df_leito, ["CO_UNIDADE", "CO_CNES"])
            col_cod_leito = get_col_name(df_leito, ["CO_LEITO", "COD_LEITO"])
            col_qtd = get_col_name(
                df_leito, ["QT_EXISTENTE", "QT_EXIST", "QTD_EXISTENTE", "NU_QUANTIDADE"]
            )

            if col_cnes_leito and col_cod_leito and col_qtd:
                df_leito[col_qtd] = pd.to_numeric(df_leito[col_qtd], errors="coerce").fillna(0)
                df_active = df_leito[df_leito[col_qtd] > 0]

                bed_ids = df_active[
                    df_active[col_cod_leito].isin(["01", "02", "10", "46"])
                ][col_cnes_leito].unique()
                nicu_ids = df_active[
                    df_active[col_cod_leito].isin(["10", "46"])
                ][col_cnes_leito].unique()
                print(f"-> Hospitais com Leitos confirmados: {len(bed_ids)}")
            else:
                print("AVISO: Arquivo de leitos inválido. Ignorando leitos.")
        else:
            print("\nAVISO: Arquivo 'rlEstabLeito' não encontrado.")
            print("-> RODANDO EM MODO DE CONTINGÊNCIA (Baseado apenas em Serviços de Urgência).")
            bed_ids = emergency_ids

        # --- CRUZAMENTO ---
        if len(bed_ids) > 0 and file_leito:
            whitelist_ids = np.intersect1d(emergency_ids, bed_ids)
        else:
            whitelist_ids = emergency_ids

        print(f"\n-> LISTA FINAL: {len(whitelist_ids)} Maternidades.")

        # --- GEO ---
        print(f"\n3. Lendo Dados Cadastrais: {os.path.basename(file_estab)}")
        df_estab = pd.read_csv(
            file_estab, sep=";", encoding="latin1", dtype=str, on_bad_lines="skip"
        )

        map_cols = {
            "id": get_col_name(df_estab, ["CO_UNIDADE", "CO_CNES", "CNES"]),
            "name": get_col_name(df_estab, ["NO_FANTASIA", "NOME_FANTASIA"]),
            "lat": get_col_name(df_estab, ["NU_LATITUDE", "LATITUDE"]),
            "long": get_col_name(df_estab, ["NU_LONGITUDE", "LONGITUDE"]),
            "logradouro": get_col_name(df_estab, ["NO_LOGRADOURO", "LOGRADOURO"]),
            "numero": get_col_name(df_estab, ["NU_ENDERECO", "NUMERO"]),
            "telefone": get_col_name(df_estab, ["NU_TELEFONE", "TELEFONE"]),
        }

        if not (map_cols["id"] and map_cols["lat"] and map_cols["long"]):
            print("ERRO: Colunas de ID ou Latitude/Longitude não encontradas no Estabelecimento.")
            print(f"Colunas disponíveis: {df_estab.columns.tolist()}")
            return

        final_df = df_estab[
            df_estab[map_cols["id"]].astype(str).str.strip().isin(
                pd.Series(whitelist_ids).astype(str).str.strip()
            )
        ].copy()
        final_df["clean_lat"] = pd.to_numeric(final_df[map_cols["lat"]], errors="coerce")
        final_df["clean_long"] = pd.to_numeric(final_df[map_cols["long"]], errors="coerce")

        final_df = final_df.dropna(subset=["clean_lat", "clean_long"])
        final_df = final_df[(final_df["clean_lat"] != 0) & (final_df["clean_long"] != 0)]

        print(f"-> Com Geolocalização Válida: {len(final_df)}")

        nicu_set = set(pd.Series(nicu_ids).astype(str).str.strip())

        # --- GERAÇÃO GEOJSON ---
        features = []
        for _, row in final_df.iterrows():
            cnes_id = str(row[map_cols["id"]]).strip()
            try:
                logr = (
                    str(row[map_cols["logradouro"]])
                    if map_cols["logradouro"] and pd.notna(row.get(map_cols["logradouro"]))
                    else ""
                )
                num = (
                    str(row[map_cols["numero"]])
                    if map_cols["numero"] and pd.notna(row.get(map_cols["numero"]))
                    else ""
                )
                full_address = f"{logr}, {num}".strip().strip(",")
            except Exception:
                full_address = "Endereço não informado"

            name_val = (
                str(row[map_cols["name"]])
                if map_cols["name"] and pd.notna(row.get(map_cols["name"]))
                else "Sem Nome"
            )
            if name_val == "nan" or not name_val.strip():
                name_val = "Sem Nome"

            phone_val = (
                str(row[map_cols["telefone"]])
                if map_cols["telefone"] and pd.notna(row.get(map_cols["telefone"]))
                else ""
            )
            if phone_val == "nan":
                phone_val = ""

            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(row["clean_long"]), float(row["clean_lat"])],
                },
                "properties": {
                    "id": cnes_id,
                    "name": name_val,
                    "address": full_address,
                    "phone": phone_val,
                    "has_nicu": cnes_id in nicu_set,
                    "accepts_sus": True,
                    "private_only": False,
                },
            }
            features.append(feature)

        geojson = {"type": "FeatureCollection", "features": features}

        output_path = os.path.join(BASE_DIR, "backend", "data", "maternities_whitelist.geojson")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(geojson, f, ensure_ascii=False, indent=2)

        print(f"\nSUCESSO! GeoJSON gerado em: {output_path}")

    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_pipeline()
