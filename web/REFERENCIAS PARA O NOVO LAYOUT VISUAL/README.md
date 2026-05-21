# Handoff: Redesign IOMAT Mineração

## Sobre este pacote

Os arquivos em `preview/` são **referências de design criadas em HTML/React** — protótipos de alta fidelidade que mostram a aparência e o comportamento pretendidos. **Não são código de produção para copiar diretamente.**

A tarefa é **recriar estes designs no codebase Django existente** (templates `.html` + Tailwind, seguindo a base que já está em `templates/base.html`), aproveitando os padrões, a estrutura de templates, as views e os componentes já estabelecidos no projeto.

## Fidelidade

**Alta fidelidade (hi-fi)** — cores, tipografia, espaçamento e estados finais estão definidos. O desenvolvedor deve reproduzir pixel a pixel usando Tailwind (extendendo `tailwind.config.js` com os tokens abaixo).

---

## Visão geral

Sistema Django que busca documentos no IOMAT (Imprensa Oficial MT), extrai páginas, faz OCR, classifica com IA (gpt-4o-mini) e permite revisão humana. O redesign dá uma identidade técnica densa (Linear/Notion-like) ao produto, com ênfase em:

- **Pipeline AI ↔ Humano visível** — cada etapa marcada com tag `AI` ou `HUM`
- **Densidade de dados** — tabelas com custo, tokens, taxa, ETA
- **Linha do tempo 1961–2008** como elemento estruturante
- **Tema claro/escuro** com toggle
- **Sidebar persistente** com navegação e atalhos

---

## Tokens de design

Todos os componentes usam CSS variables. Adicione ao Tailwind config (ou use as variáveis direto no CSS):

### Cores — Claro

| Token            | Valor       | Uso                                         |
|------------------|-------------|---------------------------------------------|
| `--t-bg`         | `#fafafa`   | Fundo da página                             |
| `--t-surface`    | `#ffffff`   | Cards, sidebar, topbar                      |
| `--t-surface-2`  | `#f4f4f5`   | Cabeçalho de tabela, item ativo na nav      |
| `--t-surface-3`  | `#ebebed`   | Fundo de barra de progresso                 |
| `--t-ink`        | `#0b0d10`   | Texto principal                             |
| `--t-ink-2`      | `#35383d`   | Texto secundário                            |
| `--t-muted`      | `#8a8e95`   | Texto auxiliar, labels                      |
| `--t-mute-2`     | `#b4b7bc`   | Texto muito suave, atalhos                  |
| `--t-rule`       | `#e4e4e7`   | Bordas, divisores                           |
| `--t-rule-2`     | `#d4d4d8`   | Bordas de botões secundários                |
| `--t-accent`     | `#2b5fd9`   | Acento primário (links, seleção, ações)     |
| `--t-accent-2`   | `#1a3f99`   | Acento hover/pressionado                    |
| `--t-ok`         | `#2f8f4e`   | Status OK, relevantes                       |
| `--t-warn`       | `#c47013`   | Duvidosos, fila de revisão                  |
| `--t-err`        | `#c83a3a`   | Erros, cancelar                             |
| `--t-ai`         | `#7a42c4`   | Tag AI e barras de etapas da IA             |
| `--t-human`      | `#2b5fd9`   | Tag HUM e etapas de revisão humana          |

### Cores — Escuro

| Token            | Valor       |
|------------------|-------------|
| `--t-bg`         | `#0a0b0d`   |
| `--t-surface`    | `#111214`   |
| `--t-surface-2`  | `#17181b`   |
| `--t-surface-3`  | `#1e2024`   |
| `--t-ink`        | `#eef0f3`   |
| `--t-ink-2`      | `#c2c6cc`   |
| `--t-muted`      | `#7a7f87`   |
| `--t-mute-2`     | `#55595f`   |
| `--t-rule`       | `#25272b`   |
| `--t-rule-2`     | `#34373c`   |
| `--t-accent`     | `#6b92f5`   |
| `--t-accent-2`   | `#94b0f8`   |
| `--t-ok`         | `#5cc47a`   |
| `--t-warn`       | `#e09946`   |
| `--t-err`        | `#e66363`   |
| `--t-ai`         | `#b892f0`   |
| `--t-human`      | `#6b92f5`   |

### Tipografia

- **Sans (UI):** `Inter` — pesos 400, 500, 600, 700
- **Mono (dados/códigos/IDs):** `JetBrains Mono` — pesos 400, 500, 600
- Carregar via Google Fonts:
  ```html
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  ```

#### Escala

