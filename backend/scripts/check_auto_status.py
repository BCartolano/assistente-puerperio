#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar Status do Modo Automático
Purpose: Mostrar progresso da validação automática
"""

import os
import sys
import json
from datetime import datetime

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    os.environ['PYTHONIOENCODING'] = 'utf-8'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATE_FILE = os.path.join(BASE_DIR, 'backend', 'scripts', 'auto_validation_state.json')
LOG_FILE = os.path.join(BASE_DIR, 'backend', 'scripts', 'auto_validation_log.json')

def main():
    print("=" * 80)
    print("STATUS DO MODO AUTOMÁTICO")
    print("=" * 80)
    print()
    
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        print("📊 ESTATÍSTICAS:")
        print(f"   Processados: {state.get('processed_count', 0)}")
        print(f"   Corrigidos: {state.get('fixed_count', 0)}")
        print(f"   Último CNES: {state.get('last_cnes_id', 'N/A')}")
        if 'last_update' in state:
            last_update = datetime.fromisoformat(state['last_update'])
            print(f"   Última atualização: {last_update.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
    else:
        print("⚠️  Estado não encontrado - Modo automático ainda não iniciado")
        print()
    
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            logs = json.load(f)
        
        print(f"📝 LOGS: {len(logs)} entradas")
        
        # Últimas 10 ações
        recent_logs = logs[-10:] if len(logs) > 10 else logs
        print()
        print("Últimas ações:")
        for log in recent_logs:
            timestamp = datetime.fromisoformat(log['timestamp']).strftime('%H:%M:%S')
            action = log['action']
            details = log.get('details', {})
            if action == 'removed':
                name = details.get('name', 'N/A')
                print(f"   [{timestamp}] 🚫 REMOVIDO: {name}")
            elif action == 'pending':
                name = details.get('name', 'N/A')
                print(f"   [{timestamp}] ⚠️  PENDENTE: {name}")
            elif action == 'error':
                error = details.get('error', 'N/A')
                print(f"   [{timestamp}] ❌ ERRO: {error}")
    else:
        print("📝 LOGS: Nenhum log encontrado ainda")
    
    print()
    print("=" * 80)

if __name__ == '__main__':
    main()
