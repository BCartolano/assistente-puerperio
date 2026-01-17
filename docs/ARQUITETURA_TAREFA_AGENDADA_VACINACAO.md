# Arquitetura - Tarefa Agendada de Lembretes de Vacinação

**Arquiteto:** Winston (Architect)  
**Data:** 2025-01-08  
**Solicitante:** Dev  

---

## 🎯 OBJETIVOS

1. Definir melhor estratégia para rodar tarefa agendada (APScheduler vs Cron)
2. Implementar trava de segurança (idempotência) para evitar envio duplo
3. Criar log simples para acompanhamento diário

---

## 🔧 ESTRATÉGIA: APSCHEDULER vs CRON

### Análise Comparativa

| Aspecto | APScheduler | Cron |
|---------|-------------|------|
| **Complexidade** | Média (biblioteca Python) | Baixa (comando sistema) |
| **Dependências** | Adiciona `APScheduler` ao requirements.txt | Nenhuma |
| **Controle** | Integrado ao Flask | Sistema operacional |
| **Portabilidade** | Funciona em qualquer OS | Depende do OS |
| **Debug** | Fácil (logs Python) | Mais difícil |
| **Idempotência** | Mais fácil de implementar | Requer lógica externa |
| **Deploy (Railway/Render)** | Requer processo separado ou thread | Não disponível em PaaS |

### Recomendação: APScheduler (Híbrido)

**Justificativa:**
- ✅ Mais fácil de gerenciar em ambiente Python
- ✅ Melhor controle de erros e logging
- ✅ Idempotência nativa com flags do banco
- ✅ Funciona em desenvolvimento e produção
- ✅ Permite execução manual via endpoint

**Limitação:** Em PaaS (Railway/Render), precisa rodar como thread do Flask ou processo separado.

---

## 🔒 IMPLEMENTAÇÃO DE IDEMPOTÊNCIA

### Estratégia: Flag no Banco de Dados

A tabela `vaccination_schedule` já possui:
- `reminder_sent` (BOOLEAN) - Flag de controle
- `reminder_sent_at` (TIMESTAMP) - Quando foi enviado

### Implementação:

1. **Verificação Antes de Enviar:**
   ```python
   # Busca vacinas pendentes
   schedules = VaccinationSchedule.query.filter(
       VaccinationSchedule.status == 'pending',
       VaccinationSchedule.recommended_date == target_date,
       VaccinationSchedule.reminder_sent == False  # Apenas não enviados
   ).all()
   ```

2. **Marcação Imediata (Transação Atômica):**
   ```python
   # Marca como "sendo processado" ANTES de enviar
   schedule.reminder_sent = True
   schedule.reminder_sent_at = datetime.now()
   db.session.commit()  # Salva ANTES de enviar
   
   # Agora envia e-mail
   if send_email(...):
       # Sucesso já foi marcado
       pass
   else:
       # Em caso de erro, pode reverter (opcional)
       schedule.reminder_sent = False
       db.session.commit()
   ```

3. **Proteção Adicional:**
   - Usar transação do SQLite para garantir atomicidade
   - Verificar novamente antes de marcar (double-check)

### Código Atualizado:

```python
def process_due_reminders(self):
    """Processa lembretes com idempotência"""
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    
    target_date = date.today() + timedelta(days=2)
    
    # Busca apenas vacinas NÃO marcadas como enviadas
    cursor.execute('''
        SELECT vs.*, bp.user_id, bp.name as baby_name, bp.birth_date,
               u.name as user_name, u.email
        FROM vaccination_schedule vs
        JOIN baby_profiles bp ON vs.baby_profile_id = bp.id
        JOIN users u ON bp.user_id = u.id
        WHERE vs.status = 'pending'
          AND vs.recommended_date = ?
          AND vs.reminder_sent = 0  -- APENAS não enviados
          AND u.email_verified = 1
    ''', (str(target_date),))
    
    schedules = cursor.fetchall()
    sent_count = 0
    
    for schedule_row in schedules:
        schedule = dict(schedule_row)
        
        # PROTEÇÃO: Verifica novamente antes de processar
        cursor.execute('SELECT reminder_sent FROM vaccination_schedule WHERE id = ?', (schedule['id'],))
        result = cursor.fetchone()
        if result and result[0]:  # Já foi enviado
            continue  # Pula
        
        # Marca ANTES de enviar (transação atômica)
        cursor.execute('''
            UPDATE vaccination_schedule
            SET reminder_sent = 1,
                reminder_sent_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (schedule['id'],))
        conn.commit()  # Salva imediatamente
        
        # Agora envia e-mail
        user = {'name': schedule['user_name'], 'email': schedule['email']}
        baby = {'name': schedule['baby_name'], 'birth_date': schedule['birth_date']}
        
        if self.send_reminder_email(schedule, user, baby):
            sent_count += 1
        else:
            # Em caso de erro, pode reverter (opcional)
            # Ou deixar marcado e logar o erro
            logger.warning(f"Falha ao enviar e-mail para vacina {schedule['id']}, mas já marcada como enviada")
    
    conn.close()
    return sent_count
```

---

## 📊 LOG SIMPLES PARA TERMINAL

### Implementação de Logging

