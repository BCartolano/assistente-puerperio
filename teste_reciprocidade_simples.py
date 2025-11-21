#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste simples e isolado para validar a detecção de reciprocidade
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def testar_pergunta(pergunta):
    """Testa uma única pergunta"""
    print(f"\n{'='*70}")
    print(f"🧪 TESTE: {pergunta}")
    print(f"{'='*70}\n")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={
                "pergunta": pergunta,
                "user_id": "teste_isolado"
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            resposta = data.get("resposta", "")
            fonte = data.get("fonte", "desconhecida")
            
            print(f"✅ Resposta recebida!")
            print(f"📊 Fonte: {fonte}")
            print(f"📏 Tamanho: {len(resposta)} caracteres")
            print(f"🔢 Palavras: {len(resposta.split())} palavras")
            print(f"\n💬 Resposta:")
            print(f"{'-'*70}")
            print(resposta)
            print(f"{'-'*70}\n")
            
            # Análise
            if fonte == "resposta_alternativa_anti_repeticao" or fonte == "resposta_variada":
                print(f"❌ PROBLEMA: Resposta veio de sistema de anti-repetição!")
                print(f"   Isso significa que a detecção de reciprocidade NÃO funcionou.")
            elif fonte.startswith("gemini"):
                if len(resposta) >= 200:
                    print(f"✅ SUCESSO: Resposta do Gemini com {len(resposta)} caracteres")
                else:
                    print(f"⚠️ ATENÇÃO: Resposta do Gemini mas curta ({len(resposta)} chars)")
            elif fonte == "resposta_reciprocidade_fallback_detalhada":
                print(f"✅ FALLBACK: Usando fallback detalhado para reciprocidade")
                if len(resposta) >= 200:
                    print(f"✅ SUCESSO: Fallback detalhado com {len(resposta)} caracteres")
                else:
                    print(f"⚠️ ATENÇÃO: Fallback mas curto ({len(resposta)} chars)")
            else:
                print(f"⚠️ Fonte desconhecida: {fonte}")
        else:
            print(f"❌ Erro: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════════╗
║  🧪 TESTE ISOLADO - RECIPROCIDADE                                       ║
║  Testa uma pergunta específica para validar a detecção                  ║
╚══════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Testa apenas uma pergunta
    testar_pergunta("Sophia, como foi o seu dia hoje?")

