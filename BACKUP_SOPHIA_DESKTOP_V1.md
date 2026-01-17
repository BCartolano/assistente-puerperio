# Backup Sophia Desktop V1.0 - Configurações e Endpoints

**Data:** 2025-01-27  
**Versão:** 1.0 PROD (DESKTOP)  
**Status:** ✅ Produção Desktop

---

## 🔐 VARIÁVEIS DE AMBIENTE

### **Arquivo:** `.env` (baseado em `env_example.txt`)

```bash
# ============================================
# OPENAI - Configuração de IA
# ============================================
OPENAI_API_KEY=sua_chave_openai_aqui
USE_AI=true
OPENAI_ASSISTANT_ID=asst_xxxxx  # Opcional - criado automaticamente se não configurado

# ============================================
# FLASK - Configuração do Servidor
# ============================================
FLASK_ENV=development  # ou 'production'
FLASK_DEBUG=True  # ou False em produção
SECRET_KEY=sua-chave-secreta-super-segura-mude-isso-em-producao
PORT=5000

# ============================================
# URL BASE - Links e Email
# ============================================
BASE_URL=http://localhost:5000  # Em produção: https://seu-dominio.com
# ⚠️ IMPORTANTE: Se usar ngrok, emails podem cair no spam!

# ============================================
# EMAIL - Configuração de Envio
# ============================================
# OPÇÃO 1: Gmail (Requer Verificação em Duas Etapas + Senha de App)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=seu_email@gmail.com
MAIL_PASSWORD=sua_senha_app_gerada_aqui  # NÃO use senha normal!
MAIL_DEFAULT_SENDER=seu_email@gmail.com

# OPÇÃO 2: Outlook/Hotmail
# MAIL_SERVER=smtp-mail.outlook.com
# MAIL_PORT=587
# MAIL_USE_TLS=True
# MAIL_USERNAME=seu_email@outlook.com
# MAIL_PASSWORD=sua_senha_normal
# MAIL_DEFAULT_SENDER=noreply@chatbot-puerperio.com

# OPÇÃO 3: Yahoo Mail
# MAIL_SERVER=smtp.mail.yahoo.com
# MAIL_PORT=587
# MAIL_USE_TLS=True
# MAIL_USERNAME=seu_email@yahoo.com
# MAIL_PASSWORD=sua_senha_normal
# MAIL_DEFAULT_SENDER=noreply@chatbot-puerperio.com
```

---

## 🌐 ENDPOINTS DA API

### **Autenticação e Usuário**

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `POST` | `/api/register` | Registro de novo usuário | ✅ |
| `POST` | `/api/login` | Login de usuário | ✅ |
| `POST` | `/api/logout` | Logout de usuário | ✅ |
| `GET` | `/api/user` | Obter dados do usuário logado | ✅ |
| `POST` | `/api/forgot-password` | Solicitar redefinição de senha | ✅ |
| `GET` | `/reset-password` | Página de redefinição de senha | ✅ |
| `POST` | `/api/reset-password` | Redefinir senha com token | ✅ |
| `POST` | `/api/resend-verification` | Reenviar email de verificação | ✅ |
| `GET` | `/api/verify-email` | Verificar email com token | ✅ |
| `POST` | `/api/auto-verify` | Verificação automática de email | ✅ |
| `POST` | `/api/delete-user` | Deletar conta de usuário | ✅ |
| `POST` | `/api/verificacao` | Verificar status de verificação | ✅ |

### **Chat e Inteligência Artificial**

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `POST` | `/api/chat` | Enviar mensagem para Sophia | ✅ |
| `POST` | `/api/triagem-emocional` | Triagem emocional (BMad Core) | ✅ |
| `POST` | `/api/limpar-memoria-ia` | Limpar memória da IA | ✅ |
| `GET` | `/api/historico/<user_id>` | Obter histórico de conversas | ✅ |
| `DELETE` | `/api/historico/<user_id>` | Deletar histórico de conversas | ✅ |

