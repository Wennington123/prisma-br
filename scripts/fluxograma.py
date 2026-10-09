#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera o PRISMA.csv para o app Shiny "PRISMA 2020 (pt-BR)".

App: https://getmep.shinyapps.io/prisma2020-ptbr/
O app recebe um CSV com as contagens do fluxograma e gera a figura
(PNG/PDF). Este script lê um JSON com as contagens (modelo em
assets/fluxograma-dados.json), CONFERE as somas do fluxograma e exporta o
CSV no formato exato que o app espera (template oficial do app; a única
coluna que muda é a última, "n").

Uso:
  python3 fluxograma.py --dados prisma/fluxograma-dados.json --out prisma/PRISMA.csv

Saída:
  - stdout: resultado da conferência + caminho do CSV
  - exit 1: alguma soma não fecha (erro listado) — corrigir o JSON e reexecutar
"""
import argparse
import csv
import json
import sys

# Linhas do template oficial do app (ordem, rótulos e colunas inalteráveis).
# Último campo: True = linha estrutural (n fixo em 0, igual ao template).
TEMPLATE = [
    ("NA", "node4", "prevstud", "Caixa de título cinza; Estudos prévios", "Estudos prévios", "Caixa de título cinza; Estudos prévios", "prevstud.html", True),
    ("previous_studies", "node5", "box1", "Estudos incluídos em versões anteriores da revisão", "Estudos incluídos em versões anteriores da revisão", "Estudos incluídos em versões anteriores da revisão", "previous_studies.html", False),
    ("previous_reports", "NA", "box1", "Publicações de estudos incluídas em versões anteriores da revisão", "Publicações de estudos incluídas em versões anteriores da revisão", "NA", "previous_reports.html", False),
    ("NA", "node6", "newstud", "Caixa de título amarela; Identificação de novos estudos via bases de dados e repositórios", "Identificação de novos estudos via bases de dados e repositórios", "Caixa de título amarela; Identificação de novos estudos via bases de dados e repositórios", "newstud.html", True),
    ("database_results", "node7", "box2", "Registros identificados de: Bases de dados", "Bases de dados", "Registros identificados de: Bases de dados e Repositórios", "database_results.html", False),
    ("database_specific_results", "NA", "box2", "Registros identificados de: bases de dados específicas", "Bases de dados específicas", "NA", "database_results.html", False),
    ("register_results", "NA", "box2", "Registros identificados de: Repositórios de registros", "Repositórios de registros", "NA", "NA", False),
    ("register_specific_results", "NA", "box2", "Registros identificados de: registros específicos", "Registros específicos", "NA", "database_results.html", False),
    ("NA", "node16", "othstud", "Caixa de título cinza; Identificação de novos estudos por outros métodos", "Identificação de novos estudos por outros métodos", "Caixa de título cinza; Identificação de novos estudos por outros métodos", "othstud.html", True),
    ("website_results", "node17", "box11", "Registros identificados de: Sites", "Sites", "Registros identificados de: Sites, Organizações e Buscas por citações", "website_results.html", False),
    ("organisation_results", "", "box11", "Registros identificados de: Organizações", "Organizações", "NA", "NA", False),
    ("citations_results", "NA", "box11", "Registros identificados de: Buscas por citações", "Buscas por citações", "NA", "NA", False),
    ("duplicates", "node8", "box3", "Registros duplicados", "Registros duplicados", "Registros duplicados", "duplicates.html", False),
    ("excluded_automatic", "NA", "box3", "Registros marcados como inelegíveis por ferramentas de automação", "Registros marcados como inelegíveis por ferramentas de automação", "NA", "NA", False),
    ("excluded_other", "NA", "box3", "Registros removidos por outras razões", "Registros removidos por outras razões", "NA", "NA", False),
    ("records_screened", "node9", "box4", "Registros triados (bases de dados e repositórios)", "Registros triados", "Registros triados (bases de dados e repositórios)", "records_screened.html", False),
    ("records_excluded", "node10", "box5", "Registros excluídos (bases de dados e repositórios)", "Registros excluídos", "Registros excluídos (bases de dados e repositórios)", "records_excluded.html", False),
    ("dbr_sought_reports", "node11", "box6", "Publicações recuperadas (bases de dados e repositórios)", "Publicações recuperadas", "Publicações recuperadas (bases de dados e repositórios)", "dbr_sought_reports.html", False),
    ("dbr_notretrieved_reports", "node12", "box7", "Publicações não recuperadas (bases de dados e repositórios)", "Publicações não recuperadas", "Publicações não recuperadas (bases de dados e repositórios)", "dbr_notretrieved_reports.html", False),
    ("other_sought_reports", "node18", "box12", "Publicações recuperadas (outros métodos)", "Publicações recuperadas", "Publicações recuperadas (outros métodos)", "other_sought_reports.html", False),
    ("other_notretrieved_reports", "node19", "box13", "Publicações não recuperadas (outros métodos)", "Publicações não recuperadas", "Publicações não recuperadas (outros métodos)", "other_notretrieved_reports.html", False),
    ("dbr_assessed", "node13", "box8", "Publicações avaliadas para elegibilidade (bases de dados e repositórios)", "Publicações avaliadas para elegibilidade", "Publicações avaliadas para elegibilidade (bases de dados e repositórios)", "dbr_assessed.html", False),
    ("dbr_excluded", "node14", "box9", "Publicações excluídas (bases de dados e repositórios): [separe as razões e números com ; ex.: Razão 1, xxx; Razão 2, xxx; Razão 3, xxx]", "Publicações excluídas", "Publicações excluídas (bases de dados e repositórios)", "dbrexcludedrecords.html", False),
    ("other_assessed", "node20", "box14", "Publicações avaliadas para elegibilidade (outros métodos)", "Publicações avaliadas para elegibilidade", "Publicações avaliadas para elegibilidade (outros métodos)", "other_assessed.html", False),
    ("other_excluded", "node21", "box15", "Publicações excluídas (outros métodos): [separe as razões e números com ; ex.: Razão 1, xxx; Razão 2, xxx; Razão 3, xxx]", "Publicações excluídas", "Publicações excluídas (outros métodos)", "other_excluded.html", False),
    ("new_studies", "node15", "box10", "Novos estudos incluídos na revisão", "Novos estudos incluídos na revisão", "Novos estudos incluídos na revisão", "new_studies.html", False),
    ("new_reports", "NA", "box10", "Publicações de novos estudos incluídos", "Publicações de novos estudos incluídos", "NA", "NA", False),
    ("total_studies", "node22", "box16", "Total de estudos incluídos na revisão", "Total de estudos incluídos na revisão", "Total de estudos incluídos na revisão", "total_studies.html", False),
    ("total_reports", "NA", "box16", "Publicações do total de estudos incluídos", "Publicações do total de estudos incluídos", "NA", "NA", False),
    ("identification", "node1", "identification", "Caixa azul de identificação", "Identificação", "Caixa azul de identificação", "identification.html", True),
    ("screening", "node2", "screening", "Caixa azul de triagem", "Triagem", "Caixa azul de triagem", "screening.html", True),
    ("included", "node3", "included", "Caixa azul de incluídos", "Incluídos", "Caixa azul de incluídos", "included.html", True),
    ("total_studies_ma", "node23", "box17", "Total de estudos incluídos na meta-análise", "Total de estudos incluídos na meta-análise", "Total de estudos incluídos na meta-análise", "total_studies_meta_analysis.html", False),
    ("total_reports_ma", "NA", "box17", "Publicações do total de estudos incluídos na meta-análise", "Publicações do total de estudos incluídos na meta-análise", "NA", "NA", False),
]

INT_KEYS = [
    "previous_studies", "previous_reports", "database_results", "register_results",
    "website_results", "organisation_results", "citations_results", "duplicates",
    "excluded_automatic", "excluded_other", "records_screened", "records_excluded",
    "dbr_sought_reports", "dbr_notretrieved_reports", "other_sought_reports",
    "other_notretrieved_reports", "dbr_assessed", "other_assessed", "new_studies",
    "new_reports", "total_studies", "total_reports", "total_studies_ma",
    "total_reports_ma",
]
TEXT_KEYS = ["database_specific_results", "register_specific_results"]
REASON_KEYS = ["dbr_excluded", "other_excluded"]


def norm(v):
    if v is None:
        return None
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    if isinstance(v, str) and v.strip() in ("", "NA", "null", "None"):
        return None
    return v


def parse_ints(d, erros):
    ints = {}
    for k in INT_KEYS:
        v = norm(d.get(k))
        if v is None:
            ints[k] = None
            continue
        try:
            ints[k] = int(v)
        except (ValueError, TypeError):
            erros.append("%s: valor não inteiro: %r" % (k, d.get(k)))
            ints[k] = 0
    return ints


def parse_reasons(d, k, erros):
    v = norm(d.get(k))
    if v is None:
        return None, 0
    s = str(v).strip()
    total = 0
    for part in s.split(";"):
        part = part.strip()
        if not part:
            continue
        if "," not in part:
            erros.append("%s: trecho sem contagem (esperado 'Razão, n'): %r" % (k, part))
            return s, total
        n_part = part.rsplit(",", 1)[1].strip()
        try:
            total += int(n_part)
        except ValueError:
            erros.append("%s: número inválido: %r" % (k, part))
            return s, total
    return s, total


def main():
    ap = argparse.ArgumentParser(
        description="Confere as somas do fluxograma PRISMA 2020 e exporta o CSV "
                    "no formato do app Shiny (getmep.shinyapps.io/prisma2020-ptbr).")
    ap.add_argument("--dados", required=True, help="JSON com as contagens (modelo: assets/fluxograma-dados.json)")
    ap.add_argument("--out", required=True, help="caminho do PRISMA.csv a gerar")
    args = ap.parse_args()

    with open(args.dados, encoding="utf-8") as f:
        d = json.load(f)

    # Chaves válidas: modelo assets/fluxograma-dados.json. Chaves com "_" são notas.
    known = set(INT_KEYS) | set(TEXT_KEYS) | set(REASON_KEYS)
    unknown = [k for k in d if not k.startswith("_") and k not in known]
    if unknown:
        print("Chaves não reconhecidas no JSON (use o modelo assets/fluxograma-dados.json): %s"
              % ", ".join(sorted(unknown)), file=sys.stderr)
        sys.exit(1)
    if all(norm(d.get(k)) is None for k in INT_KEYS) and \
       all(norm(d.get(k)) is None for k in REASON_KEYS + TEXT_KEYS):
        print("JSON sem contagens: nenhum campo preenchido (null/vazio = caixa oculta). "
              "Modelo: assets/fluxograma-dados.json", file=sys.stderr)
        sys.exit(1)

    erros = []
    ints = parse_ints(d, erros)
    dbr_excl_txt, dbr_excl_n = parse_reasons(d, "dbr_excluded", erros)
    oth_excl_txt, oth_excl_n = parse_reasons(d, "other_excluded", erros)

    def z(k):
        return ints[k] if ints[k] is not None else 0

    # Conferência de contagens (obrigatória)
    ident = z("database_results") + z("register_results")
    remov = z("duplicates") + z("excluded_automatic") + z("excluded_other")
    cs = z("records_screened")
    if cs or ident or remov:
        if cs != ident - remov:
            erros.append("registros triados (%d) != identificados (%d) - removidos antes da triagem (%d)" % (cs, ident, remov))
    if cs or z("records_excluded") or z("dbr_sought_reports"):
        lado_b = z("records_excluded") + z("dbr_sought_reports") + z("dbr_notretrieved_reports")
        if cs != lado_b:
            erros.append("registros triados (%d) != excluídos (%d) + recuperadas (%d) + não recuperadas (%d)"
                         % (cs, z("records_excluded"), z("dbr_sought_reports"), z("dbr_notretrieved_reports")))
    if z("dbr_sought_reports") and z("dbr_assessed") and z("dbr_sought_reports") != z("dbr_assessed"):
        erros.append("publicações recuperadas dbr (%d) != avaliadas para elegibilidade dbr (%d)"
                     % (z("dbr_sought_reports"), z("dbr_assessed")))
    nova = z("new_studies")
    esperado = (z("dbr_assessed") - dbr_excl_n) + (z("other_assessed") - oth_excl_n)
    if nova or esperado:
        if nova != esperado:
            erros.append("novos estudos (%d) != (avaliadas dbr - excluídas dbr) + (avaliados outros - excluídos outros) (%d)" % (nova, esperado))
    if z("total_studies") and z("total_studies") != z("previous_studies") + z("new_studies"):
        erros.append("total de estudos (%d) != versões anteriores (%d) + novos (%d)"
                     % (z("total_studies"), z("previous_studies"), z("new_studies")))
    if norm(d.get("total_studies_ma")) is not None and z("total_studies_ma") > z("total_studies"):
        erros.append("total da meta-análise (%d) > total incluídos (%d)" % (z("total_studies_ma"), z("total_studies")))

    if erros:
        print("Conferência de contagens FALHOU:", file=sys.stderr)
        for e in erros:
            print(" -", e, file=sys.stderr)
        print("Corrija o JSON e rode de novo.", file=sys.stderr)
        sys.exit(1)

    rows = []
    for data, node, box, desc, boxtext, tooltips, url, fixed in TEMPLATE:
        if fixed:
            n = 0
        elif data in REASON_KEYS:
            txt = dbr_excl_txt if data == "dbr_excluded" else oth_excl_txt
            n = txt if txt is not None else ""
        elif data in TEXT_KEYS:
            v = norm(d.get(data))
            n = str(v).strip() if v is not None else ""
        else:
            v = ints.get(data)
            n = v if v is not None else ""
        rows.append([data, node, box, desc, boxtext, tooltips, url, n])

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["data", "node", "box", "description", "boxtext", "tooltips", "url", "n"])
        w.writerows(rows)

    print("Conferência de contagens: OK")
    print("CSV exportado: %s" % args.out)
    print("Próximo passo: subir este CSV em https://getmep.shinyapps.io/prisma2020-ptbr/ e exportar o fluxograma (PNG/PDF).")


if __name__ == "__main__":
    main()
