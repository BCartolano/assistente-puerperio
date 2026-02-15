/**
 * Vaccination Timeline - Gerencia a interface da Agenda de Vacinação
 */
(function() {
    'use strict';

    class VaccinationTimeline {
        constructor() {
            this.babyData = null;
            this.vaccinationData = null;
            this.isLoading = false;
            this.log = (...args) => {
                if (window.chatApp && window.chatApp.isDevelopment) {
                    console.log('[VaccinationTimeline]', ...args);
                }
            };
        }

        /**
         * Carrega dados da vacinação da API
         */
        async loadVaccinationData() {
            if (this.isLoading) return;
            
            // Verifica se apiClient está disponível e usuário está autenticado
            if (!window.apiClient) {
                this.log('apiClient não disponível ainda');
                return;
            }
            
            this.isLoading = true;

            try {
                const response = await window.apiClient.get('/api/vaccination/status');
                
                if (response.error) {
                    this.log('Erro ao carregar dados:', response.error);
                    // Não mostra erro se usuário não estiver autenticado ou não tiver perfil de bebê
                    if (response.message && !response.message.includes('Nenhum perfil de bebê encontrado')) {
                        this.showErrorMessage(response.message || 'Erro ao carregar calendário de vacinação');
                    }
                    this.renderEmpty();
                    return;
                }

                // Aceita formatos diferentes: {timeline:[...]}, {vaccines:[...]}, ou objeto com baby/vaccination_schedule
                this.babyData = response.baby || response.babyData || null;
                this.vaccinationData = response;
                
                this.renderTimeline();
                this.updateNextVaccineWidget();
                this.checkVaccineTodayAndShowAlert();
                this.log('Dados de vacinação carregados:', response);
                
            } catch (error) {
                // Não mostra erro se for 401/403 (não autenticado) ou 404 (sem perfil de bebê)
                // Esses são casos esperados e não devem ser tratados como erros
                if (error.response && (error.response.status === 401 || error.response.status === 403 || error.response.status === 404)) {
                    this.log('Usuário não autenticado ou sem perfil de bebê - inicialização adiada');
                    return;
                }
                
                this.log('Erro na requisição:', error);
                // Só mostra erro se for um problema real (erro 500, etc)
                if (!error.response || error.response.status >= 500) {
                    this.showErrorMessage('Erro ao carregar calendário de vacinação. Tente novamente.');
                }
            } finally {
                this.isLoading = false;
            }
        }

        /**
         * Renderiza a timeline de vacinação
         */
        renderTimeline() {
            const container = document.getElementById('vaccination-timeline-container');
            if (!container || !this.vaccinationData) {
                this.renderEmpty();
                return;
            }

            // Aceita formatos diferentes: {timeline:[...]}, {vaccines:[...]}, ou array direto
            const data = this.vaccinationData;
            const baby = data.baby || data.babyData || null;
            const vaccination_schedule = Array.isArray(data.timeline) ? data.timeline
                : Array.isArray(data.vaccines) ? data.vaccines
                : Array.isArray(data.vaccination_schedule) ? data.vaccination_schedule
                : Array.isArray(data) ? data
                : [];
            const statistics = data.statistics || { completed: 0, pending: 0, completion_percentage: 0 };

            if (!baby || !vaccination_schedule.length) {
                this.renderEmpty();
                return;
            }

            // Cria estrutura HTML
            const babyName = baby?.name || baby?.nome || 'Bebê';
            let html = `
                <div class="vaccination-timeline">
                    <div class="vaccination-header">
                        <h2>💉 Jornada de Proteção - ${babyName}</h2>
                        <div class="vaccination-stats">
                            <div class="stat-item">
                                <span class="stat-number">${statistics.completed}</span>
                                <span class="stat-label">Concluídas</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-number">${statistics.pending}</span>
                                <span class="stat-label">Pendentes</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-number">${statistics.completion_percentage}%</span>
                                <span class="stat-label">Progresso</span>
                            </div>
                        </div>
                    </div>

                    <div class="progress-bar-container">
                        <div class="progress-bar" style="width: ${statistics.completion_percentage}%"></div>
                    </div>

                    <div class="timeline-content">
            `;

            // Agrupa vacinas por idade
            const groupedByAge = this.groupVaccinesByAge(vaccination_schedule);
            
            // Encontra próxima vacina
            const nextVaccine = this.findNextVaccine(vaccination_schedule);

            // Renderiza cada grupo etário
            Object.keys(groupedByAge).sort((a, b) => {
                const ageA = this.parseAgeString(a);
                const ageB = this.parseAgeString(b);
                return ageA.months - ageB.months || ageA.days - ageB.days;
            }).forEach(ageLabel => {
                const vaccines = groupedByAge[ageLabel];
                html += this.renderAgeGroup(ageLabel, vaccines, nextVaccine);
            });

            html += `
                    </div>

                    ${nextVaccine ? this.renderNextVaccineCard(nextVaccine) : ''}
                </div>
            `;

            container.innerHTML = html;
            
            // Adiciona event listeners
            this.attachEventListeners();
        }

        /**
         * Agrupa vacinas por idade (ao nascer, 2 meses, etc.)
         */
        groupVaccinesByAge(schedule) {
            const groups = {};
            
            schedule.forEach(vaccine => {
                let ageLabel = '';
                if (vaccine.age_months === 0 && vaccine.age_days === 0) {
                    ageLabel = 'Ao Nascer';
                } else if (vaccine.age_months === 1) {
                    ageLabel = '1 Mês';
                } else {
                    ageLabel = `${vaccine.age_months} Meses`;
                }

                if (!groups[ageLabel]) {
                    groups[ageLabel] = [];
                }
                groups[ageLabel].push(vaccine);
            });

            return groups;
        }

        /**
         * Parse idade string para comparação
         */
        parseAgeString(ageStr) {
            if (ageStr === 'Ao Nascer') return { months: 0, days: 0 };
            const match = ageStr.match(/(\d+)\s+M(?:ês|eses)/);
            return match ? { months: parseInt(match[1]), days: 0 } : { months: 0, days: 0 };
        }

        /**
         * Renderiza grupo etário
         */
        renderAgeGroup(ageLabel, vaccines, nextVaccine) {
            const today = new Date();
            const firstVaccine = vaccines[0];
            let recommendedDate = null;
            let daysUntil = null;

            if (firstVaccine.recommended_date) {
                recommendedDate = new Date(firstVaccine.recommended_date);
                daysUntil = Math.ceil((recommendedDate - today) / (1000 * 60 * 60 * 24));
            }

            let html = `
                <div class="age-group">
                    <div class="age-group-header">
                        <h3>${ageLabel === 'Ao Nascer' ? '✅' : '📅'} ${ageLabel}</h3>
                        ${recommendedDate ? `<span class="age-group-date">${this.formatDate(recommendedDate)}${daysUntil !== null ? ` - ${daysUntil > 0 ? `Faltam ${daysUntil} dias` : daysUntil === 0 ? 'Hoje' : 'Atrasada'}` : ''}</span>` : ''}
                    </div>
                    <div class="vaccines-grid">
            `;

            vaccines.forEach(vaccine => {
                // Render com optional chaining e fallback
                const vaccineName = vaccine?.name || vaccine?.vaccine || vaccine?.vaccine_name || 'Vacina';
                const vaccineStatus = vaccine?.status || vaccine?.state || '';
                const _vaccineDate = vaccine?.date || vaccine?.applied_at || vaccine?.recommended_date || '';
                const isNext = nextVaccine && (nextVaccine.id === vaccine.id || nextVaccine.vaccine_name === vaccineName);
                html += this.renderVaccineCard({ ...vaccine, vaccine_name: vaccineName, status: vaccineStatus }, isNext);
            });

            html += `
                    </div>
                </div>
            `;

            return html;
        }

        /**
         * Renderiza card de vacina individual
         */
        renderVaccineCard(vaccine, isNext) {
            // Aceita formatos diferentes com fallback
            const vaccineName = vaccine?.vaccine_name || vaccine?.name || vaccine?.vaccine || 'Vacina';
            const status = vaccine?.status || vaccine?.state || '';
            const vaccineId = vaccine?.id || vaccine?.schedule_id || '';
            const doseNumber = vaccine?.dose_number || vaccine?.dose || 0;
            const today = new Date();
            let recommendedDate = null;
            let daysUntil = null;

            if (vaccine?.recommended_date || vaccine?.date) {
                recommendedDate = new Date(vaccine.recommended_date || vaccine.date);
                daysUntil = Math.ceil((recommendedDate - today) / (1000 * 60 * 60 * 24));
            }

            const isOverdue = daysUntil !== null && daysUntil < 0 && status === 'pending';
            const cardClasses = [
                'vaccine-card',
                status === 'completed' ? 'completed' : '',
                status === 'pending' && isNext ? 'next' : '',
                isOverdue ? 'overdue' : '',
                status === 'pending' && !isNext && !isOverdue ? 'pending' : ''
            ].filter(c => c).join(' ');

            let html = `
                <div class="${cardClasses}" data-vaccine-id="${vaccineId}">
                    <div class="vaccine-card-header">
                        <div class="vaccine-icon">
                            ${status === 'completed' ? '✓' : isNext ? '⭐' : isOverdue ? '⚠️' : '⏳'}
                        </div>
                        <div class="vaccine-info">
                            <h4>${vaccineName}</h4>
                            ${doseNumber > 0 ? `<span class="dose-badge">${doseNumber}ª dose</span>` : ''}
                        </div>
                    </div>
            `;

            const administeredDate = vaccine?.administered_date || vaccine?.applied_at || null;
            const administeredLocation = vaccine?.administered_location || vaccine?.location || null;
            
            if (status === 'completed' && administeredDate) {
                html += `
                    <div class="vaccine-card-body">
                        <p class="vaccine-status-completed">✓ Aplicada em ${this.formatDate(new Date(administeredDate))}</p>
                        ${administeredLocation ? `<p class="vaccine-location">📍 ${administeredLocation}</p>` : ''}
                    </div>
                `;
            } else {
                html += `
                    <div class="vaccine-card-body">
                        <p class="vaccine-recommended-date">📅 Recomendada: ${recommendedDate ? this.formatDate(recommendedDate) : 'Em breve'}</p>
                        ${daysUntil !== null ? `<p class="vaccine-days-until">${daysUntil > 0 ? `⏰ Faltam ${daysUntil} dias` : daysUntil === 0 ? '⏰ Hoje!' : '⚠️ Atrasada, mas ainda pode ser aplicada'}</p>` : ''}
                        ${isNext ? `<button class="btn btn-mark-vaccine" data-schedule-id="${vaccineId}">Marcar como Aplicada 💉</button>` : ''}
                    </div>
                `;
            }

            html += `</div>`;
            return html;
        }

        /**
         * Renderiza card destacado da próxima vacina
         */
        renderNextVaccineCard(nextVaccine) {
            const today = new Date();
            const recommendedDate = new Date(nextVaccine.recommended_date);
            const daysUntil = Math.ceil((recommendedDate - today) / (1000 * 60 * 60 * 24));

            // Busca descrição do que protege (será melhorado)
            const protectsInfo = this.getVaccineProtectionInfo(nextVaccine.vaccine_code);

            return `
                <div class="next-vaccine-card">
                    <div class="next-vaccine-header">
                        <h3>🔜 Próxima Vacina</h3>
                    </div>
                    <div class="next-vaccine-content">
                        <h4>${nextVaccine.vaccine_name}</h4>
                        <p class="next-vaccine-date">📅 ${this.formatDate(recommendedDate)} ${daysUntil > 0 ? `(em ${daysUntil} dias)` : daysUntil === 0 ? '(Hoje!)' : '(Atrasada)'}</p>
                        <p class="next-vaccine-protects">💡 Protege contra: ${protectsInfo}</p>
                        <button class="btn btn-primary btn-mark-vaccine-large" data-schedule-id="${nextVaccine.id}">
                            Marcar como Aplicada 💉✨
                        </button>
                    </div>
                </div>
            `;
        }

        /**
         * Busca informação sobre o que a vacina protege
         */
        getVaccineProtectionInfo(vaccineCode) {
            const protectionInfo = {
                'BCG': 'formas graves de tuberculose',
                'HEP_B_1': 'hepatite B e suas complicações',
                'PENTA_1': 'difteria, tétano, coqueluche, meningite por Hib e hepatite B',
                'PENTA_2': 'difteria, tétano, coqueluche, Hib e hepatite B',
                'PENTA_3': 'difteria, tétano, coqueluche, Hib e hepatite B',
                'VIP_1': 'poliomielite (paralisia infantil)',
                'VIP_2': 'poliomielite',
                'VOP_3': 'poliomielite',
                'ROTA_1': 'diarreia grave por rotavírus',
                'ROTA_2': 'diarreia grave por rotavírus',
                'PNEUMO_1': 'meningite, pneumonia e outras infecções por pneumococos',
                'PNEUMO_2': 'infecções por pneumococos',
                'PNEUMO_REFORCO': 'infecções por pneumococos',
                'MENINGO_C_1': 'meningite meningocócica C',
                'MENINGO_C_2': 'meningite meningocócica C',
                'MENINGO_C_REFORCO': 'meningite meningocócica C',
                'INFLUENZA_1': 'gripe e suas complicações',
                'FEBRE_AMARELA': 'febre amarela',
                'TRIPLICE_VIRAL_1': 'sarampo, caxumba e rubéola'
            };
            
            return protectionInfo[vaccineCode] || 'doenças importantes';
        }

        /**
         * Encontra próxima vacina pendente
         */
        findNextVaccine(schedule) {
            if (!schedule || !Array.isArray(schedule)) {
                return null;
            }
            
            const _today = new Date();
            const pending = schedule.filter(v => v.status === 'pending' && v.recommended_date);
            
            if (pending.length === 0) return null;

            // Ordena por data recomendada
            pending.sort((a, b) => {
                const dateA = new Date(a.recommended_date);
                const dateB = new Date(b.recommended_date);
                return dateA - dateB;
            });

            return pending[0];
        }

        /**
         * Retorna "Mamãe" ou "Bebê" conforme o tipo da vacina
         */
        getParaQuem(vaccine) {
            const name = (vaccine.vaccine_name || '').toLowerCase();
            if (name.includes('gestante') || name.includes('puérpera') || name.includes('mãe')) {
                return 'Mamãe';
            }
            return 'Bebê';
        }

        /**
         * Atualiza card "Agenda de Vacinação" com vacinas pendentes
         */
        updateNextVaccineWidget() {
            const card = document.getElementById('agenda-de-vacinacao-card');
            const contentEl = document.getElementById('agenda-content');
            const textEl = document.getElementById('agenda-text');
            if (!card || !contentEl || !textEl) return;
            if (!this.vaccinationData) {
                contentEl.innerHTML = '<p class="agenda-text">Carregando agenda...</p>';
                return;
            }

            const babyExists = this.vaccinationData.baby_profile_exists !== false;
            if (!babyExists) {
                window.__agendaTomorrowFromPNI = false;
                this.applyAgendaCardTomorrowAlert();
                contentEl.innerHTML = '<p class="agenda-text">Cadastre o perfil do bebê para ver a agenda.</p>';
                return;
            }

            const schedule = this.vaccinationData.vaccination_schedule || this.vaccinationData.timeline || this.vaccinationData.vaccines || [];
            const nextVaccine = this.findNextVaccine(schedule);
            
            if (!nextVaccine) {
                card?.classList.remove('card-alert-today');
                window.__agendaTomorrowFromPNI = false;
                this.applyAgendaCardTomorrowAlert();
                contentEl.innerHTML = '<p class="agenda-success">Todas as vacinas aplicadas. 🎉</p>';
                return;
            }

            const recommendedDate = new Date(nextVaccine.recommended_date);
            const paraQuem = this.getParaQuem(nextVaccine);
            const local = nextVaccine.administered_location || nextVaccine.scheduled_location || 'Consulte a UBS mais próxima';
            const dataStr = this.formatDate(recommendedDate);
            const isToday = this.isDateToday(nextVaccine.recommended_date);

            if (isToday) {
                card?.classList.add('card-alert-today');
            } else {
                card?.classList.remove('card-alert-today');
            }
            window.__agendaTomorrowFromPNI = this.isDateTomorrow(nextVaccine.recommended_date);
            this.applyAgendaCardTomorrowAlert();

            const reminderBtn = `
                <button type="button" class="btn-agenda-reminder" id="btn-agenda-reminder" aria-label="Ativar lembretes de vacina no celular">
                    🔔 Ativar lembretes no celular
                </button>
            `;

            contentEl.innerHTML = `
                <p class="agenda-vaccine-name"><strong>${this.escapeHtml(nextVaccine.vaccine_name)}</strong></p>
                <p class="agenda-para-quem">Para: ${paraQuem}</p>
                <p class="agenda-date">📅 ${dataStr}</p>
                <p class="agenda-local">📍 ${this.escapeHtml(local)}</p>
                <div class="agenda-actions">${reminderBtn}</div>
            `;

            this.attachAgendaReminderButton();
        }

        isDateToday(dateStr) {
            if (!dateStr) return false;
            const today = new Date();
            const d = new Date(dateStr);
            return d.getFullYear() === today.getFullYear() && d.getMonth() === today.getMonth() && d.getDate() === today.getDate();
        }

        /**
         * Verifica se a data é amanhã (para vigia: card em tom de alerta leve).
         */
        isDateTomorrow(dateStr) {
            if (!dateStr) return false;
            const today = new Date();
            const d = new Date(dateStr);
            const tomorrow = new Date(today);
            tomorrow.setDate(tomorrow.getDate() + 1);
            return d.getFullYear() === tomorrow.getFullYear() && d.getMonth() === tomorrow.getMonth() && d.getDate() === tomorrow.getDate();
        }

        /**
         * Aplica estado de alerta "amanhã" no card (vigia). Usa a função global para o script de lembretes também.
         */
        applyAgendaCardTomorrowAlert() {
            if (typeof window.applyAgendaCardTomorrowAlert === 'function') {
                window.applyAgendaCardTomorrowAlert();
            }
        }

        /**
         * Vacinas para hoje (pendentes)
         */
        getVaccinesForToday(schedule) {
            if (!schedule || !Array.isArray(schedule)) return [];
            const today = new Date().toISOString().slice(0, 10);
            return schedule.filter(v => v.status === 'pending' && v.recommended_date && v.recommended_date.slice(0, 10) === today);
        }

        /**
         * Verifica se há vacina hoje e exibe alerta (banner + toast).
         * Não exibe se a usuária já fechou o banner hoje (persiste até novo login ou dia seguinte).
         */
        async checkVaccineTodayAndShowAlert() {
            if (!this.vaccinationData || !this.vaccinationData.baby_profile_exists) return;
            const schedule = this.vaccinationData.vaccination_schedule || this.vaccinationData.timeline || this.vaccinationData.vaccines || [];
            const forToday = this.getVaccinesForToday(schedule);
            if (forToday.length === 0) return;

            const todayStr = new Date().toISOString().slice(0, 10);
            const dismissedDate = localStorage.getItem('sophia_vaccine_banner_dismissed');
            if (dismissedDate === todayStr) return; // Já fechou hoje, não incomodar

            const babyName = this.babyData?.name || this.babyData?.nome || 'seu bebê';
            let userName = 'Mamãe';
            try {
                const r = await (window.apiClient?.get?.('/api/user') || Promise.resolve(null));
                if (r && !r.erro && (r.user?.name || r.name)) {
                    userName = r.user?.name || r.name;
                }
            } catch (_) {}

            const vaccineNames = forToday.map(v => v.vaccine_name).join(', ');
            const msg = `Atenção ${userName}: Hoje é dia de vacina para ${babyName}! 💉`;
            const fullMsg = vaccineNames ? `${msg} ${vaccineNames}` : msg;

            if (window.toast && typeof window.toast.show === 'function') {
                window.toast.show(fullMsg, 'info', 8000);
            } else if (window.toast?.success) {
                window.toast.success(fullMsg, 8000);
            }

            this.showVaccineTodayBanner(userName, babyName, vaccineNames);
        }

        /**
         * Exibe banner fixo no topo quando há vacina hoje
         */
        showVaccineTodayBanner(userName, babyName, vaccineNames) {
            let banner = document.getElementById('vaccine-today-banner');
            if (banner) banner.remove();
            banner = document.createElement('div');
            banner.id = 'vaccine-today-banner';
            banner.className = 'vaccine-today-banner';
            banner.innerHTML = `
                <div class="vaccine-today-banner-inner">
                    <span class="vaccine-today-icon">💉</span>
                    <span class="vaccine-today-text">Atenção ${this.escapeHtml(userName)}: Hoje é dia de vacina para ${this.escapeHtml(babyName)}! ${vaccineNames ? this.escapeHtml(vaccineNames) : ''}</span>
                    <a href="#" class="vaccine-today-link" id="vaccine-today-link-where">Ver onde vacinar</a>
                    <button type="button" class="vaccine-today-close" aria-label="Fechar aviso">×</button>
                </div>
            `;

            document.body.insertBefore(banner, document.body.firstChild);

            banner.querySelector('#vaccine-today-link-where').addEventListener('click', (e) => {
                e.preventDefault();
                if (window.chatApp && typeof window.chatApp.findNearbyHospitals === 'function') {
                    window.chatApp.findNearbyHospitals();
                }
            });
            banner.querySelector('.vaccine-today-close').addEventListener('click', () => {
                const todayStr = new Date().toISOString().slice(0, 10);
                localStorage.setItem('sophia_vaccine_banner_dismissed', todayStr);
                banner.remove();
            });
        }

        attachAgendaReminderButton() {
            const btn = document.getElementById('btn-agenda-reminder');
            if (!btn) return;
            btn.addEventListener('click', () => {
                if (!('Notification' in window)) {
                    if (window.toast?.warning) window.toast.warning('Seu navegador não suporta notificações.', 4000);
                    return;
                }
                if (Notification.permission === 'granted') {
                    if (window.toast?.success) window.toast.success('Lembretes já estão ativados! 💚', 3000);
                    return;
                }
                Notification.requestPermission().then((perm) => {
                    if (perm === 'granted') {
                        if (window.toast?.success) window.toast.success('Lembretes ativados! Você receberá avisos de vacina. 💚', 4000);
                    } else if (perm !== 'denied') {
                        if (window.toast?.info) window.toast.show('Ative as notificações nas configurações do navegador para receber lembretes.', 'info', 5000);
                    }
                });
            });
        }

        escapeHtml(str) {
            if (!str) return '';
            const div = document.createElement('div');
            div.textContent = str;
            return div.innerHTML;
        }

        /**
         * Formata data para exibição
         */
        formatDate(date) {
            if (!date || !(date instanceof Date) || isNaN(date)) return '';
            return date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' });
        }

        /**
         * Adiciona event listeners aos botões
         */
        attachEventListeners() {
            // Botões "Marcar como Aplicada"
            document.querySelectorAll('.btn-mark-vaccine, .btn-mark-vaccine-large').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const scheduleId = parseInt(e.target.dataset.scheduleId);
                    this.showMarkDoneModal(scheduleId);
                });
            });
        }

        /**
         * Exibe modal para marcar vacina como aplicada
         */
        showMarkDoneModal(scheduleId) {
            const vaccine = this.vaccinationData.vaccination_schedule.find(v => v.id === scheduleId);
            if (!vaccine) return;

            // Por enquanto, marca direto. Depois pode adicionar modal com mais campos
            this.markVaccineAsDone(scheduleId);
        }

        /**
         * Marca vacina como aplicada via API
         */
        async markVaccineAsDone(scheduleId, data = {}) {
            try {
                const vaccine = this.vaccinationData.vaccination_schedule.find(v => v.id === scheduleId);
                
                const response = await window.apiClient.post('/api/vaccination/mark-done', {
                    schedule_id: scheduleId,
                    administered_date: data.administered_date || null,
                    administered_location: data.administered_location || null,
                    administered_by: data.administered_by || null,
                    lot_number: data.lot_number || null,
                    notes: data.notes || null
                });

                if (response.success) {
                    const userName = response.user_name || null;
                    if (vaccine) {
                        this.showCelebrationModal(vaccine, userName);
                    }
                    await this.loadVaccinationData();
                } else {
                    alert('Erro ao marcar vacina como aplicada: ' + (response.error || 'Erro desconhecido'));
                }
            } catch (error) {
                this.log('Erro ao marcar vacina:', error);
                alert('Erro ao marcar vacina como aplicada. Tente novamente.');
            }
        }

        /**
         * Exibe modal de comemoração (com nome personalizado da mamãe)
         */
        showCelebrationModal(vaccine, userName = null) {
            const modal = document.getElementById('celebration-modal');
            if (!modal) {
                this.createCelebrationModal();
            }

            const modalElement = document.getElementById('celebration-modal');
            const babyName = this.babyData ? this.babyData.name : 'seu bebê';
            const vaccineName = vaccine ? vaccine.vaccine_name : 'vacina';
            const user = userName || 'Mamãe';

            const msgEl = document.getElementById('celebration-message');
            msgEl.innerHTML = `Parabéns pela proteção do ${babyName}! 💕<br><span style="font-size:0.9em;margin-top:0.5rem;display:block;">E parabéns para você também, ${user}! 💕</span>`;
            document.getElementById('celebration-vaccine-name').textContent = vaccineName;

            modalElement.style.display = 'flex';
            document.body.style.overflow = 'hidden';

            // Anima confetes
            this.animateConfetti();
        }

        /**
         * Cria modal de comemoração no DOM
         */
        createCelebrationModal() {
            const modalHTML = `
                <div class="celebration-modal" id="celebration-modal" style="display: none;">
                    <div class="celebration-modal-overlay"></div>
                    <div class="celebration-modal-content">
                        <div class="celebration-icons">
                            <span class="celebration-icon">🎉</span>
                            <span class="celebration-icon">✨</span>
                            <span class="celebration-icon">🎊</span>
                        </div>
                        <h2>Vacina Aplicada! 🎉</h2>
                        <p id="celebration-message">Parabéns pela proteção do seu bebê! 💕</p>
                        <p class="celebration-vaccine" id="celebration-vaccine-name"></p>
                        <div class="celebration-extra-icons">
                            <span>💉</span>
                            <span>✨</span>
                            <span>🤱</span>
                        </div>
                        <button class="btn btn-primary" id="celebration-close">Fechar</button>
                        <div class="confetti-container" id="confetti-container"></div>
                    </div>
                </div>
            `;

            document.body.insertAdjacentHTML('beforeend', modalHTML);

            // Event listeners
            document.getElementById('celebration-close').addEventListener('click', () => {
                document.getElementById('celebration-modal').style.display = 'none';
                document.body.style.overflow = '';
            });

            document.querySelector('.celebration-modal-overlay').addEventListener('click', () => {
                document.getElementById('celebration-modal').style.display = 'none';
                document.body.style.overflow = '';
            });
        }

        /**
         * Anima confetes caindo
         */
        animateConfetti() {
            const container = document.getElementById('confetti-container');
            if (!container) return;

            container.innerHTML = '';
            // Reduzido para 20 partículas para melhor performance no mobile (era 50)
            const confettiCount = 20;
            
            for (let i = 0; i < confettiCount; i++) {
                const confetti = document.createElement('div');
                confetti.className = 'confetti';
                confetti.style.left = Math.random() * 100 + '%';
                confetti.style.animationDelay = Math.random() * 2 + 's';
                confetti.style.background = ['#ff8fa3', '#ffb3c6', '#ffe8f0', '#c4d5a0', '#e07a5f'][
                    Math.floor(Math.random() * 5)
                ];
                container.appendChild(confetti);
            }

            // Remove confetes após animação
            setTimeout(() => {
                container.innerHTML = '';
            }, 3000);
        }

        /**
         * Renderiza estado vazio
         */
        renderEmpty() {
            const container = document.getElementById('vaccination-timeline-container');
            if (container) {
                container.innerHTML = '<div class="vac-empty">Sem dados de vacinação.</div>';
            }
        }

        /**
         * Exibe mensagem de erro
         */
        showErrorMessage(message) {
            const container = document.getElementById('vaccination-timeline-container');
            if (container) {
                container.innerHTML = `
                    <div class="vaccination-error">
                        <p>⚠️ ${message}</p>
                    </div>
                `;
            }
        }

        /**
         * Inicializa componente
         */
        init() {
            const agendaCard = document.getElementById('agenda-de-vacinacao-card');
            const timelineContainer = document.getElementById('vaccination-timeline-container');
            if (!agendaCard && !timelineContainer) {
                this.log('Agenda ou timeline não encontrados - inicialização adiada');
                return;
            }

            if (!window.apiClient) {
                this.log('apiClient não disponível - inicialização adiada até autenticação');
                return;
            }

            this.loadVaccinationData();
        }
    }

    // Inicializa quando DOM estiver pronto
    window.__agendaTomorrowFromPNI = false;
    window.__agendaTomorrowFromReminders = false;
    window.applyAgendaCardTomorrowAlert = function() {
        const card = document.getElementById('agenda-de-vacinacao-card');
        if (!card) return;
        card.classList.toggle('card-alert-tomorrow', !!(window.__agendaTomorrowFromPNI || window.__agendaTomorrowFromReminders));
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            window.vaccinationTimeline = new VaccinationTimeline();
            window.vaccinationTimeline.init();
        });
    } else {
        window.vaccinationTimeline = new VaccinationTimeline();
        window.vaccinationTimeline.init();
    }

})();