### **Base de Conhecimento**

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `GET` | `/api/categorias` | Listar categorias de conhecimento | ✅ |
| `GET` | `/api/alertas` | Obter alertas e recursos de apoio | ✅ |
| `GET` | `/api/telefones` | Obter telefones úteis | ✅ |
| `GET` | `/api/guias` | Listar guias práticos | ✅ |
| `GET` | `/api/guias/<guia_id>` | Obter guia específico | ✅ |
| `GET` | `/api/cuidados/gestacao` | Cuidados durante gestação | ✅ |
| `GET` | `/api/cuidados/gestacao/<trimestre>` | Cuidados por trimestre | ✅ |
| `GET` | `/api/cuidados/puerperio` | Cuidados no puerpério | ✅ |
| `GET` | `/api/cuidados/puerperio/<periodo>` | Cuidados por período | ✅ |
| `GET` | `/api/vacinas/mae` | Vacinas para mãe | ✅ |
| `GET` | `/api/vacinas/bebe` | Vacinas para bebê | ✅ |

### **Agenda de Vacinação**

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `GET` | `/api/vaccination/status` | Obter status de vacinação do bebê | ✅ |
| `POST` | `/api/vaccination/mark-done` | Marcar vacina como aplicada | ✅ |
| `GET` | `/api/vacinas/status` | Status de vacinas (legado) | ✅ |
| `POST` | `/api/vacinas/marcar` | Marcar vacina (legado) | ✅ |
| `POST` | `/api/vacinas/desmarcar` | Desmarcar vacina (legado) | ✅ |

---

## 📁 ESTRUTURA DE ARQUIVOS

### **Backend**
```
backend/
├── app.py                    # Aplicação Flask principal
├── loader.py                 # Carregador de base de conhecimento
├── services/
│   ├── vaccination_service.py
│   └── vaccination_reminder_service.py
├── tasks/
│   └── vaccination_reminders.py  # Tarefa agendada (APScheduler)
├── static/
│   ├── css/
│   │   ├── style.css
│   │   └── vaccination-timeline.css
│   └── js/
│       ├── chat.js
│       ├── api-client.js
│       ├── sidebar-content.js
│       └── vaccination-timeline.js
└── templates/
    └── index.html
```

### **Dados**
```
data/
├── base_conhecimento.json
├── mensagens_apoio.json
├── alertas.json
├── telefones_uteis.json
├── guias_praticos.json
├── cuidados_gestacao.json
├── cuidados_pos_parto.json
├── vacinas_mae.json
└── vacinas_bebe.json
```

### **Logs**
```
logs/
├── context_metrics.log        # Métricas de tags de contexto
└── .gitkeep
```

### **Documentação**
```
docs/
├── prd.md
├── sprint-planning.md
├── arquitetura-agenda-vacinacao.md
├── spec-ux-agenda-vacinacao.md
├── calendario-vacinacao-pni-2026.md
├── GUIA_TOM_DE_VOZ_MARY.md
├── REVISAO_UX_DESKTOP_FINAL.md
└── IMPLEMENTACAO_FINAL_GUIA_TOM_VOZ.md
```

---

## 🗄️ BANCO DE DADOS

### **Tabelas SQLite**

#### **users**
- `id` (INTEGER PRIMARY KEY)
- `username` (TEXT UNIQUE)
- `email` (TEXT UNIQUE)
- `password_hash` (TEXT)
- `email_verified` (BOOLEAN)
- `verification_token` (TEXT)
- `created_at` (TIMESTAMP)

#### **baby_profiles**
- `id` (INTEGER PRIMARY KEY)
- `user_id` (INTEGER, FOREIGN KEY)
- `name` (TEXT)
- `birth_date` (DATE)
- `created_at` (TIMESTAMP)

