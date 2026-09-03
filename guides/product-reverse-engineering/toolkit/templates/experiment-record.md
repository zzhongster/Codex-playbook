# 运行时实验记录模板

## ART-P5-PROTOCOL 协议包

```yaml
artifact_type: "ART-P5-PROTOCOL"
artifact_id: "artifact:p5-protocol.template-replace-me"
record_id: "artifact:p5-protocol.template-replace-me"
content_hash: "sha256:REPLACE_WITH_PROTOCOL_CONTENT_HASH"
product_version: "REPLACE_WITH_IMMUTABLE_PRODUCT_VERSION"
scope_or_module: "REPLACE_WITH_QUALIFIED_SCOPE_OR_MODULE_ID"
status: "frozen"
created_at: "YYYY-MM-DDTHH:MM:SSZ"
evidence_references:
  - "evidence:template.replace-me"
owner: "REPLACE_WITH_NAMED_HUMAN_OWNER"
validation_method: "REPLACE_WITH_REPRODUCTION_AND_ACCEPTANCE_METHOD"
last_updated: "YYYY-MM-DD"
claim_references: []
method_definitions:
  - method_id: "method:template.replace-me"
    method_maturity: "proposed"
evidence_method_entries:
  - evidence_id: "evidence:template.replace-me"
    method_id: "method:template.replace-me"
authorization_record_id: "REPLACE_WITH_ART_P0_AUTH_ID"
authorization_gate_record_id: "REPLACE_WITH_CURRENT_ART_G0_AUTH_ID"
environment_identity: "REPLACE_WITH_IMMUTABLE_ENVIRONMENT_IDENTITY_AND_HASHES"
pre_state_fingerprint: "REPLACE_WITH_BASELINE_FINGERPRINT"
fingerprints:
  source: "REPLACE_WITH_SOURCE_FINGERPRINT_OR_EXPLICIT_NOT_AVAILABLE"
  artifact: "REPLACE_WITH_ARTIFACT_FINGERPRINT"
  clone: "REPLACE_WITH_CLONE_FINGERPRINT_OR_EXPLICIT_NOT_APPLICABLE"
sentinel: "REPLACE_WITH_UNIQUE_SYNTHETIC_SENTINEL"
action_permissions:
  read:
    verdict: "not-authorized"
    authorization_reference: "REPLACE_WITH_ACTION_AUTHORIZATION_REFERENCE"
  write:
    verdict: "not-authorized"
    authorization_reference: "REPLACE_WITH_ACTION_AUTHORIZATION_REFERENCE"
  fault-injection:
    verdict: "not-authorized"
    authorization_reference: "REPLACE_WITH_ACTION_AUTHORIZATION_REFERENCE"
  egress:
    verdict: "not-authorized"
    authorization_reference: "REPLACE_WITH_ACTION_AUTHORIZATION_REFERENCE"
  cleanup:
    verdict: "not-authorized"
    authorization_reference: "REPLACE_WITH_ACTION_AUTHORIZATION_REFERENCE"
operational_limits:
  cost: "REPLACE_WITH_COST_LIMIT_AND_UNIT"
  rate: "REPLACE_WITH_RATE_LIMIT_AND_WINDOW"
  blast_radius: "REPLACE_WITH_MAXIMUM_IMPACT_BOUNDARY"
recovery:
  recovery_point: "REPLACE_WITH_RECOVERY_POINT_ID_AND_FINGERPRINT"
  owner: "REPLACE_WITH_NAMED_HUMAN_RECOVERY_OWNER"
  max_restore_time: "REPLACE_WITH_DURATION"
target_claim_references: []
protocol_frozen_at: "YYYY-MM-DDTHH:MM:SSZ"
role_and_test_account:
  role: "REPLACE_WITH_ROLE"
  test_account_id: "REPLACE_WITH_NON_SECRET_TEST_ACCOUNT_ID"
inputs:
  - input_id: "input:template.replace-me"
    value_or_fingerprint: "REPLACE_WITH_SYNTHETIC_VALUE_OR_CONTENT_FINGERPRINT"
    data_classification: "REPLACE_WITH_DATA_CLASSIFICATION"
alternative_explanations:
  - explanation_id: "explanation:template.replace-me"
    statement: "REPLACE_WITH_ALTERNATIVE_EXPLANATION"
    distinguishing_evidence_needed: "REPLACE_WITH_DISCRIMINATING_EVIDENCE"
variables:
  - name: "REPLACE_WITH_VARIABLE_NAME"
    controlled_value: "REPLACE_WITH_FROZEN_VALUE"
    uncontrolled_limit: "REPLACE_WITH_UNCONTROLLED_VARIATION_OR_EXPLICIT_NONE"
wait_conditions:
  - condition: "REPLACE_WITH_OBSERVABLE_WAIT_CONDITION"
    timeout: "REPLACE_WITH_DURATION"
    on_timeout: "REPLACE_WITH_STOP_AND_CAPTURE_ACTION"
tool_versions:
  - tool: "REPLACE_WITH_TOOL_NAME"
    version: "REPLACE_WITH_EXACT_VERSION"
    configuration_hash: "REPLACE_WITH_SHA256_OR_EXPLICIT_NOT_APPLICABLE"
forbidden_side_effects:
  - effect: "REPLACE_WITH_FORBIDDEN_EFFECT"
    detection: "REPLACE_WITH_DETECTION_METHOD"
    stop_response: "REPLACE_WITH_STOP_AND_DISCLOSURE_ACTION"
reproduction_criteria:
  required_runs: 2
  independent_executor_required: true
  environment_equivalence_rule: "REPLACE_WITH_EQUIVALENCE_RULE"
  tolerance_rule: "REPLACE_WITH_PRECOMMITTED_TOLERANCE_RULE"
protocol_steps:
  - step_id: "step:template.replace-me"
    action: "REPLACE_WITH_AUTHORIZED_ACTION"
    input: "REPLACE_WITH_INPUT_OR_EXPLICIT_NONE"
    observation_points: []
    stop_condition: "REPLACE_WITH_STEP_STOP_CONDITION"
expected_observations:
  - observation_id: "observation:template.replace-me"
    surface: "REPLACE_WITH_UI_NETWORK_LOG_DATA_MESSAGE_FILE_OR_OTHER"
    expected: "REPLACE_WITH_PRECOMMITTED_EXPECTATION"
    tolerance: "REPLACE_WITH_TOLERANCE_OR_EXACT"
```

