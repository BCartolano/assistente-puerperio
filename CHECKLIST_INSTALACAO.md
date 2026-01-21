# ✅ Checklist de Instalação - Chatbot Puerpério

## 📋 Status Atual do Sistema

### ❌ Python
- **Status**: NÃO INSTALADO
- **Versão Requerida**: 3.11.0 (mínimo 3.8+)
- **Ação**: Instalar Python 3.11 do site oficial
- **Link**: https://www.python.org/downloads/

### ❌ pip
- **Status**: NÃO INSTALADO (depende do Python)
- **Ação**: Será instalado automaticamente com Python ou via `python -m ensurepip`

### ⏳ Ambiente Virtual
- **Status**: PENDENTE (será criado pelo script de setup)
- **Localização**: `backend\venv\`
- **Ação**: Será criado automaticamente pelo script

### ⏳ Dependências Python
- **Status**: PENDENTE (aguardando instalação)
- **Arquivo**: `requirements.txt`
- **Ação**: Será instalado automaticamente pelo script

### ⏳ Arquivo .env
- **Status**: PENDENTE (será criado do template)
- **Template**: `env_example.txt`
- **Ação**: Será criado automaticamente pelo script

---

## 🔧 Instruções de Instalação Manual

### 1. Instalar Python 3.11

#### Windows:
1. Acesse: https://www.python.org/downloads/
2. Baixe **Python 3.11.x** (Windows installer 64-bit)
3. Execute o instalador
4. **⚠️ IMPORTANTE**: Marque a opção **"Add Python to PATH"**
5. Clique em "Install Now"
6. Aguarde a conclusão

#### Verificar Instalação:
```powershell
python --version
# Deve mostrar: Python 3.11.x
```

### 2. Atualizar pip

```powershell
python -m pip install --upgrade pip
```

### 3. Criar Ambiente Virtual

```powershell
python -m venv backend\venv
```

### 4. Ativar Ambiente Virtual

```powershell
# PowerShell
backend\venv\Scripts\Activate.ps1

# CMD
backend\venv\Scripts\activate.bat
```

### 5. Instalar Dependências

```powershell
# Com ambiente virtual ativado
pip install -r requirements.txt
```

### 6. Configurar NLTK (Opcional)

```powershell
python -c "import nltk; nltk.download('punkt', quiet=True)"
```

### 7. Criar Arquivo .env

```powershell
# Copiar template
Copy-Item env_example.txt .env

# Editar .env e configurar:
# - OPENAI_API_KEY (obrigatório)
# - SECRET_KEY (gerar chave segura)
```

---

## 🚀 Instalação Automática (Recomendada)

Execute o script de setup automático:

```powershell
.\setup-ambiente.ps1
```

O script irá:
- ✅ Verificar Python
- ✅ Verificar pip
- ✅ Criar ambiente virtual
- ✅ Instalar todas as dependências
- ✅ Configurar NLTK
- ✅ Criar arquivo .env

---

## 📊 Verificação Pós-Instalação

Execute o script de verificação:

```powershell
.\verificar-instalacao.ps1
```

Ou verifique manualmente:

```powershell
# Verificar Python
python --version

# Verificar pip
python -m pip --version

# Verificar Flask
python -c "import flask; print(flask.__version__)"

# Verificar OpenAI
python -c "import openai; print(openai.__version__)"

# Verificar ambiente virtual
Test-Path backend\venv\Scripts\python.exe

# Verificar arquivo .env
Test-Path .env
```

---

## ⚠️ Problemas Comuns

### Python não encontrado
- **Causa**: Python não está no PATH
- **Solução**: Reinstalar Python marcando "Add Python to PATH"

### Erro ao criar ambiente virtual
- **Causa**: Permissões ou Python não instalado corretamente
- **Solução**: Executar PowerShell como Administrador

### Erro ao instalar dependências
- **Causa**: Conexão com internet ou versão do pip desatualizada
- **Solução**: 
  ```powershell
  python -m pip install --upgrade pip
  python -m pip install -r requirements.txt
  ```

### Erro de encoding no Windows
- **Causa**: Console não configurado para UTF-8
- **Solução**: O script `setup-ambiente.ps1` já configura automaticamente

---

## 📝 Próximos Passos Após Instalação

1. ✅ Editar arquivo `.env` e configurar:
   - `OPENAI_API_KEY` (obrigatório)
   - `SECRET_KEY` (gerar chave segura)
   - Configurações de email (opcional)

2. ✅ Iniciar o servidor:
   ```powershell
   .\iniciar-servidor.ps1
   # OU
   python start.py
   ```

3. ✅ Acessar: http://localhost:5000

---

## 🔍 Comandos Úteis

```powershell
# Ativar ambiente virtual
backend\venv\Scripts\Activate.ps1

# Desativar ambiente virtual
deactivate

# Verificar dependências instaladas
pip list

# Atualizar uma dependência específica
pip install --upgrade nome-do-pacote

# Verificar versão de um pacote
pip show nome-do-pacote
```
