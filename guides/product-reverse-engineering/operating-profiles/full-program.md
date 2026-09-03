# 完整逆向项目运行配置

**证据成熟度：`proposed`**

**适用范围：** 用依赖有序的分波执行 Phase 0–9，建立可复算覆盖、可审查业务语义、运行或获批静态验证、目的专用交付及可重建冻结，并持续处理版本增量。

## 目的

完整项目把逆向工作从风险抽样推进到按显式分母、门禁和冻结规则管理的可审计计划。它支持重写/迁移/替换、收购尽调和竞品研究等决策目的，但不会把“完整项目”这个名称当成产品绝对完整性的证据。

项目以[端到端工作流](../core/end-to-end-workflow.md)的 Phase 0–9、[覆盖、质量与冻结](../core/coverage-quality-and-freeze.md)的 G0–G7 及[人机协作](../core/human-agent-collaboration.md)的决定权为权威。每一 wave 都消费固定身份输入、输出内容哈希和子摘要，父摘要不复制不可追踪结论。

## 进入条件

必须先获得不可变 `ART-P0-AUTH` 和当前 `ART-G0-AUTH pass`，再冻结 `ART-P1-BASELINE`。授权、产品版本、构建/部署身份、账号/角色、环境、数据或动作变化时，受影响工作立即停止，并用新记录重新授权和基线化。

访问轨道和运行/获批静态分支按证据面选择。运行不是默认权限；非运行也不是免验证：静态分支必须持续携带 `ART-P5-STATIC`、`ART-P5-RUNTIME-GAP` 与 `ART-P5-STATIC-ACCEPTANCE`，并保持运行缺口可见。

## 时间盒

完整项目采用 phase-and-risk-driven 规划：每个 wave 有获批的范围、容量、成本与停止点，依赖或门禁不满足时不得靠日历推进。硬停止意味着当授权失效、风险上限触发或批准的 wave 包络耗尽时，停止扩大范围并升级决定。

时间和预算只能改变本次纳入的分母/cluster 或触发后续 wave，不能降低授权边界、证据标准、人工评审要求，也不能自动把未知清零或把候选输出冻结。

## 角色

`accountable-human` 拥有目的、授权、风险接受、范围变化与 G7 发布决定；`reverse-engineering-lead` 管理 waves、依赖和交付；`evidence-custodian` 管理输入/输出哈希、证据和分母；`domain-reviewer` 管理语义、冲突和领域确认。运行实验还必须有环境/恢复责任人；大型项目可以按 cluster 分配子负责人，但父级责任不能下沉给 Agent。

Agent 可执行已授权、输入固定、输出路径受限的任务包和确定性校验。Agent 不得生成评审者身份、签署时间、风险接受或门禁批准，也不得在等待人工决定时自行扩大权限。

## 日程

项目按以下依赖波推进；允许不同独立 cluster 并行，但每个 child 的输入、输出、摘要和门禁必须独立可寻址。

1. **Wave 0 / Phase 0–1：** 授权、任务简报、停止规则、输入身份、九维分母和风险层。
2. **Wave 1 / Phase 2：** 角色、产品表面、场景和候选旅程；G3 保持 `pending`。
3. **Wave 2 / Phase 3：** 技术资产、入口交叉索引和动态盲区，计算 G2。
4. **Wave 3 / Phase 4：** 按风险建立纵向追踪、反证和缺口，补齐 G3 输入。
5. **Wave 4 / Phase 5：** 执行逐项授权的运行实验，或执行获批静态替代验证并保留运行缺口，计算 G5。
6. **Wave 5 / Phase 6：** 综合能力、旅程、状态、规则、权限、语义和不变量，完成人工领域复核并计算 G4。
7. **Wave 6 / Phase 7：** 重算覆盖、处理冲突与 P0/P1 风险，计算 G6。
8. **Wave 7 / Phase 8：** 生成所选目的交付、初始化空增量台账、人工批准 G7，并按无环顺序生成内容、phase/child 摘要、root 摘要和分离式冻结证明。
9. **Wave 8 / Phase 9：** 对新版本做 delta 影响分析，重开受影响门禁、定向重验并发布新版本，不回写旧冻结。

