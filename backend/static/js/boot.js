/**
 * Boot: na página de login o template já carrega chat.js (único handler do form).
 * Não carregamos auth/login.js aqui para evitar duplo POST em /api/login.
 * App: registra SW apenas fora do login.
 */
(function () {
    'use strict';
    var page = (document.documentElement.getAttribute('data-page') || 'app').toLowerCase();
    var isLogin = page === 'login';

    if (isLogin) {
        return;
    }

    // App: registra SW apenas fora do login (não intercepta /login nem /auth)
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js').catch(function (e) {
            console.warn('[boot] SW não registrado', e);
        });
    }
})();
