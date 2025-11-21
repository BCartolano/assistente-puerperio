# 📚 Análise da Base de Conhecimento (RAG) - Sophia

## 📋 Sumário Executivo

Este documento analisa a estrutura e funcionamento do sistema RAG (Retrieval-Augmented Generation) da Sophia, incluindo:
1. **Estrutura da Base de Conhecimento** (arquivos JSON, organização, conteúdo)
2. **Sistema de Busca/Retrieval** (algoritmo de similaridade, threshold)
3. **Integração com Gemini** (como o prompt instrui o modelo a usar a informação)

---

## 1. 📁 Estrutura da Base de Conhecimento

### 1.1 Arquivos JSON Disponíveis

O sistema carrega **9 arquivos JSON** da base de conhecimento:

```
backend/
├── base_conhecimento.json      ✅ 79 itens (principal)
├── mensagens_apoio.json        ✅ 10 mensagens empáticas
├── alertas.json                ✅ Alertas médicos
├── telefones_uteis.json        ✅ Telefones de emergência
├── guias_praticos.json         ✅ 7 guias passo a passo
├── cuidados_gestacao.json      ✅ Cuidados por trimestre
├── cuidados_pos_parto.json     ✅ Cuidados por período
├── vacinas_mae.json            ✅ Vacinas da mãe
└── vacinas_bebe.json           ✅ Vacinas do bebê
```

### 1.2 Estrutura do Arquivo Principal (`base_conhecimento.json`)

**Total de itens:** 79 perguntas/respostas

**Estrutura por item:**
```json
{
  "categoria_key": {
    "pergunta": "Pergunta exemplo?",
    "resposta": "Resposta detalhada...",
    "categoria": "categoria_nome"
  }
}
```

**Exemplo real:**
```json
{
  "identidade": {
    "pergunta": "Por que me sinto perdida depois do parto?",
    "resposta": "É normal. O puerpério é uma fase de transição intensa – seu corpo e mente estão se reorganizando. Esse sentimento de 'não ser mais a mesma' é parte do processo de se redescobrir.",
    "categoria": "identidade"
  }
}
```

**Categorias principais identificadas:**
- `identidade` - Sentimentos e mudanças emocionais
- `alimentacao` - Nutrição e dieta
- `baby_blues` - Saúde mental
- `amamentacao` - Amamentação e cuidados
- `parto` - Parto e recuperação
- `sintomas` - Sintomas físicos
- `geral` - Informações gerais
- `relacionamento` - Relacionamentos e intimidade
- `saude_gestacao` - Saúde na gestação
- `estetica` - Cuidados estéticos
- `emergencia` - Sinais de alerta

### 1.3 Conteúdo da Base de Conhecimento

**Cobertura de temas:**
- ✅ Puerpério (fase pós-parto)
- ✅ Amamentação (leite, pega, problemas comuns)
- ✅ Saúde mental (baby blues, depressão pós-parto)
- ✅ Gestação (cuidados, sintomas, exercícios)
- ✅ Parto (tipos, sinais, recuperação)
- ✅ Relacionamentos (intimidade, libido)
- ✅ Alimentação (dieta, nutrição)
- ✅ Sintomas físicos (inchaço, dores, mudanças)

**Qualidade das respostas:**
- ✅ Respostas diretas e informativas
- ✅ Tom empático e acolhedor
- ✅ Informações médicas com disclaimer
- ✅ Linguagem acessível

---

## 2. 🔍 Sistema de Busca/Retrieval

### 2.1 Algoritmo de Busca

**Localização:** `backend/app.py` - método `buscar_resposta_local()`

**Algoritmo:**
1. **Normalização:** Converte pergunta para lowercase
2. **Extração de palavras-chave:** Filtra palavras com mais de 3 caracteres
3. **Busca por similaridade:**
   - **Similaridade de strings (40%):** Usa `difflib.SequenceMatcher` para comparar pergunta do usuário com pergunta da base
   - **Similaridade por palavras-chave (60%):** Compara palavras-chave entre pergunta do usuário e texto combinado (pergunta + resposta) da base
4. **Combinação:** `similaridade_comb = (similaridade_string * 0.4) + (similaridade_palavras * 0.6)`
5. **Threshold:** Retorna resposta se `similaridade_comb > 0.35` (35%)

