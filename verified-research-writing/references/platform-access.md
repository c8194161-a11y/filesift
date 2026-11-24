# Platform access guide

This guide distinguishes direct programmatic search from opening a platform's web interface. A site being listed here does not mean the helper can query its complete catalogue or retrieve its full text. The bundled helper currently has direct adapters for Crossref, PubMed, Europe PMC, DOAJ, Wiley SRU, and arXiv. Search and access policies can change; check the official platform documentation before adding an adapter.

## Directly searched by the bundled helper

| Platform | Current integration | Access and evidence limits |
|---|---|---|
| PubMed | NCBI E-utilities API | Returns citation records and abstracts where indexed; not a general full-text service. |
| PMC | Europe PMC search results may link to eligible PMC full text | Coverage and full text depend on the record and rights; helper returns links but does not fetch full text. |
| DOAJ | Public article-search API | Open-access journal/article discovery; not comprehensive across all scholarly literature. |
| arXiv | Public Atom API | Preprint records; peer review or later journal publication must be checked separately. |
| Wiley Online Library | Wiley SRU/federated discovery API | Metadata discovery; subscription full text still requires lawful entitlement. |
| medRxiv / bioRxiv | Some records may be discoverable through Europe PMC | The repositories' official API is organized around DOI or date-range lookups rather than a broad keyword-search endpoint; use Europe PMC or their web search for topic discovery and verify repository status. |

Crossref is also directly searched as a DOI metadata registry, though it was not in the user's platform list.

## Authorized API available, but not wired into this helper

These services have documented or institution-specific APIs, but a working connection requires the user's own eligible account, subscription, key, contract, or approved API application. Do not place credentials in this repository. Add an adapter only after the user supplies authorized access details and the service terms permit the intended use.

