#!/usr/bin/env python3
"""
Script para adicionar chaves faltantes nos arquivos JSON
"""

import json
import os
from pathlib import Path

def add_categoria_to_base_conhecimento(file_path):
    """Adiciona chave 'categoria' aos objetos de base_conhecimento.json"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Categorias baseadas nas chaves dos objetos
    categorias_map = {
        'identidade': 'identidade',
        'alimentacao': 'alimentacao',
        'baby_blues': 'saude_mental',
        'puerperio': 'geral',
        'cesarea': 'parto',
        'pes_inchados': 'sintomas',
        'leite': 'amamentacao',
        'flacidez': 'recuperacao',
        'queda_cabelo': 'sintomas',
        'substancias': 'saude_gestacao',
        'tingir_cabelo': 'estetica',
        'sinais_alerta': 'emergencia',
        'depressao': 'saude_mental',
        'vacinas': 'vacinas',
        'exercicios': 'exercicios',
        'relacao': 'relacionamento',
        'sexo': 'relacionamento',
        'sono': 'cuidados',
        'higiene': 'cuidados',
        'assadura': 'bebe',
        'cuidados_bebe': 'bebe'
    }
    
    modified = False
    for key, value in data.items():
        if isinstance(value, dict) and 'categoria' not in value:
            # Tenta inferir categoria da chave
            categoria = 'geral'
            for cat_key, cat_value in categorias_map.items():
                if cat_key in key.lower():
                    categoria = cat_value
                    break
            
            value['categoria'] = categoria
            modified = True
    
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[OK] Adicionadas chaves 'categoria' em {file_path}")
        return True
    return False

def fix_mensagens_apoio(file_path):
    """Converte mensagens_apoio.json para estrutura com chave 'mensagem'"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Se já tem estrutura correta, não modifica
    if isinstance(data, dict) and len(data) > 0:
        first_key = list(data.keys())[0]
        if isinstance(data[first_key], dict) and 'mensagem' in data[first_key]:
            print(f"[INFO] {file_path} ja tem estrutura correta")
            return False
    
    # Converte estrutura de { "1": "mensagem", ... } para { "1": { "mensagem": "mensagem" }, ... }
    modified = False
    new_data = {}
    for key, value in data.items():
        if isinstance(value, str):
            new_data[key] = {"mensagem": value}
            modified = True
        else:
            new_data[key] = value
    
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, ensure_ascii=False, indent=2)
        print(f"[OK] Convertido {file_path} para estrutura com chave 'mensagem'")
        return True
    return False

def main():
    """Função principal"""
    project_root = Path(__file__).parent.parent
    
    # Arquivos para corrigir
    files_to_fix = [
        project_root / "backend" / "base_conhecimento.json",
        project_root / "dados" / "base_conhecimento.json",
        project_root / "backend" / "mensagens_apoio.json",
        project_root / "dados" / "mensagens_apoio.json"
    ]
    
    for file_path in files_to_fix:
        if not file_path.exists():
            print(f"[AVISO] Arquivo nao encontrado: {file_path}")
            continue
        
        if "base_conhecimento" in file_path.name:
            add_categoria_to_base_conhecimento(file_path)
        elif "mensagens_apoio" in file_path.name:
            fix_mensagens_apoio(file_path)

if __name__ == "__main__":
    main()

