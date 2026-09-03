# AI Agent 可复制任务包

**证据成熟度：`proposed`**

**适用范围：** 用于把已批准、边界明确的逆向子任务交给 AI Agent；任务包只允许处理闭合输入 manifest 并写入闭合输出 manifest，不授予 Agent 批准门禁、改变授权、接受风险或执行未批准运行实验的权力。

每个 YAML 块由 `packet_type` 包络元数据和[人机协作](../core/human-agent-collaboration.md)规定的恰好十三项核心字段组成。复制后必须替换全部 `<fill-before-dispatch>`，计算 manifest/文件/工具哈希，并由分派人和 `human_review_owner` 复核；仍有占位值的包不得执行。

`input_identity.entries` 是闭合的不可变输入清单，`allowed_evidence` 只能引用其中 ID；自然语言不能扩大证据范围。`output_paths_or_record_types` 每项只代表一个稳定 ID 和一个 JSON 文件，不得写集合文件、目录或 glob。发现新输入或新对象时停止并请求新版任务包。所有验证命令从 `workspace_identity.canonical_working_directory` 执行，且通过冻结的 vendor checkout 精确绑定工具版本、commit 与哈希。

所有包强制保留未知、逐 claim 引用 evidence、报告不可到达输入，并区分 `not-found` 与 `does-not-exist`。前者只表示在声明分母、路径、版本、查询和权限内未找到；没有排除替代位置的证据时不得使用后者。

## inventory

用途：为一个预先声明的资产分母项生成单对象资产记录与单对象覆盖记录；更多资产需要在新版包的输出 manifest 中逐项列出。

```yaml
packet_type: inventory
objective: "核对冻结范围内一个已声明资产分母项，生成可复核的单对象资产记录和覆盖记录，不把未找到解释为不存在。"
authorization_identity:
  authorization_record_id: "decision:phase0.authorization"
  authorization_record_hash: "sha256:<fill-before-dispatch>"
  authorization_record_version: "<fill-before-dispatch>"
  current_g0:
    gate_record_id: "gate:phase0.g0-authorization"
    gate_record_hash: "sha256:<fill-before-dispatch>"
    verdict: pass
input_identity:
  manifest_id: "manifest:inventory.inputs-v1"
  manifest_sha256: "sha256:<fill-before-dispatch>"
  entries:
    - input_id: "artifact:phase1.baseline"
      relative_path: "knowledge/records/artifact/phase1.baseline.json"
      sha256: "sha256:<fill-before-dispatch>"
      input_type: baseline-record
      version: "<fill-before-dispatch>"
      availability: required
      allowed_actions: [read, hash, parse, compare]
    - input_id: "artifact:phase1.denominator"
      relative_path: "knowledge/coverage/phase1.denominator.json"
      sha256: "sha256:<fill-before-dispatch>"
      input_type: denominator-record
      version: "<fill-before-dispatch>"
      availability: required
      allowed_actions: [read, hash, parse, compare]
workspace_identity:
  workspace_root_id: "workspace:target.reverse-engineering"
  repository_or_worktree_version: "<fill-before-dispatch>"
  canonical_working_directory: "."
  configuration_identity: "configuration:target.inventory-snapshot"
  role_identity: "role:analyst.inventory-reader"
  environment_identity: "environment:target.static-snapshot"
  time_window:
    from: "<fill-before-dispatch>"
    to: "<fill-before-dispatch>"
    timezone: "<fill-before-dispatch>"
scope:
  included: ["denominator:inventory.target-asset"]
  excluded: ["scope:inventory.all-other-assets"]
  versions: ["<fill-before-dispatch>"]
  roles: ["role:analyst.inventory-reader"]
  product_surfaces: ["surface:inventory.declared-entry"]
  assets: ["asset:inventory.target-entry"]
  data: ["data:inventory.metadata-only"]
  integrations: ["integration:inventory.none-authorized"]
  nonfunctional: ["nonfunctional:inventory.read-only"]
denominator:
  - item_id: "denominator:inventory.target-asset"
    parent_id: null
    priority: P1
    target_status: must-be-accounted-for
    calculation_rule:
      denominator_units: 1
      achieved_when: "声明 asset 记录通过指定 schema，引用 manifest 内证据，且覆盖记录明确为 supported、not-found、unreachable 或 excluded 之一。"
allowed_evidence:
  - "artifact:phase1.baseline"
  - "artifact:phase1.denominator"
forbidden_inference:
  statements:
    - "不得从文件名、依赖存在、静态可达或框架惯例推断功能已部署、已启用或已运行。"
    - "不得把 not-found 改写为 does-not-exist。"
  required_claim_discipline:
    preserve_unknowns: true
    cite_each_claim: true
    report_unreachable_inputs: true
    absence_terms: [not-found, does-not-exist]
  authority_limits:
    may_approve_gate: false
    may_change_authorization: false
    may_run_unapproved_runtime: false
output_paths_or_record_types:
  - record_id: "asset:inventory.target-entry"
    record_type: asset
    relative_path: "knowledge/records/asset/inventory.target-entry.json"
    schema_name: asset
    schema_relative_path: "vendor/codex-playbook/guides/product-reverse-engineering/toolkit/schemas/asset.schema.json"
  - record_id: "coverage-summary:inventory.target-entry"
    record_type: coverage-summary
    relative_path: "knowledge/coverage/inventory.target-entry.json"
    schema_name: coverage-summary
    schema_relative_path: "vendor/codex-playbook/guides/product-reverse-engineering/toolkit/schemas/coverage-summary.schema.json"
schema:
  registry_id: "schema-registry:product-reverse-engineering.v1"
  tool_checkout_id: "workspace:vendor.codex-playbook"
  registry_relative_path: "vendor/codex-playbook/guides/product-reverse-engineering/toolkit/schemas/"
  registry_commit: "<fill-before-dispatch>"
  registry_tree_sha256: "sha256:<fill-before-dispatch>"
validation_command:
  canonical_working_directory: "."
  tool_checkout_identity:
    checkout_id: "workspace:vendor.codex-playbook"
    relative_path: "vendor/codex-playbook/"
    repository_commit: "<fill-before-dispatch>"
    tree_sha256: "sha256:<fill-before-dispatch>"
  validator:
    relative_path: "vendor/codex-playbook/tools/validate_product_reverse_engineering_guide.py"
    version: "<fill-before-dispatch>"
    repository_commit: "<fill-before-dispatch>"
    sha256: "sha256:<fill-before-dispatch>"
  commands:
    - output_record_id: "asset:inventory.target-entry"
      command: "python3 vendor/codex-playbook/tools/validate_product_reverse_engineering_guide.py --schema asset knowledge/records/asset/inventory.target-entry.json"
      expected_exit_code: 0
    - output_record_id: "coverage-summary:inventory.target-entry"
      command: "python3 vendor/codex-playbook/tools/validate_product_reverse_engineering_guide.py --schema coverage-summary knowledge/coverage/inventory.target-entry.json"
      expected_exit_code: 0
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
```