| Uso                                  | Família | Tamanho | Peso | Letter-spacing |
|--------------------------------------|---------|---------|------|----------------|
| Título de página (h1)                | Sans    | 20–22px | 600  | −0.01em        |
| Título de card (h3)                  | Sans    | 13px    | 600  | normal         |
| Corpo padrão                         | Sans    | 13px    | 400  | normal         |
| Subtexto                             | Sans    | 12px    | 400  | normal         |
| Label maiúsculo / eyebrow            | Mono    | 9–10px  | 500  | 0.06–0.14em    |
| Valor de KPI grande                  | Mono    | 24px    | 500  | −0.02em        |
| Tabela — cabeçalho                   | Mono    | 9px     | 500  | 0.06em, UPPER  |
| Tabela — célula numérica             | Mono    | 12px    | 400  | normal         |
| Log / código                         | Mono    | 11px    | 400  | normal         |
| Tag `AI` / `HUM`                     | Mono    | 8px     | 600  | 0.1em, UPPER   |

### Espaçamento e radius

| Token          | Valor | Uso                              |
|----------------|-------|----------------------------------|
| Radius pequeno | 3–4px | Chips, tags, progress bars       |
| Radius padrão  | 5–6px | Botões, inputs, itens de nav     |
| Radius card    | 8px   | Cards, tabelas, painéis          |
| Gap denso      | 4–8px | Entre chips, ícones              |
| Gap padrão     | 16px  | Entre cards                      |
| Gap de seção   | 24px  | Entre seções                     |
| Padding card   | 14–18px | Interior de cards              |

### Sombras / bordas

O design é **flat** — quase nenhuma sombra. Bordas de 1px (`var(--t-rule)`) definem quase tudo. Use sombras só em overlays/modais (não há no MVP).

---

## Componentes compartilhados

### `TechSidebar`
Largura **236px**, altura total da viewport, fundo `--t-surface`, borda direita `--t-rule`.

- **Header:** logo quadrado 22×22px radius 5 (`--t-ink` bg, `--t-surface` texto "I") + nome do produto (12px bold) + subtítulo mono 9px com versão e usuário.
- **Seções:** cabeçalho mono 9px uppercase `--t-muted` com letter-spacing 0.14em.
- **Itens:** padding 6px 10px, radius 5, hover `--t-surface-2`. Item ativo: fundo `--t-surface-2`, texto `--t-ink`, peso 500. Pode ter dot colorido à esquerda, badge numérico à direita (radius 4, bg tintado), ou atalho mono (ex: `G P`) à direita em `--t-mute-2`.
- **Footer:** `api: ok` à esquerda, `⌘ K` à direita, mono 9px `--t-muted`.

### `TechTopbar`
Altura **48px**, borda inferior `--t-rule`, fundo `--t-surface`, padding 10px 20px.

- Esquerda: breadcrumbs separados por `/` em `--t-mute-2`. Último crumb em `--t-ink` peso 500.
- Direita: botões de ação (ver `TechButton`).

### `TechButton`
- **Primary:** fundo `--t-ink`, texto `--t-surface`, borda `--t-ink`.
- **Secondary:** fundo `--t-surface`, texto `--t-ink-2`, borda `--t-rule-2`.
- **Danger:** transparente, texto `--t-err`, borda `color-mix(in oklab, var(--t-err) 40%, transparent)`.
- Padding 5px 10px, radius 6, font-size 12, peso 500.

### Tags `AI` e `HUM`
Pequeno retângulo mono 8px bold uppercase, padding 1px 4px, radius 3:
- **AI:** cor `--t-ai`, fundo `color-mix(in oklab, var(--t-ai) 12%, transparent)`
- **HUM:** cor `--t-human`, fundo `color-mix(in oklab, var(--t-human) 12%, transparent)`

Usar em qualquer ponto onde se indica autoria de uma ação ou etapa.

### Status pill
Dot colorido 6×6px radius 50% + label mono 10px, letter-spacing 0.04em, na mesma cor. Quando "running"/"em execução", o dot pulsa:

```css
@keyframes techPulse { 0%,100% { opacity: 1 } 50% { opacity: 0.35 } }
```

Mapa: `running` → `--t-accent` (pulsa); `done` → `--t-ok`; `failed` → `--t-err`; `queued` → `--t-muted`.

### Progress bar
Altura 6px, radius 3, fundo `--t-surface-3`. Preenchimento na cor apropriada (geralmente `--t-accent`, ou `--t-ai`/`--t-human` conforme o agente).

---

## Telas

Cada seção lista a tela, sua URL Django sugerida, view e template alvo. Consulte os componentes React em `preview/variations/tech-screens.jsx` para o layout exato.

### 01 — Painel (`dashboard/home.html`)
URL: `/` · View: `dashboard.views.home`

