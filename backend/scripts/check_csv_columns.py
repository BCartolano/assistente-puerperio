#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script rápido para verificar colunas do CSV"""

import csv

CSV_PATH = 'data/tbEstabelecimento202512.csv.csv'

with open(CSV_PATH, 'r', encoding='utf-8', errors='ignore') as f:
    reader = csv.DictReader(f, delimiter=';')
    
    # Primeira linha
    row = next(reader)
    
    print("Colunas com 'TIPO' no nome:")
    for k in row.keys():
        if 'TIPO' in k.upper():
            print(f"  - {k}: valor='{row[k][:30] if row[k] else 'VAZIO'}'")
    
    print("\nPrimeiras 20 colunas e valores:")
    for i, (k, v) in enumerate(list(row.items())[:20]):
        print(f"  {i+1}. {k}: '{v[:30] if v else 'VAZIO'}'")
    
    # Verificar algumas linhas
    print("\nVerificando 5 linhas para CO_TIPO_UNIDADE:")
    count = 0
    for row in reader:
        count += 1
        tipo = row.get('CO_TIPO_UNIDADE', '')
        cnes = row.get('CO_CNES', '')
        print(f"  Linha {count+1}: CNES={cnes[:10]}, Tipo={tipo[:10] if tipo else 'VAZIO'}")
        if count >= 4:
            break
