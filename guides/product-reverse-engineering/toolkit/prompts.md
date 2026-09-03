# AI Agent 可复制任务包

**证据成熟度：`proposed`**

**适用范围：** 用于把已批准、边界明确的逆向子任务交给 AI Agent；这些任务包只允许分析已列输入和起草候选记录，不授予 Agent 批准门禁、改变授权、接受风险或执行未批准运行实验的权力。

复制后必须在分派前替换所有 `<fill-before-dispatch>` 值，并重新计算输入哈希；仍含占位值的任务包无效。路径以[项目证据仓布局](project-layout.md)中的工作区身份为根，字段语义遵循[人机协作](../core/human-agent-collaboration.md)。Agent 必须保留未知、逐条主张引用证据、报告不可到达输入，并严格区分 `not-found`（在声明搜索边界内未找到）与 `does-not-exist`（有足以排除替代位置的证据）；前者不得自动升级为后者。

## inventory

用途：在冻结输入内生成资产候选目录和未到达清单，不解释运行行为。

```yaml
packet_type: inventory
objective: "枚举冻结范围内的产品与技术资产，为 Phase 3 图谱提供可复核候选，不声称未找到资产不存在。"
authorization_identity:
  record_id: "decision:phase0.authorization"
  record_hash: "sha256:<fill-before-dispatch>"
  gate_record_id: "gate:phase0.g0-authorization"
  gate_record_hash: "sha256:<fill-before-dispatch>"
workspace_identity:
  workspace_root_id: "workspace:target.reverse-engineering"
  repository_commit: "<fill-before-dispatch>"
  product_version: "<fill-before-dispatch>"
  source_fingerprint: "sha256:<fill-before-dispatch>"
  artifact_fingerprint: "sha256:<fill-before-dispatch>"
  environment_identity: "environment:static.authorized-snapshot"
exact_inputs:
  - input_id: "artifact:phase1.baseline"
    relative_path: "knowledge/records/artifact/phase1.baseline.json"
    sha256: "sha256:<fill-before-dispatch>"
    availability: required
  - input_id: "artifact:phase1.denominator"
    relative_path: "knowledge/coverage/phase1.denominator.json"
    sha256: "sha256:<fill-before-dispatch>"
    availability: required
scope_denominator:
  - "只处理 ART-P1-DENOM 中标为 in-scope 的稳定 ID；逐项回报 covered、not-found、unreachable 或 excluded。"
allowed_evidence:
  - "只读冻结源码、制品清单、配置清单和已脱敏索引；不得打开未列目录或外部系统。"
forbidden_inference:
  - "不得从文件名、依赖存在、静态可达或框架惯例推断功能已部署、已启用或已运行。"
  - "不得把 not-found 改写为 does-not-exist。"
output_records:
  - record_type: asset
    schema: "guides/product-reverse-engineering/toolkit/schemas/asset.schema.json"
    relative_path: "knowledge/records/asset/inventory.candidates.json"
  - record_type: coverage-summary
    schema: "guides/product-reverse-engineering/toolkit/schemas/coverage-summary.schema.json"
    relative_path: "knowledge/coverage/inventory.summary.json"
validation_command: "python3 tools/validate_product_reverse_engineering_guide.py"
stop_conditions:
  - condition: authorization-drift
    action: "stop-and-request-new-authorization"
  - condition: workspace-identity-mismatch
    action: "stop-and-report-identity-mismatch"
  - condition: required-input-unreachable
    action: "stop-and-report-unreachable-input"
  - condition: unsafe-or-unapproved-runtime
    action: "stop-and-escalate-to-safety-owner"
human_review_owner: "逆向负责人"
agent_rules:
  preserve_unknowns: true
  cite_each_claim: true
  report_unreachable_inputs: true
  absence_terms:
    - not-found
    - does-not-exist
  may_approve_gate: false
  may_change_authorization: false
  may_run_unapproved_runtime: false
```

执行输出还应列出实际搜索的相对路径、查询、工具版本、访问失败和分母计数。发现分母外资产只登记为候选并交给评审人，不自行扩张范围。

## vertical-trace

用途：连接一个批准切片的入口、实现、数据/消息与可见结果，显式留下断点和替代解释。

