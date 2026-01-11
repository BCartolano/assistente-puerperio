# 📋 Requisitos e Instalação Completa do Projeto

Este documento lista **TODAS** as linguagens, programas e ferramentas necessárias para reinstalar o projeto após formatação do computador.

---

## 🐍 Linguagens de Programação

### Python (OBRIGATÓRIO)
- **Versão:** Python 3.11.0 (mínimo 3.8+)
- **Onde baixar:** https://www.python.org/downloads/
- **Como instalar:**
  1. Baixe o instalador do Python 3.11 ou superior
  2. **IMPORTANTE:** Durante a instalação, marque a opção "Add Python to PATH"
  3. Instale normalmente

### HTML5, CSS3 e JavaScript
- **Status:** Não requer instalação (são suportados nativamente pelos navegadores)
- **Observação:** O projeto usa JavaScript ES6+ (moderno), mas não requer Node.js

---

## 📦 Gerenciador de Pacotes Python

### pip (Vem com Python)
- **Status:** Instalado automaticamente com Python
- **Como verificar:** Abra o terminal e digite `pip --version`

---

## 🛠️ Programas e Ferramentas Necessárias

### 1. Git (OBRIGATÓRIO para versionamento)
- **O que é:** Sistema de controle de versão
- **Onde baixar:** https://git-scm.com/download/win
- **Como instalar:**
  1. Baixe o instalador Git for Windows
  2. Instale com todas as opções padrão
  3. Durante instalação, escolha "Git from the command line and also from 3rd-party software"
- **Como verificar:** Abra PowerShell e digite `git --version`

### 2. PowerShell (JÁ VEM INSTALADO no Windows)
- **Status:** Já está disponível no Windows 10/11
- **Versão:** 5.1 ou superior (já incluído no Windows)
- **Observação:** Os scripts `.ps1` do projeto usam PowerShell

### 3. NGROK (OPCIONAL - Para desenvolvimento/testes)
- **O que é:** Ferramenta para criar túneis HTTPS públicos temporários
- **Quando usar:** Para testar localmente e compartilhar o projeto temporariamente
- **Onde baixar:** https://ngrok.com/download
- **Como instalar:**
  1. Baixe `ngrok.exe`
  2. Coloque o arquivo na pasta raiz do projeto (`chatbot-puerperio/`)
  3. OU adicione ao PATH do sistema
- **Observação:** Não é obrigatório, mas útil para testes

---

## 📚 Frameworks e Bibliotecas Python

Todas as dependências estão listadas em `requirements.txt` e serão instaladas automaticamente. Principais:

### Backend
- **Flask 3.1.2** - Framework web principal
- **Gunicorn 23.0.0** - Servidor WSGI para produção
- **flask-login 0.6.3** - Autenticação de usuários
- **bcrypt 4.1.2** - Criptografia de senhas
- **flask-mail 0.10.0** - Envio de e-mails
- **flask-compress** - Compressão de respostas

### IA e Processamento
- **openai >= 1.0.0** - Integração com API da OpenAI (OBRIGATÓRIO)
- **nltk >= 3.8** - Processamento de linguagem natural

### Outras Dependências
- **python-dotenv 1.1.1** - Gerenciamento de variáveis de ambiente
- **pydantic 2.12.0** - Validação de dados
- **httpx 0.28.1** - Cliente HTTP moderno
- E outras dependências automáticas

---

## 💾 Banco de Dados

### SQLite (JÁ VEM COM PYTHON)
- **Status:** Incluído automaticamente com Python
- **Observação:** Não requer instalação separada
- **Arquivo:** `backend/users.db` (criado automaticamente)

---

## 🌐 APIs Externas

### OpenAI API (OBRIGATÓRIO)
- **O que é:** API de inteligência artificial para respostas do chatbot
- **Como configurar:**
  1. Acesse: https://platform.openai.com/api-keys
  2. Crie uma conta (se necessário)
  3. Adicione créditos na sua conta
  4. Gere uma chave de API
  5. Adicione no arquivo `.env`:
     ```
     OPENAI_API_KEY=sua_chave_aqui
     USE_AI=true
     ```

---

## 🚀 Guia de Instalação Passo a Passo

### Passo 1: Instalar Python
```powershell
# Verificar se Python está instalado
python --version

# Deve mostrar: Python 3.11.x ou superior
```

### Passo 2: Instalar Git
```powershell
# Verificar se Git está instalado
git --version

# Deve mostrar: git version 2.x.x ou superior
```

### Passo 3: Clonar ou Baixar o Projeto
```powershell
# Se o projeto está no Git:
git clone <url-do-repositorio>
cd chatbot-puerperio

# OU se já tem o projeto localmente:
cd C:\Users\bruno\Documents\chatbot-puerperio
```

### Passo 4: Criar Ambiente Virtual
```powershell
# Criar ambiente virtual na pasta backend
python -m venv backend\venv

# OU na raiz (se preferir)
python -m venv venv
```