## ART-P5-RESULT 结果包

```yaml
artifact_type: "ART-P5-RESULT"
artifact_id: "artifact:p5-result.template-replace-me"
content_hash: "sha256:REPLACE_WITH_RESULT_CONTENT_HASH"
status: "draft"
created_at: "YYYY-MM-DDTHH:MM:SSZ"
owner: "REPLACE_WITH_NAMED_RESULT_OWNER"
product_version: "REPLACE_WITH_IMMUTABLE_PRODUCT_VERSION"
scope_or_module: "REPLACE_WITH_QUALIFIED_SCOPE_OR_MODULE_ID"
evidence_references: []
method_definitions: []
evidence_method_entries: []
protocol_reference:
  protocol_id: "artifact:p5-protocol.template-replace-me"
  protocol_content_hash: "sha256:REPLACE_WITH_PROTOCOL_CONTENT_HASH"
run_results:
  - run_id: "run:template.primary-run"
    started_at: "YYYY-MM-DDTHH:MM:SSZ"
    ended_at: "YYYY-MM-DDTHH:MM:SSZ"
    executor: "REPLACE_WITH_NAMED_EXECUTOR"
    environment_identity: "REPLACE_WITH_FROZEN_ENVIRONMENT_IDENTITY"
    random_seed: "REPLACE_WITH_SEED_OR_EXPLICIT_NOT_APPLICABLE"
    sample_selection: "REPLACE_WITH_SAMPLE_SELECTION_RULE"
    result: "not-run"
    actual_observations: []
    deviations: []
    evidence_references: []
independent_reproduction_results:
  - run_id: "run:template.independent-reproduction"
    started_at: "YYYY-MM-DDTHH:MM:SSZ"
    ended_at: "YYYY-MM-DDTHH:MM:SSZ"
    executor: "REPLACE_WITH_DIFFERENT_NAMED_EXECUTOR"
    environment_identity: "REPLACE_WITH_EQUIVALENT_FROZEN_ENVIRONMENT_IDENTITY"
    random_seed: "REPLACE_WITH_SEED_OR_EXPLICIT_NOT_APPLICABLE"
    sample_selection: "REPLACE_WITH_SAMPLE_SELECTION_RULE"
    result: "not-run"
    actual_observations: []
    deviations: []
    evidence_references: []
first_failure:
  present: false
  run_id: null
  captured_at: null
  observation_surfaces: []
  correlation_ids: []
  evidence_references: []
  preserved_before_retry: false
```

