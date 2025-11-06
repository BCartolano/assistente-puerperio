# 🤖 Como Configurar o Google Gemini

## ✅ Implementação Completa

O sistema agora suporta **Google Gemini** como alternativa à OpenAI! 

### 🎯 Estratégia de Fallback

O sistema tenta as IAs nesta ordem:
1. **OpenAI** (se disponível)
2. **Gemini** (se OpenAI falhar ou não estiver disponível)
3. **Base Local Humanizada** (se nenhuma IA funcionar)

## 📋 Passo a Passo

### 1. Instalar a Biblioteca

```bash
pip install google-generativeai
```

Ou atualize o `requirements.txt` (já atualizado):
```bash
pip install -r requirements.txt
```

### 2. Obter Chave da API do Gemini

1. Acesse: https://aistudio.google.com/app/apikey
2. Faça login com sua conta Google
3. Clique em "Create API Key"
4. Copie a chave gerada

### 3. Configurar no `.env`

Adicione a chave ao arquivo `.env` na raiz do projeto:

```env
# OpenAI (opcional, mas recomendado)
OPENAI_API_KEY=sua_chave_openai_aqui

# Gemini (opcional, mas recomendado como backup)
GEMINI_API_KEY=sua_chave_gemini_aqui
```

### 4. Reiniciar o Servidor

Após adicionar a chave, reinicie o servidor Flask:

```bash
python backend/app.py
```

## ✅ Verificação

Ao iniciar o servidor, você verá:

```
[OPENAI] ✅ Cliente OpenAI inicializado com sucesso
[GEMINI] ✅ Cliente Gemini inicializado com sucesso
```

Ou:

```
[OPENAI] ⚠️ OPENAI_API_KEY não configurada
[GEMINI] ✅ Cliente Gemini inicializado com sucesso
```

## 🎯 Vantagens do Gemini

1. **Gratuito** - Cota generosa gratuita
2. **Fallback Automático** - Usado automaticamente se OpenAI falhar
3. **Mesma Humanização** - Respostas empáticas e conversacionais
4. **Rápido** - Modelo `gemini-1.5-flash` é muito rápido

## 📊 Logs

O sistema registra qual IA foi usada:

```
[CHAT] ✅ Resposta gerada pela IA (OpenAI)
[CHAT] ✅ Resposta gerada pela IA (Gemini)
[CHAT] 📚 Resposta da base local HUMANIZADA
```

## ⚠️ Troubleshooting

### Erro: "Biblioteca não instalada"
```bash
pip install google-generativeai
```

### Erro: "GEMINI_API_KEY não configurada"
- Verifique se adicionou a chave no `.env`
- Reinicie o servidor após adicionar

### Erro: "Quota esgotada"
- O sistema automaticamente usa a base local humanizada
- Considere atualizar seu plano no Google AI Studio

## 🚀 Pronto!

Agora você tem **duas IAs** configuradas com fallback automático! 🎉

