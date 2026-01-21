# -*- coding: utf-8 -*-
"""
Serviço de Vacinação - Lógica de negócio para agenda de vacinação
"""
import sqlite3
import logging
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)

class VaccinationService:
    """Serviço para gerenciar vacinações"""
    
    def __init__(self, db_path):
        self.db_path = db_path
    
    def calculate_recommended_date(self, birth_date, age_months, age_days=0):
        """
        Calcula data recomendada baseada na data de nascimento
        
        Args:
            birth_date: datetime.date - Data de nascimento do bebê
            age_months: int - Idade em meses quando deve ser aplicada
            age_days: int - Dias adicionais (default: 0)
        
        Returns:
            datetime.date - Data recomendada para aplicação
        """
        if isinstance(birth_date, str):
            birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
        
        recommended = birth_date + relativedelta(months=age_months) + timedelta(days=age_days)
        return recommended
    
    def create_baby_profile(self, user_id, name, birth_date, gender=None):
        """
        Cria perfil do bebê e calcula automaticamente o calendário de vacinação
        
        Args:
            user_id: int - ID do usuário (mãe)
            name: str - Nome do bebê
            birth_date: str ou date - Data de nascimento (formato 'YYYY-MM-DD')
            gender: str - Gênero ('male', 'female', 'other', None)
        
        Returns:
            int - ID do perfil criado
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Converte birth_date se necessário
            if isinstance(birth_date, str):
                birth_date_obj = datetime.strptime(birth_date, '%Y-%m-%d').date()
            else:
                birth_date_obj = birth_date
            
            # Verifica duplicatas
            cursor.execute('''
                SELECT id FROM baby_profiles 
                WHERE user_id = ? AND name = ? AND birth_date = ?
            ''', (user_id, name, str(birth_date_obj)))
            
            if cursor.fetchone():
                raise ValueError(f"Bebê '{name}' com data de nascimento {birth_date_obj} já cadastrado")
            
            # Insere perfil do bebê
            cursor.execute('''
                INSERT INTO baby_profiles (user_id, name, birth_date, gender, created_at, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ''', (user_id, name, str(birth_date_obj), gender))
            
            baby_profile_id = cursor.lastrowid
            
            # Calcula e insere calendário de vacinação
            self._create_vaccination_schedule(cursor, baby_profile_id, birth_date_obj)
            
            conn.commit()
            logger.info(f"Perfil do bebê criado: ID={baby_profile_id}, Nome={name}, User={user_id}")
            return baby_profile_id
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Erro ao criar perfil do bebê: {e}")
            raise
        finally:
            conn.close()
    
    def _create_vaccination_schedule(self, cursor, baby_profile_id, birth_date):
        """
        Cria calendário de vacinação baseado no PNI
        
        Args:
            cursor: sqlite3.Cursor - Cursor do banco
            baby_profile_id: int - ID do perfil do bebê
            birth_date: date - Data de nascimento
        """
        # Busca todas as vacinas do PNI (primeiro ano de vida)
        cursor.execute('''
            SELECT vaccine_code, vaccine_name, age_months, age_days, dose_number, description, is_optional
            FROM vaccine_reference
            WHERE age_months <= 12
            ORDER BY age_months, age_days, dose_number
        ''')
        
        vaccines = cursor.fetchall()
        
        for vaccine_code, vaccine_name, age_months, age_days, dose_number, description, is_optional in vaccines:
            recommended_date = self.calculate_recommended_date(birth_date, age_months, age_days)
            
            cursor.execute('''
                INSERT INTO vaccination_schedule (
                    baby_profile_id, vaccine_name, vaccine_code, age_months, age_days,
                    dose_number, recommended_date, status, is_optional, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ''', (baby_profile_id, vaccine_name, vaccine_code, age_months, age_days, 
                  dose_number, str(recommended_date), 1 if is_optional else 0))
    
    def get_vaccination_status(self, baby_profile_id):
        """
        Retorna status completo da vacinação de um bebê
        
        Args:
            baby_profile_id: int - ID do perfil do bebê
        
        Returns:
            dict - Dados completos da vacinação
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Busca perfil do bebê
            cursor.execute('''
                SELECT id, user_id, name, birth_date, gender, created_at
                FROM baby_profiles WHERE id = ?
            ''', (baby_profile_id,))
            
            baby_row = cursor.fetchone()
            if not baby_row:
                return None
            
            baby = dict(baby_row)
            
            # Calcula idade atual
            birth_date = datetime.strptime(baby['birth_date'], '%Y-%m-%d').date()
            today = date.today()
            age_delta = relativedelta(today, birth_date)
            baby['age_days'] = (today - birth_date).days
            baby['age_months'] = age_delta.months + (age_delta.years * 12)
            
            # Busca calendário de vacinação
            cursor.execute('''
                SELECT id, vaccine_name, vaccine_code, age_months, age_days, dose_number,
                       recommended_date, status, administered_date, administered_location,
                       administered_by, lot_number, reminder_sent, reminder_sent_at,
                       is_optional, notes
                FROM vaccination_schedule
                WHERE baby_profile_id = ?
                ORDER BY recommended_date, dose_number
            ''', (baby_profile_id,))
            
            schedules = [dict(row) for row in cursor.fetchall()]
            
            # Calcula estatísticas
            stats = self._calculate_statistics(schedules)
            
            # Busca próximas vacinas (pendentes, próximas 30 dias)
            upcoming = self._get_upcoming_vaccines(schedules, today)
            
            return {
                'baby': baby,
                'vaccination_schedule': schedules,
                'statistics': stats,
                'upcoming_vaccines': upcoming
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar status de vacinação: {e}", exc_info=True)
            import traceback
            traceback.print_exc()
            raise
        finally:
            if conn:
                conn.close()
    
    def _calculate_statistics(self, schedules):
        """Calcula estatísticas do calendário"""
        total = len(schedules)
        completed = len([s for s in schedules if s['status'] == 'completed'])
        pending = len([s for s in schedules if s['status'] == 'pending'])
        missed = len([s for s in schedules if s['status'] == 'missed'])
        scheduled = len([s for s in schedules if s['status'] == 'scheduled'])
        
        completion_percentage = (completed / total * 100) if total > 0 else 0
        
        return {
            'total_vaccines': total,
            'completed': completed,
            'pending': pending,
            'missed': missed,
            'scheduled': scheduled,
            'completion_percentage': round(completion_percentage, 1)
        }
    
    def _get_upcoming_vaccines(self, schedules, today):
        """Retorna próximas vacinas pendentes"""
        upcoming = []
        for schedule in schedules:
            if schedule['status'] == 'pending':
                try:
                    recommended_date = datetime.strptime(schedule['recommended_date'], '%Y-%m-%d').date()
                    days_until = (recommended_date - today).days
                    if days_until <= 30:  # Próximos 30 dias
                        upcoming.append({
                            'id': schedule['id'],
                            'vaccine_name': schedule['vaccine_name'],
                            'recommended_date': schedule['recommended_date'],
                            'days_until': days_until,
                            'reminder_sent': bool(schedule['reminder_sent'])
                        })
                except:
                    continue
        
        return sorted(upcoming, key=lambda x: x['days_until'])
    
    def mark_vaccine_done(self, schedule_id, administered_date=None, 
                         administered_location=None, administered_by=None, 
                         lot_number=None, notes=None):
        """
        Marca vacina como aplicada (IDEMPOTENTE)
        
        Args:
            schedule_id: int - ID do agendamento
            administered_date: str ou date - Data de aplicação (default: hoje)
            administered_location: str - Local da aplicação
            administered_by: str - Profissional/unidade
            lot_number: str - Número do lote
            notes: str - Observações
        
        Returns:
            bool - True se sucesso, False se já estava marcada (idempotente)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # IDEMPOTÊNCIA: Verifica se já está marcada
            cursor.execute('''
                SELECT status, administered_date 
                FROM vaccination_schedule 
                WHERE id = ? AND status = 'completed'
            ''', (schedule_id,))
            
            existing = cursor.fetchone()
            if existing:
                # Já está marcada, retorna True (idempotente)
                logger.info(f"[IDEMPOTÊNCIA] ✅ Vacina já estava marcada anteriormente (Schedule ID={schedule_id}) - Requisição duplicada ignorada")
                print(f"[IDEMPOTÊNCIA] ✅ Vacina já estava marcada (idempotência): Schedule ID={schedule_id}")
                conn.close()
                return True
            
            # Usa data de hoje se não informada
            if administered_date is None:
                administered_date = date.today()
            elif isinstance(administered_date, str):
                administered_date = datetime.strptime(administered_date, '%Y-%m-%d').date()
            
            # Busca dados do agendamento
            cursor.execute('''
                SELECT baby_profile_id, vaccine_name, vaccine_code, dose_number
                FROM vaccination_schedule WHERE id = ?
            ''', (schedule_id,))
            
            schedule_data = cursor.fetchone()
            if not schedule_data:
                raise ValueError(f"Agendamento {schedule_id} não encontrado")
            
            baby_profile_id, vaccine_name, vaccine_code, dose_number = schedule_data
            
            # IDEMPOTÊNCIA: Verifica se já existe no histórico
            cursor.execute('''
                SELECT id FROM vaccination_history
                WHERE schedule_id = ? AND baby_profile_id = ?
            ''', (schedule_id, baby_profile_id))
            
            history_exists = cursor.fetchone()
            
            # Atualiza agendamento
            cursor.execute('''
                UPDATE vaccination_schedule
                SET status = 'completed',
                    administered_date = ?,
                    administered_location = ?,
                    administered_by = ?,
                    lot_number = ?,
                    notes = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (str(administered_date), administered_location, administered_by,
                  lot_number, notes, schedule_id))
            
            # Cria registro histórico apenas se não existir (idempotência)
            if not history_exists:
                cursor.execute('''
                    INSERT INTO vaccination_history (
                        schedule_id, baby_profile_id, vaccine_name, vaccine_code,
                        dose_number, administered_date, administered_location,
                        administered_by, lot_number, notes, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (schedule_id, baby_profile_id, vaccine_name, vaccine_code,
                      dose_number, str(administered_date), administered_location,
                      administered_by, lot_number, notes))
            
            # COMMIT antes de verificar (garante salvamento)
            conn.commit()
            
            # Verifica se foi salvo corretamente (confirmação de persistência)
            cursor.execute('''
                SELECT status, administered_date 
                FROM vaccination_schedule 
                WHERE id = ? AND status = 'completed'
            ''', (schedule_id,))
            
            confirmed = cursor.fetchone()
            conn.close()
            
            if confirmed:
                logger.info(f"✅ Vacina marcada e CONFIRMADA no banco: Schedule ID={schedule_id}, Vacina={vaccine_name}, Data={confirmed[1]}")
                return True
            else:
                logger.error(f"❌ ERRO: Vacina não foi salva após commit! Schedule ID={schedule_id}")
                return False
            
        except Exception as e:
            conn.rollback()
            conn.close()
            logger.error(f"Erro ao marcar vacina como aplicada: {e}", exc_info=True)
            raise