## ART-P5-EFFECTS 副作用与处置包

```yaml
artifact_type: "ART-P5-EFFECTS"
artifact_id: "artifact:p5-effects.template-replace-me"
content_hash: "sha256:REPLACE_WITH_EFFECTS_CONTENT_HASH"
status: "draft"
created_at: "YYYY-MM-DDTHH:MM:SSZ"
owner: "REPLACE_WITH_NAMED_EFFECTS_OWNER"
product_version: "REPLACE_WITH_IMMUTABLE_PRODUCT_VERSION"
scope_or_module: "REPLACE_WITH_QUALIFIED_SCOPE_OR_MODULE_ID"
evidence_references: []
method_definitions: []
evidence_method_entries: []
protocol_reference:
  protocol_id: "artifact:p5-protocol.template-replace-me"
  protocol_content_hash: "sha256:REPLACE_WITH_PROTOCOL_CONTENT_HASH"
side_effect_records:
  - effect_id: "effect:template.replace-me"
    kind: "REPLACE_WITH_WRITE_OR_EGRESS_OR_OTHER_EFFECT_KIND"
    target: "REPLACE_WITH_AFFECTED_TARGET"
    occurred: false
    reversal_action: "REPLACE_WITH_REVERSAL_ACTION_OR_EXPLICIT_NONE"
    recovery_validation: "REPLACE_WITH_RECOVERY_VALIDATION"
    owner: "REPLACE_WITH_NAMED_EFFECT_OWNER"
    disposition: "not-created"
    disposition_proof_references: []
cleanup:
  steps:
    - step_id: "cleanup-step:template.replace-me"
      action: "REPLACE_WITH_REVERSE_ORDER_CLEANUP_ACTION"
      verification: "REPLACE_WITH_POST_ACTION_VERIFICATION"
  result: "not-run"
  disposition_proof_references: []
residual_checks:
  checks:
    - surface: "REPLACE_WITH_AUTHORIZED_SEARCH_SURFACE"
      sentinel_query: "REPLACE_WITH_SENTINEL_LOOKUP"
      expected: "REPLACE_WITH_ALLOWED_RESIDUAL_OR_NONE"
      actual: "REPLACE_AFTER_CHECK"
      difference: "REPLACE_WITH_DIFFERENCE_OR_EXPLICIT_NONE"
  result: "not-run"
  evidence_references: []
```

方法成熟度只评价取证、建模或验证方法及其证据基础，不评价目标产品事实；产品主张必须在主张—证据记录中使用 `claim_status`、`confidence` 和支持/反驳证据引用。

每个 YAML 块的 `status` 都是该产物自己的生命周期状态；只有 PROTOCOL 保存 `claim_references`，且 `target_claim_references` 必须是它的子集；实验支持的主张真值仍只在主张—证据记录维护。三个产物各自保存 `method_definitions` 与 `evidence_method_entries`，`method_maturity` 只评价对应方法。某产物没有 evidence 时两个数组可以为空；只要 `evidence_references` 非空，每个 evidence 必须恰好映射一次，mapping 的 evidence 与 method 集合必须分别和本产物声明的 evidence 与 method 双向闭合。

`template.replace-me` 仅演示引用闭合；发布前必须替换为已登记 ID，或同时删除 evidence、method 与映射示例。

三个 YAML 块是三个独立产物，分别拥有 `artifact_id`、`content_hash`、`status`、`created_at` 和 `owner`，可以单独签名、替换或撤回。计算 content hash 时排除 `content_hash` 包络字段，并对其余规范化 YAML 负载计算 SHA-256，避免自引用哈希。

PROTOCOL 在首次执行前完成并置为 `frozen`。协议一旦冻结，运行结果、首次失败、副作用、清理或残留检查都不得回写协议；协议变化必须创建新 `artifact_id` 与 hash。RESULT 与 EFFECTS 只能引用精确的 `protocol_id` 和 `protocol_content_hash`，不得复制可被事后改写的协议字段。

