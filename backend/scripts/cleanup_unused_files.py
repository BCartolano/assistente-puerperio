#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Limpeza de Arquivos Desnecessários
Purpose: Identificar e remover arquivos não utilizados no projeto
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Set

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    os.environ['PYTHONIOENCODING'] = 'utf-8'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPORT_FILE = os.path.join(BASE_DIR, 'backend', 'scripts', 'unused_files_report.json')

# Arquivos/diretórios essenciais (NÃO remover)
ESSENTIAL_PATTERNS = [
    'backend/api/',
    'backend/services/',
    'backend/etl/',
    'backend/static/',
    'backend/templates/',
    'backend/app.py',
    'backend/cnes_cache.db',
    'requirements.txt',
    '.git/',
    '.cursor/',
    'node_modules/',
    'venv/',
    'env/',
    '__pycache__/',
    '.pyc',
    'package.json',
    'package-lock.json',
]

# Arquivos que podem ser removidos (scripts temporários antigos)
POTENTIALLY_UNUSED = [
    '*.tmp',
    '*.bak',
    '*.old',
    '*.log',  # Exceto logs importantes
    '*.swp',
    '*.swo',
    '*~',
    '.DS_Store',
    'Thumbs.db',
]

# Diretórios de dados grandes que podem ser limpos (com cuidado)
DATA_DIRS_TO_CHECK = [
    'BASE_DE_DADOS_CNES_202512',  # CSV original (já importado)
]

def find_unused_files() -> List[Dict]:
    """Encontra arquivos potencialmente não utilizados"""
    unused = []
    
    # Procurar arquivos temporários
    for pattern in POTENTIALLY_UNUSED:
        for file_path in Path(BASE_DIR).rglob(pattern):
            rel_path = str(file_path.relative_to(BASE_DIR))
            # Verificar se não é essencial
            if not any(ess in rel_path for ess in ESSENTIAL_PATTERNS):
                unused.append({
                    'path': rel_path,
                    'type': 'temporary_file',
                    'size': file_path.stat().st_size if file_path.exists() else 0
                })
    
    # Verificar scripts de teste temporários
    scripts_dir = Path(BASE_DIR) / 'backend' / 'scripts'
    if scripts_dir.exists():
        for script_file in scripts_dir.glob('*.py'):
            # Scripts de teste/check que podem ser removidos após uso
            if any(keyword in script_file.name.lower() for keyword in ['check_', 'test_', 'temp_', 'debug_']):
                # Verificar se é realmente temporário (não usado em outros lugares)
                rel_path = str(script_file.relative_to(BASE_DIR))
                unused.append({
                    'path': rel_path,
                    'type': 'temporary_script',
                    'size': script_file.stat().st_size
                })
    
    return unused

def find_large_unused_data() -> List[Dict]:
    """Encontra dados grandes que podem ser limpos"""
    large_files = []
    
    # Verificar diretório de dados CSV (já importado)
    data_dir = Path(BASE_DIR) / 'BASE_DE_DADOS_CNES_202512'
    if data_dir.exists():
        for csv_file in data_dir.rglob('*.csv*'):
            size_mb = csv_file.stat().st_size / (1024 * 1024)
            if size_mb > 10:  # Arquivos maiores que 10MB
                large_files.append({
                    'path': str(csv_file.relative_to(BASE_DIR)),
                    'size_mb': round(size_mb, 2),
                    'type': 'large_csv_data',
                    'note': 'CSV já importado no banco - pode ser removido se espaço for necessário'
                })
    
    return large_files

def main():
    print("=" * 80)
    print("LIMPEZA DE ARQUIVOS DESNECESSÁRIOS")
    print("=" * 80)
    print()
    
    print("🔍 Procurando arquivos temporários...")
    unused_files = find_unused_files()
    print(f"   Encontrados: {len(unused_files)}")
    
    print("🔍 Procurando dados grandes não utilizados...")
    large_data = find_large_unused_data()
    print(f"   Encontrados: {len(large_data)}")
    
    total_size_mb = sum(f.get('size_mb', 0) for f in large_data)
    
    print()
    print("=" * 80)
    print("RESUMO")
    print("=" * 80)
    print(f"📁 Arquivos temporários: {len(unused_files)}")
    print(f"💾 Dados grandes: {len(large_data)} ({total_size_mb:.2f} MB)")
    print()
    
    # Salvar relatório (NÃO remover automaticamente - requer confirmação)
    report = {
        'timestamp': datetime.now().isoformat(),
        'unused_files': unused_files,
        'large_data': large_data,
        'total_size_mb': total_size_mb,
        'note': 'Arquivos identificados mas NÃO removidos automaticamente. Revisar manualmente antes de remover.'
    }
    
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Relatório salvo em: {REPORT_FILE}")
    print()
    print("⚠️  NOTA: Arquivos identificados mas NÃO removidos automaticamente")
    print("   Revisar relatório antes de remover qualquer arquivo")
    print()
    
    if unused_files:
        print("📁 ARQUIVOS TEMPORÁRIOS ENCONTRADOS (primeiros 10):")
        for f in unused_files[:10]:
            print(f"   {f['path']} ({f.get('size', 0)} bytes)")
    
    if large_data:
        print()
        print("💾 DADOS GRANDES ENCONTRADOS:")
        for f in large_data[:5]:
            print(f"   {f['path']} ({f['size_mb']} MB)")

if __name__ == '__main__':
    main()