**Código:**
```python
def buscar_resposta_local(self, pergunta):
    pergunta_lower = pergunta.lower()
    palavras_pergunta = set([p for p in pergunta_lower.split() if len(p) > 3])
    
    for tema, conteudo in self.base.items():
        pergunta_base = conteudo["pergunta"].lower()
        resposta_base = conteudo["resposta"].lower()
        texto_base = f"{pergunta_base} {resposta_base}"
        palavras_base = set([p for p in texto_base.split() if len(p) > 3])
        
        similaridade_string = difflib.SequenceMatcher(None, pergunta_lower, pergunta_base).ratio()
        palavras_comuns = palavras_pergunta.intersection(palavras_base)
        similaridade_palavras = len(palavras_comuns) / len(palavras_pergunta) if palavras_pergunta else 0
        
        similaridade_comb = (similaridade_string * 0.4) + (similaridade_palavras * 0.6)
        
        if similaridade_comb > maior_similaridade:
            maior_similaridade = similaridade_comb
            melhor_match = conteudo["resposta"]
            categoria = tema
    
    if maior_similaridade > 0.35:
        return melhor_match, categoria, maior_similaridade
    return None, None, 0
```

### 2.2 Pontos Fortes do Algoritmo

✅ **Busca em pergunta + resposta:** Considera tanto a pergunta quanto a resposta da base, aumentando a chance de encontrar correspondências relevantes

✅ **Combinação de métodos:** Usa tanto similaridade de strings quanto palavras-chave, melhorando a precisão

✅ **Threshold razoável:** 35% é um bom equilíbrio entre precisão e recall

### 2.3 Limitações Identificadas

⚠️ **Busca sequencial:** Percorre todos os 79 itens sequencialmente (O(n)) - pode ser lento com base maior

⚠️ **Sem indexação:** Não usa índices invertidos ou embeddings vetoriais para busca mais eficiente

⚠️ **Sem stemming/lemmatization:** Não normaliza palavras (ex: "amamentar" vs "amamentação")

⚠️ **Threshold fixo:** 35% pode ser muito alto para algumas perguntas ou muito baixo para outras

⚠️ **Sem busca semântica:** Não entende sinônimos ou contexto semântico (ex: "leite" vs "mama")

---

## 3. 🤖 Integração com Gemini (RAG Prompt)

### 3.1 Fluxo de Integração

**Quando a resposta local é encontrada (similaridade > 0.35):**

1. **Busca local:** `buscar_resposta_local()` retorna resposta da base
2. **Humanização (opcional):** `humanizar_resposta_local()` adiciona contexto empático
3. **Passagem para Gemini:** Resposta local é passada como `resposta_local_para_gemini`
4. **Geração com Gemini:** Gemini recebe a resposta local + instruções para humanizar

**Código:**
```python
resposta_local_para_gemini = None
if not is_saudacao and resposta_local and similaridade > 0.35:
    resposta_local_para_gemini = resposta_local
    logger.info(f"[CHAT] 📚 Passando resposta local para Gemini (similaridade: {similaridade:.2f})")

resposta_gemini = self.gerar_resposta_gemini(
    pergunta, 
    historico=historico_para_gemini,
    contexto=contexto_para_gemini,
    resposta_local=resposta_local_para_gemini,  # ← Passa resposta local
    is_saudacao=is_saudacao
)
```

### 3.2 Prompt RAG no System Instruction

**Localização:** `backend/app.py` - método `gerar_resposta_gemini()`

**Seção no System Instruction:**
```
📚 IMPORTANTE - BASE DE CONHECIMENTO LOCAL:
Quando você receber informações da base de conhecimento local sobre puerpério, USE essas informações como base para sua resposta. Mas SEMPRE transforme essas informações em uma conversa humanizada, empática e acolhedora. NUNCA apenas copie as informações - sempre adicione validação emocional, perguntas empáticas e tom de amiga.
```

### 3.3 Como a Resposta Local é Inserida no Prompt

**Localização:** `backend/app.py` - método `gerar_resposta_gemini()`

**Código:**
```python
# Se houver resposta local sobre puerpério, adiciona como contexto
if resposta_local:
    prompt += f"\n\n📚 INFORMAÇÃO DA BASE DE CONHECIMENTO SOBRE PUERPÉRIO:\n{resposta_local}\n\n⚠️ IMPORTANTE: Use essa informação como base, mas transforme em uma conversa humanizada, empática e acolhedora. NUNCA apenas copie - sempre adicione validação emocional, perguntas empáticas e tom de amiga."
```

**Estrutura do prompt final:**
```
[System Instruction completo]
[Contexto pessoal do usuário]
[Histórico de conversas]
📚 INFORMAÇÃO DA BASE DE CONHECIMENTO SOBRE PUERPÉRIO:
[Resposta local da base]
⚠️ IMPORTANTE: Use essa informação como base, mas transforme em uma conversa humanizada...
[Pergunta do usuário]
```

### 3.4 Instruções para o Gemini

