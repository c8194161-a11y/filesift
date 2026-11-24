# Scholarly search sources and helper

Use these services to discover records and check metadata. A record or abstract is not proof that a source supports a claim; inspect relevant full text when available. Choose sources that fit the discipline and report the providers actually searched. These indexes do not constitute an exhaustive search. For the user's complete requested platform list, access type, and lawful-use boundaries, read [platform-access.md](platform-access.md).

## Provider selection

- **Crossref** is a broad DOI registration metadata source. Search it for publisher-deposited titles, authors, venues, dates, and DOI records. Metadata can be incomplete; Crossref does not establish peer review or claim support.
- **PubMed** is suited to biomedical and life-science literature. The direct PubMed adapter provides bibliographic records and abstracts.
- **Europe PMC** is another biomedical index. It supplies records and abstracts and may provide links to eligible PMC open-access full text. The helper returns those links but does not download full text.
- **DOAJ** indexes open-access journals and articles. It is useful for open-access discovery, not exhaustive coverage of all scholarly literature.
- **Wiley Online Library** supports a public SRU metadata search. Search results and links do not grant access to subscription full text.
- **arXiv** is useful in fields represented by the repository. Its records include preprints; an arXiv result alone does not establish peer review or journal publication.
- Use a scholarly web search, publisher site, repository, library database, or user-provided source files as appropriate when the topic or needed evidence is not well covered by these indexes.

Official documentation:

- [Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/)
- [NCBI E-utilities quick start](https://eutilities.github.io/site/Quick_Start/eu_quick/)
- [PubMed overview](https://pubmed.ncbi.nlm.nih.gov/about/)
- [Europe PMC RESTful API](https://dev.europepmc.org/RestfulWebService)
- [DOAJ API documentation](https://doaj.org/api/v2/docs)
- [Wiley library discovery and SRU](https://onlinelibrary.wiley.com/library-info/resources/discovery)
- [arXiv API User's Manual](https://info.arxiv.org/help/api/user-manual.html)

## Bundled search helper

`scripts/search_literature.py` uses only Python's standard library and makes read-only requests to Crossref, PubMed, Europe PMC, DOAJ, Wiley SRU, and arXiv. It emits JSON containing provider status, query, UTC search time, candidate metadata, abstracts where supplied by the index, and record/full-text links where available. It does not fetch full text, verify peer review, rank study quality, or determine whether a paper supports a claim.

Run it from the skill directory:

```text
python scripts/search_literature.py "your focused search terms" --sources crossref,europepmc,doaj,wiley,arxiv --limit 8
```

Choose only relevant providers. `--sources` accepts any comma-separated subset of `crossref`, `pubmed`, `arxiv`, `doaj`, `europepmc`, and `wiley`; when omitted, it searches Crossref, DOAJ, Europe PMC, Wiley, and arXiv. `--limit` is the maximum candidates requested from each selected provider (1–20). Keep requests modest and obey the providers' usage policies. Network access must be available.

Optional environment variables:

- `CROSSREF_MAILTO`: contact email for Crossref's polite pool.
- `NCBI_EMAIL`: contact email for NCBI E-utilities.
- `NCBI_API_KEY`: user-provided NCBI API key for the user's own rate allowance.

The helper does not require secrets. Never commit API keys or personal email addresses. If a provider fails, its error is included in the JSON; report partial coverage and do not imply the failed source was searched. Some platform APIs in [platform-access.md](platform-access.md) require separate credentials and are not wired into this helper.

## From candidates to usable evidence

1. Deduplicate records by normalized DOI, then normalized title. Treat differing records as a conflict to resolve, not as permission to select whichever metadata looks convenient.
2. Verify every reference used in the draft against the publisher page or DOI registry when possible. Compare title, author list, venue, year, and DOI. A DOI resolving successfully confirms an identifier record, not the accuracy of every citation field or the paper's conclusions.
3. Read the relevant full text for claim support whenever accessible, including open repository copies or user-provided PDFs. If only metadata or an abstract is accessible, label the evidence accordingly and narrow the writing to what that material supports.
4. For central sources, check for corrections, retractions, and version changes when the relevant records are available. Describe the scope of this check accurately.
5. Keep the search log with the draft: provider names, exact query strings, date, and relevant access limitations.