### Passo 5: Ativar Ambiente Virtual
```powershell
# Windows PowerShell
backend\venv\Scripts\Activate.ps1

# Se der erro de execução de scripts:
# Execute no PowerShell como Administrador:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Passo 6: Instalar Dependências
```powershell
# Com ambiente virtual ativo:
pip install -r requirements.txt

# OU usar o script de inicialização (instala automaticamente):
python start.py
```

### Passo 7: Configurar Variáveis de Ambiente
```powershell
# Copiar arquivo de exemplo
copy env_example.txt .env

# Editar o arquivo .env e adicionar:
OPENAI_API_KEY=sua_chave_openai_aqui
USE_AI=true
```

### Passo 8: Baixar Dados do NLTK (Primeira vez)
```powershell
# Com ambiente virtual ativo:
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### Passo 9: Iniciar o Servidor
```powershell
# Opção 1: Usando script de inicialização (RECOMENDADO)
python start.py

# Opção 2: Manualmente
cd backend
python app.py

# Opção 3: Com NGROK (se instalado)
.\iniciar-com-ngrok.ps1
```

---

## ✅ Checklist de Instalação

Marque cada item após instalar:

- [ ] Python 3.11 ou superior instalado
- [ ] Git instalado e configurado
- [ ] Projeto clonado/baixado
- [ ] Ambiente virtual criado (`backend\venv`)
- [ ] Ambiente virtual ativado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Arquivo `.env` criado e configurado
- [ ] Chave da API OpenAI configurada
- [ ] Dados do NLTK baixados
- [ ] Servidor inicia sem erros (`python start.py`)

---

## 🎯 Comandos Rápidos de Verificação

```powershell
# Verificar Python
python --version
pip --version

# Verificar Git
git --version

# Verificar se ambiente virtual está ativo
# Deve aparecer (venv) no início da linha
# Ou:
python -c "import sys; print(sys.prefix)"

# Verificar instalação do Flask
python -c "import flask; print(flask.__version__)"

# Verificar instalação da OpenAI
python -c "import openai; print(openai.__version__)"

# Verificar todas as dependências
pip list
```

---

## 🔧 Configurações Recomendadas do Git

Após instalar o Git, configure suas credenciais:

```powershell
git config --global user.name "Seu Nome"
git config --global user.email "seu.email@exemplo.com"
git config --global credential.helper manager-core
git config --global core.quotepath false
git config --global i18n.commitencoding utf-8
git config --global i18n.logoutputencoding utf-8
git config --global core.autocrlf true
```

**OU** use o script automático do projeto:
```powershell
.\configurar-git-terminal.ps1
```

---

## 📝 Notas Importantes

1. **Python PATH:** Sempre marque "Add Python to PATH" durante instalação
2. **PowerShell:** Pode ser necessário habilitar execução de scripts (como Administrador):
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
3. **Ambiente Virtual:** Sempre ative o ambiente virtual antes de trabalhar
4. **Chave OpenAI:** É obrigatória para o chatbot funcionar
5. **NLTK:** Baixe os dados na primeira execução (pode demorar alguns minutos)
6. **Porta 5000:** Certifique-se de que a porta 5000 não está em uso

---

## 🆘 Solução de Problemas Comuns

### Erro: "python não é reconhecido como comando"
**Solução:** Reinstale Python e marque "Add Python to PATH"

### Erro: "pip não é reconhecido como comando"
**Solução:** Instale Python novamente ou use `python -m pip` no lugar de `pip`

### Erro: "cannot execute script" (PowerShell)
**Solução:** Execute como Administrador:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Erro: "No module named 'flask'"
**Solução:** 
1. Ative o ambiente virtual
2. Execute `pip install -r requirements.txt`

### Erro: "Port 5000 is already in use"
**Solução:** Pare o processo usando a porta ou altere a porta no código

---

## 📚 Documentação Adicional

- **README.md** - Documentação principal do projeto
- **COMO_INICIAR_SERVIDOR.md** - Como iniciar o servidor
- **COMO_INSTALAR_NGROK.md** - Instalação do NGROK (se necessário)
- **README_DEPLOY.md** - Como fazer deploy em produção

---

## ✅ Resumo Rápido

**Obrigatório:**
1. Python 3.11+ (com pip)
2. Git
3. Chave da API OpenAI

**Opcional:**
- NGROK (para testes locais com acesso público)

**Instalação rápida:**
```powershell
# 1. Instalar Python 3.11+
# 2. Instalar Git
# 3. Clonar projeto
git clone <url>
cd chatbot-puerperio

# 4. Criar ambiente virtual
python -m venv backend\venv
backend\venv\Scripts\Activate.ps1

# 5. Instalar dependências
pip install -r requirements.txt

# 6. Configurar .env
copy env_example.txt .env
# Editar .env com sua chave OpenAI

# 7. Iniciar
python start.py
```

---

**Última atualização:** 2025
**Versão do projeto:** Compatível com Python 3.8+