## vertical-trace

用途：为一个批准切片的一条预先声明关系生成单对象 trace-link 和对应单对象 claim；不得自行增加节点、边或输出文件。

```yaml
packet_type: vertical-trace
objective: "核对一个声明切片中的一条 source-target 关系，分别输出单对象 trace-link 与 claim，断点保持未知。"
authorization_identity:
  authorization_record_id: "decision:phase0.authorization"
  authorization_record_hash: "sha256:<fill-before-dispatch>"
  authorization_record_version: "<fill-before-dispatch>"
  current_g0:
    gate_record_id: "gate:phase0.g0-authorization"
    gate_record_hash: "sha256:<fill-before-dispatch>"
    verdict: pass
input_identity:
  manifest_id: "manifest:vertical-trace.inputs-v1"
  manifest_sha256: "sha256:<fill-before-dispatch>"
  entries:
    - input_id: "artifact:phase4.selected-slice"
      relative_path: "knowledge/records/artifact/phase4.selected-slice.json"
      sha256: "sha256:<fill-before-dispatch>"
      input_type: slice-record
      version: "<fill-before-dispatch>"
      availability: required
      allowed_actions: [read, hash, parse, compare]
    - input_id: "artifact:phase3.asset-atlas"
      relative_path: "knowledge/records/artifact/phase3.asset-atlas.json"
      sha256: "sha256:<fill-before-dispatch>"
      input_type: asset-atlas-record
      version: "<fill-before-dispatch>"
      availability: required
      allowed_actions: [read, hash, parse, compare]
workspace_identity:
  workspace_root_id: "workspace:target.reverse-engineering"
  repository_or_worktree_version: "<fill-before-dispatch>"
  canonical_working_directory: "."
  configuration_identity: "configuration:target.trace-snapshot"
  role_identity: "role:analyst.trace-reader"
  environment_identity: "environment:target.trace-snapshot"
  time_window:
    from: "<fill-before-dispatch>"
    to: "<fill-before-dispatch>"
    timezone: "<fill-before-dispatch>"
scope:
  included: ["denominator:trace.declared-edge"]
  excluded: ["scope:trace.other-edges"]
  versions: ["<fill-before-dispatch>"]
  roles: ["role:analyst.trace-reader"]
  product_surfaces: ["surface:trace.declared-entry"]
  assets: ["asset:trace.declared-source", "asset:trace.declared-target"]
  data: ["data:trace.declared-context"]
  integrations: ["integration:trace.declared-boundary"]
  nonfunctional: ["nonfunctional:trace.no-runtime-execution"]
denominator:
  - item_id: "denominator:trace.declared-edge"
    parent_id: null
    priority: P0
    target_status: must-be-supported
    calculation_rule:
      denominator_units: 1
      achieved_when: "声明 trace-link 与 claim 两个 JSON 均通过各自 schema，端点、上下文和逐 claim evidence 引用闭合。"
allowed_evidence:
  - "artifact:phase4.selected-slice"
  - "artifact:phase3.asset-atlas"
forbidden_inference:
  statements:
    - "不得用调用可达性替代实际执行，也不得把可见 UI 行为推断成隐藏服务端实现。"
    - "不得用框架常识补齐断边，not-found 不等于 does-not-exist。"
  required_claim_discipline:
    preserve_unknowns: true
    cite_each_claim: true
    report_unreachable_inputs: true
    absence_terms: [not-found, does-not-exist]
  authority_limits:
    may_approve_gate: false
    may_change_authorization: false
    may_run_unapproved_runtime: false
output_paths_or_record_types:
  - record_id: "trace-link:trace.declared-edge"
    record_type: trace-link
    relative_path: "knowledge/records/trace-link/trace.declared-edge.json"
    schema_name: trace-link
    schema_relative_path: "vendor/codex-playbook/guides/product-reverse-engineering/toolkit/schemas/trace-link.schema.json"
  - record_id: "claim:trace.declared-edge"
    record_type: claim
    relative_path: "knowledge/records/claim/trace.declared-edge.json"
    schema_name: claim
    schema_relative_path: "vendor/codex-playbook/guides/product-reverse-engineering/toolkit/schemas/claim.schema.json"
schema:
  registry_id: "schema-registry:product-reverse-engineering.v1"
  tool_checkout_id: "workspace:vendor.codex-playbook"
  registry_relative_path: "vendor/codex-playbook/guides/product-reverse-engineering/toolkit/schemas/"
  registry_commit: "<fill-before-dispatch>"
  registry_tree_sha256: "sha256:<fill-before-dispatch>"
validation_command:
  canonical_working_directory: "."
  tool_checkout_identity:
    checkout_id: "workspace:vendor.codex-playbook"
    relative_path: "vendor/codex-playbook/"
    repository_commit: "<fill-before-dispatch>"
    tree_sha256: "sha256:<fill-before-dispatch>"
  validator:
    relative_path: "vendor/codex-playbook/tools/validate_product_reverse_engineering_guide.py"
    version: "<fill-before-dispatch>"
    repository_commit: "<fill-before-dispatch>"
    sha256: "sha256:<fill-before-dispatch>"
  commands:
    - output_record_id: "trace-link:trace.declared-edge"
      command: "python3 vendor/codex-playbook/tools/validate_product_reverse_engineering_guide.py --schema trace-link knowledge/records/trace-link/trace.declared-edge.json"
      expected_exit_code: 0
    - output_record_id: "claim:trace.declared-edge"
      command: "python3 vendor/codex-playbook/tools/validate_product_reverse_engineering_guide.py --schema claim knowledge/records/claim/trace.declared-edge.json"
      expected_exit_code: 0
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
```

