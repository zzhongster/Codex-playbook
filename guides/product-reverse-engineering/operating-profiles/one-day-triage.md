# 一日分诊运行配置

**证据成熟度：`proposed`**

**适用范围：** 用一个工作日回答“是否值得继续、下一步查什么、主要风险在哪里”，适用于刚取得合法访问权、信息不完整且需要快速形成有界决策输入的产品逆向项目。

## 目的

一日分诊交付的是有界产品/架构草图、一个代表旅程、主要未知、风险和下一阶段区间估算。它帮助负责人决定停止、补授权、进入一周评估或启动完整项目，不负责宣称产品、架构、角色或旅程已经完整。

时间盒只压缩本轮范围：授权、证据、主张和人工复核标准继续继承[授权、隐私与安全](../core/authorization-privacy-and-safety.md)、[证据与置信度](../core/evidence-and-confidence.md)及[覆盖、质量与冻结](../core/coverage-quality-and-freeze.md)。

## 进入条件

开始前必须有不可变 `ART-P0-AUTH`，且当前 `ART-G0-AUTH.verdict` 为 `pass`；同时建立本轮 `ART-P1-BASELINE`，绑定产品版本、配置、账号/角色、环境、数据和允许动作。访问轨道必须从黑盒、灰盒或白盒中显式选择，访问面变化即停止并重新授权。

选择运行分支时，每个读取、写入、外联、故障注入和清理动作仍需逐项授权。无法安全运行时只能选择获批静态分支，并产出 `ART-P5-STATIC`、`ART-P5-RUNTIME-GAP` 和 `ART-P5-STATIC-ACCEPTANCE`；一天快结束不是运行授权。

## 时间盒

硬时间盒为一个工作日。到点即停止扩展范围，把未完成项留在未知和风险队列，不以加班、跳过 G0、复用过期环境身份或降低证据门槛换取“看起来完成”。

建议按 15%/20%/30%/20%/15% 分配给授权与边界、表面盘点、代表旅程、未知与风险、退出评审；负责人可以在不改变必需输出和安全边界的前提下调整时段。

## 角色

`accountable-human` 对目的、范围、风险接受和退出决定负责；`reverse-engineering-lead` 组织有界追踪；`evidence-custodian` 固定身份、证据和引用；`domain-reviewer` 区分业务术语与实现推断。一个人可以兼任多个角色，但 Agent 不得替代必须由人承担的批准或领域确认。

## 日程

1. 验证 G0、固定 P1 范围和轨道，只允许后续步骤消费已登记输入。
2. 盘点有界产品表面和架构形状，明确看到什么、从何处看到，以及什么仍不可见。
3. 选择一条风险代表性旅程，建立界面/入口—规则—实现—数据/集成—结果的类型化证据链；链路可保留明确缺口。
4. 将冲突、未知、安全与决策风险排队，不把未知并入已覆盖分子。
5. 核对五项输出并由负责人给出退出判定和下一阶段区间估算。

## 必需输出

- **有界产品/架构草图：** 标出版本、范围、证据面、产品表面与仅被证据支持的架构形状。
- **代表旅程追踪：** 至少一条风险排序后的旅程，保留类型化链接、证据引用和可见/内部主张边界。
- **主要未知：** 记录开放问题、缺少的证据及其决策影响。
- **风险登记：** 同时覆盖授权/安全风险、产品/技术风险、责任人和下一动作。
- **下一阶段估算：** 给区间而非伪精确点值，列出依赖、假设和推荐配置。

任何一项缺少版本/范围/证据绑定，或用推断替代缺失观察，都视为未完成而不是“先通过”。

## 允许主张

本配置不创建新状态。产品主张只能使用指南既有状态，并绑定具体产品版本、范围与证据引用；状态提升只由新增证据和相应人工评审触发，时间消耗、文件数量或 Agent 结论不会提升状态。

可见行为与内部实现必须拆成不同主张。静态分支最高支持有对应源码/制品证据的 `statically-supported`；缺少运行证据的行为不得标为 `runtime-confirmed`。

## 禁止完整性主张

禁止声称“完整产品”“完整架构”“全部旅程已覆盖”“零未知”“已经可直接重写”或“静态结构等同运行行为”。一日结果必须在标题、摘要、退出门禁和估算中保持“分诊、抽样、有界、未完成”的限定。

## 退出门禁

`PROFILE-D1-EXIT` 只核对五项必需输出是否存在、互相可追踪并显式列出缺口。通过表示这次分诊可以支持下一步决策，不表示 G1–G7 已通过，也不表示整产品完整、架构完整或达到重写就绪。

若 G0 不再有效、输出失去输入身份、代表旅程没有证据引用、未知被算作覆盖，或下一阶段估算没有依赖与区间，则退出判定为 `fail`；时间盒结束不能把失败改成通过。

## 升级处理

授权漂移、环境身份不匹配或不安全副作用要求立即停止，重新取得 G0 `pass` 后才能恢复。证据冲突冻结受影响主张并交给证据负责人/领域评审；时间耗尽而高风险仍开放时，收窄结论、登记风险并由负责人选择停止、一周评估或完整项目。

若发现范围大于一天可审查能力，不继续横向扫面；优先保持代表链路可审计，把其余对象加入带来源的初步分母和未知队列。

## 运行契约

以下 YAML 是本配置的机器可读权威；上文用于操作解释，不得单独改写其安全语义。

