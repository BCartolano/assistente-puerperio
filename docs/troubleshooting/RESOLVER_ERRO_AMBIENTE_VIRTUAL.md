# Como Resolver o Erro "Error while creating virtual environment"

## ✅ Solução Rápida

O erro é apenas do Cursor tentando criar um novo ambiente virtual. **Você já tem um ambiente virtual funcionando!**

### Opção 1: Selecionar o Interpretador Python Existente (RECOMENDADO)

1. **No Cursor/VS Code:**
   - Pressione `Ctrl+Shift+P` (ou `Cmd+Shift+P` no Mac)
   - Digite: `Python: Select Interpreter`
   - Selecione: `Python 3.14.2 ('venv': venv) .\backend\venv\Scripts\python.exe`

2. **Ou clique no botão "Select Python Interpreter"** na notificação de erro e selecione o interpretador existente.

### Opção 2: Fechar a Notificação

- **Clique no "X"** na notificação de erro para fechá-la
- O ambiente virtual já existe e funciona, então você pode ignorar o erro

### Opção 3: Criar um Arquivo de Configuração (Opcional)

Se o erro continuar aparecendo, crie um arquivo `.vscode/settings.json` na raiz do projeto:

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/backend/venv/Scripts/python.exe",
    "python.terminal.activateEnvironment": true,
    "python.venvPath": "${workspaceFolder}/backend"
}
```

## 🚀 Como Usar o Projeto

Você **não precisa** criar um novo ambiente virtual! Use o que já existe:

### 1. Ativar o Ambiente Virtual (PowerShell):
```powershell
.\backend\venv\Scripts\Activate.ps1
```

### 2. Instalar Dependências (se necessário):
```powershell
pip install -r requirements.txt
```

### 3. Iniciar o Servidor:
```powershell
python start.py
```

## 📝 Verificação

Para verificar se tudo está funcionando:

```powershell
# Verificar Python
python --version

# Verificar ambiente virtual
.\backend\venv\Scripts\python.exe --version

# Verificar pip
pip --version
```

## ⚠️ Nota Importante

O erro **não impede** o funcionamento do projeto. É apenas uma notificação do Cursor tentando criar um ambiente virtual automaticamente. Você pode:

- ✅ Ignorar o erro (clicar no X)
- ✅ Selecionar o interpretador existente
- ✅ Continuar usando `python start.py` normalmente

O ambiente virtual em `backend/venv` já está pronto e funcionando! 🎉
