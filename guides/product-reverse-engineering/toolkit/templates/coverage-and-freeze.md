# 覆盖与冻结记录模板

```yaml
record_id: "REPLACE_WITH_QUALIFIED_COVERAGE_OR_FREEZE_ID"
product_version: "REPLACE_WITH_IMMUTABLE_PRODUCT_VERSION"
scope_or_module: "REPLACE_WITH_QUALIFIED_SCOPE_OR_MODULE_ID"
status: "draft"
evidence_references:
  - "evidence:template.replace-me"
owner: "REPLACE_WITH_NAMED_HUMAN_OWNER"
validation_method: "REPLACE_WITH_DETERMINISTIC_REBUILD_AND_REVIEW_METHOD"
last_updated: "YYYY-MM-DD"
claim_references: []
method_definitions:
  - method_id: "method:template.replace-me"
    method_maturity: "proposed"
evidence_method_entries:
  - evidence_id: "evidence:template.replace-me"
    method_id: "method:template.replace-me"
denominator_version: "REPLACE_WITH_FROZEN_DENOMINATOR_VERSION"
calculation_rule_version: "REPLACE_WITH_CALCULATION_RULE_VERSION"
input_hashes: []
output_allow_list_and_hashes: []
coverage_dimensions:
  structure:
    denominator: 0
    covered: 0
    unknown: 0
    conflicting: 0
    excluded: 0
    risk_counts: {P0: 0, P1: 0, P2: 0}
  product:
    denominator: 0
    covered: 0
    unknown: 0
    conflicting: 0
    excluded: 0
    risk_counts: {P0: 0, P1: 0, P2: 0}
  semantic:
    denominator: 0
    covered: 0
    unknown: 0
    conflicting: 0
    excluded: 0
    risk_counts: {P0: 0, P1: 0, P2: 0}
  runtime:
    denominator: 0
    covered: 0
    unknown: 0
    conflicting: 0
    excluded: 0
    risk_counts: {P0: 0, P1: 0, P2: 0}
  data:
    denominator: 0
    covered: 0
    unknown: 0
    conflicting: 0
    excluded: 0
    risk_counts: {P0: 0, P1: 0, P2: 0}
  permission:
    denominator: 0
    covered: 0
    unknown: 0
    conflicting: 0
    excluded: 0
    risk_counts: {P0: 0, P1: 0, P2: 0}
  integration:
    denominator: 0
    covered: 0
    unknown: 0
    conflicting: 0
    excluded: 0
    risk_counts: {P0: 0, P1: 0, P2: 0}
  non-functional:
    denominator: 0
    covered: 0
    unknown: 0
    conflicting: 0
    excluded: 0
    risk_counts: {P0: 0, P1: 0, P2: 0}
  trace:
    denominator: 0
    covered: 0
    unknown: 0
    conflicting: 0
    excluded: 0
    risk_counts: {P0: 0, P1: 0, P2: 0}
gates:
  G0:
    gate_record_reference:
      id: "REPLACE_WITH_ART_G0_AUTH_ID"
      sha256: "REPLACE_WITH_SHA256"
    verdict: "pending"
    reviewer: "REPLACE_WITH_REVIEW_OWNER"
    decided_at: null
    evidence_references: []
  G1:
    gate_record_reference:
      id: "REPLACE_WITH_ART_G1_BASELINE_ID"
      sha256: "REPLACE_WITH_SHA256"
    verdict: "pending"
    reviewer: "REPLACE_WITH_REVIEW_OWNER"
    decided_at: null
    evidence_references: []
  G2:
    gate_record_reference:
      id: "REPLACE_WITH_ART_G2_TECHNICAL_ID"
      sha256: "REPLACE_WITH_SHA256"
    verdict: "pending"
    reviewer: "REPLACE_WITH_REVIEW_OWNER"
    decided_at: null
    evidence_references: []
  G3:
    gate_record_reference:
      id: "REPLACE_WITH_ART_G3_PRODUCT_TRACE_ID"
      sha256: "REPLACE_WITH_SHA256"
    verdict: "pending"
    reviewer: "REPLACE_WITH_REVIEW_OWNER"
    decided_at: null
    evidence_references: []
  G4:
    gate_record_reference:
      id: "REPLACE_WITH_ART_G4_SEMANTICS_ID"
      sha256: "REPLACE_WITH_SHA256"
    verdict: "pending"
    reviewer: "REPLACE_WITH_REVIEW_OWNER"
    decided_at: null
    evidence_references: []
  G5:
    gate_record_reference:
      id: "REPLACE_WITH_ART_G5_VALIDATION_ID"
      sha256: "REPLACE_WITH_SHA256"
    verdict: "pending"
    selected_branch: "runtime"
    runtime_confirmation_status: "required"
    static_non_runtime_coverage:
      gap_artifact_reference: null
      gap_count: 0
    reviewer: "REPLACE_WITH_REVIEW_OWNER"
    decided_at: null
    evidence_references: []
  G6:
    gate_record_reference:
      id: "REPLACE_WITH_ART_G6_AUDIT_ID"
      sha256: "REPLACE_WITH_SHA256"
    verdict: "pending"
    reviewer: "REPLACE_WITH_REVIEW_OWNER"
    decided_at: null
    evidence_references: []
  G7:
    gate_record_reference:
      id: "REPLACE_WITH_ART_G7_RELEASE_ID"
      sha256: "REPLACE_WITH_SHA256"
    verdict: "pending"
    reviewer: "REPLACE_WITH_REVIEW_OWNER"
    decided_at: null
    evidence_references: []
```

