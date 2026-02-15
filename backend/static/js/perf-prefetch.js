// -*- coding: utf-8 -*-
// Perf: preconnect/dns-prefetch e prefetch leve de /api/educational.
// Observação: preconnect para Groq só ajuda se o front falar direto com Groq (no seu caso é server->server, então o efeito é mínimo).
(function () {
  'use strict';

  function addLink(rel, href, attrs) {
    try {
      var l = document.createElement('link');
      l.rel = rel;
      l.href = href;
      if (attrs) {
        for (var k in attrs) {
          try { l.setAttribute(k, attrs[k]); } catch (_) {}
        }
      }
      document.head.appendChild(l);
    } catch (_) {}
  }

  function preconnect() {
    try {
      var origin = location.origin;
      addLink('preconnect', origin);
      addLink('dns-prefetch', '//' + location.host);
    } catch (_) {}
    addLink('dns-prefetch', '//api.groq.com');
    addLink('preconnect', 'https://api.groq.com', { crossorigin: 'anonymous' });
    try {
      var meta = document.querySelector('meta[name="api-base"]');
      if (meta && meta.content) {
        addLink('dns-prefetch', meta.content.replace(/^https?:\/\//, '//'));
        addLink('preconnect', meta.content, { crossorigin: 'anonymous' });
      }
    } catch (_) {}
  }

  function prefetchAPIs() {
    function go() {
      try {
        var f = (window.dedupedFetchJSON && window.dedupedFetchJSON('/api/educational', {
          credentials: 'same-origin',
          headers: { Accept: 'application/json' }
        })) || fetch('/api/educational', {
          method: 'GET',
          headers: { Accept: 'application/json' },
          cache: 'default',
          credentials: 'same-origin',
          keepalive: true
        });
        if (f && typeof f.catch === 'function') f.catch(function () {});
      } catch (_) {}
    }
    if ('requestIdleCallback' in window) {
      try { requestIdleCallback(go, { timeout: 2000 }); } catch (_) { setTimeout(go, 1200); }
    } else {
      setTimeout(go, 1200);
    }
  }

  (function init() {
    preconnect();
    prefetchAPIs();
  })();
})();
