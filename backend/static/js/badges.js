/**
 * Helper SUS: normalização e detecção de badge SUS.
 * Usado no parse de badges (excluir do array) e no dedupe (text nodes).
 * UMD: exporta para Node (Jest); em browser expõe window.Badges.
 */
(function (root, factory) {
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = factory();
    } else if (typeof root !== 'undefined') {
        root.Badges = factory();
    }
}(typeof window !== 'undefined' ? window : this, function () {
    'use strict';

    // Remove acentos (Node 16+). Fallback: /[\u0300-\u036f]/g se \p{Diacritic} não suportado
    function normalize(s) {
        if (s == null) return '';
        var str = String(s);
        // Colapsa S.U.S -> SUS (pontos entre letras) para reconhecer "S.U.S"
        try {
            str = str.replace(/(\p{L})\.(?=\p{L})/gu, '$1');
        } catch (e) {
            str = str.replace(/([a-zA-Z])\.(?=[a-zA-Z])/g, '$1');
        }
        try {
            str = str.normalize('NFD').replace(/\p{Diacritic}/gu, '');
        } catch (e) {
            str = str.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
        }
        str = str.replace(/[^\p{L}\p{N}]+/gu, ' ').trim().toLowerCase();
        return str;
    }

    var SUS_CANONICAL = [
        'sus',
        'aceita cartao sus',
        'atende sus',
        'atende pelo sus',
        'nao atende sus',
        'nao atende o sus'
    ];

    function isSusBadge(text) {
        var n = normalize(text);
        // Exige "sus" como token isolado para evitar "suspeito"/"sustentável"
        if (!/\bsus\b/.test(n)) return false;
        return SUS_CANONICAL.some(function (p) { return n.indexOf(p) !== -1; });
    }

    return {
        normalize: normalize,
        isSusBadge: isSusBadge
    };
}));
