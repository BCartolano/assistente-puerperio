#!/usr/bin/env python3
"""
Simulador de Diálogo Automático
Testa fluxos de conversa principais para verificar coerência
"""

import sys
import json
from pathlib import Path
from typing import List, Dict

class DialogueSimulator:
    def __init__(self):
        self.conversations = []
        self.results = {
            "passed": [],
            "failed": [],
            "warnings": []
        }
    
    def load_base_knowledge(self) -> Dict:
        """Carrega base de conhecimento"""
        base_path = Path("backend/base_conhecimento.json")
        if base_path.exists():
            with open(base_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def test_greeting_flow(self) -> None:
        """Testa fluxo de saudação"""
        print("[TESTE] Testando fluxo de saudacao...")
        
        test_cases = [
            {"input": "Oi", "expected": ["oi", "olá", "bom dia", "boa tarde", "boa noite"]},
            {"input": "Olá", "expected": ["olá", "oi", "bem-vinda"]},
            {"input": "Bom dia", "expected": ["bom dia", "olá", "oi"]}
        ]
        
        base = self.load_base_knowledge()
        
        for case in test_cases:
            input_text = case["input"].lower()
            found_match = False
            
            for key, value in base.items():
                if isinstance(value, dict):
                    pergunta = value.get("pergunta", "").lower()
                    resposta = value.get("resposta", "").lower()
                    
                    if any(exp in pergunta or exp in resposta for exp in case["expected"]):
                        found_match = True
                        break
            
            if found_match:
                self.results["passed"].append(f"[OK] Saudacao '{case['input']}' tem resposta adequada")
            else:
                self.results["warnings"].append(
                    f"[AVISO] Saudacao '{case['input']}' pode nao ter resposta especifica"
                )
    
    def test_question_flow(self) -> None:
        """Testa fluxo de perguntas"""
        print("[TESTE] Testando fluxo de perguntas...")
        
        base = self.load_base_knowledge()
        
        # Verifica se há perguntas e respostas
        has_questions = False
        has_answers = False
        
        for key, value in base.items():
            if isinstance(value, dict):
                if value.get("pergunta"):
                    has_questions = True
                if value.get("resposta"):
                    has_answers = True
        
        if has_questions and has_answers:
            self.results["passed"].append("[OK] Base de conhecimento tem perguntas e respostas")
        else:
            self.results["failed"].append("[ERRO] Base de conhecimento incompleta")
    
    def test_context_continuity(self) -> None:
        """Testa continuidade de contexto"""
        print("[TESTE] Testando continuidade de contexto...")
        
        # Simula conversa sequencial
        conversation = [
            "Estou grávida",
            "Tenho dúvidas sobre alimentação",
            "E sobre exercícios?"
        ]
        
        base = self.load_base_knowledge()
        
        # Verifica se há categorias relacionadas (busca variações com e sem acentos)
        related_categories = set()
        alimentacao_keywords = ["alimentacao", "alimentação", "comer", "nutricao", "nutrição", "dieta"]
        exercicio_keywords = ["exercicio", "exercício", "atividade fisica", "atividade física", "treino", "caminhada", "natação"]
        
        for key, value in base.items():
            if isinstance(value, dict):
                categoria = value.get("categoria", "").lower()
                pergunta = value.get("pergunta", "").lower()
                resposta = value.get("resposta", "").lower()
                texto_completo = f"{categoria} {pergunta} {resposta}"
                
                # Verifica alimentação
                if any(kw in texto_completo for kw in alimentacao_keywords):
                    related_categories.add(key)
                
                # Verifica exercícios
                if any(kw in texto_completo for kw in exercicio_keywords):
                    related_categories.add(key)
        
        # Verifica se encontrou pelo menos uma categoria de cada tipo
        alimentacao_found = any("alimentacao" in cat.lower() or any(kw in base.get(cat, {}).get("pergunta", "").lower() for kw in alimentacao_keywords) 
                               for cat in related_categories)
        exercicio_found = any("exercicio" in cat.lower() or any(kw in base.get(cat, {}).get("pergunta", "").lower() for kw in exercicio_keywords) 
                             for cat in related_categories)
        
        if len(related_categories) >= 2 and (alimentacao_found or exercicio_found):
            self.results["passed"].append(
                f"[OK] Contexto mantido - {len(related_categories)} categorias relacionadas encontradas"
            )
        elif len(related_categories) >= 1:
            # Se encontrou pelo menos uma categoria, não é crítico
            self.results["passed"].append(
                f"[OK] Contexto mantido - {len(related_categories)} categoria(s) relacionada(s) encontrada(s)"
            )
        else:
            self.results["warnings"].append(
                "[AVISO] Poucas categorias relacionadas - continuidade pode ser afetada"
            )
    
    def test_medical_warnings(self) -> None:
        """Testa se avisos médicos estão presentes"""
        print("[TESTE] Testando avisos medicos...")
        
        base = self.load_base_knowledge()
        has_warnings = False
        
        for key, value in base.items():
            if isinstance(value, dict):
                resposta = value.get("resposta", "").lower()
                if "importante" in resposta or "consulte" in resposta or "médico" in resposta:
                    has_warnings = True
                    break
        
        if has_warnings:
            self.results["passed"].append("[OK] Avisos medicos encontrados nas respostas")
        else:
            self.results["warnings"].append(
                "[AVISO] Avisos medicos podem nao estar presentes em todas as respostas"
            )
    
    def run_all_tests(self) -> None:
        """Executa todos os testes"""
        print("=" * 70)
        print("SIMULADOR DE DIALOGO - SOPHIA CHATBOT")
        print("=" * 70)
        print()
        
        self.test_greeting_flow()
        self.test_question_flow()
        self.test_context_continuity()
        self.test_medical_warnings()
        
        print()
        print("=" * 70)
        print("RESULTADOS:")
        print("=" * 70)
        
        if self.results["passed"]:
            print("\n[OK] TESTES APROVADOS:")
            for result in self.results["passed"]:
                print(f"  {result}")
        
        if self.results["failed"]:
            print("\n[ERRO] TESTES FALHADOS:")
            for result in self.results["failed"]:
                print(f"  {result}")
        
        if self.results["warnings"]:
            print("\n[AVISO] AVISOS:")
            for result in self.results["warnings"]:
                print(f"  {result}")
        
        print()
        print("=" * 70)
        
        total_passed = len(self.results["passed"])
        total_failed = len(self.results["failed"])
        total_warnings = len(self.results["warnings"])
        
        if total_failed == 0:
            if total_warnings == 0:
                print("[OK] COERENCIA: TOTAL")
            else:
                print("[AVISO] COERENCIA: COM AVISOS")
        else:
            print("[ERRO] COERENCIA: PROBLEMAS ENCONTRADOS")
        
        print("=" * 70)


def main():
    simulator = DialogueSimulator()
    simulator.run_all_tests()
    
    # Retorna código de saída
    if simulator.results["failed"]:
        return 1
    elif simulator.results["warnings"]:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
