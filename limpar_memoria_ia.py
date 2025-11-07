# -*- coding: utf-8 -*-
"""Script para limpar toda a memória da IA (conversas e informações pessoais)"""
import os
import sys
import sqlite3

# Configura encoding UTF-8 para Windows
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass

# Caminho do banco de dados
DB_PATH = os.path.join(os.path.dirname(__file__), "backend", "users.db")

print("=" * 60)
print("LIMPAR MEMORIA DA IA")
print("=" * 60)

if not os.path.exists(DB_PATH):
    print(f"\nERRO: Banco de dados nao encontrado em: {DB_PATH}")
    sys.exit(1)

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Conta registros antes de apagar
    cursor.execute('SELECT COUNT(*) FROM conversas')
    conversas_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM user_info')
    info_count = cursor.fetchone()[0]
    
    print(f"\nRegistros encontrados:")
    print(f"  - Conversas: {conversas_count}")
    print(f"  - Informacoes pessoais: {info_count}")
    
    if conversas_count == 0 and info_count == 0:
        print("\nNenhum registro encontrado. Memoria ja esta limpa!")
        conn.close()
        sys.exit(0)
    
    # Limpa todas as conversas (sem confirmação - execução direta)
    print("\n" + "=" * 60)
    print("Apagando memoria da IA...")
    
    # Limpa todas as conversas
    cursor.execute('DELETE FROM conversas')
    conversas_apagadas = cursor.rowcount
    
    # Limpa todas as informações pessoais
    cursor.execute('DELETE FROM user_info')
    info_apagadas = cursor.rowcount
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 60)
    print("OK: MEMORIA DA IA LIMPA COM SUCESSO!")
    print("=" * 60)
    print(f"  - Conversas apagadas: {conversas_apagadas}")
    print(f"  - Informacoes pessoais apagadas: {info_apagadas}")
    print("\nNOTA: A memoria em tempo de execucao (variavel 'conversas')")
    print("sera limpa quando o servidor Flask for reiniciado.")
    print("Ou use a rota /api/limpar-memoria-ia para limpar tambem a memoria em tempo de execucao.")
    
except Exception as e:
    print(f"\nERRO ao limpar memoria: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

