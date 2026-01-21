# 🔧 Guia de Event Delegation - Sophia

## ⚠️ PROBLEMA COMUM

Quando elementos são criados dinamicamente (via `innerHTML` ou `createElement`), event listeners diretos **NÃO FUNCIONAM** se o DOM for atualizado.

## ✅ SOLUÇÃO: Event Delegation

### Padrão Obrigatório

```javascript
// ✅ CORRETO: Event delegation no document
document.addEventListener('click', (e) => {
    const btn = e.target.closest('.sintoma-btn-yes');
    if (btn) {
        const sintomaId = btn.getAttribute('data-sintoma-id');
        if (sintomaId) {
            this.processarRespostaSintoma(sintomaId, 'sim');
        }
    }
});
```

### ❌ ERRADO: Event Listener Direto

```javascript
// ❌ ERRADO: Botão morre se DOM for atualizado
document.querySelector('.sintoma-btn-yes').addEventListener('click', ...);
```

## 📋 CHECKLIST DE IMPLEMENTAÇÃO

### Elementos Dinâmicos (SEMPRE usar delegation)
- [ ] Botões de triagem (`.sintoma-btn-yes`, `.sintoma-btn-no`)
- [ ] Botões de ação (`.sintoma-acao-hospital`, `.sintoma-voltar-btn`)
- [ ] Botões de hospital (`.hospital-call-btn`, `.hospital-copy-btn`)
- [ ] Qualquer botão criado via `innerHTML` ou `createElement`

### Elementos Estáticos (Pode usar listener direto)
- [ ] Botões do sidebar (criados no HTML inicial)
- [ ] Botões de navegação (criados no HTML inicial)
- [ ] Inputs e formulários (criados no HTML inicial)

## 🎯 EXEMPLOS PRÁTICOS

### Triagem de Sintomas
```javascript
// ✅ CORRETO
document.addEventListener('click', (e) => {
    const btn = e.target.closest('.sintoma-btn-yes, .sintoma-btn-no');
    if (btn) {
        const sintomaId = btn.getAttribute('data-sintoma-id');
        const resposta = btn.getAttribute('data-resposta');
        if (sintomaId && resposta) {
            this.processarRespostaSintoma(sintomaId, resposta);
        }
    }
});
```

### Cards de Hospital
```javascript
// ✅ CORRETO
document.addEventListener('click', (e) => {
    const copyBtn = e.target.closest('.hospital-copy-btn');
    if (copyBtn) {
        const address = copyBtn.getAttribute('data-copy');
        if (address) {
            this.copyToClipboard(address);
        }
    }
});
```

## 🚨 ALERTAS

Se você ver:
- `querySelector('.dynamic-button').addEventListener(...)` → **REVERTA**
- Event listener em elemento criado via `innerHTML` → **REVERTA**
- Botão que para de funcionar após atualização de DOM → **Use delegation**

## 📚 REFERÊNCIAS

- Implementação atual: `backend/static/js/chat.js` (linhas 1269-1279)
- Documentação completa: `docs/style-guide-sophia.md`
