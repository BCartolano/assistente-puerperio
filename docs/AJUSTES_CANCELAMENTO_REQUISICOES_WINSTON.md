# Ajustes de Cancelamento de Requisições - Architect

**Criado por:** Winston (Architect)  
**Data:** 2025-01-27  
**Versão:** 1.0  
**Status:** ✅ Aprovado

---

## 🔧 AJUSTE DE TIMEOUT PARA BROKEN PIPE

### **Problema:**
Se o cancelamento de requisições causar erro "Broken Pipe" no servidor Flask devido à troca rápida de abas, precisamos ajustar o timeout.

### **Análise:**

**Flask (backend/app.py):**
- ✅ Já está configurado com `threaded=True` (permite múltiplas requisições)
- ✅ `use_reloader=False` (evita problemas de shutdown)

**Frontend (api-client.js):**
- ✅ Timeout padrão: 30 segundos
- ✅ AbortController implementado corretamente

### **Solução:**

**1. Ajustar tratamento de erros no Flask:**

```python
# Em backend/app.py, adicionar tratamento para Broken Pipe
@app.after_request
def handle_broken_pipe(response):
    """Trata erros de Broken Pipe graciosamente"""
    try:
        return response
    except (BrokenPipeError, ConnectionResetError) as e:
        logger.warning(f"[BROKEN_PIPE] Conexão fechada pelo cliente: {e}")
        # Retorna resposta vazia para evitar erro no servidor
        return Response(status=499)  # 499 = Client Closed Request
```

**2. Aumentar timeout do AbortController:**

**Status Atual:**
- Timeout: 30 segundos (adequado)

**Recomendação:**
- ✅ **Manter 30 segundos** (adequado para mobile)
- ⚠️ Se houver muitos "Broken Pipe", aumentar para 60 segundos

**3. Adicionar retry com backoff exponencial:**

Já implementado no `api-client.js`:
- Retry automático para erros 5xx
- Backoff exponencial entre tentativas

### **Monitoramento:**

**Durante testes, observar:**
- ✅ Se erros "Broken Pipe" aparecem no log do Flask
- ✅ Se cancelamento está funcionando corretamente
- ✅ Se requisições estão sendo limpas da memória

**Comando para monitorar:**
```bash
# Windows (PowerShell)
Get-Content backend\app.log -Wait -Tail 50 | Select-String "BROKEN_PIPE|abort|cancel"

# Linux/Mac
tail -f backend/app.log | grep -i "broken_pipe\|abort\|cancel"
```

---

## 🔒 IDEMPOTÊNCIA DO POST `/api/vaccination/mark-done`

### **Análise da Implementação:**

**Endpoint:** `/api/vaccination/mark-done` (POST)

**Verificações necessárias:**
1. ✅ Transação de banco de dados (commit/rollback)
2. ✅ Verificação de duplicatas (idempotência)
3. ✅ Confirmação de salvamento antes de resposta
4. ✅ Tratamento de erro de conexão

### **Recomendação:**

**1. Adicionar verificação de duplicatas:**