```yaml
profile_id: one-day-triage
purpose: Produce bounded decision input for stop, authorize, assess, or plan decisions without claiming completeness.
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
  duration: 1 working day
  hard_stop: true
  narrows_scope_only: true
  reduces_authorization_boundary: false
  reduces_evidence_standard: false
roles:
  - role_id: accountable-human
    human_required: true
    accountabilities: [purpose-and-scope, risk-acceptance, exit-decision]
  - role_id: reverse-engineering-lead
    human_required: false
    accountabilities: [bounded-inventory, representative-trace, estimate]
  - role_id: evidence-custodian
    human_required: false
    accountabilities: [identity-binding, evidence-index, provenance]
  - role_id: domain-reviewer
    human_required: true
    accountabilities: [term-review, business-claim-boundary]
  - role_id: ai-agent
    human_required: false
    accountabilities: [authorized-retrieval, draft-links, validation]
schedule:
  - sequence: 1
    step_id: d1-authorize-bound
    depends_on: []
    time_window: 00%-15%
    activity: Verify authorization and freeze a bounded baseline.
    inputs: [ART-P0-AUTH]
    outputs: [artifact:triage.authorization-scope-record]
    gate_effect: verify
  - sequence: 2
    step_id: d1-map-surface
    depends_on: [d1-authorize-bound]
    time_window: 15%-35%
    activity: Sketch the bounded product surface and evidence-supported architecture shape.
    inputs: [ART-P1-BASELINE]
    outputs: [artifact:triage.bounded-product-architecture-sketch]
    gate_effect: keep-pending
  - sequence: 3
    step_id: d1-trace-journey
    depends_on: [d1-map-surface]
    time_window: 35%-65%
    activity: Trace one risk-ranked representative journey and retain gaps.
    inputs: [artifact:triage.bounded-product-architecture-sketch]
    outputs: [artifact:triage.representative-journey-trace]
    gate_effect: keep-pending
  - sequence: 4
    step_id: d1-rank-unknowns-risks
    depends_on: [d1-trace-journey]
    time_window: 65%-85%
    activity: Rank unknowns and risks without counting them as coverage.
    inputs: [artifact:triage.representative-journey-trace]
    outputs: [artifact:triage.major-unknowns, artifact:triage.risk-register]
    gate_effect: review
  - sequence: 5
    step_id: d1-exit-estimate
    depends_on: [d1-rank-unknowns-risks]
    time_window: 85%-100%
    activity: Review all outputs and issue a range estimate for the next phase.
    inputs: [artifact:triage.major-unknowns, artifact:triage.risk-register]
    outputs: [artifact:triage.next-phase-estimate]
    gate_effect: pass-or-fail
required_outputs:
  - output_id: artifact:triage.bounded-product-architecture-sketch
    content_contract: [bounded-product-surface, bounded-architecture-shape, version-scope-evidence-bindings]
    incomplete_when: [unbounded-scope, missing-version, unsupported-topology]
  - output_id: artifact:triage.representative-journey-trace
    content_contract: [one-risk-ranked-representative-journey, typed-links-and-evidence, visible-and-implementation-claim-separation]
    incomplete_when: [no-selection-rationale, dangling-evidence, hidden-claim-overreach]
  - output_id: artifact:triage.major-unknowns
    content_contract: [ranked-open-questions, missing-evidence, decision-impact]
    incomplete_when: [unknowns-folded-into-covered, missing-owner]
  - output_id: artifact:triage.risk-register
    content_contract: [authorization-and-safety-risks, product-and-technical-risks, owner-and-next-action]
    incomplete_when: [risk-without-owner, risk-without-next-action]
  - output_id: artifact:triage.next-phase-estimate
    content_contract: [range-not-point-estimate, assumptions-and-dependencies, recommended-profile]
    incomplete_when: [single-point-certainty, hidden-dependencies]
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
    reason: A one-day bounded sample cannot establish the full denominator.
  - claim_id: zero-unknowns
    reason: Unobserved and unresolved units remain explicit unknowns.
  - claim_id: static-equals-runtime
    reason: Static evidence does not prove deployed runtime behavior.
  - claim_id: complete-architecture
    reason: The sketch only covers the selected evidence boundary.
  - claim_id: all-journeys-covered
    reason: One representative journey is not the journey population.
  - claim_id: rewrite-ready
    reason: Triage does not complete semantic, coverage, and freeze gates.
exit_gate:
  gate_id: PROFILE-D1-EXIT
  required_predecessor_gates: [G0]
  pass_criteria:
    - artifact:triage.bounded-product-architecture-sketch
    - artifact:triage.representative-journey-trace
    - artifact:triage.major-unknowns
    - artifact:triage.risk-register
    - artifact:triage.next-phase-estimate
  fail_conditions: [invalid-G0, unbound-input-identity, missing-required-output, hidden-unknown, unsupported-overclaim]
  does_not_imply: [G1-through-G7-pass, whole-product-completeness, rewrite-readiness]
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
    resume_condition: Recovery completes and a revised action boundary receives G0 pass.
    owner: accountable-human
  - trigger: evidence-conflict
    action: hold-claim-and-review
    resume_condition: Conflict is preserved and reviewed or remains explicitly conflicting.
    owner: domain-reviewer
  - trigger: timebox-exhausted-with-open-risk
    action: stop-expand-scope
    resume_condition: Owner accepts a bounded exit or authorizes the next profile.
    owner: accountable-human
  - trigger: more-depth-authorized
    action: start-one-week-assessment-or-full-program
    resume_condition: A new profile charter binds its own scope, baseline, outputs, and current G0 pass.
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
