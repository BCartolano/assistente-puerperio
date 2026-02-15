// -*- coding: utf-8 -*-
// Integração dos chips de "esfera" (Público/Privado/Filantrópico) diretamente nos cards.
// - Mostra chip só se o valor for canônico.
// - Remove "Privado" indevido quando não há ownership válido no dataset.
// - Funciona com cards já renderizados e futuros (MutationObserver).
(function () {
  'use strict';

  function stripAccents(s) {
    return (s || '').normalize('NFD').replace(/\p{Diacritic}/gu, '');
  }

  function norm(s) {
    return stripAccents(String(s || '').trim()).toLowerCase();
  }

  function normalizeOwnership(s) {
    var v = norm(s);
    if (!v) return null;
    if (v.includes('filan')) return 'Filantrópico';
    if (v.includes('publi') || v.includes('municip') || v.includes('estad') || v.includes('feder') || v.includes('distrit')) return 'Público';
    if (v.includes('privad') || v.includes('particul') || v.includes('cooper') || v.includes('empres')) return 'Privado';
    return null;
  }

  function isCanonical(val) {
    return val === 'Público' || val === 'Privado' || val === 'Filantrópico';
  }

  function ensureTagsBox(headerEl) {
    var box = headerEl.querySelector('.hospital-header-tags');
    if (!box) {
      var bottom = headerEl.querySelector('.hospital-header-bottom');
      if (!bottom) {
        bottom = document.createElement('div');
        bottom.className = 'hospital-header-bottom';
        headerEl.appendChild(bottom);
      }
      box = document.createElement('div');
      box.className = 'hospital-header-tags';
      bottom.appendChild(box);
    }
    return box;
  }

  function buildOwnershipBadge(value) {
    var span = document.createElement('span');
    span.dataset.badge = 'esfera';
    if (value === 'Público') span.className = 'hospital-tag-public';
    else if (value === 'Filantrópico') span.className = 'hospital-tag-philanthropic';
    else span.className = 'hospital-tag-private';
    span.textContent = value;
    return span;
  }

  // Não exibir chips Público/Privado/Filantrópico nos cards (decisão de produto).
  function fixHeader(headerEl) {
    try {
      if (!headerEl || !headerEl.classList || !headerEl.classList.contains('hospital-header')) return;
      headerEl.querySelectorAll('[data-badge="esfera"], .hospital-tag-public, .hospital-tag-private, .hospital-tag-philanthropic, .hospital-badge-info')
        .forEach(function (n) {
          var t = (n.textContent || '').trim();
          if (t === 'Público' || t === 'Privado' || t === 'Filantrópico' || /sus|convênio/i.test(t)) n.remove();
        });
      var convBlock = headerEl.closest('.hospital-card');
      if (convBlock) {
        convBlock.querySelectorAll('.hospital-convenios-info, .hospital-convenios').forEach(function (n) { n.remove(); });
      }
    } catch (_) {}
  }

  function scanAll() {
    document.querySelectorAll('.hospital-header').forEach(fixHeader);
  }

  try {
    var mo = new MutationObserver(function (muts) {
      for (var i = 0; i < muts.length; i++) {
        var m = muts[i];
        m.addedNodes && m.addedNodes.forEach(function (n) {
          if (!(n instanceof Element)) return;
          if (n.classList && n.classList.contains('hospital-header')) {
            fixHeader(n);
          } else {
            var hs = n.querySelectorAll ? n.querySelectorAll('.hospital-header') : [];
            hs && hs.forEach(fixHeader);
          }
        });
      }
    });
    mo.observe(document.documentElement, { childList: true, subtree: true });
  } catch (_) {}

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', scanAll);
  } else {
    scanAll();
  }

  // expõe util por conveniência (debug)
  window.fixOwnershipBadgesForHospitalCards = scanAll;
})();
