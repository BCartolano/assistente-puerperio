# 🧪 Checklist de QA - Sophia

## ⚠️ TESTES OBRIGATÓRIOS ANTES DE COMMITAR

### 1. Teste Visual - Cores
- [ ] Inspecione TODOS os botões - nenhum está cinza (#555, #333)
- [ ] Verifique hover states - todos ficam rosa pastel
- [ ] Confirme que não há cores hex hard-coded
- [ ] Valide que variáveis CSS estão sendo usadas

### 2. Teste Visual - Tamanhos
- [ ] Nenhum botão está gigante (padding > 1rem)
- [ ] Fontes são legíveis (0.85rem - 0.95rem)
- [ ] Ícones não excedem 3rem
- [ ] Botões têm padding confortável para clique

### 3. Teste Funcional - Triagem
- [ ] Abre "Sinais de Alerta" do sidebar
- [ ] Clica em "Sim" em sintoma crítico → mostra recomendação
- [ ] Clica em "Ir para Hospitais Próximos" → abre busca de hospitais
- [ ] Clica em "Voltar aos Sintomas" → retorna à lista
- [ ] Testa 5 vezes seguidas sem erros
- [ ] Verifica localStorage - histórico está salvando

### 4. Teste Funcional - Hospitais
- [ ] Busca de hospitais funciona
- [ ] Botão "Ligar" funciona (tel: link)
- [ ] Botão "Copiar endereço" funciona
- [ ] Botão "Rota" abre Google Maps
- [ ] Badges (SUS, Maternidade) aparecem corretamente

### 5. Teste Mobile
- [ ] Botões têm padding suficiente (0.7rem mínimo)
- [ ] Texto não quebra layout
- [ ] Imagens são proporcionais (max-height: 120px)
- [ ] Cards não ficam muito pequenos
- [ ] Scroll funciona suavemente

### 6. Teste de Console
- [ ] Nenhum erro JavaScript
- [ ] Nenhum warning de CSS
- [ ] localStorage funciona sem erros
- [ ] Fetch requests não falham silenciosamente

## 🚨 CRITÉRIOS DE REJEIÇÃO

**REJEITE IMEDIATAMENTE** se:
- Botão aparecer cinza
- Botão estiver gigante (padding > 1rem)
- Cor hex hard-coded no CSS
- Event listener direto em elemento dinâmico
- Erro no console ao testar triagem
- localStorage não salvar histórico

## 📊 RELATÓRIO DE TESTE

Após cada teste, documente:
```
✅ Teste Visual: PASS
✅ Teste Funcional Triagem: PASS (5/5 execuções)
✅ Teste Mobile: PASS
✅ Console: Limpo
⚠️ Observações: [se houver]
```

## 📚 REFERÊNCIAS

- Style Guide: `docs/style-guide-sophia.md`
- Event Delegation: `docs/event-delegation-guide.md`
