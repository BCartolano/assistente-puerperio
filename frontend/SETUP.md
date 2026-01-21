# Setup do Frontend - Localizador Puerperal

## 📋 Pré-requisitos

- Node.js 18+ instalado
- Backend FastAPI rodando em `http://localhost:5000`

## 🚀 Passo a Passo

### 1. Instalar Dependências

```bash
cd frontend
npm install
```

### 2. Configurar Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar .env se necessário (padrão: http://localhost:5000)
```

### 3. Iniciar Servidor de Desenvolvimento

```bash
npm run dev
```

A aplicação estará disponível em: **http://localhost:3000**

### 4. Verificar Funcionamento

1. Abra o navegador em http://localhost:3000
2. Permita acesso à geolocalização
3. Verifique se hospitais aparecem no mapa
4. Teste os filtros e botão de emergência

## 🐛 Troubleshooting

### Erro: "Failed to fetch"
- Verifique se o backend está rodando: `uvicorn backend.api.main:app --reload`
- Verifique a URL da API no arquivo `.env`

### Erro: "Geolocalização não permitida"
- Certifique-se de permitir acesso à localização no navegador
- Em desenvolvimento local, o HTTPS não é necessário

### Mapa não carrega
- Verifique conexão com internet (Leaflet usa OpenStreetMap)
- Verifique console do navegador para erros

## 📦 Build para Produção

```bash
npm run build
```

Os arquivos estarão em `frontend/dist/`

## 🔗 Integração com Backend

O frontend faz requisições para:
- `POST /api/v1/facilities/search`

Certifique-se de que:
1. ✅ Backend está rodando
2. ✅ Banco de dados CNES foi populado: `python backend/etl/data_ingest.py`
3. ✅ CORS está configurado no backend
