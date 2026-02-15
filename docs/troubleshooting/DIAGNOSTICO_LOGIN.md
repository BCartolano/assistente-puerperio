# 🔍 Diagnóstico do Problema de Login

## ✅ Correções Aplicadas

1. **DispatcherMiddleware corrigido**: Agora roteia apenas `/api/v1/*` para FastAPI
2. **Rotas Flask preservadas**: `/api/login`, `/api/register`, etc. continuam no Flask

## 🚨 Passo a Passo para Resolver

### 1. **PARAR o servidor atual** (CRÍTICO!)
```powershell
# No terminal onde o servidor está rodando, pressione:
Ctrl + C
```

### 2. **Verificar se o servidor parou completamente**
```powershell
# Deve mostrar nenhum processo na porta 5000
netstat -ano | findstr :5000
```

### 3. **Ativar ambiente virtual**
```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. **Reiniciar o servidor**
```powershell
python start.py
```

### 5. **Verificar as mensagens de inicialização**

Quando o servidor iniciar, você DEVE ver:
```
✅ FastAPI integrado ao Flask - /api/v1/* roteado para FastAPI
   📍 FastAPI disponível em: http://localhost:5000/api/v1/facilities/search
   ✅ Rotas Flask /api/login, /api/register, etc. permanecem funcionando
```

### 6. **Testar o login novamente**

Abra o navegador e tente fazer login.

## 🔧 Se o Problema Persistir

### Opção A: Desabilitar temporariamente o FastAPI

Se o problema continuar, podemos desabilitar temporariamente a integração do FastAPI para isolar o problema:

1. Editar `backend/app.py`
2. Comentar as linhas 486-533 (integração do FastAPI)
3. Reiniciar o servidor

### Opção B: Verificar logs do servidor

Quando você tentar fazer login, veja o terminal onde o servidor está rodando e procure por:
- `[LOGIN] Tentativa de login - Email: ...`
- Qualquer mensagem de erro em vermelho

### Opção C: Verificar o banco de dados

```powershell
# Verificar se o banco existe
Test-Path backend\users.db

# Verificar se há usuários
python -c "import sqlite3; conn = sqlite3.connect('backend/users.db'); print(conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]); conn.close()"
```

## 📝 Informações Importantes

- **Servidor deve ser reiniciado** após qualquer mudança no código
- **Ambiente virtual deve estar ativo** antes de rodar `python start.py`
- **Ngrok também deve ser reiniciado** se estiver usando: `ngrok http 5000`
