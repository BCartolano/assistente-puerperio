# 🚂 Guia de Deploy no Railway

Este guia explica como fazer deploy do Chatbot Puerpério no Railway.

## 📋 Pré-requisitos

- Conta no GitHub com o repositório `assistente-puerperio`
- Conta no Railway (https://railway.app)
- Chave API do Google Gemini (https://makersuite.google.com/app/apikey)

## 🚀 Passo a Passo

### 1. Conectar Railway ao GitHub

1. Acesse https://railway.app e faça login
2. Clique em **"New Project"**
3. Selecione **"Deploy from GitHub repo"**
4. Autorize o Railway a acessar seus repositórios (se necessário)
5. Selecione o repositório `Cartolanoo/assistente-puerperio`

### 2. Configurar Variáveis de Ambiente

No projeto do Railway, vá em **Variables** e adicione as seguintes variáveis:

#### ⚠️ OBRIGATÓRIAS (Mínimo para funcionar)

```env
SECRET_KEY=sua-chave-secreta-super-segura-aleatoria-aqui
GEMINI_API_KEY=sua_chave_gemini_aqui
FLASK_ENV=production
```

**Como gerar SECRET_KEY:**
```python
import secrets
secrets.token_hex(32)
```

**Como obter GEMINI_API_KEY:**
1. Acesse https://makersuite.google.com/app/apikey
2. Faça login com sua conta Google
3. Crie uma nova API key
4. Copie e cole no Railway

#### 📧 OPCIONAIS (Para envio de emails)

Se você quiser que o sistema envie emails de verificação e recuperação de senha:

**Opção 1: Gmail (Recomendado)**
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=seu_email@gmail.com
MAIL_PASSWORD=sua_senha_app_gerada_aqui
MAIL_DEFAULT_SENDER=seu_email@gmail.com
```

⚠️ **IMPORTANTE para Gmail:**
- NÃO use a senha normal da sua conta!
- Você precisa:
  1. Ativar Verificação em Duas Etapas: https://myaccount.google.com/security
  2. Gerar Senha de App: https://myaccount.google.com/apppasswords
     - Selecione "Mail" e "Outro (nome personalizado)" → "Railway Chatbot"
     - Copie a senha gerada (16 caracteres sem espaços)
     - Use essa senha no `MAIL_PASSWORD`

**Opção 2: Outlook/Hotmail**
```env
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=seu_email@outlook.com
MAIL_PASSWORD=sua_senha_normal
MAIL_DEFAULT_SENDER=noreply@chatbot-puerperio.com
```

**Opção 3: Yahoo Mail**
```env
MAIL_SERVER=smtp.mail.yahoo.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=seu_email@yahoo.com
MAIL_PASSWORD=sua_senha_normal
MAIL_DEFAULT_SENDER=noreply@chatbot-puerperio.com
```

#### 🌐 OPCIONAL (URL Base)

Se você tiver um domínio próprio configurado no Railway:

```env
BASE_URL=https://seu-dominio.com
```

Se não configurar, o Railway vai usar automaticamente a URL gerada (ex: `https://seu-projeto.up.railway.app`)

### 3. Configurar o Deploy

O Railway deve detectar automaticamente que é um projeto Python. Se não detectar:

1. Vá em **Settings** → **Deploy**
2. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn wsgi:app`

O arquivo `railway.json` já está configurado, então o Railway deve usar automaticamente.

### 4. Configurar Domínio (Opcional)

1. No projeto, vá em **Settings** → **Domains**
2. Clique em **"Generate Domain"** para obter uma URL gratuita
3. Ou configure um domínio personalizado (requer configuração de DNS)

### 5. Monitorar o Deploy

1. Vá na aba **Deployments** para ver o progresso
2. Clique nos logs para ver o que está acontecendo
3. Procure por mensagens como:
   - ✅ `App Flask carregado com sucesso`
   - ✅ `Gemini disponível: Sim`
   - ❌ Erros (se houver)

## 🔍 Verificando se Está Funcionando

Após o deploy, acesse a URL do seu projeto e verifique:

1. ✅ A página inicial carrega
2. ✅ O chatbot responde
3. ✅ As funcionalidades estão operacionais

## 📝 Variáveis de Ambiente Resumidas

### Obrigatórias
- `SECRET_KEY` - Chave secreta para sessões Flask
- `GEMINI_API_KEY` - Chave da API do Google Gemini
- `FLASK_ENV=production` - Ambiente de produção

### Opcionais (Email)
- `MAIL_SERVER` - Servidor SMTP
- `MAIL_PORT` - Porta SMTP (geralmente 587)
- `MAIL_USE_TLS` - Usar TLS (True/False)
- `MAIL_USERNAME` - Email do remetente
- `MAIL_PASSWORD` - Senha do email ou senha de app
- `MAIL_DEFAULT_SENDER` - Email remetente padrão

### Opcionais (URL)
- `BASE_URL` - URL base do aplicativo (para links de email)

## 🐛 Solução de Problemas

### Erro: "App Flask não carregado"
- Verifique se o arquivo `wsgi.py` existe na raiz do projeto
- Verifique os logs do Railway para mais detalhes

### Erro: "Gemini não disponível"
- Verifique se `GEMINI_API_KEY` está configurada corretamente
- Verifique se a chave é válida

### Emails não são enviados
- Verifique se as variáveis de email estão configuradas
- Para Gmail, certifique-se de usar Senha de App (não a senha normal)
- Verifique os logs do Railway para erros de SMTP

### Erro 502 Bad Gateway
- Verifique se o `Procfile` está correto
- Verifique se o comando `gunicorn wsgi:app` está funcionando
- Verifique os logs do Railway

## 📚 Recursos Adicionais

- [Documentação do Railway](https://docs.railway.app)
- [Documentação do Flask](https://flask.palletsprojects.com)
- [Documentação do Gunicorn](https://gunicorn.org)

## ✅ Checklist de Deploy

- [ ] Repositório conectado ao Railway
- [ ] Variável `SECRET_KEY` configurada
- [ ] Variável `GEMINI_API_KEY` configurada
- [ ] Variável `FLASK_ENV=production` configurada
- [ ] Variáveis de email configuradas (opcional)
- [ ] Deploy executado com sucesso
- [ ] Aplicação acessível via URL
- [ ] Chatbot funcionando corretamente
