# 🤖 Opções de IA Gratuita para o Chatbot

## ✅ Melhores Opções Gratuitas (Recomendadas)

### 1. 🌟 **Google Gemini (Google Generative AI)** ⭐ RECOMENDADO

**Por quê?**
- ✅ **Totalmente gratuito** (até 60 requisições/minuto)
- ✅ **Não precisa de cartão de crédito**
- ✅ **Fácil de integrar** (biblioteca Python oficial)
- ✅ **Qualidade excelente** (modelo Gemini)
- ✅ **Generoso no plano gratuito**

**Como usar:**
1. Acesse: https://aistudio.google.com/app/apikey
2. Faça login com conta Google
3. Clique em "Create API Key"
4. Copie a chave gerada
5. Adicione no `.env`:
   ```env
   GEMINI_API_KEY=sua-chave-gemini-aqui
   USE_AI=true
   AI_PROVIDER=gemini
   ```

**Biblioteca:** `google-generativeai` (já pode estar instalada)

---

### 2. ⚡ **Groq** (Muito Rápido)

**Por quê?**
- ✅ **Totalmente gratuito** (14.400 requisições/dia)
- ✅ **Extremamente rápido** (processa em milissegundos)
- ✅ **Não precisa de cartão de crédito**
- ✅ **Fácil de integrar**

**Como usar:**
1. Acesse: https://console.groq.com/keys
2. Faça login (pode usar Google/GitHub)
3. Crie uma API key
4. Adicione no `.env`:
   ```env
   GROQ_API_KEY=sua-chave-groq-aqui
   USE_AI=true
   AI_PROVIDER=groq
   ```

**Biblioteca:** `groq` (precisa instalar)

---

### 3. 🏠 **Ollama** (Local - Totalmente Gratuito)

**Por quê?**
- ✅ **100% gratuito** (roda no seu computador)
- ✅ **Sem limites de uso**
- ✅ **Sem necessidade de internet** (após download)
- ✅ **Privacidade total** (dados não saem do seu PC)

**Desvantagens:**
- ⚠️ Precisa instalar o Ollama no Windows
- ⚠️ Requer mais recursos do computador
- ⚠️ Modelos precisam ser baixados (alguns GB)

**Como usar:**
1. Baixe: https://ollama.com/download
2. Instale o Ollama
3. Baixe um modelo (ex: `ollama pull llama2` ou `ollama pull mistral`)
4. Adicione no `.env`:
   ```env
   OLLAMA_URL=http://localhost:11434
   USE_AI=true
   AI_PROVIDER=ollama
   OLLAMA_MODEL=llama2
   ```

**Biblioteca:** `ollama` (precisa instalar)

---

### 4. 🤗 **Hugging Face Inference API** (Limitado)

**Por quê?**
- ✅ Gratuito (com limites)
- ✅ Vários modelos disponíveis
- ⚠️ Limite de requisições no plano gratuito

**Como usar:**
1. Acesse: https://huggingface.co/settings/tokens
2. Crie um token
3. Adicione no `.env`:
   ```env
   HUGGINGFACE_API_KEY=seu-token-aqui
   USE_AI=true
   AI_PROVIDER=huggingface
   ```

---

## 📊 Comparação Rápida

| Opção | Gratuito? | Fácil? | Qualidade | Velocidade | Recomendado? |
|-------|-----------|--------|-----------|------------|--------------|
| **Google Gemini** | ✅ Sim | ⭐⭐⭐ Muito | ⭐⭐⭐ Excelente | ⭐⭐⭐ Boa | ⭐⭐⭐ **SIM** |
| **Groq** | ✅ Sim | ⭐⭐⭐ Muito | ⭐⭐ Boa | ⭐⭐⭐ Excelente | ⭐⭐ Sim |
| **Ollama** | ✅ Sim | ⭐⭐ Média | ⭐⭐ Boa | ⭐⭐ Boa | ⭐⭐ Sim (se tiver espaço) |
| **Hugging Face** | ⚠️ Limitado | ⭐⭐ Média | ⭐⭐ Boa | ⭐⭐ Boa | ⭐ Não recomendado |

---

## 🎯 Recomendação

### Para o seu caso, recomendo: **Google Gemini** 🌟

**Por quê?**
- ✅ Mais fácil de integrar
- ✅ Totalmente gratuito e generoso
- ✅ Não precisa instalar nada além da biblioteca
- ✅ Qualidade excelente
- ✅ Funciona bem para chatbot de saúde

---

## 🚀 Próximos Passos

Escolha uma opção e me avise qual você prefere, que eu ajudo a integrar no seu projeto!

**Opções:**
1. **Google Gemini** (mais fácil) ⭐
2. **Groq** (mais rápido)
3. **Ollama** (totalmente local)

Qual você prefere? Posso ajudar a configurar qualquer uma delas! 😊
