# 技术资产记录模板

```yaml
record_id: "REPLACE_WITH_QUALIFIED_ASSET_ID"
product_version: "REPLACE_WITH_IMMUTABLE_PRODUCT_VERSION"
scope_or_module: "REPLACE_WITH_QUALIFIED_SCOPE_OR_MODULE_ID"
status: "REPLACE_WITH_CLAIM_STATUS_FOR_RECORDED_ASSET_FACTS"
evidence_references: []
owner: "REPLACE_WITH_NAMED_HUMAN_OWNER"
validation_method: "REPLACE_WITH_REPRODUCIBLE_VALIDATION_METHOD"
last_updated: "YYYY-MM-DD"
method_maturity: "proposed"
asset_type: "REPLACE_WITH_ASSET_TYPE"
source_identity: "REPLACE_WITH_SOURCE_ID_AND_CONTENT_HASH"
classification: "REPLACE_WITH_DATA_OR_EXPORT_CLASSIFICATION"
reachability: "REPLACE_WITH_OBSERVED_STATIC_RUNTIME_OR_UNKNOWN_BOUNDARY"
aliases: []
```

方法成熟度只评价取证、建模或验证方法及其证据基础，不评价目标产品事实；产品主张必须另用 `status`、`confidence` 和 `evidence_references`。

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
