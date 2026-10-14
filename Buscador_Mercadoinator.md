# Projeto: Buscador de Preços de Mercado

## 1. Visão Geral
* **O que é:** Ferramenta automatizada de monitoramento de preços para produtos domésticos e itens essenciais na internet, com envio de alertas de promoções em tempo real.
* **Objetivo:** Baratear o custo de aquisição da cesta básica e itens de limpeza/higiene.

---

## 2. Escopo e Lista de Monitoramento

### Itens Prioritários (Cesta Básica e Limpeza)
- Arroz
- Feijão
- Açúcar
- Leite
- Óleo
- Sabão em pó
- Amaciante

### Sites Alvo
- **Mercado Livre** (`mercadolivre.com.br`) — *Base de comparação*
- **Amazon**
- **Super São Roque** (`ecommerce.supersaoroque.com.br`)
- **Delta Super** (`loja.deltasuper.com.br`)
- **Magazine Luiza** (`magazineluiza.com.br`) — *Pendente de investigação*

---

## 3. Arquitetura e Stack Tecnológica

| Componente | Tecnologia / Ferramenta | Justificativa |
| :--- | :--- | :--- |
| **Coletor / Scraper** | Python + Playwright / BeautifulSoup | Ecossistema maduro para scraping. Uso do **Playwright** (navegador headless) para contornar proteções anti-bot (Mercado Livre) e SPAs/JS pesado (Delta Super). |
| **Armazenamento** | SQLite | Banco relacional leve e sem necessidade de servidor local. Fácil migração para PostgreSQL no futuro. |
| **Notificações** | Telegram Bot API | Gratuito, API simples, notificações instantâneas no celular, sem os custos/burocracia do WhatsApp. |
| **Agendamento** | Cron / Task Scheduler / Azure Functions | Execução diária automatizada (localmente via Cron/Task Scheduler ou em nuvem via Azure Functions Timer Trigger). |

---

## 4. Plano de Execução em Fases

### Fase 1: Escopo e Mapeamento dos Itens
- [x] Definir os produtos da cesta básica e marcas de referência.
- [x] Mapear os marketplaces e supermercados regionais-alvo.

### Fase 2: Investigação Técnica dos Sites Alvo
- [ ] **Mercado Livre:** Avaliar o uso da API pública/não-oficial vs. scraping com Playwright.
- [ ] **Delta Super & Super São Roque:** Identificar seletores CSS/XPath e requisições XHR internas.
- [ ] **Magazine Luiza:** Investigar estrutura do HTML/API e nível de proteção anti-bot.
- [ ] Validar `robots.txt` e Termos de Uso dos alvos.

### Fase 3: Construção do Coletor (Scraper)
- [ ] Criar estrutura base do script em Python.
- [ ] Implementar a extração (Nome, Preço, Link, Data/Hora) para 1 site (MVP).
- [ ] Modularizar a extração por seletores específicos de cada site (troca de parsers/seletores por domínio).

### Fase 4: Banco de Dados e Histórico
- [ ] Modelar tabela no SQLite (`historico_precos`: id, produto_id, site, preco, link, data_coleta).
- [ ] Implementar rotina para salvar cada rodada de coleta no banco de dados.

### Fase 5: Regras de Negócio e Alertas
- [ ] Definir a lógica de "Promoção":
  - Queda de X% em relação à média dos últimos 30 dias.
  - Preço abaixo do histórico mínimo registrado.
- [ ] Criar script de comparação pós-coleta.

### Fase 6: Integração com Telegram
- [ ] Criar o bot via `@BotFather` no Telegram e obter o `token`.
- [ ] Desenvolver a função Python para envio de mensagens formatadas.
- [ ] Validar disparos de teste antes da integração total.

### Fase 7: Automação e Agendamento
- [ ] Configurar execução periódica (ex: 1x ao dia).
- [ ] Configurar Cron/Task Scheduler local ou implantar no Azure Functions (Tier Gratuito).

### Fase 8: Iteração e Painel Visual (Opcional)
- [ ] Expandir o scraper para cobrir novos supermercados e marcas.
- [ ] Desenvolver um dashboard simples (HTML estático/Streamlit) para visualização do histórico de variações de preços.