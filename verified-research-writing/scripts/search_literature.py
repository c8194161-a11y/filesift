#!/usr/bin/env python3
"""Search public scholarly indexes and emit candidate records as JSON.

This helper discovers metadata and abstracts only. It does not retrieve full
text, verify a paper's conclusions, or assess study quality.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import Any


USER_AGENT = "verified-research-writing-skill/1.0 (scholarly metadata search)"
ARXIV_NS = {"atom": "http://www.w3.org/2005/Atom"}


def fetch(url: str, *, params: dict[str, str] | None = None) -> bytes:
    if params:
        separator = "&" if "?" in url else "?"
        url = f"{url}{separator}{urllib.parse.urlencode(params)}"
    headers = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=25) as response:
        return response.read()


def clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = re.sub(r"<[^>]+>", " ", value)
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def first(values: list[str]) -> str | None:
    for value in values:
        cleaned = clean_text(value)
        if cleaned:
            return cleaned
    return None


def author_name(author: dict[str, Any]) -> str | None:
    given = author.get("given", "")
    family = author.get("family", "")
    name = " ".join(part for part in (given, family) if part).strip()
    return name or author.get("name")


def crossref_search(query: str, limit: int) -> list[dict[str, Any]]:
    params = {"query.bibliographic": query, "rows": str(limit)}
    mailto = os.environ.get("CROSSREF_MAILTO")
    if mailto:
        params["mailto"] = mailto
    payload = json.loads(fetch("https://api.crossref.org/works", params=params))
    items = payload.get("message", {}).get("items", [])
    records = []
    for item in items:
        authors = [name for author in item.get("author", []) if (name := author_name(author))]
        date_parts = (
            item.get("published-print", {}).get("date-parts")
            or item.get("published-online", {}).get("date-parts")
            or item.get("issued", {}).get("date-parts")
            or []
        )
        year = date_parts[0][0] if date_parts and date_parts[0] else None
        doi = item.get("DOI")
        records.append(
            {
                "provider": "Crossref",
                "title": first(item.get("title", [])),
                "authors": authors,
                "year": year,
                "venue": first(item.get("container-title", [])),
                "doi": doi,
                "url": item.get("URL") or (f"https://doi.org/{doi}" if doi else None),
                "abstract": clean_text(item.get("abstract")),
                "record_type": item.get("type"),
            }
        )
    return records


def pubmed_search(query: str, limit: int) -> list[dict[str, Any]]:
    search_params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": str(limit),
        "tool": "verified_research_writing",
    }
    email = os.environ.get("NCBI_EMAIL")
    api_key = os.environ.get("NCBI_API_KEY")
    if email:
        search_params["email"] = email
    if api_key:
        search_params["api_key"] = api_key
    search_data = json.loads(
        fetch("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi", params=search_params)
    )
    ids = search_data.get("esearchresult", {}).get("idlist", [])
    if not ids:
        return []

    summary_params = {
        "db": "pubmed",
        "id": ",".join(ids),
        "retmode": "xml",
        "tool": "verified_research_writing",
    }
    if email:
        summary_params["email"] = email
    if api_key:
        summary_params["api_key"] = api_key
    root = ET.fromstring(
        fetch("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi", params=summary_params)
    )
    records = []
    for article in root.findall(".//PubmedArticle"):
        pmid = article.findtext(".//PMID")
        title = first(
            ["".join(article.find(".//ArticleTitle").itertext())]
            if article.find(".//ArticleTitle") is not None
            else []
        )
        authors = []
        for author in article.findall(".//AuthorList/Author"):
            collective = author.findtext("CollectiveName")
            given = author.findtext("ForeName") or author.findtext("Initials") or ""
            family = author.findtext("LastName") or ""
            name = collective or " ".join(part for part in (given, family) if part).strip()
            if name:
                authors.append(name)
        year = first([element.text or "" for element in article.findall(".//PubDate/Year")])
        if year is None:
            medline_date = first(
                [element.text or "" for element in article.findall(".//PubDate/MedlineDate")]
            )
            match = re.search(r"\b(?:19|20)\d{2}\b", medline_date or "")
            year = match.group(0) if match else None
        venue = first([article.findtext(".//Journal/Title") or ""])
        doi = None
        for article_id in article.findall(".//ArticleId"):
            if article_id.attrib.get("IdType", "").lower() == "doi":
                doi = clean_text(article_id.text)
                break
        abstract_parts = []
        for part in article.findall(".//Abstract/AbstractText"):
            label = part.attrib.get("Label")
            text = clean_text("".join(part.itertext()))
            if text:
                abstract_parts.append(f"{label}: {text}" if label else text)
        records.append(
            {
                "provider": "PubMed",
                "title": title,
                "authors": authors,
                "year": year,
                "venue": venue,
                "doi": doi,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else None,
                "abstract": " ".join(abstract_parts) or None,
                "record_type": "indexed article record",
            }
        )
    return records


def arxiv_search(query: str, limit: int) -> list[dict[str, Any]]:
    phrase = query.replace('"', " ").strip()
    search_term = f'all:"{phrase}"'
    payload = fetch(
        "https://export.arxiv.org/api/query",
        params={
            "search_query": search_term,
            "start": "0",
            "max_results": str(limit),
            "sortBy": "relevance",
            "sortOrder": "descending",
        },
    )
    root = ET.fromstring(payload)
    records = []
    for entry in root.findall("atom:entry", ARXIV_NS):
        authors = [
            author.findtext("atom:name", namespaces=ARXIV_NS)
            for author in entry.findall("atom:author", ARXIV_NS)
        ]
        published = entry.findtext("atom:published", namespaces=ARXIV_NS) or ""
        title = clean_text(entry.findtext("atom:title", namespaces=ARXIV_NS))
        summary = clean_text(entry.findtext("atom:summary", namespaces=ARXIV_NS))
        record_id = entry.findtext("atom:id", namespaces=ARXIV_NS)
        arxiv_id = record_id.rsplit("/", 1)[-1] if record_id else None
        doi = entry.findtext("arxiv:doi", namespaces={"arxiv": "http://arxiv.org/schemas/atom"})
        records.append(
            {
                "provider": "arXiv",
                "title": title,
                "authors": [name for name in authors if name],
                "year": published[:4] or None,
                "venue": "arXiv preprint",
                "doi": doi,
                "url": f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else None,
                "abstract": summary,
                "record_type": "preprint repository record",
            }
        )
    return records


def europe_pmc_search(query: str, limit: int) -> list[dict[str, Any]]:
    payload = json.loads(
        fetch(
            "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
            params={
                "query": query,
                "format": "json",
                "pageSize": str(limit),
                "resultType": "core",
            },
        )
    )
    records = []
    for item in payload.get("resultList", {}).get("result", []):
        pmid = item.get("pmid")
        pmcid = item.get("pmcid")
        doi = item.get("doi")
        full_text_urls = [
            link.get("url")
            for link in item.get("fullTextUrlList", {}).get("fullTextUrl", [])
            if link.get("url")
        ]
        record_url = (
            f"https://europepmc.org/articles/{pmcid}"
            if pmcid
            else (f"https://europepmc.org/article/MED/{pmid}" if pmid else None)
        )
        records.append(
            {
                "provider": "Europe PMC",
                "title": clean_text(item.get("title")),
                "authors": [
                    author.strip()
                    for author in (item.get("authorString") or "").split(",")
                    if author.strip()
                ],
                "year": (item.get("firstPublicationDate") or item.get("pubYear") or "")[:4] or None,
                "venue": clean_text(item.get("journalTitle")),
                "doi": doi,
                "pmid": pmid,
                "pmcid": pmcid,
                "url": record_url,
                "full_text_urls": full_text_urls,
                "open_access": item.get("isOpenAccess") == "Y",
                "abstract": clean_text(item.get("abstractText")),
                "record_type": item.get("pubType") or "biomedical index record",
            }
        )
    return records


def doaj_search(query: str, limit: int) -> list[dict[str, Any]]:
    encoded_query = urllib.parse.quote(query, safe="")
    payload = json.loads(
        fetch(f"https://doaj.org/api/v2/search/articles/{encoded_query}?pageSize={limit}")
    )
    records = []
    for item in payload.get("results", []):
        bib = item.get("bibjson", {})
        identifiers = bib.get("identifier", [])
        doi = next(
            (
                identifier.get("id")
                for identifier in identifiers
                if identifier.get("type", "").lower() == "doi"
            ),
            None,
        )
        journal = bib.get("journal", {})
        links = bib.get("link", [])
        url = next(
            (link.get("url") for link in links if link.get("type") == "fulltext"),
            None,
        )
        if not url:
            url = f"https://doi.org/{doi}" if doi else None
        records.append(
            {
                "provider": "DOAJ",
                "title": clean_text(bib.get("title")),
                "authors": [
                    author.get("name", "").strip()
                    for author in bib.get("author", [])
                    if author.get("name", "").strip()
                ],
                "year": bib.get("year"),
                "venue": clean_text(journal.get("title")),
                "doi": doi,
                "url": url,
                "abstract": clean_text(bib.get("abstract")),
                "record_type": "open-access journal article index record",
            }
        )
    return records


def wiley_search(query: str, limit: int) -> list[dict[str, Any]]:
    escaped = query.replace("\\", "\\\\").replace('"', '\\"')
    cql_query = f'cql.anywhere="{escaped}"'
    payload = fetch(
        "https://onlinelibrary.wiley.com/action/sru",
        params={
            "query": cql_query,
            "maximumRecords": str(limit),
            "facetLimit": "0",
        },
    )
    root = ET.fromstring(payload)
    records = []
    for record_data in root.iter():
        if record_data.tag.rsplit("}", 1)[-1] != "recordData":
            continue
        fields: dict[str, list[str]] = {}
        for child in record_data.iter():
            name = child.tag.rsplit("}", 1)[-1]
            if child is record_data:
                continue
            value = clean_text("".join(child.itertext()))
            if value:
                fields.setdefault(name, []).append(value)
        title = first(fields.get("title", []))
        if not title:
            continue
        identifier = first(fields.get("identifier", []))
        doi = identifier if identifier and identifier.lower().startswith("10.") else None
        url = first(fields.get("url", []))
        if not url and doi:
            url = f"https://doi.org/{doi}"
        date = first(fields.get("date", []))
        year_match = re.search(r"\b(?:19|20)\d{2}\b", date or "")
        records.append(
            {
                "provider": "Wiley Online Library",
                "title": title,
                "authors": fields.get("contributor", []),
                "year": year_match.group(0) if year_match else date,
                "venue": first(fields.get("isPartOf", [])),
                "doi": doi,
                "url": url,
                "abstract": first(fields.get("description", [])),
                "record_type": "publisher search metadata",
            }
        )
    return records


PROVIDERS = {
    "crossref": crossref_search,
    "pubmed": pubmed_search,
    "arxiv": arxiv_search,
    "doaj": doaj_search,
    "europepmc": europe_pmc_search,
    "wiley": wiley_search,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Search scholarly indexes for candidate records and abstracts."
    )
    parser.add_argument("query", help="Focused search query")
    parser.add_argument(
        "--sources",
        default="crossref,doaj,europepmc,wiley,arxiv",
        help="Comma-separated subset of crossref,pubmed,arxiv,doaj,europepmc,wiley",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=8,
        help="Maximum records per provider, from 1 to 20 (default: 8)",
    )
    args = parser.parse_args()
    args.query = args.query.strip()
    if not args.query:
        parser.error("query must not be empty")
    if not 1 <= args.limit <= 20:
        parser.error("--limit must be between 1 and 20")
    selected = [source.strip().lower() for source in args.sources.split(",") if source.strip()]
    unknown = sorted(set(selected) - set(PROVIDERS))
    if unknown:
        parser.error(f"unknown source(s): {', '.join(unknown)}")
    args.sources = list(dict.fromkeys(selected))
    if not args.sources:
        parser.error("select at least one source")
    return args


def main() -> int:
    args = parse_args()
    result: dict[str, Any] = {
        "query": args.query,
        "searched_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "providers": {},
        "records": [],
        "limitations": [
            "Search results are candidate index records, not a complete literature search.",
            "Metadata and abstracts do not substitute for reading full text to verify claim support.",
            "An arXiv record is a preprint record; peer review or later publication was not checked.",
            "Europe PMC may link to open-access full text for eligible records; linked full text was not fetched by this helper.",
            "DOAJ indexes open-access journals and is not a comprehensive index of all scholarly literature.",
            "Wiley SRU returns publisher metadata and links; full-text access depends on lawful user or institutional entitlement.",
        ],
    }
    for index, name in enumerate(args.sources):
        if index:
            time.sleep(0.4)
        try:
            records = PROVIDERS[name](args.query, args.limit)
            result["providers"][name] = {"status": "ok", "record_count": len(records)}
            result["records"].extend(records)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ET.ParseError, ValueError) as exc:
            result["providers"][name] = {
                "status": "error",
                "message": f"{type(exc).__name__}: {exc}",
                "record_count": 0,
            }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not any(provider["status"] == "ok" for provider in result["providers"].values()):
        return 1
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.stderr.write("Search cancelled.\n")
        sys.exit(130)
