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
    "end-to-end-workflow": GUIDE_ROOT / "core" / "end-to-end-workflow.md",
    "product-and-business-modeling": GUIDE_ROOT
    / "core"
    / "product-and-business-modeling.md",
}
LINK_SOURCE_DOCUMENTS = (
    REPO_ROOT / "README.md",
    REPO_ROOT / "CONTRIBUTING.md",
    GUIDE_ROOT / "README.md",
    *FOUNDATION_DOCUMENTS.values(),
)
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

    def test_guide_readme_links_root_contributing_guide_relatively(self):
        self.assertIn("](../../CONTRIBUTING.md)", self.read_guide())

    def test_all_local_markdown_links_resolve_from_their_source_document(self):
        for source_path in LINK_SOURCE_DOCUMENTS:
            self.assertTrue(
                source_path.is_file(), f"missing source document: {source_path}"
            )
            document = source_path.read_text(encoding="utf-8")
            links = re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", document)
            for link in links:
                target = link.strip().removeprefix("<").removesuffix(">")
                if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.IGNORECASE):
                    continue
                local_target = target.split("#", 1)[0]
                resolved_target = (
                    source_path if not local_target else source_path.parent / local_target
                ).resolve()
                with self.subTest(source=source_path, target=target):
                    self.assertTrue(
                        resolved_target.is_file(),
                        f"broken local link in {source_path}: {target}",
                    )

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

    def test_maturity_labels_describe_guide_methods_not_product_claim_truth(self):
        separation_statement = (
            "四个标签只描述逆向工程方法或建议的支撑证据成熟度，"
            "不描述目标产品主张的真假。"
        )
        header_statement = (
            "文档头部的“证据成熟度”是“本指南方法或建议的支撑证据成熟度”"
            "的机器可读简称。"
        )
        claim_statement = (
            "目标产品主张使用主张状态、置信度和证据引用表达可信程度。"
        )
        documents = (
            self.read_guide(),
            self.read_repo_file("CONTRIBUTING.md"),
            self.read_foundation_document("glossary"),
            self.read_foundation_document("evidence-and-confidence"),
        )
        for index, document in enumerate(documents):
            with self.subTest(document=index):
                self.assertIn(separation_statement, document)
                self.assertIn(header_statement, document)
                self.assertIn(claim_statement, document)

    def test_product_claims_can_reference_methods_with_different_maturity(self):
        document = self.read_foundation_document("evidence-and-confidence")
        maturity_section = self.section_text(document, "## 方法成熟度")
        self.assertIn("多个成熟度不同的取证方法", maturity_section)
        self.assertIn("不携带一个整体的方法成熟度", maturity_section)

        glossary = self.read_foundation_document("glossary")
        glossary_section = self.section_text(glossary, "### 置信度与成熟度")
        self.assertIn("多个成熟度不同的取证方法", glossary_section)
        self.assertIn("不携带一个整体的方法成熟度", glossary_section)

        claim_section = self.section_text(document, "## 最小主张记录")
        self.assertNotIn("方法成熟度", claim_section)
        for claim_field in ("当前状态", "置信度", "证据链接"):
            with self.subTest(claim_field=claim_field):
                self.assertIn(claim_field, claim_section)

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

    def test_end_to_end_workflow_defines_each_phase_contract_locally(self):
        document = self.read_foundation_document("end-to-end-workflow")
        phase_topics = (
            "授权、目标与安全",
            "基线与分母",
            "产品表面与角色",
            "技术图谱",
            "纵向证据链",
            "运行时实验",
            "业务语义综合",
            "完整性、冲突与质量审计",
            "冻结与目的映射",
            "增量校准与方法学习",
        )
        required_subheadings = (
            "#### 进入条件",
            "#### 执行动作",
            "#### 交付物",
            "#### 退出门禁",
            "#### 常见失败模式",
            "#### 停止规则",
        )

        for phase_number, topic in enumerate(phase_topics):
            phase_heading = f"### Phase {phase_number}"
            with self.subTest(phase=phase_number):
                self.assertEqual(1, document.splitlines().count(phase_heading))
                phase_section = self.section_text(document, phase_heading)
                self.assertIn(topic, phase_section)
                for subheading in required_subheadings:
                    self.assertEqual(1, phase_section.splitlines().count(subheading))
                action_section = self.section_text(phase_section, "#### 执行动作")
                self.assertRegex(action_section, r"(?m)^1\. \S")

    def test_end_to_end_workflow_defines_minimal_trace_loop(self):
        document = self.read_foundation_document("end-to-end-workflow")
        self.assertIn(
            "角色/入口 → 交互 → 代码/服务 → 数据/异步副作用 → "
            "规则 → 实验 → 决策 → 验收",
            document,
        )

    def test_phase_4_uses_placeholders_until_later_phases_complete_trace_loop(self):
        document = self.read_foundation_document("end-to-end-workflow")
        phase_4 = self.section_text(document, "### Phase 4")
        self.assertIn("计划/候选占位节点", phase_4)
        self.assertIn("未执行节点不得标为已完成或已确认", phase_4)

        phase_4_exit_gate = self.section_text(phase_4, "#### 退出门禁")
        self.assertIn("不得宣称最小追踪闭环已经完成", phase_4_exit_gate)

        phase_8 = self.section_text(document, "### Phase 8")
        phase_8_exit_gate = self.section_text(phase_8, "#### 退出门禁")
        self.assertIn("完整闭环门禁", phase_8_exit_gate)
        self.assertIn("实验或静态替代验证", phase_8_exit_gate)

    def test_phase_5_allows_a_governed_static_only_branch(self):
        document = self.read_foundation_document("end-to-end-workflow")
        phase_5 = self.section_text(document, "### Phase 5")
        static_branch = self.section_text(phase_5, "##### 非运行分支")
        for permitted_reason in (
            "授权未覆盖运行",
            "合法环境不可用",
            "依赖或硬件无法安全复现",
            "副作用无法隔离",
        ):
            with self.subTest(permitted_reason=permitted_reason):
                self.assertIn(permitted_reason, static_branch)
        for required_record in (
            "非运行验证记录",
            "运行证据缺口记录",
            "ART-P5-STATIC",
            "ART-P5-RUNTIME-GAP",
            "风险接受人",
            "适用期限",
            "重新打开条件",
        ):
            with self.subTest(required_record=required_record):
                self.assertIn(required_record, static_branch)
        self.assertIn("允许进入 Phase 6", static_branch)
        self.assertIn("不得标为 `runtime-confirmed`", static_branch)

        phase_5_exit_gate = self.section_text(phase_5, "#### 退出门禁")
        self.assertIn("运行分支", phase_5_exit_gate)
        self.assertIn("静态分支", phase_5_exit_gate)

    def test_phase_5_scopes_runtime_actions_to_the_runtime_branch(self):
        document = self.read_foundation_document("end-to-end-workflow")
        phase_5 = self.section_text(document, "### Phase 5")
        action_section = self.section_text(phase_5, "#### 执行动作")
        action_lines = action_section.splitlines()
        runtime_heading = "##### 运行分支"
        non_runtime_heading = "##### 非运行分支"

        self.assertEqual(1, action_lines.count(runtime_heading))
        self.assertEqual(1, action_lines.count(non_runtime_heading))
        runtime_position = action_lines.index(runtime_heading)
        non_runtime_position = action_lines.index(non_runtime_heading)
        self.assertLess(runtime_position, non_runtime_position)

        common_actions = "\n".join(action_lines[1:runtime_position])
        self.assertIn("先选择并记录一个分支", common_actions)
        runtime_branch = self.section_text(action_section, runtime_heading)
        non_runtime_branch = self.section_text(action_section, non_runtime_heading)
        for runtime_action in (
            "执行最小只读或低副作用探针",
            "采集用户可见结果",
            "重复关键实验",
            "清理核对",
        ):
            with self.subTest(runtime_action=runtime_action):
                self.assertNotIn(runtime_action, common_actions)
                self.assertIn(runtime_action, runtime_branch)
                self.assertNotIn(runtime_action, non_runtime_branch)

        self.assertRegex(runtime_branch, r"(?m)^1\. \S")
        self.assertRegex(non_runtime_branch, r"(?m)^1\. \S")

    def test_phase_8_maps_every_supported_project_purpose(self):
        document = self.read_foundation_document("end-to-end-workflow")
        phase_8 = self.section_text(document, "### Phase 8")
        purpose_mapping = self.section_text(
            phase_8, "#### 目的专用映射与交付"
        )
        purpose_artifacts = {
            "rewrite": "ART-P8-REWRITE",
            "migration": "ART-P8-MIGRATION",
            "replacement": "ART-P8-REPLACEMENT",
            "acquisition due diligence": "ART-P8-DUE-DILIGENCE",
            "competitor research": "ART-P8-COMPETITOR",
        }
        for purpose, artifact in purpose_artifacts.items():
            with self.subTest(purpose=purpose):
                self.assertRegex(
                    purpose_mapping,
                    rf"(?m)^\| `{re.escape(purpose)}` \| .+ `{artifact}` \| .+ \|$",
                )
        self.assertIn("完成条件", purpose_mapping)

        phase_8_exit_gate = self.section_text(phase_8, "#### 退出门禁")
        self.assertIn("每个已选主要目的", phase_8_exit_gate)

    def test_product_modeling_defines_substantive_model_sections(self):
        document = self.read_foundation_document("product-and-business-modeling")
        required_sections = (
            "## 产品地图先行",
            "## 能力模型",
            "## 角色模型",
            "## 用户旅程",
            "## 交互模型",
            "## 状态机",
            "## 业务规则",
            "## 决策表",
            "## 公式",
            "## 权限模型",
            "## 关键业务语义",
            "## 错误与补偿",
            "## 跨模块不变量",
        )
        for heading in required_sections:
            with self.subTest(heading=heading):
                section = self.section_text(document, heading)
                substantive_lines = [
                    line
                    for line in section.splitlines()[1:]
                    if line.strip() and not line.startswith("#")
                ]
                self.assertGreaterEqual(len(substantive_lines), 2)

    def test_product_modeling_covers_path_and_semantic_dimensions(self):
        document = self.read_foundation_document("product-and-business-modeling")
        journey_section = self.section_text(document, "## 用户旅程")
        for path in ("正常", "负向", "逆向", "重试", "部分成功", "批量", "权限"):
            with self.subTest(path=path):
                self.assertIn(path, journey_section)

        state_section = self.section_text(document, "## 状态机")
        self.assertIn("守卫条件", state_section)
        self.assertIn("副作用", state_section)

        rule_section = self.section_text(document, "## 业务规则")
        for rule_field in ("自然语言", "公式或决策表", "正反例", "适用边界", "证据"):
            with self.subTest(rule_field=rule_field):
                self.assertIn(rule_field, rule_section)

        for semantic in (
            "金额语义",
            "数量语义",
            "时间语义",
            "身份语义",
            "租户语义",
            "可见性语义",
            "历史语义",
            "删除语义",
        ):
            with self.subTest(semantic=semantic):
                self.assertRegex(document, rf"(?m)^### {semantic}$")
                section = self.section_text(document, f"### {semantic}")
                substantive_lines = [
                    line
                    for line in section.splitlines()[1:]
                    if line.strip() and not line.startswith("#")
                ]
                self.assertGreaterEqual(len(substantive_lines), 2)

    def test_product_modeling_separates_rewrite_and_competitor_outputs(self):
        document = self.read_foundation_document("product-and-business-modeling")
        rewrite_section = self.section_text(document, "## 重写输出")
        competitor_section = self.section_text(document, "## 竞品输出")
        self.assertIn("观察不会自动成为需求", rewrite_section)
        self.assertIn("观察不会自动成为战略判断", competitor_section)

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

    def test_guide_separates_reading_order_from_execution_order(self):
        guide = self.read_guide()
        reading_order = self.section_text(guide, "### 阅读顺序")
        workflow_position = reading_order.index("(core/end-to-end-workflow.md)")
        for foundation_link in (
            "(core/goals-scope-and-completion.md)",
            "(core/authorization-privacy-and-safety.md)",
            "(core/evidence-and-confidence.md)",
            "(glossary.md)",
        ):
            with self.subTest(foundation_link=foundation_link):
                self.assertLess(
                    reading_order.index(foundation_link), workflow_position
                )

        execution_order = self.section_text(guide, "### 执行顺序")
        self.assertIn(
            "必须先完成 Phase 0，之后才可采集任何证据",
            execution_order,
        )
        self.assertIn(
            "产品与业务建模从 Phase 2 开始迭代，并在 Phase 6 综合",
            execution_order,
        )

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
