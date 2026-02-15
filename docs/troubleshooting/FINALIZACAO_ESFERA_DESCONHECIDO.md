# Finalização: Eliminação de "Desconhecido" - Checklist Completo

## ✅ Implementado

### 1. Guard-Rails
- ✅ `scripts/guard_no_unknown.py` - Valida Parquet
- ✅ `tests/api/test_esfera_canonica.py` - Teste E2E (PASSED)
- ✅ Gate no orquestrador - Bloqueia pipeline se inválido

### 2. Normalização em Múltiplas Camadas
- ✅ `_normalize_esfera()` - Rejeita "Desconhecido" explicitamente
- ✅ `_apply_cnes_overrides()` - Fallback seguro
- ✅ Guards finais no Flask e FastAPI
- ✅ Frontend - Só renderiza valores válidos

### 3. Script "Martelo" Aplicado
- ✅ `scripts/apply_overrides_to_geo.py` - Aplicou overrides em massa
- ✅ 598.661 registros CNES carregados
- ✅ Parquet atualizado: 2.354 Público, 315 Filantrópico, 3.117 Privado

### 4. Endpoint de Refresh do Cache
- ✅ `POST /api/v1/debug/geo/refresh` - Limpa cache e força re-load
- ✅ Disponível em Flask e FastAPI

## 🚀 Como Usar Após Aplicar Overrides

### Passo 1: Aplicar Overrides em Massa
```powershell
python scripts/apply_overrides_to_geo.py
```

**Resultado esperado:**
```
[OK] Regravado hospitals_geo.parquet (5786 linhas)
[OK] Salvo hospitals_geo.min.parquet (5786 linhas)
[ESTATÍSTICAS] Distribuição de esfera:
  Privado: 3117
  Público: 2354
  Filantrópico: 315
```

### Passo 2: Refresh do Cache da API
```powershell
# Via curl
curl -X POST http://localhost:5000/api/v1/debug/geo/refresh

# Ou no console do navegador
fetch('/api/v1/debug/geo/refresh', {method:'POST'})
```

**Resposta esperada:**
```json
{
  "ok": true,
  "rows": 5786
}
```

### Passo 3: Limpar Cache do Navegador
- **Ctrl+F5** (ou janela anônima)
- Se tiver service worker:
  ```javascript
  navigator.serviceWorker.getRegistrations().then(rs => rs.forEach(r => r.unregister()));
  ```

### Passo 4: Diagnóstico Express (Console do Navegador)
```javascript
fetch('/api/v1/emergency/search?lat=-23.1931904&lon=-45.7965568&radius_km=25&limit=20&expand=true&debug=true')
  .then(r=>r.json())
  .then(d => console.table((d.results||[]).map(it=>({
    nome: it.nome,
    cnes: it.cnes_id,
    esfera: it.esfera,
    sus: it.sus_badge,
    hit: it.override_hit,
    reason: it.override_reason
  }))));
```

**Aceite:**
- ✅ `esfera` só "Público/Privado/Filantrópico" (ou null) — **nunca "Desconhecido"**
- ✅ `override_hit = true` e `reason="applied"` na maioria
- ✅ UI: todos os 17 mostram o badge correto

## 📊 Verificação no /health

O endpoint `/api/v1/health` já loga:
```
[geo] cache carregado: 5786 linhas (src=hospitals_geo.min.parquet)
```

Isso confirma que a API está usando o Parquet novo.

## 🔍 Se Ainda Houver Problema

Envie:
1. **1 linha do `/search?debug=true`:**
   ```json
   {
     "nome": "...",
     "cnes_id": "...",
     "esfera": "...",
     "override_hit": true/false,
     "override_reason": "..."
   }
   ```

2. **Resposta do `/api/v1/debug/overrides/coverage`:**
   ```bash
   curl http://localhost:5000/api/v1/debug/overrides/coverage
   ```

Com isso identificamos exatamente: "é snapshot X", ou "é CSV em Y", ou "é cache".

## 📝 Commit Message Sugerido

```
chore(overrides): aplicar CNES em massa no Parquet e matar fallback "Desconhecido"

- scripts/apply_overrides_to_geo.py: aplica esfera/sus_badge/convênios para todos os CNES e regrava .parquet e .min
- backend: _normalize_esfera em todos os fluxos; payload nunca "Desconhecido"
- frontend: badge só renderiza para 'Público/Privado/Filantrópico'; sem defaults
- scripts/guard_no_unknown.py + tests/api/test_esfera_canonica.py + gate no orquestrador
- endpoint admin /api/v1/debug/geo/refresh para recarregar dataset em memória
```

## ✅ Status Final

- ✅ Teste E2E passando
- ✅ Parquet atualizado com overrides
- ✅ Frontend protegido
- ✅ Backend protegido em múltiplas camadas
- ✅ Pipeline protegido com guard
- ✅ Endpoint de refresh implementado

**Tudo pronto para produção!** 🎉
