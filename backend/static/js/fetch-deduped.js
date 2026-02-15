/**
 * Deduplicação de fetch GET para /api/user e /api/educational.
 * Evita chamadas duplicadas em menos de 2 segundos (múltiplos scripts na mesma página).
 * Carregar antes de qualquer script que chame essas APIs.
 */
(function () {
  'use strict';
  var DEDUPE_MS = 2000;
  var cache = Object.create(null);

  /**
   * GET que retorna JSON; mesma URL dentro de DEDUPE_MS reutiliza a mesma Promise.
   * @param {string} url
   * @param {RequestInit} [opts]
   * @returns {Promise<object>}
   */
  function dedupedFetchJSON(url, opts) {
    opts = opts || {};
    var method = (opts.method || 'GET').toUpperCase();
    var key = method + ' ' + url;
    var now = Date.now();
    var ent = cache[key];
    if (ent && (now - ent.at) < DEDUPE_MS) {
      return ent.promise;
    }
    var promise = fetch(url, opts).then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.json();
    });
    cache[key] = { promise: promise, at: now };
    return promise;
  }

  if (typeof window !== 'undefined') {
    window.dedupedFetchJSON = dedupedFetchJSON;
  }
})();
