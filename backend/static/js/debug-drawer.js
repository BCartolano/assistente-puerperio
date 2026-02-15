// -*- coding: utf-8 -*-
// Debug Drawer (0096): versão, health, última busca, flags e botões úteis.
(function(){
  'use strict';
  try{
    if (window.__DEBUG_ENABLED === false) return;
  }catch(_){}
  function ce(tag, cls, html){ var el=document.createElement(tag); if(cls) el.className=cls; if(html!=null) el.innerHTML=html; return el; }
  function fmtTTL(sec){ if(typeof sec!=='number'||isNaN(sec)) return ''; if(sec<60) return sec+'s'; var m=Math.round(sec/60); if(m<60) return m+'m'; return Math.round(m/60)+'h'; }
  async function getVersion(){ try{ if (window.getAppVersion){ return await window.getAppVersion(); } var r=await fetch('/version.json',{cache:'no-store'}); var j=await r.json(); return j&&j.version; }catch(_){ return ''; } }
  async function getHealth(){ try{ var r=await fetch('/api/v1/emergency/health/details',{cache:'no-store'}); return r.ok? await r.json(): {}; }catch(_){ return {}; } }
  function getLastHeaders(){ try{ return window.__EMERGENCY_HEADERS || window.__NEARBY_HEADERS || {}; }catch(_){ return {}; } }
  function setLocal(k,v){ try{ if(v==null) localStorage.removeItem(k); else localStorage.setItem(k,v); }catch(_){ } }
  function rebuildFlags(){ try{ window.__APP_FLAGS = { show_sus_badges: (localStorage.getItem('flags:show_sus_badges')==='1'), show_ownership_badges: (localStorage.getItem('flags:show_ownership_badges')==='1') }; window.__HEALTH_FORCE_STATUS = localStorage.getItem('flags:health_force_status')||''; window.dispatchEvent(new Event('health:override-changed')); }catch(_){ } }
  async function buildPanel(){
    var panel = ce('div','dbg-panel'); document.body.appendChild(panel);
    var secV = ce('div','dbg-sec'); secV.appendChild(ce('h4',null,'Versão'));
    var v = await getVersion();
    var rowV = ce('div','dbg-kv'); rowV.appendChild(ce('span','dbg-k','build')); rowV.appendChild(ce('span','dbg-v', String(v||'(n/d)'))); secV.appendChild(rowV);
    panel.appendChild(secV); panel.appendChild(ce('div','dbg-hr'));
    var secH = ce('div','dbg-sec'); secH.appendChild(ce('h4',null,'Health'));
    var h = await getHealth();
    var kvs = [
      ['status', h.status||'(n/d)'],
      ['count', (h.count!=null? String(h.count):'(n/d)')],
      ['ttl', (h.ttl_remaining!=null && h.ttl_seconds!=null? fmtTTL(h.ttl_remaining)+'/'+fmtTTL(h.ttl_seconds):'')],
      ['mtime', h.mtime_iso || '(n/d)'],
      ['source', (h.source||h.source_path||'').toString().split(/[\\/]/).pop() || '(n/d)']
    ];
    kvs.forEach(function(p){ var r=ce('div','dbg-kv'); r.appendChild(ce('span','dbg-k',p[0])); r.appendChild(ce('span','dbg-v',p[1])); secH.appendChild(r); });
    panel.appendChild(secH); panel.appendChild(ce('div','dbg-hr'));
    var secS = ce('div','dbg-sec'); secS.appendChild(ce('h4',null,'Última busca'));
    var L = getLastHeaders();
    var rows = [
      ['count', (L.x_data_count!=null? String(L.x_data_count):'(n/d)')],
      ['fonte', (L.x_data_source||'').toString().split(/[\\/]/).pop() || '(n/d)'],
      ['mtime', (typeof L.x_data_mtime==='number'? new Date(L.x_data_mtime>1e12? L.x_data_mtime : L.x_data_mtime*1000).toISOString(): String(L.x_data_mtime||'(n/d)'))],
      ['lat', L.q_lat||''], ['lon', L.q_lon||''], ['radius_km', L.q_radius_km||'']
    ];
    rows.forEach(function(p){ var r=ce('div','dbg-kv'); r.appendChild(ce('span','dbg-k',p[0])); r.appendChild(ce('span','dbg-v',p[1])); secS.appendChild(r); });
    var rowBtns = ce('div','dbg-row');
    var bCopy = ce('button','dbg-btn','Copiar JSON'); bCopy.onclick=function(){ try{ navigator.clipboard.writeText(JSON.stringify({version:v, health:h, last:L},null,2)); }catch(_){ } };
    rowBtns.appendChild(bCopy); secS.appendChild(rowBtns);
    panel.appendChild(secS); panel.appendChild(ce('div','dbg-hr'));
    var secF = ce('div','dbg-sec'); secF.appendChild(ce('h4',null,'Flags (apenas front)'));
    var fSUS = ce('div','dbg-kv'); var chkSUS = ce('input'); chkSUS.type='checkbox'; chkSUS.checked = localStorage.getItem('flags:show_sus_badges')==='1';
    fSUS.appendChild(ce('span','dbg-k','SUS badges')); var spSUS = ce('span','dbg-v'); spSUS.appendChild(chkSUS); fSUS.appendChild(spSUS); secF.appendChild(fSUS);
    var fOWN = ce('div','dbg-kv'); var chkOWN = ce('input'); chkOWN.type='checkbox'; chkOWN.checked = localStorage.getItem('flags:show_ownership_badges')==='1';
    fOWN.appendChild(ce('span','dbg-k','Esfera badges')); var spOWN = ce('span','dbg-v'); spOWN.appendChild(chkOWN); fOWN.appendChild(spOWN); secF.appendChild(fOWN);
    var fH = ce('div','dbg-kv'); fH.appendChild(ce('span','dbg-k','Health force'));
    var sel = ce('select'); ['','ok','degraded','stale'].forEach(function(v){ var opt=ce('option',null,(v||'(nenhum)')); opt.value=v; if((localStorage.getItem('flags:health_force_status')||'')===v) opt.selected=true; sel.appendChild(opt); });
    var spH = ce('span','dbg-v',''); spH.appendChild(sel); fH.appendChild(spH); secF.appendChild(fH);
    var fBtns = ce('div','dbg-row');
    var bSave = ce('button','dbg-btn','Salvar'); bSave.onclick=function(){
      setLocal('flags:show_sus_badges', chkSUS.checked?'1':null);
      setLocal('flags:show_ownership_badges', chkOWN.checked?'1':null);
      setLocal('flags:health_force_status', sel.value||null);
      rebuildFlags();
    };
    var bClear = ce('button','dbg-btn','Limpar'); bClear.onclick=function(){ setLocal('flags:show_sus_badges',null); setLocal('flags:show_ownership_badges',null); setLocal('flags:health_force_status',null); rebuildFlags(); };
    fBtns.appendChild(bSave); fBtns.appendChild(bClear);
    secF.appendChild(fBtns); panel.appendChild(secF);
    return panel;
  }
  function buildFab(panel){
    var fab = ce('button','dbg-fab','⚙️ debug');
    fab.onclick=function(){ panel.classList.toggle('open'); };
    document.body.appendChild(fab);
  }
  function ready(fn){ if (document.readyState==='loading') document.addEventListener('DOMContentLoaded', fn); else fn(); }
  ready(async function(){ var panel = await buildPanel(); buildFab(panel); });
})();
