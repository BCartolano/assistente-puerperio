// -*- coding: utf-8 -*-
/**
 * Script de Geolocalização para Emergência Obstétrica
 * Alta precisão GPS, tratamento de erros e integração com backend
 */

(function() {
    'use strict';

    // Verifica se está em HTTPS (obrigatório para GPS)
    function verificarHTTPS() {
        if (location.protocol !== 'https:' && location.hostname !== 'localhost' && location.hostname !== '127.0.0.1') {
            const aviso = document.getElementById('aviso-https');
            if (aviso) {
                aviso.style.display = 'block';
            }
            return false;
        }
        return true;
    }

    /**
     * Localiza maternidade mais próxima usando GPS de alta precisão
     */
    function localizarMaternidade() {
        // Verifica HTTPS
        if (!verificarHTTPS()) {
            alert('⚠️ Este site precisa estar em HTTPS para acessar o GPS. Por favor, configure um certificado SSL.');
            return;
        }

        const statusEl = document.getElementById('status-gps');
        const btnLocalizar = document.getElementById('btn-localizar');
        
        // Desabilita botão durante busca
        if (btnLocalizar) {
            btnLocalizar.disabled = true;
            btnLocalizar.innerText = '🔍 Localizando...';
        }

        // Exibe status
        if (statusEl) {
            statusEl.innerText = "Buscando sua localização exata...";
            statusEl.className = 'loading';
        }

        // Configurações para máxima precisão (Essencial para emergência)
        const options = {
            enableHighAccuracy: true,  // Usa GPS real do celular (não apenas Wi-Fi)
            timeout: 10000,             // 10 segundos de limite
            maximumAge: 0              // Não usar localização em cache antiga
        };

        // Verifica suporte a geolocalização
        if (!navigator.geolocation) {
            const mensagem = "Seu navegador não suporta geolocalização. Digite o endereço manualmente.";
            alert(mensagem);
            if (statusEl) {
                statusEl.innerText = mensagem;
                statusEl.className = '';
            }
            if (btnLocalizar) {
                btnLocalizar.disabled = false;
                btnLocalizar.innerText = '🚨 ENCONTRAR MATERNIDADE AGORA';
            }
            return;
        }

        // Solicita localização
        navigator.geolocation.getCurrentPosition(
            async (position) => {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                const precisao = position.coords.accuracy; // Precisão em metros

                console.log(`[GPS] Localização obtida: ${lat}, ${lon} (precisão: ${precisao}m)`);

                if (statusEl) {
                    statusEl.innerText = "Localização encontrada! Buscando hospitais...";
                    statusEl.className = 'loading';
                }

                try {
                    // Envia para o servidor Python (Flask/FastAPI)
                    const url = `/api/hospitais-proximos?lat=${lat}&lon=${lon}&limit=5&ordenar_por_tempo=true&apenas_com_telefone=true`;
                    console.log(`[API] Buscando hospitais: ${url}`);
                    
                    const response = await fetch(url);
                    
                    if (!response.ok) {
                        throw new Error(`Erro HTTP: ${response.status}`);
                    }
                    
                    const data = await response.json();
                    const hospitais = data.items || [];

                    console.log(`[API] ${hospitais.length} hospitais encontrados`);

                    // Renderiza cards
                    renderizarCards(hospitais);
                    
                    if (statusEl) {
                        statusEl.innerText = hospitais.length > 0 
                            ? `✅ ${hospitais.length} maternidade(s) encontrada(s)` 
                            : "Nenhuma maternidade encontrada neste raio.";
                        statusEl.className = '';
                    }
                } catch (error) {
                    console.error("[ERRO] Erro ao buscar dados:", error);
                    if (statusEl) {
                        statusEl.innerText = "❌ Erro ao conectar com o servidor. Tente novamente.";
                        statusEl.className = '';
                    }
                    alert("Erro ao buscar hospitais. Verifique sua conexão e tente novamente.");
                } finally {
                    if (btnLocalizar) {
                        btnLocalizar.disabled = false;
                        btnLocalizar.innerText = '🚨 ENCONTRAR MATERNIDADE AGORA';
                    }
                }
            },
            (error) => {
                // Trata erros comuns de GPS
                let mensagem = '';
                
                switch(error.code) {
                    case error.PERMISSION_DENIED:
                        mensagem = "Você precisa permitir o acesso ao GPS para encontrar a maternidade mais próxima.\n\nPor favor, verifique as configurações de privacidade do seu navegador.";
                        break;
                    case error.POSITION_UNAVAILABLE:
                        mensagem = "Sinal de GPS indisponível.\n\nTente:\n• Ir para um local aberto\n• Verificar se o GPS está ligado\n• Aguardar alguns segundos";
                        break;
                    case error.TIMEOUT:
                        mensagem = "Tempo esgotado ao buscar GPS.\n\nO sinal pode estar fraco. Tente novamente em um local aberto.";
                        break;
                    default:
                        mensagem = "Erro ao obter localização. Tente novamente.";
                }
                
                console.error("[GPS] Erro:", error.code, mensagem);
                alert(mensagem);
                
                if (statusEl) {
                    statusEl.innerText = "❌ Erro ao localizar.";
                    statusEl.className = '';
                }
                
                if (btnLocalizar) {
                    btnLocalizar.disabled = false;
                    btnLocalizar.innerText = '🚨 ENCONTRAR MATERNIDADE AGORA';
                }
                
                // Foca no campo CEP do plano B para facilitar busca manual
                const cepInput = document.getElementById('cep-manual');
                if (cepInput) {
                    setTimeout(() => {
                        cepInput.focus();
                        cepInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }, 500);
                }
            },
            options
        );
    }

    /**
     * Renderiza cards de hospitais no container
     * @param {Array} lista - Lista de hospitais
     */
    function renderizarCards(lista) {
        const container = document.getElementById('container-hospitais');
        
        if (!container) {
            console.error('[ERRO] Container não encontrado');
            return;
        }

        // Limpa busca anterior
        container.innerHTML = '';

        if (!lista || lista.length === 0) {
            container.innerHTML = `
                <div class="sem-resultados">
                    <h3>Nenhuma maternidade encontrada</h3>
                    <p>Tente aumentar o raio de busca ou verifique sua localização.</p>
                    <p>Em caso de emergência grave, ligue <strong>192 (SAMU)</strong></p>
                </div>
            `;
            return;
        }

        // Usa função do hospital-cards-emergency.js se disponível
        if (window.HospitalCardsEmergency && window.HospitalCardsEmergency.renderizar) {
            window.HospitalCardsEmergency.renderizar(lista, container);
        } else {
            // Fallback: renderiza manualmente
            lista.forEach(hosp => {
                const tipoClass = (hosp.tipo || hosp.natureza || '').toLowerCase().includes('público') || 
                                 (hosp.tipo || hosp.natureza || '').toLowerCase().includes('sus')
                    ? 'publico' 
                    : 'privado';
                
                const card = `
                    <div class="card-emergencia" data-cnes="${hosp.cnes || ''}">
                        <div class="header-card">
                            <span class="badge-tipo ${tipoClass}">${hosp.tipo || hosp.natureza || 'Indefinido'}</span>
                            <span class="tempo-estimado">⏱ ${hosp.tempo_estimado || hosp.estimativa || hosp.distancia || 'N/A'}</span>
                        </div>
                        <h2 class="hospital-nome">${hosp.nome || hosp.nome_fantasia || 'Hospital'}</h2>
                        <p class="hospital-endereco">📍 ${hosp.endereco_exato || 'Endereço não disponível'}</p>
                        ${hosp.metodos_pagamento ? `
                            <div class="info-pagamento">
                                <span class="tag-pagamento">💳 ${hosp.metodos_pagamento}</span>
                            </div>
                        ` : ''}
                        <div class="acoes-container">
                            ${hosp.link_ligar ? `
                                <a href="${hosp.link_ligar}" class="btn-ligar">
                                    <span class="phone-icon">📞</span>
                                    <span>LIGAR AGORA</span>
                                </a>
                            ` : `
                                <button class="btn-ligar disabled" disabled>
                                    <span>📞</span>
                                    <span>Telefone Indisponível</span>
                                </button>
                            `}
                            ${hosp.link_gps ? `
                                <div class="rotas-grid">
                                    <a href="${hosp.link_gps}" target="_blank" rel="noopener noreferrer" class="btn-rota google">
                                        Google Maps
                                    </a>
                                    ${hosp.link_waze ? `
                                        <a href="${hosp.link_waze}" target="_blank" rel="noopener noreferrer" class="btn-rota waze">
                                            Waze
                                        </a>
                                    ` : ''}
                                </div>
                            ` : ''}
                        </div>
                    </div>
                `;
                container.innerHTML += card;
            });
        }
    }

    /**
     * Formata CEP enquanto o usuário digita
     * @param {HTMLInputElement} input - Campo de input
     */
    function formatarCEP(input) {
        let valor = input.value.replace(/\D/g, ''); // Remove não numéricos
        
        if (valor.length > 5) {
            valor = valor.substring(0, 5) + '-' + valor.substring(5, 8);
        }
        
        input.value = valor;
    }

    /**
     * Busca maternidades por CEP (Plano B quando GPS falha)
     */
    async function buscarPorCEP() {
        const cepInput = document.getElementById('cep-manual');
        const btnBuscar = document.getElementById('btn-buscar-cep');
        const hintEl = document.getElementById('hint-cep');
        const statusEl = document.getElementById('status-gps');
        const container = document.getElementById('container-hospitais');
        
        if (!cepInput || !btnBuscar) {
            console.error('[ERRO] Elementos do plano B não encontrados');
            return;
        }
        
        const cep = cepInput.value.replace(/\D/g, ''); // Remove formatação
        
        // Valida CEP
        if (cep.length !== 8) {
            if (hintEl) {
                hintEl.innerText = '❌ CEP deve ter 8 dígitos';
                hintEl.className = 'plano-b-hint erro';
            }
            cepInput.focus();
            return;
        }
        
        // Desabilita botão durante busca
        btnBuscar.disabled = true;
        btnBuscar.innerText = 'Buscando...';
        
        if (hintEl) {
            hintEl.innerText = '🔍 Buscando coordenadas do CEP...';
            hintEl.className = 'plano-b-hint';
        }
        
        if (statusEl) {
            statusEl.innerText = 'Buscando localização pelo CEP...';
            statusEl.className = 'loading';
        }
        
        try {
            // Geocodifica CEP usando API gratuita (ViaCEP)
            const viaCepUrl = `https://viacep.com.br/ws/${cep}/json/`;
            console.log(`[CEP] Consultando ViaCEP: ${viaCepUrl}`);
            
            const cepResponse = await fetch(viaCepUrl);
            
            if (!cepResponse.ok) {
                throw new Error(`Erro HTTP: ${cepResponse.status}`);
            }
            
            const cepData = await cepResponse.json();
            
            if (cepData.erro) {
                throw new Error('CEP não encontrado');
            }
            
            console.log(`[CEP] Dados recebidos:`, cepData);
            
            // Monta endereço completo para geocodificação
            const endereco = `${cepData.logradouro || ''}, ${cepData.bairro || ''}, ${cepData.localidade || ''}, ${cepData.uf || ''}`.trim();
            
            if (hintEl) {
                hintEl.innerText = `📍 ${endereco}`;
                hintEl.className = 'plano-b-hint sucesso';
            }
            
            // Geocodifica endereço usando Nominatim (OpenStreetMap - gratuito)
            const nominatimUrl = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(endereco)}&limit=1&countrycodes=br`;
            console.log(`[GEO] Consultando Nominatim: ${nominatimUrl}`);
            
            const geoResponse = await fetch(nominatimUrl, {
                headers: {
                    'User-Agent': 'Sophia-Emergencia-Obstetrica/1.0'
                }
            });
            
            if (!geoResponse.ok) {
                throw new Error(`Erro HTTP: ${geoResponse.status}`);
            }
            
            const geoData = await geoResponse.json();
            
            if (!geoData || geoData.length === 0) {
                throw new Error('Endereço não encontrado no mapa');
            }
            
            const lat = parseFloat(geoData[0].lat);
            const lon = parseFloat(geoData[0].lon);
            
            console.log(`[GEO] Coordenadas obtidas: ${lat}, ${lon}`);
            
            if (statusEl) {
                statusEl.innerText = 'Localização encontrada! Buscando hospitais...';
                statusEl.className = 'loading';
            }
            
            // Busca hospitais usando coordenadas
            const url = `/api/hospitais-proximos?lat=${lat}&lon=${lon}&limit=5&ordenar_por_tempo=true&apenas_com_telefone=true`;
            console.log(`[API] Buscando hospitais: ${url}`);
            
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`Erro HTTP: ${response.status}`);
            }
            
            const data = await response.json();
            const hospitais = data.items || [];
            
            console.log(`[API] ${hospitais.length} hospitais encontrados`);
            
            // Renderiza cards
            renderizarCards(hospitais);
            
            if (statusEl) {
                statusEl.innerText = hospitais.length > 0 
                    ? `✅ ${hospitais.length} maternidade(s) encontrada(s) próximo ao CEP ${cep}` 
                    : "Nenhuma maternidade encontrada próximo a este CEP.";
                statusEl.className = '';
            }
            
        } catch (error) {
            console.error("[ERRO] Erro ao buscar por CEP:", error);
            
            let mensagem = 'Erro ao buscar por CEP. Verifique se o CEP está correto.';
            
            if (error.message.includes('CEP não encontrado')) {
                mensagem = 'CEP não encontrado. Verifique se está correto.';
            } else if (error.message.includes('Endereço não encontrado')) {
                mensagem = 'Não foi possível encontrar as coordenadas deste endereço.';
            } else if (error.message.includes('conectar')) {
                mensagem = 'Erro ao conectar com o servidor. Verifique sua conexão.';
            }
            
            if (hintEl) {
                hintEl.innerText = `❌ ${mensagem}`;
                hintEl.className = 'plano-b-hint erro';
            }
            
            if (statusEl) {
                statusEl.innerText = '❌ Erro ao buscar por CEP.';
                statusEl.className = '';
            }
            
            alert(mensagem);
        } finally {
            if (btnBuscar) {
                btnBuscar.disabled = false;
                btnBuscar.innerText = 'Buscar';
            }
        }
    }

    // Expõe funções globalmente
    window.localizarMaternidade = localizarMaternidade;
    window.buscarPorCEP = buscarPorCEP;
    window.formatarCEP = formatarCEP;

    // Verifica HTTPS ao carregar
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', verificarHTTPS);
    } else {
        verificarHTTPS();
    }

})();