Layout:
- Sidebar (`TechSidebar active="painel"`)
- Topbar breadcrumbs: `Workspace / Painel` · ações: `Exportar CSV`, `+ Nova busca`
- Conteúdo:
  1. Título "Painel" + subtítulo mono "Corpus IOMAT 1961–2008 · atualizado há 2s"
  2. **Row de KPIs** (5 colunas iguais num card com divisores): Documentos processados, Relevantes IA, Fila de revisão, Aprovados, Custo IA mês. Label mono uppercase; valor mono 24px; delta pequeno colorido; sub em cinza.
  3. **Grid 2 colunas**: `TechPipelineCard` (pipeline ativa em miniatura) + `TechActivity` (log ao vivo com 6 linhas AI/HUM/SYS).
  4. **Heatmap ano × tipo**: 48 colunas (anos 1961–2008) × 5 linhas (tipos). Cada célula 18px alt, radius 2, cor via `color-mix(in oklab, var(--t-accent) X%, var(--t-surface-2))`. Escala na legenda.
  5. **Tabela de buscas** (ver seção 02).

### 02 — Lista de buscas (`searches/list.html`)
URL: `/buscas/` · View: `searches.views.SearchJobList`

- Título + subtítulo mono com contadores
- Toolbar de filtros: campo de busca, dropdown status, dropdown usuário, range de datas, botão "Limpar"
- Totais agregados em pill: `12.847 extraídos · 1.206 relevantes · 87 duvidosos`
- Tabela: `#`, termo, período, status (pill), extraídos, relevantes, duvidosos, custo, por, quando. Linhas com borda superior `--t-rule`, hover `--t-surface-2`. Tabela inteira em card radius 8 border `--t-rule`.

### 03 — Nova busca (`searches/new.html`)
URL: `/buscas/nova/` · View: `searches.views.SearchJobCreate`

Layout em **duas colunas** (form à esquerda, preview à direita):

Coluna esquerda — formulário:
- Grupo "Termo": input text + checkbox "busca exata"
- Grupo "Período": dois selects (de/até) com anos 1961–2008 · slider visual opcional mostrando range
- Grupo "Modelo IA": select (gpt-4o-mini default)
- Grupo "Opções avançadas" colapsável: batch size, limite de páginas
- Botões: `Cancelar` (secondary) + `Iniciar busca` (primary)

Coluna direita — **preview de estimativa**:
- Card "Estimativa" com mono 11px:
  - `anos cobertos: 48`
  - `páginas estimadas: ~2.800`
  - `tokens estimados: ~2.1M`
  - `custo estimado: $ 4.10 ± $ 0.80`
  - `tempo estimado: 35–45 min`
- Mini-heatmap mostrando densidade histórica da cobertura escolhida.

### 04 — Progresso da busca (`searches/detail.html`)
URL: `/buscas/<id>/` · View: `searches.views.SearchJobDetail`

- Sidebar ativa em "Buscas"
- Topbar: `Workspace / Buscas / #417` · ações: `Ver documentos`, `Cancelar` (danger)
- **Header da busca** num card: ID mono, status "em execução" com dot pulsante, título grande em mono `"tecnólogo" · 1961–2008`, metadata (usuário, horário, modelo em `--t-ai`)
- **KPIs inline** (6 colunas num card embutido): progresso %, decorrido, ETA, taxa doc/s, tokens, custo
- **Pipeline em esteira** (card separado):
  - Header: "Pipeline" + "3/6 concluídas"
  - 6 linhas com grid: `[num 32px] [label+detail 180px] [progress 1fr] [start 110px] [dur 70px]`
  - Linha ativa tem fundo `color-mix(in oklab, var(--t-accent) 4%, transparent)`
  - Labels têm tag AI/HUM quando aplicável
- **Grid 2 colunas (1fr × 1.2fr):** "Resultado parcial" (4 barras de % — relevantes/duvidosos/descartados/erros) + "Log ao vivo" (terminal mono com linhas `HH:MM:SS | AI/HUM/SYS | ação | mensagem`)

Comportamento: polling a cada 2s (já existe no template atual — manter).

### 05 — Lista de documentos (`documents/list.html`)
URL: `/documentos/` · View: `documents.views.DocumentList`

- Título + filtros avançados em card:
  - Search input
  - Chips de classificação: `Todos 12.847` · `Relevantes 1.206` · `Duvidosos 87` · `Descartados 11.554` · `Revisados 942` — chip ativo em `--t-ink` bg
  - Select tipo, select ano, select status IA
- Tabela com colunas: `#`, título (truncado), tipo (chip), ano (mono), página mono, classificação IA (pill cor) + tag AI, revisão humana (tag HUM + aprovado/rejeitado), score mono, ações.
- Paginação no rodapé com mono `1-50 de 1.206`.

### 06 — Detalhe do documento (`documents/detail.html`)
URL: `/documentos/<id>/` · View: `documents.views.DocumentDetail`

