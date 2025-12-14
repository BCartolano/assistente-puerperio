# ✅ RF.EMO.009 - Implementação Completa: Triagem Emocional Mãe Ansiosa

## 📋 Resumo da Implementação

**Requisito Funcional:** RF.EMO.009  
**Nome:** Integração com BMad Core - Triagem Emocional da Mãe Ansiosa  
**Status:** ✅ **IMPLEMENTADO**  
**Data:** 2025-01-27

---

## 🎯 Objetivo

Implementar sistema de triagem emocional integrado ao BMad Core para identificar e apoiar mães que apresentam sinais de ansiedade relacionados à gestação, parto ou cuidados com o bebê.

---

## ✅ Funcionalidades Implementadas

### 1. **Estrutura de Dados de Triagem Emocional**

**Arquivo:** `dados/triagem_emocional.json` e `backend/triagem_emocional.json`

- ✅ Perfil emocional "Mãe Ansiosa" definido
- ✅ Padrões de detecção (palavras-chave, frases completas, contextos)
- ✅ Níveis de ansiedade (leve, moderada, alta)
- ✅ Respostas personalizadas por nível
- ✅ Recursos de apoio (telefones úteis, orientações)
- ✅ Metadados de integração BMad Core

### 2. **Função de Detecção de Ansiedade**

**Localização:** `backend/app.py` - Função `detectar_triagem_ansiedade()`

**Funcionalidades:**
- ✅ Análise de mensagens para detectar padrões de ansiedade
- ✅ Normalização de texto (remoção de acentos)
- ✅ Detecção de palavras-chave e frases completas
- ✅ Verificação de contexto (gestação, parto, bebê, etc.)
- ✅ Classificação em níveis (leve, moderada, alta)
- ✅ Seleção de respostas apropriadas
- ✅ Retorno de recursos de apoio

**Retorno:**
```python
{
    "detectado": True/False,
    "nivel": "leve"/"moderada"/"alta"/None,
    "perfil": "mae_ansiosa"/None,
    "resposta": "resposta personalizada",
    "recursos": {
        "telefones": [...],
        "orientacoes": [...]
    },
    "indicadores_encontrados": int,
    "palavras_encontradas": [...],
    "frases_encontradas": [...]
}
```

### 3. **Integração no Fluxo do Chatbot**

**Localização:** `backend/app.py` - Método `chat()` da classe `ChatbotPuerperio`

**Integração:**
- ✅ Triagem emocional executada após detecção de risco de suicídio
- ✅ Ansiedade moderada/alta tem prioridade sobre resposta normal
- ✅ Ansiedade leve é combinada com resposta normal
- ✅ Logs detalhados para monitoramento

**Fluxo:**
1. Detecta risco de suicídio (prioridade máxima)
2. **RF.EMO.009:** Detecta triagem emocional (ansiedade)
3. Se ansiedade moderada/alta → retorna resposta de triagem
4. Se ansiedade leve → combina com resposta normal
5. Continua fluxo normal do chatbot

### 4. **Rota API Dedicada**

**Endpoint:** `POST /api/triagem-emocional`

**Parâmetros:**
```json
{
    "mensagem": "texto da mensagem",
    "user_id": "id_do_usuario"
}
```

**Resposta:**
```json
{
    "codigo_requisito": "RF.EMO.009",
    "integracao_bmad": true,
    "detectado": true,
    "nivel": "moderada",
    "perfil": "mae_ansiosa",
    "resposta": "...",
    "recursos": {...}
}
```

---

## 📊 Níveis de Ansiedade e Respostas

### **Ansiedade Leve**
- Preocupações pontuais
- Não interfere significativamente no dia a dia
- Resposta: Acolhimento e dicas de relaxamento

### **Ansiedade Moderada**
- Preocupações frequentes
- Pode afetar sono ou alimentação
- Resposta: Recomendação de buscar ajuda profissional + recursos de apoio

