# Monitoramento de Testes Mobile - Logs e Métricas

**Criado por:** Winston (Architect)  
**Data:** 2025-01-27  
**Versão:** 1.0  
**Status:** ✅ Aprovado

---

## 🔍 MONITORAMENTO DE LOGS DE CONTEXTO

### **Arquivo: `logs/context_metrics.log`**

**Formato de Log:**
```
2025-01-27 17:00:00 | cansaço_extremo
2025-01-27 17:01:23 | ansiedade
2025-01-27 17:02:45 | dúvida_vacina
```

**Como Verificar:**

```bash
# Ver últimos 20 logs
tail -n 20 logs/context_metrics.log

# Ver logs em tempo real (durante testes)
tail -f logs/context_metrics.log

# Contar frequência de tags
cat logs/context_metrics.log | cut -d'|' -f2 | sort | uniq -c | sort -rn
```

**O que observar durante testes mobile:**
- ✅ Tags sendo detectadas corretamente (não apenas vazias)
- ✅ Tags específicas aparecem (ex: `cansaço_extremo`, `dúvida_vacina`)
- ✅ Timestamps corretos (timezone do servidor)
- ⚠️ Se NÃO houver tags detectadas, pode indicar problema na detecção

---

## 🔧 VERIFICAÇÃO DE CANCELAMENTO DE REQUISIÇÕES

### **Monitoramento de Requisições Ativas:**

**Backend (Flask):**
```python
# Em backend/app.py, adicionar log quando requisição é recebida/cancelada
@app.route('/api/chat', methods=['POST'])
def api_chat():
    logger.info(f"[API_CHAT] Requisição recebida de {request.remote_addr}")
    # ... código existente ...
```

**Frontend (Console do Navegador):**
```javascript
// Em api-client.js, logs já existem:
console.log('[APIClient] 🛑 Cancelando requisição para /api/chat');
console.log('[APIClient] ✅ Todas as requisições canceladas');
```

### **Verificar Durante Testes:**

1. **Abrir DevTools (F12) → Console**
2. **Trocar rapidamente entre abas (Chat → Vacinas → Chat)**
3. **Observar logs:**
   - ✅ `[APIClient] 🛑 Cancelando requisição` aparece quando troca de aba
   - ✅ `[APIClient] ✅ Todas as requisições canceladas` confirma cancelamento
   - ⚠️ Se NÃO aparecer, requisições podem estar sendo mantidas na memória

### **Monitoramento de Carga do Servidor:**

**Verificar conexões abertas:**
```bash
# Linux/Mac (se disponível)
netstat -an | grep :5000 | wc -l

# Ou via Python (adicionar ao app.py)
import psutil
connections = psutil.net_connections()
flask_conns = [c for c in connections if c.laddr.port == 5000]
print(f"Conexões Flask ativas: {len(flask_conns)}")
```

**Durante testes:**
- ✅ Número de conexões não aumenta descontroladamente
- ✅ Conexões fecham após requisição completa
- ⚠️ Se conexões acumularem, `cancelAll()` pode não estar funcionando

---

## 📊 SISTEMA DE LOGGING PARA TESTES

### **Arquivo de Log: `logs/test_metrics.log`** (criar se necessário)

**Formato:**
```json
{
    "timestamp": "2025-01-27T17:00:00Z",
    "test_type": "mobile_navigation",
    "event": "switch_section",
    "from": "chat",
    "to": "vacinas",
    "requests_cancelled": 1,
    "memory_usage_mb": 45.2,
    "connection_count": 2
}
```

### **Implementação Recomendada:**

```python
# Em backend/app.py, adicionar endpoint para logging de testes
@app.route('/api/test-log', methods=['POST'])
def test_log():
    """Endpoint para registrar métricas de testes mobile"""
    data = request.json
    log_file = os.path.join('logs', 'test_metrics.log')
    
    os.makedirs('logs', exist_ok=True)
    
    with open(log_file, 'a', encoding='utf-8') as f:
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            **data
        }
        f.write(json.dumps(log_entry) + '\n')
    
    return jsonify({'status': 'logged'}), 200
```

