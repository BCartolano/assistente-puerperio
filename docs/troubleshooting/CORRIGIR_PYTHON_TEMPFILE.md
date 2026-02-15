# Corrigir erro "No module named 'tempfile'" (Python 3.14)

## O que está acontecendo

O comando `python -c "import tempfile"` falha **mesmo fora do projeto**. Isso indica que o **ambiente Python 3.14** que você está usando está incompleto ou com problema — o módulo `tempfile` faz parte da biblioteca padrão e deveria sempre existir.

Python 3.14 ainda está em fase de desenvolvimento; em alguns instaladores ou builds (ex.: Microsoft Store, builds mínimos) a stdlib pode vir incompleta.

## Solução recomendada: usar Python 3.11 ou 3.12

Use uma versão estável do Python e recrie o ambiente virtual.

### 1. Instalar Python 3.12 (ou 3.11)

- Baixe o instalador em: https://www.python.org/downloads/
- Escolha **Python 3.12.x** (ou 3.11.x) para Windows.
- Na instalação, marque **"Add Python to PATH"**.
- Se quiser, desmarque "Install for all users" e use "Customize" para instalar em uma pasta simples (ex.: `C:\Python312`).

### 2. Verificar se o Python 3.12 está no PATH

No PowerShell:

```powershell
py -3.12 -c "import tempfile; print('OK:', tempfile.__file__)"
```

Se aparecer `OK: ...\tempfile.py`, esse Python está correto.

### 3. Recriar o ambiente virtual com Python 3.12

Na pasta do projeto (`chatbot-puerperio`):

```powershell
# Desative o venv atual (se estiver ativo)
deactivate

# Remova o venv antigo
Remove-Item -Recurse -Force .venv

# Crie um novo venv com Python 3.12
py -3.12 -m venv .venv

# Ative o novo venv
.\.venv\Scripts\Activate.ps1

# Instale as dependências
pip install -r requirements.txt

# Teste
python -c "import tempfile; print('tempfile OK')"
python start.py
```

Se você tiver apenas `python` apontando para 3.12 (e não usar `py`):

```powershell
Remove-Item -Recurse -Force .venv
& "C:\Python312\python.exe" -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python start.py
```

### 4. Se tiver várias versões: ver qual usar

```powershell
py --list
```

Use a versão **3.12** ou **3.11** (ex.: `py -3.12` ou `py -3.11`) para criar o venv e rodar o projeto.

---

**Resumo:** o erro não é do código do projeto e não se resolve mudando `start.py`. É preciso usar um Python estável (3.11 ou 3.12) com instalação completa e recriar o `.venv` com esse interpretador.
