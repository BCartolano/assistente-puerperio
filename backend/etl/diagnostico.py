"""
Diagnóstico: lê cabeçalhos dos CSVs do CNES em BASE_DE_DADOS_CNES_202512
e mostra separador, colunas e colunas-chave (CNES, SERVICO, CLASSIFICACAO, LEITO, etc.).
Execute: python backend/etl/diagnostico.py
"""

import os
import glob
import pandas as pd


def analyze_file(file_path):
    filename = os.path.basename(file_path)
    print(f"\n{'='*60}")
    print(f"LENDO: {filename}")

    try:
        with open(file_path, "r", encoding="latin1", errors="replace") as f:
            first_line = f.readline()
            if ";" in first_line:
                sep = ";"
            else:
                sep = ","

        print(f"-> Separador detectado: '{sep}'")

        df = pd.read_csv(file_path, sep=sep, encoding="latin1", dtype=str, nrows=2)
        cols = df.columns.tolist()

        print(f"-> Colunas encontradas ({len(cols)}): {cols[:5]} ...")

        keywords = ["CNES", "SERVICO", "CLASSIFICACAO", "LEITO", "COMPETENCIA", "LATITUDE"]
        found = [col for col in cols if any(k in col.upper() for k in keywords)]
        print(f"-> Colunas Chave Identificadas: {found}")

    except Exception as e:
        print(f"-> Erro ao ler: {e}")


def main():
    base_path = r"C:\Users\bruno\OneDrive\Documentos\chatbot-puerperio\BASE_DE_DADOS_CNES_202512"

    print(f"Procurando na pasta: {base_path}")

    if not os.path.exists(base_path):
        print("ERRO: A pasta não foi encontrada. Verifique o caminho.")
        return

    all_files = glob.glob(os.path.join(base_path, "*"))

    targets = ["Estabelecimento", "ServClass", "Leito", "AtendPrest"]

    count = 0
    for f in all_files:
        name = os.path.basename(f)
        if any(t in name for t in targets):
            analyze_file(f)
            count += 1

    if count == 0:
        print(
            "\nNenhum arquivo relevante encontrado. Verifique se os nomes batem com: Estabelecimento, ServClass, Leito, AtendPrest"
        )


if __name__ == "__main__":
    main()
