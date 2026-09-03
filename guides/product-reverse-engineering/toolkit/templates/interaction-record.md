# 交互记录模板

```yaml
record_id: "REPLACE_WITH_QUALIFIED_INTERACTION_ID"
product_version: "REPLACE_WITH_IMMUTABLE_PRODUCT_VERSION"
scope_or_module: "REPLACE_WITH_QUALIFIED_SCOPE_OR_MODULE_ID"
status: "REPLACE_WITH_RECORD_STATUS"
evidence_references: []
owner: "REPLACE_WITH_NAMED_HUMAN_OWNER"
validation_method: "REPLACE_WITH_REPRODUCIBLE_VALIDATION_METHOD"
last_updated: "YYYY-MM-DD"
atomic_claims:
  - claim_id: "REPLACE_WITH_QUALIFIED_CLAIM_ID"
    statement: "REPLACE_WITH_ONE_PRECISE_INTERACTION_FACT"
    status: "REPLACE_WITH_CLAIM_STATUS"
    confidence: "REPLACE_WITH_LOW_MEDIUM_OR_HIGH"
    evidence_references: []
evidence_method_entries:
  - evidence_id: "REPLACE_WITH_QUALIFIED_EVIDENCE_ID"
    method_id: "REPLACE_WITH_QUALIFIED_METHOD_ID"
    method_maturity: "proposed"
actor_role_id: "REPLACE_WITH_QUALIFIED_ROLE_ID"
entry_surface_id: "REPLACE_WITH_QUALIFIED_SURFACE_ID"
scenario_context_id: "REPLACE_WITH_QUALIFIED_CONTEXT_ID"
```

方法成熟度只评价取证、建模或验证方法及其证据基础，不评价目标产品事实；产品主张必须另用 `status`、`confidence` 和 `evidence_references`。

顶层 `status` 是本记录的生命周期状态；产品事实只写入 `atomic_claims`。`evidence_method_entries[].method_maturity` 只评价对应 `method_id`，不得提升关联主张。

## 入口、角色与前置状态

- 记录入口、到达路径、角色/服务身份、权限范围、前置业务状态、版本和配置。
- 区分页面、命令、API、导入、批任务、通知确认或人工交接，不以控件事件名代替交互。

## 可见与启用规则

- 写明何时可见、隐藏、只读、禁用或允许执行，以及客户端和服务端各自证据。
- 覆盖角色、租户、套餐、数据状态、功能开关和时间边界；界面状态不证明服务端授权。

## 输入、校验与确认

- 列出输入、默认值、编辑顺序、必填/格式/范围/跨字段校验、校验位置和错误反馈。
- 记录确认、取消、二次确认、重复提交与幂等行为，并区分已观察事实与推断。

## 成功、失败与反馈

- 分别记录即时与延迟成功反馈、后置状态、可撤销性和最终可见结果。
- 按输入拒绝、权限拒绝、并发、依赖、超时和未知故障记录错误呈现与禁止副作用。

## 焦点、键盘与批量行为

- 记录初始焦点、Tab 顺序、快捷键、默认按钮、读屏语义、焦点恢复和键盘陷阱。
- 批量操作写明选择、上限、排序、单项/整批原子性、逐项结果、部分成功和继续策略。

## 后置状态与下游副作用

- 列出同步写入、异步消息、缓存、索引、文件、通知、审计和外部调用及其稳定 ID。
- 标明事务边界、等待条件、重试/补偿、责任人和核对方法；用户成功不自动证明下游完成。
