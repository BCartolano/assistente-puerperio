# 🔧 Solução para Erro no Render

## ❌ Erro Atual
```
python: can't open file '/opt/render/project/src/app.py': [Errno 2] No such file or directory
```

## 🔍 Causa
O Render está tentando executar `python app.py` em vez de `gunicorn wsgi:app`.

---

## ✅ SOLUÇÃO 1: Verificar Configuração no Dashboard (RECOMENDADO)

### **Passo 1: Acesse o Render Dashboard**
1. Vá para: https://dashboard.render.com
2. Faça login
3. Encontre seu serviço "assistente-puerperio"

### **Passo 2: Verifique as Configurações**
No dashboard do seu serviço:

1. **Clique em "Settings"** (Configurações)
2. **Role até "Build & Deploy"**
3. **Procure por "Start Command"** ou "Comando de Inicialização"

### **Passo 3: Corrija o Start Command**

**❌ ERRADO:**
```
python app.py
```

**✅ CORRETO:**
```
gunicorn wsgi:app
```

Ou, se não tiver gunicorn:
```
cd backend && python app.py
```

### **Passo 4: Salve e Redeply**
1. Clique em **"Save Changes"**
2. Vá em **"Manual Deploy"**
3. Clique em **"Deploy latest commit"**

---

## ✅ SOLUÇÃO 2: Usar Blueprint (Automático)

Se você já conectou o GitHub:

### **Passo 1: Limpar Serviço Antigo**
1. No dashboard, encontre o serviço antigo
2. Clique em **"Delete"** para remover
3. Confirme a deleção

### **Passo 2: Criar Novo Serviço via Blueprint**
1. Vá para https://dashboard.render.com/new/blueprint
2. Conecte o repositório: **assistente-puerperio**
3. O Render detectará o `render.yaml` automaticamente
4. Clique em **"Apply"**
5. Deploy automático iniciará!

**Isso garantirá que o render.yaml seja usado corretamente!**

---

## ✅ SOLUÇÃO 3: Arquivos Duplicados (Fallback)

Se as soluções 1 e 2 não funcionarem:

### **Opção A: Mudar nome do arquivo**
Criar um `app.py` na raiz que importa do backend:

```python
# app.py (na raiz do projeto)
import os
import sys
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)
from app import app

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
```

**⚠️ NÃO FAÇA ISSO AINDA!** Tente as Soluções 1 e 2 primeiro!

---

## 🎯 AÇÃO RECOMENDADA AGORA

### **Faça isso AGORA:**

1. **Abra:** https://dashboard.render.com
2. **Encontre** o serviço "assistente-puerperio"
3. **Vá em:** Settings → Build & Deploy
4. **Procure:** "Start Command"
5. **Mude para:** `gunicorn wsgi:app`
6. **Salve** e **Redeply**

### **Depois:**
- Aguarde o build completar (2-5 minutos)
- Verifique os logs
- Teste a URL

---

## 📋 CheckList

- [ ] Acessei dashboard.render.com
- [ ] Encontrei o serviço assistente-puerperio
- [ ] Cliquei em Settings
- [ ] Rolei até Build & Deploy
- [ ] Mudei Start Command para: `gunicorn wsgi:app`
- [ ] Cliquei em "Save Changes"
- [ ] Fiz Manual Deploy
- [ ] Aguardei o build
- [ ] Testei a URL

---

## 🔍 Verificar Logs

Depois do deploy:

1. No dashboard, clique em **"Logs"**
2. Procure por mensagens de:
   - ✅ "Starting gunicorn"
   - ✅ "Listening on: 0.0.0.0"
   - ✅ "Assistente Puerperio iniciado"

**Se vir essas mensagens = SUCESSO! 🎉**

---

## 🆘 Se AINDA Não Funcionar

### **Envie esta informação:**

1. Screenshot do **Settings → Build & Deploy**
2. Screenshot dos **Logs**
3. Screenshot da mensagem de erro completa

**Com essas informações, posso ajudar mais!**

---

## 📞 Arquivos Importantes

Certifique-se que estão no GitHub:
- ✅ `wsgi.py` (na raiz)
- ✅ `Procfile` (na raiz)
- ✅ `render.yaml` (na raiz)
- ✅ `requirements.txt` (com gunicorn)

**Todos já estão enviados! ✅**

---

## 🎯 Próximo Passo

**VÁ AGORA para o Dashboard e mude o Start Command!**

É literalmente **2 clicks**:
1. Settings
2. Start Command → `gunicorn wsgi:app`
3. Save
4. Deploy

**Isso deve resolver!** 🚀

