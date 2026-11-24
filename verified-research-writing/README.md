# Verified Research Writing

A Codex skill for writing academic papers, literature reviews, and experimental reports from traceable scholarly evidence. It requires references to be checked against reliable records and against the claims they support, and it prevents missing experimental data from being filled in with invented results.

## Install

Copy the `verified-research-writing` folder into your Codex skills directory:

- Windows, for the current user: `%USERPROFILE%\.agents\skills\verified-research-writing`
- Inside one repository only: `<repository>\.agents\skills\verified-research-writing`
- macOS/Linux: `~/.agents/skills/verified-research-writing`

Restart Codex or start a fresh session if the skill does not appear immediately. You can also invoke it explicitly with `$verified-research-writing`.

## Install in another AI tool

This package uses the portable `SKILL.md` folder format. If another AI tool supports Agent Skills or compatible `SKILL.md` skills, copy the whole `verified-research-writing` folder into that tool's skill directory and follow its reload/restart instructions. Skill discovery paths and support for helper scripts vary by product; the tool must be able to read the folder's `SKILL.md` and, to run automatic searches, execute Python 3 with network access. The `agents/openai.yaml` file is optional product metadata and can be ignored by other tools.

## What it does

- Searches selected public scholarly indexes before drafting when the host can run the bundled helper and has network access.
- Can search CNKI through the official website when the AI host has interactive browser control and the user has authorized access; the bundled helper does not call CNKI.
- Can use a separately configured CNKI MCP server exposed by the host; the package does not bundle or install a CNKI server.
- Checks reference metadata against publisher pages, DOI records, or relevant scholarly repositories and indexes.
- Checks RIS, EndNote, JSON, or CSV reference metadata against Crossref and produces a traceable JSON report.
- Checks whether each source actually supports the claim it accompanies.
- Builds a structured evidence ledger with study design, sample, methods, results, limitations, and verification level.
- Marks inaccessible or unverifiable sources instead of making up citations.
- Routes course papers, lab reports, narrative reviews, systematic reviews, and scoping reviews through different workflows.
- Uses only supplied protocols and data for experimental methods and results; makes calculations reproducible and missing values visible.
- Checks drafts against supplied rubrics, journal instructions, or institutional templates.
- Reports material limits, such as abstract-only access or unavailable subscription databases.

The included `search_literature.py` helper searches Crossref, PubMed, Europe PMC, DOAJ, Wiley Online Library's SRU metadata search, and arXiv using Python's standard library. It returns index records, abstracts, and some lawful full-text links, not downloaded full text. `verify_references.py` compares supplied reference metadata with Crossref; it does not verify claim support. CNKI search requires either a separately configured CNKI MCP server or host browser control and the user's own authorized session. The package itself does not include CNKI access. Read `references/mcp-integration.md`, `references/source-apis.md`, and `references/platform-access.md` for provider selection and access limits. Read `references/workflows.md`, `references/evidence-and-data.md`, `references/reference-verification.md`, and `references/submission-checks.md` for the writing, extraction, analysis, and review processes. A skill cannot add browser/network access or database credentials to an AI host that does not already have them.

## Local checks

Run the dependency-free project checks and parser tests before publishing changes:

```text
python scripts/validate_project.py
python -m unittest discover -s tests -v
```

GitHub Actions runs these checks on pushes and pull requests.

To check a reference export locally:

```text
python scripts/verify_references.py references.ris --output verification-report.json
```

Only citation metadata is sent to Crossref. The script does not upload abstracts or article files.

The skill does not claim that a search is exhaustive or that a verified citation is automatically high quality. It cannot certify publication readiness or replace the author's final review of the draft, source texts, data, and venue instructions.

## Verify the skill

1. Test the search helper:

   ```text
   python scripts/search_literature.py "CRISPR Cas9" --limit 2
   ```

   Check provider statuses, query, search time, and candidate records. A failed provider should appear as an error, not be reported as searched.

2. Install the folder into the Codex skills directory, start a fresh session, and explicitly invoke `$verified-research-writing`. Ask it to write a short background paragraph and report which sources it actually checked.

3. Test its honesty with a deliberately nonexistent DOI and with an experiment that has missing values/equipment details. It should mark unverified sources and missing facts instead of filling them in.

4. Test the systematic-review route without search logs or screening data. It should offer a protocol or blank log, but must not generate completed screening counts or claim a systematic search occurred.

5. Supply a rubric or journal checklist and confirm the response marks each item met, unmet, not applicable, or unverifiable.

6. If a CNKI MCP server is separately configured, invoke its actual search tool and confirm the skill logs the server/tool name, real query, filters, returned records, and coverage. If the host supports browser control and you have CNKI access, confirm it uses the official site, records the actual query/filters, stops for you at sign-in or CAPTCHA, and reports only records it actually saw. Without either capability, it should offer a query for manual use.

These checks exercise the workflow but cannot prove that every future model response will follow it. Always inspect the cited sources and final manuscript yourself.

## 中文说明

这个 skill 用于辅助撰写论文、文献综述、系统综述、范围综述和实验报告。它提供逐篇证据表、实验数据复核、按文种区分的写作流程，以及按评分标准或期刊要求进行的交稿检查。运行环境允许联网并能运行随附脚本时，它会搜索 Crossref、PubMed、Europe PMC、DOAJ、Wiley 和 arXiv 等来源；脚本提供的是候选索引记录、摘要和部分全文链接，不会自动读取全部全文。没有搜索或全文访问能力时，AI 必须如实说明限制。实验数据必须来自用户提供的真实记录，系统综述的筛选数量必须来自实际记录；缺失的信息会标为待补，不会由 AI 编造。

用户已配置知网 MCP 服务时，AI 可以调用该服务公开的检索工具；若没有 MCP，但 AI 宿主有浏览器操作能力，也可在用户授权的知网会话中按网页流程检索。这个仓库不自带知网连接器或账号。可用的接口取决于宿主工具，检索成功与否必须以真实工具返回为准。`verify_references.py` 可核对 RIS/EndNote/JSON/CSV 中的题录与 Crossref 元数据，但不能验证来源是否支持论点。

## License

MIT. See [LICENSE](LICENSE).
