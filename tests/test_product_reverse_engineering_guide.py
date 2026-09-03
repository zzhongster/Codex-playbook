import re
import runpy
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
GUIDE_ROOT = REPO_ROOT / "guides" / "product-reverse-engineering"
VALIDATOR_PATH = REPO_ROOT / "tools" / "validate_product_reverse_engineering_guide.py"
REQUIRED_ENTRY_FILES = (
    REPO_ROOT / "README.md",
    REPO_ROOT / "CONTRIBUTING.md",
    GUIDE_ROOT / "README.md",
    VALIDATOR_PATH,
)
FOUNDATION_DOCUMENTS = {
    "glossary": GUIDE_ROOT / "glossary.md",
    "goals-scope-and-completion": GUIDE_ROOT
    / "core"
    / "goals-scope-and-completion.md",
    "authorization-privacy-and-safety": GUIDE_ROOT
    / "core"
    / "authorization-privacy-and-safety.md",
    "evidence-and-confidence": GUIDE_ROOT
    / "core"
    / "evidence-and-confidence.md",
}
ALLOWED_MATURITY_LABELS = (
    "cross-project-validated",
    "project-validated",
    "industry-established",
    "proposed",
)


class ProductReverseEngineeringGuideTests(unittest.TestCase):
    def read_repo_file(self, relative_path):
        return (REPO_ROOT / relative_path).read_text(encoding="utf-8")

    def read_guide(self):
        guide_readme = GUIDE_ROOT / "README.md"
        self.assertTrue(guide_readme.is_file(), f"missing guide README: {guide_readme}")
        return guide_readme.read_text(encoding="utf-8")

    def read_foundation_document(self, name):
        path = FOUNDATION_DOCUMENTS[name]
        self.assertTrue(path.is_file(), f"missing foundation document: {path}")
        return path.read_text(encoding="utf-8")

    def section_text(self, document, heading):
        lines = document.splitlines()
        self.assertIn(heading, lines)
        start = lines.index(heading)
        heading_level = len(heading) - len(heading.lstrip("#"))
        end = len(lines)
        for index in range(start + 1, len(lines)):
            line = lines[index]
            if not line.startswith("#"):
                continue
            level = len(line) - len(line.lstrip("#"))
            if level <= heading_level:
                end = index
                break
        return "\n".join(lines[start:end])

    def load_validator(self):
        return runpy.run_path(
            str(VALIDATOR_PATH), run_name="product_reverse_engineering_validator"
        )

    def test_required_entry_files_exist(self):
        for path in REQUIRED_ENTRY_FILES:
            self.assertTrue(path.is_file(), f"missing required entry file: {path}")

    def test_foundation_documents_exist(self):
        for name, path in FOUNDATION_DOCUMENTS.items():
            with self.subTest(document=name):
                self.assertTrue(path.is_file(), f"missing foundation document: {path}")

    def test_guide_readme_links_every_foundation_document_relatively(self):
        guide = self.read_guide()
        for path in FOUNDATION_DOCUMENTS.values():
            relative_path = path.relative_to(GUIDE_ROOT).as_posix()
            with self.subTest(path=relative_path):
                self.assertIn(f"]({relative_path})", guide)

    def test_each_foundation_document_declares_one_maturity_and_applicability(self):
        maturity_pattern = re.compile(r"^\*\*证据成熟度：`([^`]+)`\*\*$")
        for name, path in FOUNDATION_DOCUMENTS.items():
            with self.subTest(document=name):
                self.assertTrue(path.is_file(), f"missing foundation document: {path}")
                document = path.read_text(encoding="utf-8")
                maturity_declarations = [
                    line
                    for line in document.splitlines()
                    if line.strip().removeprefix("**").startswith("证据成熟度：")
                ]
                self.assertEqual(1, len(maturity_declarations))
                match = maturity_pattern.fullmatch(maturity_declarations[0].strip())
                self.assertIsNotNone(match)
                self.assertIn(match.group(1), ALLOWED_MATURITY_LABELS)
                self.assertRegex(document, r"(?m)^\*\*适用范围：\*\*\s*\S.+$")

    def test_evidence_document_defines_exact_claim_status_vocabulary(self):
        document = self.read_foundation_document("evidence-and-confidence")
        expected_statuses = (
            "observed",
            "statically-supported",
            "runtime-confirmed",
            "domain-confirmed",
            "inferred",
            "conflicting",
            "unsupported",
            "deprecated",
            "superseded",
        )
        claim_status_section = self.section_text(document, "## 主张状态")
        section_lines = claim_status_section.splitlines()
        table_header = "| 状态 | 定义 |"
        self.assertIn(table_header, section_lines)
        table_start = section_lines.index(table_header)
        self.assertEqual("| --- | --- |", section_lines[table_start + 1])
        status_rows = []
        for line in section_lines[table_start + 2 :]:
            if not line.startswith("|"):
                break
            status_rows.append(line)
        status_declarations = {
            match.group(1)
            for row in status_rows
            if (match := re.fullmatch(r"\| `([a-z-]+)` \| .+ \|", row))
        }
        self.assertEqual(len(status_rows), len(status_declarations))
        self.assertEqual(set(expected_statuses), status_declarations)

    def test_goals_document_defines_purposes_scope_dimensions_and_completion(self):
        document = self.read_foundation_document("goals-scope-and-completion")
        for purpose in (
            "rewrite",
            "migration",
            "replacement",
            "acquisition due diligence",
            "competitor research",
        ):
            with self.subTest(purpose=purpose):
                self.assertIn(f"`{purpose}`", document)
        for dimension in (
            "版本",
            "角色",
            "产品表面",
            "技术资产",
            "业务能力",
            "数据",
            "集成",
            "非功能",
        ):
            with self.subTest(dimension=dimension):
                self.assertRegex(document, rf"(?m)^\| {dimension} \|")
        self.assertIn("分母覆盖率", document)
        self.assertIn("已接受的不确定性", document)

    def test_authorization_document_covers_g0_controls_and_prohibitions(self):
        document = self.read_foundation_document("authorization-privacy-and-safety")
        for control in (
            "G0 授权检查清单",
            "允许的证据来源",
            "数据最小化与脱敏",
            "测试账号隔离",
            "安全克隆",
            "保留与删除",
            "披露路径",
            "禁止事项",
        ):
            with self.subTest(control=control):
                self.assertIn(control, document)
        for prohibited_action in (
            "凭据窃取",
            "许可证破解",
            "绕过访问控制",
            "规避付费功能",
            "拒绝服务",
            "未经批准的破坏性写入",
        ):
            with self.subTest(prohibited_action=prohibited_action):
                self.assertIn(prohibited_action, document)

    def test_evidence_document_separates_axes_and_defines_traceability(self):
        document = self.read_foundation_document("evidence-and-confidence")
        for axis in ("证据与来源类型", "主张状态", "置信度", "方法成熟度"):
            with self.subTest(axis=axis):
                self.assertIn(f"## {axis}", document)
        for trace_term in ("限定稳定 ID", "别名", "墓碑", "类型化追踪链接"):
            with self.subTest(trace_term=trace_term):
                self.assertIn(trace_term, document)
        self.assertIn("没有发现证据不等于证明其不存在", document)

    def test_glossary_defines_core_objects_and_required_contrasts(self):
        document = self.read_foundation_document("glossary")
        for object_type in (
            "证据项",
            "主张",
            "产品表面",
            "技术资产",
            "业务能力",
            "追踪链接",
        ):
            with self.subTest(object_type=object_type):
                self.assertRegex(document, rf"(?m)^### {object_type}$")
        for contrast in (
            "资产与能力",
            "观察与推断",
            "置信度与成熟度",
            "结构与语义",
            "覆盖率与完整性",
            "unsupported 与 failed",
            "缺陷与历史行为",
        ):
            with self.subTest(contrast=contrast):
                self.assertRegex(document, rf"(?m)^### {contrast}$")

    def test_foundation_documents_use_only_relative_links_and_no_placeholders(self):
        placeholder_pattern = re.compile(r"(?i)\b(?:TODO|TBD|FIXME)\b|待补(?:充|全)")
        for name, path in FOUNDATION_DOCUMENTS.items():
            with self.subTest(document=name):
                self.assertTrue(path.is_file(), f"missing foundation document: {path}")
                document = path.read_text(encoding="utf-8")
                links = re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", document)
                for link in links:
                    self.assertNotRegex(link, r"^(?:[a-z]+:|/)")
                self.assertNotIn("/Users/", document)
                self.assertNotRegex(document, placeholder_pattern)

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
        self.assertIn("## 适用受众", guide_lines)
        self.assertIn("### 给项目负责人", guide_lines)
        self.assertIn("### 给执行团队与 AI Agent", guide_lines)

    def test_guide_documents_exact_validation_command(self):
        self.assertIn(
            "python3 tools/validate_product_reverse_engineering_guide.py",
            self.read_guide(),
        )

    def test_guide_scopes_maturity_to_workflow_recommendations(self):
        guide = self.read_guide()
        for heading in ("## 五分钟选型流程", "## 导航与发布顺序"):
            with self.subTest(heading=heading):
                section = self.section_text(guide, heading)
                self.assertIn("证据成熟度：`proposed`", section)

    def test_root_readme_links_the_guide(self):
        readme = self.read_repo_file("README.md")
        self.assertIn("## Guides", readme.splitlines())
        self.assertIn(
            "](guides/product-reverse-engineering/README.md)",
            readme,
        )

    def test_contributing_defines_guide_eligibility(self):
        contributing = self.read_repo_file("CONTRIBUTING.md")
        section = self.section_text(contributing, "## Guide 收录条件")
        for requirement in ("多个阶段或角色", "选型路径", "证据要求", "安全边界"):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, section)

    def test_contributing_defines_all_maturity_labels(self):
        contributing = self.read_repo_file("CONTRIBUTING.md")
        section = self.section_text(contributing, "## Guide 收录条件")
        for label in (
            "cross-project-validated",
            "project-validated",
            "industry-established",
            "proposed",
        ):
            with self.subTest(label=label):
                self.assertRegex(section, rf"(?m)^\| `{label}` \| .+ \|$")

    def test_contributing_defines_all_promotion_categories(self):
        contributing = self.read_repo_file("CONTRIBUTING.md")
        section = self.section_text(contributing, "## 从 Guide 提炼正式条目")
        for category in ("Pattern", "Anti-pattern", "Experiment"):
            with self.subTest(category=category):
                self.assertIn(f"- 提炼为 {category}：", section)

    def test_contributing_keeps_two_independent_project_pattern_gate(self):
        contributing = self.read_repo_file("CONTRIBUTING.md")
        section = self.section_text(contributing, "## 从 Guide 提炼正式条目")
        self.assertRegex(
            section,
            r"提炼为 Pattern：.*至少在两个相互独立的项目中验证",
        )

    def test_validator_loads_exact_repository_test_file(self):
        validator = self.load_validator()
        expected_test_file = REPO_ROOT / "tests" / Path(__file__).name
        self.assertEqual(expected_test_file, validator["TEST_FILE"])
        self.assertGreater(validator["load_test_suite"]().countTestCases(), 0)

    def test_validator_does_not_import_generic_tests_namespace(self):
        validator_source = VALIDATOR_PATH.read_text(encoding="utf-8")
        self.assertNotIn("from tests import", validator_source)
        self.assertNotIn("import tests", validator_source)

    def test_validator_rejects_an_empty_suite(self):
        validator = self.load_validator()
        with tempfile.TemporaryDirectory() as temp_dir:
            empty_test_file = Path(temp_dir) / "empty_test.py"
            empty_test_file.write_text("VALUE = 1\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "zero tests"):
                validator["load_test_suite"](empty_test_file)

    def test_validator_dynamic_load_does_not_write_bytecode(self):
        validator = self.load_validator()
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "sample_test.py"
            test_file.write_text(
                "import unittest\n\n"
                "class SampleTest(unittest.TestCase):\n"
                "    def test_sample(self):\n"
                "        self.assertTrue(True)\n",
                encoding="utf-8",
            )
            suite = validator["load_test_suite"](test_file)
            self.assertEqual(1, suite.countTestCases())
            self.assertFalse((Path(temp_dir) / "__pycache__").exists())


if __name__ == "__main__":
    unittest.main()
