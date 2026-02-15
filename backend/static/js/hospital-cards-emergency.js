// -*- coding: utf-8 -*-
/**
 * Componente de Cards de Hospitais para Emergência Obstétrica
 * Otimizado para situações de emergência com botão de pânico destacado
 */

(function() {
    'use strict';

    /**
     * Cria card de hospital otimizado para emergência
     * Design de alto contraste e ações rápidas (thumb-friendly)
     * @param {Object} hospital - Dados do hospital
     * @returns {string} HTML do card
     */
    function criarCardHospital(hospital) {
        const temTelefone = hospital.telefone_limpo && hospital.telefone_limpo !== '';
        const temGPS = hospital.link_gps && hospital.link_gps !== '';
        
        // Determina tipo e classe CSS
        const tipoTexto = hospital.natureza || hospital.tipo || 'Indefinido';
        const tipoClass = tipoTexto.toLowerCase().includes('público') || tipoTexto.toLowerCase().includes('sus')
            ? 'publico'
            : tipoTexto.toLowerCase().includes('privado') || tipoTexto.toLowerCase().includes('convênio')
            ? 'privado'
            : '';
        
        // Badge de natureza
        const badgeNatureza = tipoClass 
            ? `<span class="badge-tipo ${tipoClass}">${tipoTexto}</span>`
            : '';
        
        // Tempo estimado
        const tempoEstimado = hospital.tempo_estimado || hospital.estimativa || hospital.distancia || 'N/A';
        
        // Info de pagamento
        const pagamentos = hospital.metodos_pagamento || hospital.sus || 'Informação não disponível';
        
        return `
            <div class="card-emergencia" data-cnes="${hospital.cnes}">
                <div class="header-card">
                    ${badgeNatureza}
                    <span class="tempo-estimado">⏱ ${tempoEstimado}</span>
                </div>
                
                <h2 class="hospital-nome">${hospital.nome || hospital.nome_fantasia || 'Hospital'}</h2>
                <p class="hospital-endereco">📍 ${hospital.endereco_exato || 'Endereço não disponível'}</p>
                
                <div class="info-pagamento">
                    <span class="tag-pagamento">💳 ${pagamentos}</span>
                </div>

                <div class="acoes-container">
                    ${temTelefone ? `
                        <a href="${hospital.link_ligar}" 
                           class="btn-ligar"
                           aria-label="Ligar para ${hospital.nome || hospital.nome_fantasia}">
                            <span class="phone-icon">📞</span>
                            <span>LIGAR AGORA</span>
                        </a>
                    ` : `
                        <button class="btn-ligar disabled" disabled>
                            <span>📞</span>
                            <span>Telefone Indisponível</span>
                        </button>
                    `}
                    
                    ${temGPS ? `
                        <div class="rotas-grid">
                            <a href="${hospital.link_gps}" 
                               target="_blank"
                               rel="noopener noreferrer"
                               class="btn-rota google"
                               aria-label="Ver rota no Google Maps">
                                Google Maps
                            </a>
                            ${hospital.link_waze ? `
                                <a href="${hospital.link_waze}" 
                                   target="_blank"
                                   rel="noopener noreferrer"
                                   class="btn-rota waze"
                                   aria-label="Ver rota no Waze">
                                    Waze
                                </a>
                            ` : ''}
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    /**
     * Renderiza lista de hospitais em container
     * @param {Array} hospitais - Lista de hospitais
     * @param {HTMLElement} container - Container onde renderizar
     */
    function renderizarHospitais(hospitais, container) {
        if (!container) {
            console.error('❌ Container não encontrado');
            return;
        }

        if (!hospitais || hospitais.length === 0) {
            container.innerHTML = `
                <div class="hospital-empty">
                    <i class="fas fa-hospital"></i>
                    <p>Nenhum hospital encontrado neste raio.</p>
                    <p class="hospital-empty-hint">Tente aumentar o raio de busca ou verifique sua localização.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = hospitais.map(criarCardHospital).join('');
        
        // Adiciona event listeners para analytics/tracking se necessário
        container.querySelectorAll('.btn-emergency-ligar').forEach(btn => {
            btn.addEventListener('click', function() {
                const card = this.closest('.hospital-card-emergency');
                const cnes = card ? card.dataset.cnes : '';
                console.log('[EMERGENCY] Ligação iniciada para CNES:', cnes);
                // Aqui você pode adicionar tracking/analytics
            });
        });
    }

    // Expõe funções globalmente
    window.HospitalCardsEmergency = {
        criarCard: criarCardHospital,
        renderizar: renderizarHospitais
    };

})();
