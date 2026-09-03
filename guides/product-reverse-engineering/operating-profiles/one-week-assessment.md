# 一周评估运行配置

**证据成熟度：`proposed`**

**适用范围：** 用五个工作日建立可估算的初步分母、代表角色与核心旅程、高风险纵向切片和受控验证结果，为是否启动完整项目及其分波计划提供输入。

## 目的

一周评估比一日分诊扩大证据面和代表性，但仍是风险抽样而不是完整逆向。其核心问题是：已知范围怎样计算、哪些角色/旅程最能代表产品、哪些高风险链路已获证据、哪些实验可以合法安全执行、完整项目需要多少阶段与资源。

交付必须同时呈现已验证、冲突、未知和排除项，并以[端到端工作流](../core/end-to-end-workflow.md)和[覆盖、质量与冻结](../core/coverage-quality-and-freeze.md)的既有语义为准。

## 进入条件

当前不可变 `ART-P0-AUTH` 与 `ART-G0-AUTH pass` 是硬入口；`ART-P1-BASELINE` 必须绑定版本、配置、角色、环境、数据和动作。团队显式选择访问轨道与运行/获批静态分支，不能因为只有一周就扩大账号、读取数据、外联或写入权限。

若从一日分诊升级，分诊产物只是候选输入，必须重新核验哈希和适用范围；若授权或版本已变，先生成新授权/基线记录，不能沿用旧 G0 判定。

## 时间盒

硬时间盒为五个工作日。日程以依赖关系而不是“每天必须得出肯定结论”为约束：证据不足时保留未知、降低主张状态或使退出门禁失败。

时间盒只限制抽样规模，不降低证据标准、不跳过人工决定、不把静态验证改称运行确认，也不允许在第五天自动冻结未审查输出。

## 角色

`accountable-human` 批准范围、实验和退出；`reverse-engineering-lead` 维护风险优先级、切片和估算；`evidence-custodian` 维护输入身份、证据索引与可复算覆盖；`domain-reviewer` 审核代表性、业务语义与冲突。Agent 可做获准检索、链接候选和结构校验，但不得自行批准动作、接受风险或给业务主张作最终确认。

同一人可以兼任角色，但每项人工决定仍要记录实际责任人，不能把角色空缺隐藏在通用团队名称下。

## 日程

1. **第 1 日：** 验证 G0/P1，建立九类初步分母、来源、排除规则和未知单位。
2. **第 2 日：** 依据风险和业务影响选择代表角色与核心旅程，记录没有被选择的区域。
3. **第 3 日：** 建立至少两条高风险纵向切片，跨越可见表面、入口、规则、实现、数据/集成和结果。
4. **第 4 日：** 对逐项获准、已冻结协议的有界实验执行或复核；不能运行时只生成明确的未执行记录和获批静态分支缺口产物。
5. **第 5 日：** 重算初步覆盖、列出未验证区，按 phase/wave 给出完整项目区间估算并执行退出评审。

依赖未满足时后续日程保持 `pending`；日历推进本身不能替代输入、产物或门禁。

## 必需输出

- **初步分母：** 覆盖角色、产品表面、旅程、能力、规则、数据、集成、运行场景和配置/版本九维，并记录来源、排除规则、未知单位。
- **代表角色与核心旅程：** 给出风险抽样、选择理由和未覆盖边界。
- **多条高风险纵向切片：** 至少两条，使用类型化链接并保留冲突与未解析缺口。
- **获授权有界实验台账：** 每个动作有授权绑定；记录已执行结果，或明确“未执行”及静态分支/运行缺口产物。
- **完整项目估算：** 给 phase/wave 区间、人员/环境依赖和风险余量，不给无假设的单点承诺。
- **未验证区域：** 将未验证分母单位、主张上限和建议证据工作显式排队。

## 允许主张

允许使用统一主张状态，但每条主张都必须绑定版本、范围和证据。代表性只说明抽样理由，不把样本结论外推到未检查角色、租户、套餐、配置或失败路径。

