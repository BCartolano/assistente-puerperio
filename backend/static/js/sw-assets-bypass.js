/**
 * Network-first para assets versionados (JS/CSS com ?v=).
 * Evita que o SW sirva chat.js/CSS antigos quando a URL tem cache-bust.
 * Uso: importScripts('/static/js/sw-assets-bypass.js'); (no topo do sw.js)
 */
(function () {
  'use strict';

  function isVersionedAsset(url) {
    try {
      var pathname = url.pathname || '';
      var search = url.search || '';
      if (/\?v=/.test(search)) return true;
      if (/\.(js|css)(\?|$)/i.test(pathname + (url.search || ''))) return true;
      return false;
    } catch (_) {
      return false;
    }
  }

  self.addEventListener('fetch', function (event) {
    try {
      var req = event.request;
      if (req.method !== 'GET' && req.method !== 'HEAD') return;
      var url = new URL(req.url);
      if (url.origin !== self.location.origin) return;
      if (!isVersionedAsset(url)) return;

      event.respondWith(
        fetch(req, { cache: 'no-store' })
          .then(function (networkResp) {
            return networkResp;
          })
          .catch(function () {
            return caches.match(req);
          })
      );
    } catch (_) {}
  });
})();
