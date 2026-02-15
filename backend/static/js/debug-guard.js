// -*- coding: utf-8 -*-
// Guardião do debug: esconde o botão/painel em produção, mostra apenas com ?debug=1 ou flag no localStorage.
(function(){
  'use strict';
  try{
    var qs = new URLSearchParams(location.search||'');
    if (qs.get('debug') === '1') localStorage.setItem('debug:enabled','1');
    if (qs.get('debug') === '0') localStorage.removeItem('debug:enabled');
  }catch(_){}
  try{
    window.__DEBUG_ENABLED = (localStorage.getItem('debug:enabled') === '1');
    if (!window.__DEBUG_ENABLED){
      var st = document.createElement('style');
      st.textContent = '.dbg-fab, .dbg-panel{ display:none !important }';
      document.head.appendChild(st);
    }
  }catch(_){}
})();
