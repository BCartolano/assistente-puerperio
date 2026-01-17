#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar criação e escrita nos arquivos de log
"""
import os
import sys

# Adiciona caminho do backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_log_files():
    """Testa criação e escrita nos arquivos de log"""
    
    # Cria pasta logs se não existir
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logs_dir = os.path.join(project_dir, 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    log_files = [
        'error_debug.log',
        'context_metrics.log',
        'user_feedback.log'
    ]
    
    print("=" * 60)
    print("TESTE: Criacao e Permissoes de Arquivos de Log")
    print("=" * 60)
    print(f"Pasta logs: {logs_dir}\n")
    
    results = []
    
    for log_file in log_files:
        log_path = os.path.join(logs_dir, log_file)
        
        # Verifica se arquivo existe
        exists = os.path.exists(log_path)
        
        # Tenta criar/escrever no arquivo
        writable = False
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(f"# Teste de escrita - {os.path.basename(__file__)}\n")
                f.flush()
            writable = True
            test_size = os.path.getsize(log_path)
        except Exception as e:
            test_size = 0
            error_msg = str(e)
        
        # Obtém permissões (Windows)
        try:
            import stat
            file_stat = os.stat(log_path)
            readable = bool(file_stat.st_mode & stat.S_IRUSR)
            writable_check = bool(file_stat.st_mode & stat.S_IWUSR)
        except:
            readable = True
            writable_check = True
        
        results.append({
            'file': log_file,
            'exists': exists,
            'writable': writable,
            'size': test_size,
            'path': log_path
        })
        
        status = "[OK]" if (exists and writable) else "[ERRO]"
        print(f"{status} {log_file}")
        print(f"   Existe: {exists}")
        print(f"   Gravavel: {writable}")
        print(f"   Tamanho: {test_size} bytes")
        print(f"   Caminho: {log_path}\n")
    
    print("=" * 60)
    
    # Resumo
    all_ok = all(r['exists'] and r['writable'] for r in results)
    
    if all_ok:
        print("[OK] TODOS OS ARQUIVOS DE LOG ESTAO FUNCIONANDO CORRETAMENTE")
        print("\nOs arquivos serao criados automaticamente pelo backend quando necessario.")
    else:
        print("[ERRO] ALGUNS ARQUIVOS TEM PROBLEMAS")
        print("\nVerifique permissoes da pasta 'logs' e tente novamente.")
    
    return all_ok

if __name__ == '__main__':
    success = test_log_files()
    sys.exit(0 if success else 1)