## runtime-experiment-review

用途：只读复核一个已执行实验的三件套；本任务不执行、重放或修改实验。

```yaml
packet_type: runtime-experiment-review
objective: "审计一个已声明实验的协议、结果与效应是否身份一致并满足首错、清理和复现契约，输出单对象实验复核记录。"
authorization_identity:
  authorization_record_id: "decision:phase0.authorization"
  authorization_record_hash: "sha256:<fill-before-dispatch>"
  authorization_record_version: "<fill-before-dispatch>"
  current_g0:
    gate_record_id: "gate:phase0.g0-authorization"
    gate_record_hash: "sha256:<fill-before-dispatch>"
    verdict: pass
input_identity:
  manifest_id: "manifest:runtime-review.inputs-v1"
  manifest_sha256: "sha256:<fill-before-dispatch>"
  entries:
    - input_id: "experiment:phase5.protocol"
      relative_path: "knowledge/runtime/protocols/phase5.protocol.json"
      sha256: "sha256:<fill-before-dispatch>"
      input_type: experiment-protocol
      version: "<fill-before-dispatch>"
      availability: required
      allowed_actions: [read, hash, parse, compare, validate]
    - input_id: "experiment:phase5.result"
      relative_path: "knowledge/runtime/results/phase5.result.json"
      sha256: "sha256:<fill-before-dispatch>"
      input_type: experiment-result
      version: "<fill-before-dispatch>"
      availability: required
      allowed_actions: [read, hash, parse, compare, validate]
    - input_id: "experiment:phase5.effects"
      relative_path: "knowledge/runtime/effects/phase5.effects.json"
      sha256: "sha256:<fill-before-dispatch>"
      input_type: experiment-effects
      version: "<fill-before-dispatch>"
      availability: required
      allowed_actions: [read, hash, parse, compare, validate]
workspace_identity:
  workspace_root_id: "workspace:target.reverse-engineering"
  repository_or_worktree_version: "<fill-before-dispatch>"
  canonical_working_directory: "."
  configuration_identity: "configuration:target.runtime-review"
  role_identity: "role:qa.experiment-reviewer"
  environment_identity: "environment:target.authorized-clone"
  time_window:
    from: "<fill-before-dispatch>"
    to: "<fill-before-dispatch>"
    timezone: "<fill-before-dispatch>"
scope:
  included: ["denominator:runtime-review.declared-experiment"]
  excluded: ["scope:runtime-review.new-execution"]
  versions: ["<fill-before-dispatch>"]
  roles: ["role:qa.experiment-reviewer"]
  product_surfaces: ["surface:runtime-review.declared-scenario"]
  assets: ["asset:runtime-review.protocol-result-effects"]
  data: ["data:runtime-review.redacted-observations"]
  integrations: ["integration:runtime-review.no-live-access"]
  nonfunctional: ["nonfunctional:runtime-review.read-only"]
denominator:
  - item_id: "denominator:runtime-review.declared-experiment"
    parent_id: null
    priority: P0
    target_status: must-be-reviewed
    calculation_rule:
      denominator_units: 1
      achieved_when: "单对象 experiment 输出通过 schema，三项输入哈希闭合，首错、副作用、清理、残留和复现均有明确结果或未知。"
allowed_evidence:
  - "experiment:phase5.protocol"
  - "experiment:phase5.result"
  - "experiment:phase5.effects"
forbidden_inference:
  statements:
    - "不得把计划步骤当作已执行，不得用成功重试覆盖首错，不得从清理命令存在推断清理成功。"
    - "不得把一次运行泛化到未测版本、角色或环境，也不得发起任何新运行。"
  required_claim_discipline:
    preserve_unknowns: true
    cite_each_claim: true
    report_unreachable_inputs: true
    absence_terms: [not-found, does-not-exist]
  authority_limits:
    may_approve_gate: false
    may_change_authorization: false
    may_run_unapproved_runtime: false
output_paths_or_record_types:
  - record_id: "experiment:runtime-review.declared-experiment"
    record_type: experiment
    relative_path: "knowledge/records/experiment/runtime-review.declared-experiment.json"
    schema_name: experiment
    schema_relative_path: "vendor/codex-playbook/guides/product-reverse-engineering/toolkit/schemas/experiment.schema.json"
schema:
  registry_id: "schema-registry:product-reverse-engineering.v1"
  tool_checkout_id: "workspace:vendor.codex-playbook"
  registry_relative_path: "vendor/codex-playbook/guides/product-reverse-engineering/toolkit/schemas/"
  registry_commit: "<fill-before-dispatch>"
  registry_tree_sha256: "sha256:<fill-before-dispatch>"
validation_command:
  canonical_working_directory: "."
  tool_checkout_identity:
    checkout_id: "workspace:vendor.codex-playbook"
    relative_path: "vendor/codex-playbook/"
    repository_commit: "<fill-before-dispatch>"
    tree_sha256: "sha256:<fill-before-dispatch>"
  validator:
    relative_path: "vendor/codex-playbook/tools/validate_product_reverse_engineering_guide.py"
    version: "<fill-before-dispatch>"
    repository_commit: "<fill-before-dispatch>"
    sha256: "sha256:<fill-before-dispatch>"
  commands:
    - output_record_id: "experiment:runtime-review.declared-experiment"
      command: "python3 vendor/codex-playbook/tools/validate_product_reverse_engineering_guide.py --schema experiment knowledge/records/experiment/runtime-review.declared-experiment.json"
      expected_exit_code: 0
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
```

