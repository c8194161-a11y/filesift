# Optional scholarly MCP integrations

This skill is an instruction set, not an MCP server. It does not install connectors, create accounts, or provide access credentials. When a compatible scholarly MCP server is already configured in the host AI, the assistant can use its exposed tools as an optional search/retrieval provider.

## Discover and use a CNKI MCP server

1. Search the host's available tools for a CNKI or literature-search MCP server. Do not assume a server exists just because a README or setup guide mentions one.
2. Inspect the actual tool descriptions and input schema. Prefer a documented search tool for discovery, a metadata/details tool for bibliographic checks, and a read tool for full text only when available and permitted.
3. If the server is absent, disconnected, or returns an authentication/permission error, do not claim a CNKI search occurred. Offer the user a ready-to-run query or ask them to configure an authorized connector.
4. If login, institution authentication, CAPTCHA, or human verification is required, let the user complete it. Never ask for passwords, copy credentials into prompts, or bypass verification.
5. Use bounded, focused queries. For concept-heavy topics, search several translated/synonym groups instead of one vague query. Use field restrictions and filters only when the tool schema supports them.
6. Log the real server/tool names, exact query and parameters, date, visible result count, pages/cursors inspected, continuation state, errors, and any user-verified step. Do not invent total coverage or screening counts.
7. Normalize returned items into evidence cards with title, authors, year, source, identifier, URL, abstract, access status, and verification level. Keep the connector's raw identifier and source link so a reader can trace the result.
8. Read only records the connector actually returns. If full text is available, record the section/page/table used for each important claim. Distinguish metadata-only, abstract-only, and full-text inspection.
9. Export or download only through connector functions and only within the user's license. Do not automate bulk downloads, scrape hidden endpoints, bypass paywalls, or send restricted files to a third-party model unless the applicable terms allow it.

The [CNKI-Enhanced-MCP GitHub project](https://github.com/ChengDSYJ-Studio/CNKI-Enhanced-MCP) is one possible separately installed connector, not a component shipped in this skill. Its current documentation describes search, metadata, reading, download, and export tools. Check that project's current code, installation, and licensing terms independently before using it. The skill should call only tools actually exposed by the host, not hardcode a presumed tool name or treat a third-party README as evidence that the server is installed or authorized.

## Search log fields

| Field | Record |
|---|---|
| Provider | Actual MCP server and tool name |
| Query | Exact query text and fields |
| Filters | Date range, document type, language, subject, or other supplied filters |
| Time | Search date/time and timezone |
| Coverage | Returned result count, pages/cursors actually inspected, and any limit |
| Status | Success, partial result, authentication needed, blocked, or error |
| Trace | Stable record identifiers and links |
| Notes | User verification, exclusions, resume token/state, or unresolved access issue |

Do not label a search systematic or exhaustive unless the protocol, coverage, deduplication, screening, and counts were actually recorded.