### **Ansiedade Alta**
- Sintomas físicos intensos
- Ataques de pânico possíveis
- Interfere significativamente no dia a dia
- Resposta: Busca imediata de ajuda médica + recursos de emergência

---

## 🔗 Integração com BMad Core

### Metadados de Integração

```json
{
    "integracao_bmad": {
        "codigo_requisito": "RF.EMO.009",
        "nome": "Integração com BMad Core - Triagem Emocional Mãe Ansiosa",
        "descricao": "Sistema de triagem emocional integrado ao BMad Core",
        "versao": "1.0.0",
        "data_criacao": "2025-01-27"
    }
}
```

### Padrões de Detecção

**Palavras-chave:** 40+ termos relacionados à ansiedade  
**Frases completas:** 18+ frases específicas de ansiedade  
**Contextos:** Gestação, parto, bebê, amamentação, cuidados, puerpério

---

## 📁 Arquivos Criados/Modificados

### Novos Arquivos:
1. ✅ `dados/triagem_emocional.json` - Estrutura de dados completa
2. ✅ `backend/triagem_emocional.json` - Cópia para backend
3. ✅ `RF_EMO_009_IMPLEMENTACAO.md` - Esta documentação

### Arquivos Modificados:
1. ✅ `backend/app.py` - Adicionada função `detectar_triagem_ansiedade()`
2. ✅ `backend/app.py` - Integrada triagem no método `chat()`
3. ✅ `backend/app.py` - Adicionada rota `/api/triagem-emocional`

---

## 🧪 Como Testar

### 1. Teste via API de Chat (Integrado)

```bash
POST /api/chat
{
    "pergunta": "Estou muito ansiosa com o parto, não consigo parar de me preocupar",
    "user_id": "test_user"
}
```

**Resposta esperada:**
- `fonte: "triagem_emocional"`
- `nivel: "moderada"` ou `"alta"`
- `tipo: "ansiedade"`
- `perfil: "mae_ansiosa"`

### 2. Teste via API Dedicada

```bash
POST /api/triagem-emocional
{
    "mensagem": "Tenho muito medo de fazer algo errado com o bebê",
    "user_id": "test_user"
}
```

**Resposta esperada:**
- `detectado: true`
- `nivel: "leve"` ou `"moderada"`
- `codigo_requisito: "RF.EMO.009"`
- `integracao_bmad: true`

### 3. Exemplos de Mensagens para Teste

**Ansiedade Leve:**
- "Estou um pouco preocupada com o parto"
- "Tenho algumas dúvidas sobre os cuidados com o bebê"

**Ansiedade Moderada:**
- "Estou muito ansiosa e não consigo dormir de preocupação"
- "Tenho medo de fazer algo errado com o bebê"

**Ansiedade Alta:**
- "Estou tendo crises de ansiedade e não consigo relaxar"
- "Meu coração não para de bater forte, estou em pânico"

---

## 📈 Próximos Passos (Opcional)

- [ ] Adicionar mais perfis emocionais (ex: Mãe Deprimida, Mãe Sobrecarregada)
- [ ] Implementar histórico de triagens por usuário
- [ ] Adicionar métricas e analytics de triagem
- [ ] Criar dashboard de monitoramento
- [ ] Integrar com sistema de notificações para profissionais de saúde

---

## ✅ Checklist de Implementação

- [x] Estrutura de dados criada
- [x] Função de detecção implementada
- [x] Integração no fluxo do chatbot
- [x] Rota API criada
- [x] Arquivos JSON sincronizados (dados/ e backend/)
- [x] Documentação criada
- [x] Logs implementados
- [x] Tratamento de erros implementado

---

## 🎉 Status Final

**RF.EMO.009 - IMPLEMENTADO E FUNCIONAL** ✅

O sistema de triagem emocional para mães ansiosas está completamente integrado ao chatbot Puérpera e ao BMad Core, pronto para uso em produção.

---

**Implementado por:** BMad Orchestrator  
**Data:** 2025-01-27  
**Versão:** 1.0.0

