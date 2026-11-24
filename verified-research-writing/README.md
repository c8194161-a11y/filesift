# Verified Research Writing

A portable Agent Skill for writing academic papers, literature reviews, and experimental reports from traceable scholarly evidence. It requires references to be checked against reliable records and against the claims they support, and it prevents missing experimental data from being filled in with invented results.

## Cross-platform installation

The same `verified-research-writing` folder works on Windows, Linux, and macOS. It contains Markdown instructions and Python scripts that use the standard library; it has no OS-specific binaries. The AI host must support Agent Skills or a compatible `SKILL.md` format.

Copy the whole folder into the skills directory used by your AI tool. The location and reload steps vary by product and installation scope, so follow that tool's instructions. To run the bundled search or reference-check scripts, install Python 3.10 or newer and allow network access. The optional `agents/openai.yaml` file is product-specific metadata and can be ignored by compatible hosts that do not use it.

After installing, reload the host or start a fresh session. Use that product's skill selector or invocation syntax to activate the skill.

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

2. Install the folder into the target AI host, reload or start a fresh session, and activate the skill using that host's selector or invocation syntax. Ask it to write a short background paragraph and report which sources it actually checked.

3. Test its honesty with a deliberately nonexistent DOI and with an experiment that has missing values/equipment details. It should mark unverified sources and missing facts instead of filling them in.

4. Test the systematic-review route without search logs or screening data. It should offer a protocol or blank log, but must not generate completed screening counts or claim a systematic search occurred.

5. Supply a rubric or journal checklist and confirm the response marks each item met, unmet, not applicable, or unverifiable.

6. If a CNKI MCP server is separately configured, invoke its actual search tool and confirm the skill logs the server/tool name, real query, filters, returned records, and coverage. If the host supports browser control and you have CNKI access, confirm it uses the official site, records the actual query/filters, stops for you at sign-in or CAPTCHA, and reports only records it actually saw. Without either capability, it should offer a query for manual use.

These checks exercise the workflow but cannot prove that every future model response will follow it. Always inspect the cited sources and final manuscript yourself.

## 中文说明

这个 skill 文件夹可在 Windows、Linux 和 macOS 上使用；AI 工具需要支持兼容的 `SKILL.md` 格式。随附脚本使用 Python 标准库，需 Python 3.10 或更高版本及网络访问。安装目录由所用 AI 工具决定。

它用于辅助撰写论文、文献综述、系统综述、范围综述和实验报告，提供逐篇证据表、实验数据复核、按文种区分的写作流程，以及按评分标准或期刊要求进行的交稿检查。检索脚本会返回候选索引记录、摘要和部分全文链接，不会自动读取全部全文；AI 必须如实说明搜索和全文访问限制。实验数据必须来自用户提供的真实记录，系统综述的筛选数量必须来自实际记录；缺失的信息会标为待补，不会由 AI 编造。

用户已配置知网 MCP 服务时，AI 可以调用该服务公开的检索工具；若没有 MCP，但 AI 宿主有浏览器操作能力，也可在用户授权的知网会话中按网页流程检索。这个仓库不自带知网连接器或账号。可用的接口取决于宿主工具，检索成功与否必须以真实工具返回为准。`verify_references.py` 可核对 RIS/EndNote/JSON/CSV 中的题录与 Crossref 元数据，但不能验证来源是否支持论点。

## License

MIT. See [LICENSE](LICENSE).
