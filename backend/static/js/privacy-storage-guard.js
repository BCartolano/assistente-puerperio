// -*- coding: utf-8 -*-
// Remove chaves globais que podem vazar entre usuários e chama /api/me com no-store.
(function () {
  'use strict';

  function nukeGlobalKeys(userId) {
    var risky = [
      'user_name', 'baby_name', 'baby_profile', 'header_subtitle',
      'owner_name', 'currentBaby', 'selectedBaby', 'currentUserName'
    ];
    risky.forEach(function (k) {
      try {
        if (!k.startsWith('user:')) localStorage.removeItem(k);
      } catch (_) {}
    });
    try {
      localStorage.setItem('current_user_id', userId || '');
    } catch (_) {}
  }

  async function getMe() {
    try {
      var r = await fetch('/api/me', {
        method: 'GET',
        credentials: 'include',
        cache: 'no-store',
        headers: { Accept: 'application/json', 'Cache-Control': 'no-store' }
      });
      if (!r.ok) return null;
      return await r.json();
    } catch (_) {
      return null;
    }
  }

  function ready(fn) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
    else fn();
  }

  ready(async function () {
    var me = await getMe();
    var uid = (me && me.user) ? me.user.id : '';
    nukeGlobalKeys(uid);
  });
})();
