# Verify a bibliography against Crossref metadata

Use `scripts/verify_references.py` to check whether supplied DOI/title metadata agrees with Crossref records. This is a bibliographic metadata check, not a plagiarism scan, peer-review check, quality appraisal, or claim-support verification.

## Supported inputs

The script accepts:

- RIS exports (`.ris`, `.enw`): reads title, authors, year, DOI, and venue fields.
- JSON: an array of reference objects, or an object with a `references` array. Recognized keys include `title`, `authors`, `year`, `doi`, and `venue`/`journal`.
- CSV: columns named `title`, `authors`, `year`, `doi`, and `venue` or `journal`.

Example JSON:

```json
{
  "references": [
    {
      "title": "Example paper title",
      "authors": ["A. Author", "B. Author"],
      "year": 2024,
      "doi": "10.xxxx/example"
    }
  ]
}
```

Run:

```text
python scripts/verify_references.py references.ris --output verification-report.json
```

Only citation metadata is sent to Crossref. No abstract, article text, or PDF is uploaded by this script. Results use cautious statuses:

- `doi_metadata_match`: DOI resolves and the supplied title/authors/year/venue do not materially conflict with the returned record.
- `doi_metadata_mismatch`: DOI resolves, but one or more supplied fields materially differ; review manually because spelling, transliteration, version, and publisher metadata can vary.
- `doi_record_found_metadata_unchecked`: DOI resolves, but the input supplied no title/author/year/venue fields to compare.
- `title_candidate_needs_review`: no DOI was supplied; a likely title candidate was found but must be confirmed against the publisher or another source.
- `no_match`: no plausible Crossref record was found. This does not prove a work is fake; some books, theses, local journals, and non-Crossref works may be absent.
- `lookup_error`: network, rate-limit, or service failure prevented verification.

The report preserves the returned Crossref record and the fields compared. It never upgrades a title-only fuzzy match to a verified citation. Do not use a metadata match as proof that the source supports a manuscript claim.
