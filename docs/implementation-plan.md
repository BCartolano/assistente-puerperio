# Plano de Implementação - Estrutura Base

**Desenvolvedor:** Dev Agent (Alex)  
**Data:** 2025-01-12  
**Baseado em:** Architecture v1.0 (Validada)

## 🚀 RESUMO EXECUTIVO

**Status:** ⏳ PRONTO PARA INICIAR  
**Fase Atual:** Estrutura Base  
**Próxima Fase:** Integração WhatsApp

---

## 📁 ESTRUTURA DE PASTAS A CRIAR

```
backend/
├── integrations/          # NOVO
│   ├── __init__.py
│   ├── whatsapp/
│   │   ├── __init__.py
│   │   ├── service.py
│   │   ├── webhook.py
│   │   └── templates.py
│   ├── external_systems/
│   │   ├── __init__.py
│   │   ├── adapter.py
│   │   ├── totvs.py
│   │   ├── mv.py
│   │   └── generic.py
│   └── config.py
├── services/              # NOVO
│   ├── __init__.py
│   ├── appointment_service.py
│   ├── specialty_service.py
│   ├── business_hours_service.py
│   └── conversation_history_service.py
├── models/                # NOVO
│   ├── __init__.py
│   ├── appointment.py
│   ├── conversation_history.py
│   ├── specialty_mapping.py
│   ├── external_sync.py
│   └── business_hours.py
├── database/              # NOVO
│   ├── __init__.py
│   ├── migrations/
│   │   └── 001_initial_schema.py
│   └── schema.py
└── tasks/                 # NOVO (futuro - Celery)
    ├── __init__.py
    └── sync_tasks.py
```

---

## 🗄️ SCHEMA DE BANCO DE DADOS

### Script de Migração Inicial

```python
# backend/database/migrations/001_initial_schema.py

import sqlite3
from datetime import datetime

def create_tables(db_path='backend/users.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Tabela de Agendamentos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            specialty VARCHAR(100) NOT NULL,
            appointment_date DATETIME NOT NULL,
            status VARCHAR(20) DEFAULT 'pending',
            external_appointment_id VARCHAR(100),
            patient_name VARCHAR(200),
            patient_phone VARCHAR(20),
            symptoms TEXT,
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Tabela de Histórico de Conversas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            channel VARCHAR(20) NOT NULL,
            message_type VARCHAR(20) NOT NULL,
            content TEXT NOT NULL,
            specialty_identified VARCHAR(100),
            intent VARCHAR(100),
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Tabela de Mapeamento de Especialidades
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS specialty_mapping (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            specialty_name VARCHAR(100) UNIQUE NOT NULL,
            keywords TEXT,
            symptoms TEXT,
            description TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de Sincronização Externa
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS external_system_sync (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type VARCHAR(50) NOT NULL,
            entity_id INTEGER NOT NULL,
            external_id VARCHAR(100),
            sync_status VARCHAR(20) DEFAULT 'pending',
            last_sync_at DATETIME,
            sync_errors TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de Horários Comerciais
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS business_hours (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day_of_week INTEGER NOT NULL,
            start_time TIME NOT NULL,
            end_time TIME NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            timezone VARCHAR(50) DEFAULT 'America/Sao_Paulo'
        )
    ''')
    
    # Índices para performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_appointments_user_id ON appointments(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(appointment_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversation_history_user_timestamp ON conversation_history(user_id, timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_external_system_sync_status ON external_system_sync(sync_status)')
    
    conn.commit()
    conn.close()
    print("✅ Tabelas criadas com sucesso!")

if __name__ == '__main__':
    create_tables()
```

---

## 📦 MODELOS DE DADOS

### Appointment Model