## conflict-audit

用途：核对一个 P0/P1 主张的竞争证据并生成单对象 conflicting claim 与单对象覆盖审计记录；人类决定仍由决定分区唯一拥有。

```yaml
packet_type: conflict-audit
objective: "审计一个声明主张的证据冲突、版本或上下文混用，保留竞争解释并输出单对象冲突主张和覆盖记录。"
authorization_identity:
  authorization_record_id: "decision:phase0.authorization"
  authorization_record_hash: "sha256:<fill-before-dispatch>"
  authorization_record_version: "<fill-before-dispatch>"
  current_g0:
    gate_record_id: "gate:phase0.g0-authorization"
    gate_record_hash: "sha256:<fill-before-dispatch>"
    verdict: pass
input_identity:
  manifest_id: "manifest:conflict-audit.inputs-v1"
  manifest_sha256: "sha256:<fill-before-dispatch>"
  entries:
    - input_id: "claim:phase7.audit-target"
      relative_path: "knowledge/records/claim/phase7.audit-target.json"
      sha256: "sha256:<fill-before-dispatch>"
      input_type: claim-record
      version: "<fill-before-dispatch>"
      availability: required
      allowed_actions: [read, hash, parse, compare, validate]
    - input_id: "evidence:phase7.audit-target-index"
      relative_path: "knowledge/evidence/indexes/phase7.audit-target-index.json"
      sha256: "sha256:<fill-before-dispatch>"
      input_type: redacted-evidence-index
      version: "<fill-before-dispatch>"
      availability: required
      allowed_actions: [read, hash, parse, compare]
workspace_identity:
  workspace_root_id: "workspace:target.reverse-engineering"
  repository_or_worktree_version: "<fill-before-dispatch>"
  canonical_working_directory: "."
  configuration_identity: "configuration:target.conflict-audit"
  role_identity: "role:lead.conflict-reviewer"
  environment_identity: "environment:target.frozen-records"
  time_window:
    from: "<fill-before-dispatch>"
    to: "<fill-before-dispatch>"
    timezone: "<fill-before-dispatch>"
scope:
  included: ["denominator:conflict-audit.target-claim"]
  excluded: ["scope:conflict-audit.other-claims"]
  versions: ["<fill-before-dispatch>"]
  roles: ["role:lead.conflict-reviewer"]
  product_surfaces: ["surface:conflict-audit.declared-context"]
  assets: ["asset:conflict-audit.declared-claim"]
  data: ["data:conflict-audit.redacted-index"]
  integrations: ["integration:conflict-audit.none-authorized"]
  nonfunctional: ["nonfunctional:conflict-audit.preserve-history"]
denominator:
  - item_id: "denominator:conflict-audit.target-claim"
    parent_id: null
    priority: P0
    target_status: must-be-reviewed
    calculation_rule:
      denominator_units: 1
      achieved_when: "单对象 claim 与 coverage-summary 输出均通过 schema，双方证据、版本、上下文和需人类决定事项均保留。"
allowed_evidence:
  - "claim:phase7.audit-target"
  - "evidence:phase7.audit-target-index"
forbidden_inference:
  statements:
    - "不得按票数、时间新旧或来源权威感自动选择赢家，也不得删除少数证据。"
    - "不得把不同版本、角色或环境的差异压成一个冲突，不得自行接受风险。"
  required_claim_discipline:
    preserve_unknowns: true
    cite_each_claim: true
    report_unreachable_inputs: true
    absence_terms: [not-found, does-not-exist]
  authority_limits:
    may_approve_gate: false
    may_change_authorization: false
    may_run_unapproved_runtime: false
output_paths_or_record_types:
  - record_id: "claim:conflict-audit.target-claim"
    record_type: claim
    relative_path: "knowledge/records/claim/conflict-audit.target-claim.json"
    schema_name: claim
    schema_relative_path: "vendor/codex-playbook/guides/product-reverse-engineering/toolkit/schemas/claim.schema.json"
  - record_id: "coverage-summary:conflict-audit.target-claim"
    record_type: coverage-summary
    relative_path: "knowledge/coverage/conflict-audit.target-claim.json"
    schema_name: coverage-summary
    schema_relative_path: "vendor/codex-playbook/guides/product-reverse-engineering/toolkit/schemas/coverage-summary.schema.json"
schema:
  registry_id: "schema-registry:product-reverse-engineering.v1"
  tool_checkout_id: "workspace:vendor.codex-playbook"
  registry_relative_path: "vendor/codex-playbook/guides/product-reverse-engineering/toolkit/schemas/"
  registry_commit: "<fill-before-dispatch>"
  registry_tree_sha256: "sha256:<fill-before-dispatch>"
validation_command:
  canonical_working_directory: "."
  tool_checkout_identity:
    checkout_id: "workspace:vendor.codex-playbook"
    relative_path: "vendor/codex-playbook/"
    repository_commit: "<fill-before-dispatch>"
    tree_sha256: "sha256:<fill-before-dispatch>"
  validator:
    relative_path: "vendor/codex-playbook/tools/validate_product_reverse_engineering_guide.py"
    version: "<fill-before-dispatch>"
    repository_commit: "<fill-before-dispatch>"
    sha256: "sha256:<fill-before-dispatch>"
  commands:
    - output_record_id: "claim:conflict-audit.target-claim"
      command: "python3 vendor/codex-playbook/tools/validate_product_reverse_engineering_guide.py --schema claim knowledge/records/claim/conflict-audit.target-claim.json"
      expected_exit_code: 0
    - output_record_id: "coverage-summary:conflict-audit.target-claim"
      command: "python3 vendor/codex-playbook/tools/validate_product_reverse_engineering_guide.py --schema coverage-summary knowledge/coverage/conflict-audit.target-claim.json"
      expected_exit_code: 0
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
```

