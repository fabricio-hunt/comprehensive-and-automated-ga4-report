# SPEC — Layout "Relatório SEO & Search" (padrão Bemol)

> Documento de especificação visual para uma IA (ou designer) recriar um relatório mensal no mesmo padrão do "Relatório SEO & Search". Formato de origem: slides 16:9 exportados em PDF (estilo Google Slides), 12 páginas, landscape.

---

## 1. Metadados do documento

| Item | Valor |
|---|---|
| Formato da página | Slide 16:9 landscape |
| Dimensão base | 720 × 405 pt (equivalente a 1280 × 720 px / 1920 × 1080 px em escala) |
| Nº de páginas no exemplo | 12 |
| Margem externa | ~48px topo/laterais, ~40px inferior |
| Ferramenta de origem | Google Slides (exportação em PDF) |

---

## 2. Logo

- **Logo Bemol (varejo):** `https://bemolqa.vtexassets.com/assets/vtex/assets-builder/bemolqa.store-theme/17.0.3-beta.0/images/bemol-logo___0e4ce7bac603e6a725fdc3b40ad03e13.svg`
- **Logo Bemol Farma:** ícone de "coração" bipartido azul/vermelho + wordmark "bemol farma" em vermelho.
- **Posicionamento:**
  - Capa: logos lado a lado, alinhados à esquerda, abaixo do título, com uma linha/régua azul (4px, `#1E6FEB`) acima deles.
  - Páginas de conteúdo: logo específico da unidade (Bemol Varejo ou Bemol Farma) **canto superior direito**, dentro de um badge com borda arredondada fina (pill/rounded rect), ~90×40px.
- **Regra de uso:** cada página de conteúdo carrega o logo da unidade de negócio à qual os dados pertencem (Varejo = logo bemol contorno azul; Farma = logo bemol farma colorido).

---

## 3. Paleta de cores

| Papel | Cor (hex aprox.) | Uso |
|---|---|---|
| Azul primário (marca) | `#1E6FEB` / `#1467D6` | Títulos, links, ícones, linha decorativa, gráficos linha 2026 |
| Azul escuro texto | `#0B3D91` (títulos grandes) | Título principal dos slides |
| Cinza texto corpo | `#3C3C3C` / `#4B5563` | Parágrafos, texto de apoio |
| Cinza claro / neutro | `#9CA3AF` | Labels de KPI, legendas, texto secundário nos cards |
| Fundo de destaque (highlight box) | `#DCE8FC` (azul bem claro) | Caixa "Destaques" e caixas de insight/análise ao final de cada seção |
| Fundo card KPI | `#FFFFFF` com borda `#E5E7EB` | Cards de métricas |
| Fundo página | `#FFFFFF` | Fundo geral dos slides |
| Verde positivo | texto `#15803D`, fundo pill `#DCFCE7` | Variação percentual positiva (▲) |
| Vermelho negativo | texto `#DC2626`, fundo pill `#FEE2E2` | Variação percentual negativa (▼) |
| Vermelho Bemol Farma | `#E4293B` aprox. | Wordmark e ícone da Farma, gauge "baixa visibilidade" |
| Laranja/gauge alerta | `#F5A623` → `#FDBA5C` (gradiente) | Medidor "Visibilidade na IA" quando baixo |
| Roxo/lilás (gauge médio) | `#7B7FE0` gradiente para azul | Medidor "Visibilidade na IA" quando médio/alto |

**Regra de contraste:** blocos de destaque sempre em azul claro sólido (não gradiente), com texto cinza-escuro/preto, palavras-chave em **negrito preto**.

---

## 4. Tipografia

- **Fonte:** **Nunito** (Google Font, geometric rounded sans-serif) — variantes usadas: `Nunito Regular` e `Nunito Bold`.
- Combina com o logotipo Bemol (também rounded sans).

| Elemento | Peso | Tamanho aprox. | Cor |
|---|---|---|---|
| Título do slide (H1, ex. "Performance Orgânica → Web") | Bold | 32–40px | Azul primário `#1E6FEB` |
| Subtítulo de capa ("Maio / 2026") | Bold | 24px | Azul primário |
| Label de unidade (capa: "Bemol Varejo · Bemol Farma · App Bemol") | Regular | 14px | Azul primário claro |
| Texto de introdução/parágrafo | Regular | 14–16px | Cinza `#3C3C3C` |
| Valor numérico do KPI (ex. "275.529") | Bold | 28–32px | Preto/cinza-escuro `#111827` |
| Label do KPI (ex. "SESSÕES ORGÂNICAS") | Bold, letter-spacing ampliado, uppercase | 10–11px | Cinza `#6B7280` |
| Variação percentual (badge) | Bold | 11–12px | Verde ou vermelho (ver paleta) |
| Texto dentro de highlight box | Regular, trechos-chave em Bold preto | 13–15px | Cinza-escuro |
| Legendas de gráfico / eixo | Regular | 10–11px | Cinza claro |

---

## 5. Grid e estrutura por tipo de slide

