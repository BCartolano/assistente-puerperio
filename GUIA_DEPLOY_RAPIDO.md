# 🚀 Guia Rápido de Deploy no Render.com

## ⚡ Deploy Rápido (5 minutos)

### Passo 1: Preparar o Código no GitHub
1. Certifique-se de que seu código está no GitHub
2. Se não estiver, faça push:
   ```bash
   git add .
   git commit -m "Preparando para deploy"
   git push
   ```

### Passo 2: Criar Conta no Render.com
1. Acesse: https://render.com
2. Clique em "Get Started for Free"
3. Faça login com GitHub (recomendado) ou crie conta com email

### Passo 3: Criar Web Service
1. No dashboard do Render, clique em **"New +"** > **"Web Service"**
2. Conecte seu repositório GitHub
3. Selecione o repositório `chatbot-puerperio`

### Passo 4: Configurar o Serviço
O Render deve detectar automaticamente as configurações do `render.yaml`. Verifique:
- **Name**: `assistente-puerperio` (ou qualquer nome)
- **Region**: `Oregon` (ou mais próximo de você)
- **Branch**: `main` (ou sua branch principal)
- **Root Directory**: (deixe em branco)
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn wsgi:app`

### Passo 5: Adicionar Variáveis de Ambiente
Na seção **"Environment Variables"**, adicione:
```
OPENAI_API_KEY=sua_chave_openai_aqui
SECRET_KEY=sua_chave_secreta_aqui
FLASK_ENV=production
```

⚠️ **IMPORTANTE**: 
- Use as chaves do seu arquivo `.env` local
- NUNCA compartilhe essas chaves publicamente!
- Você pode verificar suas chaves no arquivo `.env` do projeto

### Passo 6: Deploy!
1. Clique em **"Create Web Service"**
2. Aguarde o build (pode levar 2-5 minutos)
3. Pronto! Você terá um link como: `https://assistente-puerperio.onrender.com`

## 📱 Compartilhar com o Chefe
Depois do deploy, você terá um link permanente tipo:
```
https://assistente-puerperio.onrender.com
```

Este link funciona de qualquer lugar do mundo! 🌍

## 🔄 Atualizações Futuras
Sempre que você fizer push no GitHub, o Render faz deploy automático (se `autoDeploy: true` estiver no `render.yaml`).

## ⚙️ Alternativa Rápida: ngrok
Se precisar de algo **super rápido** (mas temporário):

1. Baixe ngrok: https://ngrok.com/download
2. Execute o script que criei: `iniciar-com-ngrok.bat`
3. O ngrok fornecerá um link temporário (expira em algumas horas)

---

✅ **Recomendação**: Use o Render para uma demonstração profissional permanente!
