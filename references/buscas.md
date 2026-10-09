# Buscas — fontes, estratégias e execução

O PRISMA 2020 exige relatar **todas** as fontes pesquisadas com a data em que cada uma
foi pesquisada pela última vez (item 6) e a **estratégia de busca completa de todas**
as bases, repositórios e sites, incluindo filtros ou limites (item 7). Este módulo
executa as buscas em fontes com API aberta e documenta as fontes bloqueadas para
busca manual.

## Fontes com API aberta (executadas por `scripts/busca.py`)

| Fonte | O que cobre | Observação |
|-------|-------------|------------|
| `pubmed` | MEDLINE (artigos biomédicos; inclui boa parte dos artigos indexados da LILACS) | E-utilities, sem chave (3 req/s) |
| `europepmc` | MEDLINE + PMC + registros | Captura parte da CENTRAL (Cochrane) e literatura cinzenta selecionada |
| `openalex` | ~250M de obras, incl. SciELO, repositórios BR, preprints, dissertações | Principal cobertor de SciELO e produção nacional OA; abstrato via índice invertido |
| `crossref` | Registros com DOI (publicadores) | A maioria das revistas brasileiras (OJS/SEER) registra DOI lá |
| `semanticscholar` | ~200M de artigos, com citações | Rate limit compartilhado sem chave |
| `doaj` | Artigos open access indexados no DOAJ | Bom para capturar periódicos OA fora das bases indexadas |
| `clinicaltrials.gov` | Registros de ensaios clínicos | NCT, título, descrição; sem DOI |

Uso:

```bash
# estratégia única em todas as fontes
python3 scripts/busca.py --query "melatonina AND (câncer OR carcinoma)" --max 100 --out prisma/busca

# estratégia própria por fonte (arquivo estrategia.txt com linhas 'fonte:::estrategia')
python3 scripts/busca.py --query-file estrategia.txt --out prisma/busca
```

Saída: `registros.csv` (registros únicos, deduplicados por DOI ou título) e
`resumo-busca.json` (data de cada consulta, estratégia usada, total disponível,
recuperados, erros, duplicatas removidas). **Esse JSON é a evidência para os itens 6
e 16a** — não reescreva contagens de memória.

## Fontes sem API pública (busca manual pelo usuário)

Nunca rode scraping nem contorne bloqueio de acesso. Para estas fontes, gere a
estratégia adaptada, entregue pronta para colar e peça ao usuário para relatar
resultado e data em `prisma/busca/manual.md`:

| Fonte | Onde buscar | Por quê |
|-------|-------------|---------|
| Scopus | sciencedirect.com/scopus (login institucional) | Sem API pública; coberta em parte por OpenAlex |
| Web of Science | webofscience.com (login institucional) | Sem API pública |
| Embase | embase.com (login) | Essencial para farmacologia; parte sobreposta ao MEDLINE |
| LILACS / BVS | search.lilacs.bvsalud.org | Sem API pública; boa parte dos artigos também no MEDLINE/SciELO — mas se o protocolo prevê LILACS, ela deve ser consultada e relatada (item 6) |
| SciELO | scielo.br (busca) | API oficial só metadados por ID (ArticleMeta) e citações (CitedBy) — sem busca; o conteúdo é captado por `crossref`/`openalex`/`doaj` |
| ReBDc (registro nacional de ensaios) | rbdc.ana.gov.br | Registro oficial BR; parte dos ensaios também no ClinicalTrials.gov |
| Literatura cinzenta BVS | bvsalud.org (relatórios, teses, dados) | Item 6: "outras fontes" |
| Cochrane Central (CENTRAL) | cochranelibrary.com (gratuito para indivíduo) | Sem API pública; parte capturada pela Europe PMC |
| Google Scholar | scholar.google.com | Sem API oficial; útil como "outras fontes" (item 6) |
| Literatura cinzenta | sites governamentais, repositórios institucionais, listas de referências | Item 6: "outras fontes" |

Modelo de `prisma/busca/manual.md`:

```markdown
# Busca manual — [fonte]
- Data da busca: AAAA-MM-DD
- Estratégia completa (exatamente como digitada):
  ...
- Resultados: N registros
- Observações (limites/filtros aplicados):
```

## Contexto brasileiro

- **LILACS x PubMed**: a LILACS tem integração com o MEDLINE — boa parte dos registros
  LILACS aparece no PubMed. Ainda assim, se o protocolo prevê LILACS, pesquise no portal
  e relate como fonte (item 6).
- **Ciência nacional indexada em APIs abertas**: revistas OJS/SEER registram DOI no
  Crossref; o OpenAlex indexa SciELO, repositórios institucionais (USP, UNICAMP,
  UFRJ...) e dissertações. As fontes abertas do script já cobrem grande parte da
  produção nacional — documente essa sobreposição para justificar as fontes
  manuais restantes (evitar busca redundante não dispensa reportar o que o protocolo
  exigiu).
