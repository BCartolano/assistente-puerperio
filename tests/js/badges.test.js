/**
 * @jest-environment node
 */
const { normalize, isSusBadge } = require('../../backend/static/js/badges.js');

describe('Badges (normalize + isSusBadge)', () => {
    test('normalize remove acentos e colapsa pontuação', () => {
        expect(normalize('Cartão')).toBe('cartao');
        expect(normalize('  Não   atende  ')).toBe('nao atende');
        expect(normalize('S.U.S')).toBe('sus');
    });

    test('isSusBadge reconhece variações e evita falsos positivos', () => {
        const positives = [
            'SUS',
            'S.U.S',
            'Aceita Cartão SUS',
            'aceita cartao sus',
            'Atende pelo SUS',
            'Não atende SUS',
            'nao atende o S.U.S.'
        ];
        const negatives = [
            'Sustentável',
            'suspeito',
            'suspiro',
            'Cartão de Saúde',
            'Cartao do idoso'
        ];
        positives.forEach((t) => expect(isSusBadge(t)).toBe(true));
        negatives.forEach((t) => expect(isSusBadge(t)).toBe(false));
    });

    test('isSusBadge retorna false para entrada vazia ou não-string', () => {
        expect(isSusBadge('')).toBe(false);
        expect(isSusBadge(null)).toBe(false);
        expect(isSusBadge(undefined)).toBe(false);
    });
});
