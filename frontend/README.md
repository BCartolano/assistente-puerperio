# Localizador Puerperal - Frontend

Interface web **Mobile-First** construída com React (Vite) + Tailwind CSS para busca de hospitais e maternidades.

## 🎯 Objetivo

Fornecer uma interface **"à prova de estresse"** com:
- ✅ Botões grandes e claros
- ✅ Leitura fácil (mesmo com bebê no colo)
- ✅ Separação visual clara (SUS vs Privado)
- ✅ Botão de emergência destacado
- ✅ Navegação direta para Google Maps

## 🚀 Início Rápido

### 1. Instalar Dependências

```bash
cd frontend
npm install
```

### 2. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na pasta `frontend/`:

```env
VITE_API_URL=http://localhost:5000
```

### 3. Iniciar Servidor de Desenvolvimento

```bash
npm run dev
```

A aplicação estará disponível em: http://localhost:3000

### 4. Build para Produção

```bash
npm run build
```

## 📱 Funcionalidades

### Header
- Logo do app
- **Botão de Pânico** (vermelho pulsante): Ativa modo emergência

### Barra de Filtros
- **Segregação Financeira** (PM): Toggle SUS vs Privado vs Todos
- **Checkbox**: "Apenas Maternidades" (default: marcado)

### Mapa (Leaflet)
- Posição atual da usuária (marcador azul)
- Pinos coloridos dos hospitais:
  - 🔵 Azul: SUS/Público
  - 🟢 Verde: Privado
  - 🟡 Amarelo: UPA

### Cards de Resultados
- **Cores** conforme tipo:
  - Azul: SUS
  - Verde: Privado
  - Amarelo: UPA (aviso: não faz parto)
- **Informações**:
  - Nome do hospital
  - Distância
  - Badges (ACEITA SUS, MATERNIDADE, etc.)
  - Endereço
  - Warning messages (se houver)
- **Ações**:
  - Botão "Navegar": Abre Google Maps
  - Botão Telefone: Liga direto (se disponível)

### Aviso Legal
- Banner fixo no rodapé
- Texto obrigatório (Lei 11.634/2008)
- Pode ser fechado, mas sempre visível inicialmente

## 🎨 Design System

### Cores (UX Expert)

- `sus-blue` (#2563eb): Hospitais SUS/Públicos
- `private-green` (#059669): Hospitais Privados
- `emergency-yellow` (#eab308): UPAs
- `panic-red` (#dc2626): Botão de emergência

### Componentes

- **Header**: Sticky, com botão de emergência
- **FilterBar**: Filtros simples e claros
- **MapView**: Mapa interativo com Leaflet
- **ResultsList**: Cards com cores e badges
- **LegalDisclaimer**: Banner fixo no rodapé
- **EmergencyModal**: Modal de confirmação de emergência

## 🔌 Integração com API

A aplicação faz requisições para:
- `POST /api/v1/facilities/search`

Exemplo de payload:
```json
{
  "latitude": -23.5505,
  "longitude": -46.6333,
  "radius_km": 10,
  "filter_type": "MATERNITY",
  "is_emergency": false
}
```

## 📱 Mobile First

- Design responsivo
- Botões grandes (fácil de tocar)
- Texto legível
- Navegação simplificada
- Geolocalização automática

## 🛡️ Regras Implementadas

### PM (Product Manager)
- ✅ Triagem de emergência: Botão destacado, ignora filtros
- ✅ Segregação financeira: Filtros separados visualmente
- ✅ Apenas maternidades: Checkbox com default marcado

### Analyst
- ✅ Cores por tipo: Azul (SUS), Verde (Privado), Amarelo (UPA)
- ✅ Badges corretos: Baseados em tags da API

### UX Expert
- ✅ Aviso legal obrigatório: Sempre visível
- ✅ Código de cores: Implementado
- ✅ Warning messages: Exibidos em vermelho nos cards
- ✅ Botão de navegação: Link direto para Google Maps

## 🧪 Testes

### Teste Manual

1. Abrir aplicação: http://localhost:3000
2. Permitir geolocalização
3. Verificar se hospitais aparecem no mapa
4. Testar filtros (SUS, Privado, Maternidade)
5. Clicar em "EMERGÊNCIA" e verificar se ignora filtros
6. Clicar em "Navegar" e verificar se abre Google Maps

## 📚 Tecnologias

- **React 18**: Framework UI
- **Vite**: Build tool rápido
- **Tailwind CSS**: Utility-first CSS
- **Leaflet**: Mapas gratuitos (OpenStreetMap)
- **React Leaflet**: Bindings React para Leaflet
- **Lucide React**: Ícones
- **Axios**: Cliente HTTP

## 🔄 Próximos Passos

1. ✅ Interface básica criada
2. ⏳ Testes automatizados (Jest + React Testing Library)
3. ⏳ PWA (Progressive Web App)
4. ⏳ Cache offline
5. ⏳ Notificações push

---

**Desenvolvido seguindo diretrizes de Health Data Audit**  
**Mobile-First, Acessível, À Prova de Estresse**