### 5.1 Capa (slide 1)
- Fundo branco.
- Bloco de texto alinhado à esquerda, centralizado verticalmente, ocupando ~55% da largura.
- Título grande (H1) em duas linhas possíveis: "Relatório SEO & Search".
- Subtítulo abaixo: mês/ano em destaque azul.
- Linha fina de "tags" com os nomes das frentes (Varejo · Farma · App), separadas por "·".
- Régua horizontal azul (4px) logo abaixo do bloco de texto.
- Logos (Bemol + Bemol Farma) abaixo da régua, lado a lado.
- Ilustração/artwork temático de e-commerce (compras, SEO, gráficos) ocupando a metade direita do slide, estilo flat/vetor colorido em tons de azul.

### 5.2 Slide "Visão Geral" (resumo executivo)
- Título H1 no topo esquerdo.
- Parágrafo de abertura em negrito parcial (frase-chave em bold, resto regular), largura total.
- Caixa "Destaques" (highlight box azul claro, cantos arredondados ~16px, padding generoso ~32px):
  - Ícone de estrela ⭐ + palavra "Destaques:" em bold.
  - Lista de bullets (•), cada um com números/percentuais em **negrito**, texto de apoio em regular.
  - Espaçamento vertical confortável entre bullets (~16px).

### 5.3 Slides de KPIs ("Performance Orgânica", "Performance orgânica → Farma")
- Título H1 + badge de logo da unidade no canto superior direito.
- Subtítulo pequeno cinza: período de comparação (ex. "mai/26 vs mai/25 · vs abr/26").
- **Grid de 4 cards de KPI em 2 colunas × 2 linhas**, cada card:
  - Fundo branco, borda cinza clara 1px, cantos arredondados (~12px), padding interno ~20px.
  - Label uppercase cinza no topo.
  - Valor numérico grande em bold.
  - Duas linhas de comparação (YoY e MoM), cada uma com: rótulo cinza pequeno + valor de referência + badge pill colorido (verde/vermelho) com seta ▲/▼ e percentual, alinhado à direita do card.
- Caixa de insight (highlight box azul claro) full-width abaixo dos cards, com texto analítico e trechos-chave em bold.

### 5.4 Slides de gráfico duplo ("Evolução de Sessões" / "Evolução da Receita Orgânica")
- Título H1 no topo.
- **Duas colunas lado a lado**, cada uma com:
  - Mini-título do gráfico (bold, preto, 14px) + subtítulo "2026 vs 2025" (cinza).
  - Gráfico (barras ou linha) comparando série do ano atual (azul sólido) vs ano anterior (cinza claro).
  - Caixa de insight azul claro abaixo do gráfico, com texto curto de análise.
- Para gráficos de linha: 2025 em cinza claro tracejado/fino, 2026 em azul sólido mais grosso, com marcador circular nos pontos.
- Para comparação MoM/YoY pontual: dois cartões pequenos lado a lado (mês ano anterior vs mês atual) com badge de variação percentual.

### 5.5 Slide "Orgânico vs. Total"
- Duas colunas:
  - Esquerda: **gráfico de rosca (donut)** mostrando % de participação do orgânico na receita total, com número grande no centro (ex. "20,2%"), legenda lateral com valores em R$; abaixo, gráfico de barras comparando "Receita por Sessão" (Orgânico vs Total).
  - Direita: gráfico de linha "Evolução Comparativa de Receita" com duas séries (linha sólida azul = orgânico, linha tracejada cinza = total), eixo indexado (Base 100).
- Caixas de insight azul claro abaixo de cada coluna.

### 5.6 Slide "Visibilidade – Busca & IA"
- Duas colunas:
  - Esquerda: 3 mini-KPIs em linha (impressões orgânicas, posição média, CTR) + gráfico de linha de evolução mensal (série única azul).
  - Direita: **gauge/medidor semicircular** ("Visibilidade na IA") com score de 0–100 e rótulo (ex. "60/100 Média" ou "27/100 Baixa"), cor do arco variando de laranja (baixo) a azul/roxo (alto); abaixo do gauge, 3 métricas em linha (Menções, Citações, Páginas citadas) cada uma com ícone "i" de tooltip e badge de variação; e um gráfico de linhas múltiplas (3 séries coloridas: roxo, verde, lilás) mostrando evolução mensal dessas 3 métricas.
- Caixas de insight azul claro abaixo de cada coluna.

### 5.7 Slide "Top Páginas / Top Consultas"
- Duas colunas com tabelas simples:
  - Card com KPI isolado no topo ("Palavras-chave ativas").
  - Tabela "Top Páginas": colunas Página | Impressões | Tipo (badge colorido pill: categoria=azul claro, produto=lilás claro, home=preto).
  - Tabela "Top Consultas (sem marca)": lista simples com bullet, nome da consulta à esquerda, número de impressões alinhado à direita, formatação tabular sem bordas pesadas, apenas linha divisória cinza clara entre header e conteúdo.
- Caixas de insight abaixo de cada tabela.

### 5.8 Slide "App Bemol" (card único + gráfico)
- Layout assimétrico: bloco de 4 KPIs em grid 2×2 à esquerda (menor, mais compacto, dentro de um card outline arredondado) + gráfico de linha de evolução à esquerda-baixo; texto de insight em bloco azul claro à direita ocupando ~35% da largura, altura total.
- KPI "Share Orgânico" usa um pequeno **donut/gauge miniatura** ao lado do número.

