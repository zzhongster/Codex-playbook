# 主张与证据关联记录模板

**证据成熟度：`proposed`**

**适用范围：** 用于登记原子化产品主张、主张状态、置信度及支持或反驳证据；不替代取证授权或事实证明，页面的方法成熟度也不写入产品主张。

```yaml
record_id: "REPLACE_WITH_QUALIFIED_CLAIM_EVIDENCE_ASSOCIATION_ID"
product_version: "REPLACE_WITH_IMMUTABLE_PRODUCT_VERSION"
scope_or_module: "REPLACE_WITH_QUALIFIED_SCOPE_OR_MODULE_ID"
status: "draft"
evidence_references:
  - "evidence:template.replace-me"
owner: "REPLACE_WITH_NAMED_HUMAN_OWNER"
validation_method: "REPLACE_WITH_CLAIM_VALIDATION_METHOD"
last_updated: "YYYY-MM-DD"
claim_id: "claim:template.replace-me"
claim_statement: "REPLACE_WITH_ONE_PRECISE_FALSIFIABLE_PRODUCT_STATEMENT"
claim_status: "inferred"
confidence: "low"
confidence_rationale: "REPLACE_WITH_BOUNDARY_SPECIFIC_RATIONALE"
supporting_evidence_references:
  - "evidence:template.replace-me"
contradicting_evidence_references: []
method_definitions:
  - method_id: "method:template.replace-me"
    method_maturity: "proposed"
evidence_method_entries:
  - evidence_id: "evidence:template.replace-me"
    method_id: "method:template.replace-me"
```

顶层 `status` 是主张—证据关联记录的生命周期状态；产品事实使用独立的 `claim_id`、`claim_status`、`confidence` 与支持/反驳证据引用。`method_definitions[].method_maturity` 只评价对应方法；evidence—method 映射必须同时解析到本记录声明的 ID，且不评价整条产品主张。

`template.replace-me` 仅演示引用闭合；发布前必须替换 claim、evidence 与 method ID，或删除相应关联，不能把示例命名空间当作项目证据发布。

一个证据项不等于一条产品主张。支持和反驳证据必须分列，并用类型化链接连接；不要把来源描述、事实陈述、解释和方法成熟度压成一个字段。

## 原子产品主张

- 一条记录只写一个可支持、反驳、限定或取代的精确句子，并固定版本、角色、场景、环境和时间边界。
- 把可见行为、内部实现、业务意图和目标需求拆成不同主张；“未找到”不得写成“不存在”。

## 主张状态与置信度

- `claim_status` 只使用 observed、statically-supported、runtime-confirmed、domain-confirmed、inferred、conflicting、unsupported、deprecated 或 superseded。
- `confidence` 独立使用 low、medium 或 high，并说明来源独立性、版本稳定性、反证覆盖与限制。

## 支持与反驳证据

| relation | evidence ID | applicable version/context | source location/hash | relevance |
| --- | --- | --- | --- | --- |
| supports | REPLACE_WITH_EVIDENCE_ID | REPLACE_WITH_CONTEXT | REPLACE_WITH_CONTROLLED_REFERENCE | REPLACE_WITH_RELEVANCE |
| contradicts | REPLACE_WITH_EVIDENCE_ID | REPLACE_WITH_CONTEXT | REPLACE_WITH_CONTROLLED_REFERENCE | REPLACE_WITH_RELEVANCE |

证据引用必须解析到唯一登记项；不适用行应删除，不能保留看似真实却不可解析的占位 ID。

## 证据项与方法成熟度

- 每个证据项另记 kind、来源身份、采集方法、时间、完整性、脱敏、可用性和支持/反驳关系。
- 每份证据引用产生它的方法及其 method maturity；同一主张可引用成熟度不同的方法，但没有整体产品事实 maturity。

## 状态历史、冲突与取代

- 状态变化追加旧状态、新状态、触发证据、评审人和时间；不得覆写历史或删除少数证据。
- 冲突不能消解时保持 `conflicting`；新主张取代旧主张时使用 `replaces`，旧主张保留 `superseded` 和反向链接。