| Platform | Current status | Official documentation |
|---|---|---|
| Wanfang Data | Official API documented; requires account-created AppKey/secret and may expose only the licensed corpus/functions | [Wanfang API](https://open.wf.pub/docs/JSAPI) |
| Web of Science | Starter API requires application registration and an API key; richer records and citation features depend on the applicable plan/entitlement | [Clarivate Web of Science Starter API](https://developer.clarivate.com/apis/wos-starter) |
| ScienceDirect | API key plus verified eligibility/entitlement; an API key or article OA status alone does not grant API access | [ScienceDirect API access](https://dev.elsevier.com/sciencedirect.html) |
| SpringerLink / Springer Nature | Metadata API requires an API key; full-text APIs have separate access terms | [Springer Nature Metadata API](https://dev.springernature.com/docs/api-endpoints/meta-api/) |
| IEEE Xplore | API key and approval/account requirements apply; scope is governed by IEEE terms | [IEEE Xplore API setup](https://developer.ieee.org/getting_started) |
| JSTOR | Metadata/TDM integrations are controlled and may require institutional participation or agreement | [JSTOR bibliographic metadata access](https://support.jstor.org/hc/en-us/articles/32485272590487-JSTOR-Text-Analysis-Support-Working-with-JSTOR-Bibliographic-Metadata) |
| Derwent Innovation | Clarivate exposes a no-auth GET GraphQL endpoint in its developer portal, but its public docs do not establish that it provides unrestricted Derwent search. Treat searchable patent data as licensed unless the endpoint and terms confirm the user's entitlement. Not wired into this helper. | [Clarivate developer portal](https://developer.clarivate.com/apis) |

## Search through the official site when the user has access

The bundled helper does not query or scrape these interfaces. If the host provides interactive browser/computer-use tools, the AI can search the official portal through the user's already authorized session. If those tools are unavailable, offer a ready-to-run query and ask the user to search manually and provide permitted records or notes. If login, institutional access, or a CAPTCHA is needed, ask the user to perform that step; do not request their password, bypass the control, or claim the search continued while blocked.

| Platform | Portal | Notes |
|---|---|---|
| CNKI | [CNKI](https://www.cnki.net/) | Browser-assisted search is possible when the host has interactive browser control and the user is authenticated. No CNKI API is wired into the helper; institutional or account access applies to subscribed content. |
| VIP / CQVIP | [VIP](https://www.cqvip.com/) | Web search; no general public API is wired here. |
| Duxiu | [Duxiu](https://www.duxiu.com/) | Library/account access may be required. |
| Chaoxing Huiya | [Chaoxing](https://www.chaoxing.com/) | Search/catalog access varies by institution. |
| CSSCI | [CSSCI](https://cssci.nju.edu.cn/) | Citation/source index; access is provided through the official or licensed institutional service. |
| CSCD | [CSCD](https://www.sciencechina.cn/) | Citation/source index; use its official search service or library access. |
| ChinaXiv | [ChinaXiv](https://www.chinaxiv.org/) | Public preprint search/reading; treat records as preprints unless publication is separately verified. |
| Google Scholar | [Google Scholar](https://scholar.google.com/) | Manual/browser search only in this workflow; do not scrape or use third-party scraping APIs. |
| GoOA | [GoOA](https://gooa.las.ac.cn/) | Open-access discovery portal; no supported search API is wired here. |
| ACM Digital Library | [ACM Digital Library](https://dl.acm.org/) | Use the web interface or an authorized institutional service; no general public search API is wired here. |
| CNIPA patent search | [CNIPA Patent Search and Analysis](https://pss-system.cponline.cnipa.gov.cn/) | Public web search may require registration; no general public query API is wired here. |
| CNKI patents | [CNKI](https://www.cnki.net/) | Same account/institution and interface limitations as CNKI; do not scrape hidden endpoints. |

### CNKI browser-assisted search

Use this workflow only when the user asks for CNKI search and the host has an interactive browser/computer-use tool:

1. Open CNKI itself or the user's institution library link. Use the current browser session; do not collect or type the user's password into the page.
2. If the user is not signed in, institutional authentication is required, or a CAPTCHA/verification step appears, stop and ask the user to complete that step in the browser. Continue only after access is available.
3. Search using the user's research question and focused Chinese/English synonyms. Prefer Advanced Search when useful; combine fields such as subject, title, author, and date/type filters. Preserve the exact query and filters actually used.
4. Inspect only the result pages needed for relevant candidates. Record the search date, query, filters, result count if visible, title, authors, source, year, abstract if visible, identifier/link, and access status. Treat result snippets as leads, not claim verification.
5. Use the official export function for citations when available. Open/download full text only if the user's account or institutional license permits it. Do not bulk-download, scrape hidden endpoints, bypass download controls, or send licensed files to another AI service unless the applicable terms allow that processing.
6. Put the returned records into the evidence ledger. Mark each item as metadata-only, abstract-only, or full-text inspected. If access fails or a page is unavailable, report it and continue only with sources actually retrieved.

This provides browser-assisted searching, not a general CNKI API, full-corpus entitlement, or guaranteed full-text access. For unattended/high-volume search or a reusable public integration, obtain a written API/institutional authorization from CNKI first.

## Excluded source

| Platform | Decision |
|---|---|
| Sci-Hub | Do not connect or retrieve from it. Use lawful open-access copies from PMC, DOAJ journals, arXiv, medRxiv/bioRxiv, publisher OA pages, or institutional repositories; otherwise ask the user for an authorized copy or library access. |

## Safe workflow for any portal

1. Search using a focused query and note the exact platform, query, and date.
2. Use only public APIs or a user-authorized browser/account. Do not automate credential entry, evade CAPTCHAs, scrape prohibited pages, or bypass paywalls.
3. Save enough bibliographic metadata to deduplicate and verify each record against its publisher, DOI, or repository source of record.
4. Read full text only when the user or platform has lawful access. Otherwise report metadata-only or abstract-only verification.
5. Keep platform coverage precise: records found in a search index are candidates, not proof that the search was exhaustive.