```python
# backend/models/appointment.py

from datetime import datetime
import sqlite3

class Appointment:
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_COMPLETED = 'completed'
    
    def __init__(self, db_path='backend/users.db'):
        self.db_path = db_path
    
    def create(self, user_id, specialty, appointment_date, patient_name, 
               patient_phone, symptoms=None, notes=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO appointments 
            (user_id, specialty, appointment_date, status, patient_name, 
             patient_phone, symptoms, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, specialty, appointment_date, self.STATUS_PENDING,
              patient_name, patient_phone, symptoms, notes,
              datetime.now(), datetime.now()))
        
        appointment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return appointment_id
    
    def get_by_id(self, appointment_id):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM appointments WHERE id = ?', (appointment_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def update_status(self, appointment_id, status):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE appointments 
            SET status = ?, updated_at = ?
            WHERE id = ?
        ''', (status, datetime.now(), appointment_id))
        
        conn.commit()
        conn.close()
```

---

## 🔧 SERVIÇOS BASE

### BusinessHoursService (Primeiro a Implementar)

```python
# backend/services/business_hours_service.py

from datetime import datetime, time
import sqlite3
import pytz

class BusinessHoursService:
    def __init__(self, db_path='backend/users.db'):
        self.db_path = db_path
        self.timezone = pytz.timezone('America/Sao_Paulo')
    
    def is_business_hours(self, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now(self.timezone)
        
        day_of_week = timestamp.weekday()  # 0=Monday, 6=Sunday
        current_time = timestamp.time()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT start_time, end_time 
            FROM business_hours 
            WHERE day_of_week = ? AND is_active = 1
        ''', (day_of_week,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return False
        
        start_time = datetime.strptime(row[0], '%H:%M:%S').time()
        end_time = datetime.strptime(row[1], '%H:%M:%S').time()
        
        return start_time <= current_time <= end_time
    
    def get_business_hours(self, day_of_week):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT start_time, end_time 
            FROM business_hours 
            WHERE day_of_week = ? AND is_active = 1
        ''', (day_of_week,))
        
        row = cursor.fetchone()
        conn.close()
        
        return row if row else None
```

---

## 📝 CHECKLIST DE IMPLEMENTAÇÃO

### Fase 1: Estrutura Base ✅

- [ ] Criar estrutura de pastas
- [ ] Criar script de migração de banco
- [ ] Implementar modelos básicos (Appointment, ConversationHistory)
- [ ] Implementar BusinessHoursService
- [ ] Criar testes unitários básicos

### Fase 2: Integração WhatsApp ⏳

- [ ] Implementar WhatsAppIntegrationService
- [ ] Criar handlers de webhook
- [ ] Implementar envio de mensagens
- [ ] Testes de integração

### Fase 3: Identificação de Especialidade ⏳

- [ ] Implementar SpecialtyIdentificationService
- [ ] Integrar com OpenAI
- [ ] Criar SpecialtyMapping model
- [ ] Testes de classificação

### Fase 4: Sistema de Agendamento ⏳

- [ ] Implementar AppointmentService
- [ ] Validação de disponibilidade
- [ ] Confirmações
- [ ] Testes E2E

### Fase 5: Integração Externa ⏳

- [ ] Implementar ExternalSystemAdapter
- [ ] Criar adapters específicos (mock primeiro)
- [ ] Sincronização
- [ ] Testes de integração

---

## 🎯 PRÓXIMOS PASSOS IMEDIATOS

1. **Criar estrutura de pastas**
   ```bash
   mkdir -p backend/integrations/whatsapp
   mkdir -p backend/integrations/external_systems
   mkdir -p backend/services
   mkdir -p backend/models
   mkdir -p backend/database/migrations
   ```

2. **Executar migração de banco**
   ```bash
   python backend/database/migrations/001_initial_schema.py
   ```

3. **Implementar BusinessHoursService primeiro** (mais simples)

4. **Criar testes básicos**

5. **Integrar com app.py existente**

---

## ✅ CONCLUSÃO

A estrutura base está **bem definida** e **pronta para implementação**. A sequência proposta permite desenvolvimento incremental e testável.

**Status:** ✅ **PRONTO PARA COMEÇAR**

**Primeira Tarefa:** Criar estrutura de pastas e executar migração de banco.

---

**Documento criado por:** Dev Agent (Alex)  
**Versão:** 1.0

