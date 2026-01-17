# Arquitetura - Agenda de Vacinação Interativa

**Arquiteto:** Winston (Architect)  
**Data:** 2025-01-08  
**Contexto:** Implementação da funcionalidade priorizada pela PO (Sarah)

---

## 📋 VISÃO GERAL

Sistema de agenda de vacinação interativa que permite às mães acompanhar o calendário de vacinação dos filhos, com lembretes automáticos via e-mail 2 dias antes de cada vacina.

---

## 🗄️ ESTRUTURA DE DADOS NO BANCO

### Tabela: `baby_profiles`

Armazena informações básicas de cada bebê associado a um usuário.

```sql
CREATE TABLE baby_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    birth_date DATE NOT NULL,
    gender VARCHAR(10), -- 'male', 'female', 'other', NULL
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, name, birth_date) -- Evita duplicatas
);
```

**Campos:**
- `id`: Identificador único do perfil do bebê
- `user_id`: Referência ao usuário (mãe) que cadastrou
- `name`: Nome do bebê
- `birth_date`: Data de nascimento (usada para calcular idades das vacinas)
- `gender`: Gênero (opcional, pode ser útil para algumas vacinas)
- `created_at` / `updated_at`: Timestamps de auditoria

---

### Tabela: `vaccination_schedule`

Armazena o calendário de vacinação calculado para cada bebê baseado no PNI.

```sql
CREATE TABLE vaccination_schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    baby_profile_id INTEGER NOT NULL,
    vaccine_name VARCHAR(100) NOT NULL,
    vaccine_code VARCHAR(20) NOT NULL, -- Código padronizado (ex: 'BCG', 'HEP_B_1')
    age_months INTEGER NOT NULL, -- Idade em meses quando deve ser aplicada
    age_days INTEGER DEFAULT 0, -- Dias adicionais (ex: ao nascer = 0 dias)
    dose_number INTEGER NOT NULL, -- Número da dose (1, 2, 3, etc.)
    recommended_date DATE NOT NULL, -- Data calculada baseada no birth_date
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'scheduled', 'completed', 'missed', 'skipped'
    administered_date DATE NULL, -- Data em que foi realmente aplicada
    administered_location VARCHAR(200) NULL, -- Onde foi aplicada
    administered_by VARCHAR(100) NULL, -- Profissional/unidade que aplicou
    lot_number VARCHAR(50) NULL, -- Número do lote da vacina
    reminder_sent BOOLEAN DEFAULT 0, -- Se lembrete foi enviado
    reminder_sent_at TIMESTAMP NULL, -- Quando o lembrete foi enviado
    notes TEXT NULL, -- Observações adicionais
    is_optional BOOLEAN DEFAULT 0, -- Se é vacina opcional (SBP, não PNI)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (baby_profile_id) REFERENCES baby_profiles(id) ON DELETE CASCADE,
    INDEX idx_baby_status (baby_profile_id, status),
    INDEX idx_recommended_date (recommended_date, status),
    INDEX idx_reminder (reminder_sent, recommended_date)
);
```

**Campos principais:**
- `vaccine_name`: Nome completo da vacina (ex: "Pentavalente (DTP + Hib + Hepatite B)")
- `vaccine_code`: Código padronizado para processamento (ex: "PENTA_1", "BCG")
- `age_months` / `age_days`: Idade exata quando deve ser aplicada
- `recommended_date`: Data calculada automaticamente baseada em `birth_date + age`
- `status`: Estado atual da vacina
- `reminder_sent`: Flag para controlar envio de lembretes

---

### Tabela: `vaccination_history`

Registro histórico de vacinas já aplicadas (backup e auditoria).

```sql
CREATE TABLE vaccination_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    schedule_id INTEGER NOT NULL, -- Referência ao vaccination_schedule
    baby_profile_id INTEGER NOT NULL,
    vaccine_name VARCHAR(100) NOT NULL,
    vaccine_code VARCHAR(20) NOT NULL,
    administered_date DATE NOT NULL,
    dose_number INTEGER NOT NULL,
    administered_location VARCHAR(200),
    administered_by VARCHAR(100),
    lot_number VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (schedule_id) REFERENCES vaccination_schedule(id),
    FOREIGN KEY (baby_profile_id) REFERENCES baby_profiles(id) ON DELETE CASCADE
);
```

**Propósito:** Histórico imutável de vacinas aplicadas para auditoria e relatórios.

---

## 📧 INTEGRAÇÃO COM SISTEMA DE E-MAIL

### Configuração Flask-Mail

O sistema já possui Flask-Mail configurado. Verificar variáveis no `.env`:

```python
# backend/app.py (exemplo de configuração)
from flask_mail import Mail, Message

app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@sophia-chatbot.com')

mail = Mail(app)
```

### Serviço de Lembretes

Criar `backend/services/vaccination_reminder_service.py`:

```python
from flask import current_app
from flask_mail import Message
from datetime import datetime, timedelta
from backend.models import db, BabyProfile, VaccinationSchedule, User

class VaccinationReminderService:
    """Serviço para enviar lembretes de vacinação"""
    
    @staticmethod
    def send_reminder_email(schedule, user, baby):
        """Envia e-mail de lembrete para uma vacina específica"""
        try:
            msg = Message(
                subject=f'Lembrete: {schedule.vaccine_name} - {baby.name}',
                recipients=[user.email],
                html=f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #ff8fa3;">💉 Lembrete de Vacinação</h2>
                        <p>Olá {user.name or 'Mãe'}!</p>
                        <p>Este é um lembrete de que <strong>{baby.name}</strong> tem uma vacina agendada:</p>
                        <div style="background: #ffe8f0; padding: 15px; border-radius: 8px; margin: 20px 0;">
                            <h3 style="margin-top: 0; color: #ff8fa3;">{schedule.vaccine_name}</h3>
                            <p><strong>Data recomendada:</strong> {schedule.recommended_date.strftime('%d/%m/%Y')}</p>
                            <p><strong>Idade do bebê:</strong> {schedule.age_months} meses</p>
                            <p><strong>Dose:</strong> {schedule.dose_number}ª dose</p>
                        </div>
                        <p><strong>O que esta vacina protege:</strong></p>
                        <p>{VaccinationReminderService._get_vaccine_info(schedule.vaccine_code)}</p>
                        <p style="margin-top: 30px;">
                            <a href="{current_app.config['APP_URL']}/vaccination" 
                               style="background: #ff8fa3; color: white; padding: 12px 24px; 
                                      text-decoration: none; border-radius: 6px; display: inline-block;">
                                Ver Calendário Completo
                            </a>
                        </p>
                        <p style="margin-top: 30px; font-size: 12px; color: #666;">
                            Este lembrete foi enviado automaticamente 2 dias antes da data recomendada.
                        </p>
                    </div>
                </body>
                </html>
                """
            )
            current_app.extensions['mail'].send(msg)
            return True
        except Exception as e:
            current_app.logger.error(f"Erro ao enviar lembrete: {e}")
            return False
    
    @staticmethod
    def _get_vaccine_info(vaccine_code):
        """Retorna informação sobre o que a vacina protege"""
        vaccine_info = {
            'BCG': 'Protege contra formas graves de tuberculose (meningite tuberculosa e tuberculose miliar).',
            'HEP_B_1': 'Protege contra hepatite B e suas complicações (cirrose, câncer de fígado).',
            'PENTA_1': 'Protege contra difteria, tétano, coqueluche, meningite por Hib e hepatite B.',
            # ... adicionar todas as vacinas
        }
        return vaccine_info.get(vaccine_code, 'Vacina importante para a saúde do bebê.')
    
    @staticmethod
    def process_due_reminders():
        """Processa e envia lembretes para vacinas com 2 dias de antecedência"""
        from datetime import date, timedelta
        
        # Data alvo: 2 dias a partir de hoje
        target_date = date.today() + timedelta(days=2)
        
        # Busca vacinas pendentes com data recomendada em 2 dias
        schedules = VaccinationSchedule.query.filter(
            VaccinationSchedule.status == 'pending',
            VaccinationSchedule.recommended_date == target_date,
            VaccinationSchedule.reminder_sent == False
        ).all()
        
        sent_count = 0
        for schedule in schedules:
            # Busca perfil do bebê e usuário
            baby = BabyProfile.query.get(schedule.baby_profile_id)
            if not baby:
                continue
            
            user = User.query.get(baby.user_id)
            if not user or not user.email:
                continue
            
            # Envia lembrete
            if VaccinationReminderService.send_reminder_email(schedule, user, baby):
                # Marca como enviado
                schedule.reminder_sent = True
                schedule.reminder_sent_at = datetime.now()
                db.session.commit()
                sent_count += 1
        
        return sent_count
```

### Tarefa Agendada (Cron Job)

Criar `backend/tasks/vaccination_reminders.py`:

```python
from flask import current_app
from backend.services.vaccination_reminder_service import VaccinationReminderService

def send_vaccination_reminders():
    """Tarefa agendada para enviar lembretes diariamente"""
    with current_app.app_context():
        count = VaccinationReminderService.process_due_reminders()
        current_app.logger.info(f"Lembretes de vacinação enviados: {count}")
        return count
```

**Agendamento:** Executar diariamente às 08:00 (usar APScheduler, Celery, ou cron do sistema).

---

## 📊 ESTRUTURA JSON DO HISTÓRICO DE VACINAÇÃO

### Formato de Resposta da API

