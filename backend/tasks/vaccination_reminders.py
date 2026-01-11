# -*- coding: utf-8 -*-
"""
Tarefa Agendada - Envio de Lembretes de Vacinação
Executa diariamente às 08:00 para enviar lembretes 2 dias antes de cada vacina

Execução:
- Via APScheduler: Agendar para rodar diariamente às 08:00
- Via Cron: 0 8 * * * python backend/tasks/vaccination_reminders.py
- Manualmente: python backend/tasks/vaccination_reminders.py
"""
import os
import sys
import logging
from datetime import datetime

# Configurar logging para terminal
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [VACCINATION REMINDERS] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger('vaccination_reminders')

# Adiciona caminho do projeto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from flask import Flask
from backend.services.vaccination_reminder_service import VaccinationReminderService
from backend.app import send_email, DB_PATH

def send_vaccination_reminders():
    """
    Tarefa agendada para enviar lembretes diariamente
    Implementa idempotência e logging detalhado
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
            
            # Processa e envia lembretes (com idempotência e logging)
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
