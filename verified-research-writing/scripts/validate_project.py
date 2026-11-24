#!/usr/bin/env python3
"""Run dependency-free structural checks for the skill repository."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = (
    "SKILL.md",
    "README.md",
    "LICENSE",
    "agents/openai.yaml",
    "references/evidence-and-data.md",
    "references/mcp-integration.md",
    "references/platform-access.md",
    "references/reference-verification.md",
    "references/source-apis.md",
    "references/submission-checks.md",
    "references/workflows.md",
    "scripts/search_literature.py",
    "scripts/verify_references.py",
    "tests/test_verify_references.py",
)
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", re.DOTALL)


def validate() -> list[str]:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"Required file is missing: {relative}")

    skill_path = ROOT / "SKILL.md"
    if skill_path.is_file():
        text = skill_path.read_text(encoding="utf-8")
        match = FRONTMATTER.match(text)
        if not match:
            errors.append("SKILL.md has missing or malformed YAML front matter.")
        else:
            frontmatter = match.group(1)
            name_match = re.search(r"^name:\s*([a-z0-9-]+)\s*$", frontmatter, re.M)
            description_match = re.search(r"^description:\s*(.+)$", frontmatter, re.M)
            if not name_match:
                errors.append("SKILL.md front matter needs a lowercase hyphenated name.")
            if not description_match or not description_match.group(1).strip():
                errors.append("SKILL.md front matter needs a non-empty description.")
            if "[TODO" in frontmatter:
                errors.append("SKILL.md front matter contains an unfinished TODO.")

    for markdown in ROOT.rglob("*.md"):
        content = markdown.read_text(encoding="utf-8")
        for target in MARKDOWN_LINK.findall(content):
            target = target.strip().strip("<>")
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            local_target = target.split("#", 1)[0].split("?", 1)[0]
            if local_target and not (markdown.parent / local_target).resolve().is_file():
                errors.append(
                    f"Broken local link in {markdown.relative_to(ROOT)}: {target}"
                )

    for script in ROOT.rglob("*.py"):
        try:
            compile(script.read_text(encoding="utf-8"), str(script), "exec")
        except (OSError, SyntaxError, UnicodeDecodeError) as exc:
            errors.append(f"Python syntax/read error in {script.relative_to(ROOT)}: {exc}")

    for script in ("scripts/search_literature.py", "scripts/verify_references.py"):
        path = ROOT / script
        if path.is_file():
            process = subprocess.run(
                [sys.executable, str(path), "--help"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            if process.returncode != 0:
                errors.append(
                    f"{script} --help failed: {process.stderr.strip() or process.stdout.strip()}"
                )
    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    markdown_count = len(list(ROOT.rglob("*.md")))
    python_count = len(list(ROOT.rglob("*.py")))
    print(
        "Project validation passed "
        f"({markdown_count} Markdown files, {python_count} Python files, "
        "local links, front matter, syntax, and CLI smoke checks)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