**Split layout (2 colunas 1.3fr × 1fr):**

Esquerda — texto OCR:
- Header sticky: breadcrumbs + título + ações (Baixar PDF, Abrir no IOMAT)
- Corpo em serifa 15px line-height 1.7, padding 32, bg branco/`--t-surface`. Highlights do termo em `color-mix(in oklab, var(--t-warn) 30%, transparent)` com borda inferior 2px `--t-warn`.

Direita — painel lateral:
- Card "Metadados": IOMAT edição/data/página, tipo do ato, ano, tamanho, idioma
- Card "Classificação IA": tag AI, classificação (pill), score mono grande, justificativa em itálico, tokens/custo
- Card "Revisão humana": tag HUM, decisão, por quem, quando, notas
- Card "Histórico": timeline vertical com eventos

### 07 — Fila de revisão (`reviews/queue.html`)
URL: `/revisoes/` · View: `reviews.views.ReviewQueue`

- Stats row: Aguardando (mono grande), Em análise, Concluídos hoje, Tempo médio
- Filtros: por busca, por tipo, por score da IA (range slider)
- Tabela de documentos pendentes com score IA visível como barra horizontal + chip `--t-warn`

### 08 — Revisão individual (`reviews/detail.html`)
URL: `/revisoes/<id>/` · View: `reviews.views.ReviewDetail`

Split view parecido com 06, mas painel direito é **decisão**:
- Card "Classificação da IA" (contexto) — compacto
- Card "Sua decisão" (grande, destacado):
  - 4 botões grandes: `Relevante [R]`, `Irrelevante [I]`, `Duvidoso [D]`, `Pular [Space]`
  - Textarea "Notas (opcional)"
  - `← Anterior` / `Próximo →` com atalhos setas
- Barra de progresso no topo: `12 de 87 revisados`

Atalhos de teclado: R, I, D, Space, ←, →.

---

## Interações & comportamento

- **Tema claro/escuro:** toggle no topbar. Persistir em `localStorage['iomat-theme']`. Aplica `data-theme` no `<html>` e o CSS troca via `[data-theme="dark"] { … }`.
- **Densidade compact/comfortable:** toggle no perfil. Altera padding de cards (18→14) e de células de tabela (10→6). Persistir igualmente.
- **Polling:** telas 04 (progresso) e 07 (fila) refazem fetch a cada 2s.
- **Atalhos globais:** `⌘K` abre palette; `G P/B/D/R` navega. Implementar com handler no `base.html`.
- **Estados:** todo botão tem `:hover` (bg leve), `:focus-visible` (ring `--t-accent` 2px), `:disabled` (opacity 0.5, cursor not-allowed).

---

## Como implementar no Django

1. **Atualize `tailwind.config.js`** para expor os tokens como cores customizadas (`primary-ink`, `surface`, `accent`, etc.).
2. **Substitua `templates/base.html`:** adicione o carregamento das fontes, o CSS com as variáveis (claro e escuro via `[data-theme]`), e o layout sidebar + topbar (pode virar `{% include %}` ou `{% block %}`).
3. **Crie partials:** `_sidebar.html`, `_topbar.html`, `_kpi_card.html`, `_status_pill.html`, `_ai_tag.html`, `_hum_tag.html`, `_pipeline_row.html`.
4. **Atualize cada template** seguindo a lista acima. As views/URLs existentes já cobrem o fluxo — só trocar a camada visual.
5. **Adicione JS mínimo** em `static/js/iomat.js`: theme toggle, density toggle, atalhos de teclado, palette command.

---

## Arquivos de referência

- `preview/index.html` — runner que empilha as 8 telas com toggles de tema/densidade e navegação.
- `preview/variations/tech.jsx` — componentes base: `TechSidebar`, `TechTopbar`, `TechButton`, `TagAI`, `TagHuman`, `TechDashboard`, `TechProgress`, tokens em `techTheme`.
- `preview/variations/tech-screens.jsx` — telas 02, 03, 05, 06, 07, 08.

Abra `preview/index.html` em qualquer browser para ver o design rodando (precisa internet para as fontes/React CDN).

---

## Assets / ícones

Não há assets binários. Todos os ícones são SVG inline ou caracteres unicode (`●`, `○`, `✓`, `◐`, `→`, `←`). Se seu codebase tem uma biblioteca de ícones (Lucide, Heroicons, etc.), é recomendado trocar os unicode por ícones equivalentes em 14–16px stroke 1.5.

## Conteúdo / copy

Todos os números, nomes de usuários (ana.p, carlos.m, bolsa.j) e termos ("tecnólogo", "CEFET", etc.) nos mocks são **exemplos ilustrativos** — virão do backend real.
