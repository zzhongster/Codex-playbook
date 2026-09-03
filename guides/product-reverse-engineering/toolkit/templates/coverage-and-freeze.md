# 覆盖与冻结记录模板

```yaml
record_id: "REPLACE_WITH_QUALIFIED_COVERAGE_OR_FREEZE_ID"
product_version: "REPLACE_WITH_IMMUTABLE_PRODUCT_VERSION"
scope_or_module: "REPLACE_WITH_QUALIFIED_SCOPE_OR_MODULE_ID"
status: "REPLACE_WITH_RECORD_STATUS"
evidence_references: []
owner: "REPLACE_WITH_NAMED_HUMAN_OWNER"
validation_method: "REPLACE_WITH_DETERMINISTIC_REBUILD_AND_REVIEW_METHOD"
last_updated: "YYYY-MM-DD"
atomic_claims:
  - claim_id: "REPLACE_WITH_QUALIFIED_CLAIM_ID"
    statement: "REPLACE_WITH_ONE_PRECISE_COVERAGE_OR_FREEZE_FACT"
    status: "REPLACE_WITH_CLAIM_STATUS"
    confidence: "REPLACE_WITH_LOW_MEDIUM_OR_HIGH"
    evidence_references: []
evidence_method_entries:
  - evidence_id: "REPLACE_WITH_QUALIFIED_EVIDENCE_ID"
    method_id: "REPLACE_WITH_QUALIFIED_METHOD_ID"
    method_maturity: "proposed"
denominator_version: "REPLACE_WITH_FROZEN_DENOMINATOR_VERSION"
calculation_rule_version: "REPLACE_WITH_CALCULATION_RULE_VERSION"
gate_record_references: []
input_hashes: []
output_allow_list_and_hashes: []
```

方法成熟度只评价取证、建模或验证方法及其证据基础，不评价目标产品事实；产品主张必须另用 `status`、`confidence` 和 `evidence_references`。

顶层 `status` 是本记录的生命周期状态；产品事实只写入 `atomic_claims`。`evidence_method_entries[].method_maturity` 只评价对应 `method_id`，不得提升关联主张。

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
| G0–G7 | pending / pass / fail / not-applicable | REPLACE_WITH_INPUTS | REPLACE_WITH_DERIVED_REASONS | REPLACE_WITH_IMMUTABLE_DECISION_INPUTS |

未来但适用的门禁保持 `pending`；只有已评估否定用 `fail`，`not-applicable` 必须有具名人类批准。

## 产物生命周期

- 产物与摘要只使用 `active`、`replaced`、`withdrawn`，独立于产品主张状态和 `superseded`。
- 替换关系成对保存 `replaces` / `replaced-by`、哈希、理由、批准和生效范围；旧对象保持可寻址。

## 无环冻结与复核

1. `content outputs`：生成并哈希内容输出，排除摘要和冻结证明。
2. `child/phase summaries`：自叶向根生成，只引用既存内容与子摘要哈希。
3. `root summary`：汇总声明输入、输出、门禁和风险，不写入自身哈希。
4. `detached freeze manifest/attestation`：最后哈希根摘要和声明输出，并由外部锚验证。

任何层都不得递归包含自身哈希。复核从外部锚反向验证清单、根摘要、子摘要和内容输出，并从空目录重建输出。
