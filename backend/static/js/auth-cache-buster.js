// -*- coding: utf-8 -*-
// Purga e previne cache de endpoints sensíveis (mesmo com Service Worker antigo por perto).
(function () {
  'use strict';

  var SENSITIVE = [
    /^\/api\/(?:me|user-data|register|login|logout|verify|forgot-password|reset-password)(\/|$)/i
  ];

  function isSensitivePath(path) {
    try {
      return SENSITIVE.some(function (rx) { return rx.test(path); });
    } catch (_) {
      return false;
    }
  }

  async function purgeSensitiveFromCaches() {
    if (!('caches' in window)) return;
    try {
      var keys = await caches.keys();
      for (var i = 0; i < keys.length; i++) {
        var cache = await caches.open(keys[i]);
        var reqs = await cache.keys();
        for (var j = 0; j < reqs.length; j++) {
          try {
            var u = new URL(reqs[j].url);
            if (isSensitivePath(u.pathname)) await cache.delete(reqs[j]);
          } catch (_) {}
        }
      }
    } catch (_) {}
  }

  var _origFetch = window.fetch;
  try {
    window.fetch = function (input, init) {
      try {
        var url = (typeof input === 'string') ? new URL(input, location.origin) :
          (input && input.url) ? new URL(input.url) : null;
        if (url && isSensitivePath(url.pathname)) {
          init = init || {};
          init.cache = 'no-store';
          init.credentials = init.credentials || 'include';
          init.headers = Object.assign({}, init.headers || {}, { 'Cache-Control': 'no-store' });
        }
      } catch (_) {}
      return _origFetch.apply(this, arguments);
    };
  } catch (_) {}

  function notifySW() {
    try {
      if (navigator.serviceWorker && navigator.serviceWorker.controller) {
        navigator.serviceWorker.controller.postMessage({
          type: 'AUTH_CACHE_BYPASS',
          patterns: SENSITIVE.map(function (rx) { return rx.source; })
        });
      }
    } catch (_) {}
  }

  function ready(fn) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
    else fn();
  }
  ready(async function () {
    notifySW();
    await purgeSensitiveFromCaches();
  });
})();