```yaml
packet_type: vertical-trace
objective: "为选定切片建立逐边可审计的纵向追踪图；只把有对应证据的边写为已支持。"
authorization_identity:
  record_id: "decision:phase0.authorization"
  record_hash: "sha256:<fill-before-dispatch>"
  gate_record_id: "gate:phase0.g0-authorization"
  gate_record_hash: "sha256:<fill-before-dispatch>"
workspace_identity:
  workspace_root_id: "workspace:target.reverse-engineering"
  repository_commit: "<fill-before-dispatch>"
  product_version: "<fill-before-dispatch>"
  source_fingerprint: "sha256:<fill-before-dispatch>"
  artifact_fingerprint: "sha256:<fill-before-dispatch>"
  environment_identity: "environment:trace.authorized-snapshot"
exact_inputs:
  - input_id: "artifact:phase4.selected-slice"
    relative_path: "knowledge/records/artifact/phase4.selected-slice.json"
    sha256: "sha256:<fill-before-dispatch>"
    availability: required
  - input_id: "artifact:phase3.asset-atlas"
    relative_path: "knowledge/records/artifact/phase3.asset-atlas.json"
    sha256: "sha256:<fill-before-dispatch>"
    availability: required
scope_denominator:
  - "仅覆盖切片记录列出的入口、角色、前置状态、成功/失败路径和必达层；每个节点状态单独计数。"
allowed_evidence:
  - "使用已授权源码、制品、配置、脱敏日志/trace、数据库或消息索引中与该切片 ID 关联的证据项。"
forbidden_inference:
  - "不得用调用可达性替代实际执行，不得把 UI 行为推断成隐藏服务端实现。"
  - "断链保持 unknown 或 unsupported，不得用框架常识自动补边。"
output_records:
  - record_type: trace-link
    schema: "guides/product-reverse-engineering/toolkit/schemas/trace-link.schema.json"
    relative_path: "knowledge/records/trace-link/selected-slice.links.json"
  - record_type: claim
    schema: "guides/product-reverse-engineering/toolkit/schemas/claim.schema.json"
    relative_path: "knowledge/records/claim/selected-slice.claims.json"
validation_command: "python3 tools/validate_product_reverse_engineering_guide.py"
stop_conditions:
  - condition: authorization-drift
    action: "stop-and-request-new-authorization"
  - condition: workspace-identity-mismatch
    action: "stop-and-report-identity-mismatch"
  - condition: required-input-unreachable
    action: "stop-and-report-unreachable-input"
  - condition: unsafe-or-unapproved-runtime
    action: "stop-and-escalate-to-safety-owner"
human_review_owner: "技术分析负责人"
agent_rules:
  preserve_unknowns: true
  cite_each_claim: true
  report_unreachable_inputs: true
  absence_terms:
    - not-found
    - does-not-exist
  may_approve_gate: false
  may_change_authorization: false
  may_run_unapproved_runtime: false
```

输出必须逐边给出 source、target、relation、上下文和 evidence ID。候选边与已支持边分开；找不到消费者时报告已搜索的 topic、group、配置和版本，而非宣称没有消费者。

## runtime-experiment-review

用途：复核已执行实验的协议绑定、首错、结果、副作用和清理；本任务不执行或重放实验。

```yaml
packet_type: runtime-experiment-review
objective: "审计现有 ART-P5-PROTOCOL、RESULT 与 EFFECTS 是否同一身份、忠实记录实际结果并满足安全和复现契约。"
authorization_identity:
  record_id: "decision:phase0.authorization"
  record_hash: "sha256:<fill-before-dispatch>"
  gate_record_id: "gate:phase0.g0-authorization"
  gate_record_hash: "sha256:<fill-before-dispatch>"
workspace_identity:
  workspace_root_id: "workspace:target.reverse-engineering"
  repository_commit: "<fill-before-dispatch>"
  product_version: "<fill-before-dispatch>"
  source_fingerprint: "sha256:<fill-before-dispatch>"
  artifact_fingerprint: "sha256:<fill-before-dispatch>"
  environment_identity: "environment:runtime.authorized-clone"
exact_inputs:
  - input_id: "experiment:phase5.protocol"
    relative_path: "knowledge/runtime/protocols/phase5.protocol.json"
    sha256: "sha256:<fill-before-dispatch>"
    availability: required
  - input_id: "experiment:phase5.result"
    relative_path: "knowledge/runtime/results/phase5.result.json"
    sha256: "sha256:<fill-before-dispatch>"
    availability: required
  - input_id: "experiment:phase5.effects"
    relative_path: "knowledge/runtime/effects/phase5.effects.json"
    sha256: "sha256:<fill-before-dispatch>"
    availability: required
scope_denominator:
  - "逐个协议步骤、预期观察面、实际 run、首错、副作用、清理步骤、残留检查和目标主张计数。"
allowed_evidence:
  - "只读冻结协议、已有运行结果、效应记录及其脱敏证据索引；禁止发起新的请求、查询、写入或重放。"
forbidden_inference:
  - "不得把计划步骤当作已执行，不得用成功重试覆盖首错，不得从清理命令存在推断清理成功。"
  - "不得把一次运行或不同环境的结果泛化到未测版本、角色和状态。"
output_records:
  - record_type: experiment
    schema: "guides/product-reverse-engineering/toolkit/schemas/experiment.schema.json"
    relative_path: "knowledge/records/experiment/phase5.review.json"
  - record_type: claim
    schema: "guides/product-reverse-engineering/toolkit/schemas/claim.schema.json"
    relative_path: "knowledge/records/claim/phase5.review-claims.json"
validation_command: "python3 tools/validate_product_reverse_engineering_guide.py"
stop_conditions:
  - condition: authorization-drift
    action: "stop-and-request-new-authorization"
  - condition: workspace-identity-mismatch
    action: "stop-and-report-identity-mismatch"
  - condition: required-input-unreachable
    action: "stop-and-report-unreachable-input"
  - condition: unsafe-or-unapproved-runtime
    action: "stop-and-escalate-to-safety-owner"
human_review_owner: "QA/实验负责人"
agent_rules:
  preserve_unknowns: true
  cite_each_claim: true
  report_unreachable_inputs: true
  absence_terms:
    - not-found
    - does-not-exist
  may_approve_gate: false
  may_change_authorization: false
  may_run_unapproved_runtime: false
```

