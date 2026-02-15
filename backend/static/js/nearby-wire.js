// -*- coding: utf-8 -*-
// Integra /api/nearby no front sem tocar na classe Chat.
// - Extende Chat.prototype com tryLoadNearbyOnStart/renderNearbySection.
// - Busca lat/lon do navegador, consulta /api/nearby e renderiza cards.
(function () {
  'use strict';

  function http(url, opts) {
    try {
      if (typeof window !== 'undefined' && typeof window.robustFetch === 'function') {
        return window.robustFetch(url, Object.assign({ method: 'GET' }, opts || {}));
      }
    } catch (_) {}
    return fetch(url, Object.assign({ method: 'GET' }, opts || {}));
  }

  function getCurrentPositionAsync(timeoutMs = 8000) {
    return new Promise((resolve, reject) => {
      if (typeof navigator === 'undefined' || !navigator.geolocation) {
        return reject(new Error('geolocation_not_available'));
      }
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          resolve({ lat: pos.coords.latitude, lon: pos.coords.longitude });
        },
        (err) => reject(err),
        { enableHighAccuracy: false, maximumAge: 60000, timeout: timeoutMs }
      );
    });
  }

  async function fetchNearby({ lat, lon, radius_km = 20, limit = 40, accepts_sus, accepts_convenio, public_private } = {}) {
    const qs = new URLSearchParams();
    qs.set('lat', String(lat));
    qs.set('lon', String(lon));
    if (radius_km != null) qs.set('radius_km', String(radius_km));
    if (limit != null) qs.set('limit', String(limit));
    if (accepts_sus != null) qs.set('accepts_sus', String(accepts_sus));
    if (accepts_convenio != null) qs.set('accepts_convenio', String(accepts_convenio));
    if (public_private) qs.set('public_private', public_private);
    const res = await http('/api/nearby?' + qs.toString(), { method: 'GET' });
    if (!res.ok) {
      const txt = await res.text().catch(() => '');
      throw new Error('nearby http ' + res.status + ': ' + txt.slice(0, 180));
    }
    return res.json();
  }

  function ensureContainer() {
    const byData = document.querySelector('[data-nearby-results]');
    if (byData) return byData;
    const results = document.getElementById('results') || document.querySelector('.results') || document.body;
    let section = results.querySelector('.nearby-section');
    if (!section) {
      section = document.createElement('section');
      section.className = 'nearby-section';
      const title = document.createElement('h3');
      title.className = 'nearby-title';
      title.textContent = 'Perto de você';
      section.appendChild(title);
      const list = document.createElement('div');
      list.className = 'nearby-list';
      section.appendChild(list);
      results.prepend(section);
    }
    return section.querySelector('.nearby-list');
  }

  function createBadge(text, dataBadge) {
    const b = document.createElement('span');
    b.className = 'hospital-badge';
    if (dataBadge) b.setAttribute('data-badge', dataBadge);
    b.textContent = text;
    return b;
  }

  /** 0073: Normaliza item de /api/nearby para schema unificado (compatível com emergency/search). */
  function normalizeNearbyToUnified(item) {
    const esfera = item.public_private || item.esfera || null;
    const sus = item.accepts_sus;
    const susBadge = typeof sus === 'boolean' ? (sus ? 'Aceita Cartão SUS' : 'Não atende SUS') : (item.sus_badge || null);
    return {
      name: item.name || item.nome || 'Hospital',
      address: item.address || item.endereco || '',
      street: item.street || item.logradouro || null,
      houseNumber: item.houseNumber || item.numero || null,
      neighborhood: item.neighborhood || item.bairro || null,
      city: item.city || item.cidade || null,
      state: item.state || item.estado || null,
      lat: item.lat,
      lon: item.lon,
      distance_km: typeof item.distance_km === 'number' ? item.distance_km : null,
      phone: item.phone || item.telefone_formatado || item.telefone || '',
      public_private: esfera,
      esfera: esfera,
      accepts_sus: sus,
      sus_badge: susBadge,
      accepts_convenio: item.accepts_convenio,
      convenios: Array.isArray(item.convenios) ? item.convenios : [],
      has_convenios: !!item.has_convenios || (Array.isArray(item.convenios) && item.convenios.length > 0),
      cnes: item.cnes || item.cnes_id
    };
  }

  function escapeHtml(s) {
    if (s == null || s === '') return '';
    const div = document.createElement('div');
    div.textContent = s;
    return div.innerHTML;
  }

  function createCard(h) {
    const u = normalizeNearbyToUnified(h);
    const card = document.createElement('div');
    card.className = 'hospital-card';
    if (u.cnes) card.dataset.id = u.cnes;
    if (u.public_private) card.dataset.ownership = u.public_private;
    const header = document.createElement('div');
    header.className = 'hospital-header';
    const top = document.createElement('div');
    top.className = 'hospital-header-top';
    const name = document.createElement('h4');
    name.className = 'hospital-name';
    name.textContent = u.name || 'Hospital';
    top.appendChild(name);
    header.appendChild(top);
    const bottom = document.createElement('div');
    bottom.className = 'hospital-header-bottom';
    if (u.public_private) bottom.appendChild(createBadge(u.public_private, 'esfera'));
    if (u.sus_badge) bottom.appendChild(createBadge(u.sus_badge, 'sus'));
    if (typeof u.accepts_convenio === 'boolean') {
      bottom.appendChild(createBadge(u.accepts_convenio ? 'Convênio' : 'Sem convênio', 'convenio'));
    }
    if (typeof u.distance_km === 'number' && !Number.isNaN(u.distance_km)) {
      const bd = createBadge(u.distance_km.toFixed(1) + ' km', 'distance');
      bd.classList.add('hospital-badge--distance');
      bottom.appendChild(bd);
    }
    header.appendChild(bottom);
    card.appendChild(header);
    // Convênios/Público/Privado/SUS: não exibir nos cards (decisão de produto)
    var addrText = u.address;
    if (!addrText && (u.street || u.city)) {
      var parts = [];
      if (u.street) parts.push(u.street);
      if (u.houseNumber && u.street) parts[parts.length - 1] += ', ' + u.houseNumber;
      if (u.neighborhood) parts.push(u.neighborhood);
      if (u.city) parts.push(u.city);
      if (u.state) parts.push(u.state);
      addrText = parts.join(' – ');
    }
    if (addrText) {
      const addr = document.createElement('div');
      addr.className = 'hospital-address';
      addr.style.cssText = 'font-size:0.85rem;color:#6b7280;margin-top:8px;';
      addr.textContent = addrText;
      card.appendChild(addr);
    }
    if (u.phone) {
      const tel = document.createElement('div');
      tel.className = 'hospital-phone';
      tel.style.cssText = 'font-size:0.85rem;color:#6b7280;margin-top:4px;';
      const a = document.createElement('a');
      a.href = 'tel:' + u.phone.replace(/\D/g, '');
      a.textContent = u.phone;
      tel.appendChild(a);
      card.appendChild(tel);
    }
    return card;
  }

  function attachToChatPrototype() {
    if (typeof window === 'undefined' || !window.Chat) return;
    const P = window.Chat.prototype;
    if (!P || P.nearby_wired) return;
    P.nearby_wired = true;
    P.renderNearbySection = function renderNearbySection(items) {
      if (items === undefined) items = [];
      try {
        if (!Array.isArray(items) || items.length === 0) return;
        const list = ensureContainer();
        if (!list) return;
        list.innerHTML = '';
        const frag = document.createDocumentFragment();
        items.forEach(function (h) { frag.appendChild(createCard(h)); });
        list.appendChild(frag);
        if (this.log) this.log('[NEARBY] Renderizados ' + items.length + ' itens');
      } catch (e) {
        if (this.error) this.error('[NEARBY] render falhou', e);
      }
    };
    P.tryLoadNearbyOnStart = async function tryLoadNearbyOnStart() {
      try {
        if (!('geolocation' in navigator)) {
          if (this.log) this.log('[NEARBY] Geolocalização indisponível');
          return;
        }
        const pos = await getCurrentPositionAsync();
        const lat = pos.lat;
        const lon = pos.lon;
        if (this.log) this.log('[NEARBY] Coordenadas: ' + lat.toFixed(3) + ',' + lon.toFixed(3));
        const data = await fetchNearby({ lat: lat, lon: lon, radius_km: 20, limit: 40 });
        if (!data || !Array.isArray(data.items)) return;
        this.renderNearbySection(data.items);
      } catch (e) {
        if (this.error) this.error('[NEARBY] Falha ao obter próximos', e);
      }
    };
  }

  function autoKick() {
    const candidates = Object.values(window).filter(function (v) {
      return v && typeof v === 'object' &&
        typeof v.displayHospitals === 'function' &&
        (typeof v.loadChatHistory === 'function' || typeof v.initMainApp === 'function');
    });
    const chat = candidates[0];
    if (chat && typeof chat.tryLoadNearbyOnStart === 'function') {
      try { chat.tryLoadNearbyOnStart(); } catch (_) {}
      return true;
    }
    return false;
  }

  document.addEventListener('DOMContentLoaded', function () {
    try { attachToChatPrototype(); } catch (_) {}
    let tries = 0;
    const t = setInterval(function () {
      tries += 1;
      if (autoKick() || tries > 10) clearInterval(t);
    }, 400);
  });
})();
