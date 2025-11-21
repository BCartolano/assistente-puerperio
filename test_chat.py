#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de teste para validar as melhorias de humanização da Sophia
Testa respostas longas, detalhadas e conversacionais
"""

import requests
import json
import time

# URL do servidor (ajuste se necessário)
BASE_URL = "http://localhost:5000"

def testar_chat(pergunta, user_id="test_user"):
    """Testa uma pergunta no chat da Sophia"""
    print(f"\n{'='*60}")
    print(f"🧪 TESTE: {pergunta}")
    print(f"{'='*60}\n")
    
    try:
        # Faz requisição para a API
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={
                "pergunta": pergunta,
                "user_id": user_id
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            resposta = data.get("resposta", "")
            fonte = data.get("fonte", "desconhecida")
            alerta_ativo = data.get("alerta_ativo", False)
            
            print(f"✅ Resposta recebida!")
            print(f"📊 Fonte: {fonte}")
            print(f"📏 Tamanho: {len(resposta)} caracteres")
            print(f"🔢 Palavras: {len(resposta.split())} palavras")
            print(f"⚠️ Alerta ativo: {alerta_ativo}")
            print(f"\n💬 Resposta da Sophia:")
            print(f"{'-'*60}")
            print(resposta)
            print(f"{'-'*60}")
            
            # Análise da resposta
            print(f"\n📈 ANÁLISE:")
            
            # Verifica se é longa e detalhada
            if len(resposta) >= 150:
                print(f"✅ Resposta LONGA ({len(resposta)} caracteres) - Esperado: ≥150")
            elif len(resposta) >= 100:
                print(f"⚠️ Resposta MÉDIA ({len(resposta)} caracteres) - Esperado: ≥150")
            else:
                print(f"❌ Resposta CURTA ({len(resposta)} caracteres) - Esperado: ≥150")
            
            # Verifica tom conversacional
            palavras_empaticas = ['você', 'sua', 'sente', 'sentir', 'querida', 'imagino', 
                                 'entendo', 'compreendo', 'sei que', 'percebo', 'ajudar', 
                                 'ouvir', 'apoio', 'cuidado', 'importa']
            tem_empatia = any(palavra in resposta.lower() for palavra in palavras_empaticas)
            
            if tem_empatia:
                print(f"✅ Tom EMPÁTICO detectado")
            else:
                print(f"⚠️ Tom empático não detectado claramente")
            
            # Verifica perguntas abertas
            tem_pergunta = '?' in resposta
            if tem_pergunta:
                print(f"✅ Contém PERGUNTAS ABERTAS")
            else:
                print(f"⚠️ Não contém perguntas abertas")
            
            # Verifica detalhamento
            tem_exemplos = any(palavra in resposta.lower() for palavra in ['exemplo', 'como', 'talvez', 'pode', 'pode ser'])
            if tem_exemplos:
                print(f"✅ Contém DETALHES e SUGESTÕES")
            else:
                print(f"⚠️ Pode estar faltando detalhes")
            
            return True
        else:
            print(f"❌ Erro na requisição: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ ERRO: Não foi possível conectar ao servidor em {BASE_URL}")
        print(f"💡 Certifique-se de que o servidor está rodando:")
        print(f"   python start.py")
        return False
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False

def main():
    """Executa testes de conversa"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║  🧪 TESTE DE HUMANIZAÇÃO - SOPHIA                           ║
║  Testando respostas longas, detalhadas e conversacionais     ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Verifica se o servidor está rodando
    try:
        response = requests.get(f"{BASE_URL}/teste", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor está rodando!\n")
        else:
            print("⚠️ Servidor respondeu, mas com status diferente de 200\n")
    except:
        print("❌ Servidor não está acessível!")
        print("💡 Inicie o servidor primeiro:")
        print("   python start.py\n")
        return
    
    # Lista de perguntas de teste
    perguntas_teste = [
        "Sophia, como foi o seu dia hoje?",
        "Estou muito cansada",
        "Meu bebê sorriu hoje pela primeira vez!",
        "Estou com medo de não estar fazendo certo",
        "Oi",
        "Quero conversar sobre amamentação"
    ]
    
    resultados = []
    
    for i, pergunta in enumerate(perguntas_teste, 1):
        print(f"\n{'#'*60}")
        print(f"TESTE {i}/{len(perguntas_teste)}")
        print(f"{'#'*60}")
        
        sucesso = testar_chat(pergunta, user_id=f"test_user_{i}")
        resultados.append((pergunta, sucesso))
        
        # Aguarda um pouco entre testes
        if i < len(perguntas_teste):
            time.sleep(2)
    
    # Resumo final
    print(f"\n\n{'='*60}")
    print("📊 RESUMO DOS TESTES")
    print(f"{'='*60}\n")
    
    sucessos = sum(1 for _, s in resultados if s)
    total = len(resultados)
    
    for pergunta, sucesso in resultados:
        status = "✅" if sucesso else "❌"
        print(f"{status} {pergunta[:50]}...")
    
    print(f"\n✅ Testes bem-sucedidos: {sucessos}/{total}")
    print(f"❌ Testes com erro: {total - sucessos}/{total}")
    
    if sucessos == total:
        print("\n🎉 Todos os testes passaram!")
    else:
        print("\n⚠️ Alguns testes falharam. Verifique os logs acima.")

if __name__ == "__main__":
    main()

