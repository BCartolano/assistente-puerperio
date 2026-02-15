// -*- coding: utf-8 -*-
// Bundle de UX para os cards de hospitais:
// - Telefone clicável, copiar endereço, rota/mapa (lat/lon ou endereço)
// - Conveniados com "ver mais"
// - Flags para (re)exibir badges SUS/esfera por ambiente
// - Debug dos cards (?debugHosp=1) com resumo do health da base
// - Headers capturados do /api/v1/emergency/search (X-Data-Source/X-Data-Mtime)
// - Tooltips de headers (arquivo/mtime) por card (0086)
(function(){
'use strict';

// ===== Health details (fetch uma vez, reutiliza) =====
var __HEALTH_PROMISE = null;
function getHealthDetails(){
  if (!__HEALTH_PROMISE){
    __HEALTH_PROMISE = fetch('/api/v1/emergency/health/details', { cache:'no-store', credentials:'include' })
      .then(function(r){ return r.ok ? r.json() : {}; }).catch(function(){ return {}; });
  }
  return __HEALTH_PROMISE;
}

// ===== Headers (emergency/nearby) capturados pelos wires =====
function getAnyHeadersSummary(){
  try{
    var h = window.__EMERGENCY_HEADERS || window.__NEARBY_HEADERS;
    if (!h || typeof h !== 'object') return null;
    var src = h.x_data_source || '';
    try { src = src.split(/[\\/]/).pop(); } catch(_){}
    var fetchedIso = h.fetched_at ? new Date(h.fetched_at).toISOString() : undefined;
    var mtimeIso = undefined;
    if (typeof h.x_data_mtime === 'number'){
      var s = h.x_data_mtime > 1e12 ? h.x_data_mtime : (h.x_data_mtime * 1000);
      mtimeIso = new Date(s).toISOString();
    } else if (h.x_data_mtime && !isNaN(+h.x_data_mtime)) {
      var n = +h.x_data_mtime;
      var s2 = n > 1e12 ? n : (n * 1000);
      mtimeIso = new Date(s2).toISOString();
    }
    return { source: src || undefined, x_data_mtime: h.x_data_mtime || undefined, mtime_iso: mtimeIso, fetched_at_iso: fetchedIso, url: h.url || undefined,
         x_data_count: (typeof h.x_data_count==='number'? h.x_data_count: undefined), q_lat: h.q_lat||undefined, q_lon: h.q_lon||undefined, q_radius_km: h.q_radius_km||undefined };
  }catch(_){ return null; }
}

function renderTooltipContent(tip, hdr){
  var busca = (hdr.q_lat||'')+(hdr.q_lat? ', ':'')+(hdr.q_lon||'')+(hdr.q_radius_km? ' • '+hdr.q_radius_km+'km': '');
  var rows = [
    {k:'Fonte', v: hdr.source || '(desconhecida)'},
    {k:'Mtime', v: hdr.mtime_iso || String(hdr.x_data_mtime || '')},
    {k:'Capturado', v: hdr.fetched_at_iso || ''},
    {k:'Busca', v: busca}
  ];
  tip.innerHTML = rows.map(function(r){ return '<div class="row"><span class="k">'+r.k+':</span><span class="v">'+(r.v||'')+'</span></div>'; }).join('');
}

// ===== Tooltip por card (0086) =====
function attachHeaderTooltip(card){
  try{
    var hdr = getAnyHeadersSummary();
    if (!hdr) return;
    var nameEl = card.querySelector('.hospital-name');
    var host = card.querySelector('.hospital-header-top') ||
               card.querySelector('.hospital-header') ||
               (nameEl && nameEl.parentNode) ||
               card;
    if (!host || host.__hospTooltipApplied__) return;
    host.__hospTooltipApplied__ = true;
    var wrap = document.createElement('span'); wrap.className = 'hosp-tooltip-wrap';
    var btn = document.createElement('button'); btn.type='button'; btn.className='hosp-info-btn'; btn.setAttribute('aria-label','Fonte dos dados'); btn.textContent='i';
    var tip = document.createElement('div'); tip.className = 'hosp-tooltip';
    renderTooltipContent(tip, hdr);
    btn.addEventListener('click', async function(ev){
      ev.preventDefault(); ev.stopPropagation();
      tip.classList.toggle('hosp-tooltip--show');
      try{
        var fn = (window.__EMERGENCY_HEADERS && window.__EMERGENCY_HEADERS.url) ? window.refreshEmergencyHeaders : window.refreshNearbyHeaders;
          var updated = await (fn ? fn() : null);
        if (updated){
          var sum = getAnyHeadersSummary();
          if (sum) renderTooltipContent(tip, sum);
        }
      }catch(_){}
    });
    document.addEventListener('click', function(e){ if (!wrap.contains(e.target)) tip.classList.remove('hosp-tooltip--show'); }, { capture:true });
    wrap.appendChild(btn); wrap.appendChild(tip); host.appendChild(wrap);
  }catch(_){}
}

// ===== Flags (SUS/esfera) =====
var FLAGS = { show_sus_badges: false, show_ownership_badges: false };
function bool(v){ return String(v||'').toLowerCase().trim().match(/^(1|true|yes|on)$/) != null; }
async function loadFlags(){
  try{
    if (window.__APP_FLAGS){
      FLAGS.show_sus_badges = !!window.__APP_FLAGS.show_sus_badges;
      FLAGS.show_ownership_badges = !!window.__APP_FLAGS.show_ownership_badges;
      return;
    }
    var r = await fetch('/flags.json', { cache:'no-store', credentials:'include' });
    if (r.ok){
      var j = await r.json().catch(function(){ return null; });
      if (j){ FLAGS.show_sus_badges = !!j.show_sus_badges; FLAGS.show_ownership_badges = !!j.show_ownership_badges; return; }
    }
  }catch(_){}
  try{
    var b = document.body;
    if (b && b.dataset){
      FLAGS.show_sus_badges = bool(b.dataset.showSusBadges);
      FLAGS.show_ownership_badges = bool(b.dataset.showOwnershipBadges);
    }
  }catch(_){}
}
// ===== Util =====
function telE164(text){
  var digits = (text||'').replace(/\D+/g,'');
  if (!digits) return null;
  if (digits.length >= 10 && digits.length <= 13){
    if (!digits.startsWith('55')) digits = '55'+digits;
    return '+'+digits;
  }
  return null;
}
function formatTel(text){
  var d = (text||'').replace(/\D+/g,'');
  if (d.length === 10) return '('+d.slice(0,2)+') '+d.slice(2,6)+'-'+d.slice(6);
  if (d.length === 11) return '('+d.slice(0,2)+') '+d.slice(2,7)+'-'+d.slice(7);
  return text || '';
}
function mapsDir(lat, lon, end){
  try{
    if (lat != null && lon != null && lat !== '' && lon !== ''){
      return 'https://www.google.com/maps/dir/?api=1&destination='+encodeURIComponent(String(lat)+','+String(lon));
    }
    if (end && end.trim()) return 'https://www.google.com/maps/dir/?api=1&destination='+encodeURIComponent(end.trim());
  }catch(_){}
  return null;
}
function mapsPlace(lat, lon, end){
  try{
    if (lat != null && lon != null && lat !== '' && lon !== ''){
      return 'https://www.google.com/maps/search/?api=1&query='+encodeURIComponent(String(lat)+','+String(lon));
    }
    if (end && end.trim()) return 'https://www.google.com/maps/search/?api=1&query='+encodeURIComponent(end.trim());
  }catch(_){}
  return null;
}
function copyToClipboard(text){
  try {
    navigator.clipboard.writeText(text);
  } catch(_) {
    var ta = document.createElement('textarea');
    ta.value = text; document.body.appendChild(ta); ta.select(); try{ document.execCommand('copy'); }catch(_){}
    document.body.removeChild(ta);
  }
}
function addrFromCard(card){
  var el = card.querySelector('.hospital-address, [data-role="address"]');
  var t = el ? el.textContent || '' : '';
  return (t||'').trim();
}
function telFromCard(card){
  var el = card.querySelector('.hospital-phone, [data-role="phone"], a[href^="tel:"]');
  var text = el ? (el.getAttribute('data-phone') || el.getAttribute('href') || el.textContent || '') : '';
  text = text.replace(/^tel:/i,'').trim();
  return text;
}
function conveniosFromCard(card){
  var wrap = card.querySelector('.hospital-convenios, [data-role="convenios"], .convenios-chips');
  if (!wrap) return {wrap:null, list:[]};
  var items = [];
  wrap.querySelectorAll('.convenio-chip, [data-convenio], li, span').forEach(function(n){
    var v = (n.getAttribute('data-convenio') || n.textContent || '').trim();
    if (v) items.push(v);
  });
  return {wrap: wrap, list: Array.from(new Set(items))};
}

// resumo do health para debug
function summarizeHealth(h){
  if (!h || typeof h !== 'object') return null;
  var src = h.source || h.source_path || '';
  try { src = src.split(/[\/]/).pop(); } catch(_){}
  return {
    status: h.status || 'ok',
    count: typeof h.count === 'number' ? h.count : undefined,
    ttl_remaining: typeof h.ttl_remaining === 'number' ? h.ttl_remaining : undefined,
    ttl_seconds: typeof h.ttl_seconds === 'number' ? h.ttl_seconds : undefined,
    mtime_iso: h.mtime_iso || undefined, source: src || undefined
  };
}

// ===== Aplicar recursos a um card =====
function enhanceCard(card){
  try{
    var lat = card.getAttribute('data-lat') || (card.dataset && card.dataset.lat) || '';
    var lon = card.getAttribute('data-lon') || (card.dataset && card.dataset.lon) || '';
    // 1) Badges: ocultar sempre (decisão de produto)
    card.querySelectorAll('[data-badge="sus"], .badge-sus, [data-badge="esfera"], .badge-esfera').forEach(function(b){
      b.classList.add('hide');
    });
    // 2) Telefone: garantir tel: link
    var rawTel = telFromCard(card);
    var e164 = telE164(rawTel);
    if (e164){
      var pretty = formatTel(rawTel);
      var telEl = card.querySelector('.hospital-phone, [data-role="phone"]');
      if (telEl){
        var a = telEl.querySelector('a[href^="tel:"]');
        if (!a){
          a = document.createElement('a');
          a.href = 'tel:'+e164;
          a.setAttribute('data-phone', e164);
          a.textContent = pretty || e164;
          telEl.innerHTML = '';
          telEl.appendChild(a);
        } else {
          a.href = 'tel:'+e164;
          a.setAttribute('data-phone', e164);
          if (!a.textContent) a.textContent = pretty || e164;
        }
      }
      var btnCall = card.querySelector('.btn-call, [data-action="call"], .hospital-call-btn');
      if (btnCall){
        btnCall.addEventListener('click', function(ev){
          ev.preventDefault(); ev.stopPropagation();
          window.location.href = 'tel:'+e164;
        });
      }
    }
    // 3) Copiar endereço + rota/mapa
    var addr = addrFromCard(card);
    var btnCopy = card.querySelector('.btn-copy-address, [data-action="copy-address"], .hospital-copy-btn');
    if (btnCopy && addr){
      var copyText = addr;
      if (btnCopy.getAttribute('data-copy')) copyText = btnCopy.getAttribute('data-copy');
      btnCopy.addEventListener('click', function(ev){
        ev.preventDefault(); ev.stopPropagation();
        copyToClipboard(copyText);
        try{ var lbl = btnCopy.querySelector('[data-copy-label]') || btnCopy; lbl.textContent = 'Copiado!'; setTimeout(function(){ lbl.textContent = 'Copiar'; }, 1500); }catch(_){}
      });
    }
    var btnRoute = card.querySelector('.btn-route, [data-action="route"], .hospital-route-btn');
    if (btnRoute){
      var url = mapsDir(lat,lon,addr);
      if (url){
        btnRoute.addEventListener('click', function(ev){ ev.preventDefault(); ev.stopPropagation(); window.open(url,'_blank','noopener'); });
      }
    }
    var btnMap = card.querySelector('.btn-map, [data-action="map"], .hospital-map-btn');
    if (btnMap){
      var urlp = mapsPlace(lat,lon,addr);
      if (urlp){
        btnMap.addEventListener('click', function(ev){ ev.preventDefault(); ev.stopPropagation(); window.open(urlp,'_blank','noopener'); });
      }
    }
    // 4) Convenios – não exibir chips/nota (decisão de produto)
    var convWrap = card.querySelector('.hospital-convenios,[data-role="convenios"],.convenios-chips,.convenios-note');
    if (convWrap){ convWrap.innerHTML = ''; convWrap.classList.add('hide'); }
    var conv = conveniosFromCard(card);
    // 4.5) Tooltip de headers (arquivo/mtime) – sempre que headers já existirem
    attachHeaderTooltip(card);
    // 5) Debug (/?debugHosp=1)
    var qs = new URLSearchParams(location.search);
    if (qs.get('debugHosp') === '1'){
      var dbg = document.createElement('pre');
      dbg.className = 'hosp-debug';
      var cnes = card.getAttribute('data-cnes') || card.dataset.cnes || '';
      var out = { cnes: cnes, lat: lat, lon: lon, endereco: addr, telefone: rawTel, convenios: conv.list };
      dbg.textContent = JSON.stringify(out, null, 2);
      card.appendChild(dbg);
      getHealthDetails().then(function(h){
        try{
          var sum = summarizeHealth(h);
          if (sum){
            out.__health = sum;
            dbg.textContent = JSON.stringify(out, null, 2);
          }
        }catch(_){}
        try{
          var hdrs = getAnyHeadersSummary();
          if (hdrs){
            out.__headers = hdrs;
          }
        }catch(_){}
        try{
          attachHeaderTooltip(card);
        }catch(_){}
        try{
          dbg.textContent = JSON.stringify(out, null, 2);
        }catch(_){}
        try{
          window.dispatchEvent(new CustomEvent('emergency:search-done', { detail: out.__headers || {} }));
        }catch(_){}
      }).catch(function(){ /* no-op */ });
    }
  }catch(_){}
}
// ===== Aplicar na lista =====
function enhanceAll(){
  document.querySelectorAll('.hospital-card, [data-role="hospital-card"]').forEach(enhanceCard);
}
function observe(){
  try{
    var mo = new MutationObserver(function(muts){
      for (var i=0;i<muts.length;i++){
        var m = muts[i];
        if (m.addedNodes){
          for (var j=0;j<m.addedNodes.length;j++){
            var n = m.addedNodes[j];
            if (!(n instanceof Element)) continue;
            if (n.classList && (n.classList.contains('hospital-card') || n.getAttribute('data-role')==='hospital-card')) enhanceCard(n);
            var list = n.querySelectorAll ? n.querySelectorAll('.hospital-card,[data-role="hospital-card"]') : [];
            if (list) for (var k=0;k<list.length;k++) enhanceCard(list[k]);
          }
        }
      }
    });
    mo.observe(document.body, { childList:true, subtree:true });
  }catch(_){}
}
// ===== Boot =====
function ready(fn){ if (document.readyState==='loading') document.addEventListener('DOMContentLoaded', fn); else fn(); }
ready(async function(){
  await loadFlags();
  enhanceAll();
  observe();
});
})();
