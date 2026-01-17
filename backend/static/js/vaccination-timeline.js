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
            this.isLoading = true;

            try {
                const response = await window.apiClient.get('/api/vaccination/status');
                
                if (response.error) {
                    this.log('Erro ao carregar dados:', response.error);
                    this.showErrorMessage(response.message || 'Erro ao carregar calendário de vacinação');
                    return;
                }

                this.babyData = response.baby;
                this.vaccinationData = response;
                
                this.renderTimeline();
                this.updateNextVaccineWidget();
                this.log('Dados de vacinação carregados:', response);
                
            } catch (error) {
                this.log('Erro na requisição:', error);
                this.showErrorMessage('Erro ao carregar calendário de vacinação. Tente novamente.');
            } finally {
                this.isLoading = false;
            }
        }

        /**
         * Renderiza a timeline de vacinação
         */
        renderTimeline() {
            const container = document.getElementById('vaccination-timeline-container');
            if (!container || !this.vaccinationData) return;

            const { baby, vaccination_schedule, statistics } = this.vaccinationData;

            // Cria estrutura HTML
            let html = `
                <div class="vaccination-timeline">
                    <div class="vaccination-header">
                        <h2>💉 Jornada de Proteção - ${baby.name}</h2>
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
                const isNext = nextVaccine && nextVaccine.id === vaccine.id;
                html += this.renderVaccineCard(vaccine, isNext);
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
            const status = vaccine.status;
            const today = new Date();
            let recommendedDate = null;
            let daysUntil = null;

            if (vaccine.recommended_date) {
                recommendedDate = new Date(vaccine.recommended_date);
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
                <div class="${cardClasses}" data-vaccine-id="${vaccine.id}">
                    <div class="vaccine-card-header">
                        <div class="vaccine-icon">
                            ${status === 'completed' ? '✓' : isNext ? '⭐' : isOverdue ? '⚠️' : '⏳'}
                        </div>
                        <div class="vaccine-info">
                            <h4>${vaccine.vaccine_name}</h4>
                            ${vaccine.dose_number > 0 ? `<span class="dose-badge">${vaccine.dose_number}ª dose</span>` : ''}
                        </div>
                    </div>
            `;

            if (status === 'completed' && vaccine.administered_date) {
                html += `
                    <div class="vaccine-card-body">
                        <p class="vaccine-status-completed">✓ Aplicada em ${this.formatDate(new Date(vaccine.administered_date))}</p>
                        ${vaccine.administered_location ? `<p class="vaccine-location">📍 ${vaccine.administered_location}</p>` : ''}
                    </div>
                `;
            } else {
                html += `
                    <div class="vaccine-card-body">
                        <p class="vaccine-recommended-date">📅 Recomendada: ${recommendedDate ? this.formatDate(recommendedDate) : 'Em breve'}</p>
                        ${daysUntil !== null ? `<p class="vaccine-days-until">${daysUntil > 0 ? `⏰ Faltam ${daysUntil} dias` : daysUntil === 0 ? '⏰ Hoje!' : '⚠️ Atrasada, mas ainda pode ser aplicada'}</p>` : ''}
                        ${isNext ? `<button class="btn btn-mark-vaccine" data-schedule-id="${vaccine.id}">Marcar como Aplicada 💉</button>` : ''}
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
            const today = new Date();
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
         * Atualiza widget "Próxima Vacina" na sidebar esquerda
         */
        updateNextVaccineWidget() {
            const widget = document.getElementById('next-vaccine-widget');
            if (!widget || !this.vaccinationData) return;

            const nextVaccine = this.findNextVaccine(this.vaccinationData.vaccination_schedule);
            
            if (!nextVaccine) {
                widget.innerHTML = `
                    <div class="sidebar-card next-vaccine-widget">
                        <div class="card-icon">✅</div>
                        <h3>Próxima Vacina</h3>
                        <p>Todas as vacinas do primeiro ano foram aplicadas! 🎉</p>
                    </div>
                `;
                return;
            }

            const today = new Date();
            const recommendedDate = new Date(nextVaccine.recommended_date);
            const daysUntil = Math.ceil((recommendedDate - today) / (1000 * 60 * 60 * 24));

            widget.innerHTML = `
                <div class="sidebar-card next-vaccine-widget">
                    <div class="card-icon">🔜</div>
                    <h3>Próxima Vacina</h3>
                    <div class="next-vaccine-summary">
                        <p class="next-vaccine-name">${nextVaccine.vaccine_name}</p>
                        <p class="next-vaccine-countdown">
                            ${daysUntil > 0 ? `<strong>${daysUntil}</strong> ${daysUntil === 1 ? 'dia' : 'dias'}` : daysUntil === 0 ? '<strong>Hoje!</strong>' : '<strong>Atrasada</strong>'}
                        </p>
                        <p class="next-vaccine-date">${this.formatDate(recommendedDate)}</p>
                    </div>
                </div>
            `;
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
                    // Exibe modal de comemoração
                    if (vaccine) {
                        this.showCelebrationModal(vaccine);
                    }
                    // Recarrega dados
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
         * Exibe modal de comemoração
         */
        showCelebrationModal(vaccine) {
            const modal = document.getElementById('celebration-modal');
            if (!modal) {
                // Cria modal se não existir
                this.createCelebrationModal();
            }

            const modalElement = document.getElementById('celebration-modal');
            const babyName = this.babyData ? this.babyData.name : 'seu bebê';
            const vaccineName = vaccine ? vaccine.vaccine_name : 'vacina';

            document.getElementById('celebration-message').textContent = 
                `Parabéns pela proteção do ${babyName}! 💕`;
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
            // Verifica se o container existe
            const container = document.getElementById('vaccination-timeline-container');
            if (!container) {
                this.log('Container vaccination-timeline-container não encontrado');
                return;
            }

            // Carrega dados automaticamente
            this.loadVaccinationData();
        }
    }

    // Inicializa quando DOM estiver pronto
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