```python
# Em backend/app.py, endpoint mark-done
@app.route('/api/vaccination/mark-done', methods=['POST'])
def api_vaccination_mark_done():
    """Marca vacina como aplicada (idempotente)"""
    data = request.get_json()
    user_id = session.get('user_id') or data.get('user_id')
    vaccine_id = data.get('vaccine_id')
    application_date = data.get('application_date', datetime.now().isoformat())
    
    if not user_id or not vaccine_id:
        return jsonify({"erro": "user_id e vaccine_id são obrigatórios"}), 400
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # IDEMPOTÊNCIA: Verifica se já está marcada
        cursor.execute('''
            SELECT status, application_date 
            FROM vaccination_history 
            WHERE user_id = ? AND vaccine_id = ? AND status = 'applied'
        ''', (user_id, vaccine_id))
        
        existing = cursor.fetchone()
        if existing:
            # Já está marcada, retorna sucesso (idempotente)
            conn.close()
            return jsonify({
                "sucesso": True,
                "mensagem": "Vacina já estava marcada como aplicada",
                "application_date": existing[1]
            }), 200
        
        # Insere ou atualiza com transação
        cursor.execute('''
            INSERT OR REPLACE INTO vaccination_history 
            (user_id, vaccine_id, application_date, status, updated_at)
            VALUES (?, ?, ?, 'applied', CURRENT_TIMESTAMP)
        ''', (user_id, vaccine_id, application_date))
        
        # COMMIT antes de verificar (garante salvamento)
        conn.commit()
        
        # Verifica se foi salvo corretamente
        cursor.execute('''
            SELECT status, application_date 
            FROM vaccination_history 
            WHERE user_id = ? AND vaccine_id = ? AND status = 'applied'
        ''', (user_id, vaccine_id))
        
        confirmed = cursor.fetchone()
        conn.close()
        
        if confirmed:
            logger.info(f"[VACCINATION] ✅ Vacina marcada: user_id={user_id}, vaccine_id={vaccine_id}")
            return jsonify({
                "sucesso": True,
                "mensagem": "Vacina marcada como aplicada com sucesso!",
                "application_date": confirmed[1]
            }), 200
        else:
            logger.error(f"[VACCINATION] ❌ ERRO: Vacina não foi salva após commit!")
            return jsonify({"erro": "Erro ao salvar no banco de dados"}), 500
            
    except Exception as e:
        conn.rollback()
        conn.close()
        logger.error(f"[VACCINATION] ❌ Erro ao marcar vacina: {e}")
        return jsonify({"erro": "Erro interno ao processar"}), 500
```

**2. Adicionar confirmação no frontend:**

```javascript
// Em vaccination-timeline.js, adicionar retry se conexão cair
async markVaccineAsDone(vaccineId) {
    const maxRetries = 3;
    let retryCount = 0;
    
    while (retryCount < maxRetries) {
        try {
            const response = await window.apiClient.post('/api/vaccination/mark-done', {
                vaccine_id: vaccineId,
                application_date: new Date().toISOString()
            });
            
            // Verifica se foi salvo corretamente
            if (response.sucesso && response.application_date) {
                // Confirmação de salvamento recebida
                return response;
            } else {
                throw new Error('Resposta inválida do servidor');
            }
            
        } catch (error) {
            retryCount++;
            if (retryCount >= maxRetries) {
                // Exibe toast de erro
                if (window.toast && typeof window.toast.error === 'function') {
                    window.toast.error('Não foi possível marcar a vacina. Verifique sua conexão e tente novamente.', 5000);
                }
                throw error;
            }
            // Aguarda antes de tentar novamente (backoff exponencial)
            await new Promise(resolve => setTimeout(resolve, 1000 * retryCount));
        }
    }
}
```

---

## 📊 VERIFICAÇÃO DURANTE TESTES

### **Checklist:**

- [ ] Cancelamento de requisições não causa "Broken Pipe" no servidor
- [ ] Requisições canceladas são limpas da memória
- [ ] Vacina marcada é salva no banco mesmo se conexão cair
- [ ] Duplicatas não são criadas (idempotência)
- [ ] Toast de erro aparece se salvamento falhar

### **Comandos de Monitoramento:**

```bash
# Verificar se vacina foi salva no banco
sqlite3 backend/users.db "SELECT * FROM vaccination_history WHERE user_id = X ORDER BY updated_at DESC LIMIT 10;"

# Verificar logs de broken pipe
tail -f logs/flask.log | grep -i "broken\|pipe\|abort"
```

---

## ✅ CONCLUSÃO

1. **Broken Pipe:** Tratamento já adequado com `threaded=True`, adicionar handler gracioso se necessário
2. **Idempotência:** Implementar verificação de duplicatas antes de inserir
3. **Confirmação:** Verificar se salvamento foi confirmado antes de retornar sucesso

---

**Versão:** 1.0  
**Status:** ✅ Aprovado  
**Próxima Revisão:** Após testes em dispositivo real