Agent 只能报告 G5 输入是否满足规则，不能把报告写成 `pass` 批准。协议与结果身份不一致、首错丢失、未清理效应或原始证据不可到达时立即停止审计结论并交给评审人。

## conflict-audit

用途：找出同一边界内互相支持、反驳或版本错配的主张，保留竞争解释并准备人类裁决材料。

```yaml
packet_type: conflict-audit
objective: "审计 P0/P1 与抽样 P2 主张的证据冲突、版本混用和边界混用，生成不替代人工决定的冲突候选。"
authorization_identity:
  record_id: "decision:phase0.authorization"
  record_hash: "sha256:<fill-before-dispatch>"
  gate_record_id: "gate:phase0.g0-authorization"
  gate_record_hash: "sha256:<fill-before-dispatch>"
workspace_identity:
  workspace_root_id: "workspace:target.reverse-engineering"
  repository_commit: "<fill-before-dispatch>"
  product_version: "<fill-before-dispatch>"
  source_fingerprint: "sha256:<fill-before-dispatch>"
  artifact_fingerprint: "sha256:<fill-before-dispatch>"
  environment_identity: "environment:audit.frozen-records"
exact_inputs:
  - input_id: "artifact:phase7.claim-set"
    relative_path: "knowledge/records/claim/phase7.scope.json"
    sha256: "sha256:<fill-before-dispatch>"
    availability: required
  - input_id: "artifact:phase7.evidence-index"
    relative_path: "knowledge/evidence/indexes/phase7.scope.json"
    sha256: "sha256:<fill-before-dispatch>"
    availability: required
scope_denominator:
  - "全部 P0/P1 主张和分母明确指定的 P2 样本；按 claim ID、版本、角色、环境和时间窗分别计数。"
allowed_evidence:
  - "只读主张、证据、trace link、决定和覆盖记录；允许按内容哈希核对 Git 外证据是否可由保管人访问。"
forbidden_inference:
  - "不得按票数、时间新旧或来源权威感自动选择赢家，不得删除少数证据。"
  - "不得把不同版本、角色或环境的差异压成一个冲突，也不得自行接受风险。"
output_records:
  - record_type: claim
    schema: "guides/product-reverse-engineering/toolkit/schemas/claim.schema.json"
    relative_path: "knowledge/records/claim/phase7.conflicting.json"
  - record_type: coverage-summary
    schema: "guides/product-reverse-engineering/toolkit/schemas/coverage-summary.schema.json"
    relative_path: "knowledge/coverage/phase7.conflict-audit.json"
validation_command: "python3 tools/validate_product_reverse_engineering_guide.py"
stop_conditions:
  - condition: authorization-drift
    action: "stop-and-request-new-authorization"
  - condition: workspace-identity-mismatch
    action: "stop-and-report-identity-mismatch"
  - condition: required-input-unreachable
    action: "stop-and-report-unreachable-input"
  - condition: unsafe-or-unapproved-runtime
    action: "stop-and-escalate-to-safety-owner"
human_review_owner: "逆向负责人和相应领域负责人"
agent_rules:
  preserve_unknowns: true
  cite_each_claim: true
  report_unreachable_inputs: true
  absence_terms:
    - not-found
    - does-not-exist
  may_approve_gate: false
  may_change_authorization: false
  may_run_unapproved_runtime: false
```

