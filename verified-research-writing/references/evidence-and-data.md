# Evidence ledger and experimental-data checks

Use an evidence ledger for literature-based documents. Keep a compact version in the deliverable when the assignment permits; otherwise keep it as a separate audit note. A paper's existence and metadata do not establish the strength, applicability, or direction of its evidence.

## Evidence ledger fields

Use one row per source, with fields appropriate to the question:

| Field | What to record |
|---|---|
| Source ID | Stable short key used consistently in notes and draft. |
| Verified citation | Title, authors, year, venue/version, DOI or stable URL; identify preprints and published versions separately. |
| Source type/status | Primary study, review, guideline, dataset, preprint, correction/retraction notice, etc.; status only if checked. |
| Verification level | Full text, abstract only, metadata only, or user-supplied excerpt. Include access date when useful. |
| Study design and setting | Design and setting as reported by the source; do not infer missing details. |
| Population/sample | Who/what was studied, sample size, selection, and relevant subgroup only when available. |
| Methods/exposure/comparator | Concise, source-faithful description relevant to the research question. |
| Outcomes/results | Relevant result with the source's units, effect measure, uncertainty interval, and direction where reported. Preserve null and adverse findings. |
| Limitations/applicability | Authors' stated limitations plus cautious, clearly labeled applicability observations. |
| Claim link | Exact draft claim(s) this source supports, qualifies, conflicts with, or does not support. |
| Evidence location | Section, page, table, figure, or a short locator; capture only a brief quotation when necessary. |

For each central claim, ask whether evidence is direct or indirect, whether populations and methods match the claim, and whether another source conflicts. Prefer a design-appropriate appraisal framework if appraisal is requested or materially needed. Do not create a universal numeric quality score or label a study “high quality” without a named, appropriate method and evidence.

## Full-text reading

When full text is lawfully accessible, inspect the sections that can substantiate the claim: usually methods and results, and discussion for the authors' interpretation. Check tables/figures and supplementary material where the claim depends on them. Record the page/section/table locator and what was actually observed.

When the helper returns an open-full-text link, open it and inspect it if the host can do so. A link, “open access” flag, or abstract does not mean the full text was read. For Europe PMC, retrieve full text only when the record is in the eligible open-access subset; follow the article's specific license and service terms. Do not bulk-download articles or use the helper to redistribute full-text content. When no lawful full text is available, narrow the claim to what the abstract or metadata actually supports and label that limit.

Short notes should paraphrase the source. Quote only a brief passage when the wording matters, preserve quotation marks and a locator, and cite it. Never invent a page number or quote.

## Experimental data integrity

Before analysis:

- Preserve the supplied raw file unchanged; do not silently overwrite, normalize, drop, or impute values.
- Record the data file/version, sheet/table, variables, units, groups, planned exclusions, and how missing or malformed values are handled.
- Check row counts, duplicate IDs, blank cells, impossible values, inconsistent units, and whether the stated sample size matches usable observations. Report anomalies; do not silently repair them.
- Confirm the experimental unit and independent replicate. Do not treat repeated measurements on one sample as independent subjects.

For each reported calculation, record the input columns/values, formula or method, units, rounding rule, and output. Recheck key arithmetic independently. Use inferential tests only when design, assumptions, and sample size support them; state the test and assumptions, and do not choose a test solely because it yields a desired result. Do not derive a p-value, confidence interval, standard error, or uncertainty from insufficient data.

Keep these categories distinct:

- **Measured:** directly recorded by the experimenter or instrument.
- **Calculated:** derived from supplied measurements using a stated formula.
- **Interpreted:** explanation or implication, with literature support where appropriate.
- **Missing/unknown:** a placeholder or explicit limitation, never a guessed value.

Do not invent equipment models, settings, calibration, randomization, blinding, exclusions, replicates, ethical approval, consent, or instrument uncertainty. If the user supplies only a summary table, do not claim raw-data validation.
