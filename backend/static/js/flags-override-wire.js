// -*- coding: utf-8 -*-
// Flags de UI (0098): permite override local (apenas front) antes de carregar os bundles.
(function(){
  'use strict';
  function get(k){ try{ return localStorage.getItem(k); }catch(_){ return null; } }
  function bool(v){ return String(v||'').toLowerCase().trim().match(/^(1|true|yes|on)$/) != null; }
  try{
    var sus = get('flags:show_sus_badges'), own = get('flags:show_ownership_badges');
    var ff = {};
    if (sus != null) ff.show_sus_badges = bool(sus);
    if (own != null) ff.show_ownership_badges = bool(own);
    if (Object.keys(ff).length){
      window.__APP_FLAGS = Object.assign({}, window.__APP_FLAGS || {}, ff);
    }
    var hstatus = get('flags:health_force_status');
    if (hstatus) window.__HEALTH_FORCE_STATUS = hstatus;
  }catch(_){}
})();