## 必需输出

- **依赖 wave 计划：** 明确 Phase、cluster、前置输入、责任人、容量、停止条件和门禁。
- **Phase 哈希链：** 每阶段保存 `phase_id`、`input_hashes`、`output_hashes`，采用 SHA-256 内容身份。
- **父子摘要：** child 摘要先生成，parent 只消费 child 哈希；摘要自身哈希不进入自身输入。
- **评审节奏：** 每 wave 评审、领域/运行/冻结专门评审及风险触发评审均有责任和触发条件。
- **门禁台账：** 至少显式呈现授权 G0、领域语义 G4、运行/静态分支 G5、覆盖 G6 和冻结/发布 G7。
- **增量台账：** 新记录追加、影响分析、门禁重开和定向复验全部可追踪。
- **目的专用交付：** 重写类输出与竞品研究输出使用不同结构；未选择目的进入排除映射，不混入所选报告。
- **cluster 拆分/冻结台账：** 超出审查容量、混合所有权或分母无界时拆分；child 分母、门禁、哈希和 parent 重建齐全后才冻结。

## 允许主张

产品主张只使用统一状态、置信度和证据引用。`G4 pass` 表示语义模型的必备控制通过，不自动把全部业务结论设为 `domain-confirmed`；`G5 pass` 表示所选验证分支治理通过，不把静态分支变成运行确认；`G7 pass` 表示目的交付可发布，不提升产品真值。

重写交付可以形成 as-is→to-be 追踪、保留/替换决定和验收基线；竞品交付只形成授权范围内的观察、差异、假设、决策启示和未验证边界。两类输出不得互相借用完整性措辞。

## 禁止完整性主张

禁止声称“绝对完整产品”“零未知”“静态等于运行”“所有环境/角色都等价”“冻结后永久正确”或“门禁通过等于业务真理”。分母、排除项和 accepted uncertainty 决定发布边界，而不是项目名称。

任何 cluster 的通过不能外推到 sibling 或 parent 的未覆盖单位；parent 只有在 child 分母闭合、适用门禁通过、child 哈希记录并重建 parent 摘要后，才能纳入当前冻结。

## 退出门禁

完整项目退出使用 G7，并要求 G0–G7 的当前判定、八项必需输出、所选目的交付及分离式冻结证明一致可重建。G7 之前的内容输出、phase/child 摘要与 root 摘要必须先固定，冻结证明最后生成，避免递归哈希。

退出失败条件包括授权失效、任何必需分母不可复算、G5 分支义务缺失、P0/P1 未解决且未有效接受、目的输出混淆、哈希/摘要不闭合或 oversized cluster 未按 child 条件拆分。通过也不表示永远无需 Phase 9。

## 升级处理

授权漂移、环境身份不匹配或不安全副作用立即停止，完成恢复且新 G0 `pass` 后才能恢复。证据冲突冻结受影响主张和输出，由领域/证据责任人审查。wave 包络耗尽且高风险仍开放时，停止扩张，提交范围/预算/风险变更决定。

当 cluster 超出审查容量、混合所有权或无法建立有界分母时，暂停 parent 冻结，按业务域、运行身份、租户/角色、数据所有权或失败边界拆分。每个 child 独立建立分母、门禁和摘要；只有 child 条件齐全并重建 parent 后才能恢复 parent 冻结。

## 运行契约

以下 YAML 是本配置的机器可读权威；上文用于操作解释，不得单独改写其安全语义。