```json
{
  "baby": {
    "id": 1,
    "name": "Maria Silva",
    "birth_date": "2025-01-15",
    "gender": "female",
    "age_days": 45,
    "age_months": 1
  },
  "vaccination_schedule": [
    {
      "id": 1,
      "vaccine_name": "BCG",
      "vaccine_code": "BCG",
      "age_months": 0,
      "age_days": 0,
      "dose_number": 1,
      "recommended_date": "2025-01-15",
      "status": "completed",
      "administered_date": "2025-01-16",
      "administered_location": "Hospital Municipal",
      "administered_by": "Enfermeira Ana",
      "lot_number": "BCG2025001",
      "reminder_sent": true,
      "reminder_sent_at": "2025-01-13T08:00:00Z",
      "is_optional": false,
      "notes": null
    },
    {
      "id": 2,
      "vaccine_name": "Hepatite B",
      "vaccine_code": "HEP_B_1",
      "age_months": 0,
      "age_days": 0,
      "dose_number": 1,
      "recommended_date": "2025-01-15",
      "status": "completed",
      "administered_date": "2025-01-16",
      "administered_location": "Hospital Municipal",
      "administered_by": "Enfermeira Ana",
      "lot_number": "HEPB2025001",
      "reminder_sent": true,
      "reminder_sent_at": "2025-01-13T08:00:00Z",
      "is_optional": false,
      "notes": null
    },
    {
      "id": 3,
      "vaccine_name": "Pentavalente (DTP + Hib + Hepatite B)",
      "vaccine_code": "PENTA_1",
      "age_months": 2,
      "age_days": 0,
      "dose_number": 1,
      "recommended_date": "2025-03-15",
      "status": "pending",
      "administered_date": null,
      "administered_location": null,
      "administered_by": null,
      "lot_number": null,
      "reminder_sent": false,
      "reminder_sent_at": null,
      "is_optional": false,
      "notes": null
    }
  ],
  "statistics": {
    "total_vaccines": 19,
    "completed": 2,
    "pending": 15,
    "missed": 0,
    "scheduled": 2,
    "completion_percentage": 10.5
  },
  "upcoming_vaccines": [
    {
      "id": 3,
      "vaccine_name": "Pentavalente (DTP + Hib + Hepatite B)",
      "recommended_date": "2025-03-15",
      "days_until": 30,
      "reminder_sent": false
    }
  ]
}
```

### Formato para Armazenamento (Histórico Completo)

```json
{
  "baby_profile_id": 1,
  "baby_name": "Maria Silva",
  "birth_date": "2025-01-15",
  "vaccination_history": [
    {
      "vaccine_name": "BCG",
      "vaccine_code": "BCG",
      "dose_number": 1,
      "administered_date": "2025-01-16",
      "administered_location": "Hospital Municipal",
      "administered_by": "Enfermeira Ana",
      "lot_number": "BCG2025001",
      "age_at_vaccination_days": 1,
      "age_at_vaccination_months": 0,
      "notes": "Aplicada na maternidade, um dia após o nascimento"
    },
    {
      "vaccine_name": "Hepatite B",
      "vaccine_code": "HEP_B_1",
      "dose_number": 1,
      "administered_date": "2025-01-16",
      "administered_location": "Hospital Municipal",
      "administered_by": "Enfermeira Ana",
      "lot_number": "HEPB2025001",
      "age_at_vaccination_days": 1,
      "age_at_vaccination_months": 0,
      "notes": null
    }
  ],
  "last_updated": "2025-01-16T10:30:00Z"
}
```

---

## 🔄 FLUXO DE FUNCIONAMENTO

### 1. Cadastro do Bebê
1. Usuário cadastra bebê (nome, data de nascimento, gênero)
2. Sistema calcula automaticamente todas as vacinas do calendário PNI
3. Cria registros em `vaccination_schedule` com `recommended_date` calculada

### 2. Cálculo de Datas
```python
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def calculate_recommended_date(birth_date, age_months, age_days=0):
    """Calcula data recomendada baseada na data de nascimento"""
    recommended = birth_date + relativedelta(months=age_months) + timedelta(days=age_days)
    return recommended
```

### 3. Envio de Lembretes
1. Tarefa agendada executa diariamente
2. Busca vacinas com `recommended_date` = hoje + 2 dias
3. Envia e-mail para usuário
4. Marca `reminder_sent = True`

### 4. Registro de Vacina Aplicada
1. Usuário marca vacina como aplicada
2. Atualiza `vaccination_schedule`:
   - `status = 'completed'`
   - `administered_date = data informada`
   - Preenche dados adicionais (local, profissional, lote)
3. Cria registro em `vaccination_history` (backup)

---

## 🔐 SEGURANÇA E VALIDAÇÃO

### Validações Necessárias
1. **Data de nascimento:** Não pode ser futura
2. **Data de aplicação:** Não pode ser anterior à data de nascimento
3. **Dose:** Validar sequência (não pode pular doses)
4. **Idade mínima:** Validar se bebê tem idade mínima para a vacina

### Privacidade
- Dados de saúde são sensíveis (LGPD)
- Criptografar dados em repouso
- Logs não devem conter informações pessoais
- E-mails devem ser enviados apenas para e-mail verificado

---

## 📝 PRÓXIMOS PASSOS DE IMPLEMENTAÇÃO

1. **Criar migração de banco** para as 3 tabelas
2. **Implementar serviço de cálculo de calendário** baseado no PNI
3. **Criar API endpoints** para CRUD de bebês e vacinas
4. **Implementar serviço de lembretes** (e-mail)
5. **Configurar tarefa agendada** (APScheduler ou Celery)
6. **Criar interface frontend** para visualização e gerenciamento
7. **Testes unitários e integração**

---

**Documento criado por:** Winston (Architect)  
**Data:** 2025-01-08  
**Versão:** 1.0  
**Status:** Pronto para implementação
