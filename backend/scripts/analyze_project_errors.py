#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise de Erros e Arquivos Desnecessários do Projeto
Purpose: Identificar erros no código e arquivos não utilizados
"""

import os
import sys
import ast
import json
from pathlib import Path
from typing import List, Dict, Set
from datetime import datetime

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    os.environ['PYTHONIOENCODING'] = 'utf-8'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPORT_FILE = os.path.join(BASE_DIR, 'backend', 'scripts', 'project_analysis_report.json')

# Arquivos que devem existir (não remover)
ESSENTIAL_FILES = {
    'backend/api/main.py',
    'backend/api/routes.py',
    'backend/api/models.py',
    'backend/services/facility_service.py',
    'backend/etl/data_ingest.py',
    'backend/app.py',
    'backend/static/js/chat.js',
    'backend/static/css/style.css',
    'requirements.txt',
}

# Extensões de arquivos importantes
IMPORTANT_EXTENSIONS = {'.py', '.js', '.jsx', '.css', '.html', '.json', '.txt', '.md', '.sql', '.db'}

def find_unused_files() -> List[str]:
    """Encontra arquivos potencialmente não utilizados"""
    unused = []
    
    # Procurar arquivos .py que não são importados
    python_files = list(Path(BASE_DIR).rglob('*.py'))
    imported_modules: Set[str] = set()
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)
                
                # Coletar imports
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imported_modules.add(alias.name.split('.')[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imported_modules.add(node.module.split('.')[0])
        except:
            pass
    
    # Verificar arquivos que podem não estar sendo usados
    for py_file in python_files:
        rel_path = str(py_file.relative_to(BASE_DIR))
        module_name = py_file.stem
        
        # Pular arquivos essenciais
        if any(rel_path.startswith(ess) for ess in ESSENTIAL_FILES):
            continue
        
        # Pular __init__.py e arquivos de teste
        if '__init__' in module_name or 'test' in module_name.lower():
            continue
        
        # Verificar se é importado
        if module_name not in imported_modules and 'script' not in rel_path.lower():
            # Verificar se é realmente usado (buscar referências)
            is_referenced = False
            for other_file in python_files:
                if other_file == py_file:
                    continue
                try:
                    with open(other_file, 'r', encoding='utf-8') as f:
                        if module_name in f.read():
                            is_referenced = True
                            break
                except:
                    pass
            
            if not is_referenced:
                unused.append(rel_path)
    
    return unused

def find_syntax_errors() -> List[Dict]:
    """Encontra erros de sintaxe Python"""
    errors = []
    python_files = list(Path(BASE_DIR).rglob('*.py'))
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            ast.parse(content)
        except SyntaxError as e:
            errors.append({
                'file': str(py_file.relative_to(BASE_DIR)),
                'line': e.lineno,
                'message': e.msg,
                'text': e.text
            })
        except Exception as e:
            # Outros erros de parsing
            pass
    
    return errors

def find_potential_issues() -> List[Dict]:
    """Encontra problemas potenciais no código"""
    issues = []
    python_files = list(Path(BASE_DIR).rglob('*.py'))
    
    for py_file in python_files:
        rel_path = str(py_file.relative_to(BASE_DIR))
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines, 1):
                # Verificar imports não usados (heurística simples)
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    # Verificar se é usado no resto do arquivo
                    import_name = line.split()[1].split('.')[0] if 'import' in line else None
                    if import_name:
                        rest_of_file = ''.join(lines[i:])
                        if import_name not in rest_of_file and import_name not in ['os', 'sys', 'json', 'datetime']:
                            issues.append({
                                'file': rel_path,
                                'line': i,
                                'type': 'unused_import',
                                'message': f'Possível import não usado: {line.strip()}'
                            })
                
                # Verificar TODO/FIXME
                if 'TODO' in line or 'FIXME' in line or 'XXX' in line:
                    issues.append({
                        'file': rel_path,
                        'line': i,
                        'type': 'todo',
                        'message': line.strip()
                    })
        except Exception as e:
            issues.append({
                'file': rel_path,
                'type': 'read_error',
                'message': f'Erro ao ler arquivo: {str(e)}'
            })
    
    return issues

def main():
    print("=" * 80)
    print("ANÁLISE DE ERROS E ARQUIVOS DO PROJETO")
    print("=" * 80)
    print()
    
    print("🔍 Procurando erros de sintaxe...")
    syntax_errors = find_syntax_errors()
    print(f"   Encontrados: {len(syntax_errors)}")
    
    print("🔍 Procurando problemas potenciais...")
    issues = find_potential_issues()
    print(f"   Encontrados: {len(issues)}")
    
    print("🔍 Procurando arquivos não utilizados...")
    unused_files = find_unused_files()
    print(f"   Encontrados: {len(unused_files)}")
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'syntax_errors': syntax_errors,
        'issues': issues,
        'unused_files': unused_files,
        'summary': {
            'total_syntax_errors': len(syntax_errors),
            'total_issues': len(issues),
            'total_unused_files': len(unused_files)
        }
    }
    
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print()
    print("=" * 80)
    print("RESUMO")
    print("=" * 80)
    print(f"❌ Erros de sintaxe: {len(syntax_errors)}")
    print(f"⚠️  Problemas potenciais: {len(issues)}")
    print(f"📁 Arquivos não utilizados: {len(unused_files)}")
    print()
    print(f"💾 Relatório salvo em: {REPORT_FILE}")
    
    if syntax_errors:
        print("\n🚨 ERROS DE SINTAXE ENCONTRADOS:")
        for err in syntax_errors[:10]:  # Mostrar primeiros 10
            print(f"   {err['file']}:{err['line']} - {err['message']}")
    
    if unused_files:
        print("\n📁 ARQUIVOS POTENCIALMENTE NÃO UTILIZADOS:")
        for f in unused_files[:10]:  # Mostrar primeiros 10
            print(f"   {f}")

if __name__ == '__main__':
    main()