### 5.9 Rodapé (todas as páginas de conteúdo, exceto capa)
- Última página apenas: rodapé centralizado cinza claro — "Relatório SEO & Search · Maio / 2026 · Bemol".

---

## 6. Componentes reutilizáveis (definição para Design System / código)

### 6.1 KPI Card
```
- background: #FFFFFF
- border: 1px solid #E5E7EB
- border-radius: 12px
- padding: 20px 24px
- label: uppercase, 10-11px, bold, letter-spacing 0.05em, color #6B7280
- value: 28-32px, bold, color #111827
- comparison row: flex space-between
  - left: "YOY · VS MAI/25" (10px cinza) + valor referência (12px cinza)
  - right: badge pill (seta + %), bg verde #DCFCE7/texto #15803D OU bg vermelho #FEE2E2/texto #DC2626
```

### 6.2 Highlight / Insight Box
```
- background: #DCE8FC
- border-radius: 16-20px
- padding: 24-32px
- text: 13-15px, color #374151, regular
- trechos-chave: bold, color #111827 ou #000000
- bullets com marcador "•" e espaçamento vertical 12-16px (quando lista)
```

### 6.3 Badge/Pill de variação
```
- shape: pill (border-radius 999px)
- padding: 2px 10px
- font: bold, 11-12px
- positivo: bg #DCFCE7, texto #15803D, prefixo "▲" ou "↑"
- negativo: bg #FEE2E2, texto #DC2626, prefixo "▼" ou "↓"
```

### 6.4 Badge de tipo (tabela Top Páginas)
```
- shape: pill pequena
- categoria: bg azul claro #DCE8FC, texto azul #1E6FEB
- produto: bg lilás claro #EDE9FE, texto roxo #7C3AED
- home: bg preto #111827, texto branco
```

### 6.5 Gauge semicircular (Visibilidade na IA)
```
- semicírculo 180°, espessura de traço ~14-18px
- track de fundo: cinza claro #F3F4F6
- arco preenchido proporcional ao score (0-100)
- cor do arco: gradiente laranja (#F5A623) quando baixo → azul/roxo (#7B7FE0 → #1E6FEB) quando alto
- número central grande (bold, 28px) + label "/100" + rótulo textual abaixo ("Baixa"/"Média"/"Alta")
```

### 6.6 Gráfico de linha comparativo (ano atual vs anterior)
```
- eixo Y com gridlines horizontais finas cinza claro
- série ano anterior: linha cinza clara, mais fina, sem marcador ou marcador discreto
- série ano atual: linha azul #1E6FEB, mais grossa (2-3px), marcadores circulares preenchidos nos pontos com dado
- legenda no topo do gráfico (linha colorida + label do ano)
```

### 6.7 Gráfico de barras comparativo (mês a mês, ano vs ano)
```
- barras pareadas por mês (ano anterior = cinza claro, ano atual = azul)
- valor numérico no topo de cada barra do ano atual (bold, rotacionado se necessário)
- sem bordas nas barras, cantos levemente arredondados no topo (opcional)
```

---

## 7. Tom de voz do texto analítico

- Frases curtas e diretas, começando por uma afirmação-síntese em **negrito**.
- Sempre contextualiza a variação (MoM e YoY) e conecta o número a uma interpretação de negócio (ex.: "reforçando a recuperação da performance orgânica").
- Evita jargão técnico excessivo; usa vocabulário de marketing/SEO (sessões, engajamento, orgânico, receita, visibilidade).

---

## 8. Prompt-resumo para geração automática (uso em IA)

> "Gere um slide 16:9 (1920×1080), fundo branco, fonte Nunito. Título em azul #1E6FEB, bold, 36px, canto superior esquerdo, com badge de logo da unidade de negócio no canto superior direito (borda arredondada). Corpo com grid de cards KPI (fundo branco, borda #E5E7EB, radius 12px) mostrando valor grande em bold + badges de variação percentual verde/vermelho em formato pill. Abaixo, uma caixa de insight com fundo azul claro #DCE8FC, radius 16px, padding 24px, contendo texto analítico com trechos em negrito. Gráficos (linha ou barra) comparando ano atual (azul #1E6FEB) vs ano anterior (cinza claro), com legendas discretas."

---

## 9. Assets necessários

- Logo Bemol (SVG): `https://bemolqa.vtexassets.com/assets/vtex/assets-builder/bemolqa.store-theme/17.0.3-beta.0/images/bemol-logo___0e4ce7bac603e6a725fdc3b40ad03e13.svg`
- Logo Bemol Farma (coletar SVG/PNG oficial equivalente do VTEX Farma, mesmo padrão de asset builder).
- Fonte Nunito (Google Fonts, pesos 400 e 700): `https://fonts.google.com/specimen/Nunito`
- Ilustração de capa: artwork flat/vetor tema e-commerce/SEO em tons de azul (pode ser gerado ou licenciado separadamente).