运行主张要求同版本运行证据和授权场景；获批静态分支的最高状态仍是 `statically-supported`。领域确认只能由有责任的领域评审基于可定位主张完成，不能由评估者人数或一周时长自动生成。

## 禁止完整性主张

禁止声称“完整产品”“最终分母”“所有角色/旅程已覆盖”“全部高风险切片已确认”“零未知”“静态等于运行”或“无需完整项目”。一周结果是 preliminary assessment；即使所有计划样本完成，也只能说明计划样本的覆盖情况。

禁止用百分比隐藏小分母、未知、冲突或排除项。跨维总览必须保留各维单位和计算规则，不能把不同对象直接相加成伪精确总分。

## 退出门禁

`PROFILE-W1-EXIT` 要求六项必需输出均有身份、证据和缺口，可由相同输入重算；通过只表示已经形成完整项目的可审查决策输入，不表示 G1–G7 全部通过或产品已冻结。

G0 无效、分母不可计算、代表样本无选择理由、纵向切片少于两条、实验动作未逐项授权、未执行实验被写成运行成功、估算缺依赖或未验证区被删除，均导致 `fail`。

## 升级处理

授权漂移、环境身份不匹配或不安全副作用立即停止，只有修复/恢复且新 G0 `pass` 后才能恢复。证据冲突保持为 `conflicting` 并交领域和证据责任人处理；时间耗尽但高风险开放时，停止扩展、发布有界失败/缺口结论，并由负责人决定补充评估或完整项目。

若初步分母快速增长超过审查能力，按业务域、角色/租户、运行身份或证据面拆成候选 cluster，记录父分母与子分母关系，留给完整项目执行正式拆分和冻结。

## 运行契约

以下 YAML 是本配置的机器可读权威；上文用于操作解释，不得单独改写其安全语义。

