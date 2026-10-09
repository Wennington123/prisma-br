---
name: prisma-br
description: Relata revisões sistemáticas e meta-análises 100% conforme a Declaração PRISMA 2020 (tradução oficial em português brasileiro, Epidemiologia e Serviços de Saúde 2022;31(2):e2022107). Preenche a lista de checagem de 27 itens, monta o fluxograma PRISMA 2020 com contagens conferidas e audita a conformidade do manuscrito. Use quando o usuário mencionar "revisão sistemática", "meta-análise", "PRISMA", "protocolo de revisão", "fluxograma PRISMA", "checklist PRISMA" ou pedir para relatar, estruturar ou verificar uma revisão sistemática.
argument-hint: "[novo | atualizado | auditar]"
metadata:
  base: "Declaração PRISMA 2020 (pt-BR) — Page MJ et al., Epidemiologia e Serviços de Saúde 2022;31(2):e2022107. https://static1.squarespace.com/static/65b880e13b6ca75573dfe217/t/65bad72a7e897252a200b4f2/1706743595773/PRISMA+2020+statement+BRAZILIAN+PORTUGUESE.pdf"
---

# PRISMA 2020 (pt-BR)

Esta skill conduz o **relato** de uma revisão sistemática 100% conforme a Declaração
PRISMA 2020 em português brasileiro. A declaração original é diretriz de **relato**,
não de condução (o próprio texto afirma: "O PRISMA 2020 não tem como objetivo orientar
a condução de revisões sistemáticas"). Seu papel: garantir que todas as informações
exigidas pelos 27 itens existam e estejam relatadas, e que o fluxograma e a lista de
checagem fiquem prontos.

## Fonte única de referência

Baseie-se exclusivamente nos arquivos desta skill (extratos fiéis do PDF oficial):

- `references/checklist-27.md` — Tabela 1: lista de checagem PRISMA 2020 (27 itens, 7 seções)
- `references/checklist-resumo.md` — Tabela 2: lista de checagem para resumos (12 itens)
- `references/fluxograma.md` — Figura 1: modelo de fluxograma (revisão nova e atualizada) + regras de contagem
- `scripts/fluxograma.py` — confere as somas do fluxograma e exporta `PRISMA.csv` no formato do app Shiny oficial (pt-BR)
- `assets/fluxograma-dados.json` — modelo de contagens para o fluxograma
- `references/buscas.md` — fontes com API aberta vs. bloqueadas, estratégias por fonte, execução e contagens
- `scripts/busca.py` — executa buscas nas fontes abertas; exporta `registros.csv` + `resumo-busca.json`
- `references/glossario.md` — Quadro 1: glossário oficial de termos
- `references/escopo.md` — escopo da diretriz, mudanças vs. PRISMA 2009, como usar, extensões
- `assets/relatorio-modelo.md` — esqueleto do manuscrito organizado pelos 7 itens/seções
- `assets/checklist-preenchivel.md` — checklist de 27 itens com coluna "local onde relatado"

Leia `references/checklist-27.md` no início de qualquer tarefa. Leia os demais arquivos
conforme a fase exigir.

## Divisão de trabalho (IA × humano)

Divisão fixa de papéis nesta skill:

- **IA** (esta skill):
  - Estratégias de busca e execução nas APIs abertas (`busca.py`).
  - **Leitura limitada a título e resumo**: triagem, extração (itens 9–10),
    tabela de características, síntese narrativa, `PRISMA.csv` e os `.md` com o
    texto que o artigo vai usar.
  - **Registro sem resumo = exclusão** na etapa de título/resumo (razão:
    "sem resumo disponível"). A IA não busca texto completo para compensar.
- **Humano** (usuário):
  - Buscas manuais nas fontes bloqueadas (preenche `prisma/busca/manual.md`).
  - Leitura do texto completo (validação da inclusão final, citações completas).
  - Geração do fluxograma: sobe `prisma/PRISMA.csv` no app Shiny oficial e
    exporta a figura.
  - Escrita final do artigo, a partir dos textos dos `.md`.

A IA nunca afirma ter lido texto completo; informação que só existe no texto
completo fica `[PENDENTE — texto completo (humano)]`.

## Triagem (sempre primeiro)

1. Pergunte se falta:
   - **Tipo**: revisão nova ou atualização de revisão prévia (muda o fluxograma).
   - **Estado**: (a) construir relato do zero, (b) relatar revisão já feita, (c) auditar
     manuscrito pronto.
   - **Síntese**: haverá meta-análise ou apenas sumarização/relato narrativo?
   - **Resumo**: o artigo terá resumo (use também `references/checklist-resumo.md`).
2. Se manuscrito pronto para auditar: vá direto para a **Auditoria de conformidade**
   abaixo.
3. Se relato em construção ou revisão em andamento: siga as fases na ordem.
4. Crie a pasta `prisma/` no projeto (ao lado do manuscrito) para guardar os artefatos.

## Fase 1 — Título, introdução (itens 1–4)

- Item 1: título deve identificar a publicação como revisão sistemática (ex.: "Revisão
  sistemática de ...").
- Item 3: justificativa no contexto do que já é conhecido.
- Item 4: afirmação explícita dos objetivos ou questões.
- Registre cada trecho em `assets/checklist-preenchivel.md` com o local no manuscrito.

## Fase 2 — Métodos: elegibilidade, fontes, busca (itens 5–7)

- Item 5: critérios de inclusão/exclusão + como os estudos serão agrupados nas
  sumarizações.
- Item 6: **todas** as fontes (bases de dados, repositórios de registros, sites,
  organizações, listas de referências, outras) + data em que cada fonte foi
  pesquisada/consultada pela última vez.
- Item 7: estratégia de busca **completa para cada** fonte pesquisada, incluindo
  filtros/limites. (Mudança principal vs. PRISMA 2009: não basta uma base.)
- Se a busca ainda não foi feita: liste as fontes e datas que o usuário pretende usar
  e marcar as estratégias como pendentes — nunca invente estratégia de busca.

## Fase 3 — Busca: estratégia e execução (itens 6–7)

Siga `references/buscas.md`.

1. **Estratégia**: do PICO, montar termos (PT + EN), sinônimos e terminologia
   controlada; propor ao usuário e obter validação. A estratégia relatada no item 7
   deve ser a que foi efetivamente executada.
2. **Fontes abertas**: executar `python3 scripts/busca.py` (da pasta da skill) com a
   estratégia, `--out prisma/busca`. Conferir `resumo-busca.json`: datas, totais,
   erros. Fontes com erro valem fonte não consultada, com o motivo registrado.
3. **Fontes bloqueadas** (Scopus, Web of Science, Embase, LILACS/BVS, Cochrane
   Central, Google Scholar): gerar a estratégia adaptada pronta para colar; o
   usuário busca manualmente e preenche `prisma/busca/manual.md` (data + estratégia
   exata + número de resultados). Nunca scraping, nunca contornar bloqueio.
4. As contagens para o fluxograma (item 16a) saem de `resumo-busca.json` +
   `manual.md`, nunca de estimativa.

## Fase 4 — Métodos: seleção, coleta, dados (itens 8–10b)

- Item 8: método de seleção — quantos revisores, se independentes, ferramenta de
  automação (indicar quantos registros foram excluídos por pessoas vs. por automação).
- **Extrair apenas de resumos** (ver Divisão de trabalho): registro sem resumo
  é excluído nesta etapa, com a razão "sem resumo disponível"; o texto completo
  é lido pelo humano.
- Item 9: método de coleta de dados — quantos revisores, se independentes, contato com
  autores, automação.
- Item 10a: listar e definir **todos** os desfechos; se não coletou todos os
  resultados compatíveis, descrever o método de decisão.
- Item 10b: demais variáveis coletadas + pressupostos para dados faltantes.

## Fase 5 — Métodos: risco de viés, efeito, síntese (itens 11–15)

- Item 11: ferramenta(s) de risco de viés (ex.: RoB 2, ROBINS-I), quantos revisores,
  se independentes, automação.
- Item 12: medida(s) de efeito por desfecho (ex.: risco relativo, diferença de médias).
- Item 13a–13f (seis subitens): elegibilidade para cada síntese; preparação de dados
  (faltantes, conversões); tabulação/visualização; método de sumarização com
  justificativa (se meta-análise: modelo, método de heterogeneidade, software);
  causas de heterogeneidade (subgrupo, metarregressão); análises de sensibilidade.
  Sem meta-análise: referir-se à diretriz SWiM (citada no item 13d do PRISMA).
- Item 14: método para vieses de publicação (ex.: funil, Egger).
- Item 15: método de avaliação da certeza no corpo de evidências (ex.: GRADE).

## Fase 6 — Resultados (itens 16a–22)

- Item 16a: resultados do processo de busca e seleção, **idealmente por fluxograma**
  (gerar conforme `references/fluxograma.md`), com contagens de `resumo-busca.json`
  + `prisma/busca/manual.md`.
- Item 16b: citar estudos que pareciam elegíveis mas foram excluídos + motivo.
- Item 17: citar cada estudo incluído + características.
- Item 18: avaliação de risco de viés de cada estudo incluído.
- Item 19: por desfecho e por estudo: estatística sumária por grupo + estimativa de
  efeito com precisão (IC/credibilidade), em tabelas/gráficos estruturados.
- Item 20a–20d: características e risco de viés dos estudos por síntese; resultados de
  **todas** as sumarizações estatísticas (estimativa, precisão, heterogeneidade,
  direção do efeito); resultados das investigações de heterogeneidade; resultados das
  análises de sensibilidade.
- Item 21: avaliação de vieses de publicação por sumarização avaliada.
- Item 22: certeza do corpo de evidências por desfecho avaliado.

## Fase 7 — Discussão e outras informações (itens 23a–27)

- 23a: interpretação geral no contexto de outras evidências.
- 23b: limitações das evidências incluídas.
- 23c: limitações dos processos da revisão.
- 23d: implicações para prática, política e pesquisa.
- 24a: registro (repositório + número, ou declarar que não registrada).
- 24b: onde o protocolo está acessível (ou se não foi preparado).
- 24c: alterações em relação ao registro/protocolo, explicadas.
- 25: fontes de apoio financeiro/não financeiro + papel dos financiadores.
- 26: conflito de interesses dos autores (item novo no 2020).
- 27: disponibilidade pública de formulários, dados extraídos, dados de análise,
  código analítico e outros materiais (item novo no 2020) — e onde encontrar.

## Fase 8 — Fluxograma PRISMA 2020

Siga `references/fluxograma.md`. Caminho principal: CSV para o **app Shiny oficial
(pt-BR)** — https://getmep.shinyapps.io/prisma2020-ptbr/ — de onde sai a figura.

1. Coletar as contagens: `prisma/busca/resumo-busca.json` (fontes abertas),
   `prisma/busca/manual.md` (fontes manuais) e os resultados de triagem/exclusão
   do usuário. Classificar cada fonte: bases de dados e repositórios (ramo
   principal) ou outros métodos (sites, organizações, citações).
2. Copiar `assets/fluxograma-dados.json` para `prisma/fluxograma-dados.json` e
   preencher. `dbr_excluded`/`other_excluded`: "Razão 1, n; Razão 2, n".
3. Executar `python3 scripts/fluxograma.py --dados prisma/fluxograma-dados.json
   --out prisma/PRISMA.csv`. O script confere as somas e só exporta se fechar;
   se faltar, corrigir os dados — nunca pular a conferência.
4. **Humano** (Divisão de trabalho): subir `prisma/PRISMA.csv` no app e
    exportar a figura (PNG/PDF) em `prisma/fluxograma-prisma.png`. A IA entrega o
    CSV conferido; a geração da figura é do humano (automatizar com a skill
    `agent-browser` apenas se o usuário pedir).
5. Alternativa offline (apenas rascunho/preview): template Mermaid de
   `references/fluxograma.md` — não substitui a figura oficial do app.

## Fase 9 — Resumos (se houver)

Aplicar `references/checklist-resumo.md` (12 itens) ao resumo do artigo e/ou
resumo de conferência.

## Fase 10 — Auditoria de conformidade

Passo a passo:

1. Copie `assets/checklist-preenchivel.md` para `prisma/checklist-prisma-2020.md`.
2. Para cada um dos 27 itens: localize a informação no manuscrito e anote a
   localização (seção/página). Marque `OK`, `PENDENTE` (informação ausente) ou `N.A.`
   (subitem genuinamente não aplicável — justifique).
3. Confira o fluxograma: contagens fechadas, variantes certas, caixas não aplicáveis
   removidas.
4. Entregue ao usuário o resumo da auditoria: itens OK / pendentes / N.A., com a lista
   do que falta relatar.

## Regras

- **Nunca invente** contagens, estratégias de busca, dados de estudos ou resultados.
  Informação que não existe vira `[PENDENTE]` no checklist e uma pergunta ao usuário.
- Contagens do fluxograma: fontes abertas de `resumo-busca.json`, fontes manuais de
  `prisma/busca/manual.md`.
- Fontes sem API pública: busca manual pelo usuário; sem scraping, sem contornar
  bloqueio de acesso.
- **Leitura só de resumos**: a IA não lê e não afirma ter lido texto completo;
  registro sem resumo é excluído (razão "sem resumo disponível"). Busca manual,
  texto completo, geração do fluxograma (app Shiny) e escrita final do artigo
  são do humano (ver Divisão de trabalho).
- Texto dos itens: use a redação de `references/checklist-27.md` (tradução oficial),
  sem parafrasear.
- "Publicação" inclui artigo, preprint, resumo de conferência, dados de registro,
  relatório de ensaio, dissertação, manuscrito não publicado, relatório governamental.
- Revisão atualizada/viva: usar fluxograma de atualização e mencionar as
  considerações adicionais (ver `references/escopo.md`).
- Se o tipo de revisão exigir extensão (rede, IPD, harms, acurácia, escopo): relatar
  pelo PRISMA 2020 **+** a extensão correspondente (lista em `references/escopo.md`).
- Revisão de protocolo: PRISMA 2020 não se aplica — direcionar ao usuário para
  PRISMA-P (fora do escopo desta skill).
- Artefatos gerados vão em `prisma/`: `relatorio.md` (a partir de
  `assets/relatorio-modelo.md`), `fluxograma-prisma.md`, `checklist-prisma-2020.md`.
- Respostas e documentos: português brasileiro, terminologia do glossário oficial.

## Exemplo rápido

Usuário: "Tenho o manuscrito da minha revisão sistemática em `revisao.md`, audita."

1. Criar `prisma/`, copiar checklist e modelo.
2. Ler `revisao.md`, mapear cada um dos 27 itens para trechos do manuscrito.
3. Preencher `prisma/fluxograma-dados.json` com as contagens do manuscrito (ou
   `[PENDENTE]` no checklist para o que faltar) e rodar `scripts/fluxograma.py`
   (conferência de somas + `PRISMA.csv`).
4. Entregar: tabela 27 itens (OK/PENDENTE/N.A.) + o que falta + `PRISMA.csv`
   pronto para o app Shiny.
