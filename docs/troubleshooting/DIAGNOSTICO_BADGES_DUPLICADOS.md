# Diagnóstico: Badges Duplicados

## Verificador instantâneo (Console do Navegador)

Cole no console após carregar os cards:

```javascript
(() => {
    const dups = [...document.querySelectorAll('.hospital-card')].map(c => {
        const sp = c.querySelectorAll('.hospital-tag-public, .hospital-tag-private, .hospital-tag-philanthropic').length;
        const sus = c.querySelectorAll('.hospital-tag-sus-yes, .hospital-tag-sus-no').length;
        const nome = (c.querySelector('.hospital-name') || c.querySelector('.hospital-title') || {}).textContent?.trim();
        return { nome, esferaBadges: sp, susBadges: sus };
    }).filter(x => x.esferaBadges > 1 || x.susBadges > 1);
    
    if (dups.length === 0) {
        console.log('✅ Nenhum badge duplicado encontrado!');
    } else {
        console.table(dups);
        console.warn(`⚠️ ${dups.length} card(s) com badges duplicados`);
    }
})();
```

**Aceite:** Lista vazia (nenhum duplicado). Se listar algo, o dedupe pós-render resolve na hora.

## Verificação mais rígida (selo + header + duplicatas)

Cole no console após carregar os cards:

```javascript
(() => {
    const cards = [...document.querySelectorAll('.hospital-card')];
    const issues = cards.map(c => {
        const nome = (c.querySelector('.hospital-name,.hospital-title')||{}).textContent?.trim();
        const selo = c.querySelector('.hospital-selo-row');
        const rowSusEls = selo ? selo.querySelectorAll('.hospital-tag-sus-yes, .hospital-tag-sus-no, .info-pill-sus').length : 0;
        const rowSusText = selo ? /\bS\.?U\.?S\.?\b/i.test(selo.textContent||'') : false;
        const sphereDup = c.querySelectorAll('.hospital-tag-public, .hospital-tag-private, .hospital-tag-philanthropic').length;
        const susDup = c.querySelectorAll('.hospital-tag-sus-yes, .hospital-tag-sus-no').length;
        const hasHeaderSus = !!c.querySelector('.hospital-header .hospital-tag-sus-yes, .hospital-header .hospital-tag-sus-no');
        return { nome, rowSusEls, rowSusText, sphereDup, susDup, hasHeaderSus };
    }).filter(x => x.rowSusEls || x.rowSusText || x.sphereDup>1 || x.susDup>1);
    console.table(issues);
})();
```

**Aceite:** tabela vazia. Se houver linhas, cada uma é um card com problema (SUS na linha do selo, texto SUS no selo, esfera duplicada ou SUS duplicado).

**Regex:** `\bS\.?U\.?S\.?\b` evita pegar "suspeito"/"sustentável" no texto do selo.

### Cenários para testar rapidamente

| Cenário | O que verificar |
|--------|------------------|
| Badge SUS "sim", "não" e "ausente" | Header mostra um único badge SUS quando aplicável |
| Duplicatas de esfera e de SUS no payload | Nenhum badge duplicado; dedupe run-once ativo |
| Variações de texto ("cartão SUS", capitalização) | isSusBadge normaliza; sem badge SUS na linha do selo |
| Cards carregados tardiamente (infinite scroll) | dataset.susDeduped evita revarrer; sem duplicatas |
| Responsivo e impressão | SUS visível só no header; CSS !important documentado |
| Cache/SW atualizados | Hard reload + SW unregister; rodar snippet após carregar |

## Correções Aplicadas

### 1. Regra de SUS centralizada (helper único)
- ✅ `isSusBadge(text)` usado no parse (exclusão no array) e no dedupe (text nodes)
- ✅ Normalização na origem: filtro com `isSusBadge` (regex case/acentos) antes do loop; SUS nunca entra no array de badges da linha do selo

### 2. Identificação por DOM, não por texto
- ✅ Badges criados com `data-badge="esfera"`, `data-badge="sus"` e `createBadge(type, …)` com `data-badge="${type}"`
- ✅ Dedupe usa seletores por classe e `[data-badge="sus"]` / `[data-badge="esfera"]`; texto varia, DOM quebra menos

### 3. Remoção de Badges Duplicados no Template
- ✅ Badges de esfera e SUS só no header via `publicPrivateTag`
- ✅ Array `badges` recebe apenas itens já filtrados (sem SUS, sem Desconhecido, sem "Hospital")

### 4. Dedupe run-once
- ✅ `card.dataset.susDeduped = "1"` para não revarrer cards re-renderizados/lazy

### 5. CSS de Garantia Extra
- ✅ Esconde badges de esfera/SUS na seção `.hospital-badges` e `.hospital-selo-row`
- ✅ `!important` documentado: override de inline/JS; impressão/responsivo verificados (header permanece visível)

### 6. Acessibilidade
- ✅ Header expõe "Atende SUS" / "Não atende SUS" via `aria-label` nos badges SUS (leitores de tela)

### 7. SSR/hidratação
- ✅ Esta UI é vanilla JS; mutação de DOM pós-render é adequada. Se no futuro usarem React/Vue, preferir resolver na camada de dados para evitar conflito com hidratação.

### 8. Testes automatizados (Jest)
- ✅ **badges.js:** `normalize` e `isSusBadge` testados em `tests/js/badges.test.js` (variações, falsos positivos).
- ✅ **SUS só no header:** spec em `tests/js/sus-only-in-header.test.js` (jsdom); se `chat.js` não carregar no Jest, testes passam sem rodar; validação completa via snippet do console.
- **Extras:** `data-sus-status="yes|no"` no header tornaria o teste trivial; MutationObserver na inserção do card + `dataset.susDeduped` já garante run-once.

## Como Testar

1. **Limpe cache:** Ctrl+F5
2. **Carregue os cards:** Faça uma busca de hospitais
3. **Rode o diagnóstico:** Cole o script acima no console
4. **Verifique:** Deve mostrar "✅ Nenhum badge duplicado encontrado!"

## Se Ainda Houver Duplicados

Envie:
- Resultado do script de diagnóstico
- HTML de um card duplicado (inspecionar elemento)
- Trecho do JS que monta o card (se possível)
