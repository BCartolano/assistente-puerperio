# Wiring do /api/nearby no front

Este plugin adiciona suporte a “Perto de você” sem editar a classe Chat.

## Como usar

1. Garanta que o backend está com o endpoint ativo (0010-geo-index aplicado) e que o índice foi gerado:

   ```bash
   python scripts/build_hospitals_index.py
   ```

2. Inclua o script no HTML (após os outros scripts):

   ```html
   <script src="/static/js/nearby-wire.js" defer></script>
   ```

3. Recarregue a página com Ctrl+Shift+R.

## O que ele faz

- Pede a geolocalização do navegador.
- Chama `GET /api/nearby` com lat/lon.
- Cria uma seção **“Perto de você”** no topo da área de resultados e renderiza cards com:
  - Nome, Endereço (se houver)
  - Badges: Público/Privado/Filantrópico, SUS/Convênio, distância (km)
- Não interfere no restante da listagem/categorias.

## Tuning (opcional)

- Para mudar o raio/limite, edite `nearby-wire.js` (parâmetros `radius_km`/`limit` em `fetchNearby` e `tryLoadNearbyOnStart`).
- Se quiser inserir em um container específico, adicione `data-nearby-results` em um elemento e o plugin usa esse nó.

## Debug

- Abra o console e veja logs `[NEARBY]`.
- Se não aparecer, a app pode não expor a instância de Chat globalmente. O plugin tenta achar uma instância pelo método `displayHospitals`.
- Se a geolocalização estiver desativada, o plugin sai sem erro.

## Notas

- O patch não altera templates. Inclua o `<script>` no seu layout base.
- Se quiser integração mais “profunda” (usar o mesmo `displayHospitals` da app), dá para ajustar a chamada no `initMainApp` e mostrar a distância também nos cards da lista principal.

## Próximos passos recomendados

Depois de validar, podemos trocar o “autoKick” por uma chamada explícita no `initMainApp`, se preferir, e mostrar a distância também nos cards da lista principal.
