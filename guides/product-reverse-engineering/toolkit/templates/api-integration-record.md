# API 与集成记录模板

**证据成熟度：`proposed`**

**适用范围：** 用于登记已获授权范围内的 API、RPC、消息或文件集成及其边界；不替代访问授权、协议所有者确认或目标产品事实证明。

```yaml
record_id: "REPLACE_WITH_QUALIFIED_INTEGRATION_ID"
product_version: "REPLACE_WITH_IMMUTABLE_PRODUCT_VERSION"
scope_or_module: "REPLACE_WITH_QUALIFIED_SCOPE_OR_MODULE_ID"
status: "draft"
evidence_references:
  - "evidence:template.replace-me"
owner: "REPLACE_WITH_NAMED_HUMAN_OWNER"
validation_method: "REPLACE_WITH_REPRODUCIBLE_VALIDATION_METHOD"
last_updated: "YYYY-MM-DD"
claim_references: []
method_definitions:
  - method_id: "method:template.replace-me"
    method_maturity: "proposed"
evidence_method_entries:
  - evidence_id: "evidence:template.replace-me"
    method_id: "method:template.replace-me"
consumer_ids: []
provider_ids: []
protocol: "REPLACE_WITH_PROTOCOL_OR_EXCHANGE_TYPE"
contract_version: "REPLACE_WITH_CONTRACT_VERSION"
```

方法成熟度只评价取证、建模或验证方法及其证据基础，不评价目标产品事实；产品主张必须在主张—证据记录中使用 `claim_status`、`confidence` 和支持/反驳证据引用。

顶层 `status` 是本记录的生命周期状态；这里只保存 `claim_references`，主张正文、状态、置信度与支持/反驳关系只在主张—证据记录维护。`method_definitions[].method_maturity` 只评价对应方法，映射必须同时解析到本记录的 evidence 与 method ID。

`template.replace-me` 仅演示引用闭合；发布前必须替换为已登记 ID，或同时删除 evidence、method 与映射示例。

## 消费者、提供者与契约

- 为 consumer、provider、网关、人工交接和端点/主题/文件交换分配不同稳定 ID，并固定方向与责任边界。
- 记录协议、契约版本、触发方式、请求/响应或消息 schema、兼容策略、内容类型、顺序和大小限制。

## 认证与授权事实

- 记录实际使用的身份类型、凭据受控引用、令牌/证书范围、租户上下文、授权决策点和审计归属。
- 分离文档声明、配置候选、客户端行为和服务端允许/拒绝结果；不可见入口不证明服务端拒绝。

## 幂等、分页与错误

- 写明幂等键来源、唯一范围、去重窗口、重复响应和重复副作用；没有证据时保持未知。
- 记录分页模型、游标稳定性、排序、上限、空页、并发变化，以及协议错误、业务错误和部分成功。

## 重试、超时与一致性

- 记录调用方和提供方的 timeout、retry、退避、抖动、最大次数、熔断、死信与人工恢复责任。
- 标明事务提交点、至少/至多/恰好一次候选语义、最终一致性窗口、补偿和最终核对方法。

## Webhook 与事件语义

- 记录 webhook/event 的生产者、消费者、事件身份、版本、分区/顺序、投递、确认、重放和签名验证。
- 区分发生时间、发送时间和处理时间；保存首错、重复、乱序、迟到、毒消息及残留处理证据。