```yaml
profile_id: full-program
purpose: Execute Phase 0 through Phase 9 in dependency-ordered waves with reviewable gates, purpose-specific delivery, and rebuildable freeze identities.
entry_conditions:
  authorization:
    artifact: ART-P0-AUTH
    gate: G0
    verdict: pass
  scope_baseline: ART-P1-BASELINE
  access_track:
    allowed: [black-box, gray-box, white-box]
  execution_branch:
    allowed: [runtime, approved-static]
    approved_static_artifacts:
      - ART-P5-STATIC
      - ART-P5-RUNTIME-GAP
      - ART-P5-STATIC-ACCEPTANCE
timebox:
  duration: phase-and-risk-driven
  hard_stop: true
  narrows_scope_only: true
  reduces_authorization_boundary: false
  reduces_evidence_standard: false
roles:
  - role_id: accountable-human
    human_required: true
    accountabilities: [purpose-and-authorization, risk-and-scope-decisions, G7-release]
  - role_id: reverse-engineering-lead
    human_required: false
    accountabilities: [wave-dependencies, cluster-coordination, purpose-delivery]
  - role_id: evidence-custodian
    human_required: false
    accountabilities: [input-output-hashes, denominator-accounting, evidence-provenance]
  - role_id: domain-reviewer
    human_required: true
    accountabilities: [semantic-review, conflict-review, domain-decisions]
  - role_id: runtime-environment-owner
    human_required: true
    accountabilities: [experiment-environment, recovery, side-effect-review]
  - role_id: ai-agent
    human_required: false
    accountabilities: [authorized-task-packets, candidate-links, deterministic-validation]
schedule:
  - sequence: 1
    step_id: wave-0-authorize-baseline
    depends_on: []
    time_window: phase-0-and-phase-1
    activity: Authorize, bind immutable inputs, define denominators, and approve wave boundaries.
    inputs: [ART-P0-AUTH]
    outputs: [artifact:program.wave-plan, artifact:program.phase-0-1-baseline]
    gate_effect: verify
  - sequence: 2
    step_id: wave-1-product-surface
    depends_on: [wave-0-authorize-baseline]
    time_window: phase-2
    activity: Map roles, product surfaces, scenarios, and journey candidates while G3 remains pending.
    inputs: [ART-P1-BASELINE]
    outputs: [artifact:program.product-surface]
    gate_effect: keep-pending
  - sequence: 3
    step_id: wave-2-architecture-assets
    depends_on: [wave-1-product-surface]
    time_window: phase-3
    activity: Map technical assets, entry points, dynamic boundaries, and phase input/output identity.
    inputs: [artifact:program.product-surface]
    outputs: [artifact:program.technical-atlas, artifact:program.phase-hash-chain]
    gate_effect: pass-or-fail
  - sequence: 4
    step_id: wave-3-vertical-traces
    depends_on: [wave-2-architecture-assets]
    time_window: phase-4
    activity: Build risk-ranked vertical traces, counterevidence, gaps, and child summaries.
    inputs: [artifact:program.product-surface, artifact:program.technical-atlas]
    outputs: [artifact:program.vertical-traces, artifact:program.parent-child-summaries]
    gate_effect: pass-or-fail
  - sequence: 5
    step_id: wave-4-runtime-or-static-validation
    depends_on: [wave-3-vertical-traces]
    time_window: phase-5
    activity: Execute authorized runtime protocols or the approved-static branch and calculate G5.
    inputs: [artifact:program.vertical-traces]
    outputs: [artifact:program.validation-results, artifact:program.gate-ledger]
    gate_effect: pass-or-fail
  - sequence: 6
    step_id: wave-5-domain-synthesis
    depends_on: [wave-4-runtime-or-static-validation]
    time_window: phase-6
    activity: Synthesize product and semantic models and run the domain review for G4.
    inputs: [artifact:program.vertical-traces, artifact:program.validation-results]
    outputs: [artifact:program.semantic-model]
    gate_effect: pass-or-fail
  - sequence: 7
    step_id: wave-6-coverage-conflict
    depends_on: [wave-5-domain-synthesis]
    time_window: phase-7
    activity: Recalculate denominators, resolve or accept conflicts, schedule reviews, and calculate G6.
    inputs: [artifact:program.semantic-model, artifact:program.gate-ledger]
    outputs: [artifact:program.coverage-audit, artifact:program.review-cadence]
    gate_effect: pass-or-fail
  - sequence: 8
    step_id: wave-7-freeze-delivery
    depends_on: [wave-6-coverage-conflict]
    time_window: phase-8
    activity: Produce the selected purpose delivery, initialize the delta ledger, close cluster decisions, calculate G7, and create the detached freeze.
    inputs: [artifact:program.coverage-audit, artifact:program.parent-child-summaries]
    outputs: [artifact:program.purpose-delivery, artifact:program.cluster-split-freeze-ledger, artifact:program.delta-ledger]
    gate_effect: pass-or-fail
  - sequence: 9
    step_id: wave-8-delta-calibration
    depends_on: [wave-7-freeze-delivery]
    time_window: phase-9-and-ongoing
    activity: Append deltas, analyze impact, reopen affected gates, and target revalidation.
    inputs: [artifact:program.purpose-delivery, artifact:program.cluster-split-freeze-ledger]
    outputs: [artifact:program.delta-ledger]
    gate_effect: review
required_outputs:
  - output_id: artifact:program.wave-plan
    content_contract: [dependency-ordered-waves]
    incomplete_when: [missing-phase, missing-dependency, missing-owner-or-stop]
  - output_id: artifact:program.phase-hash-chain
    content_contract: [phase-input-and-output-hashes]
    incomplete_when: [input-hash-missing, output-hash-missing, non-content-identity]
  - output_id: artifact:program.parent-child-summaries
    content_contract: [child-hash-bound-parent-summaries]
    incomplete_when: [child-summary-missing, parent-copies-unbound-claim, recursive-self-hash]
  - output_id: artifact:program.review-cadence
    content_contract: [scheduled-and-risk-triggered-reviews]
    incomplete_when: [review-owner-missing, risk-trigger-missing]
  - output_id: artifact:program.gate-ledger
    content_contract: [domain-runtime-coverage-freeze-verdicts]
    incomplete_when: [G4-missing, G5-missing, G6-missing, G7-missing]
  - output_id: artifact:program.delta-ledger
    content_contract: [append-only-delta-impact-and-revalidation]
    incomplete_when: [history-rewritten, affected-gate-not-reopened, targeted-revalidation-missing]
  - output_id: artifact:program.purpose-delivery
    content_contract: [selected-purpose-specific-delivery-and-exclusion-map]
    incomplete_when: [purpose-not-selected, rewrite-and-competitor-content-mixed, exclusions-hidden]
  - output_id: artifact:program.cluster-split-freeze-ledger
    content_contract: [split-and-child-freeze-decisions]
    incomplete_when: [oversized-cluster-unsplit, child-denominator-unbound, parent-summary-not-rebuilt]
allowed_claims:
  statuses: [observed, statically-supported, runtime-confirmed, domain-confirmed, inferred, conflicting, unsupported, deprecated, superseded]
  required_binding:
    product_version: required
    scope: required
    evidence_references: required
  promotion_rule: evidence-and-review-only
  timebox_effect: none
forbidden_completeness_claims:
  - claim_id: full-product-complete
    reason: Completion is always bounded by named denominators, exclusions, and accepted uncertainty.
  - claim_id: zero-unknowns
    reason: Unknowns remain accounting buckets until evidence resolves them.
  - claim_id: static-equals-runtime
    reason: Approved static work preserves a runtime evidence gap.
  - claim_id: all-environments-and-roles-equivalent
    reason: One deployment or role cannot establish all runtime identities.
  - claim_id: gate-pass-equals-business-truth
    reason: Gates verify process contracts and do not promote every product claim.
  - claim_id: freeze-is-eternal
    reason: Phase 9 deltas can reopen affected gates and create a new freeze.
exit_gate:
  gate_id: G7
  required_predecessor_gates: [G0, G1, G2, G3, G4, G5, G6]
  pass_criteria:
    - artifact:program.wave-plan
    - artifact:program.phase-hash-chain
    - artifact:program.parent-child-summaries
    - artifact:program.review-cadence
    - artifact:program.gate-ledger
    - artifact:program.delta-ledger
    - artifact:program.purpose-delivery
    - artifact:program.cluster-split-freeze-ledger
  fail_conditions: [invalid-G0, uncalculable-denominator, failed-required-gate, purpose-output-mixed, hash-or-summary-cycle, unsafe-cluster-freeze]
  does_not_imply: [eternal-validity, universal-product-completeness, automatic-claim-promotion]
escalation:
  - trigger: authorization-drift
    action: stop
    resume_condition: New ART-P0-AUTH and G0 pass bind the changed scope.
    owner: accountable-human
  - trigger: environment-identity-mismatch
    action: stop
    resume_condition: Corrected environment identity is authorized and G0 passes.
    owner: evidence-custodian
  - trigger: unsafe-write-or-side-effect
    action: stop
    resume_condition: Recovery completes and revised actions receive G0 pass.
    owner: accountable-human
  - trigger: evidence-conflict
    action: hold-claim-and-review
    resume_condition: Conflict is preserved and reviewed or remains explicitly conflicting.
    owner: domain-reviewer
  - trigger: timebox-exhausted-with-open-risk
    action: stop-expand-scope
    resume_condition: Owner approves a new wave envelope or a bounded failed exit.
    owner: accountable-human
  - trigger: oversized-cluster
    action: split-and-hold-parent-freeze
    resume_condition: Child denominators and gates pass, child hashes are recorded, and the parent summary is rebuilt.
    owner: reverse-engineering-lead
inherited_contracts:
  authorization:
    artifact: ART-P0-AUTH
    gate: G0
    verdict: pass
  branches:
    runtime:
      individual_action_authorization_required: true
      runtime_claim_requires_runtime_evidence: true
    approved-static:
      required_artifacts: [ART-P5-STATIC, ART-P5-RUNTIME-GAP, ART-P5-STATIC-ACCEPTANCE]
      claim_ceiling: statically-supported
      forbidden_status: runtime-confirmed
  risk_policy:
    P0: stop-and-escalate-before-release
    P1: resolve-or-valid-written-acceptance
    timebox_can_downgrade: false
  unknown_policy:
    record_unresolved: true
    unknown_never_counts_as_covered: true
  coverage_policy:
    denominators_required: true
    numerator_only_forbidden: true
  freeze_policy:
    append_only: true
    delta_reopens_affected_gates: true
    timebox_never_auto_freezes: true
full_program_controls:
  phase_hashes:
    algorithm: SHA-256
    required_fields: [phase_id, input_hashes, output_hashes]
    generation_order: [content-outputs, phase-summary, root-summary, freeze-attestation]
  parent_child_summaries:
    child_summary_required: true
    parent_inputs_are_child_hashes: true
    self_hash_excluded: true
  review_cadence:
    per_wave: Human owner reviews inputs, outputs, gaps, and gate effects before the next dependent wave.
    domain: Domain reviewers examine Phase 6 semantics and every risk-triggered semantic conflict.
    runtime: Environment owner reviews every Phase 5 protocol, result, side effect, and recovery record.
    freeze: Accountable human reviews G6 inputs, purpose delivery, G7 decision, and detached freeze order.
    risk_triggered: Authorization, P0/P1, conflict, identity, safety, and oversized-cluster triggers add immediate reviews.
  gates:
    authorization: G0
    runtime: G5
    domain: G4
    coverage: G6
    freeze: G7
  delta_handling:
    append_new_records: true
    impact_analysis: true
    reopen_affected_gates: true
    targeted_revalidation: true
  purpose_outputs:
    rewrite: [ART-P8-REWRITE, as-is-to-be-traces, preserve-replace-decisions, acceptance-baseline]
    competitor-research: [ART-P8-COMPETITOR, bounded-observations, differentiators-and-hypotheses, unverified-boundaries]
  cluster_policy:
    oversized_when: [review_capacity_exceeded, mixed_ownership, unbounded_denominator]
    split_by: [business-domain, runtime-identity, tenant-role, data-ownership, failure-boundary]
    freeze_conditions: [child_denominator_bound, child_gates_pass, child_hashes_recorded, parent_summary_rebuilt]
```
