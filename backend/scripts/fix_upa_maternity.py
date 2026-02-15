#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correção: UPAs não podem ter maternidade
Purpose: Corrigir UPAs incorretamente marcadas com has_maternity=1
"""

import os
import sys
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'cnes_cache.db')

def fix_upa_maternity():
    """Corrige UPAs marcadas incorretamente com maternidade"""
    print("="*70)
    print("CORRECAO: UPAs NAO PODEM TER MATERNIDADE")
    print("="*70)
    print()
    
    if not os.path.exists(DB_PATH):
        print(f"[ERRO] Banco de dados nao encontrado: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Encontrar UPAs com maternidade
    cursor.execute("""
        SELECT cnes_id, name, fantasy_name, tipo_unidade, has_maternity
        FROM hospitals_cache
        WHERE tipo_unidade IN ('73', 'UPA')
          AND has_maternity = 1
    """)
    
    upas_incorretas = cursor.fetchall()
    
    if not upas_incorretas:
        print("[OK] Nenhuma UPA marcada incorretamente com maternidade")
        conn.close()
        return
    
    print(f"[ERRO] Encontradas {len(upas_incorretas)} UPAs marcadas incorretamente:")
    for row in upas_incorretas:
        nome = row[1] or row[2] or 'Sem nome'
        print(f"   - {nome} (CNES: {row[0]}, Tipo: {row[3]})")
    
    print("\n[INFO] Corrigindo...")
    
    # Corrigir: UPAs nunca têm maternidade
    cursor.execute("""
        UPDATE hospitals_cache
        SET has_maternity = 0
        WHERE tipo_unidade IN ('73', 'UPA')
          AND has_maternity = 1
    """)
    
    rows_updated = cursor.rowcount
    conn.commit()
    
    print(f"[OK] {rows_updated} UPAs corrigidas (has_maternity = 0)")
    
    # Verificar correção
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM hospitals_cache 
        WHERE tipo_unidade IN ('73', 'UPA')
          AND has_maternity = 1
    """)
    upas_restantes = cursor.fetchone()[0]
    
    if upas_restantes == 0:
        print("[OK] Correcao validada: Nenhuma UPA com maternidade")
    else:
        print(f"[ERRO] Ainda ha {upas_restantes} UPAs com maternidade!")
    
    conn.close()
    print("\n[OK] Correcao concluida!")

if __name__ == "__main__":
    fix_upa_maternity()
