#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Busca PRISMA — consulta fontes acadêmicas abertas e exporta registros.

Uso básico (mesma estratégia em todas as fontes):
  python3 busca.py --query "diabetes AND exercise" --sources pubmed,openalex --max 50 --out prisma/busca

Estratégia própria por fonte (arquivo com linhas 'fonte:::estrategia'):
  python3 busca.py --query-file estrategia.txt --out prisma/busca

Fontes disponíveis (APIs públicas, sem chave):
  pubmed, europepmc, openalex, crossref, semanticscholar, doaj, clinicaltrials

Saída em --out:
  registros.csv      registros únicos (duplicatas por DOI ou título removidas)
  resumo-busca.json  datas, estratégias, contagens por fonte, duplicatas —
                     alimenta os itens 6 e 16a do PRISMA 2020 e o fluxograma
"""
import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

UA = "prisma-br-skill/1.0 (uso academico)"
TIMEOUT = 40


def http_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.loads(r.read().decode("utf-8"))


def norm_title(t):
    return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()


def rec(source, id_, title, abstract="", year="", journal="", doi="", url=""):
    return {
        "fonte": source,
        "id": id_ or "",
        "titulo": (title or "").strip(),
        "resumo": (abstract or "").strip(),
        "ano": str(year or ""),
        "revista": journal or "",
        "doi": doi or "",
        "url": url or "",
    }


def _openalex_abstract(w):
    ii = w.get("abstract_inverted_index")
    if not ii:
        return ""
    pos = {}
    for word, idxs in ii.items():
        for i in idxs:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))


def search_pubmed(query, max_n):
    q = urllib.parse.urlencode({"db": "pubmed", "term": query, "retmode": "json", "retmax": min(max_n, 10000)})
    d = http_json("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?" + q)
    r = d.get("esearchresult", {})
    total = int(r.get("count", 0) or 0)
    ids = r.get("idlist", [])[:max_n]
    out = []
    for i in range(0, len(ids), 100):
        batch = ",".join(ids[i:i + 100])
        q2 = urllib.parse.urlencode({"db": "pubmed", "id": batch, "retmode": "json"})
        d2 = http_json("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?" + q2)
        res = d2.get("result", {})
        for k in res.get("uids", []):
            v = res.get(k, {})
            doi = next((a.get("value", "") for a in v.get("articleids", []) if a.get("idtype") == "doi"), "")
            out.append(rec(
                "pubmed", k, v.get("title", ""),
                " ".join(v.get("abstract", [])), (v.get("pubdate", "") or "")[:4],
                v.get("fulljournalname", ""), doi,
                "https://pubmed.ncbi.nlm.nih.gov/%s/" % k,
            ))
        time.sleep(0.4)
    return total, out


def search_europepmc(query, max_n):
    q = urllib.parse.urlencode({"query": query, "format": "json", "pageSize": min(max_n, 1000), "resultType": "core"})
    d = http_json("https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + q)
    total = int(d.get("hitCount", 0) or 0)
    out = []
    for v in d.get("resultList", {}).get("result", []):
        pmid = v.get("pmid", "")
        pmcid = v.get("pmcid", "")
        ident = pmcid or pmid or v.get("id", "")
        out.append(rec(
            "europepmc", ident, v.get("title", ""), v.get("abstractText", ""),
            v.get("pubYear", ""), v.get("journalTitle", ""), v.get("doi", ""),
            "https://europepmc.org/article/%s" % ident,
        ))
    return total, out


def search_openalex(query, max_n):
    out = []
    cursor = "*"
    total = None
    while cursor and len(out) < max_n:
        q = urllib.parse.urlencode({
            "search": query,
            "per-page": min(max(20, max_n - len(out)), 200),
            "cursor": cursor,
        })
        d = http_json("https://api.openalex.org/works?" + q)
        if total is None:
            total = int(d.get("meta", {}).get("count", 0) or 0)
        for w in d.get("results", []):
            src = (w.get("primary_location") or {}).get("source") or {}
            doi = (w.get("doi") or "").replace("https://doi.org/", "")
            out.append(rec(
                "openalex", (w.get("id") or "").rstrip("/").split("/")[-1],
                w.get("title", ""), _openalex_abstract(w), w.get("publication_year", ""),
                src.get("display_name", ""), doi, w.get("id", ""),
            ))
        cursor = d.get("meta", {}).get("next_cursor")
    return total if total is not None else len(out), out


def search_crossref(query, max_n):
    q = urllib.parse.urlencode({"query": query, "rows": min(max_n, 100)})
    d = http_json("https://api.crossref.org/works?" + q)
    m = d.get("message", {})
    total = int(m.get("total-results", 0) or 0)
    out = []
    for it in m.get("items", []):
        doi = it.get("DOI", "")
        title = (it.get("title") or [""])[0]
        ct = it.get("container-title") or []
        year = ""
        for key in ("issued", "created"):
            dp = (it.get(key) or {}).get("date-parts")
            if dp and dp[0] and dp[0][0]:
                year = str(dp[0][0])
                break
        out.append(rec("crossref", doi, title, "", year, ct[0] if ct else "", doi,
                       "https://doi.org/%s" % doi if doi else ""))
    return total, out


def search_s2(query, max_n):
    q = urllib.parse.urlencode({
        "query": query, "limit": min(max_n, 100),
        "fields": "title,abstract,year,externalIds,venue,doi",
    })
    d = http_json("https://api.semanticscholar.org/graph/v1/paper/search?" + q)
    total = int(d.get("total", 0) or 0)
    out = []
    for p in d.get("data", []):
        pid = p.get("paperId", "")
        out.append(rec(
            "semanticscholar", pid, p.get("title", ""), p.get("abstract", ""),
            p.get("year", ""), p.get("venue", ""), (p.get("externalIds") or {}).get("DOI", ""),
            "https://www.semanticscholar.org/paper/%s" % pid,
        ))
    return total, out


def search_doaj(query, max_n):
    q = urllib.parse.urlencode({"pageSize": min(max_n, 100)})
    d = http_json("https://doaj.org/api/search/articles/" + urllib.parse.quote(query) + "?" + q)
    total = int(d.get("total", 0) or 0)
    out = []
    for a in d.get("results", []):
        b = a.get("bibjson", {})
        aid = b.get("id", "")
        out.append(rec(
            "doaj", aid, b.get("title", ""), b.get("abstract", ""), b.get("year", ""),
            (b.get("journal") or {}).get("title", ""), b.get("doi", ""),
            "https://doaj.org/article/%s" % aid,
        ))
    return total, out


def search_ctgov(query, max_n):
    out = []
    total = None
    url = ("https://clinicaltrials.gov/api/v2/studies?query.term=%s&pageSize=%d&format=json"
           % (urllib.parse.quote(query), min(max_n, 100)))
    while url and len(out) < max_n:
        d = http_json(url)
        if d.get("totalCount") is not None:
            total = int(d.get("totalCount") or 0)
        for s in d.get("studies", []):
            proto = s.get("protocolSection", {})
            ident = proto.get("identificationModule", {})
            desc = proto.get("descriptionModule", {})
            nct = ident.get("nctId", "")
            out.append(rec(
                "clinicaltrials", nct, ident.get("briefTitle", ""), desc.get("briefDescription", ""),
                "", "", "", "https://clinicaltrials.gov/study/%s" % nct,
            ))
        page = d.get("nextPageToken")
        if not page:
            break
        url = ("https://clinicaltrials.gov/api/v2/studies?query.term=%s&pageSize=%d&pageToken=%s&format=json"
               % (urllib.parse.quote(query), min(max_n, 100), page))
    if total is None:
        # API não informou total; a paginação rodou até o fim, então recuperados = total
        total = len(out)
    return total, out


SOURCES = {
    "pubmed": search_pubmed,
    "europepmc": search_europepmc,
    "openalex": search_openalex,
    "crossref": search_crossref,
    "semanticscholar": search_s2,
    "doaj": search_doaj,
    "clinicaltrials": search_ctgov,
}


def main():
    ap = argparse.ArgumentParser(
        description="Busca PRISMA — fontes acadêmicas abertas. Saída: registros.csv + resumo-busca.json",
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("--query", help="estratégia padrão (usada por fontes sem estratégia própria no --query-file)")
    ap.add_argument("--query-file", help="arquivo com linhas 'fonte:::estrategia' (uma por fonte)")
    ap.add_argument("--sources", default=",".join(SOURCES), help="fontes separadas por vírgula")
    ap.add_argument("--max", type=int, default=100, dest="max_n", help="máx. de registros por fonte (padrão 100)")
    ap.add_argument("--out", default="prisma/busca", help="pasta de saída (padrão prisma/busca)")
    args = ap.parse_args()

    per = {}
    if args.query_file:
        with open(args.query_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if ":::" not in line:
                    print("linha inválida: %r (esperado fonte:::estrategia)" % line, file=sys.stderr)
                    sys.exit(1)
                src, estr = line.split(":::", 1)
                per[src.strip().lower()] = estr.strip()
    if not args.query and not per:
        print("informe --query ou --query-file", file=sys.stderr)
        sys.exit(1)

    names = [s.strip().lower() for s in args.sources.split(",") if s.strip()]
    for n in names:
        if n not in SOURCES:
            print("fonte desconhecida: %s. disponíveis: %s" % (n, ", ".join(SOURCES)), file=sys.stderr)
            sys.exit(1)

    os.makedirs(args.out, exist_ok=True)
    all_records = []
    resumo = {
        "data": time.strftime("%Y-%m-%d %H:%M:%S %z").strip(),
        "fontes": {},
    }

    for n in names:
        query = per.get(n, args.query)
        try:
            total, recs = SOURCES[n](query, args.max_n)
            resumo["fontes"][n] = {"estrategia": query, "total_disponivel": total, "recuperados": len(recs), "erro": None}
            all_records.extend(recs)
            print("%-16s total=%-8d recuperados=%d" % (n, total, len(recs)))
        except Exception as e:
            resumo["fontes"][n] = {"estrategia": query, "total_disponivel": None, "recuperados": 0,
                                   "erro": "%s: %s" % (type(e).__name__, e)}
            print("%-16s ERRO: %s" % (n, e), file=sys.stderr)
        time.sleep(0.5)

    seen = set()
    unicos = []
    for r in all_records:
        key = r["doi"].lower() if r["doi"] else "t:" + norm_title(r["titulo"])
        if key in seen:
            continue
        seen.add(key)
        unicos.append(r)
    resumo["registros_unicos"] = len(unicos)
    resumo["duplicatas_removidas"] = len(all_records) - len(unicos)

    csv_path = os.path.join(args.out, "registros.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["fonte", "id", "titulo", "resumo", "ano", "revista", "doi", "url"])
        w.writeheader()
        for r in unicos:
            w.writerow(r)
    json_path = os.path.join(args.out, "resumo-busca.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(resumo, f, ensure_ascii=False, indent=2)

    print("\nregistros únicos: %d (duplicatas removidas: %d)" % (len(unicos), resumo["duplicatas_removidas"]))
    print("CSV:   %s" % csv_path)
    print("Resumo: %s" % json_path)
    print("Use resumo-busca.json para os itens 6 (fontes + datas) e 16a (fluxograma) do PRISMA 2020.")


if __name__ == "__main__":
    main()
