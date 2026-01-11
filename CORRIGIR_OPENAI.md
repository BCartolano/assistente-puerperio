# Como Corrigir o Problema do OpenAI

## Problema Identificado

O diagnóstico mostrou que:
- ✅ Biblioteca `openai` está instalada
- ✅ Arquivo `.env` existe e contém `OPENAI_API_KEY`
- ❌ `USE_AI` está configurado como `False`
- ❌ A chave não está sendo carregada corretamente

## Solução Rápida

### 1. Verifique o arquivo `.env`

Abra o arquivo `.env` na raiz do projeto e verifique se contém:

```env
USE_AI=true
OPENAI_API_KEY=sk-sua-chave-aqui
```

**IMPORTANTE:**
- `USE_AI` deve ser `true` (não `false` ou `True`)
- `OPENAI_API_KEY` deve começar com `sk-`
- Não deve haver espaços ao redor do `=`

### 2. Se não tiver a chave OpenAI

1. Acesse: https://platform.openai.com/api-keys
2. Faça login na sua conta OpenAI
3. Clique em "Create new secret key"
4. Copie a chave gerada (ela só aparece uma vez!)
5. Adicione no arquivo `.env`:
   ```
   OPENAI_API_KEY=sk-sua-chave-copiada-aqui
   USE_AI=true
   ```

### 3. Verifique se há créditos na conta

1. Acesse: https://platform.openai.com/account/billing
2. Verifique se há créditos disponíveis
3. Se não houver, adicione créditos

### 4. Reinicie o servidor

Após fazer as alterações no `.env`:

1. Pare o servidor (Ctrl+C)
2. Inicie novamente:
   ```bash
   python start.py
   ```

### 5. Execute o diagnóstico novamente

Para verificar se está tudo OK:

```bash
python verificar_openai.py
```

## Exemplo de arquivo `.env` correto

```env
# Configurações do Chatbot Puerpério
USE_AI=true
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Opcional: Se já tiver um assistente criado
# OPENAI_ASSISTANT_ID=asst_xxxxxxxxxxxxx

# Outras configurações...
SECRET_KEY=sua-chave-secreta-aqui
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000
BASE_URL=http://localhost:5000
```

## Problemas Comuns

### "USE_AI está False"
- Verifique se no `.env` está escrito `USE_AI=true` (minúsculas)
- Não use aspas: `USE_AI="true"` ❌

### "OPENAI_API_KEY não encontrada"
- Verifique se a linha não tem espaços: `OPENAI_API_KEY = sk-xxx` ❌
- Use: `OPENAI_API_KEY=sk-xxx` ✅

### "Quota excedida"
- Adicione créditos em: https://platform.openai.com/account/billing

### "Chave inválida"
- Verifique se a chave começa com `sk-`
- Gere uma nova chave se necessário

## Ainda não funciona?

Execute o diagnóstico e envie o resultado:

```bash
python verificar_openai.py
```

Isso mostrará exatamente qual é o problema.