#### **vaccine_reference**
- `id` (INTEGER PRIMARY KEY)
- `name` (TEXT)
- `age_months` (INTEGER)
- `description` (TEXT)
- `protects_against` (TEXT)

#### **vaccination_history**
- `id` (INTEGER PRIMARY KEY)
- `baby_profile_id` (INTEGER, FOREIGN KEY)
- `vaccine_id` (INTEGER, FOREIGN KEY)
- `scheduled_date` (DATE)
- `application_date` (DATE, NULLABLE)
- `status` (TEXT)  # 'pending', 'applied', 'overdue'

---

## 🔧 CONFIGURAÇÕES DE TAREFAS AGENDADAS

### **APScheduler**
- **Tarefa:** `send_vaccination_reminders()`
- **Frequência:** Diária às 09:00
- **Arquivo:** `backend/tasks/vaccination_reminders.py`
- **Thread:** Background (não bloqueia Flask)

### **Logs de Contexto**
- **Arquivo:** `logs/context_metrics.log`
- **Formato:** `YYYY-MM-DD HH:MM | tag`
- **Exemplo:** `2025-01-27 14:30 | cansaço_extremo`

---

## 🎨 PALETA DE CORES (Desktop)

### **Cores Principais**
- **Coral:** `#ff8fa3`
- **Pêssego:** `#ffb3c6`
- **Creme:** `#ffe8f0`
- **Verde Sálvia:** `#c4d5a0`
- **Terracota:** `#e07a5f`

### **Gradiente de Fundo**
```css
background: linear-gradient(135deg, 
    rgba(255, 245, 247, 0.4) 0%, 
    rgba(255, 238, 242, 0.3) 50%, 
    rgba(248, 213, 224, 0.4) 100%);
```

---

## 📊 TAGS DE CONTEXTO

### **Tags Disponíveis**
1. `cansaço_extremo`
2. `cansaço_extremo_critico` (detectado após 3x `cansaço_extremo`)
3. `celebração`
4. `ansiedade`
5. `tristeza`
6. `dúvida_vacina`
7. `dúvida_amamentação`
8. `busca_orientação`
9. `busca_apoio_emocional`
10. `crise_emocional`
11. `nivel_risco_alto`
12. `nivel_risco_moderado`
13. `nivel_risco_leve`

---

## 🚀 DEPLOY

### **Plataformas Suportadas**
- **Railway:** `railway.json`, `nixpacks.toml`
- **Render:** `render.yaml`
- **Heroku:** `Procfile`
- **Docker:** `Dockerfile`

### **Requisitos**
- Python 3.11.0+
- Dependências: `requirements.txt`
- Banco de dados: SQLite (desenvolvimento) ou PostgreSQL (produção)

---

## ✅ CHECKLIST DE PRODUÇÃO

- [x] Variáveis de ambiente configuradas
- [x] Endpoints da API funcionando
- [x] Banco de dados estruturado
- [x] Sistema de email configurado
- [x] Tarefas agendadas (APScheduler)
- [x] Logs de contexto funcionando
- [x] Interface desktop responsiva
- [x] Sistema de vacinação completo
- [x] Inteligência emocional implementada
- [x] Quick Replies mapeados
- [x] Guia de Tom de Voz integrado

---

## 📝 NOTAS IMPORTANTES

1. **Email:** Gmail requer Verificação em Duas Etapas + Senha de App
2. **ngrok:** Links podem cair no spam - use domínio próprio em produção
3. **Logs:** `logs/context_metrics.log` não contém dados sensíveis
4. **Histórico:** `CONTEXT_TAG_HISTORY` mantém últimas 10 tags por usuário
5. **Cansaço Crítico:** Detectado após 3 mensagens consecutivas com `cansaço_extremo`

---

**Versão:** 1.0 PROD (DESKTOP)  
**Data:** 2025-01-27  
**Status:** ✅ Produção Desktop Aprovada
