# 竞品洞察记录模板

```yaml
record_id: "REPLACE_WITH_QUALIFIED_COMPETITOR_INSIGHT_ID"
product_version: "REPLACE_WITH_OBSERVED_COMPETITOR_VERSION_OR_TIME_BOUNDARY"
scope_or_module: "REPLACE_WITH_QUALIFIED_COMPARISON_SCOPE_ID"
status: "REPLACE_WITH_CLAIM_STATUS"
evidence_references: []
owner: "REPLACE_WITH_NAMED_HUMAN_OWNER"
validation_method: "REPLACE_WITH_REPRODUCIBLE_COMPARISON_METHOD"
last_updated: "YYYY-MM-DD"
method_maturity: "proposed"
confidence: "REPLACE_WITH_LOW_MEDIUM_OR_HIGH"
strategic_decision_owner: "REPLACE_WITH_AUTHORIZED_HUMAN_OWNER"
```

方法成熟度只评价取证、建模或验证方法及其证据基础，不评价目标产品事实；产品主张必须另用 `status`、`confidence` 和 `evidence_references`。

## 可比边界

- 固定双方版本、套餐、角色、地区、语言、设备、配置、数据状态、时间和来源访问权。
- 写明比较单位、共同成功标准、不可比项与证据缺口；名称相似不等于能力或价值等价。

## 观察

- 只记录公开或另行获准范围内实际可见的产品表面、步骤、反馈、结果、限制和来源时间。
- 给每条 observation 独立主张 ID、状态和证据，不混入原因、优劣、市场意图或隐藏实现。

## 推断

- 明确从哪些观察经过何种 reasoning 得到解释，限定适用边界，并列出仍缺失的证据。
- inference 使用独立主张 ID 和 `inferred` 状态；语言合理或行业常识不能将其升级为事实。

## 替代解释

- 为每个主要推断列出至少一个可同时解释现象的 alternative explanation。
- 说明哪些新证据能区分解释、哪些来源不可访问，以及证据缺失对结论的影响。

## 置信度

- 使用 low、medium 或 high，并给出来源独立性、样本代表性、版本稳定性和反证覆盖 rationale。
- confidence 评价限定主张，不表示方法 maturity，也不由漂亮界面、功能数量或单次成功决定。

## 战略假设

- 将战略 hypothesis 写成“若差异对特定用户/场景重要，则可观察到何种结果”，并指定人类决策人。
- 分列潜在用户价值、成本、进入壁垒、风险和时效；观察不会自动成为战略判断或产品路线决定。

## 证伪方法

- 写明 falsification method、反例、最小新证据、停止标准和复核时间，优先使用合法可重复的比较。
- 假设被证伪时保留历史记录并新建取代主张；不得为补齐矩阵越过付费、授权或访问控制。