审计输出只在 claim/coverage 记录中列出“需要谁决定什么”，不得写入 `knowledge/decisions/`。有权限的人类复核后另建决定记录；Agent 不能模仿签名、选择最终结果或生成风险接受。

## freeze-audit

用途：在发布前核对分母、门禁输入、批准、确定性生成和分离式冻结顺序，不创建批准。

```yaml
packet_type: freeze-audit
objective: "验证声明输出是否由固定权威输入无环、确定性重建，所有阻断项和人工批准是否真实可寻址。"
authorization_identity:
  record_id: "decision:phase0.authorization"
  record_hash: "sha256:<fill-before-dispatch>"
  gate_record_id: "gate:phase0.g0-authorization"
  gate_record_hash: "sha256:<fill-before-dispatch>"
workspace_identity:
  workspace_root_id: "workspace:target.reverse-engineering"
  repository_commit: "<fill-before-dispatch>"
  product_version: "<fill-before-dispatch>"
  source_fingerprint: "sha256:<fill-before-dispatch>"
  artifact_fingerprint: "sha256:<fill-before-dispatch>"
  environment_identity: "environment:freeze.frozen-inputs"
exact_inputs:
  - input_id: "artifact:phase8.root-summary"
    relative_path: "knowledge/coverage/phase8.root-summary.json"
    sha256: "sha256:<fill-before-dispatch>"
    availability: required
  - input_id: "decision:phase8.release-approval"
    relative_path: "knowledge/decisions/phase8.release-approval.json"
    sha256: "sha256:<fill-before-dispatch>"
    availability: required
  - input_id: "artifact:phase8.generated-manifest"
    relative_path: "knowledge/generated/phase8.output-manifest.json"
    sha256: "sha256:<fill-before-dispatch>"
    availability: required
scope_denominator:
  - "全部 P0/P1、声明输出、G0–G7 判定、已接受未知、根摘要输入和冻结 allow-list；不得抽样。"
allowed_evidence:
  - "只读已提交 canonical 记录、签署决定、生成清单和内容哈希；只运行声明的无副作用验证/重建命令。"
forbidden_inference:
  - "不得因 schema 通过就推断产品主张为真，不得把 Agent 输出当成人类批准。"
  - "不得忽略不可到达输入、P0 冲突、非确定性差异或根摘要自引用。"
output_records:
  - record_type: coverage-summary
    schema: "guides/product-reverse-engineering/toolkit/schemas/coverage-summary.schema.json"
    relative_path: "knowledge/coverage/phase8.freeze-audit.json"
validation_command: "python3 tools/validate_product_reverse_engineering_guide.py"
stop_conditions:
  - condition: authorization-drift
    action: "stop-and-request-new-authorization"
  - condition: workspace-identity-mismatch
    action: "stop-and-report-identity-mismatch"
  - condition: required-input-unreachable
    action: "stop-and-report-unreachable-input"
  - condition: unsafe-or-unapproved-runtime
    action: "stop-and-escalate-to-safety-owner"
human_review_owner: "发布责任人与目的决策人"
agent_rules:
  preserve_unknowns: true
  cite_each_claim: true
  report_unreachable_inputs: true
  absence_terms:
    - not-found
    - does-not-exist
  may_approve_gate: false
  may_change_authorization: false
  may_run_unapproved_runtime: false
```

Agent 输出的只有冻结审计记录；需要决定的事项作为阻断项交给 `human_review_owner`，不得写入 `knowledge/decisions/`。最终 `ART-P8-APPROVAL`、G7 判定和分离式冻结证明必须由既定人类/确定性流程按[覆盖、质量与冻结](../core/coverage-quality-and-freeze.md)生成；Agent 无权自批 Gate 或改写输入来使验证通过。

## 通用交付格式

每次执行先回显 packet ID、授权/工作区身份、输入哈希和停止条件，再报告：已完成分母、未知、`not-found`、不可到达输入、证据冲突、输出路径、验证结果与需人类决定事项。任何 claim 都必须逐条引用 evidence ID；汇总段落不能成为新的无证据 claim。

验证失败时保留原始失败输出并停止接受流程。修复只发生在拥有写权限的 canonical 分区，生成投影必须重新构建；具体写入边界见[项目证据仓布局](project-layout.md)。
