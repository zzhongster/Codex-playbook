# 主张与证据关联记录模板

```yaml
record_id: "REPLACE_WITH_QUALIFIED_CLAIM_ID"
product_version: "REPLACE_WITH_IMMUTABLE_PRODUCT_VERSION"
scope_or_module: "REPLACE_WITH_QUALIFIED_SCOPE_OR_MODULE_ID"
status: "REPLACE_WITH_CLAIM_STATUS"
evidence_references: []
owner: "REPLACE_WITH_NAMED_HUMAN_OWNER"
validation_method: "REPLACE_WITH_CLAIM_VALIDATION_METHOD"
last_updated: "YYYY-MM-DD"
method_maturity: "proposed"
atomic_statement: "REPLACE_WITH_ONE_PRECISE_FALSIFIABLE_PRODUCT_STATEMENT"
confidence: "REPLACE_WITH_LOW_MEDIUM_OR_HIGH"
confidence_rationale: "REPLACE_WITH_BOUNDARY_SPECIFIC_RATIONALE"
supporting_evidence_references: []
contradicting_evidence_references: []
```

方法成熟度只评价取证、建模或验证方法及其证据基础，不评价目标产品事实；产品主张必须另用 `status`、`confidence` 和 `evidence_references`。

一个证据项不等于一条产品主张。支持和反驳证据必须分列，并用类型化链接连接；不要把来源描述、事实陈述、解释和方法成熟度压成一个字段。

## 原子产品主张

- 一条记录只写一个可支持、反驳、限定或取代的精确句子，并固定版本、角色、场景、环境和时间边界。
- 把可见行为、内部实现、业务意图和目标需求拆成不同主张；“未找到”不得写成“不存在”。

## 主张状态与置信度

- `status` 只使用 observed、statically-supported、runtime-confirmed、domain-confirmed、inferred、conflicting、unsupported、deprecated 或 superseded。
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
