/**
 * Dispatcher único: botões com data-action="foo" disparam actions[foo].
 * Botão sem action registrada gera warning (evita "botão morto").
 * Dev-only: localStorage DEV_WARN_BUTTONS=1 lista possíveis botões mortos.
 */
(function () {
    'use strict';
    window.actions = window.actions || {};

    document.addEventListener('click', function (e) {
        var el = e.target.closest('[data-action]');
        if (!el) return;
        var fn = window.actions[el.dataset.action];
        if (!fn) {
            console.warn('[Ação desconhecida]', el.dataset.action, el);
            return;
        }
        fn(el, e);
    });

    if (typeof localStorage !== 'undefined' && localStorage.getItem('DEV_WARN_BUTTONS') === '1') {
        setTimeout(function () {
            document.querySelectorAll('button, [role="button"]').forEach(function (btn) {
                var hasAction = btn.matches('[data-action]') || btn.onclick || btn.getAttribute('href');
                if (!hasAction) console.warn('[Possível botão morto]', btn);
            });
        }, 1000);
    }
})();
