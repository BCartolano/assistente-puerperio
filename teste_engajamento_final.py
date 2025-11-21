#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste Final de Validação do MANDATO DE ENGAJAMENTO
Valida que a Sophia responde com engajamento profundo, empatia e detalhamento
"""

import requests
import time
import uuid
import re

BASE_URL = "http://localhost:5000"

def testar_engajamento(pergunta, user_id_prefix="test_engajamento"):
    """Testa uma pergunta validando o engajamento da Sophia"""
    user_id = f"{user_id_prefix}_{uuid.uuid4().hex[:8]}"
    print(f"\n{'='*70}")
    print(f"🧪 TESTE DE ENGAJAMENTO")
    print(f"{'='*70}\n")
    print(f"📝 Pergunta: {pergunta}")
    print(f"🆔 User ID: {user_id}")
    print(f"{'='*70}\n")
    
    resultados = {
        "pergunta": pergunta,
        "user_id": user_id,
        "tempo_resposta": 0,
        "resposta": "",
        "tamanho": 0,
        "fonte": "",
        "validacoes": {}
    }
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={
                "pergunta": pergunta,
                "user_id": user_id
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        end_time = time.time()
        resultados["tempo_resposta"] = end_time - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            resultados["resposta"] = data.get("resposta", "")
            resultados["tamanho"] = len(resultados["resposta"])
            resultados["fonte"] = data.get("fonte", "desconhecida")
            resultados["alerta_ativo"] = data.get("alerta_ativo", False)
            
            print(f"✅ Resposta recebida!")
            print(f"⏱️  Tempo de resposta: {resultados['tempo_resposta']:.2f}s")
            print(f"📊 Fonte: {resultados['fonte']}")
            print(f"📏 Tamanho: {resultados['tamanho']} caracteres")
            print(f"⚠️  Alerta ativo: {resultados['alerta_ativo']}")
            print(f"\n💬 Resposta da Sophia:")
            print(f"{'-'*70}")
            print(resultados['resposta'])
            print(f"{'-'*70}\n")
            
            # Validações
            validacoes = {}
            score = 0
            max_score = 100
            
            # 1. Tamanho mínimo (150 caracteres)
            print(f"1️⃣ TAMANHO MÍNIMO (≥150 caracteres):")
            if resultados["tamanho"] >= 150:
                print(f"   ✅ PASSOU! Resposta tem {resultados['tamanho']} caracteres (≥150)")
                validacoes["tamanho"] = True
                score += 30
            elif resultados["tamanho"] >= 100:
                print(f"   ⚠️  ATENÇÃO! Resposta tem {resultados['tamanho']} caracteres (100-149, esperado ≥150)")
                validacoes["tamanho"] = False
                score += 15
            else:
                print(f"   ❌ FALHOU! Resposta tem apenas {resultados['tamanho']} caracteres (esperado ≥150)")
                validacoes["tamanho"] = False
            
            # 2. Ausência de frases genéricas
            print(f"\n2️⃣ AUSÊNCIA DE FRASES GENÉRICAS:")
            frases_genericas = [
                "como posso ajudar",
                "em que posso te ajudar",
                "o que você gostaria",
                "tudo bem por aí",
                "tudo bem por ai",
                "tudo bem?",
                "o que você gostaria de saber"
            ]
            tem_frase_generica = any(frase in resultados["resposta"].lower() for frase in frases_genericas)
            if not tem_frase_generica:
                print(f"   ✅ PASSOU! Nenhuma frase genérica detectada")
                validacoes["sem_genericas"] = True
                score += 25
            else:
                print(f"   ❌ FALHOU! Frase genérica detectada na resposta")
                validacoes["sem_genericas"] = False
            
            # 3. Presença de empatia/engajamento
            print(f"\n3️⃣ PRESENÇA DE EMPATIA/ENGAJAMENTO:")
            palavras_empatia = ["sinto", "entendo", "compreendo", "imagino", "percebo", "lamento", "sinto muito"]
            tem_empatia = any(palavra in resultados["resposta"].lower() for palavra in palavras_empatia)
            tem_pergunta_aberta = "?" in resultados["resposta"]
            if tem_empatia and tem_pergunta_aberta:
                print(f"   ✅ PASSOU! Resposta demonstra empatia e faz perguntas abertas")
                validacoes["empatia"] = True
                score += 25
            elif tem_empatia or tem_pergunta_aberta:
                print(f"   ⚠️  PARCIAL! Resposta tem empatia OU pergunta aberta (esperado ambos)")
                validacoes["empatia"] = False
                score += 12
            else:
                print(f"   ❌ FALHOU! Resposta não demonstra empatia nem faz perguntas abertas")
                validacoes["empatia"] = False
            
            # 4. Resposta direta ao problema/sentimento (para casos 2 e 3)
            if "passando mal" in pergunta.lower() or "cansada" in pergunta.lower() or "cansado" in pergunta.lower():
                print(f"\n4️⃣ RESPOSTA DIRETA AO PROBLEMA/SENTIMENTO:")
                pergunta_lower = pergunta.lower()
                resposta_lower = resultados["resposta"].lower()
                
                # Verifica se a resposta menciona o problema/sentimento
                if "passando mal" in pergunta_lower:
                    menciona_problema = any(palavra in resposta_lower for palavra in ["passando mal", "mal", "problema", "acontecendo", "sentindo"])
                elif "cansada" in pergunta_lower or "cansado" in pergunta_lower:
                    menciona_problema = any(palavra in resposta_lower for palavra in ["cansada", "cansado", "cansaço", "cansada", "cansado", "tired"])
                else:
                    menciona_problema = True  # Para outros casos, não aplica
                
                # Verifica se NÃO usa saudações genéricas no início
                nao_tem_saudacao_generica = not resposta_lower.startswith(("oi! em que", "olá! em que", "oi! como", "olá! como"))
                
                if menciona_problema and nao_tem_saudacao_generica:
                    print(f"   ✅ PASSOU! Resposta menciona o problema e não usa saudações genéricas")
                    validacoes["resposta_direta"] = True
                    score += 20
                elif menciona_problema:
                    print(f"   ⚠️  PARCIAL! Resposta menciona o problema mas usa saudações genéricas")
                    validacoes["resposta_direta"] = False
                    score += 10
                else:
                    print(f"   ❌ FALHOU! Resposta não menciona o problema diretamente")
                    validacoes["resposta_direta"] = False
            else:
                # Para saudações, valida engajamento geral
                print(f"\n4️⃣ ENGAJAMENTO EM SAUDAÇÃO:")
                tem_interesse = any(palavra in resultados["resposta"].lower() for palavra in ["como você está", "como está", "sentindo", "acontecendo"])
                if tem_interesse:
                    print(f"   ✅ PASSOU! Resposta demonstra interesse genuíno")
                    validacoes["resposta_direta"] = True
                    score += 20
                else:
                    print(f"   ⚠️  ATENÇÃO! Resposta não demonstra interesse genuíno suficiente")
                    validacoes["resposta_direta"] = False
                    score += 10
            
            resultados["validacoes"] = validacoes
            resultados["score"] = score
            resultados["max_score"] = max_score
            
            print(f"\n{'='*70}")
            print(f"📊 RESULTADO DO TESTE:")
            print(f"{'='*70}\n")
            print(f"Score: {score}/{max_score} ({score/max_score*100:.0f}%)")
            if score >= 80:
                print(f"✅ EXCELENTE! Engajamento funcionando perfeitamente!")
            elif score >= 60:
                print(f"⚠️  BOM! Engajamento funcionando, mas pode melhorar")
            else:
                print(f"❌ ATENÇÃO! Engajamento precisa de ajustes")
            print(f"{'='*70}\n")
            
        else:
            print(f"❌ ERRO: Status code {response.status_code} - {response.text}")
            resultados["erro"] = f"Status {response.status_code}"
            
    except requests.exceptions.Timeout:
        print(f"❌ ERRO: Requisição excedeu o tempo limite de 30 segundos.")
        resultados["erro"] = "Timeout"
    except Exception as e:
        print(f"❌ ERRO inesperado: {e}")
        resultados["erro"] = str(e)
    
    return resultados

def main():
    print(f"\n{'='*70}")
    print(f"🧪 TESTE FINAL - VALIDAÇÃO DO MANDATO DE ENGAJAMENTO")
    print(f"{'='*70}\n")
    print(f"Este teste valida que a Sophia:")
    print(f"1. ✅ Responde com MÍNIMO 150 caracteres")
    print(f"2. ✅ NÃO usa frases genéricas que encerram a conversa")
    print(f"3. ✅ Demonstra empatia e faz perguntas abertas")
    print(f"4. ✅ Responde DIRETAMENTE a problemas/sentimentos")
    print(f"{'='*70}\n")
    
    resultados = []
    
    # Teste 1: Saudação/Engajamento
    print(f"\n{'='*70}\n")
    print(f"🧪 TESTE 1: Saudação/Engajamento - 'Sophia'")
    resultados.append(testar_engajamento("Sophia", "test_saudacao"))
    
    # Aguarda um pouco entre testes
    time.sleep(1)
    
    # Teste 2: Problema Genérico
    print(f"\n{'='*70}\n")
    print(f"🧪 TESTE 2: Problema Genérico - 'Eu estou passando mal'")
    resultados.append(testar_engajamento("Eu estou passando mal", "test_problema"))
    
    # Aguarda um pouco entre testes
    time.sleep(1)
    
    # Teste 3: Afirmação de Sentimento
    print(f"\n{'='*70}\n")
    print(f"🧪 TESTE 3: Afirmação de Sentimento - 'Estou cansada'")
    resultados.append(testar_engajamento("Estou cansada", "test_sentimento"))
    
    # Resumo Final
    print(f"\n{'='*70}")
    print(f"📊 RESUMO FINAL DOS TESTES")
    print(f"{'='*70}\n")
    
    total_score = 0
    total_max_score = 0
    
    for i, resultado in enumerate(resultados):
        if "erro" not in resultado:
            print(f"Teste {i+1}: {resultado['pergunta']}")
            print(f"  📏 Tamanho: {resultado['tamanho']} caracteres")
            print(f"  ⏱️  Tempo: {resultado['tempo_resposta']:.2f}s")
            print(f"  📊 Fonte: {resultado['fonte']}")
            print(f"  ✅ Validações: {sum(1 for v in resultado['validacoes'].values() if v)}/{len(resultado['validacoes'])}")
            print(f"  📈 Score: {resultado.get('score', 0)}/{resultado.get('max_score', 100)} ({resultado.get('score', 0)/resultado.get('max_score', 100)*100:.0f}%)")
            print()
            total_score += resultado.get('score', 0)
            total_max_score += resultado.get('max_score', 100)
    
    if total_max_score > 0:
        score_final = (total_score / total_max_score) * 100
        print(f"{'='*70}")
        print(f"📊 SCORE FINAL GERAL: {total_score}/{total_max_score} ({score_final:.0f}%)")
        if score_final >= 80:
            print(f"✅✅✅ EXCELENTE! MANDATO DE ENGAJAMENTO FUNCIONANDO PERFEITAMENTE!")
        elif score_final >= 60:
            print(f"⚠️  BOM! MANDATO DE ENGAJAMENTO FUNCIONANDO, MAS PODE MELHORAR")
        else:
            print(f"❌ ATENÇÃO! MANDATO DE ENGAJAMENTO PRECISA DE AJUSTES")
        print(f"{'='*70}\n")

if __name__ == "__main__":
    main()