方法成熟度只评价取证、建模或验证方法及其证据基础，不评价目标产品事实；产品主张必须在主张—证据记录中使用 `claim_status`、`confidence` 和支持/反驳证据引用。

顶层 `status` 是本记录的生命周期状态；这里只保存 `claim_references`，覆盖与冻结事实真值只在主张—证据记录维护。`method_definitions[].method_maturity` 只评价对应方法，映射必须同时解析到本记录的 evidence 与 method ID。

`template.replace-me` 仅演示引用闭合；发布前必须替换为已登记 ID，或同时删除 evidence、method 与映射示例。

## 冻结分母与计算规则

- 先冻结分母，再计算分子；保存叶子稳定 ID、父子结构、包含/排除、风险级别、目标证据状态和规则版本。
- 分子只计边界完整、状态达标且证据可追踪的项；合法范围变化生成新分母版本并保留前后结果。

## 九类覆盖与风险队列

| dimension | denominator | covered | unknown | conflicting | excluded | P0/P1/P2 |
| --- | --- | --- | --- | --- | --- | --- |
| structure | REPLACE_WITH_DENOMINATOR | REPLACE_WITH_COVERED | REPLACE_WITH_UNKNOWN | REPLACE_WITH_CONFLICTS | REPLACE_WITH_EXCLUSIONS | REPLACE_WITH_P0_P1_P2_COUNTS |
| product | REPLACE_WITH_DENOMINATOR | REPLACE_WITH_COVERED | REPLACE_WITH_UNKNOWN | REPLACE_WITH_CONFLICTS | REPLACE_WITH_EXCLUSIONS | REPLACE_WITH_P0_P1_P2_COUNTS |
| semantic | REPLACE_WITH_DENOMINATOR | REPLACE_WITH_COVERED | REPLACE_WITH_UNKNOWN | REPLACE_WITH_CONFLICTS | REPLACE_WITH_EXCLUSIONS | REPLACE_WITH_P0_P1_P2_COUNTS |
| runtime | REPLACE_WITH_DENOMINATOR | REPLACE_WITH_COVERED | REPLACE_WITH_UNKNOWN | REPLACE_WITH_CONFLICTS | REPLACE_WITH_EXCLUSIONS | REPLACE_WITH_P0_P1_P2_COUNTS |
| data | REPLACE_WITH_DENOMINATOR | REPLACE_WITH_COVERED | REPLACE_WITH_UNKNOWN | REPLACE_WITH_CONFLICTS | REPLACE_WITH_EXCLUSIONS | REPLACE_WITH_P0_P1_P2_COUNTS |
| permission | REPLACE_WITH_DENOMINATOR | REPLACE_WITH_COVERED | REPLACE_WITH_UNKNOWN | REPLACE_WITH_CONFLICTS | REPLACE_WITH_EXCLUSIONS | REPLACE_WITH_P0_P1_P2_COUNTS |
| integration | REPLACE_WITH_DENOMINATOR | REPLACE_WITH_COVERED | REPLACE_WITH_UNKNOWN | REPLACE_WITH_CONFLICTS | REPLACE_WITH_EXCLUSIONS | REPLACE_WITH_P0_P1_P2_COUNTS |
| non-functional | REPLACE_WITH_DENOMINATOR | REPLACE_WITH_COVERED | REPLACE_WITH_UNKNOWN | REPLACE_WITH_CONFLICTS | REPLACE_WITH_EXCLUSIONS | REPLACE_WITH_P0_P1_P2_COUNTS |
| trace | REPLACE_WITH_DENOMINATOR | REPLACE_WITH_COVERED | REPLACE_WITH_UNKNOWN | REPLACE_WITH_CONFLICTS | REPLACE_WITH_EXCLUSIONS | REPLACE_WITH_P0_P1_P2_COUNTS |