审计输出只在 claim/coverage 记录中列出“需要谁决定什么”，不得写入 `knowledge/decisions/`。有权限的人类复核后另建决定记录；Agent 不能模仿签名、选择最终结果或生成风险接受。

## freeze-audit

用途：核对一个声明冻结输出的分母、门禁输入、批准、确定性生成和无环顺序；Agent 只写单对象覆盖审计记录。

```yaml
packet_type: freeze-audit
objective: "验证一个声明冻结输出是否由固定权威输入无环、确定性重建，并核对其阻断项和人工批准引用。"
authorization_identity:
  authorization_record_id: "decision:phase0.authorization"
  authorization_record_hash: "sha256:<fill-before-dispatch>"
  authorization_record_version: "<fill-before-dispatch>"
  current_g0:
    gate_record_id: "gate:phase0.g0-authorization"
    gate_record_hash: "sha256:<fill-before-dispatch>"
    verdict: pass
input_identity:
  manifest_id: "manifest:freeze-audit.inputs-v1"
  manifest_sha256: "sha256:<fill-before-dispatch>"
  entries:
    - input_id: "coverage-summary:phase8.root-summary"
      relative_path: "knowledge/coverage/phase8.root-summary.json"
      sha256: "sha256:<fill-before-dispatch>"
      input_type: root-summary-record
      version: "<fill-before-dispatch>"
      availability: required
      allowed_actions: [read, hash, parse, compare, validate]
    - input_id: "decision:phase8.release-approval"
      relative_path: "knowledge/decisions/phase8.release-approval.json"
      sha256: "sha256:<fill-before-dispatch>"
      input_type: human-signed-decision
      version: "<fill-before-dispatch>"
      availability: required
      allowed_actions: [read, hash, parse, compare, validate]
    - input_id: "artifact:phase8.generated-output"
      relative_path: "knowledge/generated/phase8.declared-output.json"
      sha256: "sha256:<fill-before-dispatch>"
      input_type: generated-output
      version: "<fill-before-dispatch>"
      availability: required
      allowed_actions: [read, hash, compare]
workspace_identity:
  workspace_root_id: "workspace:target.reverse-engineering"
  repository_or_worktree_version: "<fill-before-dispatch>"
  canonical_working_directory: "."
  configuration_identity: "configuration:target.freeze-audit"
  role_identity: "role:release.freeze-reviewer"
  environment_identity: "environment:target.frozen-inputs"
  time_window:
    from: "<fill-before-dispatch>"
    to: "<fill-before-dispatch>"
    timezone: "<fill-before-dispatch>"
scope:
  included: ["denominator:freeze-audit.declared-output"]
  excluded: ["scope:freeze-audit.other-outputs"]
  versions: ["<fill-before-dispatch>"]
  roles: ["role:release.freeze-reviewer"]
  product_surfaces: ["surface:freeze-audit.declared-release"]
  assets: ["asset:freeze-audit.declared-output"]
  data: ["data:freeze-audit.hashes-only"]
  integrations: ["integration:freeze-audit.integrity-anchor"]
  nonfunctional: ["nonfunctional:freeze-audit.deterministic-rebuild"]
denominator:
  - item_id: "denominator:freeze-audit.declared-output"
    parent_id: null
    priority: P0
    target_status: must-be-supported
    calculation_rule:
      denominator_units: 1
      achieved_when: "单对象 coverage-summary 输出通过 schema，输入 allow-list、G0-G7、人工批准、根摘要和声明输出哈希全部可寻址且无环。"
allowed_evidence:
  - "coverage-summary:phase8.root-summary"
  - "decision:phase8.release-approval"
  - "artifact:phase8.generated-output"
forbidden_inference:
  statements:
    - "不得因 schema 通过就推断产品主张为真，不得把 Agent 输出当成人类批准。"
    - "不得忽略不可到达输入、P0 冲突、非确定性差异或根摘要自引用。"
  required_claim_discipline:
    preserve_unknowns: true
    cite_each_claim: true
    report_unreachable_inputs: true
    absence_terms: [not-found, does-not-exist]
  authority_limits:
    may_approve_gate: false
    may_change_authorization: false
    may_run_unapproved_runtime: false
output_paths_or_record_types:
  - record_id: "coverage-summary:freeze-audit.declared-output"
    record_type: coverage-summary
    relative_path: "knowledge/coverage/freeze-audit.declared-output.json"
    schema_name: coverage-summary
    schema_relative_path: "vendor/codex-playbook/guides/product-reverse-engineering/toolkit/schemas/coverage-summary.schema.json"
schema:
  registry_id: "schema-registry:product-reverse-engineering.v1"
  tool_checkout_id: "workspace:vendor.codex-playbook"
  registry_relative_path: "vendor/codex-playbook/guides/product-reverse-engineering/toolkit/schemas/"
  registry_commit: "<fill-before-dispatch>"
  registry_tree_sha256: "sha256:<fill-before-dispatch>"
validation_command:
  canonical_working_directory: "."
  tool_checkout_identity:
    checkout_id: "workspace:vendor.codex-playbook"
    relative_path: "vendor/codex-playbook/"
    repository_commit: "<fill-before-dispatch>"
    tree_sha256: "sha256:<fill-before-dispatch>"
  validator:
    relative_path: "vendor/codex-playbook/tools/validate_product_reverse_engineering_guide.py"
    version: "<fill-before-dispatch>"
    repository_commit: "<fill-before-dispatch>"
    sha256: "sha256:<fill-before-dispatch>"
  commands:
    - output_record_id: "coverage-summary:freeze-audit.declared-output"
      command: "python3 vendor/codex-playbook/tools/validate_product_reverse_engineering_guide.py --schema coverage-summary knowledge/coverage/freeze-audit.declared-output.json"
      expected_exit_code: 0
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
```

Agent 输出的只有冻结审计记录；需要决定的事项作为阻断项交给 `human_review_owner`，不得写入 `knowledge/decisions/`。最终 `ART-P8-APPROVAL`、G7 判定和分离式冻结证明必须由既定人类/确定性流程按[覆盖、质量与冻结](../core/coverage-quality-and-freeze.md)生成。

## 通用交付格式

执行前回显 `packet_type`、十三项核心字段、授权/G0 身份、workspace/cwd、输入 manifest 哈希、输出 manifest 和停止条件。若任一 required 输入不可到达、哈希不符、路径越界或工具 checkout 无法解析，应停止并报告该 input ID，不得搜索替代输入。

执行后逐分母项报告状态，逐 claim 引用 evidence ID，并单列未知、`not-found`、不可到达输入、冲突、输出文件及每条精确验证命令的退出码。不得动态增加输出记录；新对象交由 `human_review_owner` 决定是否创建新版任务包。