---

## 🔍 VERIFICAÇÃO DE STREAMING ADAPTATIVO (15ms)

### **Monitoramento no Console do Navegador:**

**Durante teste:**
1. Abrir DevTools → Console
2. Enviar mensagem no mobile
3. Observar logs:
   - ✅ `[STREAMING] Delay alto: XXXms` (se aparecer, indica problema)
   - ✅ Se NÃO aparecer, streaming está funcionando corretamente

**Adicionar logging estruturado:**

```javascript
// Em chat.js, método typewriterEffect
async typewriterEffect(element, text, speed = 25) {
    const isMobile = window.innerWidth <= 1023;
    const streamingSpeed = isMobile ? 15 : 25;
    
    const startTime = performance.now();
    let errorCount = 0;
    const delays = [];
    
    for (let i = 0; i < text.length; i++) {
        const charStart = performance.now();
        element.textContent += text[i];
        
        if (i < text.length - 1) {
            await new Promise(resolve => setTimeout(resolve, streamingSpeed));
            const charEnd = performance.now();
            const actualDelay = charEnd - charStart;
            delays.push(actualDelay);
            
            // Se delay muito alto (> 2x esperado), loga warning
            if (actualDelay > streamingSpeed * 2) {
                console.warn(`[STREAMING] Delay alto: ${actualDelay.toFixed(2)}ms (esperado: ${streamingSpeed}ms)`);
                errorCount++;
            }
        }
    }
    
    const totalTime = performance.now() - startTime;
    
    // Log estruturado (apenas em desenvolvimento)
    if (window.DEBUG_MODE) {
        console.log({
            event: 'streaming_complete',
            device: isMobile ? 'mobile' : 'desktop',
            speed: streamingSpeed,
            textLength: text.length,
            totalTime: totalTime.toFixed(2),
            avgDelay: (delays.reduce((a, b) => a + b, 0) / delays.length).toFixed(2),
            errors: errorCount
        });
    }
}
```

---

## 📈 MÉTRICAS A COLETAR DURANTE TESTES

### **1. Performance:**
- Tempo de resposta da API (ms)
- Tempo de streaming (ms)
- Delay médio por caractere (ms)
- Número de erros de streaming

### **2. Rede:**
- Tipo de conexão (2G, 3G, 4G, 5G)
- Velocidade média (Mbps)
- Taxa de erros (%)

### **3. Memória:**
- Uso de memória JavaScript (MB)
- Número de conexões ativas
- Requisições canceladas

### **4. UX:**
- Tarefas completadas (%)
- Tempo médio por tarefa (s)
- Elementos inacessíveis

---

## ✅ CHECKLIST DE MONITORAMENTO

### **Pré-Teste:**
- [ ] Arquivo `logs/context_metrics.log` existe e tem permissão de escrita
- [ ] DevTools aberto no navegador (Console)
- [ ] `tail -f logs/context_metrics.log` rodando no terminal
- [ ] `DEBUG_MODE = true` definido (se necessário)

### **Durante Teste:**
- [ ] Verificar se tags de contexto aparecem em `context_metrics.log`
- [ ] Verificar se logs de cancelamento aparecem no Console
- [ ] Monitorar número de conexões ativas
- [ ] Observar erros de streaming (se houver)

### **Pós-Teste:**
- [ ] Analisar frequência de tags em `context_metrics.log`
- [ ] Verificar se conexões foram fechadas corretamente
- [ ] Documentar problemas encontrados
- [ ] Compartilhar métricas com equipe

---

## 📝 PRÓXIMOS PASSOS

1. **Durante testes:** Monitorar logs em tempo real
2. **Após testes:** Analisar métricas coletadas
3. **Ajustes:** Corrigir problemas identificados
4. **Validação:** Confirmar melhorias

---

**Versão:** 1.0  
**Status:** ✅ Aprovado  
**Próxima Revisão:** Após testes em dispositivo real
