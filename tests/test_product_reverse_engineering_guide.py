import copy
import json
import re
import runpy
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

import yaml
from jsonschema import (
    Draft202012Validator,
    FormatChecker,
    ValidationError,
    validators,
)
from referencing import Registry, Resource
from referencing.exceptions import NoSuchResource, Unresolvable


REPO_ROOT = Path(__file__).resolve().parents[1]
GUIDE_ROOT = REPO_ROOT / "guides" / "product-reverse-engineering"
VALIDATOR_PATH = REPO_ROOT / "tools" / "validate_product_reverse_engineering_guide.py"
BUNDLE_VALIDATOR_PATH = (
    REPO_ROOT / "tools" / "validate_product_reverse_engineering_bundle.py"
)
FIXTURE_SAFETY_PATH = REPO_ROOT / "tools" / "validate_fixture_safety.py"
REQUIRED_ENTRY_FILES = (
    REPO_ROOT / "README.md",
    REPO_ROOT / "CONTRIBUTING.md",
    GUIDE_ROOT / "README.md",
    VALIDATOR_PATH,
    BUNDLE_VALIDATOR_PATH,
    FIXTURE_SAFETY_PATH,
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
    "dotnet-backends": GUIDE_ROOT / "stacks" / "dotnet-backends.md",
    "data-messaging-and-infrastructure": GUIDE_ROOT
    / "stacks"
    / "data-messaging-and-infrastructure.md",
    "java-backends": GUIDE_ROOT / "stacks" / "java-backends.md",
    "web-products": GUIDE_ROOT / "stacks" / "web-products.md",
}
TEMPLATE_ROOT = GUIDE_ROOT / "toolkit" / "templates"
TEMPLATE_DOCUMENTS = {
    name: TEMPLATE_ROOT / f"{name}.md"
    for name in (
        "project-charter",
        "asset-record",
        "capability-record",
        "interaction-record",
        "rule-record",
        "data-object-record",
        "api-integration-record",
        "experiment-record",
        "claim-evidence-record",
        "decision-record",
        "coverage-and-freeze",
        "as-is-to-be-trace",
        "competitor-insight",
    )
}
SCHEMA_ROOT = GUIDE_ROOT / "toolkit" / "schemas"
SCHEMA_NAMES = (
    "definitions",
    "asset",
    "evidence",
    "claim",
    "trace-link",
    "experiment",
    "decision",
    "coverage-summary",
)
RECORD_SCHEMA_NAMES = tuple(name for name in SCHEMA_NAMES if name != "definitions")
SCHEMA_DOCUMENTS = {
    name: SCHEMA_ROOT / f"{name}.schema.json" for name in SCHEMA_NAMES
}
SCHEMA_EXAMPLES = {
    name: {
        validity: SCHEMA_ROOT / "examples" / f"{name}.{validity}.json"
        for validity in ("valid", "invalid")
    }
    for name in RECORD_SCHEMA_NAMES
}
SCHEMA_BASE_URI = "https://schemas.example.invalid/product-reverse-engineering/"
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
RECORD_STATUSES = {
    "draft",
    "in-review",
    "active",
    "approved",
    "frozen",
    "replaced",
    "withdrawn",
}
CONFIDENCE_LEVELS = {"low", "medium", "high"}
GATE_VERDICTS = {"pending", "pass", "fail", "not-applicable"}
STABLE_ID_PATTERN = re.compile(
    r"^[a-z][a-z0-9-]*:[a-z][a-z0-9-]*(?:\.[a-z0-9-]+)+$"
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
REQUIRED_WEB_SECTIONS = (
    "路由与产品地图",
    "渲染模式与水合",
    "DOM 与可访问性树",
    "组件、客户端状态、表单与校验",
    "当前授权会话的网络证据",
    "API、流式通信与文件传输",
    "浏览器持久状态",
    "Service Worker 与离线",
    "功能开关与实验",
    "角色、权限、租户与套餐",
    "遥测与可观测性",
    "源码、构建产物与前端制品",
    "响应式、设备、语言与时间状态",
    "证据边界与主张拆分",
    "常见盲区",
    "纵向追踪示例",
    "有序工作流",
    "停止与安全边界",
)
REQUIRED_JAVA_SECTIONS = (
    "构建与依赖图",
    "模块与启动身份",
    "框架识别与条件分支",
    "配置、Profile 与环境优先级",
    "HTTP/RPC 入口与过滤链",
    "控制器、服务与仓储边界",
    "DI、代理、AOP、反射与生成代码",
    "校验、认证与授权",
    "事务边界与传播",
    "持久化、SQL 与迁移",
    "消息、Outbox 与消费者",
    "定时任务与异步执行",
    "缓存与搜索",
    "异常映射",
    "重试、幂等与一致性",
    "仅编译制品与反编译边界",
    "运行时关联",
    "证据平面与主张上限",
    "常见盲区与停止规则",
    "纵向追踪示例",
    "有序工作流",
)
REQUIRED_DOTNET_SECTIONS = (
    "Solution、Project、TFM 与构建身份",
    "Host 启动、IIS、Kestrel 与部署身份",
    "ASP.NET Core Middleware 顺序与 Endpoint Routing",
    "传统 ASP.NET 条件分支",
    "DI 生命周期、Options 与配置优先级",
    "Controller、Minimal API 与服务边界",
    "校验、认证与授权",
    "EF、EF Core、Dapper 与手写 SQL",
    "事务、TransactionScope 与异步边界",
    "异常过滤器与协议结果",
    "Hosted Service、任务与消息",
    "WCF、Windows Service 与 COM",
    "DLL、EXE、IL 与反编译边界",
    "部署与运行时关联",
    "证据平面与主张上限",
    "常见盲区与停止规则",
    "纵向追踪示例",
    "有序工作流",
)
REQUIRED_INFRASTRUCTURE_SECTIONS = (
    "组件记录契约",
    "关系型数据库与 NoSQL",
    "缓存",
    "搜索与索引",
    "消息与 Outbox/Inbox",
    "调度任务",
    "文件与对象存储交换",
    "第三方集成与回调",
    "网关",
    "容器与编排平台",
    "秘密引用与配置边界",
    "可观测性",
    "备份与恢复",
    "所有权、一致性与失败影响",
    "配置存在与部署行为",
    "基础设施链路示例",
    "有序工作流",
    "停止与安全边界",
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
WEB_SESSION_EVIDENCE_CONTRACT = (
    "- **会话证据边界：** 只记录已授权会话与场景中实际发生、且会话持有人获准"
    "检查的请求、响应、推送与外部效应；分别记录用户动作、生命周期自动化/轮询/"
    "重连/令牌刷新/预取、服务端推送、Service Worker/后台同步、卸载遥测和第三方"
    "效应的因果 provenance，不把同一时段流量都归因于直接用户动作；继续遵守授权、"
    "速率和数据最小化边界，且不得把偶然可见端点扩展为枚举、重放或修改目标。"
)
WEB_AUTHORIZATION_CLAIM_CONTRACT = (
    "- **授权主张边界：** 前端隐藏或禁用按钮只支持该角色与状态下的界面观察，"
    "不是服务端授权证明；只验证授权内角色实际得到的允许或拒绝结果，不猜测或"
    "探测未授权资源。"
)
WEB_BUNDLE_REACHABILITY_CONTRACT = (
    "- **可达性主张边界：** bundle 中存在代码或功能开关只支持制品结构主张，"
    "不证明该能力已部署、已启用或能由当前角色到达；可见产品行为必须另有同版本"
    "运行证据。"
)
WEB_BACKEND_CLAIM_SEPARATION_CONTRACT = (
    "- **后端主张边界：** 隐藏服务端实现和数据模型始终与可见 UI 行为分立；"
    "前端证据只能支持 `inferred` 或 `unsupported`，获准后端源码/模式可支持"
    " `statically-supported`，只有绑定已部署版本、授权场景和日志/trace/运行结果"
    "的后端证据才能支持窄边界的 `runtime-confirmed`。"
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

    def read_template_document(self, name):
        path = TEMPLATE_DOCUMENTS[name]
        self.assertTrue(path.is_file(), f"missing record template: {path}")
        return path.read_text(encoding="utf-8")

    def read_json_file(self, path):
        self.assertTrue(path.is_file(), f"missing JSON file: {path}")
        with path.open(encoding="utf-8") as stream:
            return json.load(stream)

    def assert_validation_errors_without_exception(self, validator, instance):
        try:
            errors = list(validator.iter_errors(instance))
        except (TypeError, ValueError) as error:
            self.fail(f"custom semantic validator raised {type(error).__name__}: {error}")
        self.assertTrue(errors, "malformed instance should produce validation errors")

    def require_all_schemas_and_examples(self):
        paths = list(SCHEMA_DOCUMENTS.values())
        paths.extend(
            path
            for examples in SCHEMA_EXAMPLES.values()
            for path in examples.values()
        )
        if not all(path.is_file() for path in paths):
            self.skipTest("schema and fixture existence is checked separately")

    def schema_registry(self, schemas):
        def reject_remote_retrieval(uri):
            raise NoSuchResource(ref=uri)

        resources = [
            (schema["$id"], Resource.from_contents(schema))
            for schema in schemas.values()
        ]
        return Registry(retrieve=reject_remote_retrieval).with_resources(resources)

    def schema_validator(self, name, schemas=None):
        if schemas is None:
            schemas = {
                schema_name: self.read_json_file(path)
                for schema_name, path in SCHEMA_DOCUMENTS.items()
            }

        def coverage_buckets_fit_denominator(
            validator, enabled, instance, schema
        ):
            bucket_names = (
                "numerator",
                "unknown_count",
                "conflicting_count",
                "excluded_count",
            )
            if not enabled or not isinstance(instance, dict):
                return
            denominator = instance.get("denominator")
            buckets = [instance.get(bucket) for bucket in bucket_names]
            if type(denominator) is not int or not all(
                type(bucket) is int for bucket in buckets
            ):
                return
            if sum(buckets) != denominator:
                yield ValidationError(
                    "numerator + unknown_count + conflicting_count + "
                    "excluded_count must equal denominator"
                )

        def experiment_artifacts_are_bound(validator, enabled, instance, schema):
            if not enabled or not isinstance(instance, dict):
                return

            def parse_timestamp(value):
                if not isinstance(value, str):
                    return None
                try:
                    parsed = datetime.fromisoformat(
                        value.replace("Z", "+00:00")
                    )
                except (ValueError, OverflowError):
                    return None
                if parsed.tzinfo is None or parsed.utcoffset() is None:
                    return None
                return parsed

            protocol = instance.get("protocol")
            if not isinstance(protocol, dict):
                return
            expected_reference = {
                "protocol_id": protocol.get("artifact_id"),
                "protocol_content_hash": protocol.get("content_hash"),
            }
            artifacts = [
                instance.get(artifact_name)
                for artifact_name in ("protocol", "result", "effects")
            ]
            complete_artifacts = [
                artifact for artifact in artifacts if isinstance(artifact, dict)
            ]
            artifact_ids = [
                artifact.get("artifact_id")
                for artifact in complete_artifacts
                if isinstance(artifact.get("artifact_id"), str)
            ]
            artifact_hashes = [
                artifact.get("content_hash")
                for artifact in complete_artifacts
                if isinstance(artifact.get("content_hash"), str)
            ]
            if len(artifact_ids) != len(set(artifact_ids)):
                yield ValidationError("experiment artifact IDs must be unique")
            if len(artifact_hashes) != len(set(artifact_hashes)):
                yield ValidationError("experiment artifact hashes must be unique")
            if protocol.get("record_id") != protocol.get("artifact_id"):
                yield ValidationError(
                    "protocol record_id must equal its artifact_id"
                )
            claim_references = protocol.get("claim_references")
            target_claim_references = protocol.get("target_claim_references")
            if isinstance(claim_references, list) and isinstance(
                target_claim_references, list
            ) and all(
                isinstance(reference, str)
                for reference in (*claim_references, *target_claim_references)
            ):
                if not set(target_claim_references).issubset(
                    set(claim_references)
                ):
                    yield ValidationError(
                        "target claims must be declared by the protocol"
                    )
            for artifact_name in ("result", "effects"):
                artifact = instance.get(artifact_name)
                if not isinstance(artifact, dict):
                    continue
                if artifact.get("protocol_reference") != expected_reference:
                    yield ValidationError(
                        f"{artifact_name} must reference the exact frozen protocol"
                    )
                for context_key in ("product_version", "scope_or_module"):
                    if artifact.get(context_key) != protocol.get(context_key):
                        yield ValidationError(
                            f"{artifact_name}.{context_key} must equal protocol.{context_key}"
                        )

            def inner_evidence_references(value):
                if isinstance(value, dict):
                    for key, child in value.items():
                        if key in {
                            "evidence_references",
                            "disposition_proof_references",
                        } and isinstance(child, list):
                            yield from child
                        elif key == "evidence_id" and isinstance(child, str):
                            yield child
                        else:
                            yield from inner_evidence_references(child)
                elif isinstance(value, list):
                    for child in value:
                        yield from inner_evidence_references(child)

            for artifact_name in ("protocol", "result", "effects"):
                artifact = instance.get(artifact_name)
                if not isinstance(artifact, dict):
                    continue
                evidence_references = artifact.get("evidence_references")
                method_definitions = artifact.get("method_definitions")
                evidence_method_entries = artifact.get(
                    "evidence_method_entries"
                )
                if (
                    isinstance(evidence_references, list)
                    and isinstance(method_definitions, list)
                    and isinstance(evidence_method_entries, list)
                ):
                    method_ids = [
                        method.get("method_id")
                        for method in method_definitions
                        if isinstance(method, dict)
                        and isinstance(method.get("method_id"), str)
                    ]
                    mapped_evidence_ids = [
                        entry.get("evidence_id")
                        for entry in evidence_method_entries
                        if isinstance(entry, dict)
                        and isinstance(entry.get("evidence_id"), str)
                    ]
                    mapped_method_ids = {
                        entry.get("method_id")
                        for entry in evidence_method_entries
                        if isinstance(entry, dict)
                        and isinstance(entry.get("method_id"), str)
                    }
                    if len(method_ids) != len(set(method_ids)):
                        yield ValidationError(
                            f"{artifact_name} method IDs must be unique"
                        )
                    if all(
                        isinstance(reference, str)
                        for reference in evidence_references
                    ) and (
                        set(evidence_references) != set(mapped_evidence_ids)
                        or len(mapped_evidence_ids)
                        != len(set(mapped_evidence_ids))
                    ):
                        yield ValidationError(
                            f"{artifact_name} evidence must map exactly once"
                        )
                    if set(method_ids) != mapped_method_ids:
                        yield ValidationError(
                            f"{artifact_name} mapped methods must equal declared methods"
                        )
                declared = (
                    set(evidence_references)
                    if isinstance(evidence_references, list)
                    and all(
                        isinstance(reference, str)
                        for reference in evidence_references
                    )
                    else None
                )
                nested_payload = {
                    key: value
                    for key, value in artifact.items()
                    if key != "evidence_references"
                }
                nested_references = list(
                    inner_evidence_references(nested_payload)
                )
                undeclared = (
                    set(nested_references) - declared
                    if declared is not None
                    and all(
                        isinstance(reference, str)
                        for reference in nested_references
                    )
                    else set()
                )
                if declared is not None and undeclared:
                    yield ValidationError(
                        f"{artifact_name} contains evidence references absent from its top-level index"
                    )

            result = instance.get("result")
            if isinstance(result, dict):
                primary_runs = result.get("run_results")
                independent_runs = result.get("independent_reproduction_results")
                runs = []
                for list_name in (
                    "run_results",
                    "independent_reproduction_results",
                ):
                    run_list = result.get(list_name)
                    if isinstance(run_list, list):
                        runs.extend(
                            run for run in run_list if isinstance(run, dict)
                        )
                run_ids = [
                    run.get("run_id")
                    for run in runs
                    if isinstance(run.get("run_id"), str)
                ]
                if len(run_ids) != len(set(run_ids)):
                    yield ValidationError("experiment run IDs must be unique")
                if isinstance(primary_runs, list) and isinstance(
                    independent_runs, list
                ):
                    primary_executors = {
                        run.get("executor")
                        for run in primary_runs
                        if isinstance(run, dict)
                        and isinstance(run.get("executor"), str)
                    }
                    independent_executors = {
                        run.get("executor")
                        for run in independent_runs
                        if isinstance(run, dict)
                        and isinstance(run.get("executor"), str)
                    }
                    if primary_executors & independent_executors:
                        yield ValidationError(
                            "independent reproduction must use a different executor"
                        )
                reproduction_criteria = protocol.get("reproduction_criteria")
                if isinstance(reproduction_criteria, dict):
                    required_runs = reproduction_criteria.get("required_runs")
                    if type(required_runs) is int and len(runs) < required_runs:
                        yield ValidationError(
                            "declared runs must satisfy reproduction criteria"
                        )
                failed_run_ids = []
                failed_run_count = 0
                parsed_failed_runs = []
                parsed_runs = []
                for sequence, run in enumerate(runs):
                    started_at = run.get("started_at")
                    ended_at = run.get("ended_at")
                    start = parse_timestamp(started_at)
                    end = parse_timestamp(ended_at)
                    if isinstance(started_at, str) and start is None:
                        yield ValidationError(
                            "run started_at must be a timezone-aware timestamp"
                        )
                    if isinstance(ended_at, str) and end is None:
                        yield ValidationError(
                            "run ended_at must be a timezone-aware timestamp"
                        )
                    if start is not None and end is not None:
                        if end < start:
                            yield ValidationError(
                                "run ended_at must not precede started_at"
                            )
                        run_id = run.get("run_id")
                        if isinstance(run_id, str):
                            parsed_runs.append(
                                (sequence, run_id, start, end)
                            )
                    run_result = run.get("result")
                    if isinstance(run_result, str) and run_result in {
                        "failed",
                        "mixed",
                    }:
                        failed_run_count += 1
                        run_id = run.get("run_id")
                        if isinstance(run_id, str):
                            failed_run_ids.append(run_id)
                            if start is not None and end is not None:
                                parsed_failed_runs.append(
                                    (sequence, run_id, start, end)
                                )
                        observations = run.get("actual_observations")
                        evidence = run.get("evidence_references")
                        if not isinstance(observations, list) or not observations:
                            yield ValidationError(
                                "failed or mixed run requires actual observations"
                            )
                        if not isinstance(evidence, list) or not evidence:
                            yield ValidationError(
                                "failed or mixed run requires evidence references"
                            )

                first_failure = result.get("first_failure")
                if isinstance(first_failure, dict):
                    failure_run_id = first_failure.get("run_id")
                    if first_failure.get("present") is True:
                        if not isinstance(failure_run_id, str) or (
                            failure_run_id not in failed_run_ids
                        ):
                            yield ValidationError(
                                "first_failure.run_id must resolve to a failed or mixed run"
                            )
                        if first_failure.get("preserved_before_retry") is not True:
                            yield ValidationError(
                                "first failure must be preserved before retry"
                            )
                        if (
                            failed_run_count > 0
                            and len(parsed_failed_runs) == failed_run_count
                        ):
                            earliest_failure = min(
                                parsed_failed_runs,
                                key=lambda item: (item[2], item[0]),
                            )
                            (
                                earliest_sequence,
                                earliest_run_id,
                                earliest_start,
                                earliest_end,
                            ) = earliest_failure
                            if failure_run_id != earliest_run_id:
                                yield ValidationError(
                                    "first_failure.run_id must identify the earliest failed or mixed run"
                                )
                            captured_value = first_failure.get("captured_at")
                            captured_at = parse_timestamp(captured_value)
                            if isinstance(captured_value, str) and captured_at is None:
                                yield ValidationError(
                                    "first_failure.captured_at must be a timezone-aware timestamp"
                                )
                            if captured_at is not None:
                                if not earliest_start <= captured_at <= earliest_end:
                                    yield ValidationError(
                                        "first_failure.captured_at must fall within the earliest failed run"
                                    )
                                subsequent_starts = [
                                    run_start
                                    for (
                                        sequence,
                                        _run_id,
                                        run_start,
                                        _run_end,
                                    ) in parsed_runs
                                    if sequence > earliest_sequence
                                    and run_start > earliest_start
                                ]
                                if any(
                                    captured_at >= retry_start
                                    for retry_start in subsequent_starts
                                ):
                                    yield ValidationError(
                                        "first failure must be captured before any subsequent retry starts"
                                    )
                    elif failed_run_ids:
                        yield ValidationError(
                            "failed or mixed runs require first_failure.present true"
                        )

            effects = instance.get("effects")
            if isinstance(effects, dict):
                effect_records = effects.get("side_effect_records")
                if isinstance(effect_records, list):
                    for effect in effect_records:
                        if not isinstance(effect, dict):
                            continue
                        occurred = effect.get("occurred")
                        disposition = effect.get("disposition")
                        if occurred is True and isinstance(disposition, str) and (
                            disposition == "not-created"
                        ):
                            yield ValidationError(
                                "an occurred side effect cannot be not-created"
                            )
                        if occurred is False and isinstance(disposition, str) and (
                            disposition != "not-created"
                        ):
                            yield ValidationError(
                                "a side effect that did not occur must be not-created"
                            )

        def coverage_gates_are_consistent(validator, enabled, instance, schema):
            if not enabled or not isinstance(instance, dict):
                return
            gates = instance.get("gates")
            if not isinstance(gates, dict):
                return
            evidence_references = instance.get("evidence_references")
            method_definitions = instance.get("method_definitions")
            evidence_method_entries = instance.get("evidence_method_entries")
            if (
                isinstance(evidence_references, list)
                and all(isinstance(item, str) for item in evidence_references)
                and isinstance(method_definitions, list)
                and isinstance(evidence_method_entries, list)
            ):
                method_ids = [
                    method.get("method_id")
                    for method in method_definitions
                    if isinstance(method, dict)
                    and isinstance(method.get("method_id"), str)
                ]
                mapped_evidence_ids = [
                    entry.get("evidence_id")
                    for entry in evidence_method_entries
                    if isinstance(entry, dict)
                    and isinstance(entry.get("evidence_id"), str)
                ]
                mapped_method_ids = [
                    entry.get("method_id")
                    for entry in evidence_method_entries
                    if isinstance(entry, dict)
                    and isinstance(entry.get("method_id"), str)
                ]
                if (
                    len(method_ids) != len(set(method_ids))
                    or set(method_ids) != set(mapped_method_ids)
                ):
                    yield ValidationError(
                        "coverage methods must be unique and fully mapped"
                    )
                if (
                    len(mapped_evidence_ids) != len(set(mapped_evidence_ids))
                    or set(evidence_references) != set(mapped_evidence_ids)
                ):
                    yield ValidationError(
                        "coverage evidence must map exactly once"
                    )
            gate_record_ids = []
            for expected_gate_id, gate in gates.items():
                if not isinstance(gate, dict):
                    continue
                if gate.get("gate_id") != expected_gate_id:
                    yield ValidationError(
                        f"{expected_gate_id}.gate_id must equal {expected_gate_id}"
                    )
                reference = gate.get("gate_record_reference")
                if isinstance(reference, dict):
                    record_id = reference.get("id")
                    if isinstance(record_id, str):
                        gate_record_ids.append(record_id)
                gate_evidence = gate.get("evidence_references")
                if (
                    isinstance(evidence_references, list)
                    and all(
                        isinstance(item, str) for item in evidence_references
                    )
                    and isinstance(gate_evidence, list)
                    and all(isinstance(item, str) for item in gate_evidence)
                    and not set(gate_evidence).issubset(
                        set(evidence_references)
                    )
                ):
                    yield ValidationError(
                        f"{expected_gate_id} evidence must resolve in the summary index"
                    )
            if len(gate_record_ids) != len(set(gate_record_ids)):
                yield ValidationError(
                    "different gates must not reuse a gate record ID"
                )
            dimensions = instance.get("dimensions")
            runtime = (
                dimensions.get("runtime")
                if isinstance(dimensions, dict)
                else None
            )
            g5 = gates.get("G5")
            if not isinstance(runtime, dict) or not isinstance(g5, dict):
                return
            unknown_count = runtime.get("unknown_count")
            conflicting_count = runtime.get("conflicting_count")
            static_coverage = g5.get("static_non_runtime_coverage")
            if (
                type(unknown_count) is not int
                or type(conflicting_count) is not int
                or not isinstance(static_coverage, dict)
            ):
                return
            unresolved_runtime = unknown_count + conflicting_count
            gap_count = static_coverage.get("gap_count")
            selected_branch = g5.get("selected_branch")
            verdict = g5.get("verdict")
            if (
                selected_branch == "approved-static"
                and type(gap_count) is int
                and gap_count != unresolved_runtime
            ):
                yield ValidationError(
                    "approved-static G5 gap_count must equal runtime unknown_count "
                    "+ conflicting_count"
                )
            if (
                selected_branch == "runtime"
                and verdict == "pass"
                and unresolved_runtime != 0
            ):
                yield ValidationError(
                    "runtime G5 pass requires zero unknown and conflicting items"
                )

        def chosen_alternative_is_declared(validator, enabled, instance, schema):
            if not enabled or not isinstance(instance, dict):
                return
            alternatives = instance.get("alternatives")
            if not isinstance(alternatives, list):
                return
            declared = {
                alternative.get("alternative_id")
                for alternative in alternatives
                if isinstance(alternative, dict)
                and isinstance(alternative.get("alternative_id"), str)
            }
            alternative_ids = [
                alternative.get("alternative_id")
                for alternative in alternatives
                if isinstance(alternative, dict)
                and isinstance(alternative.get("alternative_id"), str)
            ]
            if len(alternative_ids) != len(set(alternative_ids)):
                yield ValidationError("alternative_id values must be unique")
            chosen_outcome = instance.get("chosen_outcome")
            if isinstance(chosen_outcome, str) and chosen_outcome not in declared:
                yield ValidationError(
                    "chosen_outcome must resolve to a declared alternative_id"
                )
            if instance.get("supersedes_decision_id") == instance.get(
                "record_id"
            ):
                yield ValidationError("a decision must not supersede itself")

        contract_validator = validators.extend(
            Draft202012Validator,
            {
                "x-coverage-buckets-fit-denominator": (
                    coverage_buckets_fit_denominator
                ),
                "x-experiment-artifacts-are-bound": experiment_artifacts_are_bound,
                "x-coverage-gates-are-consistent": coverage_gates_are_consistent,
                "x-chosen-alternative-is-declared": (
                    chosen_alternative_is_declared
                ),
            },
        )
        return contract_validator(
            schemas[name],
            registry=self.schema_registry(schemas),
            format_checker=FormatChecker(),
        )

    def require_all_templates(self):
        if not all(path.is_file() for path in TEMPLATE_DOCUMENTS.values()):
            self.skipTest("template existence contract is checked separately")

    def yaml_metadata_block(self, document):
        match = re.search(r"(?ms)^```yaml\n(.+?)\n```$", document)
        self.assertIsNotNone(match, "missing copyable YAML metadata block")
        return match.group(1)

    def yaml_metadata_blocks(self, document):
        blocks = re.findall(r"(?ms)^```yaml\n(.+?)\n```$", document)
        self.assertTrue(blocks, "missing copyable YAML metadata blocks")
        return blocks

    def parse_yaml_block(self, block):
        try:
            metadata = yaml.safe_load(block)
        except yaml.YAMLError as error:
            raise AssertionError(f"invalid YAML metadata: {error}") from error
        self.assertIsInstance(metadata, dict)
        self.assertTrue(metadata)
        return metadata

    def parse_yaml_metadata(self, document):
        return self.parse_yaml_block(self.yaml_metadata_block(document))

    def parse_all_yaml_metadata(self, document):
        return [
            self.parse_yaml_block(block)
            for block in self.yaml_metadata_blocks(document)
        ]

    def assert_qualified_references(self, references, expected_prefix=None):
        self.assertIsInstance(references, list)
        for reference in references:
            self.assertIsInstance(reference, str)
            self.assertRegex(reference, STABLE_ID_PATTERN)
            if expected_prefix:
                self.assertTrue(reference.startswith(f"{expected_prefix}:"))

    def assert_common_record_metadata(self, metadata):
        required = {
            "record_id",
            "status",
            "evidence_references",
            "owner",
            "validation_method",
            "last_updated",
            "method_definitions",
            "evidence_method_entries",
        }
        self.assertTrue(required.issubset(metadata))
        for key in (
            "record_id",
            "owner",
            "last_updated",
        ):
            self.assertIsInstance(metadata[key], str)
            self.assertTrue(metadata[key].strip())
        if "version_scope" in metadata:
            self.assertIsInstance(metadata["version_scope"], dict)
            self.assertTrue(
                {"product_version", "scope_or_module"}.issubset(
                    metadata["version_scope"]
                )
            )
        else:
            self.assertTrue(
                {"product_version", "scope_or_module"}.issubset(metadata)
            )
            for key in ("product_version", "scope_or_module"):
                self.assertIsInstance(metadata[key], str)
                self.assertTrue(metadata[key].strip())
        validation_method = metadata["validation_method"]
        if isinstance(validation_method, dict):
            self.assertEqual(
                {"method_id", "description", "reproducible"},
                set(validation_method),
            )
        else:
            self.assertIsInstance(validation_method, str)
            self.assertTrue(validation_method.strip())
        self.assertIn(metadata["status"], RECORD_STATUSES)
        self.assertNotIn("method_maturity", metadata)
        self.assert_qualified_references(
            metadata["evidence_references"], "evidence"
        )

        methods = metadata["method_definitions"]
        self.assertIsInstance(methods, list)
        self.assertTrue(methods)
        method_ids = set()
        for method in methods:
            self.assertIsInstance(method, dict)
            self.assertTrue({"method_id", "method_maturity"}.issubset(method))
            self.assertRegex(method["method_id"], STABLE_ID_PATTERN)
            self.assertTrue(method["method_id"].startswith("method:"))
            self.assertIn(method["method_maturity"], ALLOWED_MATURITY_LABELS)
            method_ids.add(method["method_id"])
        self.assertEqual(len(methods), len(method_ids))
        maturity_locations = []

        def find_maturity_locations(value, path=()):
            if isinstance(value, dict):
                for key, child in value.items():
                    child_path = (*path, key)
                    if key == "method_maturity":
                        maturity_locations.append(child_path)
                    find_maturity_locations(child, child_path)
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    find_maturity_locations(child, (*path, index))

        find_maturity_locations(metadata)
        self.assertEqual(
            {
                ("method_definitions", index, "method_maturity")
                for index in range(len(methods))
            },
            set(maturity_locations),
        )

        mappings = metadata["evidence_method_entries"]
        self.assertIsInstance(mappings, list)
        self.assertTrue(mappings)
        evidence_ids = set(metadata["evidence_references"])
        mapped_evidence_ids = set()
        for mapping in mappings:
            self.assertIsInstance(mapping, dict)
            self.assertEqual({"evidence_id", "method_id"}, set(mapping))
            self.assertIn(mapping["evidence_id"], evidence_ids)
            self.assertIn(mapping["method_id"], method_ids)
            mapped_evidence_ids.add(mapping["evidence_id"])
        self.assertEqual(evidence_ids, mapped_evidence_ids)

    def assert_composite_template_metadata(self, metadata):
        self.assert_common_record_metadata(metadata)
        self.assertIn("claim_references", metadata)
        self.assert_qualified_references(metadata["claim_references"], "claim")
        for forbidden_truth_field in (
            "atomic_claims",
            "claim",
            "claims",
            "claim_statement",
            "claim_status",
            "confidence",
            "confidence_rationale",
            "supporting_evidence_references",
            "contradicting_evidence_references",
        ):
            self.assertNotIn(forbidden_truth_field, metadata)

    def assert_claim_evidence_template_metadata(self, metadata):
        self.assert_common_record_metadata(metadata)
        required = {
            "claim_id",
            "claim_statement",
            "claim_status",
            "confidence",
            "confidence_rationale",
            "supporting_evidence_references",
            "contradicting_evidence_references",
        }
        self.assertTrue(required.issubset(metadata))
        self.assertRegex(metadata["claim_id"], STABLE_ID_PATTERN)
        self.assertTrue(metadata["claim_id"].startswith("claim:"))
        self.assertIsInstance(metadata["claim_statement"], str)
        self.assertTrue(metadata["claim_statement"].strip())
        self.assertIn(metadata["claim_status"], CLAIM_STATUSES)
        self.assertIn(metadata["confidence"], CONFIDENCE_LEVELS)
        self.assertIsInstance(metadata["confidence_rationale"], str)
        evidence_ids = set(metadata["evidence_references"])
        for relation_key in (
            "supporting_evidence_references",
            "contradicting_evidence_references",
        ):
            self.assert_qualified_references(metadata[relation_key], "evidence")
            self.assertTrue(set(metadata[relation_key]).issubset(evidence_ids))
        self.assertEqual(
            evidence_ids,
            set(metadata["supporting_evidence_references"])
            | set(metadata["contradicting_evidence_references"]),
        )

    def assert_coverage_gate_metadata(self, metadata):
        gates = metadata.get("gates")
        self.assertIsInstance(gates, dict)
        self.assertEqual({f"G{index}" for index in range(8)}, set(gates))
        gate_record_references = []
        for gate_id, gate in gates.items():
            self.assertIsInstance(gate, dict)
            expected_fields = {
                "gate_id",
                "gate_record_reference",
                "verdict",
                "reviewer",
                "decided_at",
                "evidence_references",
                "not_applicable_approval",
            }
            if gate_id == "G5":
                expected_fields |= {
                    "selected_branch",
                    "runtime_confirmation_status",
                    "static_non_runtime_coverage",
                }
            self.assertEqual(
                expected_fields,
                set(gate),
            )
            allowed_verdicts = GATE_VERDICTS - (
                {"not-applicable"} if gate_id == "G5" else set()
            )
            self.assertIn(gate["verdict"], allowed_verdicts)
            self.assertEqual(gate_id, gate["gate_id"])
            self.assertIsInstance(gate["gate_record_reference"], dict)
            self.assertEqual(
                {"id", "sha256"}, set(gate["gate_record_reference"])
            )
            for identity_part in gate["gate_record_reference"].values():
                self.assertIsInstance(identity_part, str)
                self.assertTrue(identity_part.strip())
            gate_record_references.append(gate["gate_record_reference"]["id"])
            self.assertIsInstance(gate["reviewer"], str)
            self.assertTrue(gate["reviewer"].strip())
            if gate["verdict"] == "pending":
                self.assertIsNone(gate["decided_at"])
            else:
                self.assertIsInstance(gate["decided_at"], str)
                self.assertTrue(gate["decided_at"].strip())
            self.assert_qualified_references(
                gate["evidence_references"], "evidence"
            )
            self.assertTrue(
                set(gate["evidence_references"]).issubset(
                    set(metadata["evidence_references"])
                )
            )
            if gate["verdict"] == "not-applicable":
                self.assertIsInstance(gate["not_applicable_approval"], dict)
            else:
                self.assertIsNone(gate["not_applicable_approval"])
            if gate_id == "G5":
                self.assert_g5_branch_combination(gate)
        self.assertEqual(
            len(gate_record_references), len(set(gate_record_references))
        )

    def assert_g5_branch_combination(self, gate):
        self.assertIn(gate["selected_branch"], {"runtime", "approved-static"})
        self.assertIn(
            gate["runtime_confirmation_status"],
            {
                "required",
                "confirmed",
                "unavailable-with-approved-static-ceiling",
            },
        )
        coverage = gate["static_non_runtime_coverage"]
        self.assertIsInstance(coverage, dict)
        self.assertEqual(
            {"gap_artifact_reference", "gap_count"}, set(coverage)
        )
        self.assertIsInstance(coverage["gap_count"], int)
        self.assertGreaterEqual(coverage["gap_count"], 0)

        combination = (
            gate["selected_branch"],
            gate["verdict"],
            gate["runtime_confirmation_status"],
        )
        self.assertIn(
            combination,
            {
                ("runtime", "pending", "required"),
                ("runtime", "fail", "required"),
                ("runtime", "pass", "confirmed"),
                (
                    "approved-static",
                    "pending",
                    "unavailable-with-approved-static-ceiling",
                ),
                (
                    "approved-static",
                    "pass",
                    "unavailable-with-approved-static-ceiling",
                ),
                (
                    "approved-static",
                    "fail",
                    "unavailable-with-approved-static-ceiling",
                ),
            },
        )
        gap_reference = coverage["gap_artifact_reference"]
        if gate["selected_branch"] == "runtime":
            self.assertIsNone(gap_reference)
            self.assertEqual(0, coverage["gap_count"])
        else:
            self.assertIsInstance(gap_reference, dict)
            self.assertEqual({"id", "sha256"}, set(gap_reference))
            for identity_part in gap_reference.values():
                self.assertIsInstance(identity_part, str)
                self.assertTrue(identity_part.strip())
            self.assertGreaterEqual(coverage["gap_count"], 1)

    def assert_experiment_protocol_metadata(self, metadata):
        required = {
            "fingerprints",
            "action_permissions",
            "operational_limits",
            "recovery",
            "target_claim_references",
            "protocol_frozen_at",
            "role_and_test_account",
            "inputs",
            "alternative_explanations",
            "variables",
            "wait_conditions",
            "tool_versions",
            "forbidden_side_effects",
            "reproduction_criteria",
            "protocol_steps",
            "expected_observations",
            "authorization_record_id",
            "authorization_gate_record_id",
            "environment_identity",
            "pre_state_fingerprint",
            "sentinel",
        }
        self.assertTrue(required.issubset(metadata))
        self.assertEqual(
            {"source", "artifact", "clone"}, set(metadata["fingerprints"])
        )
        for fingerprint in metadata["fingerprints"].values():
            self.assertIsInstance(fingerprint, str)
            self.assertTrue(fingerprint.strip())
        permissions = metadata["action_permissions"]
        self.assertEqual(
            {"read", "write", "fault-injection", "egress", "cleanup"},
            set(permissions),
        )
        for permission in permissions.values():
            self.assertIsInstance(permission, dict)
            self.assertEqual({"verdict", "authorization_reference"}, set(permission))
            self.assertIn(
                permission["verdict"],
                {"authorized", "not-authorized", "not-applicable"},
            )
            self.assertIsInstance(permission["authorization_reference"], str)
            self.assertTrue(permission["authorization_reference"].strip())
        self.assertEqual(
            {"cost", "rate", "blast_radius"},
            set(metadata["operational_limits"]),
        )
        for limit in metadata["operational_limits"].values():
            self.assertIsInstance(limit, str)
            self.assertTrue(limit.strip())
        self.assertEqual(
            {"recovery_point", "owner", "max_restore_time"},
            set(metadata["recovery"]),
        )
        for recovery_field in metadata["recovery"].values():
            self.assertIsInstance(recovery_field, str)
            self.assertTrue(recovery_field.strip())
        self.assert_qualified_references(
            metadata["target_claim_references"], "claim"
        )
        self.assertIsInstance(metadata["protocol_frozen_at"], str)
        self.assertTrue(metadata["protocol_frozen_at"].strip())
        self.assertEqual(
            {"role", "test_account_id"}, set(metadata["role_and_test_account"])
        )
        for value in metadata["role_and_test_account"].values():
            self.assertIsInstance(value, str)
            self.assertTrue(value.strip())
        for identity_key in (
            "authorization_record_id",
            "authorization_gate_record_id",
            "environment_identity",
            "pre_state_fingerprint",
            "sentinel",
        ):
            self.assertIsInstance(metadata[identity_key], str)
            self.assertTrue(metadata[identity_key].strip())
        structured_lists = {
            "alternative_explanations": {
                "explanation_id",
                "statement",
                "distinguishing_evidence_needed",
            },
            "variables": {"name", "controlled_value", "uncontrolled_limit"},
            "wait_conditions": {"condition", "timeout", "on_timeout"},
            "tool_versions": {"tool", "version", "configuration_hash"},
            "forbidden_side_effects": {"effect", "detection", "stop_response"},
            "protocol_steps": {
                "step_id",
                "action",
                "input",
                "observation_points",
                "stop_condition",
            },
            "expected_observations": {
                "observation_id",
                "surface",
                "expected",
                "tolerance",
            },
            "inputs": {"input_id", "value_or_fingerprint", "data_classification"},
        }
        for list_key, item_keys in structured_lists.items():
            self.assertIsInstance(metadata[list_key], list)
            self.assertTrue(metadata[list_key])
            for item in metadata[list_key]:
                self.assertIsInstance(item, dict)
                self.assertEqual(item_keys, set(item))
        self.assertEqual(
            {
                "required_runs",
                "independent_executor_required",
                "environment_equivalence_rule",
                "tolerance_rule",
            },
            set(metadata["reproduction_criteria"]),
        )
        self.assertIsInstance(metadata["reproduction_criteria"]["required_runs"], int)
        self.assertGreaterEqual(metadata["reproduction_criteria"]["required_runs"], 1)
        self.assertIsInstance(
            metadata["reproduction_criteria"]["independent_executor_required"],
            bool,
        )

    def assert_experiment_artifact_envelope(self, metadata, artifact_type):
        required = {
            "artifact_type",
            "artifact_id",
            "content_hash",
            "status",
            "created_at",
            "owner",
            "product_version",
            "scope_or_module",
            "evidence_references",
        }
        self.assertTrue(required.issubset(metadata))
        self.assertEqual(artifact_type, metadata["artifact_type"])
        self.assertRegex(metadata["artifact_id"], STABLE_ID_PATTERN)
        self.assertTrue(metadata["artifact_id"].startswith("artifact:"))
        self.assertIsInstance(metadata["content_hash"], str)
        self.assertTrue(metadata["content_hash"].startswith("sha256:"))
        self.assertGreater(len(metadata["content_hash"]), len("sha256:"))
        self.assertIn(metadata["status"], RECORD_STATUSES)
        for key in ("created_at", "owner", "product_version", "scope_or_module"):
            self.assertIsInstance(metadata[key], str)
            self.assertTrue(metadata[key].strip())
        self.assert_qualified_references(metadata["evidence_references"], "evidence")

    def assert_experiment_result_metadata(self, metadata):
        self.assertEqual(
            {
                "artifact_type",
                "artifact_id",
                "content_hash",
                "status",
                "created_at",
                "owner",
                "product_version",
                "scope_or_module",
                "evidence_references",
                "method_definitions",
                "evidence_method_entries",
                "protocol_reference",
                "run_results",
                "independent_reproduction_results",
                "first_failure",
            },
            set(metadata),
        )
        self.assert_experiment_evidence_method_metadata(metadata)
        top_level_evidence_ids = set(metadata["evidence_references"])
        run_ids = set()
        for list_key in ("run_results", "independent_reproduction_results"):
            self.assertIsInstance(metadata[list_key], list)
            self.assertTrue(metadata[list_key])
        for result in (
            *metadata["run_results"],
            *metadata["independent_reproduction_results"],
        ):
            self.assertIsInstance(result, dict)
            self.assertEqual(
                {
                    "run_id",
                    "started_at",
                    "ended_at",
                    "executor",
                    "environment_identity",
                    "random_seed",
                    "sample_selection",
                    "result",
                    "actual_observations",
                    "deviations",
                    "evidence_references",
                },
                set(result),
            )
            self.assertIsInstance(result["run_id"], str)
            self.assertTrue(result["run_id"].strip())
            self.assertNotIn(result["run_id"], run_ids)
            run_ids.add(result["run_id"])
            self.assertIn(result["result"], {"not-run", "passed", "failed", "mixed"})
            self.assertIsInstance(result["actual_observations"], list)
            self.assert_qualified_references(result["evidence_references"], "evidence")
            self.assertTrue(
                set(result["evidence_references"]).issubset(
                    top_level_evidence_ids
                )
            )
        self.assertEqual(
            {
                "present",
                "run_id",
                "captured_at",
                "observation_surfaces",
                "correlation_ids",
                "evidence_references",
                "preserved_before_retry",
            },
            set(metadata["first_failure"]),
        )
        self.assertIsInstance(metadata["first_failure"]["present"], bool)
        self.assertIsInstance(
            metadata["first_failure"]["preserved_before_retry"], bool
        )
        for nullable_string_key in ("run_id", "captured_at"):
            self.assertTrue(
                metadata["first_failure"][nullable_string_key] is None
                or isinstance(
                    metadata["first_failure"][nullable_string_key], str
                )
            )
        for list_key in ("observation_surfaces", "correlation_ids"):
            self.assertIsInstance(metadata["first_failure"][list_key], list)
        self.assert_qualified_references(
            metadata["first_failure"]["evidence_references"], "evidence"
        )
        self.assertTrue(
            set(metadata["first_failure"]["evidence_references"]).issubset(
                top_level_evidence_ids
            )
        )
        failure_run_id = metadata["first_failure"]["run_id"]
        if metadata["first_failure"]["present"]:
            self.assertIn(failure_run_id, run_ids)
        else:
            self.assertIsNone(failure_run_id)

    def assert_experiment_effects_metadata(self, metadata):
        self.assertEqual(
            {
                "artifact_type",
                "artifact_id",
                "content_hash",
                "status",
                "created_at",
                "owner",
                "product_version",
                "scope_or_module",
                "evidence_references",
                "method_definitions",
                "evidence_method_entries",
                "protocol_reference",
                "side_effect_records",
                "cleanup",
                "residual_checks",
            },
            set(metadata),
        )
        self.assert_experiment_evidence_method_metadata(metadata)
        top_level_evidence_ids = set(metadata["evidence_references"])
        self.assertIsInstance(metadata["side_effect_records"], list)
        self.assertTrue(metadata["side_effect_records"])
        for effect in metadata["side_effect_records"]:
            self.assertIsInstance(effect, dict)
            self.assertEqual(
                {
                    "effect_id",
                    "kind",
                    "target",
                    "occurred",
                    "reversal_action",
                    "recovery_validation",
                    "owner",
                    "disposition",
                    "disposition_proof_references",
                },
                set(effect),
            )
            self.assertIsInstance(effect["occurred"], bool)
            self.assert_qualified_references(
                effect["disposition_proof_references"], "evidence"
            )
            self.assertTrue(
                set(effect["disposition_proof_references"]).issubset(
                    top_level_evidence_ids
                )
            )
        self.assertEqual(
            {"steps", "result", "disposition_proof_references"},
            set(metadata["cleanup"]),
        )
        self.assertIn(
            metadata["cleanup"]["result"],
            {"not-run", "passed", "failed", "partial"},
        )
        self.assertIsInstance(metadata["cleanup"]["steps"], list)
        self.assertTrue(metadata["cleanup"]["steps"])
        for step in metadata["cleanup"]["steps"]:
            self.assertIsInstance(step, dict)
            self.assertEqual({"step_id", "action", "verification"}, set(step))
        self.assert_qualified_references(
            metadata["cleanup"]["disposition_proof_references"], "evidence"
        )
        self.assertTrue(
            set(metadata["cleanup"]["disposition_proof_references"]).issubset(
                top_level_evidence_ids
            )
        )
        self.assertEqual(
            {"checks", "result", "evidence_references"},
            set(metadata["residual_checks"]),
        )
        self.assertIsInstance(metadata["residual_checks"]["checks"], list)
        self.assertTrue(metadata["residual_checks"]["checks"])
        for check in metadata["residual_checks"]["checks"]:
            self.assertIsInstance(check, dict)
            self.assertEqual(
                {"surface", "sentinel_query", "expected", "actual", "difference"},
                set(check),
            )
        self.assertIn(
            metadata["residual_checks"]["result"],
            {"not-run", "passed", "failed", "partial"},
        )
        self.assert_qualified_references(
            metadata["residual_checks"]["evidence_references"], "evidence"
        )
        self.assertTrue(
            set(metadata["residual_checks"]["evidence_references"]).issubset(
                top_level_evidence_ids
            )
        )

    def assert_experiment_evidence_method_metadata(self, metadata):
        methods = metadata["method_definitions"]
        mappings = metadata["evidence_method_entries"]
        self.assertIsInstance(methods, list)
        self.assertIsInstance(mappings, list)
        evidence_ids = set(metadata["evidence_references"])
        if not evidence_ids:
            self.assertEqual([], methods)
            self.assertEqual([], mappings)
            return
        self.assertTrue(methods)
        self.assertTrue(mappings)
        method_ids = []
        for method in methods:
            self.assertEqual({"method_id", "method_maturity"}, set(method))
            self.assertTrue(method["method_id"].startswith("method:"))
            self.assertIn(method["method_maturity"], ALLOWED_MATURITY_LABELS)
            method_ids.append(method["method_id"])
        self.assertEqual(len(method_ids), len(set(method_ids)))
        mapped_evidence_ids = []
        mapped_method_ids = set()
        for mapping in mappings:
            self.assertEqual({"evidence_id", "method_id"}, set(mapping))
            mapped_evidence_ids.append(mapping["evidence_id"])
            mapped_method_ids.add(mapping["method_id"])
        self.assertEqual(evidence_ids, set(mapped_evidence_ids))
        self.assertEqual(len(evidence_ids), len(mapped_evidence_ids))
        self.assertEqual(set(method_ids), mapped_method_ids)

    def assert_experiment_artifact_packages(self, artifacts):
        self.assertEqual(3, len(artifacts))
        by_type = {artifact.get("artifact_type"): artifact for artifact in artifacts}
        self.assertEqual(
            {"ART-P5-PROTOCOL", "ART-P5-RESULT", "ART-P5-EFFECTS"},
            set(by_type),
        )
        protocol = by_type["ART-P5-PROTOCOL"]
        result = by_type["ART-P5-RESULT"]
        effects = by_type["ART-P5-EFFECTS"]
        for artifact_type, metadata in by_type.items():
            self.assert_experiment_artifact_envelope(metadata, artifact_type)
        self.assertEqual(3, len({item["artifact_id"] for item in artifacts}))
        self.assertEqual(3, len({item["content_hash"] for item in artifacts}))
        self.assertEqual("frozen", protocol["status"])
        self.assertEqual(protocol["record_id"], protocol["artifact_id"])
        self.assert_common_record_metadata(protocol)
        self.assert_experiment_evidence_method_metadata(protocol)
        self.assert_composite_template_metadata(protocol)
        self.assert_experiment_protocol_metadata(protocol)
        self.assert_experiment_result_metadata(result)
        self.assert_experiment_effects_metadata(effects)

        protocol_reference = {
            "protocol_id": protocol["artifact_id"],
            "protocol_content_hash": protocol["content_hash"],
        }
        self.assertEqual(protocol_reference, result["protocol_reference"])
        self.assertEqual(protocol_reference, effects["protocol_reference"])
        for derived_artifact in (result, effects):
            self.assertEqual(
                protocol["product_version"],
                derived_artifact["product_version"],
            )
            self.assertEqual(
                protocol["scope_or_module"],
                derived_artifact["scope_or_module"],
            )
        protocol_only_fields = {
            "authorization_record_id",
            "authorization_gate_record_id",
            "environment_identity",
            "pre_state_fingerprint",
            "fingerprints",
            "sentinel",
            "action_permissions",
            "operational_limits",
            "recovery",
            "target_claim_references",
            "protocol_frozen_at",
            "role_and_test_account",
            "inputs",
            "alternative_explanations",
            "variables",
            "wait_conditions",
            "tool_versions",
            "forbidden_side_effects",
            "reproduction_criteria",
            "protocol_steps",
            "expected_observations",
        }
        for derived_artifact in (result, effects):
            self.assertTrue(protocol_only_fields.isdisjoint(derived_artifact))

    def assert_guided_sections(self, document, headings):
        for heading in headings:
            with self.subTest(heading=heading):
                section = self.section_text(document, f"## {heading}")
                substantive_lines = [
                    line
                    for line in section.splitlines()[1:]
                    if line.strip() and not line.startswith("#")
                ]
                self.assertGreaterEqual(
                    len(substantive_lines), 2, f"thin template section: {heading}"
                )

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
            "拥有完整且已获授权读取的源码时，选择"
            "[白盒访问轨道](../access-tracks/white-box.md)",
            selection,
        )
        self.assertIn(
            "不以构建材料是否存在或获准作为白盒轨道的前置条件",
            selection,
        )
        self.assertIn(
            "构建文件/材料、构建执行和运行观察是相互独立的可选证据与权限面",
            selection,
        )
        self.assertIn("缺失或未获准时分别明确记录", selection)

    def assert_delphi_lab_identity_is_branch_specific(self, document):
        lab = self.section_text(document, "## 遗留运行实验室")
        for contract in (
            "每次实验只记录实际使用的数据或外部依赖身份",
            "数据库分支记录数据库副本稳定 ID",
            "文件分支记录文件/目录稳定 ID 与哈希",
            "远程分支记录脱敏端点/服务稳定 ID",
            "设备分支记录设备稳定 ID",
            "无数据层分支显式记录 `no-data-layer`",
            "不要求每次实验记录数据库身份",
        ):
            self.assertIn(contract, lab)

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
            typed_links = re.findall(
                r"`([^`]+)` → `([a-z-]+)` → `([^`]+)`",
                links,
            )
            self.assertTrue(typed_links, f"missing typed relation in row: {stable_id}")
            self.assertEqual(
                links.count("→"),
                2 * len(typed_links),
                f"unparsed typed link in row: {stable_id}",
            )
            for source_id, relation, target_id in typed_links:
                self.assertRegex(source_id, stable_id_pattern)
                self.assertIn(relation, CORE_RELATION_KINDS)
                self.assertRegex(target_id, stable_id_pattern)

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

    def assert_web_claim_split_contract(self, document):
        section = self.section_text(document, "## 证据边界与主张拆分")
        expected_rows = {
            "可重复可见 Web 行为": (
                "runtime-confirmed",
                "只限已测版本、当前合法会话、角色、套餐、租户、配置与状态",
            ),
            "前端静态实现": (
                "statically-supported",
                "不证明对应代码已部署、已执行或当前角色可达",
            ),
            "隐藏服务端实现或数据模型（前端推断）": (
                "inferred",
                "与可见 UI 行为分立；记录推理、替代解释和后端证据缺口",
            ),
            "隐藏服务端实现或数据模型（证据不足）": (
                "unsupported",
                "与可见 UI 行为分立；没有适用后端证据时保持未知",
            ),
            "隐藏服务端实现或数据模型（授权后端静态证据）": (
                "statically-supported",
                "只限已哈希后端源码或模式身份，不证明部署或执行",
            ),
            "隐藏服务端实现或数据模型（授权部署运行证据）": (
                "runtime-confirmed",
                "只限已绑定部署版本、授权场景和日志/trace/运行结果",
            ),
            "前端隐藏或禁用控件": (
                "observed",
                "不是服务端授权证明",
            ),
            "bundle 代码或功能开关存在": (
                "observed",
                "不证明能力已部署、已启用或当前角色可达",
            ),
        }
        observed_rows = {}
        for line in section.splitlines():
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
        self.assertIn(WEB_AUTHORIZATION_CLAIM_CONTRACT, section)
        self.assertIn(WEB_BUNDLE_REACHABILITY_CONTRACT, section)
        self.assertIn(WEB_BACKEND_CLAIM_SEPARATION_CONTRACT, section)

    def assert_web_vertical_example_contract(self, document):
        trace = self.section_text(document, "## 纵向追踪示例")
        nodes = self.section_text(trace, "### 示例节点")
        node_pattern = re.compile(
            r"\| `([^`]+)` \| `([^`]+)` \| `([^`]+)` \| ([^|]+) \|"
        )
        node_rows = [
            match.groups()
            for line in nodes.splitlines()
            if (match := node_pattern.fullmatch(line))
        ]
        self.assertGreaterEqual(len(node_rows), 8)

        stable_id_pattern = re.compile(
            r"^[a-z][a-z0-9-]*:[a-z][a-z0-9-]*(?:\.[a-z0-9-]+)+$"
        )
        node_ids = set()
        declared_evidence_ids = []
        for node_id, node_kind, status, _boundary in node_rows:
            self.assertRegex(node_id, stable_id_pattern)
            self.assertIn(status, CLAIM_STATUSES)
            node_ids.add(node_id)
            if node_id.startswith("evidence:"):
                self.assertTrue(node_kind.endswith("-evidence"))
                declared_evidence_ids.append(node_id)
        self.assertTrue(declared_evidence_ids)

        browser_routes = {
            node_id
            for node_id, node_kind, _status, _boundary in node_rows
            if node_kind == "browser-route"
        }
        backend_endpoints = {
            node_id
            for node_id, node_kind, _status, _boundary in node_rows
            if node_kind == "backend-endpoint"
        }
        self.assertEqual({"product-surface:sample.browser-route"}, browser_routes)
        self.assertEqual(
            {"integration:sample.current-session-endpoint"}, backend_endpoints
        )
        self.assertTrue(browser_routes.isdisjoint(backend_endpoints))

        context_section = self.section_text(trace, "### 示例版本/上下文")
        context_pattern = re.compile(r"\| `([^`]+)` \| [^|]+ \|")
        context_table_rows = [
            line
            for line in context_section.splitlines()
            if line.startswith("| `context:")
        ]
        declared_context_ids = [
            match.group(1)
            for line in context_section.splitlines()
            if (match := context_pattern.fullmatch(line))
        ]
        self.assertEqual(len(context_table_rows), len(declared_context_ids))
        self.assertTrue(declared_context_ids)
        for context_id in declared_context_ids:
            self.assertRegex(context_id, stable_id_pattern)
            self.assertTrue(context_id.startswith("context:"))

        links = self.section_text(trace, "### 示例类型化链接")
        link_pattern = re.compile(
            r"\| `([^`]+)` \| `([^`]+)` \| `([a-z-]+)` \| `([^`]+)` \| "
            r"`([^`]+)` \| `(required|optional)` \| `([^`]+)` \| `([^`]+)` \|"
        )
        table_rows = [
            line for line in links.splitlines() if line.startswith("| `trace-link:")
        ]
        link_rows = [
            match.groups()
            for line in links.splitlines()
            if (match := link_pattern.fullmatch(line))
        ]
        self.assertEqual(len(table_rows), len(link_rows))
        self.assertGreaterEqual(len(link_rows), 8)
        self.assertIn("optional", {row[5] for row in link_rows})
        for (
            link_id,
            source_id,
            relation,
            target_id,
            status,
            _branch,
            evidence_references,
            contexts,
        ) in link_rows:
            self.assertRegex(link_id, stable_id_pattern)
            self.assertIn(source_id, node_ids)
            self.assertIn(target_id, node_ids)
            self.assertIn(relation, CORE_RELATION_KINDS)
            self.assertIn(status, CLAIM_STATUSES)
            evidence_ids = [
                item.strip() for item in evidence_references.split(",") if item.strip()
            ]
            context_ids = [item.strip() for item in contexts.split(",") if item.strip()]
            self.assertTrue(evidence_ids, f"missing evidence reference: {link_id}")
            self.assertTrue(context_ids, f"missing version/context: {link_id}")
            for evidence_id in evidence_ids:
                self.assertRegex(evidence_id, stable_id_pattern)
                self.assertTrue(evidence_id.startswith("evidence:"))
                self.assertEqual(
                    1,
                    declared_evidence_ids.count(evidence_id),
                    f"evidence reference must resolve exactly once: {evidence_id}",
                )
            for context_id in context_ids:
                self.assertRegex(context_id, stable_id_pattern)
                self.assertTrue(context_id.startswith("context:"))
                self.assertEqual(
                    1,
                    declared_context_ids.count(context_id),
                    f"context reference must resolve exactly once: {context_id}",
                )

        expected_links = {
            (
                "interaction:sample.user-action",
                "calls",
                "asset:sample.client-handler",
                "statically-supported",
                "required",
            ),
            (
                "asset:sample.client-handler",
                "reads",
                "data:sample.client-form-state",
                "statically-supported",
                "required",
            ),
            (
                "evidence:sample.client-validation",
                "validates",
                "claim:sample.client-validation",
                "runtime-confirmed",
                "required",
            ),
            (
                "asset:sample.client-handler",
                "calls",
                "integration:sample.current-session-endpoint",
                "statically-supported",
                "required",
            ),
            (
                "asset:sample.backend-candidate",
                "implements",
                "capability:sample.accept-action",
                "statically-supported",
                "optional",
            ),
            (
                "integration:sample.current-session-endpoint",
                "emits",
                "integration:sample.async-outcome",
                "inferred",
                "optional",
            ),
            (
                "integration:sample.async-outcome",
                "supports",
                "claim:sample.visible-result",
                "inferred",
                "optional",
            ),
            (
                "evidence:sample.visible-result",
                "validates",
                "claim:sample.visible-result",
                "runtime-confirmed",
                "required",
            ),
        }
        observed_links = {
            (source_id, relation, target_id, status, branch)
            for (
                _link_id,
                source_id,
                relation,
                target_id,
                status,
                branch,
                _evidence_references,
                _contexts,
            ) in link_rows
        }
        self.assertTrue(expected_links.issubset(observed_links))
        self.assertIn(
            "用户动作 → 客户端状态与校验 → 当前授权会话网络契约 → "
            "可选后端/异步证据 → 可见结果",
            trace,
        )
        self.assertIn("可选节点缺失时保留缺口", trace)
        self.assertIn(
            "异步结果到可见结果的候选边只有在当前场景确有异步迹象时保留",
            trace,
        )
        self.assertIn(
            "不能取代可见结果自己的独立观察与运行证据",
            trace,
        )

    def assert_java_evidence_planes_remain_distinct(self, document):
        section = self.section_text(document, "## 证据平面与主张上限")
        expected_rows = {
            "源码结构": (
                "statically-supported",
                "不证明配置生效、制品已部署或路径已执行",
            ),
            "配置解析候选": (
                "statically-supported",
                "不证明该值在目标部署生效",
            ),
            "部署装配事实": (
                "observed",
                "只证明已检查部署元数据中的装配事实，不证明请求经过该路径",
            ),
            "已观察运行行为": (
                "runtime-confirmed",
                "只限绑定版本、部署、配置、角色、输入和时间窗的场景",
            ),
        }
        observed_rows = {}
        for line in section.splitlines():
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
            "源码结构、配置解析候选、部署装配事实和已观察运行行为必须分别建证据项与主张",
            section,
        )
        self.assertIn(
            "静态证据不得直接升级为 `runtime-confirmed`",
            section,
        )

    def assert_java_framework_topology_is_conditional(self, document):
        frameworks = self.section_text(document, "## 框架识别与条件分支")
        for contract in (
            "Spring Boot、Spring MVC、Jakarta REST、Quarkus、Micronaut 与 Vert.x 都是条件分支",
            "只为实际发现且证据可定位的框架组件建节点和边",
            "不得把 Spring、Jakarta、JPA 或消息系统写成必经层",
        ):
            self.assertIn(contract, frameworks)

        persistence = self.section_text(document, "## 持久化、SQL 与迁移")
        self.assertIn(
            "JPA/Hibernate、MyBatis、JDBC 与动态 SQL 都按实际发现选择",
            persistence,
        )
        messaging = self.section_text(document, "## 消息、Outbox 与消费者")
        self.assertIn("消息代理、Outbox 和消费者都是可选分支", messaging)
        workflow = self.section_text(document, "## 有序工作流")
        self.assertIn("若实际存在消息或任务分支", workflow)

    def assert_java_vertical_example_contract(self, document):
        trace = self.section_text(document, "## 纵向追踪示例")
        nodes = self.section_text(trace, "### 节点注册表")
        node_pattern = re.compile(
            r"\| `([^`]+)` \| `([^`]+)` \| `([^`]+)` \| ([^|]+) \|"
        )
        node_rows = [
            match.groups()
            for line in nodes.splitlines()
            if (match := node_pattern.fullmatch(line))
        ]
        self.assertGreaterEqual(len(node_rows), 12)

        stable_id_pattern = re.compile(
            r"^[a-z][a-z0-9-]*:[a-z][a-z0-9-]*(?:\.[a-z0-9-]+)+$"
        )
        node_ids = set()
        node_contracts = {}
        for node_id, node_kind, status, boundary in node_rows:
            self.assertRegex(node_id, stable_id_pattern)
            self.assertIn(status, CLAIM_STATUSES)
            node_ids.add(node_id)
            node_contracts[node_id] = (node_kind, status, boundary.strip())
        self.assertEqual(len(node_ids), len(node_rows))
        for required_node_id in (
            "asset:sample.java-service",
            "claim:sample.internal-db-path",
            "claim:sample.sync-visible-result",
            "claim:sample.later-visible-result",
            "data:sample.atomic-business-outbox-commit",
            "asset:sample.outbox-relay",
        ):
            self.assertIn(required_node_id, node_contracts)
        self.assertEqual(
            ("service", "statically-supported"),
            node_contracts["asset:sample.java-service"][:2],
        )
        self.assertEqual(
            ("internal-claim", "statically-supported"),
            node_contracts["claim:sample.internal-db-path"][:2],
        )
        self.assertEqual(
            ("visible-claim", "runtime-confirmed"),
            node_contracts["claim:sample.sync-visible-result"][:2],
        )
        self.assertEqual(
            ("visible-claim", "runtime-confirmed"),
            node_contracts["claim:sample.later-visible-result"][:2],
        )
        self.assertEqual(
            ("atomic-business-outbox-transaction-outcome", "statically-supported"),
            node_contracts["data:sample.atomic-business-outbox-commit"][:2],
        )
        self.assertIn(
            "业务数据库变更与 Outbox 记录在同一事务提交",
            node_contracts["data:sample.atomic-business-outbox-commit"][2],
        )
        self.assertNotIn("claim:sample.visible-result", node_ids)

        evidence = self.section_text(trace, "### 证据注册表")
        evidence_pattern = re.compile(r"\| `([^`]+)` \| [^|]+ \|")
        evidence_table_rows = [
            line for line in evidence.splitlines() if line.startswith("| `evidence:")
        ]
        evidence_ids = [
            match.group(1)
            for line in evidence.splitlines()
            if (match := evidence_pattern.fullmatch(line))
        ]
        self.assertEqual(len(evidence_table_rows), len(evidence_ids))
        self.assertTrue(evidence_ids)
        for evidence_id in evidence_ids:
            self.assertRegex(evidence_id, stable_id_pattern)
            self.assertTrue(evidence_id.startswith("evidence:"))

        contexts = self.section_text(trace, "### 上下文注册表")
        context_pattern = re.compile(r"\| `([^`]+)` \| [^|]+ \|")
        context_table_rows = [
            line for line in contexts.splitlines() if line.startswith("| `context:")
        ]
        context_ids = [
            match.group(1)
            for line in contexts.splitlines()
            if (match := context_pattern.fullmatch(line))
        ]
        self.assertEqual(len(context_table_rows), len(context_ids))
        self.assertTrue(context_ids)
        for context_id in context_ids:
            self.assertRegex(context_id, stable_id_pattern)
            self.assertTrue(context_id.startswith("context:"))

        links = self.section_text(trace, "### 类型化链接")
        link_pattern = re.compile(
            r"\| `([^`]+)` \| `([^`]+)` \| `([a-z-]+)` \| `([^`]+)` \| "
            r"`([^`]+)` \| `(shared|sync-optional|async-optional)` \| "
            r"`([^`]+)` \| `([^`]+)` \|"
        )
        link_table_rows = [
            line for line in links.splitlines() if line.startswith("| `trace-link:")
        ]
        link_rows = [
            match.groups()
            for line in links.splitlines()
            if (match := link_pattern.fullmatch(line))
        ]
        self.assertEqual(len(link_table_rows), len(link_rows))
        self.assertGreaterEqual(len(link_rows), 15)
        self.assertEqual(
            {"shared", "sync-optional", "async-optional"},
            {row[5] for row in link_rows},
        )
        self.assertEqual(len(link_rows), len({row[0] for row in link_rows}))
        for (
            link_id,
            source_id,
            relation,
            target_id,
            status,
            _branch,
            evidence_references,
            context_references,
        ) in link_rows:
            self.assertRegex(link_id, stable_id_pattern)
            self.assertIn(source_id, node_ids)
            self.assertIn(target_id, node_ids)
            self.assertIn(relation, CORE_RELATION_KINDS)
            self.assertIn(status, CLAIM_STATUSES)
            referenced_evidence = [
                item.strip() for item in evidence_references.split(",") if item.strip()
            ]
            referenced_contexts = [
                item.strip() for item in context_references.split(",") if item.strip()
            ]
            self.assertTrue(referenced_evidence)
            self.assertTrue(referenced_contexts)
            for evidence_id in referenced_evidence:
                self.assertRegex(evidence_id, stable_id_pattern)
                self.assertEqual(
                    1,
                    evidence_ids.count(evidence_id),
                    f"evidence reference must resolve exactly once: {evidence_id}",
                )
            for context_id in referenced_contexts:
                self.assertRegex(context_id, stable_id_pattern)
                self.assertEqual(
                    1,
                    context_ids.count(context_id),
                    f"context reference must resolve exactly once: {context_id}",
                )

        expected_links = {
            (
                "integration:sample.http-input",
                "calls",
                "asset:sample.validation",
                "shared",
            ),
            (
                "asset:sample.validation",
                "calls",
                "asset:sample.authorization",
                "shared",
            ),
            (
                "asset:sample.authorization",
                "calls",
                "asset:sample.java-service",
                "shared",
            ),
            (
                "asset:sample.java-service",
                "calls",
                "asset:sample.transaction",
                "shared",
            ),
            (
                "asset:sample.transaction",
                "writes",
                "data:sample.business-commit",
                "sync-optional",
            ),
            (
                "data:sample.business-commit",
                "supports",
                "integration:sample.http-response",
                "sync-optional",
            ),
            (
                "integration:sample.http-response",
                "supports",
                "claim:sample.sync-visible-result",
                "sync-optional",
            ),
            (
                "asset:sample.transaction",
                "writes",
                "data:sample.atomic-business-outbox-commit",
                "async-optional",
            ),
            (
                "asset:sample.outbox-relay",
                "reads",
                "data:sample.atomic-business-outbox-commit",
                "async-optional",
            ),
            (
                "asset:sample.outbox-relay",
                "emits",
                "integration:sample.message",
                "async-optional",
            ),
            (
                "integration:sample.message",
                "calls",
                "asset:sample.consumer-job",
                "async-optional",
            ),
            (
                "asset:sample.consumer-job",
                "supports",
                "claim:sample.later-visible-result",
                "async-optional",
            ),
            (
                "evidence:sample.source-structure",
                "supports",
                "claim:sample.internal-db-path",
                "async-optional",
            ),
            (
                "data:sample.atomic-business-outbox-commit",
                "supports",
                "claim:sample.internal-db-path",
                "async-optional",
            ),
            (
                "evidence:sample.runtime-sync-visible",
                "validates",
                "claim:sample.sync-visible-result",
                "sync-optional",
            ),
            (
                "evidence:sample.runtime-later-visible",
                "validates",
                "claim:sample.later-visible-result",
                "async-optional",
            ),
        }
        observed_links = {
            (source_id, relation, target_id, branch)
            for (
                _link_id,
                source_id,
                relation,
                target_id,
                _status,
                branch,
                _evidence_references,
                _context_references,
            ) in link_rows
        }
        self.assertTrue(expected_links.issubset(observed_links))

        def has_path(source_id, target_id, allowed_branches):
            adjacency = {}
            for (
                _link_id,
                edge_source,
                relation,
                edge_target,
                _status,
                branch,
                _evidence_references,
                _context_references,
            ) in link_rows:
                if branch in allowed_branches:
                    if relation == "reads":
                        adjacency.setdefault(edge_target, set()).add(edge_source)
                    else:
                        adjacency.setdefault(edge_source, set()).add(edge_target)
            pending = [source_id]
            visited = set()
            while pending:
                current = pending.pop()
                if current == target_id:
                    return True
                if current in visited:
                    continue
                visited.add(current)
                pending.extend(adjacency.get(current, ()))
            return False

        self.assertTrue(
            has_path(
                "integration:sample.http-input",
                "claim:sample.sync-visible-result",
                {"shared", "sync-optional"},
            )
        )
        self.assertTrue(
            has_path(
                "integration:sample.http-input",
                "claim:sample.later-visible-result",
                {"shared", "async-optional"},
            )
        )
        self.assertFalse(
            has_path(
                "asset:sample.consumer-job",
                "claim:sample.sync-visible-result",
                {"shared", "sync-optional", "async-optional"},
            )
        )

        undirected = {node_id: set() for node_id in node_ids}
        for row in link_rows:
            undirected[row[1]].add(row[3])
            undirected[row[3]].add(row[1])
        pending = ["integration:sample.http-input"]
        connected = set()
        while pending:
            current = pending.pop()
            if current in connected:
                continue
            connected.add(current)
            pending.extend(undirected[current])
        self.assertEqual(node_ids, connected)

        visible_validation_edges = {
            target_id: (source_id, status, branch)
            for (
                _link_id,
                source_id,
                relation,
                target_id,
                status,
                branch,
                _evidence_references,
                _context_references,
            ) in link_rows
            if relation == "validates" and target_id.startswith("claim:sample.")
        }
        self.assertEqual(
            {
                "claim:sample.sync-visible-result": (
                    "evidence:sample.runtime-sync-visible",
                    "runtime-confirmed",
                    "sync-optional",
                ),
                "claim:sample.later-visible-result": (
                    "evidence:sample.runtime-later-visible",
                    "runtime-confirmed",
                    "async-optional",
                ),
            },
            visible_validation_edges,
        )
        self.assertIn(
            "HTTP 输入 → 校验 → 授权 → 服务 → 事务 → "
            "业务数据库变更与 Outbox 记录的原子提交 → relay/消息 → "
            "消费者/任务 → 稍后可见结果",
            trace,
        )
        for contract in (
            "同步响应/即时可见确认是独立分支",
            "Outbox 分支不是必经路径",
            "消费者不位于即时 HTTP 响应之前",
            "可选分支缺失时保留缺口且不创建占位边",
            "可见结果主张与内部实现主张使用不同稳定 ID",
            "每个可见主张都由自己的运行证据独立验证",
        ):
            self.assertIn(contract, trace)

    def parse_registered_typed_trace(self, document, trace_heading):
        trace = self.section_text(document, trace_heading)
        stable_id_pattern = re.compile(
            r"^[a-z][a-z0-9-]*:[a-z][a-z0-9-]*(?:\.[a-z0-9-]+)+$"
        )

        nodes = self.section_text(trace, "### 节点注册表")
        node_pattern = re.compile(
            r"\| `([^`]+)` \| `([^`]+)` \| `([^`]+)` \| ([^|]+) \|"
        )
        node_rows = [
            match.groups()
            for line in nodes.splitlines()
            if (match := node_pattern.fullmatch(line))
        ]
        node_table_rows = [
            line for line in nodes.splitlines() if line.startswith("| `")
        ]
        self.assertEqual(len(node_table_rows), len(node_rows))
        self.assertTrue(node_rows)
        node_ids = set()
        for node_id, _kind, status, _boundary in node_rows:
            self.assertRegex(node_id, stable_id_pattern)
            self.assertIn(status, CLAIM_STATUSES)
            node_ids.add(node_id)
        self.assertEqual(len(node_ids), len(node_rows))

        def registry_ids(subheading, prefix):
            registry = self.section_text(trace, subheading)
            pattern = re.compile(r"\| `([^`]+)` \| [^|]+ \|")
            table_rows = [
                line
                for line in registry.splitlines()
                if line.startswith(f"| `{prefix}:")
            ]
            identifiers = [
                match.group(1)
                for line in registry.splitlines()
                if (match := pattern.fullmatch(line))
            ]
            self.assertEqual(len(table_rows), len(identifiers))
            self.assertTrue(identifiers)
            for identifier in identifiers:
                self.assertRegex(identifier, stable_id_pattern)
                self.assertTrue(identifier.startswith(f"{prefix}:"))
            self.assertEqual(len(identifiers), len(set(identifiers)))
            return identifiers

        evidence_ids = registry_ids("### 证据注册表", "evidence")
        context_ids = registry_ids("### 上下文注册表", "context")

        links = self.section_text(trace, "### 类型化链接")
        link_pattern = re.compile(
            r"\| `([^`]+)` \| `([^`]+)` \| `([a-z-]+)` \| `([^`]+)` \| "
            r"`([^`]+)` \| `([^`]+)` \| `([^`]+)` \|"
        )
        link_rows = [
            match.groups()
            for line in links.splitlines()
            if (match := link_pattern.fullmatch(line))
        ]
        link_table_rows = [
            line for line in links.splitlines() if line.startswith("| `trace-link:")
        ]
        self.assertEqual(len(link_table_rows), len(link_rows))
        self.assertTrue(link_rows)
        self.assertEqual(len(link_rows), len({row[0] for row in link_rows}))
        valid_sources = node_ids | set(evidence_ids)
        for (
            link_id,
            source_id,
            relation,
            target_id,
            status,
            evidence_references,
            context_references,
        ) in link_rows:
            self.assertRegex(link_id, stable_id_pattern)
            self.assertIn(source_id, valid_sources)
            self.assertIn(target_id, node_ids)
            self.assertIn(relation, CORE_RELATION_KINDS)
            self.assertIn(status, CLAIM_STATUSES)
            referenced_evidence = [
                item.strip() for item in evidence_references.split(",") if item.strip()
            ]
            referenced_contexts = [
                item.strip() for item in context_references.split(",") if item.strip()
            ]
            self.assertTrue(referenced_evidence)
            self.assertTrue(referenced_contexts)
            for evidence_id in referenced_evidence:
                self.assertEqual(1, evidence_ids.count(evidence_id))
            for context_id in referenced_contexts:
                self.assertEqual(1, context_ids.count(context_id))

        return trace, node_ids, link_rows

    def assert_registered_trace_path(self, link_rows, source_id, target_id):
        adjacency = {}
        for (
            _link_id,
            edge_source,
            relation,
            edge_target,
            _status,
            _evidence_references,
            _context_references,
        ) in link_rows:
            if relation == "reads":
                adjacency.setdefault(edge_target, set()).add(edge_source)
            elif not edge_source.startswith("evidence:"):
                adjacency.setdefault(edge_source, set()).add(edge_target)
        pending = [source_id]
        visited = set()
        while pending:
            current = pending.pop()
            if current == target_id:
                return
            if current in visited:
                continue
            visited.add(current)
            pending.extend(adjacency.get(current, ()))
        self.fail(f"no registered typed path: {source_id} -> {target_id}")

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

    def test_all_human_readable_record_templates_exist(self):
        for name, path in TEMPLATE_DOCUMENTS.items():
            with self.subTest(template=name):
                self.assertTrue(path.is_file(), f"missing record template: {path}")

    def test_all_machine_readable_schemas_and_examples_exist(self):
        for name, path in SCHEMA_DOCUMENTS.items():
            with self.subTest(schema=name):
                self.assertTrue(path.is_file(), f"missing JSON Schema: {path}")
        for name, examples in SCHEMA_EXAMPLES.items():
            for validity, path in examples.items():
                with self.subTest(schema=name, fixture=validity):
                    self.assertTrue(path.is_file(), f"missing schema fixture: {path}")

    def test_all_json_schemas_are_valid_draft_2020_12_documents(self):
        self.require_all_schemas_and_examples()
        observed_ids = set()
        for name, path in SCHEMA_DOCUMENTS.items():
            with self.subTest(schema=name):
                schema = self.read_json_file(path)
                self.assertEqual(
                    "https://json-schema.org/draft/2020-12/schema",
                    schema.get("$schema"),
                )
                self.assertEqual(
                    f"{SCHEMA_BASE_URI}{name}.schema.json", schema.get("$id")
                )
                Draft202012Validator.check_schema(schema)
                if name != "definitions":
                    self.assertIs(schema.get("additionalProperties"), False)
                observed_ids.add(schema["$id"])
        self.assertEqual(len(SCHEMA_NAMES), len(observed_ids))

    def test_shared_schema_enums_are_exact_and_closed(self):
        self.require_all_schemas_and_examples()
        definitions = self.read_json_file(SCHEMA_DOCUMENTS["definitions"])[
            "$defs"
        ]
        expected = {
            "methodMaturity": set(ALLOWED_MATURITY_LABELS),
            "claimStatus": CLAIM_STATUSES,
            "riskLevel": {"P0", "P1", "P2"},
            "evidenceKind": {
                "runtime",
                "static",
                "interface",
                "documentary",
                "domain",
                "derived",
            },
            "relationKind": CORE_RELATION_KINDS | {"replaced-by"},
            "projectGoal": {
                "rewrite",
                "migration",
                "replacement",
                "acquisition-due-diligence",
                "competitor-research",
            },
            "gateVerdict": GATE_VERDICTS,
        }
        for definition_name, expected_values in expected.items():
            with self.subTest(definition=definition_name):
                self.assertEqual(
                    expected_values, set(definitions[definition_name]["enum"])
                )

    def test_schema_examples_have_one_valid_and_one_invalid_contract(self):
        self.require_all_schemas_and_examples()
        schemas = {
            name: self.read_json_file(path)
            for name, path in SCHEMA_DOCUMENTS.items()
        }
        for name, examples in SCHEMA_EXAMPLES.items():
            validator = self.schema_validator(name, schemas)
            valid = self.read_json_file(examples["valid"])
            invalid = self.read_json_file(examples["invalid"])
            with self.subTest(schema=name, fixture="valid"):
                self.assertEqual([], list(validator.iter_errors(valid)))
            with self.subTest(schema=name, fixture="invalid"):
                self.assertTrue(list(validator.iter_errors(invalid)))

    def test_schema_references_are_local_and_remote_retrieval_is_denied(self):
        self.require_all_schemas_and_examples()
        schemas = {
            name: self.read_json_file(path)
            for name, path in SCHEMA_DOCUMENTS.items()
        }

        def collect_refs(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    if key == "$ref":
                        yield child
                    else:
                        yield from collect_refs(child)
            elif isinstance(value, list):
                for child in value:
                    yield from collect_refs(child)

        definitions_id = schemas["definitions"]["$id"]
        for name, schema in schemas.items():
            with self.subTest(schema=name):
                for reference in collect_refs(schema):
                    self.assertTrue(
                        reference.startswith("#/")
                        or reference.startswith(f"{definitions_id}#/$defs/"),
                        f"non-local schema reference: {reference}",
                    )

        broken = copy.deepcopy(schemas)
        broken["asset"]["properties"]["record_id"] = {
            "$ref": f"{SCHEMA_BASE_URI}missing.schema.json#/$defs/stableId"
        }
        with self.assertRaisesRegex(Exception, "Unresolvable") as raised:
            list(
                self.schema_validator("asset", broken).iter_errors(
                    self.read_json_file(SCHEMA_EXAMPLES["asset"]["valid"])
                )
            )
        self.assertIsInstance(raised.exception.__cause__, Unresolvable)
        self.assertIsInstance(
            raised.exception.__cause__.__context__, NoSuchResource
        )

    def test_schema_closed_enums_reject_unknown_values(self):
        self.require_all_schemas_and_examples()
        mutations = {
            "evidence": (
                ("kind", "unknown-kind"),
                ("method", "maturity", "unknown-maturity"),
            ),
            "claim": (("claim_status", "unknown-status"),),
            "trace-link": (("relation", "unknown-relation"),),
            "decision": (
                ("project_goal", "unknown-goal"),
                ("risks", 0, "level", "P9"),
            ),
            "coverage-summary": (("gates", "G0", "verdict", "unknown-gate"),),
        }
        for name, paths in mutations.items():
            validator = self.schema_validator(name)
            valid = self.read_json_file(SCHEMA_EXAMPLES[name]["valid"])
            for mutation_path in paths:
                with self.subTest(schema=name, mutation=mutation_path):
                    mutated = copy.deepcopy(valid)
                    *parents, replacement = mutation_path
                    target = mutated
                    for key in parents[:-1]:
                        target = target[key]
                    target[parents[-1]] = replacement
                    self.assertTrue(list(validator.iter_errors(mutated)))

    def test_schemas_reject_unknown_fields_at_record_and_nested_boundaries(self):
        self.require_all_schemas_and_examples()
        asset = self.read_json_file(SCHEMA_EXAMPLES["asset"]["valid"])
        asset["undeclared"] = True
        self.assertTrue(list(self.schema_validator("asset").iter_errors(asset)))

        evidence = self.read_json_file(SCHEMA_EXAMPLES["evidence"]["valid"])
        evidence["capture_identity"]["undeclared"] = True
        self.assertTrue(
            list(self.schema_validator("evidence").iter_errors(evidence))
        )

    def test_claim_schema_rejects_product_level_method_maturity(self):
        self.require_all_schemas_and_examples()
        claim = self.read_json_file(SCHEMA_EXAMPLES["claim"]["valid"])
        claim["method_maturity"] = "project-validated"
        self.assertTrue(list(self.schema_validator("claim").iter_errors(claim)))
        claim["maturity"] = "project-validated"
        self.assertTrue(list(self.schema_validator("claim").iter_errors(claim)))

    def test_stable_id_schema_rejects_blanks_and_display_names(self):
        self.require_all_schemas_and_examples()
        asset = self.read_json_file(SCHEMA_EXAMPLES["asset"]["valid"])
        validator = self.schema_validator("asset")
        for invalid_id in ("", " ", "Orders service", "asset"):
            with self.subTest(stable_id=invalid_id):
                mutated = copy.deepcopy(asset)
                mutated["record_id"] = invalid_id
                self.assertTrue(list(validator.iter_errors(mutated)))

        uppercase_hex = copy.deepcopy(asset)
        uppercase_hex["record_id"] = "asset:DEADBEEF"
        self.assertEqual([], list(validator.iter_errors(uppercase_hex)))

        lowercase_unqualified_hex = copy.deepcopy(asset)
        lowercase_unqualified_hex["record_id"] = "asset:deadbeef"
        self.assertTrue(list(validator.iter_errors(lowercase_unqualified_hex)))

    def test_record_ids_use_schema_specific_type_prefixes(self):
        self.require_all_schemas_and_examples()
        for name in RECORD_SCHEMA_NAMES:
            with self.subTest(schema=name):
                fixture = self.read_json_file(SCHEMA_EXAMPLES[name]["valid"])
                fixture["record_id"] = "other:sample.wrong-type"
                self.assertTrue(
                    list(self.schema_validator(name).iter_errors(fixture))
                )

    def test_schema_validation_enforces_iso_dates_and_timestamps(self):
        self.require_all_schemas_and_examples()
        asset = self.read_json_file(SCHEMA_EXAMPLES["asset"]["valid"])
        asset["last_updated"] = "15 January someday"
        self.assertTrue(list(self.schema_validator("asset").iter_errors(asset)))

        evidence = self.read_json_file(SCHEMA_EXAMPLES["evidence"]["valid"])
        evidence["capture_identity"]["captured_at"] = "yesterday"
        self.assertTrue(
            list(self.schema_validator("evidence").iter_errors(evidence))
        )

    def test_coverage_semantics_reject_overcount_and_invalid_g5_combinations(self):
        self.require_all_schemas_and_examples()
        coverage = self.read_json_file(
            SCHEMA_EXAMPLES["coverage-summary"]["valid"]
        )
        validator = self.schema_validator("coverage-summary")

        overcount = copy.deepcopy(coverage)
        overcount["dimensions"]["product"]["numerator"] = (
            overcount["dimensions"]["product"]["denominator"] + 1
        )
        self.assertTrue(list(validator.iter_errors(overcount)))

        hidden_static_gap = copy.deepcopy(coverage)
        hidden_static_gap["gates"]["G5"]["static_non_runtime_coverage"][
            "gap_count"
        ] = 0
        self.assertTrue(list(validator.iter_errors(hidden_static_gap)))

        runtime_not_confirmed = copy.deepcopy(coverage)
        runtime_not_confirmed["gates"]["G5"].update(
            {
                "verdict": "pass",
                "selected_branch": "runtime",
                "runtime_confirmation_status": "required",
                "static_non_runtime_coverage": {
                    "gap_artifact_reference": None,
                    "gap_count": 0,
                },
                "evidence_references": ["evidence:sample.runtime-gate"],
            }
        )
        self.assertTrue(list(validator.iter_errors(runtime_not_confirmed)))

        not_applicable = copy.deepcopy(coverage)
        not_applicable["gates"]["G5"]["verdict"] = "not-applicable"
        self.assertTrue(list(validator.iter_errors(not_applicable)))

    def test_coverage_buckets_exactly_partition_the_frozen_denominator(self):
        self.require_all_schemas_and_examples()
        coverage = self.read_json_file(
            SCHEMA_EXAMPLES["coverage-summary"]["valid"]
        )
        mutation = copy.deepcopy(coverage)
        mutation["dimensions"]["product"]["numerator"] -= 1
        self.assertTrue(
            list(self.schema_validator("coverage-summary").iter_errors(mutation))
        )

    def test_coverage_g5_static_gap_matches_runtime_unresolved_partition(self):
        self.require_all_schemas_and_examples()
        coverage = self.read_json_file(
            SCHEMA_EXAMPLES["coverage-summary"]["valid"]
        )
        validator = self.schema_validator("coverage-summary")

        contradictory_static_gap = copy.deepcopy(coverage)
        runtime = contradictory_static_gap["dimensions"]["runtime"]
        runtime["numerator"] = 1
        runtime["unknown_count"] = 3
        self.assertTrue(list(validator.iter_errors(contradictory_static_gap)))

        runtime_pass_with_unresolved_items = copy.deepcopy(coverage)
        runtime_pass_with_unresolved_items["gates"]["G5"].update(
            {
                "selected_branch": "runtime",
                "verdict": "pass",
                "runtime_confirmation_status": "confirmed",
                "static_non_runtime_coverage": {
                    "gap_artifact_reference": None,
                    "gap_count": 0,
                },
            }
        )
        self.assertTrue(
            list(validator.iter_errors(runtime_pass_with_unresolved_items))
        )

    def test_coverage_schema_enforces_bucket_and_gate_identity_contracts(self):
        self.require_all_schemas_and_examples()
        coverage = self.read_json_file(
            SCHEMA_EXAMPLES["coverage-summary"]["valid"]
        )
        validator = self.schema_validator("coverage-summary")
        gate_record_ids = []
        for gate_id, gate in coverage["gates"].items():
            with self.subTest(gate=gate_id):
                self.assertTrue(
                    {
                        "gate_id",
                        "reviewer",
                        "decided_at",
                        "evidence_references",
                    }.issubset(gate)
                )
                self.assertEqual(gate_id, gate["gate_id"])
                self.assertTrue(gate["reviewer"].strip())
                if gate["verdict"] == "pending":
                    self.assertIsNone(gate["decided_at"])
                else:
                    self.assertIsInstance(gate["decided_at"], str)
                    self.assertTrue(gate["decided_at"].strip())
                gate_record_ids.append(gate["gate_record_reference"]["id"])
        self.assertEqual(len(gate_record_ids), len(set(gate_record_ids)))

        excessive_buckets = copy.deepcopy(coverage)
        excessive_buckets["dimensions"]["product"].update(
            {
                "denominator": 6,
                "numerator": 5,
                "unknown_count": 2,
                "conflicting_count": 0,
                "excluded_count": 0,
            }
        )
        self.assertTrue(list(validator.iter_errors(excessive_buckets)))

        reused_gate_record = copy.deepcopy(coverage)
        reused_gate_record["gates"]["G2"]["gate_record_reference"] = copy.deepcopy(
            reused_gate_record["gates"]["G1"]["gate_record_reference"]
        )
        self.assertTrue(list(validator.iter_errors(reused_gate_record)))

        mismatched_gate_id = copy.deepcopy(coverage)
        mismatched_gate_id["gates"]["G2"]["gate_id"] = "G1"
        self.assertTrue(list(validator.iter_errors(mismatched_gate_id)))

        pending_with_decision_time = copy.deepcopy(coverage)
        pending_with_decision_time["gates"]["G6"][
            "decided_at"
        ] = "2026-01-15T12:00:00Z"
        self.assertTrue(list(validator.iter_errors(pending_with_decision_time)))

        decided_without_time = copy.deepcopy(coverage)
        decided_without_time["gates"]["G1"]["decided_at"] = None
        self.assertTrue(list(validator.iter_errors(decided_without_time)))

        valid_not_applicable = copy.deepcopy(coverage)
        valid_not_applicable["gates"]["G7"].update(
            {
                "verdict": "not-applicable",
                "decided_at": "2026-01-15T12:00:00Z",
                "not_applicable_approval": {
                    "approval_reference": "decision:sample.g7-not-applicable",
                    "approved_by": "Sample release owner",
                    "reason": "The approved sample scope has no release operation.",
                    "expires_at": "2026-06-30T00:00:00Z",
                    "reopen_condition": "Reopen when a release target enters scope."
                },
            }
        )
        self.assertEqual([], list(validator.iter_errors(valid_not_applicable)))

        missing_not_applicable_approval = copy.deepcopy(valid_not_applicable)
        missing_not_applicable_approval["gates"]["G7"][
            "not_applicable_approval"
        ] = None
        self.assertTrue(
            list(validator.iter_errors(missing_not_applicable_approval))
        )

    def test_experiment_schema_requires_three_bound_immutable_artifacts(self):
        self.require_all_schemas_and_examples()
        experiment = self.read_json_file(
            SCHEMA_EXAMPLES["experiment"]["valid"]
        )
        validator = self.schema_validator("experiment")

        mutable_single_package = copy.deepcopy(experiment)
        del mutable_single_package["effects"]
        self.assertTrue(list(validator.iter_errors(mutable_single_package)))

        wrong_protocol = copy.deepcopy(experiment)
        wrong_protocol["result"]["protocol_reference"]["protocol_id"] = (
            "artifact:sample.other-protocol"
        )
        self.assertTrue(list(validator.iter_errors(wrong_protocol)))

        divergent_context = copy.deepcopy(experiment)
        divergent_context["effects"]["product_version"] = "build:sample.other"
        self.assertTrue(list(validator.iter_errors(divergent_context)))

        undeclared_inner_evidence = copy.deepcopy(experiment)
        undeclared_inner_evidence["result"]["run_results"][0][
            "evidence_references"
        ] = ["evidence:sample.not-in-result-index"]
        self.assertTrue(list(validator.iter_errors(undeclared_inner_evidence)))

    def test_experiment_schema_matches_task10_three_artifact_contract(self):
        self.require_all_schemas_and_examples()
        fixture = self.read_json_file(SCHEMA_EXAMPLES["experiment"]["valid"])
        template_artifacts = self.parse_all_yaml_metadata(
            self.read_template_document("experiment-record")
        )
        template_by_type = {
            artifact["artifact_type"]: artifact for artifact in template_artifacts
        }
        fixture_by_type = {
            fixture[name]["artifact_type"]: fixture[name]
            for name in ("protocol", "result", "effects")
        }
        self.assertEqual(set(template_by_type), set(fixture_by_type))
        shape_mismatches = {}
        for artifact_type, expected in template_by_type.items():
            expected_fields = set(expected)
            actual_fields = set(fixture_by_type[artifact_type])
            if expected_fields != actual_fields:
                shape_mismatches[artifact_type] = {
                    "missing": sorted(expected_fields - actual_fields),
                    "extra": sorted(actual_fields - expected_fields),
                }
        self.assertEqual({}, shape_mismatches)

        protocol = fixture["protocol"]
        self.assertEqual(
            {"source", "artifact", "clone"}, set(protocol["fingerprints"])
        )
        self.assertEqual(
            {"read", "write", "fault-injection", "egress", "cleanup"},
            set(protocol["action_permissions"]),
        )
        self.assertEqual(
            {"cost", "rate", "blast_radius"},
            set(protocol["operational_limits"]),
        )
        self.assertEqual(
            {"recovery_point", "owner", "max_restore_time"},
            set(protocol["recovery"]),
        )
        self.assertTrue(protocol["inputs"])
        self.assertTrue(protocol["alternative_explanations"])
        self.assertTrue(protocol["variables"])
        self.assertTrue(protocol["wait_conditions"])
        self.assertTrue(protocol["tool_versions"])
        self.assertTrue(protocol["forbidden_side_effects"])
        self.assertTrue(protocol["protocol_steps"])
        self.assertTrue(protocol["expected_observations"])
        for observation in protocol["expected_observations"]:
            self.assertEqual(
                {"observation_id", "surface", "expected", "tolerance"},
                set(observation),
            )

        result = fixture["result"]
        self.assertTrue(
            {"method_definitions", "evidence_method_entries"}.issubset(result)
        )
        self.assertTrue(result["run_results"])
        self.assertTrue(result["independent_reproduction_results"])
        expected_run_fields = {
            "run_id",
            "started_at",
            "ended_at",
            "executor",
            "environment_identity",
            "random_seed",
            "sample_selection",
            "result",
            "actual_observations",
            "deviations",
            "evidence_references",
        }
        for run in (
            *result["run_results"],
            *result["independent_reproduction_results"],
        ):
            self.assertEqual(expected_run_fields, set(run))
        self.assertEqual(
            {
                "present",
                "run_id",
                "captured_at",
                "observation_surfaces",
                "correlation_ids",
                "evidence_references",
                "preserved_before_retry",
            },
            set(result["first_failure"]),
        )

        effects = fixture["effects"]
        self.assertTrue(
            {"method_definitions", "evidence_method_entries"}.issubset(effects)
        )
        self.assertTrue(effects["side_effect_records"])
        self.assertEqual(
            {"steps", "result", "disposition_proof_references"},
            set(effects["cleanup"]),
        )
        self.assertEqual(
            {"checks", "result", "evidence_references"},
            set(effects["residual_checks"]),
        )

    def test_experiment_artifacts_require_closed_local_evidence_method_maps(self):
        self.require_all_schemas_and_examples()
        experiment = self.read_json_file(
            SCHEMA_EXAMPLES["experiment"]["valid"]
        )
        validator = self.schema_validator("experiment")
        for artifact_name in ("protocol", "result", "effects"):
            artifact = experiment[artifact_name]
            with self.subTest(artifact=artifact_name):
                self.assertTrue(
                    {
                        "evidence_references",
                        "method_definitions",
                        "evidence_method_entries",
                    }.issubset(artifact)
                )

        unmapped_top_level_evidence = copy.deepcopy(experiment)
        unmapped_top_level_evidence["result"]["evidence_references"].append(
            "evidence:sample.unmapped-result"
        )
        self.assertTrue(
            list(validator.iter_errors(unmapped_top_level_evidence))
        )

        mapping_to_undeclared_evidence = copy.deepcopy(experiment)
        mapping_to_undeclared_evidence["effects"]["evidence_method_entries"][0][
            "evidence_id"
        ] = "evidence:sample.not-declared"
        self.assertTrue(
            list(validator.iter_errors(mapping_to_undeclared_evidence))
        )

        mapping_to_undeclared_method = copy.deepcopy(experiment)
        mapping_to_undeclared_method["result"]["evidence_method_entries"][0][
            "method_id"
        ] = "method:sample.not-declared"
        self.assertTrue(
            list(validator.iter_errors(mapping_to_undeclared_method))
        )

        multiply_mapped_evidence = copy.deepcopy(experiment)
        multiply_mapped_evidence["result"]["method_definitions"].append(
            {
                "method_id": "method:sample.second-result-method",
                "method_maturity": "proposed",
            }
        )
        multiply_mapped_evidence["result"]["evidence_method_entries"].append(
            {
                "evidence_id": "evidence:sample.order-response",
                "method_id": "method:sample.second-result-method",
            }
        )
        self.assertTrue(list(validator.iter_errors(multiply_mapped_evidence)))

        orphan_method = copy.deepcopy(experiment)
        orphan_method["protocol"]["method_definitions"].append(
            {
                "method_id": "method:sample.not-used",
                "method_maturity": "proposed",
            }
        )
        self.assertTrue(list(validator.iter_errors(orphan_method)))

    def test_experiment_conditionally_requires_evidence_for_positive_results(self):
        self.require_all_schemas_and_examples()
        experiment = self.read_json_file(
            SCHEMA_EXAMPLES["experiment"]["valid"]
        )
        validator = self.schema_validator("experiment")

        passed_without_observations = copy.deepcopy(experiment)
        passed_without_observations["result"]["run_results"][0][
            "actual_observations"
        ] = []
        self.assertTrue(list(validator.iter_errors(passed_without_observations)))

        passed_without_evidence = copy.deepcopy(experiment)
        passed_without_evidence["result"]["run_results"][0][
            "evidence_references"
        ] = []
        self.assertTrue(list(validator.iter_errors(passed_without_evidence)))

        occurred_without_disposition_proof = copy.deepcopy(experiment)
        occurred_without_disposition_proof["effects"]["side_effect_records"][0][
            "disposition_proof_references"
        ] = []
        self.assertTrue(
            list(validator.iter_errors(occurred_without_disposition_proof))
        )

        passed_cleanup_without_proof = copy.deepcopy(experiment)
        passed_cleanup_without_proof["effects"]["cleanup"][
            "disposition_proof_references"
        ] = []
        self.assertTrue(list(validator.iter_errors(passed_cleanup_without_proof)))

        passed_residual_check_without_evidence = copy.deepcopy(experiment)
        passed_residual_check_without_evidence["effects"]["residual_checks"][
            "evidence_references"
        ] = []
        self.assertTrue(
            list(validator.iter_errors(passed_residual_check_without_evidence))
        )

    def test_experiment_draft_artifacts_allow_empty_evidence_method_sets(self):
        self.require_all_schemas_and_examples()
        experiment = self.read_json_file(
            SCHEMA_EXAMPLES["experiment"]["valid"]
        )
        validator = self.schema_validator("experiment")

        empty_result_evidence = copy.deepcopy(experiment)
        result = empty_result_evidence["result"]
        result["evidence_references"] = []
        result["method_definitions"] = []
        result["evidence_method_entries"] = []
        for run in (
            *result["run_results"],
            *result["independent_reproduction_results"],
        ):
            run["result"] = "not-run"
            run["actual_observations"] = []
            run["evidence_references"] = []
        self.assertEqual([], list(validator.iter_errors(empty_result_evidence)))

        empty_effects_evidence = copy.deepcopy(experiment)
        effects = empty_effects_evidence["effects"]
        effects["evidence_references"] = []
        effects["method_definitions"] = []
        effects["evidence_method_entries"] = []
        effects["side_effect_records"][0]["occurred"] = False
        effects["side_effect_records"][0]["disposition"] = "not-created"
        effects["side_effect_records"][0][
            "disposition_proof_references"
        ] = []
        effects["cleanup"]["result"] = "not-run"
        effects["cleanup"]["disposition_proof_references"] = []
        effects["residual_checks"]["result"] = "not-run"
        effects["residual_checks"]["evidence_references"] = []
        self.assertEqual([], list(validator.iter_errors(empty_effects_evidence)))

    def test_experiment_schema_enforces_artifact_run_and_claim_contracts(self):
        self.require_all_schemas_and_examples()
        experiment = self.read_json_file(
            SCHEMA_EXAMPLES["experiment"]["valid"]
        )
        validator = self.schema_validator("experiment")

        duplicate_artifact_id = copy.deepcopy(experiment)
        duplicate_artifact_id["effects"]["artifact_id"] = (
            duplicate_artifact_id["result"]["artifact_id"]
        )
        self.assertTrue(list(validator.iter_errors(duplicate_artifact_id)))

        duplicate_artifact_hash = copy.deepcopy(experiment)
        duplicate_artifact_hash["effects"]["content_hash"] = (
            duplicate_artifact_hash["result"]["content_hash"]
        )
        self.assertTrue(list(validator.iter_errors(duplicate_artifact_hash)))

        no_independent_reproduction = copy.deepcopy(experiment)
        no_independent_reproduction["result"][
            "independent_reproduction_results"
        ] = []
        self.assertTrue(list(validator.iter_errors(no_independent_reproduction)))

        reused_executor = copy.deepcopy(experiment)
        reused_executor["result"]["independent_reproduction_results"][0][
            "executor"
        ] = reused_executor["result"]["run_results"][0]["executor"]
        self.assertTrue(list(validator.iter_errors(reused_executor)))

        insufficient_required_runs = copy.deepcopy(experiment)
        insufficient_required_runs["protocol"]["reproduction_criteria"][
            "required_runs"
        ] = 3
        self.assertTrue(list(validator.iter_errors(insufficient_required_runs)))

        unresolved_method_mapping = copy.deepcopy(experiment)
        unresolved_method_mapping["protocol"]["evidence_method_entries"][0][
            "method_id"
        ] = "method:sample.not-declared"
        self.assertTrue(list(validator.iter_errors(unresolved_method_mapping)))

        undeclared_target_claim = copy.deepcopy(experiment)
        undeclared_target_claim["protocol"]["target_claim_references"].append(
            "claim:sample.not-declared"
        )
        self.assertTrue(list(validator.iter_errors(undeclared_target_claim)))

        unknown_failure_run = copy.deepcopy(experiment)
        unknown_failure_run["result"]["first_failure"].update(
            {
                "present": True,
                "run_id": "run:sample.not-declared",
                "captured_at": "2026-01-15T09:11:00Z",
                "observation_surfaces": ["log"],
                "correlation_ids": ["synthetic-correlation-1"],
                "evidence_references": ["evidence:sample.order-response"],
                "preserved_before_retry": True,
            }
        )
        self.assertTrue(list(validator.iter_errors(unknown_failure_run)))

        missing_action_permission = copy.deepcopy(experiment)
        del missing_action_permission["protocol"]["action_permissions"][
            "fault-injection"
        ]
        self.assertTrue(list(validator.iter_errors(missing_action_permission)))

        missing_expected_tolerance = copy.deepcopy(experiment)
        del missing_expected_tolerance["protocol"]["expected_observations"][0][
            "tolerance"
        ]
        self.assertTrue(list(validator.iter_errors(missing_expected_tolerance)))

        missing_reversal_action = copy.deepcopy(experiment)
        del missing_reversal_action["effects"]["side_effect_records"][0][
            "reversal_action"
        ]
        self.assertTrue(list(validator.iter_errors(missing_reversal_action)))

    def test_experiment_records_failed_cleanup_without_deriving_g5_verdict(self):
        self.require_all_schemas_and_examples()
        experiment = self.read_json_file(
            SCHEMA_EXAMPLES["experiment"]["valid"]
        )
        experiment["effects"]["cleanup"]["result"] = "failed"

        self.assertEqual(
            [], list(self.schema_validator("experiment").iter_errors(experiment))
        )
        self.assertNotIn("gates", experiment)
        self.assertNotIn("gate_verdict", experiment)

    def test_experiment_semantics_validate_time_effect_and_failure_state(self):
        self.require_all_schemas_and_examples()
        experiment = self.read_json_file(
            SCHEMA_EXAMPLES["experiment"]["valid"]
        )
        validator = self.schema_validator("experiment")

        reversed_time = copy.deepcopy(experiment)
        reversed_time["result"]["run_results"][0]["ended_at"] = (
            "2026-01-15T09:00:00Z"
        )
        self.assertTrue(list(validator.iter_errors(reversed_time)))

        occurred_but_not_created = copy.deepcopy(experiment)
        occurred_but_not_created["effects"]["side_effect_records"][0][
            "disposition"
        ] = "not-created"
        self.assertTrue(list(validator.iter_errors(occurred_but_not_created)))

        absent_but_deleted = copy.deepcopy(experiment)
        effect = absent_but_deleted["effects"]["side_effect_records"][0]
        effect["occurred"] = False
        effect["disposition"] = "deleted"
        self.assertTrue(list(validator.iter_errors(absent_but_deleted)))

        failed_without_first_failure = copy.deepcopy(experiment)
        failed_without_first_failure["result"]["run_results"][0][
            "result"
        ] = "failed"
        self.assertTrue(list(validator.iter_errors(failed_without_first_failure)))

        first_failure_points_to_passed_run = copy.deepcopy(experiment)
        failed_run = first_failure_points_to_passed_run["result"][
            "run_results"
        ][0]
        failed_run["result"] = "mixed"
        first_failure_points_to_passed_run["result"]["first_failure"].update(
            {
                "present": True,
                "run_id": "run:sample.independent",
                "captured_at": "2026-01-15T09:01:30Z",
                "observation_surfaces": ["synthetic response"],
                "correlation_ids": ["correlation:sample.first-failure"],
                "evidence_references": ["evidence:sample.order-response"],
                "preserved_before_retry": True,
            }
        )
        self.assertTrue(
            list(validator.iter_errors(first_failure_points_to_passed_run))
        )

        failed_without_observation = copy.deepcopy(experiment)
        failed_run = failed_without_observation["result"]["run_results"][0]
        failed_run["result"] = "failed"
        failed_run["actual_observations"] = []
        failed_run["evidence_references"] = []
        failed_without_observation["result"]["first_failure"].update(
            {
                "present": True,
                "run_id": failed_run["run_id"],
                "captured_at": "2026-01-15T09:01:30Z",
                "observation_surfaces": ["synthetic response"],
                "correlation_ids": ["correlation:sample.first-failure"],
                "evidence_references": ["evidence:sample.order-response"],
                "preserved_before_retry": True,
            }
        )
        self.assertTrue(list(validator.iter_errors(failed_without_observation)))

    def test_experiment_first_failure_is_the_earliest_failure_and_precedes_retries(self):
        self.require_all_schemas_and_examples()
        experiment = self.read_json_file(
            SCHEMA_EXAMPLES["experiment"]["valid"]
        )
        validator = self.schema_validator("experiment")
        result = experiment["result"]
        primary = result["run_results"][0]
        retry = result["independent_reproduction_results"][0]
        primary["result"] = "failed"
        retry["result"] = "mixed"
        result["first_failure"].update(
            {
                "present": True,
                "run_id": primary["run_id"],
                "captured_at": "2026-01-15T09:01:30Z",
                "observation_surfaces": ["synthetic response"],
                "correlation_ids": ["correlation:sample.first-failure"],
                "evidence_references": ["evidence:sample.order-response"],
                "preserved_before_retry": True,
            }
        )
        self.assertEqual([], list(validator.iter_errors(experiment)))

        points_to_later_failure = copy.deepcopy(experiment)
        points_to_later_failure["result"]["first_failure"].update(
            {
                "run_id": retry["run_id"],
                "captured_at": "2026-01-15T09:05:30Z",
            }
        )
        self.assertTrue(list(validator.iter_errors(points_to_later_failure)))

        captured_after_retry_started = copy.deepcopy(experiment)
        captured_after_retry_started["result"]["run_results"][0][
            "ended_at"
        ] = "2026-01-15T09:06:00Z"
        captured_after_retry_started["result"]["first_failure"][
            "captured_at"
        ] = "2026-01-15T09:05:30Z"
        self.assertTrue(list(validator.iter_errors(captured_after_retry_started)))

        not_preserved_before_retry = copy.deepcopy(experiment)
        not_preserved_before_retry["result"]["first_failure"][
            "preserved_before_retry"
        ] = False
        self.assertTrue(list(validator.iter_errors(not_preserved_before_retry)))

        for boundary in (primary["started_at"], primary["ended_at"]):
            with self.subTest(captured_at=boundary):
                boundary_capture = copy.deepcopy(experiment)
                boundary_capture["result"]["first_failure"][
                    "captured_at"
                ] = boundary
                self.assertEqual([], list(validator.iter_errors(boundary_capture)))

        tied_failure_start = copy.deepcopy(experiment)
        tied_failure_start["result"]["independent_reproduction_results"][0][
            "started_at"
        ] = primary["started_at"]
        tied_failure_start["result"]["first_failure"]["captured_at"] = primary[
            "started_at"
        ]
        self.assertEqual([], list(validator.iter_errors(tied_failure_start)))

        tied_but_points_to_second = copy.deepcopy(tied_failure_start)
        tied_but_points_to_second["result"]["first_failure"]["run_id"] = retry[
            "run_id"
        ]
        self.assertTrue(list(validator.iter_errors(tied_but_points_to_second)))

        malformed_timestamp = copy.deepcopy(experiment)
        malformed_timestamp["result"]["first_failure"]["captured_at"] = (
            "not-a-timestamp"
        )
        self.assert_validation_errors_without_exception(
            validator, malformed_timestamp
        )

    def test_custom_schema_keywords_never_crash_on_malformed_json_types(self):
        self.require_all_schemas_and_examples()
        experiment = self.read_json_file(
            SCHEMA_EXAMPLES["experiment"]["valid"]
        )
        experiment_validator = self.schema_validator("experiment")
        malformed_experiment_values = []

        object_evidence_reference = copy.deepcopy(experiment)
        object_evidence_reference["result"]["evidence_references"][0] = {
            "unexpected": "object"
        }
        malformed_experiment_values.append(object_evidence_reference)

        object_claim_reference = copy.deepcopy(experiment)
        object_claim_reference["protocol"]["claim_references"][0] = {
            "unexpected": "object"
        }
        malformed_experiment_values.append(object_claim_reference)

        object_artifact_hash = copy.deepcopy(experiment)
        object_artifact_hash["effects"]["content_hash"] = {
            "unexpected": "object"
        }
        malformed_experiment_values.append(object_artifact_hash)

        mixed_timezone_types = copy.deepcopy(experiment)
        mixed_timezone_types["result"]["run_results"][0]["started_at"] = (
            "2026-01-15T09:01:00"
        )
        malformed_experiment_values.append(mixed_timezone_types)

        for mutation in malformed_experiment_values:
            with self.subTest(mutation=mutation):
                self.assert_validation_errors_without_exception(
                    experiment_validator, mutation
                )

        coverage = self.read_json_file(
            SCHEMA_EXAMPLES["coverage-summary"]["valid"]
        )
        object_gate_id = copy.deepcopy(coverage)
        object_gate_id["gates"]["G2"]["gate_record_reference"]["id"] = {
            "unexpected": "object"
        }
        self.assert_validation_errors_without_exception(
            self.schema_validator("coverage-summary"), object_gate_id
        )
        object_gate_label = copy.deepcopy(coverage)
        object_gate_label["gates"]["G2"]["gate_id"] = {
            "unexpected": "object"
        }
        self.assert_validation_errors_without_exception(
            self.schema_validator("coverage-summary"), object_gate_label
        )

        decision = self.read_json_file(SCHEMA_EXAMPLES["decision"]["valid"])
        object_alternative_id = copy.deepcopy(decision)
        object_alternative_id["alternatives"][0]["alternative_id"] = {
            "unexpected": "object"
        }
        self.assert_validation_errors_without_exception(
            self.schema_validator("decision"), object_alternative_id
        )

    def test_claim_evidence_trace_bundle_relations_and_endpoints_are_closed(self):
        self.require_all_schemas_and_examples()
        self.assertTrue(
            BUNDLE_VALIDATOR_PATH.is_file(),
            f"missing bundle validator: {BUNDLE_VALIDATOR_PATH}",
        )
        validate_bundle = runpy.run_path(str(BUNDLE_VALIDATOR_PATH))[
            "validate_claim_evidence_trace_bundle"
        ]
        claim = self.read_json_file(SCHEMA_EXAMPLES["claim"]["valid"])
        evidence = self.read_json_file(SCHEMA_EXAMPLES["evidence"]["valid"])
        trace = self.read_json_file(SCHEMA_EXAMPLES["trace-link"]["valid"])
        known_ids = {"endpoint:sample.create-order"}

        self.assertEqual(
            [], validate_bundle([claim], [evidence], [trace], known_ids)
        )

        dangling = copy.deepcopy(claim)
        dangling["evidence_relations"][0]["evidence_id"] = (
            "evidence:sample.missing"
        )
        self.assertTrue(validate_bundle([dangling], [evidence], [trace], known_ids))

        one_sided = copy.deepcopy(evidence)
        one_sided["claim_relations"] = []
        self.assertTrue(validate_bundle([claim], [one_sided], [trace], known_ids))

        relation_conflict = copy.deepcopy(evidence)
        relation_conflict["claim_relations"][0]["relation"] = "contradicts"
        self.assertTrue(
            validate_bundle([claim], [relation_conflict], [trace], known_ids)
        )

        dangling_endpoint = copy.deepcopy(trace)
        dangling_endpoint["source_id"] = "endpoint:sample.missing"
        self.assertTrue(
            validate_bundle([claim], [evidence], [dangling_endpoint], known_ids)
        )

        dangling_trace_evidence = copy.deepcopy(trace)
        dangling_trace_evidence["evidence_references"] = [
            "evidence:sample.missing"
        ]
        self.assertTrue(
            validate_bundle(
                [claim], [evidence], [dangling_trace_evidence], known_ids
            )
        )

        malformed_relation = copy.deepcopy(claim)
        malformed_relation["evidence_relations"][0]["evidence_id"] = {
            "unexpected": "object"
        }
        self.assertTrue(
            validate_bundle([malformed_relation], [evidence], [trace], known_ids)
        )

        malformed_endpoint = copy.deepcopy(trace)
        malformed_endpoint["target_id"] = {"unexpected": "object"}
        self.assertTrue(
            validate_bundle([claim], [evidence], [malformed_endpoint], known_ids)
        )

    def test_decision_chosen_outcome_must_resolve_to_a_declared_alternative(self):
        self.require_all_schemas_and_examples()
        decision = self.read_json_file(SCHEMA_EXAMPLES["decision"]["valid"])
        decision["chosen_outcome"] = "alternative:sample.not-declared"
        self.assertTrue(list(self.schema_validator("decision").iter_errors(decision)))

    def test_decision_schema_rejects_duplicate_or_mistyped_decision_links(self):
        self.require_all_schemas_and_examples()
        decision = self.read_json_file(SCHEMA_EXAMPLES["decision"]["valid"])
        validator = self.schema_validator("decision")

        duplicate_alternative = copy.deepcopy(decision)
        duplicate = copy.deepcopy(duplicate_alternative["alternatives"][0])
        duplicate["description"] = "A second description with the same ID."
        duplicate_alternative["alternatives"].append(duplicate)
        self.assertTrue(list(validator.iter_errors(duplicate_alternative)))

        mistyped_supersession = copy.deepcopy(decision)
        mistyped_supersession["supersedes_decision_id"] = (
            "asset:sample.previous-decision"
        )
        self.assertTrue(list(validator.iter_errors(mistyped_supersession)))

        self_supersession = copy.deepcopy(decision)
        self_supersession["supersedes_decision_id"] = self_supersession[
            "record_id"
        ]
        self.assertTrue(list(validator.iter_errors(self_supersession)))

    def test_schema_examples_are_synthetic_and_contain_no_secret_shaped_fields(self):
        self.require_all_schemas_and_examples()
        self.assertTrue(
            FIXTURE_SAFETY_PATH.is_file(),
            f"missing fixture safety validator: {FIXTURE_SAFETY_PATH}",
        )
        fixture_safety_errors = runpy.run_path(str(FIXTURE_SAFETY_PATH))[
            "fixture_safety_errors"
        ]
        prohibited_keys = re.compile(
            r"(?i)^(?:password|passwd|secret|access[_-]?token|api[_-]?key)$"
        )
        for name, examples in SCHEMA_EXAMPLES.items():
            for validity, path in examples.items():
                fixture = self.read_json_file(path)
                serialized = json.dumps(fixture, ensure_ascii=False)
                with self.subTest(schema=name, fixture=validity):
                    self.assertNotIn("/Users/", serialized)
                    self.assertNotIn("/home/", serialized)
                    self.assertNotRegex(serialized, r"[A-Za-z]:\\\\Users\\\\")

                    def assert_no_secret_fields(value):
                        if isinstance(value, dict):
                            for key, child in value.items():
                                self.assertNotRegex(key, prohibited_keys)
                                assert_no_secret_fields(child)
                        elif isinstance(value, list):
                            for child in value:
                                assert_no_secret_fields(child)

                    assert_no_secret_fields(fixture)
                    self.assertEqual([], fixture_safety_errors(fixture))

    def test_fixture_safety_checks_values_without_rejecting_reserved_examples(self):
        self.assertTrue(
            FIXTURE_SAFETY_PATH.is_file(),
            f"missing fixture safety validator: {FIXTURE_SAFETY_PATH}",
        )
        fixture_safety_errors = runpy.run_path(str(FIXTURE_SAFETY_PATH))[
            "fixture_safety_errors"
        ]
        safe_values = {
            "record_id": "evidence:sample.normal-id",
            "content_hash": "sha256:abcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcd",
            "url": "https://api.example.invalid/synthetic",
            "ipv4": "192.0.2.25",
            "ipv6": "2001:db8::25",
            "embedded_reserved_networks": (
                "Reserved endpoints example.invalid, example.com, 192.0.2.25, and "
                "2001:db8::25 are synthetic."
            ),
            "note": "A normal synthetic observation without credentials.",
            "auth_description": "Basic authentication is disabled in this fixture.",
            "code_symbol": "com.example.order.OrderHandler.execute",
            "java_type": "java.lang.String",
            "type_name": "System.Collections.Generic.List",
            "delphi_unit": "System.SysUtils",
            "assembly_version": "1.2.3",
            "config_filename": "config.json",
            "response_filename": "order-response.json",
            "authorization": {
                "verdict": "approved",
                "reference": "artifact:sample.authorization",
            },
            "authorization_status": "approved",
            "customer_status": "active",
            "customer": {"status": "active", "role": "buyer"},
        }
        self.assertEqual([], fixture_safety_errors(safe_values))

        unsafe_values = {
            "credential text": {"note": "password=hunter2"},
            "token value": {"note": "sk-proj-abcdefghijklmnopqrstuv"},
            "public hostname": {"url": "https://customer.com/api"},
            "plain hostname": {"host": "api.customer.com"},
            "non-reserved IP": {"address": "203.0.114.8"},
            "absolute user path": {"path": "/Users/alice/customer.json"},
            "customer record": {"note": "customer_name=RealCo Holdings"},
            "secret-shaped key": {"api_key": "synthetic-placeholder"},
            "URL userinfo": {
                "url": "https://fixture-user:long-password@example.invalid/private"
            },
            "embedded user path": {
                "note": "artifact=/Users/alice/private/capture.json"
            },
            "embedded root home path": {
                "note": "artifact=/root/private/capture.json"
            },
        }
        for label, value in unsafe_values.items():
            with self.subTest(label=label):
                self.assertTrue(fixture_safety_errors(value))

        for assignment in (
            "token=abcdefghijklmnop",
            "password=abcdefghijklmnop",
            "secret=abcdefghijklmnop",
            "api-key=abcdefghijklmnop",
        ):
            with self.subTest(assignment=assignment):
                self.assertTrue(fixture_safety_errors({"note": assignment}))

        contributing = self.read_repo_file("CONTRIBUTING.md")
        for documented_reservation in (
            "example.invalid",
            "192.0.2.0/24",
            "198.51.100.0/24",
            "203.0.113.0/24",
            "2001:db8::/32",
        ):
            self.assertIn(documented_reservation, contributing)

    def test_fixture_safety_combines_key_paths_with_values_and_has_narrow_exemptions(self):
        self.assertTrue(
            FIXTURE_SAFETY_PATH.is_file(),
            f"missing fixture safety validator: {FIXTURE_SAFETY_PATH}",
        )
        fixture_safety_errors = runpy.run_path(str(FIXTURE_SAFETY_PATH))[
            "fixture_safety_errors"
        ]

        review_mutations = {
            "real username field": {"username": "alice"},
            "real customer name field": {"customer_name": "Acme Corporation"},
            "basic authorization": {
                "note": "Authorization: Basic dXNlcjpwYXNzd29yZA=="
            },
            "bearer authorization": {
                "note": "Authorization: Bearer abcdefghijklmnop"
            },
            "colon-prefixed public host": {
                "note": "host:api.customer.com"
            },
            "customer record filename": {"artifact_name": "customer.md"},
        }
        for label, mutation in review_mutations.items():
            with self.subTest(label=label):
                self.assertTrue(fixture_safety_errors(mutation))

        for identity_key in ("username", "user_name", "login_user"):
            with self.subTest(identity_key=identity_key):
                self.assertTrue(fixture_safety_errors({identity_key: "alice"}))
        for business_subject in ("customer", "client", "company", "tenant"):
            with self.subTest(business_subject=business_subject):
                self.assertTrue(
                    fixture_safety_errors(
                        {business_subject: {"name": "Acme Corporation"}}
                    )
                )
        for generic_metadata in ("owner", "project_name"):
            with self.subTest(generic_metadata=generic_metadata):
                self.assertTrue(
                    fixture_safety_errors({generic_metadata: "Acme Migration"})
                )

        exemption_escape_mutations = {
            "safe filename plus credential": {
                "note": "template.md password=abcdefghijklmnop"
            },
            "stable ID plus public host": {
                "record_id": (
                    "evidence:sample.normal-id host:api.customer.com"
                )
            },
            "synthetic key plus user path": {
                "note": "sample.logical-key at /Users/alice/private/result.json"
            },
        }
        for label, mutation in exemption_escape_mutations.items():
            with self.subTest(label=label):
                self.assertTrue(fixture_safety_errors(mutation))

        explicitly_fictional_values = {
            "username": "synthetic-user",
            "customer_name": "Synthetic Customer",
            "owner": "Sample owner",
            "project_name": "Synthetic migration project",
            "url": "https://api.example.invalid/v1/template",
            "host_note": "host:api.example.invalid",
            "documentation_ipv4": "192.0.2.25",
            "documentation_ipv6": "2001:db8::25",
            "artifact_name": "template.md",
            "record_id": "evidence:sample.normal-id",
            "io_record_id": "evidence:sample.service.io",
            "content_hash": (
                "sha256:abcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcd"
            ),
        }
        self.assertEqual([], fixture_safety_errors(explicitly_fictional_values))

        contributing = self.read_repo_file("CONTRIBUTING.md")
        self.assertIn(
            "业务主体的 identity/name/id/address/contact 字段", contributing
        )

    def test_fixture_safety_preserves_symbols_and_checks_explicit_network_contexts(self):
        fixture_safety_errors = runpy.run_path(str(FIXTURE_SAFETY_PATH))[
            "fixture_safety_errors"
        ]
        allowed_non_network_values = {
            "code_symbol": "org.example.product.OrderService.handle",
            "type_name": "Example.Product.CustomerStatus",
            "endpoint_reference": "endpoint:sample.create-order",
            "endpoint": "endpoint:sample.create-order",
            "java_type": "java.lang.String",
            "dotnet_type": "System.Collections.Generic.List",
            "delphi_unit": "System.SysUtils",
            "artifact_name": "config.json",
            "response_name": "order-response.json",
        }
        self.assertEqual([], fixture_safety_errors(allowed_non_network_values))

        network_bypass_mutations = {
            "host field": {"host": "api.customer.com"},
            "endpoint field": {"api_endpoint": "api.customer.com"},
            "URL authority in prose": {
                "note": "callback=https://api.customer.com/v1"
            },
            "explicit host label": {"note": "host:api.customer.com"},
            "explicit domain label": {
                "note": "domain=api.customer.com"
            },
            "server IP": {"server": "203.0.114.8"},
            "explicit server IPv6 label": {
                "note": "server:2001:4860:4860::8888"
            },
        }
        for label, mutation in network_bypass_mutations.items():
            with self.subTest(label=label):
                self.assertTrue(fixture_safety_errors(mutation))

        contributing = self.read_repo_file("CONTRIBUTING.md")
        self.assertIn("扫描所有字符串中的 IPv4/IPv6", contributing)
        self.assertIn("不依赖固定 TLD 清单", contributing)

    def test_fixture_safety_scans_high_confidence_network_tokens_in_all_strings(self):
        fixture_safety_errors = runpy.run_path(str(FIXTURE_SAFETY_PATH))[
            "fixture_safety_errors"
        ]
        review_network_mutations = {
            "embedded IPv4": {"note": "peer=203.0.114.8"},
            "embedded IPv6": {"note": "peer=2001:4860:4860::8888"},
            "embedded com hostname": {"note": "callback=api.customer.com"},
            "embedded io hostname": {"note": "origin=telemetry.customer.io"},
        }
        for label, mutation in review_network_mutations.items():
            with self.subTest(label=label):
                self.assertTrue(fixture_safety_errors(mutation))
        for hostname in (
            "api.customer.net",
            "api.customer.org",
            "api.customer.cn",
        ):
            with self.subTest(hostname=hostname):
                self.assertTrue(
                    fixture_safety_errors({"note": f"observed={hostname}"})
                )

        technical_and_documentation_values = {
            "java_type": "java.lang.String",
            "dotnet_type": "System.Collections.Generic.List",
            "delphi_unit": "System.SysUtils",
            "config_filename": "config.json",
            "response_filename": "order-response.json",
            "documentation_domain": "example.com",
            "documentation_url": "https://example.com/sample",
            "documentation_ipv4": "192.0.2.25",
            "documentation_ipv6": "2001:db8::25",
        }
        self.assertEqual(
            [], fixture_safety_errors(technical_and_documentation_values)
        )

    def test_fixture_safety_rejects_any_dns_shaped_public_suffix(self):
        fixture_safety_errors = runpy.run_path(str(FIXTURE_SAFETY_PATH))[
            "fixture_safety_errors"
        ]
        for hostname in (
            "api.customer.shop",
            "api.customer.online",
            "api.customer.site",
            "api.customer.hk",
            "api.customer.sg",
            "api.customer.futuretld",
        ):
            with self.subTest(hostname=hostname):
                self.assertTrue(
                    fixture_safety_errors({"note": f"observed={hostname}"})
                )

        contributing = self.read_repo_file("CONTRIBUTING.md")
        self.assertIn("不依赖固定 TLD 清单", contributing)

    def test_fixture_safety_uses_field_semantics_for_symbols_and_versions(self):
        fixture_safety_errors = runpy.run_path(str(FIXTURE_SAFETY_PATH))[
            "fixture_safety_errors"
        ]
        technical_values = {
            "type": "Acme.Platform.Widget",
            "class_name": "Acme.Platform.Widget",
            "symbol": "alpha.beta.Handler",
            "package": "org.acme.orders",
            "namespace": "Acme.Product",
            "assembly": "Acme.Product.Core",
            "module": "System.SysUtils",
            "java_io_note": "java.io",
            "java_net_note": "java.net",
            "dotnet_io_note": "System.IO",
            "dotnet_net_note": "System.Net",
            "reverse_package_note": "com.sample.app",
            "javax_note": "javax.crypto.Cipher",
            "jakarta_note": "jakarta.persistence.Entity",
            "kotlin_note": "kotlin.collections.List",
            "scala_note": "scala.collection.Seq",
            "version": "1.2.3.4",
            "assembly_version": "10.20.30.40",
            "file_version": "1.2.3.4",
            "product_version": "10.20.30.40",
            "not_an_ip": "999.20.30.40",
        }
        self.assertEqual([], fixture_safety_errors(technical_values))

        for label, mutation in {
            "IPv4 in note": {"note": "peer=1.2.3.4"},
            "private IPv4 in note": {"note": "peer=10.20.30.40"},
            "IPv4 in host": {"host": "1.2.3.4"},
            "URL hidden in type": {
                "type": "https://api.customer.shop/Widget"
            },
            "host label hidden in namespace": {
                "namespace": "host:api.customer.online"
            },
            "credential hidden in symbol": {
                "symbol": "token=abcdefghijklmnop"
            },
            "path hidden in module": {
                "module": "/Users/alice/private/System.SysUtils"
            },
        }.items():
            with self.subTest(label=label):
                self.assertTrue(fixture_safety_errors(mutation))

        contributing = self.read_repo_file("CONTRIBUTING.md")
        self.assertIn("版本字段", contributing)
        self.assertIn("字段语义", contributing)

    def test_fixture_safety_limits_business_checks_to_identity_fields(self):
        fixture_safety_errors = runpy.run_path(str(FIXTURE_SAFETY_PATH))[
            "fixture_safety_errors"
        ]
        non_identity_metadata = {
            "customer_status": "active",
            "client_role": "buyer",
            "company": {"status": "inactive", "role": "supplier"},
            "tenant": {"status": "provisioned", "role": "sandbox"},
            "business_rule": "orders require approval",
            "authorization": {
                "verdict": "approved",
                "reference": "artifact:sample.authorization",
            },
            "authorization_status": "approved",
        }
        self.assertEqual([], fixture_safety_errors(non_identity_metadata))
        for safe_status in ("approved", "denied", "pending", "not-applicable"):
            with self.subTest(safe_status=safe_status):
                self.assertEqual(
                    [], fixture_safety_errors({"authorization": safe_status})
                )

        identity_and_credential_mutations = {
            "customer filename": {"artifact_name": "customer.md"},
            "nested customer name": {"customer": {"name": "Acme Corp"}},
            "nested client contact": {"client": {"contact": "Jane Doe"}},
            "company address": {"company_address": "1 Private Road"},
            "tenant ID": {"tenant_id": "tenant-prod-42"},
            "authorization Basic scalar": {
                "authorization": "Basic dXNlcjpwYXNzd29yZA=="
            },
            "authorization token scalar": {
                "authorization": "token=abcdefghijklmnop"
            },
            "authorization Negotiate scalar": {
                "authorization": "Negotiate TlRMTVNTUAABAAAAB4IIogAAAAAAAAAAAAAAAAAAAAAGAbEdAAAADw=="
            },
            "authorization Digest scalar": {
                "authorization": (
                    'Digest username="synthetic-user", nonce="abcdef0123456789", '
                    'response="0123456789abcdef", signature="abcdef0123456789"'
                )
            },
            "authorization arbitrary scheme": {
                "authorization": "CustomAuth abcdefghijklmnop"
            },
            "arbitrary authorization header": {
                "note": "Authorization: CustomAuth abcdefghijklmnop"
            },
            "authorization unsafe scalar status": {
                "authorization": "reviewed"
            },
            "Negotiate authorization header": {
                "note": "Authorization: Negotiate TlRMTVNTUAABAAAAB4IIogAAAAAA"
            },
            "Digest authorization header": {
                "note": (
                    'Authorization: Digest username="synthetic-user", '
                    'nonce="abcdef0123456789", response="0123456789abcdef"'
                )
            },
            "authorization object username": {
                "authorization": {"username": "synthetic-user"}
            },
            "authorization object nonce": {
                "authorization": {"nonce": "abcdef0123456789"}
            },
            "authorization object response": {
                "authorization": {"response": "0123456789abcdef"}
            },
            "authorization object signature": {
                "authorization": {"signature": "abcdef0123456789"}
            },
            "authorization object unsafe URL": {
                "authorization": {"reference_url": "https://api.customer.com"}
            },
        }
        for label, mutation in identity_and_credential_mutations.items():
            with self.subTest(label=label):
                self.assertTrue(fixture_safety_errors(mutation))

    def test_development_dependencies_include_the_yaml_parser(self):
        requirements = self.read_repo_file("requirements-dev.txt").splitlines()
        self.assertIn("PyYAML>=6,<7", requirements)

    def test_record_templates_have_parseable_typed_metadata_and_closed_method_links(self):
        self.require_all_templates()
        for name in TEMPLATE_DOCUMENTS:
            if name == "project-charter":
                continue
            with self.subTest(template=name):
                document = self.read_template_document(name)
                metadata = self.parse_yaml_metadata(document)
                self.assert_common_record_metadata(metadata)
                self.assertNotIn("产品主张必须另用 `status`", document)
                self.assertIn("`claim_status`", document)
                self.assertNotRegex(document, r"(?i)\b(?:TODO|TBD|FIXME)\b|待补(?:充|全)")
                self.assertNotIn("/Users/", document)

    def test_composite_templates_reference_claim_authority_without_copying_truth(self):
        self.require_all_templates()
        composite_templates = set(TEMPLATE_DOCUMENTS) - {
            "project-charter",
            "claim-evidence-record",
        }
        for name in sorted(composite_templates):
            with self.subTest(template=name):
                metadata = self.parse_yaml_metadata(
                    self.read_template_document(name)
                )
                self.assert_composite_template_metadata(metadata)

    def test_template_contract_rejects_invalid_yaml_and_duplicate_claim_truth(self):
        invalid_yaml = self.read_template_document("asset-record").replace(
            'record_id: "REPLACE_WITH_QUALIFIED_ASSET_ID"',
            'record_id: ["unterminated"',
            1,
        )
        with self.assertRaises(AssertionError):
            self.parse_yaml_metadata(invalid_yaml)

        duplicated_truth = self.parse_yaml_metadata(
            self.read_template_document("asset-record")
        )
        duplicated_truth["atomic_claims"] = [
            {
                "claim_id": "claim:mutation.duplicate-truth",
                "statement": "duplicated claim truth",
                "status": "observed",
                "confidence": "high",
                "evidence_references": [],
            }
        ]
        with self.assertRaises(AssertionError):
            self.assert_composite_template_metadata(duplicated_truth)

        broken_method_link = self.parse_yaml_metadata(
            self.read_template_document("asset-record")
        )
        broken_method_link["evidence_method_entries"][0][
            "method_id"
        ] = "method:mutation.not-declared"
        with self.assertRaises(AssertionError):
            self.assert_common_record_metadata(broken_method_link)

    def test_project_charter_fixes_authorization_and_delivery_boundaries(self):
        self.require_all_templates()
        document = self.read_template_document("project-charter")
        metadata = self.parse_yaml_metadata(document)
        self.assertTrue(
            {
                "charter_id",
                "authorization",
                "allowed_environments",
                "data_policy",
                "prohibited_actions",
                "outputs",
                "exclusions",
                "risks",
                "approval_owners",
            }.issubset(metadata)
        )
        self.assertIsInstance(metadata["authorization"], dict)
        for list_key in (
            "allowed_environments",
            "prohibited_actions",
            "outputs",
            "exclusions",
            "risks",
            "approval_owners",
        ):
            self.assertIsInstance(metadata[list_key], list)
        self.assert_guided_sections(
            document,
            (
                "决策目的与完成定义",
                "授权与允许环境",
                "数据政策与禁止动作",
                "范围、输出与排除",
                "风险、审批与停止条件",
            ),
        )
        for contract in (
            "ART-P0-AUTH",
            "ART-G0-AUTH",
            "当前 `pass`",
            "授权变化时新建 charter 版本",
            "不得原地扩大授权",
        ):
            self.assertIn(contract, document)

    def test_asset_capability_interaction_rule_and_data_templates_cover_product_modeling(self):
        self.require_all_templates()
        expected_sections = {
            "asset-record": (
                "身份、类型与来源",
                "版本、分类与可达性",
                "依赖、所有权与退役",
                "证据边界与验证",
            ),
            "capability-record": (
                "参与者与业务结果",
                "包含、排除与成功标准",
                "场景、规则与依赖",
                "产品表面与实现追踪",
            ),
            "interaction-record": (
                "入口、角色与前置状态",
                "可见与启用规则",
                "输入、校验与确认",
                "成功、失败与反馈",
                "焦点、键盘与批量行为",
                "后置状态与下游副作用",
            ),
            "rule-record": (
                "规则陈述与适用边界",
                "前置条件与表达式",
                "决策表与优先级",
                "状态影响与副作用",
                "正例、反例与边界例",
                "冲突、例外与未知",
            ),
            "data-object-record": (
                "业务身份与技术别名",
                "字段语义",
                "生命周期与历史",
                "读者、写者与派生者",
                "所有权、保留与删除",
            ),
        }
        for name, headings in expected_sections.items():
            with self.subTest(template=name):
                document = self.read_template_document(name)
                self.assert_guided_sections(document, headings)

        data_document = self.read_template_document("data-object-record")
        for field in (
            "type",
            "precision",
            "unit",
            "null",
            "default",
            "special values",
            "readers",
            "writers",
            "ownership",
        ):
            self.assertIn(field, data_document)

    def test_integration_experiment_claim_decision_freeze_trace_and_competitor_templates_are_complete(self):
        self.require_all_templates()
        expected_sections = {
            "api-integration-record": (
                "消费者、提供者与契约",
                "认证与授权事实",
                "幂等、分页与错误",
                "重试、超时与一致性",
                "Webhook 与事件语义",
            ),
            "experiment-record": (
                "不可变环境与授权",
                "前置状态指纹与唯一哨兵",
                "实验步骤与观测点",
                "预期与实际观察",
                "首个失败保全",
                "逆序清理与残留检查",
            ),
            "claim-evidence-record": (
                "原子产品主张",
                "主张状态与置信度",
                "支持与反驳证据",
                "证据项与方法成熟度",
                "状态历史、冲突与取代",
            ),
            "decision-record": (
                "待决问题与权限",
                "备选方案",
                "选择、理由与影响",
                "证据与不确定性",
                "取代与重新打开",
            ),
            "coverage-and-freeze": (
                "冻结分母与计算规则",
                "九类覆盖与风险队列",
                "G0–G7 门禁",
                "产物生命周期",
                "无环冻结与复核",
            ),
            "as-is-to-be-trace": (
                "As-Is 观察",
                "To-Be 需求",
                "保留、纠正、舍弃或研究决定",
                "迁移与兼容影响",
                "验收与双向追踪",
            ),
            "competitor-insight": (
                "可比边界",
                "观察",
                "推断",
                "替代解释",
                "置信度",
                "战略假设",
                "证伪方法",
            ),
        }
        for name, headings in expected_sections.items():
            with self.subTest(template=name):
                self.assert_guided_sections(
                    self.read_template_document(name), headings
                )

        experiment = self.read_template_document("experiment-record")
        experiment_artifacts = self.parse_all_yaml_metadata(experiment)
        self.assert_experiment_artifact_packages(experiment_artifacts)
        for artifact_heading in (
            "## ART-P5-PROTOCOL 协议包",
            "## ART-P5-RESULT 结果包",
            "## ART-P5-EFFECTS 副作用与处置包",
        ):
            self.assertIn(artifact_heading, experiment)
        for boundary_statement in (
            "三个 YAML 块是三个独立产物",
            "RESULT 与 EFFECTS 只能引用",
            "协议一旦冻结",
            "计算 content hash 时排除 `content_hash` 包络字段",
            "`product_version` 与 `scope_or_module` 必须逐字等于 PROTOCOL",
            "内层证据引用必须解析到所属产物顶层的 `evidence_references`",
            "`first_failure.run_id` 必须解析到本 RESULT",
            "`ended_at` 不得早于 `started_at`",
            "failed/mixed run",
            "按 `started_at` 排序并用记录序列打破同刻并列",
            "早于任何后续 retry 的 `started_at`",
            "occurred: false + disposition: not-created",
        ):
            self.assertIn(boundary_statement, experiment)
        self.assertNotIn("用 `artifacts` 分别登记", experiment)

        claim = self.read_template_document("claim-evidence-record")
        claim_metadata = self.parse_yaml_metadata(claim)
        self.assert_claim_evidence_template_metadata(claim_metadata)
        self.assertIn("一个证据项不等于一条产品主张", claim)
        self.assertIn("支持和反驳证据必须分列", claim)
        self.assertNotIn("claim_maturity", claim)

        freeze = self.read_template_document("coverage-and-freeze")
        freeze_metadata = self.parse_yaml_metadata(freeze)
        self.assert_composite_template_metadata(freeze_metadata)
        self.assert_coverage_gate_metadata(freeze_metadata)
        self.assertNotIn(
            "| G0–G7 | pending / pass / fail / not-applicable |", freeze
        )
        for contract in (
            "先冻结分母，再计算分子",
            "active",
            "replaced",
            "withdrawn",
            "content outputs",
            "child/phase summaries",
            "root summary",
            "detached freeze manifest/attestation",
            "不得递归包含自身哈希",
        ):
            self.assertIn(contract, freeze)
        coverage_dimensions = (
            "structure",
            "product",
            "semantic",
            "runtime",
            "data",
            "permission",
            "integration",
            "non-functional",
            "trace",
        )
        dimensions = freeze_metadata.get("dimensions")
        self.assertIsInstance(dimensions, dict)
        self.assertEqual(set(coverage_dimensions), set(dimensions))
        for dimension in coverage_dimensions:
            record = dimensions[dimension]
            self.assertEqual(
                {
                    "denominator",
                    "numerator",
                    "unknown_count",
                    "conflicting_count",
                    "excluded_count",
                    "risk_counts",
                },
                set(record),
            )
            for count_key in (
                "denominator",
                "numerator",
                "unknown_count",
                "conflicting_count",
                "excluded_count",
            ):
                self.assertIsInstance(record[count_key], int)
                self.assertGreaterEqual(record[count_key], 0)
            self.assertEqual(
                record["denominator"],
                record["numerator"]
                + record["unknown_count"]
                + record["conflicting_count"]
                + record["excluded_count"],
            )
            self.assertEqual({"P0", "P1", "P2"}, set(record["risk_counts"]))
            for risk_count in record["risk_counts"].values():
                self.assertIsInstance(risk_count, int)
                self.assertGreaterEqual(risk_count, 0)

    def test_coverage_template_yaml_is_directly_schema_compatible(self):
        metadata = self.parse_yaml_metadata(
            self.read_template_document("coverage-and-freeze")
        )
        schema = self.read_json_file(SCHEMA_DOCUMENTS["coverage-summary"])
        self.assertEqual(set(schema["required"]), set(metadata))
        self.assertEqual(
            set(schema["properties"]["dimensions"]["required"]),
            set(metadata["dimensions"]),
        )
        dimension_fields = set(schema["$defs"]["coverageDimension"]["required"])
        for dimension in metadata["dimensions"].values():
            self.assertEqual(dimension_fields, set(dimension))
        for gate_id, gate in metadata["gates"].items():
            gate_definition = "g5Gate" if gate_id == "G5" else "gate"
            self.assertEqual(
                set(schema["$defs"][gate_definition]["required"]), set(gate)
            )
        document = self.read_template_document("coverage-and-freeze")
        self.assertIn(
            "gap_count = runtime.unknown_count + runtime.conflicting_count",
            document,
        )

    def test_coverage_template_status_text_matches_shared_lifecycle_enum(self):
        schema = self.read_json_file(SCHEMA_DOCUMENTS["definitions"])
        lifecycle = schema["$defs"]["recordLifecycle"]["enum"]
        document = self.read_template_document("coverage-and-freeze")
        metadata = self.parse_yaml_metadata(document)
        self.assertIn(metadata["status"], lifecycle)
        lifecycle_section = self.section_text(document, "## 产物生命周期")
        for status in lifecycle:
            with self.subTest(status=status):
                self.assertIn(f"`{status}`", lifecycle_section)
        self.assertIn("`draft` 是合法初始状态", lifecycle_section)
        self.assertNotIn("只使用 `active`、`replaced`、`withdrawn`", lifecycle_section)

    def test_coverage_template_rejects_g5_not_applicable(self):
        metadata = self.parse_yaml_metadata(
            self.read_template_document("coverage-and-freeze")
        )
        mutation = copy.deepcopy(metadata)
        mutation["gates"]["G5"]["verdict"] = "not-applicable"
        mutation["gates"]["G5"]["decided_at"] = "2000-01-01T00:00:00Z"
        with self.assertRaises(AssertionError):
            self.assert_coverage_gate_metadata(mutation)

    def test_coverage_template_rejects_invalid_g5_branch_combinations(self):
        document = self.read_template_document("coverage-and-freeze")
        metadata = self.parse_yaml_metadata(document)
        self.assertIn(
            "approved-static + pending/pass/fail + "
            "unavailable-with-approved-static-ceiling",
            document,
        )
        g5 = metadata["gates"]["G5"]
        self.assertTrue(
            {
                "selected_branch",
                "runtime_confirmation_status",
                "static_non_runtime_coverage",
            }.issubset(g5)
        )
        self.assert_g5_branch_combination(g5)

        approved_static = copy.deepcopy(g5)
        approved_static["selected_branch"] = "approved-static"
        approved_static["verdict"] = "pass"
        approved_static[
            "runtime_confirmation_status"
        ] = "unavailable-with-approved-static-ceiling"
        approved_static["static_non_runtime_coverage"] = {
            "gap_artifact_reference": {
                "id": "REPLACE_WITH_ART_P5_RUNTIME_GAP_ID",
                "sha256": "REPLACE_WITH_SHA256",
            },
            "gap_count": 1,
        }
        self.assert_g5_branch_combination(approved_static)

        approved_static_pending = copy.deepcopy(approved_static)
        approved_static_pending["verdict"] = "pending"
        self.assert_g5_branch_combination(approved_static_pending)
        approved_static_pending_record = copy.deepcopy(metadata)
        approved_static_pending_record["gates"]["G5"] = approved_static_pending
        self.assert_coverage_gate_metadata(approved_static_pending_record)

        invalid_mutations = []
        runtime_confirmed_while_pending = copy.deepcopy(g5)
        runtime_confirmed_while_pending[
            "runtime_confirmation_status"
        ] = "confirmed"
        invalid_mutations.append(runtime_confirmed_while_pending)
        static_claims_runtime_confirmation = copy.deepcopy(approved_static)
        static_claims_runtime_confirmation[
            "runtime_confirmation_status"
        ] = "confirmed"
        invalid_mutations.append(static_claims_runtime_confirmation)
        static_hides_gap = copy.deepcopy(approved_static)
        static_hides_gap["static_non_runtime_coverage"]["gap_count"] = 0
        invalid_mutations.append(static_hides_gap)
        static_clears_gap = copy.deepcopy(approved_static_pending)
        static_clears_gap["static_non_runtime_coverage"] = {
            "gap_artifact_reference": None,
            "gap_count": 0,
        }
        invalid_mutations.append(static_clears_gap)
        for mutation in invalid_mutations:
            with self.subTest(mutation=mutation):
                with self.assertRaises(AssertionError):
                    self.assert_g5_branch_combination(mutation)

    def test_experiment_template_rejects_missing_artifact_or_protocol_field(self):
        artifacts = self.parse_all_yaml_metadata(
            self.read_template_document("experiment-record")
        )
        self.assertEqual(3, len(artifacts))

        missing_artifact = copy.deepcopy(artifacts[:-1])
        with self.assertRaises(AssertionError):
            self.assert_experiment_artifact_packages(missing_artifact)

        missing_protocol_field = copy.deepcopy(artifacts)
        protocol = next(
            item
            for item in missing_protocol_field
            if item["artifact_type"] == "ART-P5-PROTOCOL"
        )
        del protocol["recovery"]["max_restore_time"]
        with self.assertRaises(AssertionError):
            self.assert_experiment_artifact_packages(missing_protocol_field)

    def test_experiment_result_and_effects_reject_protocol_boundary_tampering(self):
        artifacts = self.parse_all_yaml_metadata(
            self.read_template_document("experiment-record")
        )
        self.assertEqual(3, len(artifacts))

        tampered_hash = copy.deepcopy(artifacts)
        result = next(
            item
            for item in tampered_hash
            if item["artifact_type"] == "ART-P5-RESULT"
        )
        result["protocol_reference"][
            "protocol_content_hash"
        ] = "sha256:TAMPERED"
        with self.assertRaises(AssertionError):
            self.assert_experiment_artifact_packages(tampered_hash)

        copied_protocol_truth = copy.deepcopy(artifacts)
        effects = next(
            item
            for item in copied_protocol_truth
            if item["artifact_type"] == "ART-P5-EFFECTS"
        )
        effects["expected_observations"] = []
        with self.assertRaises(AssertionError):
            self.assert_experiment_artifact_packages(copied_protocol_truth)

    def test_experiment_derived_artifacts_reject_protocol_context_drift(self):
        artifacts = self.parse_all_yaml_metadata(
            self.read_template_document("experiment-record")
        )
        context_mutations = (
            ("ART-P5-RESULT", "product_version", "MUTATED_VERSION"),
            ("ART-P5-RESULT", "scope_or_module", "MUTATED_SCOPE"),
            ("ART-P5-EFFECTS", "product_version", "MUTATED_VERSION"),
            ("ART-P5-EFFECTS", "scope_or_module", "MUTATED_SCOPE"),
        )
        for artifact_type, field, replacement in context_mutations:
            with self.subTest(artifact_type=artifact_type, field=field):
                mutation = copy.deepcopy(artifacts)
                target = next(
                    item
                    for item in mutation
                    if item["artifact_type"] == artifact_type
                )
                target[field] = replacement
                with self.assertRaises(AssertionError):
                    self.assert_experiment_artifact_packages(mutation)

    def test_experiment_artifacts_reject_ghost_evidence_and_bad_failure_run(self):
        artifacts = self.parse_all_yaml_metadata(
            self.read_template_document("experiment-record")
        )
        ghost_evidence_mutations = (
            ("ART-P5-RESULT", ("run_results", 0, "evidence_references")),
            (
                "ART-P5-RESULT",
                ("independent_reproduction_results", 0, "evidence_references"),
            ),
            ("ART-P5-RESULT", ("first_failure", "evidence_references")),
            (
                "ART-P5-EFFECTS",
                ("side_effect_records", 0, "disposition_proof_references"),
            ),
            (
                "ART-P5-EFFECTS",
                ("cleanup", "disposition_proof_references"),
            ),
            ("ART-P5-EFFECTS", ("residual_checks", "evidence_references")),
        )
        for artifact_type, path in ghost_evidence_mutations:
            with self.subTest(artifact_type=artifact_type, path=path):
                mutation = copy.deepcopy(artifacts)
                target = next(
                    item
                    for item in mutation
                    if item["artifact_type"] == artifact_type
                )
                nested = target
                for segment in path[:-1]:
                    nested = nested[segment]
                nested[path[-1]] = ["evidence:mutation.ghost"]
                with self.assertRaises(AssertionError):
                    self.assert_experiment_artifact_packages(mutation)

        bad_failure_run = copy.deepcopy(artifacts)
        result = next(
            item
            for item in bad_failure_run
            if item["artifact_type"] == "ART-P5-RESULT"
        )
        result["first_failure"]["present"] = True
        result["first_failure"]["run_id"] = "run:mutation.not-declared"
        with self.assertRaises(AssertionError):
            self.assert_experiment_artifact_packages(bad_failure_run)

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

        mutations = {
            "routes partial source to white box": document.replace(
                "只有编译产物、配置、数据库或部分源码时，选择"
                "[灰盒访问轨道](../access-tracks/gray-box.md)",
                "只有编译产物、配置、数据库或部分源码时，选择"
                "[白盒访问轨道](../access-tracks/white-box.md)",
            ),
            "requires build materials for white box": document.replace(
                "拥有完整且已获授权读取的源码时，选择"
                "[白盒访问轨道](../access-tracks/white-box.md)",
                "拥有完整源码和获准读取的构建材料时，选择"
                "[白盒访问轨道](../access-tracks/white-box.md)",
            ),
            "makes build execution implicit": document.replace(
                "构建文件/材料、构建执行和运行观察是相互独立的可选证据与权限面",
                "源码获准后构建执行和运行观察自动获准",
            ),
        }
        for name, mutation in mutations.items():
            with self.subTest(mutation=name):
                with self.assertRaises(AssertionError):
                    self.assert_delphi_access_track_selection(mutation)

    def test_delphi_runtime_lab_records_only_the_identity_used_by_each_branch(self):
        document = self.read_stack_document("delphi-desktop")
        self.assert_delphi_lab_identity_is_branch_specific(document)

        mutations = {
            "requires database identity universally": document.replace(
                "不要求每次实验记录数据库身份",
                "每次实验都必须记录数据库身份",
            ),
            "omits explicit no-data identity": document.replace(
                "无数据层分支显式记录 `no-data-layer`",
                "无数据层分支不记录数据身份",
            ),
        }
        for name, mutation in mutations.items():
            with self.subTest(mutation=name):
                with self.assertRaises(AssertionError):
                    self.assert_delphi_lab_identity_is_branch_specific(mutation)

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
            "授权、身份、版本、实际分支目标或隔离状态漂移时立即停止",
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
            "unqualified typed-link source": document.replace(
                "`evidence:sample.run-001` → `validates` → "
                "`claim:sample.export-visible`",
                "`SAN-SOURCE-01` → `validates` → `claim:sample.export-visible`",
                1,
            ),
            "unqualified typed-link target": document.replace(
                "`evidence:sample.run-001` → `validates` → "
                "`claim:sample.export-visible`",
                "`evidence:sample.run-001` → `validates` → `SAN-TARGET-01`",
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

    def test_web_stack_guide_exists_and_is_linked_from_the_guide_readme(self):
        guide = self.read_guide()
        path = STACK_DOCUMENTS["web-products"]
        self.assertTrue(path.is_file(), f"missing Web stack guide: {path}")
        relative_path = path.relative_to(GUIDE_ROOT).as_posix()
        self.assertIn(f"]({relative_path})", guide)

    def test_web_stack_guide_has_one_proposed_maturity_and_applicability(self):
        document = self.read_stack_document("web-products")
        maturity_declarations = [
            line.strip()
            for line in document.splitlines()
            if line.strip().removeprefix("**").startswith("证据成熟度：")
        ]
        self.assertEqual(["**证据成熟度：`proposed`**"], maturity_declarations)
        self.assert_one_nonblank_applicability_declaration(document)
        self.assertNotIn("/Users/", document)
        self.assertNotRegex(document, r"(?i)\b(?:TODO|TBD|FIXME)\b|待补(?:充|全)")

    def test_web_stack_guide_has_all_substantive_sections(self):
        document = self.read_stack_document("web-products")
        for section_name in REQUIRED_WEB_SECTIONS:
            with self.subTest(section=section_name):
                section = self.section_text(document, f"## {section_name}")
                substantive_lines = [
                    line
                    for line in section.splitlines()[1:]
                    if line.strip() and not line.startswith("#")
                ]
                self.assertGreaterEqual(
                    len(substantive_lines), 2, f"thin Web section: {section_name}"
                )

    def test_web_inventory_covers_role_plan_locale_device_and_data_states(self):
        document = self.read_stack_document("web-products")
        product_map = self.section_text(document, "## 路由与产品地图")
        workflow = self.section_text(document, "## 有序工作流")
        for dimension in ("角色", "套餐", "语言/地区", "设备/视口", "数据状态"):
            with self.subTest(dimension=dimension):
                self.assertIn(dimension, product_map + workflow)
        for state in ("空", "有数据", "加载中", "错误", "权限拒绝"):
            with self.subTest(state=state):
                self.assertIn(state, product_map)
        self.assertIn("浏览器路由", product_map)
        self.assertIn("后端端点", product_map)
        self.assertIn("不同稳定 ID", product_map)

    def test_web_rendering_dom_state_storage_and_environment_surfaces_are_covered(self):
        document = self.read_stack_document("web-products")
        required_terms = {
            "## 渲染模式与水合": ("SSR", "CSR", "静态生成", "hydration", "水合不一致"),
            "## DOM 与可访问性树": ("DOM", "可访问性树", "焦点", "键盘", "语义"),
            "## 组件、客户端状态、表单与校验": (
                "组件",
                "客户端状态",
                "表单",
                "客户端校验",
                "服务端校验",
            ),
            "## 浏览器持久状态": ("Cookie", "Web Storage", "IndexedDB"),
            "## Service Worker 与离线": ("Service Worker", "缓存", "离线", "更新"),
            "## 功能开关与实验": ("功能开关", "实验", "分桶", "制品"),
            "## 响应式、设备、语言与时间状态": (
                "响应式",
                "设备",
                "语言/地区",
                "时区",
            ),
        }
        for heading, terms in required_terms.items():
            section = self.section_text(document, heading)
            for term in terms:
                with self.subTest(heading=heading, term=term):
                    self.assertIn(term, section)

    def test_web_current_session_network_contract_covers_protocol_semantics(self):
        document = self.read_stack_document("web-products")
        network = self.section_text(document, "## 当前授权会话的网络证据")
        self.assertIn(WEB_SESSION_EVIDENCE_CONTRACT, network)
        self.assertNotIn("只记录当前合法会话中由已执行用户动作实际产生", network)
        for provenance in (
            "用户动作",
            "生命周期自动化",
            "轮询",
            "重连",
            "令牌刷新",
            "预取",
            "服务端推送",
            "Service Worker",
            "后台同步",
            "卸载遥测",
            "第三方效应",
            "因果 provenance",
        ):
            with self.subTest(provenance=provenance):
                self.assertIn(provenance, network)
        for field in (
            "请求身份",
            "响应事实",
            "schema",
            "分页",
            "错误",
            "幂等",
            "异步结果",
            "脱敏",
        ):
            with self.subTest(field=field):
                self.assertIn(field, network)

        protocols = self.section_text(document, "## API、流式通信与文件传输")
        for protocol in (
            "REST",
            "GraphQL",
            "WebSocket",
            "SSE",
            "下载",
            "上传",
            "流式",
            "后台",
        ):
            with self.subTest(protocol=protocol):
                self.assertIn(protocol, protocols)

    def test_web_network_boundary_rejects_replay_and_endpoint_enumeration_mutations(self):
        document = self.read_stack_document("web-products")
        network = self.section_text(document, "## 当前授权会话的网络证据")
        self.assertIn(WEB_SESSION_EVIDENCE_CONTRACT, network)
        mutations = {
            "allows arbitrary replay": document.replace(
                WEB_SESSION_EVIDENCE_CONTRACT,
                "- **会话证据边界：** 可以重放和修改任意请求以补齐证据。",
            ),
            "allows endpoint enumeration": document.replace(
                WEB_SESSION_EVIDENCE_CONTRACT,
                "- **会话证据边界：** 当前会话暴露的端点可以扩展为枚举清单。",
            ),
            "collapses session traffic into direct user action": document.replace(
                WEB_SESSION_EVIDENCE_CONTRACT,
                "- **会话证据边界：** 只记录直接用户动作产生的请求，并把同一时段"
                "流量都归因于该动作。",
            ),
        }
        for name, mutation in mutations.items():
            with self.subTest(mutation=name):
                mutated_network = self.section_text(
                    mutation, "## 当前授权会话的网络证据"
                )
                with self.assertRaises(AssertionError):
                    self.assertIn(WEB_SESSION_EVIDENCE_CONTRACT, mutated_network)

    def test_web_claim_planes_are_split_and_reject_semantic_overclaiming(self):
        document = self.read_stack_document("web-products")
        self.assert_web_claim_split_contract(document)
        mutations = {
            "hidden button proves server authorization": document.replace(
                WEB_AUTHORIZATION_CLAIM_CONTRACT,
                "- **授权主张边界：** 前端隐藏按钮证明服务端拒绝该角色。",
            ),
            "bundle presence proves reachability": document.replace(
                WEB_BUNDLE_REACHABILITY_CONTRACT,
                "- **可达性主张边界：** bundle 中存在代码就证明能力已部署且可达。",
            ),
            "frontend inference becomes runtime confirmed": document.replace(
                "| 隐藏服务端实现或数据模型（前端推断） | `inferred` |",
                "| 隐藏服务端实现或数据模型（前端推断） | `runtime-confirmed` |",
            ),
            "backend static evidence becomes runtime confirmed": document.replace(
                "| 隐藏服务端实现或数据模型（授权后端静态证据） | "
                "`statically-supported` |",
                "| 隐藏服务端实现或数据模型（授权后端静态证据） | "
                "`runtime-confirmed` |",
            ),
            "removes backend and UI claim separation": document.replace(
                WEB_BACKEND_CLAIM_SEPARATION_CONTRACT,
                "- **后端主张边界：** 浏览器结果可以直接证明隐藏服务端实现。",
            ),
        }
        for name, mutation in mutations.items():
            with self.subTest(mutation=name):
                with self.assertRaises(AssertionError):
                    self.assert_web_claim_split_contract(mutation)

    def test_web_permissions_flags_telemetry_and_artifacts_preserve_evidence_limits(self):
        document = self.read_stack_document("web-products")
        permissions = self.section_text(document, "## 角色、权限、租户与套餐")
        for boundary in (
            "角色",
            "权限",
            "租户",
            "套餐",
            "服务端",
            "可观察的允许或拒绝结果",
            "不猜测",
        ):
            with self.subTest(boundary=boundary):
                self.assertIn(boundary, permissions)

        telemetry = self.section_text(document, "## 遥测与可观测性")
        for surface in ("埋点", "错误上报", "性能", "关联 ID", "第三方"):
            with self.subTest(surface=surface):
                self.assertIn(surface, telemetry)

        artifacts = self.section_text(document, "## 源码、构建产物与前端制品")
        for artifact in ("源码", "构建", "chunk", "source map", "内容哈希"):
            with self.subTest(artifact=artifact):
                self.assertIn(artifact, artifacts)
        self.assertIn("仅在现有、获准范围内", artifacts)

    def test_web_vertical_example_uses_qualified_endpoint_ids_core_relations_and_statuses(self):
        document = self.read_stack_document("web-products")
        self.assert_web_vertical_example_contract(document)
        for forbidden in ("/admin", "tenant_id", "`dispatches-to`", "`transitions-to`"):
            self.assertNotIn(forbidden, document)

        mutations = {
            "browser route masquerades as endpoint": document.replace(
                "| `integration:sample.current-session-endpoint` | `backend-endpoint` |",
                "| `product-surface:sample.browser-route` | `backend-endpoint` |",
            ),
            "unqualified endpoint id": document.replace(
                "integration:sample.current-session-endpoint",
                "API-ENDPOINT-1",
            ),
            "unregistered relation": document.replace(
                "| `trace-link:sample.handler-to-endpoint` | "
                "`asset:sample.client-handler` | `calls` |",
                "| `trace-link:sample.handler-to-endpoint` | "
                "`asset:sample.client-handler` | `dispatches-to` |",
            ),
            "internal implementation runtime overclaim": document.replace(
                "`capability:sample.accept-action` | `statically-supported` | `optional` |",
                "`capability:sample.accept-action` | `runtime-confirmed` | `optional` |",
            ),
            "static client endpoint edge upgraded to runtime": document.replace(
                "`integration:sample.current-session-endpoint` | "
                "`statically-supported` | `required` |",
                "`integration:sample.current-session-endpoint` | "
                "`runtime-confirmed` | `required` |",
            ),
            "drops conditional async visible edge": document.replace(
                "| `trace-link:sample.async-to-visible` | "
                "`integration:sample.async-outcome` | `supports` | "
                "`claim:sample.visible-result` | `inferred` | `optional` | "
                "`evidence:sample.async-candidate` | "
                "`context:sample.session-version` |\n",
                "",
            ),
            "upgrades conditional async visible edge": document.replace(
                "`claim:sample.visible-result` | `inferred` | `optional` |",
                "`claim:sample.visible-result` | `runtime-confirmed` | `required` |",
            ),
            "missing evidence reference": document.replace(
                "| `trace-link:sample.handler-to-endpoint` | "
                "`asset:sample.client-handler` | `calls` | "
                "`integration:sample.current-session-endpoint` | "
                "`statically-supported` | `required` | "
                "`evidence:sample.client-static` | "
                "`context:sample.frontend-build` |",
                "| `trace-link:sample.handler-to-endpoint` | "
                "`asset:sample.client-handler` | `calls` | "
                "`integration:sample.current-session-endpoint` | "
                "`statically-supported` | `required` |  | "
                "`context:sample.frontend-build` |",
            ),
            "invalid evidence reference": document.replace(
                "| `trace-link:sample.route-to-capability` | "
                "`product-surface:sample.browser-route` | `exposes` | "
                "`capability:sample.accept-action` | `observed` | `required` | "
                "`evidence:sample.route-observation` | "
                "`context:sample.session-version` |",
                "| `trace-link:sample.route-to-capability` | "
                "`product-surface:sample.browser-route` | `exposes` | "
                "`capability:sample.accept-action` | `observed` | `required` | "
                "`ROUTE-EVIDENCE` | `context:sample.session-version` |",
            ),
            "missing version context": document.replace(
                "| `trace-link:sample.network-evidence` | "
                "`evidence:sample.network-contract` | `supports` | "
                "`claim:sample.network-contract` | `runtime-confirmed` | "
                "`required` | `evidence:sample.network-contract` | "
                "`context:sample.session-version` |",
                "| `trace-link:sample.network-evidence` | "
                "`evidence:sample.network-contract` | `supports` | "
                "`claim:sample.network-contract` | `runtime-confirmed` | "
                "`required` | `evidence:sample.network-contract` |  |",
            ),
            "invalid version context": document.replace(
                "| `trace-link:sample.route-to-capability` | "
                "`product-surface:sample.browser-route` | `exposes` | "
                "`capability:sample.accept-action` | `observed` | `required` | "
                "`evidence:sample.route-observation` | "
                "`context:sample.session-version` |",
                "| `trace-link:sample.route-to-capability` | "
                "`product-surface:sample.browser-route` | `exposes` | "
                "`capability:sample.accept-action` | `observed` | `required` | "
                "`evidence:sample.route-observation` | `VERSION-1` |",
            ),
            "well-formed undeclared evidence reference": document.replace(
                "`evidence:sample.route-observation` | "
                "`context:sample.session-version` |",
                "`evidence:sample.missing-evidence` | "
                "`context:sample.session-version` |",
                1,
            ),
            "well-formed undeclared context reference": document.replace(
                "`evidence:sample.route-observation` | "
                "`context:sample.session-version` |",
                "`evidence:sample.route-observation` | "
                "`context:sample.missing-context` |",
                1,
            ),
        }
        for name, mutation in mutations.items():
            with self.subTest(mutation=name):
                with self.assertRaises(AssertionError):
                    self.assert_web_vertical_example_contract(mutation)

    def test_web_blind_spots_and_stop_boundaries_are_explicit_and_safe(self):
        document = self.read_stack_document("web-products")
        blind_spots = self.section_text(document, "## 常见盲区")
        for blind_spot in (
            "客户端可见不等于服务端实现",
            "缓存与旧 chunk",
            "水合与竞态",
            "后台与流式终态",
            "多角色、租户与套餐",
            "响应式、语言与时区",
        ):
            with self.subTest(blind_spot=blind_spot):
                self.assertRegex(
                    blind_spots, rf"(?m)^\| {re.escape(blind_spot)} \|"
                )

        stop = self.section_text(document, "## 停止与安全边界")
        prohibited_actions = (
            "认证绕过",
            "隐藏租户 ID",
            "凭据提取",
            "规避付费功能",
            "任意端点枚举",
            "速率滥用",
            "授权范围外发现 source map",
            "超出已批准实验重放或修改请求",
        )
        for prohibited in prohibited_actions:
            with self.subTest(prohibited=prohibited):
                self.assertRegex(
                    stop,
                    rf"(?m)^- 禁止.*{re.escape(prohibited)}.*",
                )
        self.assertIn("立即停止", stop)
        self.assertIn("重新授权", stop)

    def test_java_stack_guide_exists_and_is_linked_from_the_guide_readme(self):
        guide = self.read_guide()
        path = STACK_DOCUMENTS["java-backends"]
        self.assertTrue(path.is_file(), f"missing Java stack guide: {path}")
        relative_path = path.relative_to(GUIDE_ROOT).as_posix()
        self.assertIn(f"]({relative_path})", guide)

    def test_java_stack_guide_has_one_proposed_maturity_and_applicability(self):
        document = self.read_stack_document("java-backends")
        maturity_declarations = [
            line.strip()
            for line in document.splitlines()
            if line.strip().removeprefix("**").startswith("证据成熟度：")
        ]
        self.assertEqual(["**证据成熟度：`proposed`**"], maturity_declarations)
        self.assert_one_nonblank_applicability_declaration(document)
        self.assertNotIn("/Users/", document)
        self.assertNotRegex(document, r"(?i)\b(?:TODO|TBD|FIXME)\b|待补(?:充|全)")

    def test_java_stack_guide_has_all_substantive_sections(self):
        document = self.read_stack_document("java-backends")
        for section_name in REQUIRED_JAVA_SECTIONS:
            with self.subTest(section=section_name):
                section = self.section_text(document, f"## {section_name}")
                substantive_lines = [
                    line
                    for line in section.splitlines()[1:]
                    if line.strip() and not line.startswith("#")
                ]
                self.assertGreaterEqual(
                    len(substantive_lines), 2, f"thin Java section: {section_name}"
                )

    def test_java_workflow_follows_the_required_evidence_order(self):
        document = self.read_stack_document("java-backends")
        workflow = self.section_text(document, "## 有序工作流")
        steps = [line for line in workflow.splitlines() if re.match(r"^\d+\. ", line)]
        self.assertEqual(8, len(steps))
        expected_terms = (
            ("Maven/Gradle", "构建图", "依赖图"),
            ("模块", "启动入口", "JAR/WAR", "启动身份"),
            ("路由", "过滤器/拦截器"),
            ("控制器", "服务", "仓储"),
            ("事务边界", "传播"),
            ("持久化", "数据库"),
            ("若实际存在消息或任务分支", "消息", "任务"),
            ("可见结果", "对外契约"),
        )
        for step, terms in zip(steps, expected_terms):
            for term in terms:
                with self.subTest(step=step, term=term):
                    self.assertIn(term, step)
        self.assert_java_evidence_planes_remain_distinct(document)

        overclaim = document.replace(
            "| 源码结构 | `statically-supported` |",
            "| 源码结构 | `runtime-confirmed` |",
        )
        self.assertNotEqual(document, overclaim)
        with self.assertRaises(AssertionError):
            self.assert_java_evidence_planes_remain_distinct(overclaim)

    def test_java_frameworks_and_topology_are_conditional_and_mutation_guarded(self):
        document = self.read_stack_document("java-backends")
        self.assert_java_framework_topology_is_conditional(document)
        mutations = {
            "forces Spring JPA and messaging": document.replace(
                "不得把 Spring、Jakarta、JPA 或消息系统写成必经层",
                "所有 Java 后端都按 Spring、JPA 和消息系统建立必经层",
            ),
            "forces persistence framework": document.replace(
                "JPA/Hibernate、MyBatis、JDBC 与动态 SQL 都按实际发现选择",
                "所有 Java 后端都使用 JPA/Hibernate",
            ),
            "forces messaging": document.replace(
                "消息代理、Outbox 和消费者都是可选分支",
                "消息代理、Outbox 和消费者都是必经分支",
            ),
        }
        for name, mutation in mutations.items():
            with self.subTest(mutation=name):
                self.assertNotEqual(document, mutation)
                with self.assertRaises(AssertionError):
                    self.assert_java_framework_topology_is_conditional(mutation)

    def test_java_runtime_semantics_remain_evidence_questions(self):
        document = self.read_stack_document("java-backends")
        proxy = self.section_text(document, "## DI、代理、AOP、反射与生成代码")
        for contract in (
            "只有证据确认使用相应代理机制时，才提出代理拦截与 self-invocation 问题",
            "普通对象或非代理调用不得套用该结论",
            "注解",
            "反射",
            "自动配置",
            "生成代码",
        ):
            self.assertIn(contract, proxy)

        config = self.section_text(document, "## 配置、Profile 与环境优先级")
        self.assertIn("配置优先级必须按每个部署实测", config)
        self.assertIn("不得假定一条跨框架、跨版本的固定优先级", config)

        persistence = self.section_text(document, "## 持久化、SQL 与迁移")
        for question in ("lazy/eager", "N+1", "证据问题"):
            self.assertIn(question, persistence)

        transactions = self.section_text(document, "## 事务边界与传播")
        self.assertIn("事务传播不得仅凭注解名称推定", transactions)
        self.assertIn("事务不会按假设跨越异步边界", transactions)

        messaging = self.section_text(document, "## 消息、Outbox 与消费者")
        self.assertIn(
            "不能仅因依赖中出现消息库就推定重试、顺序或投递语义",
            messaging,
        )

    def test_java_generated_persistence_factories_and_mappers_have_claim_ceilings(self):
        document = self.read_stack_document("java-backends")
        persistence = self.section_text(document, "## 持久化、SQL 与迁移")
        generated = self.section_text(persistence, "### 生成式持久化调用")
        for contract in (
            "Spring Data repository factory/proxy 仅在实际发现时建立",
            "派生查询方法",
            "自定义 fragment/实现",
            "接口方法可能在运行时由 factory/proxy 提供实现",
            "MyBatis mapper proxy",
            "XML statement",
            "注解 SQL",
            "namespace + statement ID",
            "不得虚构方法体",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, generated)

        expected_rows = {
            "Spring Data 接口声明": (
                "statically-supported",
                "不证明目标部署生成代理或调用该方法",
            ),
            "MyBatis mapper 声明": (
                "statically-supported",
                "不证明 mapper proxy 已创建或 SQL 已执行",
            ),
            "部署注册/装配元数据": (
                "observed",
                "不证明某请求调用该代理",
            ),
            "已关联的代理/mapper 调用": (
                "runtime-confirmed",
                "只限已绑定部署、配置、输入和 SQL/结果的调用",
            ),
        }
        observed_rows = {}
        for line in generated.splitlines():
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

        mutations = {
            "forces Spring Data": document.replace(
                "Spring Data repository factory/proxy 仅在实际发现时建立",
                "每个 repository 都按 Spring Data factory/proxy 建立",
            ),
            "promotes interface declaration to runtime": document.replace(
                "| Spring Data 接口声明 | `statically-supported` |",
                "| Spring Data 接口声明 | `runtime-confirmed` |",
            ),
            "invents generated method body": document.replace(
                "不得虚构方法体",
                "按接口名称补写生成方法体",
            ),
        }
        for name, mutation in mutations.items():
            with self.subTest(mutation=name):
                self.assertNotEqual(document, mutation)
                mutated_persistence = self.section_text(
                    mutation, "## 持久化、SQL 与迁移"
                )
                mutated_generated = self.section_text(
                    mutated_persistence, "### 生成式持久化调用"
                )
                with self.assertRaises(AssertionError):
                    if name == "promotes interface declaration to runtime":
                        mutated_rows = {}
                        for line in mutated_generated.splitlines():
                            match = re.fullmatch(
                                r"\| ([^|]+) \| `([^`]+)` \| [^|]+ \| ([^|]+) \|",
                                line,
                            )
                            if match and match.group(1).strip() in expected_rows:
                                mutated_rows[match.group(1).strip()] = (
                                    match.group(2).strip(),
                                    match.group(3).strip(),
                                )
                        self.assertEqual(expected_rows, mutated_rows)
                    else:
                        required = (
                            "Spring Data repository factory/proxy 仅在实际发现时建立",
                            "不得虚构方法体",
                        )
                        for contract in required:
                            self.assertIn(contract, mutated_generated)

    def test_java_compiled_only_evidence_records_identity_and_claim_ceiling(self):
        document = self.read_stack_document("java-backends")
        compiled = self.section_text(document, "## 仅编译制品与反编译边界")
        for field in (
            "制品 SHA-256",
            "Java/class 版本",
            "依赖与 package 元数据",
            "签名可用性",
            "调试符号可用性",
            "反编译器与工具版本",
            "synthetic",
            "bridge",
            "生成代码",
            "名称缺失",
        ):
            with self.subTest(field=field):
                self.assertIn(field, compiled)
        self.assertIn("反编译结果不是原始源码", compiled)
        self.assertIn("不得据此解释开发者意图", compiled)

    def test_java_runtime_log_and_database_work_are_separately_authorized_and_safe(self):
        document = self.read_stack_document("java-backends")
        runtime = self.section_text(document, "## 运行时关联")
        for contract in (
            "运行、日志与数据库操作必须分别授权",
            "绑定当前 `ART-G0-AUTH`",
            "`verdict` 为 `pass`",
            "只读为默认",
        ):
            self.assertIn(contract, runtime)

        stop = self.section_text(document, "## 常见盲区与停止规则")
        for contract in (
            "不得提取凭据或秘密",
            "不得对生产环境执行破坏性写入",
            "授权、版本或环境不匹配",
            "敏感信息泄露",
            "立即停止",
            "重新授权",
        ):
            self.assertIn(contract, stop)

    def test_java_vertical_trace_resolves_graph_evidence_and_context(self):
        document = self.read_stack_document("java-backends")
        self.assert_java_vertical_example_contract(document)
        mutations = {
            "unqualified endpoint": document.replace(
                "integration:sample.http-input",
                "HTTP-INPUT-1",
            ),
            "unregistered relation": document.replace(
                "| `trace-link:sample.http-to-validation` | "
                "`integration:sample.http-input` | `calls` |",
                "| `trace-link:sample.http-to-validation` | "
                "`integration:sample.http-input` | `dispatches-to` |",
            ),
            "static service overclaim": document.replace(
                "| `asset:sample.java-service` | `service` | "
                "`statically-supported` |",
                "| `asset:sample.java-service` | `service` | "
                "`runtime-confirmed` |",
            ),
            "missing evidence": document.replace(
                "| `trace-link:sample.http-to-validation` | "
                "`integration:sample.http-input` | `calls` | "
                "`asset:sample.validation` | `statically-supported` | "
                "`shared` | `evidence:sample.source-structure` | "
                "`context:sample.source-artifact` |",
                "| `trace-link:sample.http-to-validation` | "
                "`integration:sample.http-input` | `calls` | "
                "`asset:sample.validation` | `statically-supported` | "
                "`shared` |  | `context:sample.source-artifact` |",
            ),
            "undeclared evidence": document.replace(
                "`evidence:sample.source-structure` | "
                "`context:sample.source-artifact` |",
                "`evidence:sample.missing-source` | "
                "`context:sample.source-artifact` |",
                1,
            ),
            "undeclared context": document.replace(
                "`evidence:sample.source-structure` | "
                "`context:sample.source-artifact` |",
                "`evidence:sample.source-structure` | "
                "`context:sample.missing-source` |",
                1,
            ),
            "breaks atomic business outbox outcome": document.replace(
                "| `data:sample.atomic-business-outbox-commit` | "
                "`atomic-business-outbox-transaction-outcome` |",
                "| `data:sample.atomic-business-outbox-commit` | `outbox-row` |",
            ),
            "disconnects async path": document.replace(
                "| `trace-link:sample.transaction-to-atomic-outcome` | "
                "`asset:sample.transaction` | `writes` | "
                "`data:sample.atomic-business-outbox-commit` |",
                "| `trace-link:sample.transaction-to-atomic-outcome` | "
                "`asset:sample.java-service` | `writes` | "
                "`data:sample.atomic-business-outbox-commit` |",
            ),
            "consumer precedes sync response": document.replace(
                "| `trace-link:sample.commit-to-http-response` | "
                "`data:sample.business-commit` | `supports` | "
                "`integration:sample.http-response` |",
                "| `trace-link:sample.commit-to-http-response` | "
                "`asset:sample.consumer-job` | `supports` | "
                "`integration:sample.http-response` |",
            ),
            "drops independent later visible validation": document.replace(
                "| `trace-link:sample.runtime-to-later-visible` | "
                "`evidence:sample.runtime-later-visible` | `validates` |",
                "| `trace-link:sample.runtime-to-later-visible` | "
                "`evidence:sample.runtime-later-visible` | `supports` |",
            ),
        }
        for name, mutation in mutations.items():
            with self.subTest(mutation=name):
                self.assertNotEqual(document, mutation)
                with self.assertRaises(AssertionError):
                    self.assert_java_vertical_example_contract(mutation)

    def test_dotnet_stack_guide_contract(self):
        path = STACK_DOCUMENTS["dotnet-backends"]
        self.assertTrue(path.is_file(), f"missing .NET stack guide: {path}")
        guide = self.read_guide()
        self.assertIn(f"]({path.relative_to(GUIDE_ROOT).as_posix()})", guide)
        document = self.read_stack_document("dotnet-backends")

        maturity_declarations = [
            line.strip()
            for line in document.splitlines()
            if line.strip().removeprefix("**").startswith("证据成熟度：")
        ]
        self.assertEqual(["**证据成熟度：`proposed`**"], maturity_declarations)
        self.assert_one_nonblank_applicability_declaration(document)
        self.assertNotIn("/Users/", document)
        self.assertNotRegex(document, r"(?i)\b(?:TODO|TBD|FIXME)\b|待补(?:充|全)")
        self.assertNotIn("Spring Data", document)
        self.assertNotIn("JAR/WAR", document)

        for section_name in REQUIRED_DOTNET_SECTIONS:
            with self.subTest(section=section_name):
                section = self.section_text(document, f"## {section_name}")
                substantive_lines = [
                    line
                    for line in section.splitlines()[1:]
                    if line.strip() and not line.startswith("#")
                ]
                self.assertGreaterEqual(
                    len(substantive_lines), 2, f"thin .NET section: {section_name}"
                )

        build = self.section_text(
            document, "## Solution、Project、TFM 与构建身份"
        )
        for term in (
            ".sln",
            ".csproj",
            "TargetFramework",
            "TargetFrameworks",
            "SDK",
            "NuGet",
            "restore",
            "RID",
            "构建配置",
            "DLL/EXE 哈希",
        ):
            self.assertIn(term, build)
        self.assertIn("目标框架不等于目标部署实际使用的运行时", build)

        hosting = self.section_text(
            document, "## Host 启动、IIS、Kestrel 与部署身份"
        )
        for term in (
            "Generic Host",
            "WebApplication.CreateBuilder",
            "Startup",
            "IIS",
            "Kestrel",
            "进程命令",
            "assembly 哈希",
            "运行时版本",
        ):
            self.assertIn(term, hosting)

        pipeline = self.section_text(
            document, "## ASP.NET Core Middleware 顺序与 Endpoint Routing"
        )
        for contract in (
            "Middleware 的注册顺序、条件分支、短路和响应回程顺序分别记录",
            "Endpoint Routing",
            "UseRouting",
            "UseAuthentication",
            "UseAuthorization",
            "MapControllers",
            "MapGet",
            "源码顺序只支持静态主张",
        ):
            self.assertIn(contract, pipeline)

        traditional = self.section_text(
            document, "## 传统 ASP.NET 条件分支"
        )
        for term in (
            "System.Web",
            "Global.asax",
            "OWIN",
            "ASP.NET MVC",
            "Web API",
            "Web Forms",
            "条件分支",
        ):
            self.assertIn(term, traditional)

        dependency = self.section_text(
            document, "## DI 生命周期、Options 与配置优先级"
        )
        for term in (
            "Singleton",
            "Scoped",
            "Transient",
            "ValidateScopes",
            "IOptions",
            "IOptionsSnapshot",
            "IOptionsMonitor",
            "配置优先级必须按目标部署、框架版本和实际 provider 链取证",
            "不得假定一条跨版本、跨宿主的固定优先级",
        ):
            self.assertIn(term, dependency)

        endpoints = self.section_text(
            document, "## Controller、Minimal API 与服务边界"
        )
        for term in ("Controller", "Minimal API", "endpoint filter", "DTO", "服务"):
            self.assertIn(term, endpoints)

        security = self.section_text(document, "## 校验、认证与授权")
        for term in (
            "模型绑定",
            "DataAnnotations",
            "认证",
            "授权",
            "policy",
            "资源级",
            "租户",
        ):
            self.assertIn(term, security)

        persistence = self.section_text(
            document, "## EF、EF Core、Dapper 与手写 SQL"
        )
        for term in (
            "EF6",
            "EF Core",
            "Dapper",
            "手写 SQL",
            "tracking/no-tracking",
            "lazy/eager",
            "N+1",
            "数据库迁移",
        ):
            self.assertIn(term, persistence)

        transaction = self.section_text(
            document, "## 事务、TransactionScope 与异步边界"
        )
        for term in (
            "DbContext transaction",
            "TransactionScope",
            "ambient transaction",
            "async/await",
            "ConfigureAwait",
            "提交",
            "回滚",
            "不会按假设跨越",
        ):
            self.assertIn(term, transaction)

        exceptions = self.section_text(
            document, "## 异常过滤器与协议结果"
        )
        for term in ("exception filter", "middleware", "ProblemDetails", "首个失败"):
            self.assertIn(term, exceptions)

        background = self.section_text(
            document, "## Hosted Service、任务与消息"
        )
        for term in (
            "IHostedService",
            "BackgroundService",
            "Timer",
            "消息",
            "Outbox",
            "取消",
            "关闭",
        ):
            self.assertIn(term, background)

        legacy = self.section_text(document, "## WCF、Windows Service 与 COM")
        for term in (
            "WCF",
            "binding",
            "endpoint",
            "Windows Service",
            "COM",
            "ProgID/CLSID",
            "assembly binding",
        ):
            self.assertIn(term, legacy)

        compiled = self.section_text(
            document, "## DLL、EXE、IL 与反编译边界"
        )
        for term in (
            "assembly SHA-256",
            "TFM",
            "运行时家族/版本",
            "架构/RID",
            "PDB",
            "反编译器名称、版本、插件、参数与输出哈希",
            "IL",
            "ReadyToRun",
            "single-file",
            "trimming",
            "AOT",
            "混淆",
            "反编译结果不是原始源码",
            "不得据此解释开发者意图",
        ):
            self.assertIn(term, compiled)

        evidence = self.section_text(document, "## 证据平面与主张上限")
        expected_rows = {
            "源码结构": (
                "statically-supported",
                "不证明配置生效、assembly 已部署或路径已执行",
            ),
            "反编译/IL 派生结构": (
                "statically-supported",
                "不等同原始源码，不证明符号、意图或运行路径",
            ),
            "配置与部署装配事实": (
                "observed",
                "不证明请求经过该配置或组件",
            ),
            "已关联运行行为": (
                "runtime-confirmed",
                "只限绑定版本、部署、配置、角色、输入和时间窗的场景",
            ),
        }
        observed_rows = {}
        for line in evidence.splitlines():
            match = re.fullmatch(
                r"\| ([^|]+) \| `([^`]+)` \| [^|]+ \| ([^|]+) \|", line
            )
            if match and match.group(1).strip() in expected_rows:
                observed_rows[match.group(1).strip()] = (
                    match.group(2).strip(),
                    match.group(3).strip(),
                )
        self.assertEqual(expected_rows, observed_rows)

        for contract in (
            "所有具体技术与拓扑都是条件分支",
            "不得把 IIS、Kestrel、ASP.NET Core、EF Core、消息系统、WCF 或 COM 写成必经层",
            "运行、日志、数据库、调试与外部消息操作必须分别授权",
            "绑定当前 `ART-G0-AUTH` 且 `verdict` 为 `pass`",
        ):
            self.assertIn(contract, document)

        trace, node_ids, link_rows = self.parse_registered_typed_trace(
            document, "## 纵向追踪示例"
        )
        for node_id in (
            "asset:sample.dotnet-project",
            "asset:sample.dotnet-assembly",
            "asset:sample.dotnet-host",
            "integration:sample.dotnet-http-input",
            "asset:sample.dotnet-middleware",
            "asset:sample.dotnet-endpoint",
            "asset:sample.dotnet-validation",
            "asset:sample.dotnet-authorization",
            "asset:sample.dotnet-service",
            "asset:sample.dotnet-transaction",
            "data:sample.dotnet-atomic-commit",
            "asset:sample.dotnet-outbox-relay",
            "integration:sample.dotnet-message",
            "asset:sample.dotnet-consumer",
            "claim:sample.dotnet-later-visible",
        ):
            self.assertIn(node_id, node_ids)
        observed_links = {(row[1], row[2], row[3]) for row in link_rows}
        expected_links = {
            ("asset:sample.dotnet-assembly", "derived-from", "asset:sample.dotnet-project"),
            ("asset:sample.dotnet-host", "derived-from", "asset:sample.dotnet-assembly"),
            ("integration:sample.dotnet-http-input", "calls", "asset:sample.dotnet-host"),
            ("asset:sample.dotnet-host", "calls", "asset:sample.dotnet-middleware"),
            ("asset:sample.dotnet-middleware", "calls", "asset:sample.dotnet-endpoint"),
            ("asset:sample.dotnet-endpoint", "calls", "asset:sample.dotnet-authorization"),
            ("asset:sample.dotnet-authorization", "calls", "asset:sample.dotnet-validation"),
            ("asset:sample.dotnet-validation", "calls", "asset:sample.dotnet-service"),
            ("asset:sample.dotnet-service", "calls", "asset:sample.dotnet-transaction"),
            ("asset:sample.dotnet-transaction", "writes", "data:sample.dotnet-atomic-commit"),
            ("asset:sample.dotnet-outbox-relay", "reads", "data:sample.dotnet-atomic-commit"),
            ("asset:sample.dotnet-outbox-relay", "emits", "integration:sample.dotnet-message"),
            ("integration:sample.dotnet-message", "calls", "asset:sample.dotnet-consumer"),
            ("asset:sample.dotnet-consumer", "supports", "claim:sample.dotnet-later-visible"),
            ("evidence:sample.dotnet-visible-run", "validates", "claim:sample.dotnet-later-visible"),
        }
        self.assertTrue(expected_links.issubset(observed_links))
        self.assert_registered_trace_path(
            link_rows,
            "integration:sample.dotnet-http-input",
            "claim:sample.dotnet-later-visible",
        )
        self.assertIn("可选分支缺失时保留缺口且不创建占位边", trace)
        self.assertIn("可见结果由独立运行证据验证", trace)

    def test_data_messaging_and_infrastructure_guide_contract(self):
        path = STACK_DOCUMENTS["data-messaging-and-infrastructure"]
        self.assertTrue(path.is_file(), f"missing infrastructure guide: {path}")
        guide = self.read_guide()
        self.assertIn(f"]({path.relative_to(GUIDE_ROOT).as_posix()})", guide)
        document = self.read_stack_document("data-messaging-and-infrastructure")

        maturity_declarations = [
            line.strip()
            for line in document.splitlines()
            if line.strip().removeprefix("**").startswith("证据成熟度：")
        ]
        self.assertEqual(["**证据成熟度：`proposed`**"], maturity_declarations)
        self.assert_one_nonblank_applicability_declaration(document)
        self.assertNotIn("/Users/", document)
        self.assertNotRegex(document, r"(?i)\b(?:TODO|TBD|FIXME)\b|待补(?:充|全)")

        for section_name in REQUIRED_INFRASTRUCTURE_SECTIONS:
            with self.subTest(section=section_name):
                section = self.section_text(document, f"## {section_name}")
                substantive_lines = [
                    line
                    for line in section.splitlines()[1:]
                    if line.strip() and not line.startswith("#")
                ]
                self.assertGreaterEqual(
                    len(substantive_lines),
                    2,
                    f"thin infrastructure section: {section_name}",
                )

        component = self.section_text(document, "## 组件记录契约")
        fields = [
            match.group(1)
            for line in component.splitlines()
            if (match := re.fullmatch(r"\| `([^`]+)` \| [^|]+ \|", line))
        ]
        self.assertEqual(
            [
                "component ID",
                "owner",
                "version",
                "namespace/tenant",
                "schema",
                "readers",
                "writers",
                "consistency",
                "ordering",
                "idempotency",
                "retry",
                "retention",
                "encryption",
                "backup",
                "restore",
                "observability",
                "failure effect",
            ],
            fields,
        )
        self.assertIn("每个实际发现的组件都必须逐项记录", component)
        self.assertIn("未知值写 `unknown` 并附验证缺口", component)

        section_terms = {
            "## 关系型数据库与 NoSQL": (
                "关系型数据库",
                "NoSQL",
                "schema/catalog",
                "读者",
                "写者",
                "迁移",
                "复制",
            ),
            "## 缓存": (
                "key",
                "TTL",
                "cache-aside",
                "失效",
                "租户",
                "提交",
                "回填",
            ),
            "## 搜索与索引": (
                "索引 schema",
                "文档 ID",
                "刷新",
                "别名",
                "权限过滤",
                "重建",
            ),
            "## 消息与 Outbox/Inbox": (
                "Outbox",
                "Inbox",
                "ack/commit",
                "顺序",
                "幂等",
                "死信",
                "重复",
            ),
            "## 调度任务": (
                "调度注册",
                "时区",
                "leader/lock",
                "misfire",
                "并发",
                "运行记录",
            ),
            "## 文件与对象存储交换": (
                "对象 key/文件路径",
                "内容哈希",
                "临时名",
                "原子重命名",
                "完成标记",
                "重复导入",
            ),
            "## 第三方集成与回调": (
                "第三方回调",
                "签名校验",
                "重放窗口",
                "关联 ID",
                "幂等",
                "终态",
            ),
            "## 网关": ("路由", "认证", "限流", "重试", "超时", "版本"),
            "## 容器与编排平台": (
                "image digest",
                "revision",
                "副本",
                "滚动发布",
                "readiness",
                "网络策略",
            ),
            "## 秘密引用与配置边界": (
                "秘密引用",
                "不得读取或保存秘密值",
                "配置存在",
                "实际注入",
            ),
            "## 可观测性": (
                "trace",
                "日志",
                "指标",
                "关联 ID",
                "采样",
                "首个失败",
            ),
            "## 备份与恢复": (
                "备份存在",
                "恢复演练",
                "RPO",
                "RTO",
                "完整性",
            ),
        }
        for heading, terms in section_terms.items():
            section = self.section_text(document, heading)
            for term in terms:
                with self.subTest(section=heading, term=term):
                    self.assertIn(term, section)

        config = self.section_text(document, "## 配置存在与部署行为")
        expected_rows = {
            "源码/配置文件中的组件声明": (
                "statically-supported",
                "不证明组件已部署、已连接或被调用",
            ),
            "控制面/部署清单中的装配事实": (
                "observed",
                "不证明运行实例健康或业务流量到达",
            ),
            "已关联运行观测": (
                "runtime-confirmed",
                "只限绑定部署、配置、输入和时间窗的行为",
            ),
        }
        observed_rows = {}
        for line in config.splitlines():
            match = re.fullmatch(
                r"\| ([^|]+) \| `([^`]+)` \| [^|]+ \| ([^|]+) \|", line
            )
            if match and match.group(1).strip() in expected_rows:
                observed_rows[match.group(1).strip()] = (
                    match.group(2).strip(),
                    match.group(3).strip(),
                )
        self.assertEqual(expected_rows, observed_rows)
        for contract in (
            "配置存在不得直接声称组件已经部署或产生业务行为",
            "所有组件类别和拓扑都按实际证据条件化",
            "不得把数据库、缓存、搜索、消息、任务、对象存储、网关或容器平台写成必经层",
            "Outbox/Inbox、调度、缓存失效、搜索索引、文件交换和第三方回调都必须从触发到终态逐段取证",
        ):
            self.assertIn(contract, document)

        trace, node_ids, link_rows = self.parse_registered_typed_trace(
            document, "## 基础设施链路示例"
        )
        for node_id in (
            "data:sample.infra-atomic-business-outbox",
            "asset:sample.infra-outbox-relay",
            "integration:sample.infra-message",
            "asset:sample.infra-consumer",
            "data:sample.infra-inbox-record",
            "data:sample.infra-search-document",
            "claim:sample.infra-later-visible",
        ):
            self.assertIn(node_id, node_ids)
        observed_links = {(row[1], row[2], row[3]) for row in link_rows}
        expected_links = {
            ("asset:sample.infra-outbox-relay", "reads", "data:sample.infra-atomic-business-outbox"),
            ("asset:sample.infra-outbox-relay", "emits", "integration:sample.infra-message"),
            ("integration:sample.infra-message", "calls", "asset:sample.infra-consumer"),
            ("asset:sample.infra-consumer", "writes", "data:sample.infra-inbox-record"),
            ("asset:sample.infra-consumer", "writes", "data:sample.infra-search-document"),
            ("data:sample.infra-search-document", "supports", "claim:sample.infra-later-visible"),
            ("evidence:sample.infra-visible-run", "validates", "claim:sample.infra-later-visible"),
        }
        self.assertTrue(expected_links.issubset(observed_links))
        self.assert_registered_trace_path(
            link_rows,
            "data:sample.infra-atomic-business-outbox",
            "claim:sample.infra-later-visible",
        )
        self.assertIn("链路只示范已发现分支，不规定通用拓扑", trace)
        self.assertIn("可见结果由独立运行证据验证", trace)

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
        self.assertIn(
            "denominator = numerator + unknown_count + conflicting_count + excluded_count",
            coverage,
        )
        self.assertIn("互斥且穷尽", coverage)
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
        self.assertIn(
            "gap_count = runtime.unknown_count + runtime.conflicting_count", g5
        )
        self.assertIn("`unknown_count` 与 `conflicting_count` 都为零", g5)

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
