# 技术资产记录模板

**证据成熟度：`proposed`**

**适用范围：** 用于登记已获授权的软件、配置、制品、数据或部署资产及其身份边界；不替代资产访问授权、来源保管证明或目标产品事实证明。

```yaml
record_id: "REPLACE_WITH_QUALIFIED_ASSET_ID"
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
asset_type: "REPLACE_WITH_ASSET_TYPE"
source_identity: "REPLACE_WITH_SOURCE_ID_AND_CONTENT_HASH"
classification: "REPLACE_WITH_DATA_OR_EXPORT_CLASSIFICATION"
reachability: "REPLACE_WITH_OBSERVED_STATIC_RUNTIME_OR_UNKNOWN_BOUNDARY"
aliases: []
```

方法成熟度只评价取证、建模或验证方法及其证据基础，不评价目标产品事实；产品主张必须在主张—证据记录中使用 `claim_status`、`confidence` 和支持/反驳证据引用。

顶层 `status` 是本记录的生命周期状态；这里只保存 `claim_references`，主张正文、状态、置信度与支持/反驳关系只在主张—证据记录维护。`method_definitions[].method_maturity` 只评价对应方法，映射必须同时解析到本记录的 evidence 与 method ID。

`template.replace-me` 仅演示引用闭合；发布前必须替换为已登记 ID，或同时删除 evidence、method 与映射示例。

## 身份、类型与来源

- 记录规范稳定 ID、显示名、历史别名、资产类型、仓库/制品/配置来源和内容哈希。
- 标明原始、派生或生成属性；派生产物列出输入、工具版本、参数和 `derived-from` 链接。

## 版本、分类与可达性

- 固定产品版本、构建、部署实例、配置基线、有效时间窗和适用访问轨道。
- 区分“文件存在”“静态可达”“已部署”和“运行命中”，并写明数据分类与导出限制。

## 依赖、所有权与退役

- 列出上游依赖、下游消费者、运行责任、维护责任、许可证/权利边界和替代候选。
- 记录活动、替换、撤回或退役计划；旧资产身份保持可寻址并连接替代项。

## 证据边界与验证

- 分列支持与反驳证据、定位、采集时间、完整性校验和当前不可访问来源。
- 写明验证命令或人工复核方法，以及本记录不能证明的业务能力、运行行为和意图。
