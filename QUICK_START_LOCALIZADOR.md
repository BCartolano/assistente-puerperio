# 🚀 Quick Start - Localizador Puerperal

Guia rápido para iniciar o Localizador Puerperal em 3 passos.

## ⚡ Início Rápido (3 Passos)

### Passo 1: Popular Banco com Dados de Teste

```bash
python backend/etl/seed_data.py
```

✅ Isso cria 5 hospitais simulados em São Paulo para testes.

### Passo 2: Iniciar Backend

```bash
# Terminal 1
uvicorn backend.api.main:app --reload
```

✅ Backend disponível em: http://localhost:5000

### Passo 3: Iniciar Frontend

```bash
# Terminal 2
cd frontend
npm install  # Primeira vez apenas
npm run dev
```

✅ Frontend disponível em: http://localhost:3000

## 🧪 Teste Rápido

1. Abra http://localhost:3000
2. Permita geolocalização (ou use coordenadas de SP: -23.5505, -46.6333)
3. Veja os hospitais aparecerem no mapa!
4. Teste os filtros:
   - **SUS + Maternidade**: Deve mostrar Hospital das Clínicas (AZUL)
   - **Privado**: Deve mostrar Santa Joana (VERDE)
   - **Sem filtro maternidade**: Deve mostrar UPA (AMARELO)
   - **Botão EMERGÊNCIA**: Deve mostrar TODOS

## 📚 Documentação Completa

Para testes detalhados e validação QA, veja: [TESTING_LOCALIZADOR.md](./TESTING_LOCALIZADOR.md)

## 🐳 Com Docker (Opcional)

```bash
# Iniciar tudo de uma vez
docker-compose up --build

# Parar
docker-compose down
```

---

**Pronto para uso! 🎉**