```python
import logging
from datetime import datetime

# Configurar logger
logger = logging.getLogger('vaccination_reminders')
logger.setLevel(logging.INFO)

# Handler para terminal (console)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formato do log
formatter = logging.Formatter(
    '[%(asctime)s] [VACCINATION REMINDERS] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

def process_due_reminders(self):
    """Processa lembretes com logging detalhado"""
    logger.info("=" * 60)
    logger.info(f"Processando lembretes de vacinação - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    target_date = date.today() + timedelta(days=2)
    logger.info(f"Data alvo: {target_date.strftime('%d/%m/%Y')} (2 dias a partir de hoje)")
    
    # ... código de busca ...
    
    logger.info(f"Encontradas {len(schedules)} vacinas para processar")
    
    sent_count = 0
    error_count = 0
    
    for schedule in schedules:
        try:
            # ... código de envio ...
            if self.send_reminder_email(schedule, user, baby):
                sent_count += 1
                logger.info(f"✅ Enviado: {schedule['vaccine_name']} para {baby['name']} ({user['email']})")
            else:
                error_count += 1
                logger.error(f"❌ Erro ao enviar: {schedule['vaccine_name']} para {user['email']}")
        except Exception as e:
            error_count += 1
            logger.error(f"❌ Exceção ao processar vacina {schedule['id']}: {e}", exc_info=True)
    
    logger.info("=" * 60)
    logger.info(f"RESUMO: {sent_count} enviados, {error_count} erros")
    logger.info("=" * 60)
    
    return sent_count
```

### Saída Esperada no Terminal:

```
============================================================
Processando lembretes de vacinação - 2025-01-08 08:00:00
============================================================
Data alvo: 10/01/2025 (2 dias a partir de hoje)
Encontradas 3 vacinas para processar
✅ Enviado: Pentavalente - 1ª dose para Maria Silva (maria@email.com)
✅ Enviado: VIP - 1ª dose para João Santos (joao@email.com)
✅ Enviado: Rotavírus - 1ª dose para Ana Costa (ana@email.com)
============================================================
RESUMO: 3 enviados, 0 erros
============================================================
```

---

## 🚀 IMPLEMENTAÇÃO COM APSCHEDULER

### Arquivo Atualizado: `backend/tasks/vaccination_reminders.py`

```python
# -*- coding: utf-8 -*-
"""
Tarefa Agendada - Envio de Lembretes de Vacinação
Executa diariamente às 08:00 para enviar lembretes 2 dias antes de cada vacina
"""
import os
import sys
import logging
from datetime import datetime

# Configurar logging
logger = logging.getLogger('vaccination_reminders')
logger.setLevel(logging.INFO)

# Handler para console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '[%(asctime)s] [VACCINATION REMINDERS] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Adiciona caminho do projeto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from flask import Flask
from backend.services.vaccination_reminder_service import VaccinationReminderService
from backend.app import send_email, DB_PATH

def send_vaccination_reminders():
    """
    Tarefa agendada para enviar lembretes diariamente
    
    Execução:
    - Via APScheduler: Agendar para rodar diariamente às 08:00
    - Via Cron: 0 8 * * * python backend/tasks/vaccination_reminders.py
    - Manualmente: python backend/tasks/vaccination_reminders.py
    """
    logger.info("=" * 60)
    logger.info(f"Iniciando processamento de lembretes - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    # Cria contexto da aplicação Flask
    app = Flask(__name__)
    app.config.from_object('backend.app')
    
    with app.app_context():
        try:
            # Inicializa serviço de lembretes
            reminder_service = VaccinationReminderService(DB_PATH, send_email)
            
            # Processa e envia lembretes (com idempotência)
            sent_count = reminder_service.process_due_reminders()
            
            logger.info("=" * 60)
            logger.info(f"✅ Processamento concluído: {sent_count} lembretes enviados")
            logger.info("=" * 60)
            
            return sent_count
            
        except Exception as e:
            logger.error("=" * 60)
            logger.error(f"❌ Erro ao processar lembretes: {e}", exc_info=True)
            logger.error("=" * 60)
            return 0

if __name__ == "__main__":
    # Permite execução manual
    send_vaccination_reminders()
```

---

## 📝 INTEGRAÇÃO COM FLASK (APScheduler)

### Opcional: Rodar como Thread no Flask

```python
# Em backend/app.py (após criar app)
from apscheduler.schedulers.background import BackgroundScheduler

def init_scheduler():
    """Inicializa scheduler de tarefas"""
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=send_vaccination_reminders,
        trigger="cron",
        hour=8,
        minute=0,
        id='vaccination_reminders',
        replace_existing=True
    )
    scheduler.start()
    logger.info("[SCHEDULER] ✅ Tarefa de lembretes agendada para 08:00 diariamente")

# Chamar após criar app
if __name__ != '__main__':  # Não roda em desenvolvimento manual
    init_scheduler()
```

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

- [x] Estratégia definida (APScheduler recomendado)
- [x] Idempotência implementada (flag `reminder_sent`)
- [x] Logging detalhado para terminal
- [x] Proteção contra envio duplo (double-check)
- [x] Transações atômicas no banco
- [x] Tratamento de erros com logging

---

**Arquitetura criada por:** Winston (Architect)  
**Data:** 2025-01-08  
**Versão:** 1.0
