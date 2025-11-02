# 🚀 Guia de Deploy - Assistente Puerpério

## Opção 1: Render.com (✅ RECOMENDADO)

### Passos para Deploy

1. **Criar conta no Render**
   - Acesse https://render.com
   - Crie uma conta gratuita (conecte com GitHub)

2. **Conectar Repositório**
   - No dashboard, clique em "New +" → "Web Service"
   - Conecte seu repositório GitHub
   - Render detectará automaticamente o arquivo `render.yaml`

3. **Configurar Variáveis de Ambiente**
   - No painel do serviço, vá em "Environment"
   - Adicione as variáveis:
     ```
     OPENAI_API_KEY=sua_chave_aqui (opcional)
     PORT=10000
     ```

4. **Deploy Automático**
   - Render usará o arquivo `render.yaml` que já está configurado
   - O deploy será automático em cada push no repositório
   - URL: `https://assistente-puerperio.onrender.com`

### Configurações do Render

O arquivo `render.yaml` já está configurado:
- **Build**: `pip install -r requirements.txt`
- **Start**: `gunicorn wsgi:app`
- **Plan**: Free
- **Region**: Oregon (USA)

---

## Opção 2: Railway.app

### Passos para Deploy

1. **Criar conta no Railway**
   - Acesse https://railway.app
   - Crie uma conta gratuita ($5 de crédito mensal)

2. **Deploy o Projeto**
   - Clique em "New Project"
   - Selecione "Deploy from GitHub"
   - Escolha seu repositório

3. **Configurar**
   - Railway detecta automaticamente Python/Flask
   - Adicione variáveis de ambiente:
     ```
     OPENAI_API_KEY=sua_chave_aqui (opcional)
     PORT=${{PORT}}
     ```

4. **Pronto!**
   - Railway cria uma URL automática
   - Deploy contínuo ativado

---

## Opção 3: Fly.io

### Passos para Deploy

1. **Instalar Fly CLI**
   ```bash
   # Windows (PowerShell)
   iwr https://fly.io/install.ps1 -useb | iex
   ```

2. **Criar Conta**
   ```bash
   fly auth signup
   ```

3. **Deploy**
   ```bash
   cd caminho/do/projeto
   fly launch
   ```

4. **Configurar Variáveis**
   ```bash
   fly secrets set OPENAI_API_KEY=sua_chave_aqui
   ```

---

## Opção 4: PythonAnywhere

### Passos para Deploy

1. **Criar conta**
   - Acesse https://www.pythonanywhere.com
   - Plano Beginner: $5/mês

2. **Upload do Código**
   - Via interface web ou Git:
     ```bash
     git clone seu-repositorio
     ```

3. **Configurar Web App**
   - Vá em "Web" → "Add new web app"
   - Escolha Flask
   - Source code: seu diretório
   - WSGI file: edite e use:
     ```python
     import sys
     sys.path.insert(0, '/home/seu-usuario/chatbot-puerperio')
     
     from wsgi import app
     
     if __name__ == "__main__":
         app.run()
     ```

---

## ⚙️ Variáveis de Ambiente

No dashboard da plataforma, configure:

```env
# Opcional - Para respostas com IA
OPENAI_API_KEY=sk-sua-chave-aqui

# Porta (geralmente configurada automaticamente)
PORT=5000
```

---

## 🧪 Testar Localmente antes do Deploy

```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar com Python
python wsgi.py

# OU com Gunicorn (Linux/Mac)
gunicorn wsgi:app --bind 0.0.0.0:5000

# Testar
curl http://localhost:5000
```

---

## 📝 Estrutura de Arquivos Importantes

```
chatbot-puerperio/
├── Procfile              # Configuração Heroku/Render
├── render.yaml           # Configuração Render
├── wsgi.py              # Entry point WSGI
├── requirements.txt     # Dependências Python
├── backend/
│   ├── app.py           # Aplicação Flask
│   ├── templates/       # HTML
│   └── static/          # CSS/JS
└── dados/               # Base de conhecimento JSON
```

---

## 🔍 Verificar se Deploy Funcionou

1. **Endpoint de Status**
   ```bash
   curl https://sua-url.com/teste
   ```

2. **Testar Interface Web**
   - Acesse a URL fornecida pela plataforma
   - Deve ver a interface do chatbot

3. **Testar API**
   ```bash
   curl -X POST https://sua-url.com/api/chat \
     -H "Content-Type: application/json" \
     -d '{"pergunta":"Olá, como estou?"}'
   ```

---

## 🚨 Solução de Problemas

### Erro: "ModuleNotFoundError"
- Verifique se todas as dependências estão em `requirements.txt`
- Execute: `pip install -r requirements.txt` localmente

### Erro: "Port already in use"
- Deixe a plataforma definir a porta automaticamente
- Use variável `PORT` do ambiente

### Erro: "Template not found"
- Verifique se `backend/templates/` existe
- Verifique permissões de arquivos

### App "dorme" no Render (Free)
- Normal no plano gratuito
- Primeira requisição após inatividade demora ~30s
- Considere Railway ou Fly.io para evitar dormência

---

## 💰 Comparação de Custos

| Plataforma | Plano Gratuito | Observação |
|------------|---------------|------------|
| Render | ✅ Sim | App "dorme" após inatividade |
| Railway | $5 crédito/mês | Sem dormência |
| Fly.io | ✅ Limitado | Muito generoso |
| PythonAnywhere | ❌ | $5/mês mais barato |
| Heroku | ❌ | Apenas pago agora |

---

## ✅ Pronto para Deploy!

Escolha a plataforma e siga os passos acima. **Render.com é a mais simples** para começar!

Qualquer dúvida, consulte a documentação oficial da plataforma escolhida.

