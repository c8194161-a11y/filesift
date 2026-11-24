#!/usr/bin/env python3
"""Compare RIS, JSON, or CSV reference metadata with Crossref records.

This verifies bibliographic metadata only. It does not assess source quality
or determine whether a paper supports a manuscript claim.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import difflib
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


USER_AGENT = "verified-research-writing-reference-check/1.0"
TITLE_MATCH_MIN = 0.88
TITLE_MATCH_STRONG = 0.96


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        value = " ".join(str(part) for part in value if part is not None)
    value = str(value).casefold()
    value = value.replace("&", " and ")
    value = re.sub(r"https?://doi\.org/", "", value)
    value = re.sub(r"\bdoi\s*:\s*", "", value)
    value = unicodedata.normalize("NFKC", value)
    return "".join(character for character in value if character.isalnum())


def normalize_doi(value: Any) -> str:
    doi = str(value or "").strip()
    doi = re.sub(r"^(?:https?://)?(?:dx\.)?doi\.org/", "", doi, flags=re.I)
    doi = re.sub(r"^doi\s*:\s*", "", doi, flags=re.I)
    return doi.strip().rstrip(".,;)")


def normalize_authors(value: Any) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        items = value
    else:
        text = str(value).strip()
        if not text:
            return []
        if ";" in text:
            items = text.split(";")
        elif "|" in text:
            items = text.split("|")
        else:
            items = [text]
    return [str(item).strip() for item in items if str(item).strip()]


def normalize_reference(item: dict[str, Any]) -> dict[str, Any]:
    lower = {str(key).strip().casefold(): value for key, value in item.items()}
    title = lower.get("title") or lower.get("ti") or lower.get("t1") or ""
    authors = (
        lower.get("authors")
        or lower.get("author")
        or lower.get("au")
        or lower.get("a1")
        or []
    )
    year_value = lower.get("year") or lower.get("py") or lower.get("y1") or ""
    match = re.search(r"(?:19|20)\d{2}", str(year_value))
    venue = (
        lower.get("venue")
        or lower.get("journal")
        or lower.get("jo")
        or lower.get("jf")
        or lower.get("t2")
        or lower.get("ja")
        or ""
    )
    doi = (
        lower.get("doi")
        or lower.get("do")
        or lower.get("m3")
        or lower.get("id")
        or ""
    )
    return {
        "title": str(title).strip(),
        "authors": normalize_authors(authors),
        "year": match.group(0) if match else "",
        "venue": str(venue).strip(),
        "doi": normalize_doi(doi),
    }


def parse_ris(text: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    record: dict[str, list[str]] = {}
    last_tag: str | None = None

    def finish() -> None:
        nonlocal record, last_tag
        if record:
            records.append({key: values if len(values) > 1 else values[0] for key, values in record.items()})
        record = {}
        last_tag = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip("\r\n")
        match = re.match(r"^\s*([A-Za-z0-9]{2})\s*-\s?(.*)$", line)
        if not match:
            if line[:1].isspace() and last_tag and record.get(last_tag):
                record[last_tag][-1] += " " + line.strip()
            continue
        tag, value = match.group(1).upper(), match.group(2).strip()
        if tag == "TY":
            finish()
        if tag == "ER":
            finish()
            continue
        record.setdefault(tag, []).append(value)
        last_tag = tag
    finish()
    return [normalize_reference(item) for item in records]


def load_references(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.casefold()
    text = path.read_text(encoding="utf-8-sig")
    if suffix in {".ris", ".enw"}:
        items = parse_ris(text)
    elif suffix == ".json":
        data = json.loads(text)
        if isinstance(data, dict):
            data = data.get("references", [data])
        if not isinstance(data, list):
            raise ValueError("JSON must be a reference object or an array of reference objects.")
        items = [normalize_reference(item) for item in data if isinstance(item, dict)]
    elif suffix == ".csv":
        items = [normalize_reference(item) for item in csv.DictReader(text.splitlines())]
    else:
        raise ValueError("Input must be .ris, .enw, .json, or .csv.")
    return [
        {**item, "input_index": index}
        for index, item in enumerate(items, start=1)
        if item.get("title") or item.get("doi")
    ]


def fetch_json(url: str, mailto: str = "") -> dict[str, Any]:
    headers = {
        "User-Agent": f"{USER_AGENT} ({mailto})" if mailto else USER_AGENT,
        "Accept": "application/json",
    }
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def crossref_date(item: dict[str, Any]) -> str:
    date_sets = (
        item.get("published-print", {}).get("date-parts")
        or item.get("published-online", {}).get("date-parts")
        or item.get("issued", {}).get("date-parts")
        or []
    )
    if date_sets and date_sets[0]:
        year = date_sets[0][0]
        return str(year) if year is not None else ""
    return ""


def crossref_authors(item: dict[str, Any]) -> list[str]:
    authors = []
    for author in item.get("author", []):
        name = " ".join(
            part for part in (author.get("given", ""), author.get("family", "")) if part
        ).strip()
        if name:
            authors.append(name)
    return authors


def crossref_record(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": (item.get("title") or [""])[0],
        "authors": crossref_authors(item),
        "year": crossref_date(item),
        "venue": (item.get("container-title") or [""])[0],
        "doi": normalize_doi(item.get("DOI")),
        "url": item.get("URL"),
        "type": item.get("type"),
    }


def title_similarity(first_title: str, second_title: str) -> float:
    first_norm = normalize_text(first_title)
    second_norm = normalize_text(second_title)
    if not first_norm or not second_norm:
        return 0.0
    return difflib.SequenceMatcher(None, first_norm, second_norm).ratio()


def person_roughly_matches(expected: str, actual: str) -> bool:
    expected_norm = normalize_text(expected)
    actual_norm = normalize_text(actual)
    if not expected_norm or not actual_norm:
        return True
    if expected_norm in actual_norm or actual_norm in expected_norm:
        return True
    expected_parts = {
        normalize_text(part)
        for part in re.findall(r"[^\W_]+", expected.casefold(), flags=re.UNICODE)
        if normalize_text(part)
    }
    actual_parts = {
        normalize_text(part)
        for part in re.findall(r"[^\W_]+", actual.casefold(), flags=re.UNICODE)
        if normalize_text(part)
    }
    if expected_parts and actual_parts and expected_parts == actual_parts:
        return True
    if any(len(part) >= 3 for part in expected_parts & actual_parts):
        return True
    return difflib.SequenceMatcher(None, expected_norm, actual_norm).ratio() >= 0.82


def compare_reference(expected: dict[str, Any], actual: dict[str, Any]) -> dict[str, Any]:
    differences = []
    score = title_similarity(expected.get("title", ""), actual.get("title", ""))
    if expected.get("title") and score < TITLE_MATCH_STRONG:
        differences.append(
            {
                "field": "title",
                "expected": expected["title"],
                "crossref": actual.get("title", ""),
                "similarity": round(score, 3),
            }
        )
    expected_authors = expected.get("authors") or []
    actual_authors = actual.get("authors") or []
    if expected_authors and actual_authors and not person_roughly_matches(
        expected_authors[0], actual_authors[0]
    ):
        differences.append(
            {
                "field": "first_author",
                "expected": expected_authors[0],
                "crossref": actual_authors[0],
            }
        )
    if expected.get("year") and actual.get("year") and expected["year"] != actual["year"]:
        differences.append(
            {"field": "year", "expected": expected["year"], "crossref": actual["year"]}
        )
    if expected.get("venue") and actual.get("venue"):
        venue_similarity = title_similarity(expected["venue"], actual["venue"])
        if venue_similarity < 0.72:
            differences.append(
                {
                    "field": "venue",
                    "expected": expected["venue"],
                    "crossref": actual["venue"],
                    "similarity": round(venue_similarity, 3),
                }
            )
    return {
        "title_similarity": round(score, 3) if expected.get("title") else None,
        "differences": differences,
    }


def lookup_doi(doi: str, mailto: str) -> dict[str, Any]:
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
    return fetch_json(url, mailto=mailto)["message"]


def search_title(title: str, mailto: str) -> list[dict[str, Any]]:
    params = urllib.parse.urlencode({"query.title": title, "rows": "3"})
    url = f"https://api.crossref.org/works?{params}"
    if mailto:
        url += "&" + urllib.parse.urlencode({"mailto": mailto})
    return fetch_json(url, mailto=mailto).get("message", {}).get("items", [])


def verify_one(reference: dict[str, Any], mailto: str) -> dict[str, Any]:
    expected = {key: reference.get(key, "") for key in ("title", "authors", "year", "venue", "doi")}
    result: dict[str, Any] = {
        "input_index": reference["input_index"],
        "input": expected,
        "provider": "Crossref",
        "status": "",
        "matched_record": None,
        "comparison": None,
        "message": "",
    }
    try:
        if expected.get("doi"):
            message = lookup_doi(expected["doi"], mailto)
            actual = crossref_record(message)
            comparison = compare_reference(expected, actual)
            result["matched_record"] = actual
            result["comparison"] = comparison
            has_comparable_fields = any(
                expected.get(field) for field in ("title", "authors", "year", "venue")
            )
            if not has_comparable_fields:
                result["status"] = "doi_record_found_metadata_unchecked"
                result["message"] = (
                    "DOI resolves in Crossref, but no title/author/year/venue fields were supplied for comparison."
                )
            elif comparison["differences"]:
                result["status"] = "doi_metadata_mismatch"
                result["message"] = (
                    "DOI resolves in Crossref, but supplied metadata differs; review the publisher record."
                )
            else:
                result["status"] = "doi_metadata_match"
                result["message"] = (
                    "DOI resolves in Crossref and supplied fields match; compare important records with the publisher."
                )
            return result

        candidates = search_title(expected.get("title", ""), mailto)
        ranked = sorted(
            candidates,
            key=lambda item: title_similarity(
                expected.get("title", ""), (item.get("title") or [""])[0]
            ),
            reverse=True,
        )
        if not ranked:
            result["status"] = "no_match"
            result["message"] = "No Crossref title candidates were returned; this does not prove the work is fake."
            return result

        top = crossref_record(ranked[0])
        score = title_similarity(expected.get("title", ""), top.get("title", ""))
        result["matched_record"] = top
        result["comparison"] = compare_reference(expected, top)
        if score >= TITLE_MATCH_MIN:
            result["status"] = "title_candidate_needs_review"
            result["message"] = (
                "Likely title candidate only. Confirm authors, venue, year, and identifier "
                "against the publisher or another authoritative record."
            )
        else:
            result["status"] = "no_match"
            result["message"] = "No sufficiently close title candidate; Crossref coverage is not exhaustive."
        return result
    except urllib.error.HTTPError as exc:
        if exc.code == 404 and expected.get("doi"):
            result["status"] = "doi_not_found_in_crossref"
            result["message"] = (
                "DOI did not resolve in Crossref. Check for a typo and search another authoritative registry."
            )
        else:
            result["status"] = "lookup_error"
            result["message"] = f"Crossref HTTP error {exc.code}."
        return result
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError, ValueError) as exc:
        result["status"] = "lookup_error"
        result["message"] = f"{type(exc).__name__}: {exc}"
        return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare RIS, JSON, or CSV bibliography metadata with Crossref."
    )
    parser.add_argument("input", type=Path, help="Input .ris, .enw, .json, or .csv file")
    parser.add_argument("--output", type=Path, help="Write JSON report to this path (default: stdout)")
    parser.add_argument(
        "--mailto",
        default=os.environ.get("CROSSREF_MAILTO", ""),
        help="Contact email for Crossref polite-pool requests (or set CROSSREF_MAILTO)",
    )
    args = parser.parse_args()
    if not args.input.is_file():
        parser.error(f"input file does not exist: {args.input}")
    return args


def main() -> int:
    args = parse_args()
    try:
        references = load_references(args.input)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, csv.Error, ValueError) as exc:
        sys.stderr.write(f"Could not read references: {exc}\n")
        return 2
    if not references:
        sys.stderr.write("No references with a title or DOI were found.\n")
        return 2

    records = []
    for index, reference in enumerate(references):
        if index:
            time.sleep(0.25)
        records.append(verify_one(reference, args.mailto))
    report = {
        "checked_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "input_file": args.input.name,
        "provider": "Crossref REST API",
        "records_checked": len(records),
        "scope": "Bibliographic metadata only; claim support and scholarly quality were not assessed.",
        "results": records,
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        print(rendered)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.stderr.write("Verification cancelled.\n")
        sys.exit(130)
