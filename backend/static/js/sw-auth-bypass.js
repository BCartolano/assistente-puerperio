// -*- coding: utf-8 -*-
// Bypass de cache dentro do Service Worker para rotas sensíveis de autenticação/identidade.
// Modo de uso: no seu SW, adicione: importScripts('/static/js/sw-auth-bypass.js');
// Este arquivo:
// - intercepta fetch GET/HEAD para /api/me, /api/user-data, /api/register, /api/login, /api/logout, /api/verify,
//   /api/forgot-password e /api/reset-password e responde sempre via rede (no-store);
// - escuta mensagens do cliente com AUTH_CACHE_BYPASS para atualizar padrões se necessário.
(function () {
  'use strict';
  var AUTH_BYPASS = [
    /^\/api\/(?:me|user-data|register|login|logout|verify|forgot-password|reset-password)(\/|$)/i
  ];

  function isSensitive(pathname) {
    try {
      return AUTH_BYPASS.some(function (rx) { return rx.test(pathname); });
    } catch (_) {
      return false;
    }
  }

  self.addEventListener('message', function (ev) {
    try {
      var data = ev.data || {};
      if (data.type === 'AUTH_CACHE_BYPASS' && Array.isArray(data.patterns)) {
        AUTH_BYPASS = data.patterns.map(function (src) {
          try {
            return new RegExp(src, 'i');
          } catch (_) {
            return null;
          }
        }).filter(Boolean);
      }
    } catch (_) {}
  });

  self.addEventListener('fetch', function (event) {
    try {
      var req = event.request;
      if (req.method !== 'GET' && req.method !== 'HEAD') return;
      var url = new URL(req.url);
      if (!isSensitive(url.pathname)) return;
      event.respondWith(fetch(req, { cache: 'no-store', credentials: 'include' }));
    } catch (_) {}
  });
})();
