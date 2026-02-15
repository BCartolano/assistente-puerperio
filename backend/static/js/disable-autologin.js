/**
 * Corta tentativas de autologin automáticas no Chat (login só quando o usuário envia o formulário).
 */
(function () {
  'use strict';
  function patch() {
    var P = (window.ChatbotPuerperio && window.ChatbotPuerperio.prototype)
      ? window.ChatbotPuerperio.prototype
      : (window.Chat && window.Chat.prototype ? window.Chat.prototype : null);
    if (!P || P.autoLoginPatched) return;
    P.autoLoginPatched = true;

    if (typeof P.handleInitialLogin === 'function') {
      var orig = P.handleInitialLogin;
      P.handleInitialLogin = function () {
        if (this && this.log) try { this.log('[AUTH] AutoLogin desativado (wire)'); } catch (_) {}
        return Promise.resolve();
      };
      return;
    }
    if (typeof P.initMainApp === 'function') {
      var origInit = P.initMainApp;
      P.initMainApp = function () {
        this.shouldTryAutoLogin = false;
        if (this && this.log) try { this.log('[AUTH] AutoLogin desativado (initMainApp)'); } catch (_) {}
        return origInit.apply(this, arguments);
      };
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', patch);
  } else {
    patch();
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      setTimeout(patch, 500);
    });
  } else {
    setTimeout(patch, 500);
  }
})();