- **Terminologia**: use DeCS (Descritores em Ciências da Saúde, BVS) em PT e o
  correspondente MeSH em EN. O mesmo conceito muda de rótulo entre bases:
  `educação inclusiva` (DeCS) vs. `Inclusive Education[MeSH]`.
- **Exemplo de estratégia PT (LILACS/SciELO)**:
  `(educação inclusiva OR inclusão escolar OR aluno com deficiência[ti]) AND (saúde OR enfermagem) E (2020:2025[dp])`
- **Exemplo de estratégia EN (PubMed)**:
  `("Inclusive Education"[MeSH] OR "inclusive education"[tiab] OR "school inclusion"[tiab]) AND (nursing[tiab] OR "health services"[tiab]) AND 2020/01/01:2025/12/31[dp]`

## Construindo a estratégia

1. Termos do PICO em português e inglês (bases indexam em inglês; LILACS/SciELO aceitam PT).
2. Sinônimos + terminologia controlada. PubMed/Embase: MeSH; Scopus: Emplus; WoS:
   MeSH/Thesaurus; LILACS: DeCS.
3. Operadores: `OR` entre sinônimos, `AND` entre conceitos, `NOT` só com justificativa
   (registrada).
4. Frases entre aspas. Truncagem onde a fonte suportar.
5. O agente **propõe** a estratégia; o usuário **valida** — a estratégia relatada
   (item 7) deve ser a que foi efetivamente executada.

Adaptações de sintaxe:

| Fonte | Sintaxe típica |
|-------|----------------|
| PubMed | `"melatonin"[MeSH] OR melatonin[tiab] AND (cancer[MeSH] OR cancer[tiab])` |
| Scopus | `TITLE-ABS-KEY ( "melatonin" AND ( cancer OR carcinoma ) )` |
| WoS | `TS=(melatonin AND (cancer OR carcinoma))` |
| LILACS/BVS | `melatonina AND (câncer OR carcinoma)` (campos: [t], [ti], [au]...) |
| OpenAlex | texto livre: `melatonin AND cancer` (o script usa `search=`) |
| ClinicalTrials.gov | `query.term=melatonin AND cancer` |

Arquivo de exemplo `prisma/busca/estrategia.txt`:

```
# uma estratégia por fonte; linhas sem 'fonte:::' ignoradas
pubmed:::"melatonin"[MeSH] OR melatonin[tiab] AND (cancer[MeSH] OR carcinoma[tiab])
scielo... (manual — não é fonte do script)
clinicaltrials:::melatonin AND cancer
```

## Regras de contagem para o fluxograma (item 16a)

- **Registros identificados**: soma dos `total_disponivel` das fontes abertas
  (`resumo-busca.json`) + resultados manuais (`manual.md`). Quando possível, reporte
  por base (nota (a) do modelo oficial do fluxograma).
- **Duplicados removidos**: `duplicatas_removidas` do `resumo-busca.json`
  (deduplicação automática por DOI/título).
- **Registros triados**: `registros_unicos`.
- Registros que a API retornou com erro (`"erro"` não nulo): trate como fonte não
  consultada e registre o motivo — não some a fonte.
- Se `--max` truncou uma fonte (recuperados < total), declare no relato o limite
  usado (parte da estratégia completa, item 7).

## Outras opções (fora do script, por decisão)

- **BASE (Bielefeld)**: API aberta (`api.base-search.net`, JSON, sem chave), indexa
  repositórios BR. Bloqueou o IP local em teste — manter como opção manual se
  disponível na rede do usuário (universidade).
- **Epistemonikos**: API gratuita com chave (registro), forte em América Latina.
  Usar como fonte extra se o usuário tiver chave.
- **OAI-PMH / OJS (ex.: `sickle`)**: harvesting por revista conhecida
  (`https://revista.ex.com/oai`). Útil para **monitorar periódicos específicos**
  (revisão viva, atualizações) — não é estratégia de busca sistemática (não há
  busca por termo em todo o universo OJS), então não conta como fonte do item 6
  de revisão nova.
- **API oficial SciELO**: ArticleMeta (metadados por ID/DOI) e CitedBy (citações) —
  útil para enriquecer registros já identificados, não para busca.
- **Google Scholar via scraping/proxies**: rejeitado — contorna bloqueio e viola
  os termos de uso. Google Scholar entra como fonte manual.

## Nota sobre PRISMA-S

O texto do PRISMA 2020 remete, nos itens 6 e 7, à extensão **PRISMA-S** para relato
de buscas em literatura. Se a revista exigir, aplique o checklist PRISMA-S por cima
da estratégia registrada aqui (extensão externa; não altera os 27 itens).
