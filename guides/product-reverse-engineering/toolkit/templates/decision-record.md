# 决定记录模板

```yaml
record_id: "REPLACE_WITH_QUALIFIED_DECISION_ID"
product_version: "REPLACE_WITH_IMMUTABLE_PRODUCT_VERSION"
scope_or_module: "REPLACE_WITH_QUALIFIED_SCOPE_OR_MODULE_ID"
status: "REPLACE_WITH_RECORD_STATUS"
evidence_references: []
owner: "REPLACE_WITH_AUTHORIZED_HUMAN_DECISION_OWNER"
validation_method: "REPLACE_WITH_DECISION_INPUT_REVIEW_METHOD"
last_updated: "YYYY-MM-DD"
atomic_claims:
  - claim_id: "REPLACE_WITH_QUALIFIED_CLAIM_ID"
    statement: "REPLACE_WITH_ONE_PRECISE_FACT_USED_BY_THE_DECISION"
    status: "REPLACE_WITH_CLAIM_STATUS"
    confidence: "REPLACE_WITH_LOW_MEDIUM_OR_HIGH"
    evidence_references: []
evidence_method_entries:
  - evidence_id: "REPLACE_WITH_QUALIFIED_EVIDENCE_ID"
    method_id: "REPLACE_WITH_QUALIFIED_METHOD_ID"
    method_maturity: "proposed"
question: "REPLACE_WITH_PRECISE_DECISION_QUESTION"
alternatives: []
chosen_outcome: "REPLACE_WITH_CHOSEN_ALTERNATIVE"
impact: []
supersedes_decision_id: "REPLACE_WITH_PRIOR_DECISION_ID_OR_EXPLICIT_NONE"
```

方法成熟度只评价取证、建模或验证方法及其证据基础，不评价目标产品事实；产品主张必须另用 `status`、`confidence` 和 `evidence_references`。

顶层 `status` 是本记录的生命周期状态；产品事实只写入 `atomic_claims`。`evidence_method_entries[].method_maturity` 只评价对应 `method_id`，不得提升关联主张。

## 待决问题与权限

- 写明必须决定的单一问题、服务的项目目的、决定期限、范围和不决定的后果。
- 指明有权决定的人类 owner、所依据的授权、所需共同签署者；AI Agent 只能起草和校验输入。

## 备选方案

| alternative ID | description | benefits | costs/risks | evidence and unknowns |
| --- | --- | --- | --- | --- |
| REPLACE_WITH_ALTERNATIVE_ID | REPLACE_WITH_DESCRIPTION | REPLACE_WITH_BENEFITS | REPLACE_WITH_COSTS_AND_RISKS | REPLACE_WITH_EVIDENCE_AND_UNKNOWNS |

保留未选方案及其证据，不把未获授权、不可逆或违反硬约束的方案伪装成可选项。

## 选择、理由与影响

- 记录 chosen outcome、选择理由、批准人、适用版本/范围、生效条件和明确未决定内容。
- 分列用户、业务、迁移、兼容、安全、隐私、运行和财务影响，以及缓解、责任人和期限。

## 证据与不确定性

- 引用支持与反驳证据、相关产品主张、风险接受和验证结果；决定不会提高原主张状态或置信度。
- 列出仍存在的未知、冲突、假设和后续验证；超出证据边界的部分明确由谁承担判断责任。

## 取代与重新打开

- 新决定通过 `replaces` 指向旧决定，旧记录保持不可变、可寻址并标明替代项和理由。
- 写明到期、版本/法规/风险/证据变化和失败指标等重开条件；触发后不得静默沿用旧决定。