```yaml
profile_id: one-week-assessment
purpose: Build preliminary denominators and representative high-risk evidence for a bounded full-program decision.
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
  duration: 5 working days
  hard_stop: true
  narrows_scope_only: true
  reduces_authorization_boundary: false
  reduces_evidence_standard: false
roles:
  - role_id: accountable-human
    human_required: true
    accountabilities: [scope-and-experiment-approval, risk-acceptance, exit-decision]
  - role_id: reverse-engineering-lead
    human_required: false
    accountabilities: [risk-sampling, vertical-slices, program-estimate]
  - role_id: evidence-custodian
    human_required: false
    accountabilities: [identity-binding, denominator-accounting, evidence-provenance]
  - role_id: domain-reviewer
    human_required: true
    accountabilities: [representativeness-review, semantic-review, conflict-review]
  - role_id: ai-agent
    human_required: false
    accountabilities: [authorized-retrieval, candidate-links, deterministic-validation]
schedule:
  - sequence: 1
    step_id: w1-baseline-denominator
    depends_on: []
    time_window: day-1
    activity: Verify G0 and build a sourced preliminary nine-dimension denominator.
    inputs: [ART-P0-AUTH, ART-P1-BASELINE]
    outputs: [artifact:assessment.preliminary-denominator]
    gate_effect: verify
  - sequence: 2
    step_id: w1-select-representatives
    depends_on: [w1-baseline-denominator]
    time_window: day-2
    activity: Select representative roles and core journeys by explicit risk criteria.
    inputs: [artifact:assessment.preliminary-denominator]
    outputs: [artifact:assessment.representative-roles-core-journeys]
    gate_effect: keep-pending
  - sequence: 3
    step_id: w1-trace-high-risk-slices
    depends_on: [w1-select-representatives]
    time_window: day-3
    activity: Trace at least two high-risk vertical slices and retain conflicts and gaps.
    inputs: [artifact:assessment.representative-roles-core-journeys]
    outputs: [artifact:assessment.high-risk-vertical-slices]
    gate_effect: keep-pending
  - sequence: 4
    step_id: w1-authorize-validate
    depends_on: [w1-trace-high-risk-slices]
    time_window: day-4
    activity: Execute only individually authorized bounded experiments or record approved-static non-execution and gaps.
    inputs: [artifact:assessment.high-risk-vertical-slices]
    outputs: [artifact:assessment.authorized-experiment-ledger]
    gate_effect: review
  - sequence: 5
    step_id: w1-audit-estimate-exit
    depends_on: [w1-authorize-validate]
    time_window: day-5
    activity: Recalculate preliminary coverage, expose unverified areas, estimate the full program, and review exit.
    inputs: [artifact:assessment.preliminary-denominator, artifact:assessment.authorized-experiment-ledger]
    outputs: [artifact:assessment.unverified-areas, artifact:assessment.full-program-estimate]
    gate_effect: pass-or-fail
required_outputs:
  - output_id: artifact:assessment.preliminary-denominator
    content_contract: [nine-dimension-preliminary-denominator, source-and-exclusion-rules, unknown-units]
    incomplete_when: [dimension-missing, source-missing, unknown-folded-into-covered]
  - output_id: artifact:assessment.representative-roles-core-journeys
    content_contract: [risk-based-role-sample, core-journey-sample, selection-rationale]
    incomplete_when: [selection-rationale-missing, unselected-boundary-hidden]
  - output_id: artifact:assessment.high-risk-vertical-slices
    content_contract: [at-least-two-risk-ranked-slices, typed-end-to-end-links, unresolved-gaps]
    incomplete_when: [fewer-than-two-slices, dangling-evidence, gaps-deleted]
  - output_id: artifact:assessment.authorized-experiment-ledger
    content_contract: [per-action-authorization, executed-or-explicitly-not-executed, results-or-static-gap-artifacts]
    incomplete_when: [action-authorization-missing, non-execution-hidden, runtime-overclaim]
  - output_id: artifact:assessment.full-program-estimate
    content_contract: [phase-and-wave-range-estimates, staffing-and-environment-dependencies, risk-contingency]
    incomplete_when: [single-point-certainty, phase-missing, dependency-hidden]
  - output_id: artifact:assessment.unverified-areas
    content_contract: [unverified-denominator-units, claim-ceilings, recommended-evidence-work]
    incomplete_when: [unknowns-omitted, claim-ceiling-omitted]
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
    reason: The assessment uses representative sampling and a preliminary denominator.
  - claim_id: zero-unknowns
    reason: Unverified denominator units remain explicit unknowns.
  - claim_id: static-equals-runtime
    reason: Approved static validation cannot prove deployed behavior.
  - claim_id: denominator-final
    reason: Discovery and exclusions have not completed full-program review.
  - claim_id: all-roles-and-journeys-covered
    reason: Representative roles and journeys are not the full population.
  - claim_id: all-high-risk-slices-confirmed
    reason: Selected slices can contain static ceilings, conflicts, and gaps.
  - claim_id: full-program-unnecessary
    reason: An assessment estimates later work rather than completing it.
exit_gate:
  gate_id: PROFILE-W1-EXIT
  required_predecessor_gates: [G0]
  pass_criteria:
    - artifact:assessment.preliminary-denominator
    - artifact:assessment.representative-roles-core-journeys
    - artifact:assessment.high-risk-vertical-slices
    - artifact:assessment.authorized-experiment-ledger
    - artifact:assessment.full-program-estimate
    - artifact:assessment.unverified-areas
  fail_conditions: [invalid-G0, uncalculable-denominator, fewer-than-two-slices, unauthorized-experiment, hidden-unverified-area]
  does_not_imply: [G1-through-G7-pass, final-denominator, whole-product-completeness]
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
    resume_condition: Recovery completes and revised experiment actions receive G0 pass.
    owner: accountable-human
  - trigger: evidence-conflict
    action: hold-claim-and-review
    resume_condition: Conflict is preserved and reviewed or remains explicitly conflicting.
    owner: domain-reviewer
  - trigger: timebox-exhausted-with-open-risk
    action: stop-expand-scope
    resume_condition: Owner accepts bounded gaps or authorizes additional work.
    owner: accountable-human
  - trigger: full-program-authorized
    action: start-full-program
    resume_condition: The full-program charter binds waves, resources, outputs, and current G0 pass.
    owner: accountable-human
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
```
