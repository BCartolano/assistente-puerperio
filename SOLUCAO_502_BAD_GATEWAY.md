# 🔧 Solução para Erro 502 Bad Gateway

## 📋 Diagnóstico

O erro **502 Bad Gateway** ocorre quando há um proxy (NGROK ou Render) entre você e o servidor Flask, mas esse proxy não consegue se conectar ao servidor backend.

## ✅ Status Atual

- ✅ **Flask Server**: Funcionando corretamente na porta 5000
- ✅ **Rota /health**: Retorna 200 OK
- ✅ **Rota /**: Retorna 200 OK com conteúdo
- ⚠️ **NGROK/Render**: Problema de conexão

---

## 🔍 Causas Possíveis

### 1. **NGROK não está rodando ou está desconectado**
- O ngrok pode ter parado ou não estar conectado à porta 5000
- Solução: Reiniciar o ngrok

### 2. **Flask não está respondendo rápido o suficiente**
- Timeout entre proxy e Flask
- Solução: Verificar logs do Flask

### 3. **Render fazendo deploy mas com erro**
- O Render pode estar tentando se conectar mas o serviço não está ativo
- Solução: Verificar logs do Render

---

## 🛠️ Soluções

### Solução 1: Reiniciar Flask e NGROK

**Passo 1: Parar processos existentes**
```powershell
# Parar Flask
Get-Process python | Where-Object {$_.Path -like "*chatbot*"} | Stop-Process -Force

# Parar NGROK
Get-Process ngrok -ErrorAction SilentlyContinue | Stop-Process -Force
```

**Passo 2: Iniciar Flask**
```powershell
cd C:\Users\Cartolano\Documents\chatbot-puerperio
python start.py
```

**Passo 3: Aguardar Flask iniciar (5-10 segundos)**

**Passo 4: Verificar se Flask está rodando**
```powershell
curl http://localhost:5000/health
# Deve retornar: {"status": "ok", "message": "Servidor funcionando"}
```

**Passo 5: Iniciar NGROK (se necessário)**
```powershell
# Se ngrok.exe está na pasta do projeto:
.\ngrok.exe http 5000

# OU se ngrok está no PATH:
ngrok http 5000
```

### Solução 2: Verificar Render

**Se você está acessando via Render:**

1. Acesse: https://dashboard.render.com
2. Vá em "Services" > "assistente-puerperio"
3. Verifique os logs:
   - Procure por erros de inicialização
   - Verifique se o servidor está "Live"
4. Se houver erro, verifique:
   - Variáveis de ambiente configuradas
   - Build completado com sucesso
   - Health check retornando 200

### Solução 3: Testar Acesso Direto

**Teste se o Flask funciona localmente:**
```powershell
# Teste 1: Health check
curl http://localhost:5000/health

# Teste 2: Página principal
curl http://localhost:5000/

# Teste 3: Navegador
# Abra: http://localhost:5000
```

Se funcionar localmente mas não via proxy, o problema é no proxy (NGROK/Render).

---

## 🔄 Reiniciar Tudo (Solução Completa)

### Script PowerShell para reiniciar tudo:

```powershell
# Parar tudo
Write-Host "Parando processos..."
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*chatbot*"} | Stop-Process -Force
Get-Process ngrok -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

# Iniciar Flask
Write-Host "Iniciando Flask..."
cd C:\Users\Cartolano\Documents\chatbot-puerperio
Start-Process python -ArgumentList "start.py" -WindowStyle Normal

# Aguardar
Write-Host "Aguardando Flask iniciar..."
Start-Sleep -Seconds 8

# Verificar
Write-Host "Verificando Flask..."
$health = Invoke-WebRequest -Uri "http://localhost:5000/health" -UseBasicParsing -TimeoutSec 3 -ErrorAction SilentlyContinue
if ($health.StatusCode -eq 200) {
    Write-Host "✅ Flask está funcionando!"
    
    # Iniciar NGROK se existir
    if (Test-Path "ngrok.exe") {
        Write-Host "Iniciando NGROK..."
        Start-Process -FilePath "ngrok.exe" -ArgumentList "http","5000" -WindowStyle Normal
        Start-Sleep -Seconds 3
        Write-Host "✅ NGROK iniciado!"
        Write-Host "Acesse http://localhost:4040 para ver o dashboard do ngrok"
    } else {
        Write-Host "⚠️ ngrok.exe não encontrado. Instale o ngrok primeiro."
    }
} else {
    Write-Host "❌ Flask não está respondendo. Verifique os logs."
}
```

---

## 📝 Checklist de Verificação

- [ ] Flask está rodando na porta 5000
- [ ] `/health` retorna 200 OK
- [ ] `/` retorna 200 OK
- [ ] NGROK está apontando para porta 5000 (se usando)
- [ ] Render está com deploy ativo (se usando)
- [ ] Sem erros nos logs do Flask
- [ ] Sem erros nos logs do proxy (NGROK/Render)

---

## 🆘 Se Nada Funcionar

1. **Verifique os logs do Flask:**
   - Procure por erros de inicialização
   - Verifique se todos os arquivos JSON foram carregados
   - Verifique se o banco de dados está acessível

2. **Verifique firewall/antivírus:**
   - Pode estar bloqueando conexões
   - Adicione exceção para porta 5000

3. **Reinstale dependências:**
   ```powershell
   pip install -r requirements.txt --force-reinstall
   ```

4. **Teste em outra porta:**
   ```python
   # Em app.py, mude para:
   app.run(debug=True, host='0.0.0.0', port=8080)
   # E use: ngrok http 8080
   ```

---

**Última atualização:** 2025-01-27  
**Status Flask:** ✅ Funcionando localmente  
**Status Proxy:** ⚠️ Verificar NGROK/Render

