# 🔧 Como Corrigir Erro ngrok ERR_NGROK_8012

## ❌ Problema

O erro `ERR_NGROK_8012` indica que o ngrok está tentando conectar na porta **80**, mas o servidor Flask está rodando na porta **5000**.

## ✅ Solução Rápida

### Passo 1: Parar qualquer processo ngrok rodando
```powershell
Stop-Process -Name "ngrok" -Force -ErrorAction SilentlyContinue
```

### Passo 2: Verificar se o Flask está rodando na porta 5000
```powershell
netstat -ano | Select-String ":5000 " | Select-String "LISTENING"
```

Se não estiver rodando, inicie o servidor:
```powershell
python start.py
```

### Passo 3: Iniciar o ngrok na porta CORRETA (5000)

**Método 1: Usar o script automático (RECOMENDADO)**
```powershell
.\iniciar-com-ngrok.ps1
```

**Método 2: Comando manual**
```powershell
# Se ngrok.exe está na pasta do projeto:
.\ngrok.exe http 5000

# OU se está instalado globalmente:
ngrok http 5000
```

## 🔍 Verificar Porta do Flask

O Flask sempre roda na porta **5000** por padrão neste projeto. Você pode verificar:

1. Quando inicia o servidor, verá:
   ```
   Running on http://127.0.0.1:5000
   ```

2. Ou verifique diretamente:
   ```powershell
   netstat -ano | Select-String ":5000"
   ```

## ⚠️ Importante

- **Flask usa porta 5000** (não 80)
- **ngrok deve apontar para 5000** (não 80)
- Se você iniciou o ngrok manualmente, sempre use: `ngrok http 5000`

## 📝 Exemplo Correto

```powershell
# Terminal 1: Iniciar Flask
python start.py

# Terminal 2: Iniciar ngrok (DEPOIS que Flask iniciar)
ngrok http 5000
```

## 🎯 Resultado Esperado

Quando iniciar o ngrok corretamente, você verá algo como:

```
Forwarding   https://abc123.ngrok-free.app -> http://localhost:5000
```

E o link `https://abc123.ngrok-free.app` funcionará corretamente!
