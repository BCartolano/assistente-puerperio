#!/usr/bin/env python3
"""
Script de Auditoria de Coerência - Sophia Chatbot
Verifica coerência de personalidade, linguagem, dados e estrutura
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

class CoherenceChecker:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.issues = {
            "critical": [],
            "warning": [],
            "info": []
        }
        self.stats = {
            "files_checked": 0,
            "json_files": 0,
            "js_files": 0,
            "html_files": 0,
            "css_files": 0
        }
        
        # Padrões a evitar (exceto em avisos médicos)
        self.forbidden_words = [
            "prescreva", "prescrever", "prescrição",
            "remédio", "medicamento", "medicação",
            "cura", "curar",
            "diagnóstico", "diagnosticar"
        ]
        
        # Contextos onde palavras proibidas são permitidas
        self.allowed_contexts = [
            "importante:",
            "aviso",
            "consulte",
            "profissional",
            "não substitui",
            "procure orientação",
            "orientação médica",
            "orientação de enfermagem",
            "prescrição médica",
            "prescrito",
            "prescrita",
            "realize apenas com",
            "deve ser indicado",
            "deve ser orientado",
            "check_coherence",  # Ignora no próprio script
            "validate_json",    # Ignora nos scripts de validação
            "simulate_dialogue" # Ignora nos scripts de validação
        ]
        
        # Padrões de linguagem a verificar
        self.dry_responses = [
            r'\bOk\.\s*$',
            r'\bok\.\s*$',
            r'\bOK\.\s*$',
            r'\bTudo bem\.\s*$',
            r'\bEntendi\.\s*$'
        ]
        
        # Chaves JSON esperadas
        self.expected_json_keys = {
            "base_conhecimento": ["pergunta", "resposta", "categoria"],
            "guias_praticos": ["titulo", "descricao", "passos"],
            "mensagens_apoio": ["mensagem"],
            "cuidados_gestacao": ["trimestre", "titulo", "cuidados"],
            "cuidados_pos_parto": ["periodo", "titulo", "cuidados"]
        }
    
    def check_file(self, file_path: Path) -> None:
        """Verifica um arquivo individual"""
        self.stats["files_checked"] += 1
        
        if file_path.suffix == ".json":
            self.stats["json_files"] += 1
            self.check_json_file(file_path)
        elif file_path.suffix == ".js":
            self.stats["js_files"] += 1
            self.check_js_file(file_path)
        elif file_path.suffix == ".html":
            self.stats["html_files"] += 1
            self.check_html_file(file_path)
        elif file_path.suffix == ".css":
            self.stats["css_files"] += 1
            self.check_css_file(file_path)
        elif file_path.suffix == ".py":
            self.check_python_file(file_path)
    
    def check_json_file(self, file_path: Path) -> None:
        """Verifica arquivo JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Verifica palavras proibidas (exceto em contexto de avisos)
            content_str = json.dumps(data, ensure_ascii=False)
            content_lower = content_str.lower()
            
            for word in self.forbidden_words:
                # Usa regex com word boundaries para evitar falsos positivos
                pattern = rf'\b{re.escape(word.lower())}\b'
                matches = list(re.finditer(pattern, content_lower))
                
                for match in matches:
                    # Verifica se está em contexto permitido (avisos médicos)
                    word_pos = match.start()
                    context_before = content_lower[max(0, word_pos-100):word_pos]
                    context_after = content_lower[word_pos:min(len(content_lower), word_pos+100)]
                    context = context_before + context_after
                    
                    is_allowed = any(allowed in context for allowed in self.allowed_contexts)
                    
                    if not is_allowed:
                        self.issues["critical"].append(
                            f"[CRITICO] {file_path}: Palavra proibida encontrada: '{word}'"
                        )
                        break  # Evita múltiplos avisos para a mesma palavra no mesmo arquivo
            
            # Verifica estrutura de chaves
            self.check_json_structure(file_path, data)
            
        except json.JSONDecodeError as e:
                    self.issues["critical"].append(
                        f"[CRITICO] {file_path}: JSON invalido - {str(e)}"
                    )
        except Exception as e:
            self.issues["warning"].append(
                f"[AVISO] {file_path}: Erro ao processar - {str(e)}"
            )
    
    def check_json_structure(self, file_path: Path, data: dict) -> None:
        """Verifica estrutura de chaves JSON"""
        filename = file_path.stem
        
        # Verifica se é um dos arquivos conhecidos
        for key_pattern, expected_keys in self.expected_json_keys.items():
            if key_pattern in filename:
                self.validate_keys(file_path, data, expected_keys)
                break
    
    def validate_keys(self, file_path: Path, data: dict, expected_keys: List[str]) -> None:
        """Valida chaves esperadas em um objeto JSON"""
        if isinstance(data, dict):
            # Verifica se é um objeto ou array de objetos
            items = [data] if not any(isinstance(v, dict) for v in data.values()) else data.values()
            
            for item in items:
                if isinstance(item, dict):
                    missing_keys = [key for key in expected_keys if key not in item]
                    if missing_keys:
                        self.issues["warning"].append(
                            f"[AVISO] {file_path}: Chaves faltando: {', '.join(missing_keys)}"
                        )
    
    def check_js_file(self, file_path: Path) -> None:
        """Verifica arquivo JavaScript"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verifica respostas secas
            for pattern in self.dry_responses:
                matches = re.finditer(pattern, content, re.MULTILINE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    self.issues["warning"].append(
                        f"[AVISO] {file_path}:{line_num} Resposta seca encontrada: '{match.group()}'"
                    )
            
            # Verifica palavras proibidas em strings (exceto em contexto de avisos)
            for word in self.forbidden_words:
                pattern = rf'["\']([^"\']*{word}[^"\']*)["\']'
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Ignora se for arquivo de script de validação
                    if "check_coherence" in str(file_path) or "validate_json" in str(file_path):
                        continue
                    
                    string_content = match.group(1).lower()
                    # Verifica se está em contexto de aviso médico
                    is_allowed = any(ctx in string_content for ctx in self.allowed_contexts)
                    
                    if not is_allowed:
                        line_num = content[:match.start()].count('\n') + 1
                        self.issues["critical"].append(
                            f"[CRITICO] {file_path}:{line_num} Palavra proibida em string: '{word}'"
                        )
        
        except Exception as e:
            self.issues["warning"].append(
                f"[AVISO] {file_path}: Erro ao processar - {str(e)}"
            )
    
    def check_html_file(self, file_path: Path) -> None:
        """Verifica arquivo HTML"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verifica palavras proibidas (exceto em contexto de avisos)
            content_lower = content.lower()
            for word in self.forbidden_words:
                if word.lower() in content_lower:
                    word_pos = content_lower.find(word.lower())
                    # Ignora se estiver em comentários
                    if "<!--" in content[:word_pos]:
                        continue
                    
                    # Verifica contexto
                    context = content_lower[max(0, word_pos-100):min(len(content_lower), word_pos+100)]
                    is_allowed = any(ctx in context for ctx in self.allowed_contexts)
                    
                    if not is_allowed:
                        self.issues["warning"].append(
                            f"[AVISO] {file_path}: Palavra proibida encontrada: '{word}'"
                        )
        
        except Exception as e:
            self.issues["warning"].append(
                f"[AVISO] {file_path}: Erro ao processar - {str(e)}"
            )
    
    def check_css_file(self, file_path: Path) -> None:
        """Verifica arquivo CSS (verifica comentários)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verifica apenas em comentários CSS
            comment_pattern = r'/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/'
            comments = re.finditer(comment_pattern, content)
            
            for comment in comments:
                comment_text = comment.group()
                for word in self.forbidden_words:
                    if word.lower() in comment_text.lower():
                        self.issues["info"].append(
                            f"[INFO] {file_path}: Palavra proibida em comentario CSS: '{word}'"
                        )
        
        except Exception as e:
            self.issues["warning"].append(
                f"[AVISO] {file_path}: Erro ao processar - {str(e)}"
            )
    
    def check_python_file(self, file_path: Path) -> None:
        """Verifica arquivo Python"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verifica palavras proibidas em strings
            string_pattern = r'["\']([^"\']*?)["\']'
            strings = re.finditer(string_pattern, content)
            
            for string_match in strings:
                string_content = string_match.group(1)
                string_lower = string_content.lower()
                
                # Ignora se for arquivo de script
                if "check_coherence" in str(file_path) or "validate_json" in str(file_path):
                    continue
                
                for word in self.forbidden_words:
                    if word.lower() in string_lower:
                        # Verifica contexto
                        is_allowed = any(ctx in string_lower for ctx in self.allowed_contexts)
                        
                        if not is_allowed:
                            line_num = content[:string_match.start()].count('\n') + 1
                            self.issues["critical"].append(
                                f"[CRITICO] {file_path}:{line_num} Palavra proibida em string: '{word}'"
                            )
        
        except Exception as e:
            self.issues["warning"].append(
                f"[AVISO] {file_path}: Erro ao processar - {str(e)}"
            )
    
    def check_messages_centralization(self) -> None:
        """Verifica se mensagens estão centralizadas"""
        messages_file = self.project_root / "backend" / "messages.json"
        
        if not messages_file.exists():
            self.issues["warning"].append(
                "[AVISO] Arquivo messages.json nao encontrado. Mensagens podem estar espalhadas."
            )
        else:
            self.issues["info"].append(
                "[OK] Arquivo messages.json encontrado - mensagens centralizadas"
            )
    
    def check_consistency(self) -> None:
        """Verifica consistência entre arquivos"""
        # Verifica se há duplicação de mensagens
        welcome_messages = []
        
        html_file = self.project_root / "backend" / "templates" / "index.html"
        if html_file.exists():
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Procura por mensagens de boas-vindas
                welcome_pattern = r'Bem-vinda[^<]*'
                matches = re.findall(welcome_pattern, content, re.IGNORECASE)
                welcome_messages.extend(matches)
        
        if len(welcome_messages) > 1:
            self.issues["warning"].append(
                f"[AVISO] Multiplas mensagens de boas-vindas encontradas ({len(welcome_messages)})"
            )
    
    def scan_project(self) -> None:
        """Escaneia todo o projeto"""
        print("[SCAN] Escaneando projeto...")
        
        # Diretórios a verificar
        dirs_to_check = [
            "backend",
            "dados",
            "scripts"
        ]
        
        # Extensões a verificar
        extensions = [".json", ".js", ".html", ".css", ".py"]
        
        for dir_name in dirs_to_check:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                for ext in extensions:
                    for file_path in dir_path.rglob(f"*{ext}"):
                        # Ignora node_modules, venv, etc
                        if "node_modules" not in str(file_path) and "venv" not in str(file_path):
                            self.check_file(file_path)
        
        # Verificações adicionais
        self.check_messages_centralization()
        self.check_consistency()
    
    def generate_report(self) -> str:
        """Gera relatório de coerência"""
        report = []
        report.append("=" * 70)
        report.append("RELATORIO DE COERENCIA - SOPHIA CHATBOT")
        report.append("=" * 70)
        report.append("")
        
        # Estatísticas
        report.append("ESTATISTICAS:")
        report.append(f"  • Arquivos verificados: {self.stats['files_checked']}")
        report.append(f"  • Arquivos JSON: {self.stats['json_files']}")
        report.append(f"  • Arquivos JavaScript: {self.stats['js_files']}")
        report.append(f"  • Arquivos HTML: {self.stats['html_files']}")
        report.append(f"  • Arquivos CSS: {self.stats['css_files']}")
        report.append("")
        
        # Problemas críticos
        if self.issues["critical"]:
            report.append("[CRITICO] PROBLEMAS CRITICOS:")
            for issue in self.issues["critical"]:
                report.append(f"  {issue}")
            report.append("")
        else:
            report.append("[OK] Nenhum problema critico encontrado!")
            report.append("")
        
        # Avisos
        if self.issues["warning"]:
            report.append("[AVISO] AVISOS:")
            for issue in self.issues["warning"]:
                report.append(f"  {issue}")
            report.append("")
        else:
            report.append("[OK] Nenhum aviso encontrado!")
            report.append("")
        
        # Informações
        if self.issues["info"]:
            report.append("[INFO] INFORMACOES:")
            for issue in self.issues["info"]:
                report.append(f"  {issue}")
            report.append("")
        
        # Resumo
        report.append("=" * 70)
        total_critical = len(self.issues["critical"])
        total_warnings = len(self.issues["warning"])
        
        if total_critical == 0 and total_warnings == 0:
            report.append("[OK] COERENCIA: TOTAL")
        elif total_critical == 0:
            report.append("[AVISO] COERENCIA: INCONSISTENTE (com avisos)")
        else:
            report.append("[CRITICO] COERENCIA: CRITICO")
        
        report.append("=" * 70)
        
        return "\n".join(report)


def main():
    """Função principal"""
    checker = CoherenceChecker()
    checker.scan_project()
    report = checker.generate_report()
    
    print(report)
    
    # Salva relatório em arquivo
    report_file = Path("COHERENCE_REPORT.txt")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n[INFO] Relatorio salvo em: {report_file}")
    
    # Retorna código de saída baseado em problemas
    if checker.issues["critical"]:
        return 1
    elif checker.issues["warning"]:
        return 2
    return 0


if __name__ == "__main__":
    exit(main())
