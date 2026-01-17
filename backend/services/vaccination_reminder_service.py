# -*- coding: utf-8 -*-
"""
Serviço de Lembretes de Vacinação - Envia e-mails de lembretes
"""
import os
import sqlite3
import logging
from datetime import datetime, date, timedelta
from flask import current_app, url_for

logger = logging.getLogger(__name__)

class VaccinationReminderService:
    """Serviço para enviar lembretes de vacinação por e-mail"""
    
    def __init__(self, db_path, send_email_func):
        """
        Args:
            db_path: str - Caminho do banco de dados
            send_email_func: function - Função para enviar e-mail (do app.py)
        """
        self.db_path = db_path
        self.send_email = send_email_func
    
    def send_reminder_email(self, schedule, user, baby):
        """
        Envia e-mail de lembrete para uma vacina específica
        
        Args:
            schedule: dict - Dados do agendamento da vacina
            user: dict - Dados do usuário (mãe)
            baby: dict - Dados do bebê
        
        Returns:
            bool - True se enviado com sucesso
        """
        try:
            # Calcula dias até a vacina
            recommended_date = datetime.strptime(schedule['recommended_date'], '%Y-%m-%d').date()
            days_until = (recommended_date - date.today()).days
            
            # Obtém informação sobre o que a vacina protege
            vaccine_info = self._get_vaccine_info(schedule['vaccine_code'])
            
            # Base URL para links (usa BASE_URL do .env ou localhost)
            base_url = os.getenv('BASE_URL', 'http://localhost:5000')
            
            # Template HTML do e-mail
            subject = f'💉 Lembrete: {schedule["vaccine_name"]} - {baby["name"]}'
            
            html_body = f"""
            <!DOCTYPE html>
            <html lang="pt-BR">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
            </head>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; background: #f9f9f9;">
                    <div style="background: white; border-radius: 12px; padding: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <h2 style="color: #ff8fa3; margin-top: 0; font-size: 24px;">
                            💉 Lembrete de Vacinação
                        </h2>
                        <p style="font-size: 16px;">Olá <strong>{user.get('name', 'Mãe')}</strong>!</p>
                        <p style="font-size: 16px;">
                            Este é um lembrete de que <strong>{baby['name']}</strong> tem uma vacina agendada:
                        </p>
                        
                        <div style="background: #ffe8f0; padding: 20px; border-radius: 8px; margin: 25px 0; border-left: 4px solid #ff8fa3;">
                            <h3 style="margin-top: 0; color: #ff8fa3; font-size: 20px;">
                                {schedule['vaccine_name']}
                            </h3>
                            <p style="margin: 8px 0;"><strong>📅 Data recomendada:</strong> {recommended_date.strftime('%d/%m/%Y')}</p>
                            <p style="margin: 8px 0;"><strong>⏰ Faltam:</strong> {days_until} {'dia' if days_until == 1 else 'dias'}</p>
                            <p style="margin: 8px 0;"><strong>👶 Idade do bebê:</strong> {schedule['age_months']} {'mês' if schedule['age_months'] == 1 else 'meses'}</p>
                            <p style="margin: 8px 0;"><strong>💉 Dose:</strong> {schedule['dose_number']}ª dose</p>
                        </div>
                        
                        <div style="margin: 25px 0;">
                            <p style="font-weight: bold; color: #555; margin-bottom: 8px;">O que esta vacina protege:</p>
                            <p style="color: #666; margin: 0;">{vaccine_info}</p>
                        </div>
                        
                        <div style="margin: 30px 0;">
                            <p style="font-weight: bold; color: #555; margin-bottom: 8px;">📍 Onde aplicar:</p>
                            <p style="color: #666; margin: 0;">
                                Procure uma unidade básica de saúde (UBS) próxima ou posto de saúde mais próximo da sua residência. 
                                As vacinas do calendário PNI são oferecidas gratuitamente pelo SUS.
                            </p>
                        </div>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{base_url}/vaccination" 
                               style="background: #ff8fa3; color: white; padding: 14px 28px; 
                                      text-decoration: none; border-radius: 6px; display: inline-block; 
                                      font-weight: bold; font-size: 16px;">
                                📋 Ver Calendário Completo
                            </a>
                        </div>
                        
                        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                        
                        <p style="font-size: 12px; color: #999; margin: 0; text-align: center;">
                            Este lembrete foi enviado automaticamente 2 dias antes da data recomendada.<br>
                            <strong>Sophia - Sua Amiga do Puerpério</strong>
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Envia e-mail
            success = self.send_email(
                to=user['email'],
                subject=subject,
                body=html_body
            )
            
            if success:
                logger.info(f"Lembrete enviado: Vacina={schedule['vaccine_name']}, Bebê={baby['name']}, Email={user['email']}")
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao enviar lembrete de vacinação: {e}", exc_info=True)
            return False
    
    def _get_vaccine_info(self, vaccine_code):
        """
        Retorna informação sobre o que a vacina protege
        
        Args:
            vaccine_code: str - Código da vacina
        
        Returns:
            str - Descrição do que a vacina protege
        """
        vaccine_info = {
            'BCG': 'Formas graves de tuberculose (meningite tuberculosa e tuberculose miliar).',
            'HEP_B_1': 'Hepatite B e suas complicações (cirrose, câncer de fígado).',
            'PENTA_1': 'Difteria, Tétano, Coqueluche, Meningite por Haemophilus influenzae tipo b e Hepatite B.',
            'PENTA_2': 'Difteria, Tétano, Coqueluche, Hib e Hepatite B (3ª dose).',
            'PENTA_3': 'Difteria, Tétano, Coqueluche, Hib e Hepatite B (3ª dose).',
            'VIP_1': 'Poliomielite (paralisia infantil).',
            'VIP_2': 'Poliomielite.',
            'VOP_3': 'Poliomielite (última dose da série primária).',
            'ROTA_1': 'Diarreia grave causada por rotavírus.',
            'ROTA_2': 'Diarreia grave por rotavírus.',
            'PNEUMO_1': 'Meningite, pneumonia, otite média e outras infecções causadas por pneumococos.',
            'PNEUMO_2': 'Infecções por pneumococos.',
            'PNEUMO_REFORCO': 'Infecções por pneumococos (última dose da série primária).',
            'MENINGO_C_1': 'Meningite e outras doenças graves causadas por Neisseria meningitidis sorogrupo C.',
            'MENINGO_C_2': 'Meningite meningocócica C.',
            'MENINGO_C_REFORCO': 'Meningite meningocócica C (última dose da série primária).',
            'INFLUENZA_1': 'Gripe e suas complicações (deve ser repetida anualmente durante campanhas).',
            'FEBRE_AMARELA': 'Febre amarela (reforço recomendado aos 4 anos).',
            'TRIPLICE_VIRAL_1': 'Sarampo, Caxumba e Rubéola.',
        }
        
        return vaccine_info.get(vaccine_code, 'Vacina importante para a saúde do bebê.')
    
    def process_due_reminders(self):
        """
        Processa e envia lembretes para vacinas com 2 dias de antecedência
        Implementa idempotência para evitar envio duplo
        
        Returns:
            int - Número de lembretes enviados
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Log de início
            logger.info("=" * 60)
            logger.info(f"Processando lembretes de vacinação - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("=" * 60)
            
            # Data alvo: 2 dias a partir de hoje
            target_date = date.today() + timedelta(days=2)
            logger.info(f"Data alvo: {target_date.strftime('%d/%m/%Y')} (2 dias a partir de hoje)")
            
            # Busca vacinas pendentes com data recomendada em 2 dias
            # IMPORTANTE: Apenas busca vacinas NÃO marcadas como enviadas (idempotência)
            cursor.execute('''
                SELECT vs.*, bp.user_id, bp.name as baby_name, bp.birth_date,
                       u.name as user_name, u.email
                FROM vaccination_schedule vs
                JOIN baby_profiles bp ON vs.baby_profile_id = bp.id
                JOIN users u ON bp.user_id = u.id
                WHERE vs.status = 'pending'
                  AND vs.recommended_date = ?
                  AND vs.reminder_sent = 0
                  AND u.email_verified = 1
            ''', (str(target_date),))
            
            schedules = cursor.fetchall()
            logger.info(f"Encontradas {len(schedules)} vacinas para processar")
            
            sent_count = 0
            error_count = 0
            
            for schedule_row in schedules:
                schedule = dict(schedule_row)
                
                # PROTEÇÃO ADICIONAL: Verifica novamente antes de processar (double-check para idempotência)
                cursor.execute('SELECT reminder_sent FROM vaccination_schedule WHERE id = ?', (schedule['id'],))
                result = cursor.fetchone()
                if result and result[0]:  # Já foi enviado
                    logger.info(f"[IDEMPOTÊNCIA] ✅ Lembrete já foi enviado anteriormente para vacina {schedule['id']} (Schedule ID={schedule['id']}) - Ignorando duplicata")
                    print(f"[IDEMPOTÊNCIA] ✅ Lembrete já enviado (idempotência): Schedule ID={schedule['id']}")
                    continue  # Pula
                
                # MARCA ANTES DE ENVIAR (transação atômica para idempotência)
                cursor.execute('''
                    UPDATE vaccination_schedule
                    SET reminder_sent = 1,
                        reminder_sent_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (schedule['id'],))
                conn.commit()  # Salva imediatamente
                
                # Prepara dados do usuário e bebê
                user = {
                    'name': schedule['user_name'],
                    'email': schedule['email']
                }
                
                baby = {
                    'name': schedule['baby_name'],
                    'birth_date': schedule['birth_date']
                }
                
                # Envia lembrete
                try:
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
            
        except Exception as e:
            logger.error("=" * 60)
            logger.error(f"❌ Erro ao processar lembretes: {e}", exc_info=True)
            logger.error("=" * 60)
            return 0
        finally:
            conn.close()
