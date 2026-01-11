# Comandos para Teste Mobile - Guia Rápido

**Data:** 2025-01-27  
**Versão:** 1.0  
**Status:** ✅ Pronto para Uso

---

## 🚀 INICIAR SERVIDOR COM NGROK

### **Windows (PowerShell):**

```powershell
# Inicia Flask + ngrok automaticamente
.\iniciar-com-ngrok.ps1
```

**O que acontece:**
1. Flask inicia em `0.0.0.0:5000`
2. Aguarda 5 segundos para Flask iniciar
3. ngrok inicia e exibe URL pública (ex: `https://abc123.ngrok.io`)

**Copiar URL:** Procure por "Forwarding" no terminal do ngrok

---

## ✅ VERIFICAR ARQUIVOS ESTÁTICOS

### **Antes de Testar:**

```bash
# Verifica se todos os arquivos estão sendo servidos
python tests/verify_mobile_deploy.py

# Ou com URL do ngrok
python tests/verify_mobile_deploy.py https://abc123.ngrok.io
```

**Saída esperada:**
```
✓ /static/js/mobile-navigation.js (XXXX bytes)
✓ /static/js/toast-notification.js (XXXX bytes)
✓ /static/js/api-client.js (XXXX bytes)
✓ /static/js/chat.js (XXXX bytes)
✓ Todos os arquivos estão sendo servidos corretamente!
```

---

## 📊 LOGS EM TEMPO REAL

### **Monitorar `context_metrics.log`:**

**Windows (PowerShell):**
```powershell
# Últimas 20 linhas + atualização em tempo real
Get-Content logs\context_metrics.log -Wait -Tail 20

# Apenas últimas 50 linhas
Get-Content logs\context_metrics.log -Tail 50
```

**Linux/Mac:**
```bash
# Últimas 20 linhas + atualização em tempo real
tail -f logs/context_metrics.log

# Apenas últimas 50 linhas
tail -n 50 logs/context_metrics.log
```

### **Filtrar tags específicas:**

**Windows (PowerShell):**
```powershell
Get-Content logs\context_metrics.log | Select-String "cansaço|ansiedade|dúvida"
```

**Linux/Mac:**
```bash
grep -i "cansaço\|ansiedade\|dúvida" logs/context_metrics.log
```

### **Contar frequência de tags:**

**Windows (PowerShell):**
```powershell
Get-Content logs\context_metrics.log | ForEach-Object { ($_ -split '\|')[1].Trim() } | Group-Object | Sort-Object Count -Descending
```

**Linux/Mac:**
```bash
cat logs/context_metrics.log | cut -d'|' -f2 | sort | uniq -c | sort -rn
```

---

## 🔍 MONITORAR REQUISIÇÕES (FLASK)

### **Ver conexões ativas:**

**Windows (PowerShell):**
```powershell
netstat -an | findstr ":5000"
```

**Linux/Mac:**
```bash
lsof -i :5000
```

### **Ver logs do Flask:**

Os logs do Flask aparecem no terminal onde o Flask está rodando.

**Procurar por:**
- `[API_CHAT]` - Requisições de chat
- `[VACCINATION]` - Requisições de vacinação
- `[BROKEN_PIPE]` - Erros de conexão fechada

---

## 🐛 DEBUG DO KEYBOARD-OPEN

### **Ativar DEBUG_MODE:**

No console do navegador (F12), antes de carregar a página:

```javascript
window.DEBUG_MODE = true;
```

**Depois recarregue a página.** O indicador visual aparecerá no topo quando o teclado virtual for detectado.

### **Desativar DEBUG_MODE:**

```javascript
window.DEBUG_MODE = false;
```

---

## 📝 CHECKLIST PRÉ-TESTE

- [ ] Flask rodando em `0.0.0.0:5000`
- [ ] ngrok rodando e URL pública disponível
- [ ] `tests/verify_mobile_deploy.py` executado com sucesso
- [ ] `logs/context_metrics.log` sendo monitorado (outro terminal)
- [ ] Checklist da Sally impresso ou aberto (`docs/CHECKLIST_TESTE_MOBILE_SALLY.md`)
- [ ] Celular conectado na mesma rede ou usando URL do ngrok

---

## 🎯 DURANTE OS TESTES

### **Terminal 1: Flask**
- Observar logs de requisições
- Verificar se não há erros críticos

### **Terminal 2: Logs de Contexto**
```powershell
Get-Content logs\context_metrics.log -Wait -Tail 20
```
- Observar tags sendo detectadas
- Verificar se tags estão corretas

### **Terminal 3: Verificação de Arquivos (se necessário)**
```powershell
python tests/verify_mobile_deploy.py https://URL_DO_NGROK
```

---

**Versão:** 1.0  
**Status:** ✅ Pronto para Uso
