"""Regression tests for collections and attributes in the YAML style check."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from review_docs.checks.code_blocks import check_yaml_flow_syntax
from review_docs.config import Config
from review_docs.models import FileResult, ParseState


class YamlFlowSyntaxTests(unittest.TestCase):
    def findings(self, line, language="yaml"):
        result = FileResult(file="example.adoc")
        check_yaml_flow_syntax(
            line, 1, ParseState(code_block_lang=language), Config(), result
        )
        return result.findings

    def test_empty_mappings_are_allowed(self):
        for line in (
            "devices: {}",
            "resources: {}",
            "  pod: {}",
            "  - masquerade: {}",
            "disk: { }",
            "rng: {   } # <1>",
            '"devices": {}',
            "devices: {}, resources: {}",
        ):
            with self.subTest(line=line):
                self.assertEqual(self.findings(line), [])

    def test_nonempty_flow_mappings_still_warn(self):
        for line in (
            "disk: {bus: virtio}",
            "disk: { bus: virtio } # <1>",
            "config: {devices: {}}",
            "devices: {}, cpu: {cores: 2}",
            "cpu: {cores: 2}, devices: {}",
        ):
            with self.subTest(line=line):
                findings = self.findings(line)
                self.assertEqual(len(findings), 1)
                self.assertEqual(findings[0].check, "yaml-flow-syntax")

    def test_flow_sequences_still_warn(self):
        for line in (
            "verbs: [get, list]",
            "verbs: []",
            "devices: {}, verbs: [get]",
            "devices: [{}]",
        ):
            with self.subTest(line=line):
                self.assertEqual(len(self.findings(line)), 1)

    def test_attribute_references_in_scalars_are_allowed(self):
        for line in (
            "image: quay.io/openshift-release-dev/ocp-release:{ocp-min-version}.20-x86_64 # <5>",
            "image: {image-registry}/ocp-release:{ocp-min-version}",
            "url: https://example.com/{ocp-docs-version}/index.html",
            'version: "{ocp-min-version}"',
            "version: '{ocp-min-version}'",
        ):
            with self.subTest(line=line):
                self.assertEqual(self.findings(line), [])

    def test_collections_containing_attributes_still_warn(self):
        for line in (
            "release: {image: quay.io/ocp-release:{ocp-min-version}}",
            "versions: [{ocp-min-version}, {ocp-docs-version}]",
            "image: repo:{ocp-min-version}, options: {pullPolicy: Always}",
            "image: repo:{ocp-min-version}, versions: [4.18, 4.22]",
        ):
            with self.subTest(line=line):
                self.assertEqual(len(self.findings(line)), 1)

    def test_standalone_mapping_keys_are_not_treated_as_attributes(self):
        for line in ("options: {enabled}", "options: {enabled, disabled}"):
            with self.subTest(line=line):
                self.assertEqual(len(self.findings(line)), 1)

    def test_non_yaml_blocks_are_ignored(self):
        for language in ("text", "bash", "json", ""):
            with self.subTest(language=language):
                self.assertEqual(
                    self.findings("disk: {bus: virtio}", language), []
                )

    def test_existing_chpasswd_exception_is_preserved(self):
        self.assertEqual(
            self.findings("chpasswd: {expire: false}"), []
        )

    def test_cli_accepts_empty_mapping_and_reports_nonempty_mapping(self):
        with tempfile.TemporaryDirectory() as directory:
            page = Path(directory) / "example.adoc"
            page.write_text(
                "= Example\n\n[source,yaml]\n----\n"
                "devices: {}\nresources: {}\ndisk: {bus: virtio}\n"
                "image: quay.io/ocp-release:{ocp-min-version}.20-x86_64\n----\n",
                encoding="utf-8",
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / "scripts/review-docs.py"),
                    "--no-config",
                    "--only", "yaml-flow-syntax",
                    "--format", "json",
                    str(page),
                ],
                capture_output=True,
                text=True,
                check=True,
            )
        report = json.loads(completed.stdout)
        self.assertEqual(report["summary"]["total_errors"], 0)
        self.assertEqual(report["summary"]["total_warnings"], 1)
        self.assertEqual(report["files"][0]["findings"][0]["line"], 7)


if __name__ == "__main__":
    unittest.main()