九类维度分别计算，不把不同单位直接相加；未知队列记录影响、下一动作、责任人、期限和重开条件。

## G0–G7 门禁

| gate | verdict | input artifact IDs/hashes | reason codes | human decision artifact IDs/hashes |
| --- | --- | --- | --- | --- |
| G0–G4, G6–G7 | pending / pass / fail / not-applicable | REPLACE_WITH_INPUTS | REPLACE_WITH_DERIVED_REASONS | REPLACE_WITH_IMMUTABLE_DECISION_INPUTS |
| G5 | pending / pass / fail | REPLACE_WITH_P5_INPUTS | REPLACE_WITH_G5_DERIVED_REASONS | REPLACE_WITH_STATIC_BRANCH_ACCEPTANCE_IF_USED |

未来但适用的门禁保持 `pending`；只有已评估否定用 `fail`，`not-applicable` 必须有具名人类批准。G5 只允许 `pending`、`pass` 或 `fail`，绝不使用 `not-applicable`；获批非运行分支仍必须对 G5 作通过或失败判定。

G5 的合法组合是封闭集合：运行分支开始或失败时为 `runtime + pending/fail + required`，获得完整运行确认时才是 `runtime + pass + confirmed`；获批静态分支只能是 `approved-static + pass/fail + unavailable-with-approved-static-ceiling`。静态分支必须在 `static_non_runtime_coverage` 持续引用 `ART-P5-RUNTIME-GAP` 的稳定 ID/哈希，并保留至少一个未获运行确认的 gap count；不能以 G5 通过清零或隐藏运行覆盖缺口。运行分支则保持 gap reference 为 `null`、gap count 为 `0`。

每个 `reviewer` 与 `decided_at` 是覆盖汇总中的评审投影，并与对应证据引用一起指向人工决定；它们不写入确定性 `ART-G*` 派生门禁记录的内容身份，派生记录只由规则版本和不可变输入计算。

## 产物生命周期

- 产物与摘要只使用 `active`、`replaced`、`withdrawn`，独立于产品主张状态和 `superseded`。
- 替换关系成对保存 `replaces` / `replaced-by`、哈希、理由、批准和生效范围；旧对象保持可寻址。

## 无环冻结与复核

1. `content outputs`：生成并哈希内容输出，排除摘要和冻结证明。
2. `child/phase summaries`：自叶向根生成，只引用既存内容与子摘要哈希。
3. `root summary`：汇总声明输入、输出、门禁和风险，不写入自身哈希。
4. `detached freeze manifest/attestation`：最后哈希根摘要和声明输出，并由外部锚验证。

任何层都不得递归包含自身哈希。复核从外部锚反向验证清单、根摘要、子摘要和内容输出，并从空目录重建输出。
