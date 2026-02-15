/**
 * Namespacing automático de localStorage por usuário (seguro contra vazamentos de sessão).
 */
(function () {
  'use strict';
  try {
    if (localStorage.getItem('nsStorage:disable') === '1' || window.NS_STORAGE_DISABLE === true) return;
  } catch (_) {}

  var GLOBAL_WHITELIST = new Set([
    'current_user_id', 'skeletonOff', 'theme', 'lang', 'app_version',
    'CACHE_VERSION', 'last_sw_update', 'ns:migrated'
  ]);
  var GLOBAL_PREFIX = [/^app:/i, /^sw:/i, /^cache:/i];
  var LEGACY_RISKY = [
    'user_name', 'baby_name', 'baby_profile', 'header_subtitle',
    'owner_name', 'currentBaby', 'selectedBaby', 'currentUserName'
  ];
  var SENSITIVE_STRICT = new Set(['user_name', 'baby_name', 'header_subtitle']);

  function isGlobalKey(k) {
    try {
      if (!k || typeof k !== 'string') return true;
      if (GLOBAL_WHITELIST.has(k)) return true;
      for (var i = 0; i < GLOBAL_PREFIX.length; i++) {
        if (GLOBAL_PREFIX[i].test(k)) return true;
      }
      if (/^user:[^:]+:/.test(k)) return true;
      return false;
    } catch (_) {
      return true;
    }
  }

  function getUid() {
    try {
      return localStorage.getItem('current_user_id') || '';
    } catch (_) {
      return '';
    }
  }

  function nsKey(k, uid) {
    if (!k || isGlobalKey(k)) return k;
    uid = uid || getUid() || 'anon';
    return 'user:' + uid + ':' + k;
  }

  function migrateLegacy(uid) {
    try {
      if (localStorage.getItem('ns:migrated') === '1') return;
      uid = uid || getUid();
      if (!uid) return;
      for (var i = 0; i < LEGACY_RISKY.length; i++) {
        var k = LEGACY_RISKY[i];
        try {
          var v = _get(k);
          if (v !== null && !isGlobalKey(k)) {
            _set(nsKey(k, uid), v);
            _rem(k);
          }
        } catch (_) {}
      }
      localStorage.setItem('ns:migrated', '1');
    } catch (_) {}
  }

  var _get = localStorage.getItem.bind(localStorage);
  var _set = localStorage.setItem.bind(localStorage);
  var _rem = localStorage.removeItem.bind(localStorage);

  localStorage.getItem = function (k) {
    try {
      if (!k) return _get(k);
      var uid = getUid();
      if (isGlobalKey(k)) return _get(k);
      if (!uid) {
        return SENSITIVE_STRICT.has(k) ? null : _get(k);
      }
      var ns = _get(nsKey(k, uid));
      if (ns !== null) return ns;
      return SENSITIVE_STRICT.has(k) ? null : _get(k);
    } catch (_) {
      try {
        return _get(k);
      } catch (__) {
        return null;
      }
    }
  };

  localStorage.setItem = function (k, v) {
    try {
      if (!k) return _set(k, v);
      var uid = getUid();
      if (uid && !isGlobalKey(k)) return _set(nsKey(k, uid), v);
      return _set(k, v);
    } catch (_) {
      try {
        return _set(k, v);
      } catch (__) {}
    }
  };

  localStorage.removeItem = function (k) {
    try {
      if (!k) return _rem(k);
      var uid = getUid();
      if (uid && !isGlobalKey(k)) {
        try {
          _rem(nsKey(k, uid));
        } catch (_) {}
      }
      return _rem(k);
    } catch (_) {
      try {
        return _rem(k);
      } catch (__) {}
    }
  };

  try {
    window.nsStorage = {
      migrateLegacy: migrateLegacy,
      clearUser: function (uid) {
        uid = uid || getUid();
        if (!uid) return;
        try {
          var dels = [];
          for (var i = 0; i < localStorage.length; i++) {
            var key = localStorage.key(i);
            if (key && key.indexOf('user:' + uid + ':') === 0) dels.push(key);
          }
          dels.forEach(function (k) {
            try {
              _rem(k);
            } catch (_) {}
          });
        } catch (_) {}
      }
    };
  } catch (_) {}

  migrateLegacy(getUid());
})();
