"""Regression tests for page types and tutorial-section requirements."""

from pathlib import Path
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from review_docs.checks.structural import check_tutorial_sections
from review_docs.config import Config
from review_docs.engine import review_file
from review_docs.models import FileResult


class PageTypeTests(unittest.TestCase):
    def findings(self, content, name="example.adoc"):
        filepath = f"modules/example/pages/{name}"
        result = FileResult(file=filepath)
        check_tutorial_sections(filepath, content.splitlines(), Config(), result)
        return result.findings

    def test_untyped_and_explicit_tutorial_pages_require_sections(self):
        for metadata in ("", ":page-type: tutorial\n"):
            with self.subTest(metadata=metadata):
                content = f"= Example\n{metadata}\nA tutorial.\n"
                self.assertEqual(len(self.findings(content)), 2)

    def test_non_tutorial_page_types_do_not_require_tutorial_sections(self):
        for page_type in ("reference", "troubleshooting", "setup"):
            with self.subTest(page_type=page_type):
                content = (
                    "= Example\n:navtitle: Example\n"
                    f":page-type: {page_type}\n\nReference content.\n"
                )
                self.assertEqual(self.findings(content), [])

    def test_unknown_or_empty_types_keep_tutorial_checks(self):
        for page_type in ("refernece", "other", ""):
            with self.subTest(page_type=page_type):
                content = f"= Example\n:page-type: {page_type}\n\nContent.\n"
                self.assertEqual(len(self.findings(content)), 2)

    def test_page_type_in_body_or_code_example_does_not_skip_checks(self):
        for body in (
            ":page-type: reference\n",
            "[source,asciidoc]\n----\n:page-type: reference\n----\n",
        ):
            with self.subTest(body=body):
                self.assertEqual(len(self.findings(f"= Example\n\n{body}")), 2)

    def test_last_header_page_type_takes_effect(self):
        content = (
            "= Example\n:page-type: reference\n:page-type: tutorial\n\nContent.\n"
        )
        self.assertEqual(len(self.findings(content)), 2)

    def test_tutorial_with_required_sections_passes(self):
        for ending in ("Summary", "Verification"):
            with self.subTest(ending=ending):
                content = f"= Example\n\n== Prerequisites\n\nSetup.\n\n== {ending}\n"
                self.assertEqual(self.findings(content), [])

    def test_index_and_nav_pages_remain_exempt(self):
        for name in ("index.adoc", "nav.adoc"):
            with self.subTest(name=name):
                self.assertEqual(self.findings("= Example\n\nContent.\n", name), [])

    def test_reference_page_still_receives_general_checks(self):
        with tempfile.TemporaryDirectory() as directory:
            page = Path(directory) / "modules/example/pages/reference.adoc"
            page.parent.mkdir(parents=True)
            page.write_text(
                "= Reference\n:page-type: reference\n\n"
                "link:https://example.com[Example]\n",
                encoding="utf-8",
            )
            result = review_file(str(page), Config())
        self.assertEqual(
            [finding.check for finding in result.findings], ["external-link-target"]
        )


if __name__ == "__main__":
    unittest.main()