**O que o Gemini é instruído a fazer:**
1. ✅ **Usar a informação como base:** Não ignorar a resposta local
2. ✅ **Transformar em conversa:** Não copiar literalmente
3. ✅ **Adicionar empatia:** Incluir validação emocional
4. ✅ **Fazer perguntas:** Incluir perguntas empáticas
5. ✅ **Tom de amiga:** Usar linguagem acolhedora e próxima

**O que o Gemini NÃO deve fazer:**
1. ❌ Copiar literalmente a resposta local
2. ❌ Ser apenas informativo sem empatia
3. ❌ Responder como um manual técnico
4. ❌ Ignorar o contexto da conversa

---

## 4. 📊 Análise de Pontos Fortes e Fraquezas

### 4.1 Pontos Fortes ✅

1. **Base de conhecimento bem estruturada:**
   - 79 itens cobrindo temas principais
   - Respostas diretas e informativas
   - Categorização clara

2. **Integração com Gemini:**
   - Resposta local é usada como base
   - Gemini humaniza e adiciona empatia
   - Mantém precisão técnica + tom acolhedor

3. **Sistema de busca funcional:**
   - Encontra respostas relevantes
   - Combina múltiplos métodos de similaridade
   - Threshold razoável (35%)

4. **Humanização:**
   - `humanizar_resposta_local()` adiciona contexto empático
   - Gemini transforma em conversa natural
   - Tom de amiga mantido

### 4.2 Limitações Identificadas ⚠️

1. **Busca limitada:**
   - Apenas 79 itens (pode não cobrir todos os casos)
   - Busca sequencial (lenta com base maior)
   - Sem busca semântica (não entende sinônimos)

2. **Algoritmo de similaridade:**
   - Não usa embeddings vetoriais
   - Não faz stemming/lemmatization
   - Threshold fixo (pode ser otimizado)

3. **Falta de indexação:**
   - Sem índices invertidos
   - Sem busca por categoria
   - Sem busca por palavras-chave específicas

4. **Dependência do Gemini:**
   - Se Gemini não estiver disponível, usa apenas resposta local (sem humanização)
   - Resposta local pode ser muito técnica sem Gemini

---

## 5. 🎯 Recomendações de Melhoria

### 5.1 Melhorias Imediatas (Curto Prazo)

1. **Expandir base de conhecimento:**
   - Adicionar mais itens (objetivo: 150-200 itens)
   - Cobrir mais casos de uso
   - Adicionar variações de perguntas

2. **Otimizar busca:**
   - Adicionar índice invertido para palavras-chave
   - Implementar busca por categoria
   - Cachear resultados de busca frequentes

3. **Melhorar algoritmo:**
   - Adicionar stemming/lemmatization (ex: usar NLTK ou spaCy)
   - Ajustar threshold dinamicamente
   - Adicionar busca por sinônimos

### 5.2 Melhorias Avançadas (Médio/Longo Prazo)

1. **Busca semântica:**
   - Usar embeddings vetoriais (ex: Sentence-BERT, OpenAI embeddings)
   - Implementar busca por similaridade semântica
   - Adicionar busca híbrida (keywords + semântica)

2. **RAG avançado:**
   - Usar múltiplos documentos relevantes (não apenas 1)
   - Adicionar reranking de resultados
   - Implementar busca iterativa (refine query se não encontrar)

3. **Indexação:**
   - Usar banco de dados vetorial (ex: Pinecone, Weaviate)
   - Implementar índice invertido completo
   - Adicionar busca full-text

4. **Avaliação:**
   - Criar métricas de precisão/recall
   - Testar com perguntas reais de usuários
   - Ajustar threshold e pesos baseado em resultados

---

## 6. 📝 Conclusão

### 6.1 Status Atual

✅ **Sistema RAG funcional:** A base de conhecimento está sendo usada corretamente e o Gemini está humanizando as respostas.

✅ **Integração bem feita:** O prompt RAG está claro e o Gemini segue as instruções.

⚠️ **Limitações identificadas:** Busca sequencial, falta de indexação, base pequena.

### 6.2 Próximos Passos Recomendados

1. **Expandir base de conhecimento** (prioridade alta)
2. **Otimizar busca** (prioridade média)
3. **Implementar busca semântica** (prioridade baixa, longo prazo)

### 6.3 Perguntas para Decisão

1. **Quer expandir a base de conhecimento primeiro?** (adicionar mais itens)
2. **Quer otimizar a busca?** (melhorar algoritmo, adicionar indexação)
3. **Quer implementar busca semântica?** (usar embeddings vetoriais)

---

**Data da Análise:** 2025-01-27  
**Versão Analisada:** Atual (commit mais recente)  
**Arquivo Principal:** `backend/app.py`  
**Base de Conhecimento:** `backend/base_conhecimento.json` (79 itens)

