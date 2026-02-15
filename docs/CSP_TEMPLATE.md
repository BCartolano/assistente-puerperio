# Content-Security-Policy (CSP) – Template

Parcial: **backend/templates/_csp_meta.html**

## Diretivas definidas (padrão)

- **default-src** 'self'
- **script-src** 'self' 'unsafe-inline'
- **style-src** 'self' 'unsafe-inline' https://fonts.googleapis.com
- **img-src** 'self' data: https:
- **font-src** 'self' https://fonts.gstatic.com
- **connect-src** 'self' https://api.groq.com
- **base-uri** 'self'; **form-action** 'self'; **frame-ancestors** 'self'; **object-src** 'none'; **upgrade-insecure-requests**

## Observações

- `'unsafe-inline'` está ligado porque há scripts/estilos inline. Para apertar:
  - remova scripts inline e use arquivos .js
  - troque `script-src` para: `script-src 'self'`
- Se carregar fontes/estilos de outro provedor, adicione-o em style-src/font-src.
- Se o backend/API estiver em outro domínio, inclua em connect-src.

## Validar

- DevTools > Console: corrija erros CSP que aparecerem (dizem qual diretiva bloquearia o recurso).
- Se algum fetch aparecer bloqueado, inclua o host na connect-src (ex.: CDN, analytics).
