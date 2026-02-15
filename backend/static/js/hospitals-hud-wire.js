// -*- coding: utf-8 -*-
// HUD com resumo do health no topo da modal/lista de hospitais (0088)
(function(){
  'use strict';
  function fmtTTL(sec){
    if (typeof sec !== 'number' || isNaN(sec)) return '';
    if (sec < 60) return sec+'s';
    var m = Math.round(sec/60);
    if (m < 60) return m+'m';
    var h = Math.round(m/60);
    return h+'h';
  }
  function pickHost(){
    return document.querySelector('#hospitals-modal .modal-body') ||
           document.querySelector('#hospitals-modal') ||
           document.querySelector('.hospitals-list, [data-role="hospitals-list"]') ||
           document.body;
  }
  function renderHUD(host, d){
    if (!host) return;
    if (window.__HEALTH_FORCE_STATUS) d.status = window.__HEALTH_FORCE_STATUS;
    var hud = host.querySelector('.hosp-hud');
    if (!hud){
      hud = document.createElement('div'); hud.className='hosp-hud';
      if (host.firstChild) host.insertBefore(hud, host.firstChild); else host.appendChild(hud);
    }
    var cls = 'hosp-hud';
    if (d.status === 'stale') cls += ' hud-bad';
    else if (d.status === 'degraded') cls += ' hud-warn';
    hud.className = cls;
    var parts = [];
    parts.push('<span class="dot"></span>');
    var line = 'Base '+(d.status||'ok').toUpperCase();
    if (typeof d.count === 'number') line += ' • '+d.count+' itens';
    if (d.mtime_iso) line += ' • mtime '+d.mtime_iso;
    if (typeof d.ttl_remaining === 'number' && typeof d.ttl_seconds === 'number') line += ' • TTL '+fmtTTL(d.ttl_remaining)+'/'+fmtTTL(d.ttl_seconds);
    var help = (d.status === 'degraded' || d.status === 'stale') ? '<span class="hud-help">Base desatualizada ou menor que o esperado. Tente novamente em instantes.</span>' : '';
    hud.innerHTML = parts.join('')+'<span class="line">'+line+'</span>'+help;
  }
  async function fetchDetails(){
    try{
      var r = await fetch('/api/v1/emergency/health/details', { cache:'no-store', credentials:'include' });
      if (!r.ok) return null;
      return await r.json();
    }catch(_){ return null; }
  }
  function ready(fn){ if (document.readyState==='loading') document.addEventListener('DOMContentLoaded', fn); else fn(); }
  ready(async function(){
    // HUD desativado para usuário final (evita exibir metadados técnicos: Base OK, mtime, itens)
    return;
    var host = pickHost();
    var d = await fetchDetails();
    if (d) renderHUD(host, d);
    window.addEventListener('health:override-changed', async function(){ var h = pickHost(); var data = await fetchDetails(); if (data) renderHUD(h, data); });
  });
})();
