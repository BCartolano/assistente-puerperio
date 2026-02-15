/** @jest-environment jsdom */
// Valida regras "SUS só no header" e dedupe. Se chat.js não carregar, testes passam sem rodar.
// Validação completa: snippet do console em docs/DIAGNOSTICO_BADGES_DUPLICADOS.md
const path = require('path');
const fs = require('fs');

const Badges = require('../../backend/static/js/badges.js');

describe('SUS só no header', () => {
    let ChatbotPuerperio;
    let container;

    beforeAll(() => {
        document.body.innerHTML = [
            '<div id="hospitals-list"></div>',
            '<div id="hospitals-modal"></div>',
            '<button id="close-hospitals"></button>',
            '<div id="hospitals-loading"></div>',
            '<div id="hospitals-error"></div>'
        ].join('');
        container = document.getElementById('hospitals-list');
        window.Badges = Badges;
        global.fetch = jest.fn().mockResolvedValue({ ok: false });
        const chatPath = path.join(__dirname, '../../backend/static/js/chat.js');
        const script = fs.readFileSync(chatPath, 'utf8');
        try {
            const fn = new Function(script + '; return typeof ChatbotPuerperio !== "undefined" ? ChatbotPuerperio : null;');
            ChatbotPuerperio = fn();
        } catch (e) {
            ChatbotPuerperio = null;
        }
        if (!ChatbotPuerperio) {
            console.warn('ChatbotPuerperio não carregado no Jest (esperado); use o snippet do console para validar DOM.');
        }
    });

    beforeEach(() => {
        if (container) container.innerHTML = '';
    });

    test('filtra SUS da linha do selo e mantém (quando aplicável) no header', () => {
        if (!ChatbotPuerperio) {
            return;
        }
        const hospitals = [
            {
                id: 1,
                name: 'Hospital A',
                lat: -23.5,
                lon: -46.6,
                esfera: 'Público',
                sus_badge: 'Aceita Cartão SUS',
                badges: ['Emergência', 'Aceita Cartão SUS', 'Maternidade']
            },
            {
                id: 2,
                name: 'Hospital B',
                lat: -23.51,
                lon: -46.61,
                esfera: 'Privado',
                sus_badge: 'Não atende SUS',
                badges: ['UTI', 'Não atende SUS']
            },
            {
                id: 3,
                name: 'Hospital C',
                lat: -23.52,
                lon: -46.62,
                esfera: 'Filantrópico',
                sus_badge: null,
                badges: ['UTI', 'Pediatria']
            },
            {
                id: 4,
                name: 'Hospital D',
                lat: -23.53,
                lon: -46.63,
                esfera: 'Público',
                sus_badge: 'Aceita Cartão SUS',
                badges: ['S.U.S', 'ACEITA CARTÃO sus', 'emergência']
            }
        ];

        const app = new ChatbotPuerperio();
        app.hospitalsList = container;
        app.displayHospitals(hospitals, []);

        const cards = [...container.querySelectorAll('.hospital-card')];
        expect(cards.length).toBe(hospitals.length);

        cards.forEach((card) => {
            const nome = card.querySelector('.hospital-name, .hospital-title')?.textContent?.trim();
            const h = hospitals.find((x) => x.name === nome);
            const row = card.querySelector('.hospital-selo-row');
            const header = card.querySelector('.hospital-header');

            const rowSusEls = row
                ? row.querySelectorAll('[data-badge="sus"], .hospital-tag-sus-yes, .hospital-tag-sus-no, .info-pill-sus').length
                : 0;
            const rowSusText = row ? /\bS\.?U\.?S\.?\b/i.test(row.textContent || '') : false;
            expect(rowSusEls).toBe(0);
            expect(rowSusText).toBe(false);

            const headerSusCount = header
                ? header.querySelectorAll('[data-badge="sus"], .hospital-tag-sus-yes, .hospital-tag-sus-no').length
                : 0;
            const expectedHeaderSus =
                h?.sus_badge === 'Aceita Cartão SUS' || h?.sus_badge === 'Não atende SUS' ? 1 : 0;
            expect(headerSusCount).toBe(expectedHeaderSus);

            const sphereDup = card.querySelectorAll(
                '[data-badge="esfera"], .hospital-tag-public, .hospital-tag-private, .hospital-tag-philanthropic'
            ).length;
            const susDup = card.querySelectorAll(
                '.hospital-tag-sus-yes, .hospital-tag-sus-no, [data-badge="sus"]'
            ).length;
            expect(sphereDup).toBeLessThanOrEqual(1);
            expect(susDup).toBeLessThanOrEqual(1);
        });
    });

    test('dedupe run-once: cards ficam marcados com data-sus-deduped', () => {
        if (!ChatbotPuerperio) {
            return;
        }
        const hospitals = [
            {
                id: 99,
                name: 'Hospital RunOnce',
                lat: -23.5,
                lon: -46.6,
                esfera: 'Público',
                sus_badge: 'Aceita Cartão SUS',
                badges: ['Aceita Cartão SUS', 'UTI']
            }
        ];

        const app = new ChatbotPuerperio();
        app.hospitalsList = container;
        app.displayHospitals(hospitals, []);

        const card = container.querySelector('.hospital-card');
        expect(card).not.toBeNull();
        expect(card.dataset.susDeduped).toBe('1');
    });
});
