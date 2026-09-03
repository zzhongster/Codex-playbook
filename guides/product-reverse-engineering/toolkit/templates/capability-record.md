# 业务能力记录模板

```yaml
record_id: "REPLACE_WITH_QUALIFIED_CAPABILITY_ID"
product_version: "REPLACE_WITH_IMMUTABLE_PRODUCT_VERSION"
scope_or_module: "REPLACE_WITH_QUALIFIED_SCOPE_OR_MODULE_ID"
status: "REPLACE_WITH_CLAIM_STATUS"
evidence_references: []
owner: "REPLACE_WITH_NAMED_HUMAN_OWNER"
validation_method: "REPLACE_WITH_REPRODUCIBLE_VALIDATION_METHOD"
last_updated: "YYYY-MM-DD"
method_maturity: "proposed"
actor_ids: []
outcome: "REPLACE_WITH_BUSINESS_OUTCOME"
surface_ids: []
scenario_ids: []
```

方法成熟度只评价取证、建模或验证方法及其证据基础，不评价目标产品事实；产品主张必须另用 `status`、`confidence` 和 `evidence_references`。

## 参与者与业务结果

- 用“为某参与者实现某结果”陈述能力，给角色和结果各自的稳定 ID。
- 说明触发、业务输入、期望结果、结果的可观察信号，以及不算成功的情况。

## 包含、排除与成功标准

- 写明包含的职责、明确排除、版本/角色/租户/配置边界和允许未知项。
- 将成功标准写成可验证结果、业务容差和终止状态，不使用菜单名或组件名代替能力。

## 场景、规则与依赖

- 连接正常、负向、逆向、重试、部分成功、批量和权限场景，并标出当前覆盖缺口。
- 列出规则、状态机、不变量、依赖能力、人工交接和外部系统；候选关系保持 `inferred`。

## 产品表面与实现追踪

- 用 `exposes` 连接入口、页面、API、报表或任务，用 `implements` 连接有证据的技术资产。
- 每条链接包含版本/上下文、状态和证据；资产存在或同名入口不证明能力可用或等价。
