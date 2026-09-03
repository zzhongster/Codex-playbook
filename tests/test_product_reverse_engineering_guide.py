import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
GUIDE_ROOT = REPO_ROOT / "guides" / "product-reverse-engineering"
REQUIRED_ENTRY_FILES = (
    REPO_ROOT / "README.md",
    REPO_ROOT / "CONTRIBUTING.md",
    GUIDE_ROOT / "README.md",
    REPO_ROOT / "tools" / "validate_product_reverse_engineering_guide.py",
)


class ProductReverseEngineeringGuideTests(unittest.TestCase):
    def read_guide(self):
        guide_readme = GUIDE_ROOT / "README.md"
        self.assertTrue(guide_readme.is_file(), f"missing guide README: {guide_readme}")
        return guide_readme.read_text(encoding="utf-8")

    def test_required_entry_files_exist(self):
        for path in REQUIRED_ENTRY_FILES:
            self.assertTrue(path.is_file(), f"missing required entry file: {path}")

    def test_guide_lists_all_evidence_maturity_labels(self):
        guide = self.read_guide()
        for label in (
            "cross-project-validated",
            "project-validated",
            "industry-established",
            "proposed",
        ):
            with self.subTest(label=label):
                self.assertIn(label, guide)

    def test_guide_has_exact_audience_headings(self):
        guide_lines = self.read_guide().splitlines()
        self.assertIn("## 给项目负责人", guide_lines)
        self.assertIn("## 给执行团队与 AI Agent", guide_lines)


if __name__ == "__main__":
    unittest.main()
