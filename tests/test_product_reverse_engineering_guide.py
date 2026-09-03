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
    "runtime-experiments": GUIDE_ROOT / "core" / "runtime-experiments.md",
    "coverage-quality-and-freeze": GUIDE_ROOT
    / "core"
    / "coverage-quality-and-freeze.md",
    "human-agent-collaboration": GUIDE_ROOT
    / "core"
    / "human-agent-collaboration.md",
}
ACCESS_TRACK_DOCUMENTS = {
    "black-box": GUIDE_ROOT / "access-tracks" / "black-box.md",
    "gray-box": GUIDE_ROOT / "access-tracks" / "gray-box.md",
    "white-box": GUIDE_ROOT / "access-tracks" / "white-box.md",
}
STACK_DOCUMENTS = {
    "delphi-desktop": GUIDE_ROOT / "stacks" / "delphi-desktop.md",
}
LINK_SOURCE_DOCUMENTS = (
    REPO_ROOT / "README.md",
    REPO_ROOT / "CONTRIBUTING.md",
    GUIDE_ROOT / "README.md",
    *FOUNDATION_DOCUMENTS.values(),
    *ACCESS_TRACK_DOCUMENTS.values(),
    *STACK_DOCUMENTS.values(),
)
ALLOWED_MATURITY_LABELS = (
    "cross-project-validated",
    "project-validated",
    "industry-established",
    "proposed",
)
CLAIM_STATUSES = {
    "observed",
    "statically-supported",
    "runtime-confirmed",
    "domain-confirmed",
    "inferred",
    "conflicting",
    "unsupported",
    "deprecated",
    "superseded",
}
CORE_RELATION_KINDS = {
    "supports",
    "contradicts",
    "exposes",
    "implements",
    "reads",
    "writes",
    "calls",
    "emits",
    "derived-from",
    "validates",
    "replaces",
}
TASK_4_DOCUMENT_NAMES = (
    "runtime-experiments",
    "coverage-quality-and-freeze",
    "human-agent-collaboration",
)
REQUIRED_DELPHI_SECTIONS = (
    "来源项目观察与证据缺口",
    "访问轨道选择",
    "项目与运行身份",
    "DPR、PAS 与 DFM 资产",
    "VCL 继承、Action 与事件",
    "DataModule、数据库与中间件",
    "报表、打印与导出",
    "动态与配置驱动调用",
    "仅编译产物与兼容性边界",
    "遗留运行实验室",
    "常见盲区与停止规则",
    "纵向追踪示例",
    "有序工作流",
)
REQUIRED_ACCESS_TRACK_SECTIONS = (
    "适用条件",
    "可用证据",
    "逐步流程",
    "能够证明",
    "不能证明",
    "升级路径",
    "停止条件",
)
ACCESS_TRACK_ENTRY_CONTRACT = (
    "- **进入/恢复门禁：** 每次进入或恢复本轨道，都必须绑定不可变的 "
    "`ART-P0-AUTH`，并验证当前 `ART-G0-AUTH` 的 `verdict` 为 `pass`；"
    "授权、版本、账号、环境、数据或动作发生变化时，必须重新授权并取得新的 "
    "`pass`，旧判定不得沿用。"
)
ACCESS_TRACK_HISTORY_CONTRACT = (
    "- **历史保留：** 新证据必须新建证据项和类型化追踪链接；已有证据、主张、"
    "状态历史和 `ART-P4-TRACE` 版本必须保留且保持可寻址，禁止原地改写或删除。"
)
ACCESS_TRACK_STOP_CONTRACT = (
    "- **立即停止：** 一旦发生授权漂移、版本不匹配、不安全写入、敏感信息泄露或"
    "环境未绑定，必须立即停止相关执行；在重新授权且新的 `ART-G0-AUTH` 判定为 "
    "`pass` 前，不得继续或恢复。"
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

    def read_access_track(self, name):
        path = ACCESS_TRACK_DOCUMENTS[name]
        self.assertTrue(path.is_file(), f"missing access track: {path}")
        return path.read_text(encoding="utf-8")

    def read_stack_document(self, name):
        path = STACK_DOCUMENTS[name]
        self.assertTrue(path.is_file(), f"missing stack document: {path}")
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

    def assert_one_nonblank_applicability_declaration(self, document):
        declaration_lines = [
            line.strip()
            for line in document.splitlines()
            if line.strip().removeprefix("**").startswith("适用范围：")
        ]
        self.assertEqual(1, len(declaration_lines))
        match = re.fullmatch(r"\*\*适用范围：\*\*\s*(\S.+)", declaration_lines[0])
        self.assertIsNotNone(match)
        self.assertTrue(match.group(1).strip())

    def assert_exact_normative_bullet(
        self, document, section_heading, contract_heading, expected
    ):
        section = self.section_text(document, section_heading)
        contract = self.section_text(section, contract_heading)
        normative_bullets = [
            line.strip()
            for line in contract.splitlines()
            if line.strip().startswith("- **")
        ]
        self.assertEqual([expected], normative_bullets)
        return contract

    def assert_access_track_normative_contracts(self, document):
        self.assert_exact_normative_bullet(
            document,
            "## 适用条件",
            "### 进入/恢复规范",
            ACCESS_TRACK_ENTRY_CONTRACT,
        )
        history_contract = self.assert_exact_normative_bullet(
            document,
            "## 升级路径",
            "### 证据升级规范",
            ACCESS_TRACK_HISTORY_CONTRACT,
        )
        stop_contract = self.assert_exact_normative_bullet(
            document,
            "## 停止条件",
            "### 安全停止规范",
            ACCESS_TRACK_STOP_CONTRACT,
        )
        for reversal in ("不保留历史", "允许原地改写", "可以删除旧"):
            self.assertNotIn(reversal, history_contract)
        for reversal in (
            "不要停止",
            "无需停止",
            "不必停止",
            "可以继续",
            "允许继续",
            "继续执行",
        ):
            self.assertNotIn(reversal, stop_contract)

    def assert_phase_summary_self_hash_invariant(self, document):
        phase_summary = self.section_text(document, "## 阶段摘要记录")
        self.assertIn("阶段摘要是独立包络", phase_summary)
        self.assertIn(
            "不得列入自身的 `output allow-list and hashes`",
            phase_summary,
        )
        self.assertIn("摘要哈希只出现在父摘要或冻结清单", phase_summary)

    def assert_acyclic_freeze_generation(self, document):
        freeze_order = self.section_text(document, "## 无环冻结生成顺序")
        ordered_outputs = (
            "content outputs",
            "child/phase summaries",
            "root summary",
            "detached freeze manifest/attestation",
        )
        positions = []
        for step, output in enumerate(ordered_outputs, start=1):
            marker = f"{step}. `{output}`"
            self.assertIn(marker, freeze_order)
            positions.append(freeze_order.index(marker))
        self.assertEqual(sorted(positions), positions)
        self.assertIn("排除自身包络和所有证明", freeze_order)
        self.assertIn("位于每个阶段摘要的输出哈希集合之外", freeze_order)
        self.assertIn("Git commit 或外部签名", freeze_order)
        self.assertIn("不得递归包含自身哈希", freeze_order)

    def assert_delphi_evidence_planes_remain_distinct(self, document):
        evidence_section = self.section_text(document, "### 证据面分离矩阵")
        expected_rows = {
            "DFM 静态属性": (
                "statically-supported",
                "",
                "不证明控件运行时可见、可用或处理器被触发",
            ),
            "通用组件能力": (
                "inferred",
                "",
                "不证明某业务窗体启用了该能力",
            ),
            "数据库聚合探针": (
                "runtime-confirmed",
                "（仅探针主张）",
                "不证明按钮、筛选、穿透、状态迁移、报表或打印行为",
            ),
            "已观察 UI 行为": (
                "runtime-confirmed",
                "（仅已回放场景）",
                "不外推到未覆盖角色、版本、配置或路径",
            ),
        }
        observed_rows = {}
        for line in evidence_section.splitlines():
            match = re.fullmatch(
                r"\| ([^|]+) \| [^|]+ \| `([^`]+)`([^|]*) \| ([^|]+) \|",
                line,
            )
            if match and match.group(1).strip() in expected_rows:
                observed_rows[match.group(1).strip()] = (
                    match.group(2).strip(),
                    match.group(3).strip(),
                    match.group(4).strip(),
                )
        self.assertEqual(expected_rows, observed_rows)
        self.assertIn(
            "数据库聚合探针通过不得把任何 UI、报表或打印主张升级为 "
            "`runtime-confirmed`。",
            evidence_section,
        )

    def assert_delphi_access_track_selection(self, document):
        selection = self.section_text(document, "## 访问轨道选择")
        self.assertIn(
            "轨道按当前已获授权且能绑定身份的可用证据选择",
            selection,
        )
        self.assertIn(
            "只有编译产物、配置、数据库或部分源码时，选择"
            "[灰盒访问轨道](../access-tracks/gray-box.md)",
            selection,
        )
        self.assertIn(
            "拥有完整源码和获准读取的构建材料时，选择"
            "[白盒访问轨道](../access-tracks/white-box.md)",
            selection,
        )
        self.assertIn("构建和运行仍须逐项授权", selection)

    def assert_delphi_report_evidence_ceilings(self, document):
        report = self.section_text(document, "## 报表、打印与导出")
        matrix = self.section_text(report, "### 报表证据上限矩阵")
        expected_rows = {
            "可见报表/打印/导出行为": (
                "runtime-confirmed",
                "只确认已测版本、角色、配置、输入与输出边界",
            ),
            "静态模板/代码结构": (
                "statically-supported",
                "不得声称未执行模板的运行行为",
            ),
            "编译产物/元数据事实": (
                "observed",
                "只证明产物事实；源码关系保持未知",
            ),
            "不完整内部链候选": (
                "inferred",
                "缺失的实现或数据边保持未知",
            ),
            "无证据内部链": (
                "unsupported",
                "不得由可见行为反推内部拓扑",
            ),
        }
        observed_rows = {}
        for line in matrix.splitlines():
            match = re.fullmatch(
                r"\| ([^|]+) \| `([^`]+)` \| [^|]+ \| ([^|]+) \|",
                line,
            )
            if match and match.group(1).strip() in expected_rows:
                observed_rows[match.group(1).strip()] = (
                    match.group(2).strip(),
                    match.group(3).strip(),
                )
        self.assertEqual(expected_rows, observed_rows)
        self.assertIn(
            "可重复、已授权并绑定捕获身份的 UI、打印或导出观察，可以在测量边界内"
            "支持可见行为的 `runtime-confirmed` 主张，即使只有编译产物。",
            report,
        )
        self.assertIn(
            "缺少模板、源码、中间件或数据库链接，只限制独立的内部实现/数据血缘"
            "主张，不得降级已经满足运行协议的可见行为主张。",
            report,
        )
        self.assertIn(
            "可见行为的运行确认不要求伪造或补齐内部链",
            report,
        )
        self.assertNotIn(
            "只有申请 `runtime-confirmed` 的具体报表主张，才必须同时具备",
            report,
        )

    def assert_delphi_topology_is_selected_not_forced(self, document):
        data_section = self.section_text(document, "## DataModule、数据库与中间件")
        topology = self.section_text(data_section, "### 拓扑分支决策表")
        expected_branches = {
            "静态菜单",
            "动态/配置菜单",
            "本地数据库/直接 DataModule",
            "中间件/RPC/API",
            "文件",
            "无数据层",
        }
        observed_branches = {
            match.group(1)
            for line in topology.splitlines()
            if (match := re.fullmatch(r"\| ([^|]+) \| .+ \|", line))
            and match.group(1) in expected_branches
        }
        self.assertEqual(expected_branches, observed_branches)
        self.assertIn(
            "只为实际遇到且有证据的层建边；缺少的层不创建占位边",
            data_section,
        )
        self.assertIn(
            "MIDAS、DCOM、Provider 和存储过程都是可选的遇见技术",
            data_section,
        )
        self.assertIn("不得把它们写成每个 Delphi 产品的必经顺序", data_section)
        workflow = self.section_text(document, "## 有序工作流")
        self.assertIn("数据目标/数据库（如存在）", workflow)
        self.assertIn("若为数据库分支才使用一次性数据库副本", workflow)
        self.assertIn("文件分支使用一次性目录", workflow)
        self.assertIn("无数据层不引入数据库", workflow)

    def assert_delphi_project_file_roles(self, document):
        assets = self.section_text(document, "## DPR、PAS 与 DFM 资产")
        for contract in (
            "DPR 的首个声明是 `program` 或 `library`",
            "DPR 不声明 `package`",
            "DPK 解析 `package`、`requires` 和 `contains`",
            "Delphi 5 常见的 DOF/CFG",
            "后续版本按实际存在解析 BDSProj/DPROJ",
            "项目 RES",
            "package 元数据",
        ):
            self.assertIn(contract, assets)

    def assert_delphi_vertical_example_contract(self, document):
        trace = self.section_text(document, "## 纵向追踪示例")
        records = self.section_text(trace, "### 示例主张与链接")
        row_pattern = re.compile(
            r"\| `([^`]+)` \| [^|]+ \| `([^`]+)` \| `([^`]+)` \| "
            r"([^|]+) \| [^|]+ \|"
        )
        rows = [
            match.groups()
            for line in records.splitlines()
            if (match := row_pattern.fullmatch(line))
        ]
        self.assertGreaterEqual(len(rows), 5)

        stable_id_pattern = re.compile(
            r"^[a-z][a-z0-9-]*:[a-z][a-z0-9-]*(?:\.[a-z0-9-]+)+$"
        )
        for stable_id, status, candidates, links in rows:
            self.assertRegex(stable_id, stable_id_pattern)
            self.assertIn(status, CLAIM_STATUSES)
            candidate_match = re.fullmatch(
                r"candidate-set=\[([^\]]*)\]; cardinality=(\d+)",
                candidates,
            )
            self.assertIsNotNone(candidate_match)
            candidate_ids = [
                candidate.strip()
                for candidate in candidate_match.group(1).split(",")
                if candidate.strip()
            ]
            self.assertEqual(len(candidate_ids), int(candidate_match.group(2)))
            for candidate_id in candidate_ids:
                self.assertRegex(candidate_id, stable_id_pattern)
            relations = re.findall(r"→ `([a-z-]+)` →", links)
            self.assertTrue(relations, f"missing typed relation in row: {stable_id}")
            self.assertTrue(set(relations).issubset(CORE_RELATION_KINDS))

        referenced_ids = re.findall(
            r"\b[a-z][a-z0-9-]*:[a-z][a-z0-9-]*(?:\.[a-z0-9-]+)+\b",
            records,
        )
        self.assertTrue(referenced_ids)
        for stable_id in referenced_ids:
            self.assertRegex(stable_id, stable_id_pattern)
        self.assertIn(
            "candidate set 与 cardinality 是独立字段，不得塞入主张状态",
            trace,
        )
        self.assertIn(
            "若需要核心词汇之外的关系，必须先登记扩展关系定义",
            trace,
        )

    def assert_deterministic_gate_record_schema(self, document):
        gate_records = self.section_text(document, "## 门禁判定记录与 Phase 产物")
        schema = self.section_text(gate_records, "### 派生门禁记录字段")
        fields = [
            match.group(1)
            for line in schema.splitlines()
            if (match := re.fullmatch(r"\| `([^`]+)` \| .+ \|", line))
        ]
        self.assertEqual(
            [
                "gate record ID",
                "gate ID",
                "schema version",
                "rule version",
                "input artifact IDs/hashes",
                "human-decision artifact IDs/hashes",
                "verdict",
                "derived reason codes",
                "generator version",
            ],
            fields,
        )
        for forbidden_metadata in (
            "reviewer",
            "approver",
            "signature",
            "approval time",
            "execution timestamp",
            "评审人",
            "批准人",
            "签名",
            "批准时间",
            "执行时间",
        ):
            self.assertNotIn(forbidden_metadata, schema)

    def test_required_entry_files_exist(self):
        for path in REQUIRED_ENTRY_FILES:
            self.assertTrue(path.is_file(), f"missing required entry file: {path}")

    def test_foundation_documents_exist(self):
        for name, path in FOUNDATION_DOCUMENTS.items():
            with self.subTest(document=name):
                self.assertTrue(path.is_file(), f"missing foundation document: {path}")

    def test_access_track_documents_exist_and_are_linked_from_the_guide(self):
        guide = self.read_guide()
        for name, path in ACCESS_TRACK_DOCUMENTS.items():
            with self.subTest(track=name):
                self.assertTrue(path.is_file(), f"missing access track: {path}")
                relative_path = path.relative_to(GUIDE_ROOT).as_posix()
                self.assertIn(f"]({relative_path})", guide)

    def test_delphi_stack_guide_exists_and_is_linked_from_the_guide_readme(self):
        guide = self.read_guide()
        path = STACK_DOCUMENTS["delphi-desktop"]
        self.assertTrue(path.is_file(), f"missing Delphi stack guide: {path}")
        relative_path = path.relative_to(GUIDE_ROOT).as_posix()
        self.assertIn(f"]({relative_path})", guide)

    def test_delphi_stack_guide_has_one_canonical_maturity_and_applicability(self):
        document = self.read_stack_document("delphi-desktop")
        maturity_declarations = [
            line.strip()
            for line in document.splitlines()
            if line.strip().removeprefix("**").startswith("证据成熟度：")
        ]
        self.assertEqual(["**证据成熟度：`proposed`**"], maturity_declarations)
        self.assert_one_nonblank_applicability_declaration(document)
        self.assertNotIn("**段落依据：`project-validated`**", document)
        self.assertIn(
            "**证据标记：`source-project-observation`；通用指南链接：`pending`**",
            document,
        )
        source_project = self.section_text(
            document, "## 来源项目观察与证据缺口"
        )
        self.assertIn("gjpERP 启发的观察", source_project)
        self.assertIn("可审计案例索引、限定稳定 ID 和输入哈希", source_project)
        self.assertIn("不能证明整页方法已完成项目验证", source_project)
        self.assertNotIn("/Users/", document)
        self.assertNotRegex(document, r"(?i)\b(?:TODO|TBD|FIXME)\b|待补(?:充|全)")

    def test_delphi_stack_guide_has_all_substantive_sections(self):
        document = self.read_stack_document("delphi-desktop")
        for section_name in REQUIRED_DELPHI_SECTIONS:
            with self.subTest(section=section_name):
                section = self.section_text(document, f"## {section_name}")
                substantive_lines = [
                    line
                    for line in section.splitlines()[1:]
                    if line.strip() and not line.startswith("#")
                ]
                self.assertGreaterEqual(
                    len(substantive_lines), 3, f"thin Delphi section: {section_name}"
                )

    def test_delphi_guide_selects_gray_or_white_track_from_available_evidence(self):
        document = self.read_stack_document("delphi-desktop")
        self.assert_delphi_access_track_selection(document)

        mutated = document.replace(
            "只有编译产物、配置、数据库或部分源码时，选择"
            "[灰盒访问轨道](../access-tracks/gray-box.md)",
            "只有编译产物、配置、数据库或部分源码时，选择"
            "[白盒访问轨道](../access-tracks/white-box.md)",
        )
        with self.assertRaises(AssertionError):
            self.assert_delphi_access_track_selection(mutated)

    def test_delphi_workflow_is_ordered_and_preserves_original_resources(self):
        document = self.read_stack_document("delphi-desktop")
        workflow = self.section_text(document, "## 有序工作流")
        steps = [
            line for line in workflow.splitlines() if re.match(r"^\d+\. ", line)
        ]
        self.assertEqual(7, len(steps))
        expected_terms = (
            (
                "可执行文件、安装包、DPR 项目、源码变体、数据目标/数据库（如存在）"
                "与组件版本",
                "SHA-256",
                "运行时身份",
            ),
            (
                "DPR",
                "窗体",
                "DataModule",
                "Frame",
                "Package",
                "资源",
                "第三方",
                "生成代码",
            ),
            ("PAS", "声明", "实现", "文本 DFM", "二进制 DFM", "不覆盖原件"),
            (
                "继承",
                "控件",
                "事件",
                "Action",
                "菜单",
                "快捷键",
                "动态创建",
            ),
            (
                "按实际依赖选择",
                "本地数据库/直接 DataModule",
                "中间件/RPC/API",
                "文件",
                "无数据层",
                "只为实际遇到",
                "不补齐不存在的层",
            ),
            ("动态数据库调用", "完全限定", "证据", "不得伪造精确调用边"),
            (
                "32 位",
                "ART-G0-AUTH",
                "pass",
                "若为数据库分支才使用一次性数据库副本",
                "文件分支使用一次性目录",
                "无数据层不引入数据库",
                "四类证据面",
            ),
        )
        for step, terms in zip(steps, expected_terms):
            for term in terms:
                with self.subTest(step=step[:2], term=term):
                    self.assertIn(term, step)

    def test_delphi_evidence_planes_are_distinct_and_reject_ui_overclaiming(self):
        document = self.read_stack_document("delphi-desktop")
        self.assert_delphi_evidence_planes_remain_distinct(document)

        mutated = document.replace(
            "数据库聚合探针通过不得把任何 UI、报表或打印主张升级为 "
            "`runtime-confirmed`。",
            "数据库聚合探针通过可以把 UI、报表和打印主张升级为 "
            "`runtime-confirmed`。",
        )
        with self.assertRaises(AssertionError):
            self.assert_delphi_evidence_planes_remain_distinct(mutated)

    def test_delphi_dynamic_calls_require_qualified_seed_evidence(self):
        document = self.read_stack_document("delphi-desktop")
        dynamic_calls = self.section_text(document, "## 动态与配置驱动调用")
        for contract in (
            "字符串 SQL 或过程名",
            "数据库驱动菜单",
            "反射",
            "动态加载",
            "调用点稳定 ID",
            "数据库类型与完全限定对象名",
            "关系类型",
            "证据位置与 SHA-256",
            "状态、置信度与验证方法",
            "候选 seed 边不等于源码中的精确直接调用边",
            "零匹配、多匹配或版本不一致必须停止自动连边",
            "不得伪造精确调用边",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, dynamic_calls)

    def test_delphi_guide_selects_only_encountered_topology_branches(self):
        document = self.read_stack_document("delphi-desktop")
        self.assert_delphi_topology_is_selected_not_forced(document)

        mutated = document.replace(
            "只为实际遇到且有证据的层建边；缺少的层不创建占位边",
            "所有产品都必须串联 DataModule、中间件、Provider 和数据库",
        )
        with self.assertRaises(AssertionError):
            self.assert_delphi_topology_is_selected_not_forced(mutated)

    def test_delphi_project_files_have_version_specific_roles(self):
        document = self.read_stack_document("delphi-desktop")
        self.assert_delphi_project_file_roles(document)

        mutated = document.replace(
            "DPR 不声明 `package`",
            "DPR 声明 `package`",
        )
        with self.assertRaises(AssertionError):
            self.assert_delphi_project_file_roles(mutated)

    def test_delphi_compiled_only_evidence_has_explicit_claim_ceiling(self):
        document = self.read_stack_document("delphi-desktop")
        compiled = self.section_text(document, "## 仅编译产物与兼容性边界")
        for artifact in ("DCU", "BPL", "DLL", "EXE", "资源"):
            with self.subTest(artifact=artifact):
                self.assertIn(f"`{artifact}`", compiled)
        for limit in (
            "反编译器与元数据工具版本",
            "Delphi 编译器版本",
            "组件版本",
            "编译选项",
            "不等价于原始源码",
            "不能证明业务意图",
            "兼容性矩阵",
        ):
            with self.subTest(limit=limit):
                self.assertIn(limit, compiled)

    def test_delphi_report_claim_ceiling_depends_on_available_evidence(self):
        document = self.read_stack_document("delphi-desktop")
        self.assert_delphi_report_evidence_ceilings(document)

        mutations = {
            "downgrades visible runtime behavior": document.replace(
                "| 可见报表/打印/导出行为 | `runtime-confirmed` |",
                "| 可见报表/打印/导出行为 | `observed` |",
            ),
            "requires internal chain for visible behavior": document.replace(
                "可见行为的运行确认不要求伪造或补齐内部链",
                "可见行为的运行确认必须补齐内部链",
            ),
            "downgrades behavior for missing internals": document.replace(
                "不得降级已经满足运行协议的可见行为主张。",
                "必须降级已经满足运行协议的可见行为主张。",
            ),
        }
        for name, mutation in mutations.items():
            with self.subTest(mutation=name):
                with self.assertRaises(AssertionError):
                    self.assert_delphi_report_evidence_ceilings(mutation)

    def test_delphi_blind_spots_and_lab_stop_rules_are_explicit(self):
        document = self.read_stack_document("delphi-desktop")
        blind_spots = self.section_text(document, "## 常见盲区与停止规则")
        for blind_spot in (
            "二进制 DFM",
            "反射/动态加载",
            "字符串 SQL/过程名",
            "版本分叉",
            "不可达/死代码",
            "设计期与运行时状态",
            "32 位会话约束",
        ):
            with self.subTest(blind_spot=blind_spot):
                self.assertRegex(blind_spots, rf"(?m)^\| {re.escape(blind_spot)} \|")
        for stop_rule in (
            "授权、身份、版本、数据库目标或隔离状态漂移时立即停止",
            "二进制 DFM 无法无损转换时保留原件并把对应字段标为 `unsupported`",
            "动态目标不能唯一解析时停止自动连边",
            "不能启动安全的 32 位会话时转入受治理的静态分支",
        ):
            self.assertIn(stop_rule, blind_spots)

    def test_delphi_vertical_example_uses_core_identity_and_status_contracts(self):
        document = self.read_stack_document("delphi-desktop")
        self.assert_delphi_vertical_example_contract(document)
        for forbidden in (
            "".join(("Tdm", "Client")),
            "SAN-MENU-01",
            "`configures`",
            "`dispatches-to`",
            "`candidate-invokes`",
        ):
            self.assertNotIn(forbidden, document)

        mutations = {
            "unqualified stable ID": document.replace(
                "claim:sample.export-visible",
                "SAN-MENU-01",
                1,
            ),
            "non-core claim status": document.replace(
                "| `claim:sample.export-visible` | 指定输入的可见导出按相同步骤重复出现 "
                "| `runtime-confirmed` |",
                "| `claim:sample.export-visible` | 指定输入的可见导出按相同步骤重复出现 "
                "| `candidate` |",
                1,
            ),
            "unregistered relation kind": document.replace(
                "→ `validates` →",
                "→ `transitions-to` →",
                1,
            ),
        }
        for name, mutation in mutations.items():
            with self.subTest(mutation=name):
                with self.assertRaises(AssertionError):
                    self.assert_delphi_vertical_example_contract(mutation)

    def test_access_tracks_have_the_exact_substantive_section_contract(self):
        maturity_pattern = re.compile(r"^\*\*证据成熟度：`([^`]+)`\*\*$")
        for name in ACCESS_TRACK_DOCUMENTS:
            with self.subTest(track=name):
                document = self.read_access_track(name)
                h2_headings = [
                    line.removeprefix("## ")
                    for line in document.splitlines()
                    if line.startswith("## ")
                ]
                self.assertEqual(list(REQUIRED_ACCESS_TRACK_SECTIONS), h2_headings)

                maturity_declarations = [
                    line.strip()
                    for line in document.splitlines()
                    if line.strip().removeprefix("**").startswith("证据成熟度：")
                ]
                self.assertEqual(1, len(maturity_declarations))
                match = maturity_pattern.fullmatch(maturity_declarations[0])
                self.assertIsNotNone(match)
                self.assertIn(match.group(1), ALLOWED_MATURITY_LABELS)
                self.assert_one_nonblank_applicability_declaration(document)

                for section_name in REQUIRED_ACCESS_TRACK_SECTIONS:
                    section = self.section_text(document, f"## {section_name}")
                    substantive_lines = [
                        line
                        for line in section.splitlines()[1:]
                        if line.strip() and not line.startswith("#")
                    ]
                    self.assertGreaterEqual(
                        len(substantive_lines),
                        2,
                        f"thin section in {name}: {section_name}",
                    )

    def test_access_tracks_use_exact_entry_history_and_stop_contracts(self):
        for name in ACCESS_TRACK_DOCUMENTS:
            with self.subTest(track=name):
                self.assert_access_track_normative_contracts(
                    self.read_access_track(name)
                )

    def test_access_track_contracts_reject_history_and_stop_semantic_reversals(self):
        document = self.read_access_track("black-box")
        self.assert_access_track_normative_contracts(document)
        mutations = {
            "negated history preservation": document.replace(
                ACCESS_TRACK_HISTORY_CONTRACT,
                "- **历史保留：** 不保留历史，允许原地改写并删除旧主张。",
            ),
            "negated immediate stop": document.replace(
                ACCESS_TRACK_STOP_CONTRACT,
                "- **立即停止：** 发生安全触发器时不要停止，可以继续执行。",
            ),
            "continued execution exception": document.replace(
                ACCESS_TRACK_STOP_CONTRACT,
                ACCESS_TRACK_STOP_CONTRACT + " 可以继续执行已开始的动作。",
            ),
        }
        for name, mutation in mutations.items():
            with self.subTest(mutation=name):
                with self.assertRaises(AssertionError):
                    self.assert_access_track_normative_contracts(mutation)

    def test_black_box_track_limits_sources_and_binds_observation_matrix(self):
        document = self.read_access_track("black-box")
        applicability = self.section_text(document, "## 适用条件")
        evidence = self.section_text(document, "## 可用证据")
        workflow = self.section_text(document, "## 逐步流程")

        for boundary in ("公开信息", "合法账号", "ART-P0-AUTH", "当前合法会话"):
            self.assertIn(boundary, applicability + evidence)
        for dimension in ("角色", "套餐", "地区/语言", "设备"):
            self.assertIn(dimension, workflow)
        for state in ("空状态", "有数据状态", "错误状态", "权限状态"):
            self.assertIn(state, workflow)
        for path in ("正常", "逆向", "负向", "边界", "重试"):
            self.assertIn(path, workflow)
        for surface in ("系统化导航", "成对动作", "导入", "导出", "通知"):
            self.assertIn(surface, workflow)
        for control in ("速率限制", "数据最小化", "浏览器", "网络"):
            self.assertIn(control, evidence + workflow)

    def test_black_box_track_guards_prohibited_actions_and_claim_ceiling(self):
        document = self.read_access_track("black-box")
        cannot_prove = self.section_text(document, "## 不能证明")
        stop = self.section_text(document, "## 停止条件")
        for prohibited in (
            "隐藏租户",
            "隐藏账号",
            "凭据提取",
            "绕过访问控制",
            "规避付费功能",
            "破坏性端点探测",
            "未授权端点探测",
        ):
            self.assertIn(prohibited, stop)
        for limit in ("内部算法", "内部数据模型", "产品事实", "战略推断"):
            self.assertIn(limit, cannot_prove)

    def test_gray_box_track_catalogs_partial_assets_and_static_limits(self):
        document = self.read_access_track("gray-box")
        evidence = self.section_text(document, "## 可用证据")
        workflow = self.section_text(document, "## 逐步流程")
        cannot_prove = self.section_text(document, "## 不能证明")
        upgrade = self.section_text(document, "## 升级路径")

        for source in (
            "软件包",
            "清单",
            "配置",
            "日志",
            "API 文档",
            "只读数据库",
            "部署元数据",
            "二进制",
            "符号元数据",
            "部分源码",
        ):
            self.assertIn(source, evidence)
        for identity in ("内容哈希", "反编译工具版本"):
            self.assertIn(identity, workflow)
        for limit in ("名称", "类型", "生成代码", "控制流", "意图"):
            self.assertIn(limit, cannot_prove)
        self.assertIn("配置存在", cannot_prove)
        self.assertIn("部署行为", cannot_prove)
        self.assertIn("黑盒事实", upgrade)

    def test_white_box_track_traces_runtime_architecture_without_overclaiming(self):
        document = self.read_access_track("white-box")
        workflow = self.section_text(document, "## 逐步流程")
        can_prove = self.section_text(document, "## 能够证明")
        cannot_prove = self.section_text(document, "## 不能证明")

        for target in (
            "构建入口",
            "运行入口",
            "依赖图",
            "路由",
            "配置优先级",
            "事务",
            "持久化",
            "异步副作用",
            "测试",
            "死代码",
            "生成代码",
            "运行确认",
        ):
            self.assertIn(target, workflow + can_prove)
        for identity in ("生产版本", "源码身份"):
            self.assertIn(identity, workflow)
        self.assertIn("代码覆盖率不等于产品覆盖率", cannot_prove)
        self.assertIn("源码分支", cannot_prove)
        self.assertIn("测试通过", cannot_prove)
        self.assertIn("部署行为", cannot_prove)

    def test_white_box_track_authorizes_operations_individually(self):
        applicability = self.section_text(
            self.read_access_track("white-box"), "## 适用条件"
        )
        authorization = self.section_text(applicability, "### 逐项授权记录")
        operation_rows = [
            match.group(1)
            for line in authorization.splitlines()
            if (
                match := re.fullmatch(
                    r"\| (源码读取|构建|静态分析|运行观察|调试|数据访问) \| .+ \|",
                    line,
                )
            )
        ]
        self.assertEqual(
            ["源码读取", "构建", "静态分析", "运行观察", "调试", "数据访问"],
            operation_rows,
        )
        self.assertIn("每项操作", authorization)
        self.assertIn("`ART-P0-AUTH`", authorization)
        self.assertIn("未获准的操作不得执行", authorization)

    def test_white_box_track_keeps_runtime_optional_with_governed_static_ceiling(self):
        applicability = self.section_text(
            self.read_access_track("white-box"), "## 适用条件"
        )
        non_runtime = self.section_text(
            applicability, "### 运行可选性与非运行分支"
        )
        for contract in (
            "运行观察不是进入白盒轨道的必需条件",
            "授权未覆盖运行",
            "无法安全运行",
            "显式选择受治理的非运行分支",
            "ART-P5-STATIC",
            "ART-P5-RUNTIME-GAP",
            "ART-P5-STATIC-ACCEPTANCE",
            "statically-supported",
            "inferred",
            "conflicting",
            "unsupported",
            "不得标为 `runtime-confirmed`",
        ):
            self.assertIn(contract, non_runtime)

    def test_readme_validation_scope_includes_core_and_access_tracks(self):
        validation = self.section_text(self.read_guide(), "## 验证")
        self.assertIn("九项核心模块和三条访问轨道", validation)

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

    def test_each_task_4_document_declares_exactly_one_nonblank_applicability(self):
        for name in TASK_4_DOCUMENT_NAMES:
            with self.subTest(document=name):
                self.assert_one_nonblank_applicability_declaration(
                    self.read_foundation_document(name)
                )

    def test_task_4_applicability_check_rejects_duplicate_and_blank_mutations(self):
        valid = "# 示例\n\n**适用范围：** 有限且明确的边界。\n"
        duplicate = valid + "\n**适用范围：** 第二个边界。\n"
        blank = valid.replace("有限且明确的边界。", "")
        for mutation in (duplicate, blank):
            with self.subTest(mutation=mutation):
                with self.assertRaises(AssertionError):
                    self.assert_one_nonblank_applicability_declaration(mutation)

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

    def test_runtime_experiments_freeze_identity_baseline_and_probe_safety(self):
        document = self.read_foundation_document("runtime-experiments")
        setup = self.section_text(document, "## 环境身份、基线与探针安全")
        for requirement in (
            "不可变环境身份",
            "基线",
            "唯一哨兵",
            "只读探针",
            "写入实验",
            "源码指纹",
            "克隆指纹",
            "专用测试账号",
            "安全克隆",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, setup)
        self.assertIn("分开批准", setup)

    def test_runtime_experiments_separate_probe_claim_boundaries(self):
        document = self.read_foundation_document("runtime-experiments")
        section = self.section_text(document, "## 三类探针与主张边界")
        probe_rows = {
            match.group(1)
            for line in section.splitlines()
            if (match := re.fullmatch(r"\| (基础设施可达性|聚合数据探针|观察到的产品行为) \| .+ \| .+ \|", line))
        }
        self.assertEqual(
            {"基础设施可达性", "聚合数据探针", "观察到的产品行为"},
            probe_rows,
        )
        self.assertIn("聚合数据探针不能升级界面或产品行为主张", section)
        self.assertIn("基础设施可达不等于产品行为成立", section)

    def test_runtime_protocol_records_observations_expectations_and_failures(self):
        document = self.read_foundation_document("runtime-experiments")
        protocol = self.section_text(document, "## 实验协议与观察记录")
        for observation in ("界面", "网络", "日志", "数据库"):
            with self.subTest(observation=observation):
                self.assertRegex(protocol, rf"(?m)^\| {observation} \|")
        for field in ("预期结果", "实际结果", "可重复步骤"):
            with self.subTest(field=field):
                self.assertIn(field, protocol)

        paths = self.section_text(document, "## 路径矩阵与首错保全")
        for path in ("负向", "边界", "并发", "重试", "故障注入", "逆向"):
            with self.subTest(path=path):
                self.assertIn(path, paths)
        self.assertIn("首个失败", paths)
        self.assertIn("不得被重试覆盖", paths)

    def test_runtime_cleanup_reproducibility_and_static_branch_are_governed(self):
        document = self.read_foundation_document("runtime-experiments")
        cleanup = self.section_text(document, "## 逆序清理、完整性与处置")
        for control in ("逆序清理", "完整性核对", "残留检查", "处置证明"):
            with self.subTest(control=control):
                self.assertIn(control, cleanup)

        reproducibility = self.section_text(document, "## 可复现性与结论状态")
        self.assertIn("另一执行者", reproducibility)
        self.assertIn("`unsupported`", reproducibility)

        static_branch = self.section_text(document, "## 非运行分支")
        for permitted_reason in (
            "授权未覆盖运行",
            "合法环境不可用",
            "依赖或硬件无法安全复现",
            "副作用无法隔离",
        ):
            with self.subTest(permitted_reason=permitted_reason):
                self.assertIn(permitted_reason, static_branch)
        for required_record in ("ART-P5-STATIC", "ART-P5-RUNTIME-GAP"):
            self.assertIn(required_record, static_branch)
        self.assertIn("不得标为 `runtime-confirmed`", static_branch)

    def test_coverage_model_defines_denominators_dimensions_and_risk_queues(self):
        document = self.read_foundation_document("coverage-quality-and-freeze")
        coverage = self.section_text(document, "## 覆盖模型：先分母后分子")
        self.assertIn("先定义分母，再计算分子", coverage)
        for dimension in (
            "结构覆盖",
            "产品覆盖",
            "语义覆盖",
            "运行时覆盖",
            "数据覆盖",
            "权限覆盖",
            "集成覆盖",
            "非功能覆盖",
            "追踪覆盖",
        ):
            with self.subTest(dimension=dimension):
                self.assertRegex(coverage, rf"(?m)^\| {dimension} \|")

        risk = self.section_text(document, "## 风险分层与未知队列")
        for risk_level in ("P0", "P1", "P2"):
            with self.subTest(risk_level=risk_level):
                self.assertRegex(risk, rf"(?m)^\| `{risk_level}` \|")
        self.assertIn("未知队列", risk)
        self.assertIn("P0/P1", risk)
        self.assertIn("书面接受", risk)

    def test_coverage_quality_defines_exact_g0_through_g7_gate_contract(self):
        document = self.read_foundation_document("coverage-quality-and-freeze")
        gates = self.section_text(document, "## G0–G7 质量门禁")
        gate_rows = [
            match.group(1)
            for line in gates.splitlines()
            if (match := re.fullmatch(r"\| `(G[0-7])` \| \S.+ \| \S.+ \|", line))
        ]
        self.assertEqual([f"G{index}" for index in range(8)], gate_rows)
        for gate in gate_rows:
            with self.subTest(gate=gate):
                row = next(line for line in gates.splitlines() if line.startswith(f"| `{gate}` |"))
                self.assertGreaterEqual(len(row.split("|")), 5)

    def test_gate_verdict_lifecycle_includes_pending_without_abusing_other_verdicts(self):
        document = self.read_foundation_document("coverage-quality-and-freeze")
        lifecycle = self.section_text(document, "## 门禁判定生命周期")
        verdicts = [
            match.group(1)
            for line in lifecycle.splitlines()
            if (match := re.fullmatch(r"\| `([a-z-]+)` \| .+ \|", line))
        ]
        self.assertEqual(
            ["pending", "pass", "fail", "not-applicable"],
            verdicts,
        )
        self.assertIn("未来但仍适用的门禁保持 `pending`", lifecycle)
        self.assertIn("不能记为 `fail` 或 `not-applicable`", lifecycle)

    def test_phase_to_gate_execution_map_matches_the_workflow(self):
        document = self.read_foundation_document("coverage-quality-and-freeze")
        mapping = self.section_text(document, "## Phase→Gate 执行映射")
        expected_rows = (
            ("Phase 0", "G0"),
            ("Phase 1", "G1"),
            ("Phase 2 + Phase 4", "G3"),
            ("Phase 3", "G2"),
            ("Phase 5", "G5"),
            ("Phase 6", "G4"),
            ("Phase 7", "G6"),
            ("Phase 8", "G7"),
            ("Phase 9", "受影响门禁"),
        )
        for phase, gate in expected_rows:
            with self.subTest(phase=phase):
                self.assertRegex(
                    mapping,
                    rf"(?m)^\| {re.escape(phase)} \| `{re.escape(gate)}` \| .+ \|$",
                )
        self.assertIn("Phase 2 后 G3 保持 `pending`", mapping)
        self.assertIn("获批非运行分支", mapping)
        self.assertIn("运行分支和获批非运行分支都必须判为 `pass` 或 `fail`", mapping)

    def test_g5_has_branch_specific_verdict_and_runtime_confirmation_status(self):
        document = self.read_foundation_document("coverage-quality-and-freeze")
        g5 = self.section_text(document, "## G5 分支判定")
        expected_rows = (
            ("运行分支", "pass/fail", "required/confirmed"),
            (
                "获批非运行分支",
                "pass/fail",
                "unavailable-with-approved-static-ceiling",
            ),
        )
        for branch, verdict, runtime_status in expected_rows:
            with self.subTest(branch=branch):
                self.assertRegex(
                    g5,
                    rf"(?m)^\| {re.escape(branch)} \| `{re.escape(verdict)}` \| `{re.escape(runtime_status)}` \| .+ \|$",
                )
        for requirement in (
            "`ART-P5-STATIC`",
            "`ART-P5-RUNTIME-GAP`",
            "`ART-P5-STATIC-ACCEPTANCE`",
            "风险接受",
            "验证上限",
            "未来验证方法",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, g5)
        self.assertIn("G5 不得使用 `not-applicable`", g5)

    def test_gate_records_derive_from_named_phase_artifacts_without_replacing_them(self):
        document = self.read_foundation_document("coverage-quality-and-freeze")
        workflow = self.read_foundation_document("end-to-end-workflow")
        records = self.section_text(document, "## 门禁判定记录与 Phase 产物")
        self.assertIn("派生判定记录", records)
        self.assertIn("绝不替代 Phase 产物", records)
        self.assertIn("第二事实权威", records)
        gate_record_rows = [
            (match.group(1), match.group(2), match.group(3))
            for line in records.splitlines()
            if (
                match := re.fullmatch(
                    r"\| `(G[0-7])` \| `(ART-G[^`]+)` \| (.+) \|", line
                )
            )
        ]
        self.assertEqual([f"G{index}" for index in range(8)], [row[0] for row in gate_record_rows])
        self.assertEqual(8, len({row[1] for row in gate_record_rows}))
        for gate, gate_record, phase_artifacts in gate_record_rows:
            referenced_artifacts = re.findall(r"`(ART-P[^`]+)`", phase_artifacts)
            with self.subTest(gate=gate, gate_record=gate_record):
                self.assertTrue(referenced_artifacts)
                for artifact in referenced_artifacts:
                    self.assertIn(f"`{artifact}`", workflow)

    def test_gate_records_verify_immutable_human_decisions_as_inputs(self):
        document = self.read_foundation_document("coverage-quality-and-freeze")
        records = self.section_text(document, "## 门禁判定记录与 Phase 产物")
        decision_inputs = {
            "G0": "ART-P0-AUTH",
            "G5": "ART-P5-STATIC-ACCEPTANCE",
            "G6": "ART-P7-ACCEPTANCE",
            "G7": "ART-P8-APPROVAL",
        }
        for gate, decision_artifact in decision_inputs.items():
            row = next(
                line for line in records.splitlines() if line.startswith(f"| `{gate}` |")
            )
            with self.subTest(gate=gate):
                self.assertIn(f"`{decision_artifact}`", row)

        boundary = self.section_text(document, "## 人类决定与派生门禁的边界")
        for contract in (
            "不可变输入",
            "规则版本",
            "不得生成评审者身份、批准时间、决定或签名",
            "派生且固定的来源元数据",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, boundary)
        self.assertIn("人工决定先于门禁判定", boundary)

    def test_derived_gate_record_schema_excludes_human_and_time_metadata(self):
        document = self.read_foundation_document("coverage-quality-and-freeze")
        self.assert_deterministic_gate_record_schema(document)

        records = self.section_text(document, "## 门禁判定记录与 Phase 产物")
        detached = self.section_text(records, "### 分离执行元数据")
        self.assertIn("执行时间", detached)
        self.assertIn("不进入确定性身份", detached)
        self.assertIn("人工决定产物 ID/哈希", detached)

    def test_gate_record_schema_rejects_reviewer_metadata_mutation(self):
        document = self.read_foundation_document("coverage-quality-and-freeze")
        mutated = document.replace(
            "| `generator version` |",
            "| `reviewer` | 人工评审者 |\n| `generator version` |",
        )
        with self.assertRaises(AssertionError):
            self.assert_deterministic_gate_record_schema(mutated)

    def test_coverage_summaries_and_freeze_are_deterministic_and_append_only(self):
        document = self.read_foundation_document("coverage-quality-and-freeze")
        summary = self.section_text(document, "## 父子汇总与确定性生成")
        for contract in (
            "父项",
            "子项",
            "确定性生成",
            "输出允许列表",
            "内容哈希",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, summary)

        freeze = self.section_text(document, "## 冻结输入、更正与指标防篡改")
        for contract in ("冻结输入", "取代", "`superseded`", "replaces"):
            with self.subTest(contract=contract):
                self.assertIn(contract, freeze)
        self.assertIn("不得删除未知项来改善指标", freeze)

    def test_phase_summary_records_have_complete_immutable_identity(self):
        document = self.read_foundation_document("coverage-quality-and-freeze")
        phase_summary = self.section_text(document, "## 阶段摘要记录")
        fields = [
            match.group(1)
            for line in phase_summary.splitlines()
            if (match := re.fullmatch(r"\| `([^`]+)` \| .+ \|", line))
        ]
        self.assertEqual(
            [
                "phase ID",
                "status",
                "target/version and scope identity",
                "frozen denominator",
                "input hashes",
                "child-summary hashes",
                "output allow-list and hashes",
                "coverage/unknown/risk counts",
                "G0–G7 gate verdicts",
                "owner",
                "timestamp",
            ],
            fields,
        )
        self.assertIn("父阶段只消费不可变子摘要", phase_summary)
        self.assertIn("不得重新解释子项事实", phase_summary)

    def test_phase_summary_excludes_its_own_hash_from_its_output_envelope(self):
        document = self.read_foundation_document("coverage-quality-and-freeze")
        self.assert_phase_summary_self_hash_invariant(document)

    def test_phase_summary_self_hash_invariant_rejects_inclusion_mutation(self):
        document = self.read_foundation_document("coverage-quality-and-freeze")
        mutated = document.replace(
            "不得列入自身的 `output allow-list and hashes`",
            "必须列入自身的 `output allow-list and hashes`",
        )
        with self.assertRaises(AssertionError):
            self.assert_phase_summary_self_hash_invariant(mutated)

    def test_freeze_generation_order_is_explicit_and_acyclic(self):
        document = self.read_foundation_document("coverage-quality-and-freeze")
        self.assert_acyclic_freeze_generation(document)

    def test_freeze_no_cycle_invariant_rejects_recursive_attestation_mutation(self):
        document = self.read_foundation_document("coverage-quality-and-freeze")
        mutated = document.replace(
            "位于每个阶段摘要的输出哈希集合之外",
            "位于每个阶段摘要的输出哈希集合之内",
        )
        with self.assertRaises(AssertionError):
            self.assert_acyclic_freeze_generation(mutated)

    def test_phase_8_artifacts_follow_detached_freeze_order(self):
        workflow = self.read_foundation_document("end-to-end-workflow")
        phase_8 = self.section_text(workflow, "### Phase 8")
        actions = self.section_text(phase_8, "#### 执行动作")
        for step, output in enumerate(
            (
                "content outputs",
                "child/phase summaries",
                "root summary",
                "detached freeze manifest/attestation",
            ),
            start=1,
        ):
            with self.subTest(step=step):
                self.assertRegex(actions, rf"(?m)^{step}\. .*`{re.escape(output)}`")

        deliverables = self.section_text(phase_8, "#### 交付物")
        for artifact in (
            "ART-P8-APPROVAL",
            "ART-P8-ROOT-SUMMARY",
            "ART-P8-FREEZE",
        ):
            with self.subTest(artifact=artifact):
                self.assertIn(f"`{artifact}`", deliverables)
        self.assertIn("分离式冻结清单/证明", deliverables)

    def test_artifact_and_summary_lifecycle_is_separate_from_claim_status(self):
        document = self.read_foundation_document("coverage-quality-and-freeze")
        lifecycle = self.section_text(document, "## 产物与摘要生命周期")
        lifecycle_values = [
            match.group(1)
            for line in lifecycle.splitlines()
            if (match := re.fullmatch(r"\| `([a-z-]+)` \| .+ \|", line))
        ]
        self.assertEqual(["active", "replaced", "withdrawn"], lifecycle_values)
        self.assertIn("`replaces`", lifecycle)
        self.assertIn("`replaced-by`", lifecycle)
        self.assertIn("独立于产品主张状态", lifecycle)
        self.assertNotRegex(lifecycle, r"(?m)^\| `superseded` \|")
        self.assertIn("产品主张的 `superseded`", lifecycle)

    def test_human_agent_collaboration_assigns_decision_rights(self):
        document = self.read_foundation_document("human-agent-collaboration")
        rights = self.section_text(document, "## 决策权矩阵")
        roles = (
            "产品/领域负责人",
            "逆向负责人",
            "技术分析师",
            "产品研究员",
            "QA/实验负责人",
            "安全/隐私负责人",
            "AI Agent",
        )
        for role in roles:
            with self.subTest(role=role):
                self.assertRegex(rights, rf"(?m)^\| {re.escape(role)} \|")

    def test_human_agent_task_packet_has_exact_required_fields(self):
        document = self.read_foundation_document("human-agent-collaboration")
        task_packet = self.section_text(document, "## 任务包契约")
        fields = [
            match.group(1)
            for line in task_packet.splitlines()
            if (match := re.fullmatch(r"\| `([^`]+)` \| .+ \|", line))
        ]
        self.assertEqual(
            [
                "objective",
                "authorization record ID + content hash/version",
                "input identity",
                "workspace root / working directory identity",
                "scope",
                "denominator",
                "allowed evidence",
                "forbidden inference",
                "output paths or record types",
                "schema",
                "validation command",
                "stop conditions",
                "review owner",
            ],
            fields,
        )

    def test_human_agent_task_packet_is_immutably_bound_to_g0_authorization(self):
        document = self.read_foundation_document("human-agent-collaboration")
        task_packet = self.section_text(document, "## 任务包契约")
        for contract in (
            "`ART-P0-AUTH`",
            "`ART-G0-AUTH`",
            "`allowed evidence` 必须是该授权记录的子集",
            "人类重新授权",
            "新的授权记录",
            "G0 再次 `pass`",
            "新的任务包",
            "分派人和评审人都无权扩大",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, task_packet)

    def test_readme_assigns_phase_7_and_phase_8_their_actual_gates(self):
        execution_order = self.section_text(self.read_guide(), "### 执行顺序")
        self.assertIn("Phase 7 执行 G6", execution_order)
        self.assertIn("Phase 8 执行 G7", execution_order)
        self.assertNotIn("Phase 7 用九类分母、风险队列和 G0–G7", execution_order)

    def test_human_agent_boundaries_keep_high_risk_decisions_human_owned(self):
        document = self.read_foundation_document("human-agent-collaboration")
        limits = self.section_text(document, "## AI Agent 能力边界")
        self.assertIn("可以报告“未找到”", limits)
        self.assertIn("不能据此推断不存在", limits)
        self.assertIn("不能作出业务最终决定", limits)

        review = self.section_text(document, "## 人工确认与发布责任")
        for decision in (
            "高风险规则",
            "证据冲突",
            "安全边界",
            "破坏性实验",
            "冻结",
        ):
            with self.subTest(decision=decision):
                self.assertIn(decision, review)

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
