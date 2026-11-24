import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "verify_references.py"
SPEC = importlib.util.spec_from_file_location("verify_references", SCRIPT)
verify_references = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verify_references)


class ReferenceVerificationTests(unittest.TestCase):
    def test_ris_parser_keeps_multiple_authors_and_normalizes_doi(self):
        ris = """TY  - JOUR
TI  - A Carefully Reported Study
AU  - Lin, Mei
AU  - Chen, Yu
PY  - 2024
JO  - Example Journal
DO  - https://doi.org/10.1234/example.2024.5
ER  -
"""
        records = verify_references.parse_ris(ris)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["title"], "A Carefully Reported Study")
        self.assertEqual(records[0]["authors"], ["Lin, Mei", "Chen, Yu"])
        self.assertEqual(records[0]["year"], "2024")
        self.assertEqual(records[0]["doi"], "10.1234/example.2024.5")

    def test_json_and_csv_inputs_are_normalized(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            json_file = root / "references.json"
            json_file.write_text(
                json.dumps(
                    {
                        "references": [
                            {
                                "title": "Example",
                                "authors": ["Mei Lin"],
                                "year": 2024,
                                "doi": "https://doi.org/10.1234/example",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            csv_file = root / "references.csv"
            csv_file.write_text(
                "title,authors,year,doi,venue\n"
                '"Example","Mei Lin;Yu Chen",2024,10.1234/example,Journal\n',
                encoding="utf-8",
            )
            json_records = verify_references.load_references(json_file)
            csv_records = verify_references.load_references(csv_file)
        self.assertEqual(json_records[0]["doi"], "10.1234/example")
        self.assertEqual(json_records[0]["year"], "2024")
        self.assertEqual(csv_records[0]["authors"], ["Mei Lin", "Yu Chen"])
        self.assertEqual(csv_records[0]["venue"], "Journal")

    def test_author_order_and_unicode_are_handled_without_false_mismatch(self):
        self.assertTrue(verify_references.person_roughly_matches("Lin, Mei", "Mei Lin"))
        self.assertTrue(verify_references.normalize_text("Физика 中文"))

    def test_missing_crossref_year_stays_empty(self):
        self.assertEqual(
            verify_references.crossref_date({"issued": {"date-parts": [[None]]}}),
            "",
        )

    def test_doi_match_compares_supplied_fields(self):
        reference = {
            "input_index": 1,
            "title": "A Carefully Reported Study",
            "authors": ["Mei Lin"],
            "year": "2024",
            "venue": "Example Journal",
            "doi": "10.1234/example.2024.5",
        }
        crossref_item = {
            "title": ["A Carefully Reported Study"],
            "author": [{"given": "Mei", "family": "Lin"}],
            "issued": {"date-parts": [[2024, 2, 1]]},
            "container-title": ["Example Journal"],
            "DOI": "10.1234/example.2024.5",
            "URL": "https://doi.org/10.1234/example.2024.5",
            "type": "journal-article",
        }
        with patch.object(verify_references, "lookup_doi", return_value=crossref_item):
            result = verify_references.verify_one(reference, "")
        self.assertEqual(result["status"], "doi_metadata_match")
        self.assertEqual(result["comparison"]["differences"], [])

    def test_doi_mismatch_is_not_reported_as_verified(self):
        reference = {
            "input_index": 1,
            "title": "A Different Study",
            "authors": ["Mei Lin"],
            "year": "2024",
            "venue": "Example Journal",
            "doi": "10.1234/example.2024.5",
        }
        crossref_item = {
            "title": ["A Carefully Reported Study"],
            "author": [{"given": "Mei", "family": "Lin"}],
            "issued": {"date-parts": [[2024]]},
            "container-title": ["Example Journal"],
            "DOI": "10.1234/example.2024.5",
            "URL": "https://doi.org/10.1234/example.2024.5",
            "type": "journal-article",
        }
        with patch.object(verify_references, "lookup_doi", return_value=crossref_item):
            result = verify_references.verify_one(reference, "")
        self.assertEqual(result["status"], "doi_metadata_mismatch")
        self.assertTrue(result["comparison"]["differences"])

    def test_doi_without_metadata_is_not_reported_as_metadata_match(self):
        reference = {
            "input_index": 1,
            "title": "",
            "authors": [],
            "year": "",
            "venue": "",
            "doi": "10.1234/example.2024.5",
        }
        crossref_item = {
            "title": ["A Carefully Reported Study"],
            "author": [{"given": "Mei", "family": "Lin"}],
            "issued": {"date-parts": [[2024]]},
            "container-title": ["Example Journal"],
            "DOI": "10.1234/example.2024.5",
            "URL": "https://doi.org/10.1234/example.2024.5",
            "type": "journal-article",
        }
        with patch.object(verify_references, "lookup_doi", return_value=crossref_item):
            result = verify_references.verify_one(reference, "")
        self.assertEqual(result["status"], "doi_record_found_metadata_unchecked")

    def test_title_only_candidate_remains_manual_review(self):
        reference = {
            "input_index": 1,
            "title": "A Carefully Reported Study",
            "authors": [],
            "year": "",
            "venue": "",
            "doi": "",
        }
        crossref_item = {
            "title": ["A Carefully Reported Study"],
            "author": [{"given": "Mei", "family": "Lin"}],
            "issued": {"date-parts": [[2024]]},
            "container-title": ["Example Journal"],
            "DOI": "10.1234/example.2024.5",
            "URL": "https://doi.org/10.1234/example.2024.5",
            "type": "journal-article",
        }
        with patch.object(verify_references, "search_title", return_value=[crossref_item]):
            result = verify_references.verify_one(reference, "")
        self.assertEqual(result["status"], "title_candidate_needs_review")


if __name__ == "__main__":
    unittest.main()