RESULT 和 EFFECTS 的 `product_version` 与 `scope_or_module` 必须逐字等于 PROTOCOL；上下文变化必须创建并冻结新协议，不能在派生产物中另写版本或范围。run、independent reproduction、first failure、effect、cleanup 和 residual check 的内层证据引用必须解析到所属产物顶层的 `evidence_references`；每个产物的顶层 evidence 也必须由该产物自己的 evidence-method mapping 完整解释。`first_failure.run_id` 必须解析到本 RESULT 已声明的某个运行或独立复现 run ID，未发生首次失败时保持 `null`。

业务 run 为 `passed` 而 cleanup 为 `failed` 是必须如实保存的有效审计事实，不能由实验记录 schema 拒绝或改写；该组合也不会自动产生 G5 `pass`。G5 仍由覆盖与门禁规则依据独立的不可变输入判定，清理失败须作为未满足条件或缺口进入其评审。

## 不可变环境与授权

- 在 PROTOCOL 执行前写入 `protocol_frozen_at`，固定 environment identity、构建、部署、运行时、依赖、配置哈希、功能开关、时区、角色、测试账号和输入指纹。
- 分别记录 source、artifact 与 clone fingerprint；来源不可用或无克隆时显式说明，不用空字符串冒充相同身份。
- 引用当前 `ART-G0-AUTH` 的 `pass`，按 read、write、fault-injection、egress、cleanup 分别给授权判定和来源；默认 `not-authorized`，不得由读取权限推定其他动作。
- 固定 cost、rate、blast radius 上限；任一上限或授权来源不明确时停止相应动作。

## 前置状态指纹与唯一哨兵

- 保存 pre-state fingerprint：对象状态、关键只读快照、队列、缓存、外部连接、权限和资源基线。
- 使用不含个人信息或秘密的 sentinel 贯穿界面、网络、日志、数据、消息、文件和清理记录。
- `recovery` 同时写明 recovery point、具名 owner 和 max restore time；恢复能力未验证时不得进入写入或故障注入。

## 实验步骤与观测点

| step | action/input | expected observation | observation surface | stop condition |
| --- | --- | --- | --- | --- |
| REPLACE_WITH_STEP_NUMBER | REPLACE_WITH_ACTION | REPLACE_WITH_EXPECTATION | REPLACE_WITH_UI_NETWORK_LOG_DATA_OR_OTHER | REPLACE_WITH_STOP_TRIGGER |

每步只改变一个研究 variable，写明 input、wait condition、tool version 和证据捕获位置；协议同时引用 target claims、alternative explanations、forbidden side effects 与预先冻结的 reproduction criteria。未获准的观测面保持缺口。

## 预期与实际观察

- 执行前冻结 expected observations；每个 run result 另填 actual observations、开始/结束时间、执行者、环境身份、随机种子、样本选择、偏差和证据 ID；`ended_at` 不得早于 `started_at`。
- independent reproduction results 与首次执行分列，记录另一执行者是否从同一协议和等价身份复现，而不复制第一次结论。
- 界面、网络、日志、数据库、消息、缓存、文件、通知和外部效应分别记录，不用最终结果覆盖中间状态。

## 首个失败保全

- 在任何自动重试前保存 first failure 的多观察面、关联 ID、时间顺序和当时状态。任一 run 为 `failed` 或 `mixed` 时必须保留非空实际观察和证据，并将 `first_failure.present` 置为 true，且其 run ID 必须指向本 RESULT 中的 failed/mixed run。
- 后续尝试使用新运行序号并链接首错；最终成功不得抹去失败、部分提交或补偿证据。

## 逆序清理与残留检查

- `side_effect_records` 逐项记录实际写入或外发、影响目标、是否发生、逆向动作、恢复验证、责任人、处置状态和证明；不存在副作用也要保留预期项并写 `occurred: false + disposition: not-created`，已发生项只能使用 retained/reversed/deleted 并给出处置证明。
- cleanup 按副作用逆序记录停止外发、下游撤销、队列/缓存处理、业务逆向动作和临时权限撤销，并引用 disposition proof。
- residual checks 用哨兵核对界面、数据、日志、消息、文件、备份可达范围和外部模拟器，并记录结果、差异及证据。
