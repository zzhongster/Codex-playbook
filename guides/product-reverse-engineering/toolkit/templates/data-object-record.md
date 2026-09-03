# 数据对象记录模板

```yaml
record_id: "REPLACE_WITH_QUALIFIED_DATA_OBJECT_ID"
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
business_identity: "REPLACE_WITH_IDENTITY_SCOPE_AND_ALLOCATION_RULE"
technical_aliases: []
classification: "REPLACE_WITH_DATA_CLASSIFICATION"
```

方法成熟度只评价取证、建模或验证方法及其证据基础，不评价目标产品事实；产品主张必须在主张—证据记录中使用 `claim_status`、`confidence` 和支持/反驳证据引用。

顶层 `status` 是本记录的生命周期状态；这里只保存 `claim_references`，主张正文、状态、置信度与支持/反驳关系只在主张—证据记录维护。`method_definitions[].method_maturity` 只评价对应方法，映射必须同时解析到本记录的 evidence 与 method ID。

`template.replace-me` 仅演示引用闭合；发布前必须替换为已登记 ID，或同时删除 evidence、method 与映射示例。

## 业务身份与技术别名

- 定义对象的业务含义、稳定 ID、身份分配者、唯一范围、自然键、外部 ID 和版本关系。
- 表、字段、类、事件或文件名只登记为带来源和有效期的技术别名，不自动等同业务身份。

## 字段语义

| field ID | meaning | type | precision | unit | null | default | special values | evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| REPLACE_WITH_FIELD_ID | REPLACE_WITH_MEANING | REPLACE_WITH_TYPE | REPLACE_WITH_PRECISION | REPLACE_WITH_UNIT | REPLACE_WITH_NULL_RULE | REPLACE_WITH_DEFAULT | REPLACE_WITH_SPECIAL_VALUES | REPLACE_WITH_EVIDENCE_REFS |

逐字段补充枚举、币种、时区、方向、舍入、编码和未知值；存储类型不能单独证明业务语义。

## 生命周期与历史

- 记录创建、修改、状态转换、合并/拆分、归档、停用、作废、删除、匿名化和恢复。
- 区分快照、事件、当前值、有效时间与记录时间，并说明旧规则下历史是否重算。

## 读者、写者与派生者

| relation | qualified object ID | version/context | transaction or async boundary | evidence |
| --- | --- | --- | --- | --- |
| readers | REPLACE_WITH_READER_ID | REPLACE_WITH_CONTEXT | REPLACE_WITH_BOUNDARY | REPLACE_WITH_EVIDENCE_REFS |
| writers | REPLACE_WITH_WRITER_ID | REPLACE_WITH_CONTEXT | REPLACE_WITH_BOUNDARY | REPLACE_WITH_EVIDENCE_REFS |
| derived-from | REPLACE_WITH_SOURCE_ID | REPLACE_WITH_CONTEXT | REPLACE_WITH_DERIVATION | REPLACE_WITH_EVIDENCE_REFS |

对每条读写边记录状态和反证；静态调用候选不得冒充运行时数据流。

## 所有权、保留与删除

- 记录业务 ownership、技术托管、数据质量、主来源、修复责任、保留期限和法定限制。
- 核对数据库、缓存、搜索、附件、消息、备份与下游副本；删除按钮不证明所有副本已清除。
