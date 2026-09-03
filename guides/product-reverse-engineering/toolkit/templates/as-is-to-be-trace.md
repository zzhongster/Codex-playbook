# As-Is 到 To-Be 追踪模板

```yaml
record_id: "REPLACE_WITH_QUALIFIED_TRANSFORMATION_TRACE_ID"
product_version: "REPLACE_WITH_IMMUTABLE_AS_IS_PRODUCT_VERSION"
scope_or_module: "REPLACE_WITH_QUALIFIED_SCOPE_OR_MODULE_ID"
status: "REPLACE_WITH_RECORD_STATUS"
evidence_references: []
owner: "REPLACE_WITH_NAMED_HUMAN_OWNER"
validation_method: "REPLACE_WITH_BIDIRECTIONAL_TRACE_VALIDATION_METHOD"
last_updated: "YYYY-MM-DD"
atomic_claims:
  - claim_id: "REPLACE_WITH_QUALIFIED_CLAIM_ID"
    statement: "REPLACE_WITH_ONE_PRECISE_TRANSFORMATION_FACT"
    status: "REPLACE_WITH_CLAIM_STATUS"
    confidence: "REPLACE_WITH_LOW_MEDIUM_OR_HIGH"
    evidence_references: []
evidence_method_entries:
  - evidence_id: "REPLACE_WITH_QUALIFIED_EVIDENCE_ID"
    method_id: "REPLACE_WITH_QUALIFIED_METHOD_ID"
    method_maturity: "proposed"
as_is_claim_ids: []
to_be_requirement_ids: []
decision_id: "REPLACE_WITH_QUALIFIED_HUMAN_DECISION_ID"
decision_outcome: "REPLACE_WITH_RETAIN_CORRECT_INTENTIONALLY_DROP_OR_RESEARCH"
```

方法成熟度只评价取证、建模或验证方法及其证据基础，不评价目标产品事实；产品主张必须另用 `status`、`confidence` 和 `evidence_references`。

顶层 `status` 是本记录的生命周期状态；产品事实只写入 `atomic_claims`。`evidence_method_entries[].method_maturity` 只评价对应 `method_id`，不得提升关联主张。

## As-Is 观察

- 引用旧产品行为主张的稳定 ID、版本/角色/场景边界、状态、置信度和原始证据。
- 区分历史行为、疑似缺陷、内部实现与业务意图；缺陷判断不得删除或改写历史观察。

## To-Be 需求

- 为目标需求建立独立稳定 ID、目标用户结果、约束、优先级、适用边界和验收标准。
- To-Be 不继承 As-Is 的 `runtime-confirmed`，也不因旧代码、字段或菜单存在而自动成为需求。

## 保留、纠正、舍弃或研究决定

- 由有权限的产品/领域负责人选择 retain、correct、intentionally-drop 或 research，并给出决定记录 ID。
- 记录用户价值、法规、风险、成本和证据理由；“继续研究”必须有责任人、期限与重开条件。

## 迁移与兼容影响

- 说明数据、身份、状态、历史、进行中业务、集成、报表和操作习惯的转换或兼容影响。
- 记录共存、切换、回退、补偿、不可逆点和旧版本支持窗口，以及每项未知的风险。

## 验收与双向追踪

- 建立 As-Is claim → decision → To-Be requirement → acceptance scenario 的类型化链接，并给每条边状态与证据。
- 从需求可回溯为什么存在，从旧行为可前向查看处置结果；断链、冲突和未决定项不得进入完成分子。
