# 业务规则记录模板

```yaml
record_id: "REPLACE_WITH_QUALIFIED_RULE_ID"
product_version: "REPLACE_WITH_IMMUTABLE_PRODUCT_VERSION"
scope_or_module: "REPLACE_WITH_QUALIFIED_SCOPE_OR_MODULE_ID"
status: "REPLACE_WITH_CLAIM_STATUS"
evidence_references: []
owner: "REPLACE_WITH_NAMED_HUMAN_OWNER"
validation_method: "REPLACE_WITH_REPRODUCIBLE_VALIDATION_METHOD"
last_updated: "YYYY-MM-DD"
method_maturity: "proposed"
confidence: "REPLACE_WITH_LOW_MEDIUM_OR_HIGH"
priority: "REPLACE_WITH_RULE_PRIORITY"
conflicting_rule_ids: []
```

方法成熟度只评价取证、建模或验证方法及其证据基础，不评价目标产品事实；产品主张必须另用 `status`、`confidence` 和 `evidence_references`。

## 规则陈述与适用边界

- 用可判定自然语言说明在给定条件下允许、拒绝、计算或触发什么。
- 限定版本、角色、租户、配置、数据域、币种、单位、时间窗、例外和未知项。

## 前置条件与表达式

- 列出必须已成立的状态、权限、数据和并发条件；未知值不能默认视为假。
- 写出表达式、输入/输出、运算顺序、精度、舍入、空值、溢出、阈值和默认分支。

## 决策表与优先级

| 条件组合 | 动作/结果 | 命中策略与优先级 | 证据与状态 |
| --- | --- | --- | --- |
| REPLACE_WITH_CONDITION_SET | REPLACE_WITH_ACTION | REPLACE_WITH_PRIORITY_RULE | REPLACE_WITH_EVIDENCE_AND_STATUS |

补充未观察组合、冲突组合和不可能组合；不得用表格顺序臆测优先级。

## 状态影响与副作用

- 记录源状态、事件、目标状态、守卫、原子性、失败状态以及同步和异步副作用。
- 写明回滚、重试、补偿、审计、不变量和外部系统影响，区分业务意图与历史实现。

## 正例、反例与边界例

- 正例给出输入、中间结果、预期输出和允许副作用；用于证明规则在一个明确边界成立。
- 反例或拒绝例写明不得发生的状态和副作用；边界例覆盖空值、极值、精度与时间边界。

## 冲突、例外与未知

- 分列支持和反驳证据、替代解释、冲突规则 ID、领域确认与运行结果。
- 无法按版本或上下文拆分时保持 `conflicting`；缺证据时使用 `unsupported`，不猜测默认规则。
