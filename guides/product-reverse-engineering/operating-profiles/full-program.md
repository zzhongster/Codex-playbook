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
8. **Wave 7 / Phase 8：** 先生成目的交付、发布说明、最终 review/delta 内容快照等 Phase 8 内容，再由人签署 `ART-P8-APPROVAL`；随后派生 G7，生成 child/phase 摘要、`ART-P8-ROOT-SUMMARY`、分离式 `ART-P8-FREEZE`，最后单独验证 profile exit。
9. **Wave 8 / Phase 9：** 新版本/证据输入先绑定版本、范围、内容哈希和授权身份；随后依次生成 `ART-P9-DELTA`、影响集合、`pending` gate ledger、分支选择、`ART-P9-REVALIDATION`、复验 verdict ledger、`ART-P9-CALIBRATION`、`ART-P9-LEARNING`，最后发布新的 delta/hash/summary 版本；不回写旧冻结。

## 必需输出

- **依赖 wave 计划：** 明确 Phase、cluster、前置输入、责任人、容量、停止条件和门禁。
- **Phase 哈希索引：** 每个 wave 发布新的不可变 ID，保存 `phase_id`、`input_hashes`、`output_hashes` 和明确替代链；最终 Phase 8 快照在根摘要前固定。
- **父子摘要索引：** 每个 wave 追加独立 child/phase 摘要，parent 只消费既有 child 哈希；摘要自身哈希和未来冻结证明都不进入自身输入。
- **评审节奏：** review cadence 按实际变化发布新版本，每 wave 评审、领域/运行/冻结专门评审及风险触发评审均有责任和触发条件。
- **门禁台账：** 每次门禁变化发布新版本，显式呈现授权 G0、领域语义 G4、运行/静态分支 G5、覆盖 G6 和发布 G7；G7 只消费 Phase 8 内容与既有人类批准，不能消费包含自身的 gate ledger。
- **增量台账：** Phase 8 冻结一个当时快照；Phase 9 以新 ID 追加记录、影响分析、门禁重开和定向复验，不改写冻结引用的旧版本。
- **目的专用交付：** `rewrite`、`migration`、`replacement`、`acquisition-due-diligence`、`competitor-research` 分别映射到核心五类 `ART-P8-*` 输出；所选分支包含自身差异映射，另外四类进入明确排除映射。
- **cluster 拆分/冻结台账：** 超出审查容量、混合所有权或分母无界时拆分；child 分母、门禁、哈希和 parent 重建齐全后才冻结。
- **单向终局产物：** `ART-P8-RELEASE`、`ART-P8-APPROVAL`、`ART-G7-RELEASE`、最终 child/phase 摘要、`ART-P8-ROOT-SUMMARY`、`ART-P8-FREEZE` 和 profile-exit 验证均有独立 ID 与单向依赖。

机器契约中的 `artifact_dag` 是追加式生命周期注册表：`replaced_by` 关系只在后继版本存在后作为独立关系登记，不回写旧产物的已冻结内容；真正的 `inputs` 只能指向已经存在的外部输入或较早产物。重复 concept 必须通过成对替代关系或 parent 链连接，不能复用同一 artifact ID。

`selected_goal` 必须从 Phase 0 已批准的不可变 `ART-P0-BRIEF.approved_primary_goal` 复制并校验其哈希；下方可执行示例取 `rewrite`。五个条件化 `ART-P8-*` 节点都直接引用该 brief 并进入 schedule/DAG，但恰好一个标记 `selected` 并承载 purpose 内容，另外四个只能标记 `excluded`、生成排除/差异映射，禁止伪造未选择目的的业务内容。任何激活切换都必须先有匹配的上游批准 brief；选中的核心产物先完成，`purpose-delivery` 必须直接引用它和四个排除映射，之后 `ART-P8-APPROVAL` 与 G7 均直接引用选中产物，形成可验证主链。

Phase 9 不是四个布尔开关。`ART-P9-EVIDENCE-INPUT` 是不可变外部输入，必须携带版本、范围、SHA-256 内容哈希和授权身份；`ART-P9-DELTA` 必须同时直接消费它和旧 freeze。影响选择确定最小重跑集合后，先发布受影响门禁为 `pending` 的 ledger，再执行分支选择；`ART-P9-REVALIDATION` 必须消费该 pending ledger，完成后才发布 post-revalidation verdict ledger，禁止先复验后补 pending。

分支选择器恰好激活一个分支。运行分支直接绑定当前 `ART-P0-AUTH`、当前且 `pass` 的 `ART-G0-AUTH` 和逐动作授权；获批静态分支直接绑定 `ART-P5-STATIC`、`ART-P5-RUNTIME-GAP`、`ART-P5-STATIC-ACCEPTANCE`、`ART-G5-RUNTIME` 与有效接受决定，最高为 `statically-supported`，不得生成 `runtime-confirmed`。schedule 的 `conditional_inputs`、选择器 DAG 节点和复验节点必须引用相同的当前激活输入，不能只在说明文字里声明分支。`ART-P9-CALIBRATION` 对照先前预测/置信度和实证结果，`ART-P9-LEARNING` 只形成方法修订与成熟度候选，不直接修改产品主张真值，也不因单项目成功提升成熟度；之后才生成新的 delta/hash/summary 快照。

## 允许主张

产品主张只使用统一状态、置信度和证据引用。`G4 pass` 表示语义模型的必备控制通过，不自动把全部业务结论设为 `domain-confirmed`；`G5 pass` 表示所选验证分支治理通过，不把静态分支变成运行确认；`G7 pass` 表示目的交付可发布，不提升产品真值。

重写形成 as-is→to-be 与保留/纠正/舍弃决定；迁移形成身份、字段、状态、历史、切换和回退连续性；替换形成能力适配、差距、变通和退出成本；收购尽调形成事实、权利、整合/交易风险与证据缺口；竞品研究形成同边界观察、差异、假设和战略问题。五类输出各有差异与排除映射，不得混用完成门槛或完整性措辞。

## 禁止完整性主张

禁止声称“绝对完整产品”“零未知”“静态等于运行”“所有环境/角色都等价”“冻结后永久正确”或“门禁通过等于业务真理”。分母、排除项和 accepted uncertainty 决定发布边界，而不是项目名称。

任何 cluster 的通过不能外推到 sibling 或 parent 的未覆盖单位；parent 只有在 child 分母闭合、适用门禁通过、child 哈希记录并重建 parent 摘要后，才能纳入当前冻结。

## 退出门禁

G7 是完整项目的发布门禁，但不是 profile exit 自身。单向终局必须是：Phase 8 内容与不可变 `ART-P8-APPROVAL` → 派生 `ART-G7-RELEASE` → 最终 child/phase 摘要 → `ART-P8-ROOT-SUMMARY` → 分离式 `ART-P8-FREEZE` → `artifact:program.profile-exit-verification.phase8.v1`。profile exit 最后验证 G7、root 和 freeze；没有后向写回，也不把 summary/hash 或 freeze 放进自身输入。

`ART-G7-RELEASE` 只验证 Phase 8 内容、所选 purpose 输出和已经存在的人类批准；它不读取 `artifact:program.gate-ledger.g7.v06`。G7 派生后才创建包含 G7 的 gate-ledger 新版本和最终 phase/hash 摘要，因此不会产生“G7 依赖包含 G7 的 ledger”循环。

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
    activity: Authorize, bind immutable inputs, define denominators, and create the first append-only control versions.
    inputs: [ART-P0-AUTH, ART-P0-BRIEF, ART-P1-BASELINE]
    outputs:
      - artifact:program.wave-plan.v1
      - artifact:program.phase01-baseline.v1
      - artifact:program.review-cadence.wave0.v00
      - artifact:program.delta-ledger.wave0.v00
      - artifact:program.gate-ledger.g01.v00
      - artifact:program.phase-hash-index.wave0.v00
      - artifact:program.phase-summary-index.wave0.v00
    gate_effect: verify
  - sequence: 2
    step_id: wave-1-product-surface
    depends_on: [wave-0-authorize-baseline]
    time_window: phase-2
    activity: Map roles, product surfaces, scenarios, and journey candidates while G3 remains pending.
    inputs: [artifact:program.phase-summary-index.wave0.v00]
    outputs:
      - artifact:program.product-surface.phase2.v1
      - artifact:program.review-cadence.wave1.v01
      - artifact:program.phase-hash-index.wave1.v01
      - artifact:program.phase-summary-index.wave1.v01
    gate_effect: keep-pending
  - sequence: 3
    step_id: wave-2-architecture-assets
    depends_on: [wave-1-product-surface]
    time_window: phase-3
    activity: Map technical assets and publish new gate, hash-index, and summary-index versions.
    inputs: [artifact:program.phase-summary-index.wave1.v01]
    outputs:
      - artifact:program.technical-atlas.phase3.v1
      - artifact:program.gate-ledger.g2.v01
      - artifact:program.phase-hash-index.wave2.v02
      - artifact:program.phase-summary-index.wave2.v02
    gate_effect: pass-or-fail
  - sequence: 4
    step_id: wave-3-vertical-traces
    depends_on: [wave-2-architecture-assets]
    time_window: phase-4
    activity: Build risk-ranked vertical traces and append their independent control versions.
    inputs: [artifact:program.phase-summary-index.wave2.v02]
    outputs:
      - artifact:program.vertical-traces.phase4.v1
      - artifact:program.gate-ledger.g3.v02
      - artifact:program.phase-hash-index.wave3.v03
      - artifact:program.phase-summary-index.wave3.v03
    gate_effect: pass-or-fail
  - sequence: 5
    step_id: wave-4-runtime-or-static-validation
    depends_on: [wave-3-vertical-traces]
    time_window: phase-5
    activity: Execute authorized runtime protocols or the approved-static branch and publish the G5-era control versions.
    inputs: [artifact:program.phase-summary-index.wave3.v03]
    outputs:
      - artifact:program.validation-results.phase5.v1
      - artifact:program.review-cadence.wave4.v02
      - artifact:program.gate-ledger.g5.v03
      - artifact:program.phase-hash-index.wave4.v04
      - artifact:program.phase-summary-index.wave4.v04
    gate_effect: pass-or-fail
  - sequence: 6
    step_id: wave-5-domain-synthesis
    depends_on: [wave-4-runtime-or-static-validation]
    time_window: phase-6
    activity: Synthesize product and semantic models and run the domain review for G4.
    inputs: [artifact:program.phase-summary-index.wave4.v04]
    outputs:
      - artifact:program.semantic-model.phase6.v1
      - artifact:program.gate-ledger.g4.v04
      - artifact:program.phase-hash-index.wave5.v05
      - artifact:program.phase-summary-index.wave5.v05
    gate_effect: pass-or-fail
  - sequence: 7
    step_id: wave-6-coverage-conflict
    depends_on: [wave-5-domain-synthesis]
    time_window: phase-7
    activity: Recalculate denominators, resolve or accept conflicts, and publish the G6-era control versions.
    inputs: [artifact:program.phase-summary-index.wave5.v05]
    outputs:
      - artifact:program.coverage-audit.phase7.v1
      - artifact:program.review-cadence.wave6.v03
      - artifact:program.gate-ledger.g6.v05
      - artifact:program.phase-hash-index.wave6.v06
      - artifact:program.phase-summary-index.wave6.v06
    gate_effect: pass-or-fail
  - sequence: 8
    step_id: wave-7-freeze-delivery
    depends_on: [wave-6-coverage-conflict]
    time_window: phase-8
    activity: Generate Phase 8 content, obtain human approval, derive G7, build final summaries, root, detached freeze, and exit verification in that order.
    inputs:
      - artifact:program.coverage-audit.phase7.v1
      - artifact:program.review-cadence.wave6.v03
      - artifact:program.gate-ledger.g6.v05
      - artifact:program.phase-hash-index.wave6.v06
      - artifact:program.phase-summary-index.wave6.v06
      - artifact:program.delta-ledger.wave0.v00
      - ART-P0-BRIEF
    outputs:
      - artifact:program.cluster-split-freeze-ledger.phase8.v1
      - ART-P8-REWRITE
      - ART-P8-MIGRATION
      - ART-P8-REPLACEMENT
      - ART-P8-DUE-DILIGENCE
      - ART-P8-COMPETITOR
      - artifact:program.purpose-delivery.phase8.v1
      - ART-P8-RELEASE
      - artifact:program.review-cadence.phase8.v04
      - artifact:program.delta-ledger.phase8.v01
      - ART-P8-APPROVAL
      - ART-G7-RELEASE
      - artifact:program.gate-ledger.g7.v06
      - artifact:program.phase-hash-index.phase8.v07
      - artifact:program.phase-summary-index.phase8.v07
      - ART-P8-ROOT-SUMMARY
      - ART-P8-FREEZE
      - artifact:program.profile-exit-verification.phase8.v1
    gate_effect: pass-or-fail
  - sequence: 9
    step_id: wave-8-delta-calibration
    depends_on: [wave-7-freeze-delivery]
    time_window: phase-9-and-ongoing
    activity: Bind new evidence, append a post-freeze delta, mark affected gates pending, execute exactly one governed revalidation branch, publish verdicts, and create new control versions without rewriting the Phase 8 freeze.
    inputs: [ART-P8-FREEZE, artifact:program.profile-exit-verification.phase8.v1, ART-P9-EVIDENCE-INPUT, ART-P0-AUTH, ART-G0-AUTH]
    conditional_inputs:
      selector_artifact: artifact:program.phase9-branch-selection.v1
      selected_branch: runtime
      branch_inputs:
        runtime: [ART-P0-AUTH, ART-G0-AUTH]
        approved-static: [ART-P5-STATIC, ART-P5-RUNTIME-GAP, ART-P5-STATIC-ACCEPTANCE, ART-G5-RUNTIME]
    outputs:
      - ART-P9-DELTA
      - artifact:program.impact-selection.phase9.v1
      - artifact:program.gate-ledger.phase9-pending.v07
      - artifact:program.phase9-branch-selection.v1
      - ART-P9-REVALIDATION
      - artifact:program.gate-ledger.phase9-verdict.v08
      - ART-P9-CALIBRATION
      - ART-P9-LEARNING
      - artifact:program.delta-ledger.phase9.v02
      - artifact:program.phase-hash-index.wave8.v08
      - artifact:program.phase-summary-index.wave8.v08
    gate_effect: review
required_outputs:
  - output_id: artifact:program.wave-plan.v1
    content_contract: [dependency-ordered-waves]
    incomplete_when: [missing-phase, missing-dependency, missing-owner-or-stop]
  - output_id: artifact:program.phase-hash-index.phase8.v07
    content_contract: [phase-input-and-output-hashes]
    incomplete_when: [input-hash-missing, output-hash-missing, future-input, non-content-identity]
  - output_id: artifact:program.phase-summary-index.phase8.v07
    content_contract: [child-hash-bound-parent-summaries]
    incomplete_when: [child-summary-missing, parent-copies-unbound-claim, recursive-self-hash, freeze-input]
  - output_id: artifact:program.review-cadence.phase8.v04
    content_contract: [scheduled-and-risk-triggered-reviews]
    incomplete_when: [review-owner-missing, risk-trigger-missing]
  - output_id: artifact:program.gate-ledger.g7.v06
    content_contract: [domain-runtime-coverage-freeze-verdicts]
    incomplete_when: [G4-missing, G5-missing, G6-missing, G7-missing, G7-self-ledger-cycle]
  - output_id: artifact:program.delta-ledger.phase8.v01
    content_contract: [append-only-delta-impact-and-revalidation]
    incomplete_when: [history-rewritten, affected-gate-not-reopened, targeted-revalidation-missing]
  - output_id: artifact:program.purpose-delivery.phase8.v1
    content_contract: [selected-purpose-specific-delivery-and-exclusion-map, selected-core-purpose-output-id-and-hash]
    incomplete_when: [purpose-not-selected, selected-output-missing, other-purpose-exclusions-hidden]
  - output_id: artifact:program.cluster-split-freeze-ledger.phase8.v1
    content_contract: [split-and-child-freeze-decisions]
    incomplete_when: [oversized-cluster-unsplit, child-denominator-unbound, parent-summary-not-rebuilt]
  - output_id: ART-P8-REWRITE
    content_contract: [selected-delivery-or-explicit-exclusion-map, no-unselected-purpose-content]
    incomplete_when: [activation-missing, selected-content-missing, unselected-content-fabricated]
  - output_id: ART-P8-MIGRATION
    content_contract: [selected-delivery-or-explicit-exclusion-map, no-unselected-purpose-content]
    incomplete_when: [activation-missing, selected-content-missing, unselected-content-fabricated]
  - output_id: ART-P8-REPLACEMENT
    content_contract: [selected-delivery-or-explicit-exclusion-map, no-unselected-purpose-content]
    incomplete_when: [activation-missing, selected-content-missing, unselected-content-fabricated]
  - output_id: ART-P8-DUE-DILIGENCE
    content_contract: [selected-delivery-or-explicit-exclusion-map, no-unselected-purpose-content]
    incomplete_when: [activation-missing, selected-content-missing, unselected-content-fabricated]
  - output_id: ART-P8-COMPETITOR
    content_contract: [selected-delivery-or-explicit-exclusion-map, no-unselected-purpose-content]
    incomplete_when: [activation-missing, selected-content-missing, unselected-content-fabricated]
  - output_id: ART-P8-RELEASE
    content_contract: [purpose-and-limit-release-notes]
    incomplete_when: [purpose-missing, limitations-hidden, review-boundary-missing]
  - output_id: ART-P8-APPROVAL
    content_contract: [immutable-human-release-decision]
    incomplete_when: [human-decision-missing, unsigned-input-hashes, mutable-decision]
  - output_id: ART-G7-RELEASE
    content_contract: [derived-g7-without-self-ledger-input]
    incomplete_when: [approval-missing, purpose-output-missing, gate-ledger-as-input]
  - output_id: ART-P8-ROOT-SUMMARY
    content_contract: [root-summary-without-self-or-freeze-input]
    incomplete_when: [child-summary-missing, self-hash, freeze-input]
  - output_id: ART-P8-FREEZE
    content_contract: [detached-root-and-content-attestation]
    incomplete_when: [root-summary-missing, declared-output-missing, recursive-self-hash]
  - output_id: artifact:program.profile-exit-verification.phase8.v1
    content_contract: [root-and-freeze-verification]
    incomplete_when: [G7-invalid, root-verification-failed, freeze-verification-failed]
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
  gate_id: PROFILE-FULL-EXIT
  required_predecessor_gates: [G0, G1, G2, G3, G4, G5, G6, G7]
  pass_criteria:
    - artifact:program.wave-plan.v1
    - artifact:program.phase-hash-index.phase8.v07
    - artifact:program.phase-summary-index.phase8.v07
    - artifact:program.review-cadence.phase8.v04
    - artifact:program.gate-ledger.g7.v06
    - artifact:program.delta-ledger.phase8.v01
    - artifact:program.purpose-delivery.phase8.v1
    - artifact:program.cluster-split-freeze-ledger.phase8.v1
    - ART-P8-REWRITE
    - ART-P8-MIGRATION
    - ART-P8-REPLACEMENT
    - ART-P8-DUE-DILIGENCE
    - ART-P8-COMPETITOR
    - ART-P8-RELEASE
    - ART-P8-APPROVAL
    - ART-G7-RELEASE
    - ART-P8-ROOT-SUMMARY
    - ART-P8-FREEZE
    - artifact:program.profile-exit-verification.phase8.v1
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
    generation_order: [phase8-content, human-approval, derived-g7, child-phase-summaries, root-summary, detached-freeze, profile-exit-verification]
  parent_child_summaries:
    append_only_ids: true
    parent_inputs_are_child_hashes: true
    self_hash_excluded: true
    freeze_excluded: true
    final_snapshot_before_root: true
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
    final_phase8_snapshot_before_freeze: true
  selected_goal: rewrite
  selected_goal_binding:
    artifact_id: ART-P0-BRIEF
    artifact_field: approved_primary_goal
    approved_primary_goal: rewrite
    artifact_hash_required: true
    binding_rule: selected_goal-equals-approved-primary-goal
  phase9_evidence_input:
    artifact_id: ART-P9-EVIDENCE-INPUT
    immutable: true
    required_fields: [version_id, scope_ids, content_hash, authorization_identity]
    hash_algorithm: SHA-256
    authorization_identity:
      authorization_artifact_id: ART-P0-AUTH
      required_fields: [authorization_artifact_id, authorization_artifact_hash, authorized_scope_ids]
  phase9_branch_selector:
    artifact_id: artifact:program.phase9-branch-selection.v1
    selected_branch: runtime
    exactly_one: true
    branches:
      runtime:
        activation: selected
        required_inputs: [ART-P0-AUTH, ART-G0-AUTH]
        current_authorization_required: true
        current_g0_required: true
        g0_required_verdict: pass
        per_action_authorization: true
      approved-static:
        activation: excluded
        required_inputs: [ART-P5-STATIC, ART-P5-RUNTIME-GAP, ART-P5-STATIC-ACCEPTANCE, ART-G5-RUNTIME]
        valid_acceptance_decision_required: true
        claim_ceiling: statically-supported
        forbidden_status: runtime-confirmed
  phase9_revalidation:
    runtime:
      authorization_required: true
      authorization_artifact: ART-P0-AUTH
      per_action_authorization: true
      result_artifact: ART-P9-REVALIDATION
    approved-static:
      required_artifacts: [ART-P5-STATIC, ART-P5-RUNTIME-GAP, ART-P5-STATIC-ACCEPTANCE]
      claim_ceiling: statically-supported
      forbidden_status: runtime-confirmed
      result_artifact: ART-P9-REVALIDATION
    learning:
      may_update_method_revision_candidate: true
      may_update_product_truth: false
      maturity_requires_independent_evidence: true
  phase9_required_outputs:
    ART-P9-DELTA: [frozen-baseline-and-new-evidence, affected-object-and-link-candidates, unaffected-rationale]
    ART-P9-REVALIDATION: [selected-impact-set, targeted-rerun-results-or-static-gap, affected-denominator-recalculation]
    ART-P9-CALIBRATION: [prior-prediction-and-confidence, empirical-outcome, false-positive-and-false-negative-analysis, sample-boundary]
    ART-P9-LEARNING: [method-revision-candidate, counterexamples-and-evidence-scope, maturity-candidate-not-product-truth]
  purpose_outputs:
    rewrite:
      output_artifact: ART-P8-REWRITE
      required_content: [as-is-to-be-traces, preserve-correct-drop-or-research-decisions, migration-impact, executable-acceptance]
      exclusion_map: [migration, replacement, acquisition-due-diligence, competitor-research]
      difference_map: [legacy-behavior-vs-target-requirement, accepted-vs-rejected-differences]
      activation_condition: selected_goal=rewrite
      inactive_content: exclusion-map-only
    migration:
      output_artifact: ART-P8-MIGRATION
      required_content: [source-to-target-identity, field-state-history-conversion, reconciliation-cutover-coexistence, rollback-ownership]
      exclusion_map: [rewrite, replacement, acquisition-due-diligence, competitor-research]
      difference_map: [source-vs-target-semantics, convertible-vs-exception-records]
      activation_condition: selected_goal=migration
      inactive_content: exclusion-map-only
    replacement:
      output_artifact: ART-P8-REPLACEMENT
      required_content: [capability-fit, behavioral-gaps, workarounds, conversion-and-exit-cost]
      exclusion_map: [rewrite, migration, acquisition-due-diligence, competitor-research]
      difference_map: [required-vs-candidate-behavior, accepted-vs-blocking-gaps]
      activation_condition: selected_goal=replacement
      inactive_content: exclusion-map-only
    acquisition-due-diligence:
      output_artifact: ART-P8-DUE-DILIGENCE
      required_content: [product-technology-data-dependency-facts, rights-boundaries, valuation-and-integration-risks, evidence-gaps-and-owners]
      exclusion_map: [rewrite, migration, replacement, competitor-research]
      difference_map: [represented-vs-evidenced-facts, known-vs-unverified-risk]
      activation_condition: selected_goal=acquisition-due-diligence
      inactive_content: exclusion-map-only
    competitor-research:
      output_artifact: ART-P8-COMPETITOR
      required_content: [bounded-observations, comparable-capabilities-and-journeys, differentiators-and-hypotheses, unverified-boundaries]
      exclusion_map: [rewrite, migration, replacement, acquisition-due-diligence]
      difference_map: [observed-difference-vs-interpretation, comparable-vs-noncomparable-scope]
      activation_condition: selected_goal=competitor-research
      inactive_content: exclusion-map-only
  cluster_policy:
    oversized_when: [review_capacity_exceeded, mixed_ownership, unbounded_denominator]
    split_by: [business-domain, runtime-identity, tenant-role, data-ownership, failure-boundary]
    freeze_conditions: [child_denominator_bound, child_gates_pass, child_hashes_recorded, parent_summary_rebuilt]
  artifact_dag:
    external_inputs: [ART-P0-AUTH, ART-P0-BRIEF, ART-P1-BASELINE, ART-P9-EVIDENCE-INPUT, ART-G0-AUTH, ART-P5-STATIC, ART-P5-RUNTIME-GAP, ART-P5-STATIC-ACCEPTANCE, ART-G5-RUNTIME]
    artifact_versions:
      - {sequence: 1, artifact_id: artifact:program.wave-plan.v1, concept_id: artifact-concept:program.wave-plan, produced_in: wave-0-authorize-baseline, inputs: [ART-P0-AUTH, ART-P1-BASELINE], predecessor_id: null, predecessor_relation: root, replaced_by: null, lifecycle: active, terminal_stage: pre-terminal}
      - {sequence: 2, artifact_id: artifact:program.phase01-baseline.v1, concept_id: artifact-concept:program.phase-baseline, produced_in: wave-0-authorize-baseline, inputs: [ART-P1-BASELINE], predecessor_id: null, predecessor_relation: root, replaced_by: null, lifecycle: active, terminal_stage: pre-terminal}
      - {sequence: 3, artifact_id: artifact:program.review-cadence.wave0.v00, concept_id: artifact-concept:program.review-cadence, produced_in: wave-0-authorize-baseline, inputs: [artifact:program.wave-plan.v1], predecessor_id: null, predecessor_relation: root, replaced_by: artifact:program.review-cadence.wave1.v01, lifecycle: replaced, terminal_stage: pre-terminal}
      - {sequence: 4, artifact_id: artifact:program.delta-ledger.wave0.v00, concept_id: artifact-concept:program.delta-ledger, produced_in: wave-0-authorize-baseline, inputs: [artifact:program.phase01-baseline.v1], predecessor_id: null, predecessor_relation: root, replaced_by: artifact:program.delta-ledger.phase8.v01, lifecycle: replaced, terminal_stage: pre-terminal}
      - {sequence: 5, artifact_id: artifact:program.gate-ledger.g01.v00, concept_id: artifact-concept:program.gate-ledger, produced_in: wave-0-authorize-baseline, inputs: [ART-P0-AUTH, artifact:program.phase01-baseline.v1], predecessor_id: null, predecessor_relation: root, replaced_by: artifact:program.gate-ledger.g2.v01, lifecycle: replaced, terminal_stage: pre-terminal}
      - {sequence: 6, artifact_id: artifact:program.phase-hash-index.wave0.v00, concept_id: artifact-concept:program.phase-hash-index, produced_in: wave-0-authorize-baseline, inputs: [artifact:program.wave-plan.v1, artifact:program.phase01-baseline.v1, artifact:program.review-cadence.wave0.v00, artifact:program.delta-ledger.wave0.v00, artifact:program.gate-ledger.g01.v00], predecessor_id: null, predecessor_relation: root, replaced_by: artifact:program.phase-hash-index.wave1.v01, lifecycle: replaced, terminal_stage: pre-terminal}
      - {sequence: 7, artifact_id: artifact:program.phase-summary-index.wave0.v00, concept_id: artifact-concept:program.phase-summary-index, produced_in: wave-0-authorize-baseline, inputs: [artifact:program.phase-hash-index.wave0.v00, artifact:program.gate-ledger.g01.v00], predecessor_id: null, predecessor_relation: root, replaced_by: null, lifecycle: active, terminal_stage: pre-terminal}
      - {sequence: 8, artifact_id: artifact:program.product-surface.phase2.v1, concept_id: artifact-concept:program.product-surface, produced_in: wave-1-product-surface, inputs: [artifact:program.phase-summary-index.wave0.v00], predecessor_id: null, predecessor_relation: root, replaced_by: null, lifecycle: active, terminal_stage: pre-terminal}
      - {sequence: 9, artifact_id: artifact:program.review-cadence.wave1.v01, concept_id: artifact-concept:program.review-cadence, produced_in: wave-1-product-surface, inputs: [artifact:program.review-cadence.wave0.v00, artifact:program.product-surface.phase2.v1], predecessor_id: artifact:program.review-cadence.wave0.v00, predecessor_relation: replaces, replaced_by: artifact:program.review-cadence.wave4.v02, lifecycle: replaced, terminal_stage: pre-terminal}
      - {sequence: 10, artifact_id: artifact:program.phase-hash-index.wave1.v01, concept_id: artifact-concept:program.phase-hash-index, produced_in: wave-1-product-surface, inputs: [artifact:program.phase-hash-index.wave0.v00, artifact:program.product-surface.phase2.v1, artifact:program.review-cadence.wave1.v01], predecessor_id: artifact:program.phase-hash-index.wave0.v00, predecessor_relation: replaces, replaced_by: artifact:program.phase-hash-index.wave2.v02, lifecycle: replaced, terminal_stage: pre-terminal}
      - {sequence: 11, artifact_id: artifact:program.phase-summary-index.wave1.v01, concept_id: artifact-concept:program.phase-summary-index, produced_in: wave-1-product-surface, inputs: [artifact:program.phase-summary-index.wave0.v00, artifact:program.phase-hash-index.wave1.v01, artifact:program.product-surface.phase2.v1], predecessor_id: artifact:program.phase-summary-index.wave0.v00, predecessor_relation: parent, replaced_by: null, lifecycle: active, terminal_stage: pre-terminal}
      - {sequence: 12, artifact_id: artifact:program.technical-atlas.phase3.v1, concept_id: artifact-concept:program.technical-atlas, produced_in: wave-2-architecture-assets, inputs: [artifact:program.phase-summary-index.wave1.v01], predecessor_id: null, predecessor_relation: root, replaced_by: null, lifecycle: active, terminal_stage: pre-terminal}
      - {sequence: 13, artifact_id: artifact:program.gate-ledger.g2.v01, concept_id: artifact-concept:program.gate-ledger, produced_in: wave-2-architecture-assets, inputs: [artifact:program.gate-ledger.g01.v00, artifact:program.technical-atlas.phase3.v1], predecessor_id: artifact:program.gate-ledger.g01.v00, predecessor_relation: replaces, replaced_by: artifact:program.gate-ledger.g3.v02, lifecycle: replaced, terminal_stage: pre-terminal}
      - {sequence: 14, artifact_id: artifact:program.phase-hash-index.wave2.v02, concept_id: artifact-concept:program.phase-hash-index, produced_in: wave-2-architecture-assets, inputs: [artifact:program.phase-hash-index.wave1.v01, artifact:program.technical-atlas.phase3.v1, artifact:program.gate-ledger.g2.v01], predecessor_id: artifact:program.phase-hash-index.wave1.v01, predecessor_relation: replaces, replaced_by: artifact:program.phase-hash-index.wave3.v03, lifecycle: replaced, terminal_stage: pre-terminal}
      - {sequence: 15, artifact_id: artifact:program.phase-summary-index.wave2.v02, concept_id: artifact-concept:program.phase-summary-index, produced_in: wave-2-architecture-assets, inputs: [artifact:program.phase-summary-index.wave1.v01, artifact:program.phase-hash-index.wave2.v02, artifact:program.gate-ledger.g2.v01], predecessor_id: artifact:program.phase-summary-index.wave1.v01, predecessor_relation: parent, replaced_by: null, lifecycle: active, terminal_stage: pre-terminal}
      - {sequence: 16, artifact_id: artifact:program.vertical-traces.phase4.v1, concept_id: artifact-concept:program.vertical-traces, produced_in: wave-3-vertical-traces, inputs: [artifact:program.phase-summary-index.wave2.v02], predecessor_id: null, predecessor_relation: root, replaced_by: null, lifecycle: active, terminal_stage: pre-terminal}
      - {sequence: 17, artifact_id: artifact:program.gate-ledger.g3.v02, concept_id: artifact-concept:program.gate-ledger, produced_in: wave-3-vertical-traces, inputs: [artifact:program.gate-ledger.g2.v01, artifact:program.vertical-traces.phase4.v1], predecessor_id: artifact:program.gate-ledger.g2.v01, predecessor_relation: replaces, replaced_by: artifact:program.gate-ledger.g5.v03, lifecycle: replaced, terminal_stage: pre-terminal}
      - {sequence: 18, artifact_id: artifact:program.phase-hash-index.wave3.v03, concept_id: artifact-concept:program.phase-hash-index, produced_in: wave-3-vertical-traces, inputs: [artifact:program.phase-hash-index.wave2.v02, artifact:program.vertical-traces.phase4.v1, artifact:program.gate-ledger.g3.v02], predecessor_id: artifact:program.phase-hash-index.wave2.v02, predecessor_relation: replaces, replaced_by: artifact:program.phase-hash-index.wave4.v04, lifecycle: replaced, terminal_stage: pre-terminal}
      - {sequence: 19, artifact_id: artifact:program.phase-summary-index.wave3.v03, concept_id: artifact-concept:program.phase-summary-index, produced_in: wave-3-vertical-traces, inputs: [artifact:program.phase-summary-index.wave2.v02, artifact:program.phase-hash-index.wave3.v03, artifact:program.gate-ledger.g3.v02], predecessor_id: artifact:program.phase-summary-index.wave2.v02, predecessor_relation: parent, replaced_by: null, lifecycle: active, terminal_stage: pre-terminal}
      - {sequence: 20, artifact_id: artifact:program.validation-results.phase5.v1, concept_id: artifact-concept:program.validation-results, produced_in: wave-4-runtime-or-static-validation, inputs: [artifact:program.phase-summary-index.wave3.v03], predecessor_id: null, predecessor_relation: root, replaced_by: null, lifecycle: active, terminal_stage: pre-terminal}
      - {sequence: 21, artifact_id: artifact:program.review-cadence.wave4.v02, concept_id: artifact-concept:program.review-cadence, produced_in: wave-4-runtime-or-static-validation, inputs: [artifact:program.review-cadence.wave1.v01, artifact:program.validation-results.phase5.v1], predecessor_id: artifact:program.review-cadence.wave1.v01, predecessor_relation: replaces, replaced_by: artifact:program.review-cadence.wave6.v03, lifecycle: replaced, terminal_stage: pre-terminal}
      - {sequence: 22, artifact_id: artifact:program.gate-ledger.g5.v03, concept_id: artifact-concept:program.gate-ledger, produced_in: wave-4-runtime-or-static-validation, inputs: [artifact:program.gate-ledger.g3.v02, artifact:program.validation-results.phase5.v1], predecessor_id: artifact:program.gate-ledger.g3.v02, predecessor_relation: replaces, replaced_by: artifact:program.gate-ledger.g4.v04, lifecycle: replaced, terminal_stage: pre-terminal}
      - {sequence: 23, artifact_id: artifact:program.phase-hash-index.wave4.v04, concept_id: artifact-concept:program.phase-hash-index, produced_in: wave-4-runtime-or-static-validation, inputs: [artifact:program.phase-hash-index.wave3.v03, artifact:program.validation-results.phase5.v1, artifact:program.review-cadence.wave4.v02, artifact:program.gate-ledger.g5.v03], predecessor_id: artifact:program.phase-hash-index.wave3.v03, predecessor_relation: replaces, replaced_by: artifact:program.phase-hash-index.wave5.v05, lifecycle: replaced, terminal_stage: pre-terminal}
      - {sequence: 24, artifact_id: artifact:program.phase-summary-index.wave4.v04, concept_id: artifact-concept:program.phase-summary-index, produced_in: wave-4-runtime-or-static-validation, inputs: [artifact:program.phase-summary-index.wave3.v03, artifact:program.phase-hash-index.wave4.v04, artifact:program.gate-ledger.g5.v03], predecessor_id: artifact:program.phase-summary-index.wave3.v03, predecessor_relation: parent, replaced_by: null, lifecycle: active, terminal_stage: pre-terminal}
      - {sequence: 25, artifact_id: artifact:program.semantic-model.phase6.v1, concept_id: artifact-concept:program.semantic-model, produced_in: wave-5-domain-synthesis, inputs: [artifact:program.phase-summary-index.wave4.v04], predecessor_id: null, predecessor_relation: root, replaced_by: null, lifecycle: active, terminal_stage: pre-terminal}
      - {sequence: 26, artifact_id: artifact:program.gate-ledger.g4.v04, concept_id: artifact-concept:program.gate-ledger, produced_in: wave-5-domain-synthesis, inputs: [artifact:program.gate-ledger.g5.v03, artifact:program.semantic-model.phase6.v1], predecessor_id: artifact:program.gate-ledger.g5.v03, predecessor_relation: replaces, replaced_by: artifact:program.gate-ledger.g6.v05, lifecycle: replaced, terminal_stage: pre-terminal}
      - {sequence: 27, artifact_id: artifact:program.phase-hash-index.wave5.v05, concept_id: artifact-concept:program.phase-hash-index, produced_in: wave-5-domain-synthesis, inputs: [artifact:program.phase-hash-index.wave4.v04, artifact:program.semantic-model.phase6.v1, artifact:program.gate-ledger.g4.v04], predecessor_id: artifact:program.phase-hash-index.wave4.v04, predecessor_relation: replaces, replaced_by: artifact:program.phase-hash-index.wave6.v06, lifecycle: replaced, terminal_stage: pre-terminal}
      - {sequence: 28, artifact_id: artifact:program.phase-summary-index.wave5.v05, concept_id: artifact-concept:program.phase-summary-index, produced_in: wave-5-domain-synthesis, inputs: [artifact:program.phase-summary-index.wave4.v04, artifact:program.phase-hash-index.wave5.v05, artifact:program.gate-ledger.g4.v04], predecessor_id: artifact:program.phase-summary-index.wave4.v04, predecessor_relation: parent, replaced_by: null, lifecycle: active, terminal_stage: pre-terminal}
      - {sequence: 29, artifact_id: artifact:program.coverage-audit.phase7.v1, concept_id: artifact-concept:program.coverage-audit, produced_in: wave-6-coverage-conflict, inputs: [artifact:program.phase-summary-index.wave5.v05], predecessor_id: null, predecessor_relation: root, replaced_by: null, lifecycle: active, terminal_stage: pre-terminal}
      - {sequence: 30, artifact_id: artifact:program.review-cadence.wave6.v03, concept_id: artifact-concept:program.review-cadence, produced_in: wave-6-coverage-conflict, inputs: [artifact:program.review-cadence.wave4.v02, artifact:program.coverage-audit.phase7.v1], predecessor_id: artifact:program.review-cadence.wave4.v02, predecessor_relation: replaces, replaced_by: artifact:program.review-cadence.phase8.v04, lifecycle: replaced, terminal_stage: pre-terminal}
      - {sequence: 31, artifact_id: artifact:program.gate-ledger.g6.v05, concept_id: artifact-concept:program.gate-ledger, produced_in: wave-6-coverage-conflict, inputs: [artifact:program.gate-ledger.g4.v04, artifact:program.coverage-audit.phase7.v1], predecessor_id: artifact:program.gate-ledger.g4.v04, predecessor_relation: replaces, replaced_by: artifact:program.gate-ledger.g7.v06, lifecycle: replaced, terminal_stage: pre-terminal}
      - {sequence: 32, artifact_id: artifact:program.phase-hash-index.wave6.v06, concept_id: artifact-concept:program.phase-hash-index, produced_in: wave-6-coverage-conflict, inputs: [artifact:program.phase-hash-index.wave5.v05, artifact:program.coverage-audit.phase7.v1, artifact:program.review-cadence.wave6.v03, artifact:program.gate-ledger.g6.v05], predecessor_id: artifact:program.phase-hash-index.wave5.v05, predecessor_relation: replaces, replaced_by: artifact:program.phase-hash-index.phase8.v07, lifecycle: replaced, terminal_stage: pre-terminal}
      - {sequence: 33, artifact_id: artifact:program.phase-summary-index.wave6.v06, concept_id: artifact-concept:program.phase-summary-index, produced_in: wave-6-coverage-conflict, inputs: [artifact:program.phase-summary-index.wave5.v05, artifact:program.phase-hash-index.wave6.v06, artifact:program.gate-ledger.g6.v05], predecessor_id: artifact:program.phase-summary-index.wave5.v05, predecessor_relation: parent, replaced_by: null, lifecycle: active, terminal_stage: pre-terminal}
      - {sequence: 34, artifact_id: artifact:program.cluster-split-freeze-ledger.phase8.v1, concept_id: artifact-concept:program.cluster-freeze-ledger, produced_in: wave-7-freeze-delivery, inputs: [artifact:program.coverage-audit.phase7.v1, artifact:program.phase-summary-index.wave6.v06], predecessor_id: null, predecessor_relation: root, replaced_by: null, lifecycle: active, terminal_stage: phase8-content}
      - {sequence: 35, artifact_id: ART-P8-REWRITE, concept_id: artifact-concept:program.purpose-rewrite, produced_in: wave-7-freeze-delivery, inputs: [ART-P0-BRIEF, artifact:program.coverage-audit.phase7.v1, artifact:program.phase-summary-index.wave6.v06, artifact:program.cluster-split-freeze-ledger.phase8.v1], predecessor_id: null, predecessor_relation: root, replaced_by: null, lifecycle: active, terminal_stage: phase8-content, activation_condition: selected_goal=rewrite, activation: selected, content_mode: purpose-content}
      - {sequence: 36, artifact_id: ART-P8-MIGRATION, concept_id: artifact-concept:program.purpose-migration, produced_in: wave-7-freeze-delivery, inputs: [ART-P0-BRIEF, artifact:program.coverage-audit.phase7.v1, artifact:program.phase-summary-index.wave6.v06, artifact:program.cluster-split-freeze-ledger.phase8.v1], predecessor_id: null, predecessor_relation: root, replaced_by: null, lifecycle: active, terminal_stage: phase8-content, activation_condition: selected_goal=migration, activation: excluded, content_mode: exclusion-map-only}
      - {sequence: 37, artifact_id: ART-P8-REPLACEMENT, concept_id: artifact-concept:program.purpose-replacement, produced_in: wave-7-freeze-delivery, inputs: [ART-P0-BRIEF, artifact:program.coverage-audit.phase7.v1, artifact:program.phase-summary-index.wave6.v06, artifact:program.cluster-split-freeze-ledger.phase8.v1], predecessor_id: null, predecessor_relation: root, replaced_by: null, lifecycle: active, terminal_stage: phase8-content, activation_condition: selected_goal=replacement, activation: excluded, content_mode: exclusion-map-only}
      - {sequence: 38, artifact_id: ART-P8-DUE-DILIGENCE, concept_id: artifact-concept:program.purpose-due-diligence, produced_in: wave-7-freeze-delivery, inputs: [ART-P0-BRIEF, artifact:program.coverage-audit.phase7.v1, artifact:program.phase-summary-index.wave6.v06, artifact:program.cluster-split-freeze-ledger.phase8.v1], predecessor_id: null, predecessor_relation: root, replaced_by: null, lifecycle: active, terminal_stage: phase8-content, activation_condition: selected_goal=acquisition-due-diligence, activation: excluded, content_mode: exclusion-map-only}
      - {sequence: 39, artifact_id: ART-P8-COMPETITOR, concept_id: artifact-concept:program.purpose-competitor, produced_in: wave-7-freeze-delivery, inputs: [ART-P0-BRIEF, artifact:program.coverage-audit.phase7.v1, artifact:program.phase-summary-index.wave6.v06, artifact:program.cluster-split-freeze-ledger.phase8.v1], predecessor_id: null, predecessor_relation: root, replaced_by: null, lifecycle: active, terminal_stage: phase8-content, activation_condition: selected_goal=competitor-research, activation: excluded, content_mode: exclusion-map-only}
      - {sequence: 40, artifact_id: artifact:program.purpose-delivery.phase8.v1, concept_id: artifact-concept:program.purpose-delivery, produced_in: wave-7-freeze-delivery, inputs: [ART-P8-REWRITE, ART-P8-MIGRATION, ART-P8-REPLACEMENT, ART-P8-DUE-DILIGENCE, ART-P8-COMPETITOR], predecessor_id: null, predecessor_relation: root, replaced_by: null, lifecycle: active, terminal_stage: phase8-content}
      - {sequence: 41, artifact_id: ART-P8-RELEASE, concept_id: artifact-concept:program.release-notes, produced_in: wave-7-freeze-delivery, inputs: [artifact:program.purpose-delivery.phase8.v1, ART-P8-REWRITE, artifact:program.coverage-audit.phase7.v1], predecessor_id: null, predecessor_relation: root, replaced_by: null, lifecycle: active, terminal_stage: phase8-content}
      - {sequence: 42, artifact_id: artifact:program.review-cadence.phase8.v04, concept_id: artifact-concept:program.review-cadence, produced_in: wave-7-freeze-delivery, inputs: [artifact:program.review-cadence.wave6.v03, ART-P8-RELEASE], predecessor_id: artifact:program.review-cadence.wave6.v03, predecessor_relation: replaces, replaced_by: null, lifecycle: active, terminal_stage: phase8-content}
      - {sequence: 43, artifact_id: artifact:program.delta-ledger.phase8.v01, concept_id: artifact-concept:program.delta-ledger, produced_in: wave-7-freeze-delivery, inputs: [artifact:program.delta-ledger.wave0.v00, ART-P8-RELEASE], predecessor_id: artifact:program.delta-ledger.wave0.v00, predecessor_relation: replaces, replaced_by: artifact:program.delta-ledger.phase9.v02, lifecycle: replaced, terminal_stage: phase8-content}
      - {sequence: 44, artifact_id: ART-P8-APPROVAL, concept_id: artifact-concept:program.human-release-approval, produced_in: wave-7-freeze-delivery, inputs: [ART-P8-REWRITE, artifact:program.purpose-delivery.phase8.v1, ART-P8-RELEASE, artifact:program.cluster-split-freeze-ledger.phase8.v1, artifact:program.review-cadence.phase8.v04, artifact:program.delta-ledger.phase8.v01, artifact:program.gate-ledger.g6.v05], predecessor_id: null, predecessor_relation: root, replaced_by: null, lifecycle: active, terminal_stage: human-approval}
      - {sequence: 45, artifact_id: ART-G7-RELEASE, concept_id: artifact-concept:program.derived-g7, produced_in: wave-7-freeze-delivery, inputs: [ART-P8-REWRITE, ART-P8-APPROVAL, ART-P8-RELEASE, artifact:program.purpose-delivery.phase8.v1], predecessor_id: null, predecessor_relation: root, replaced_by: null, lifecycle: active, terminal_stage: derived-g7}
      - {sequence: 46, artifact_id: artifact:program.gate-ledger.g7.v06, concept_id: artifact-concept:program.gate-ledger, produced_in: wave-7-freeze-delivery, inputs: [artifact:program.gate-ledger.g6.v05, ART-G7-RELEASE], predecessor_id: artifact:program.gate-ledger.g6.v05, predecessor_relation: replaces, replaced_by: artifact:program.gate-ledger.phase9-pending.v07, lifecycle: replaced, terminal_stage: child-phase-summaries}
      - {sequence: 47, artifact_id: artifact:program.phase-hash-index.phase8.v07, concept_id: artifact-concept:program.phase-hash-index, produced_in: wave-7-freeze-delivery, inputs: [artifact:program.phase-hash-index.wave6.v06, artifact:program.cluster-split-freeze-ledger.phase8.v1, ART-P8-REWRITE, ART-P8-MIGRATION, ART-P8-REPLACEMENT, ART-P8-DUE-DILIGENCE, ART-P8-COMPETITOR, artifact:program.purpose-delivery.phase8.v1, ART-P8-RELEASE, artifact:program.review-cadence.phase8.v04, artifact:program.delta-ledger.phase8.v01, ART-P8-APPROVAL, ART-G7-RELEASE, artifact:program.gate-ledger.g7.v06], predecessor_id: artifact:program.phase-hash-index.wave6.v06, predecessor_relation: replaces, replaced_by: artifact:program.phase-hash-index.wave8.v08, lifecycle: replaced, terminal_stage: child-phase-summaries}
      - {sequence: 48, artifact_id: artifact:program.phase-summary-index.phase8.v07, concept_id: artifact-concept:program.phase-summary-index, produced_in: wave-7-freeze-delivery, inputs: [artifact:program.phase-summary-index.wave6.v06, artifact:program.phase-hash-index.phase8.v07, artifact:program.gate-ledger.g7.v06, ART-G7-RELEASE], predecessor_id: artifact:program.phase-summary-index.wave6.v06, predecessor_relation: parent, replaced_by: null, lifecycle: active, terminal_stage: child-phase-summaries}
      - {sequence: 49, artifact_id: ART-P8-ROOT-SUMMARY, concept_id: artifact-concept:program.root-summary, produced_in: wave-7-freeze-delivery, inputs: [artifact:program.phase-summary-index.phase8.v07, ART-G7-RELEASE, ART-P8-REWRITE, artifact:program.purpose-delivery.phase8.v1, ART-P8-RELEASE, artifact:program.gate-ledger.g7.v06], predecessor_id: null, predecessor_relation: root, replaced_by: null, lifecycle: active, terminal_stage: root-summary}
      - {sequence: 50, artifact_id: ART-P8-FREEZE, concept_id: artifact-concept:program.detached-freeze, produced_in: wave-7-freeze-delivery, inputs: [ART-P8-ROOT-SUMMARY, artifact:program.phase-hash-index.phase8.v07, artifact:program.phase-summary-index.phase8.v07, artifact:program.review-cadence.phase8.v04, artifact:program.gate-ledger.g7.v06, artifact:program.delta-ledger.phase8.v01, artifact:program.cluster-split-freeze-ledger.phase8.v1, ART-P8-REWRITE, ART-P8-MIGRATION, ART-P8-REPLACEMENT, ART-P8-DUE-DILIGENCE, ART-P8-COMPETITOR, artifact:program.purpose-delivery.phase8.v1, ART-P8-RELEASE, ART-P8-APPROVAL, ART-G7-RELEASE], predecessor_id: null, predecessor_relation: root, replaced_by: null, lifecycle: active, terminal_stage: detached-freeze}
      - {sequence: 51, artifact_id: artifact:program.profile-exit-verification.phase8.v1, concept_id: artifact-concept:program.profile-exit-verification, produced_in: wave-7-freeze-delivery, inputs: [ART-G7-RELEASE, ART-P8-ROOT-SUMMARY, ART-P8-FREEZE], predecessor_id: null, predecessor_relation: root, replaced_by: null, lifecycle: active, terminal_stage: profile-exit-verification}
      - {sequence: 52, artifact_id: ART-P9-DELTA, concept_id: artifact-concept:program.phase9-delta, produced_in: wave-8-delta-calibration, inputs: [ART-P8-FREEZE, artifact:program.profile-exit-verification.phase8.v1, ART-P9-EVIDENCE-INPUT], predecessor_id: null, predecessor_relation: root, replaced_by: null, lifecycle: active, terminal_stage: phase9-delta}
      - {sequence: 53, artifact_id: artifact:program.impact-selection.phase9.v1, concept_id: artifact-concept:program.phase9-impact-selection, produced_in: wave-8-delta-calibration, inputs: [ART-P9-DELTA], predecessor_id: null, predecessor_relation: root, replaced_by: null, lifecycle: active, terminal_stage: phase9-delta}
      - {sequence: 54, artifact_id: artifact:program.gate-ledger.phase9-pending.v07, concept_id: artifact-concept:program.gate-ledger, produced_in: wave-8-delta-calibration, inputs: [artifact:program.gate-ledger.g7.v06, ART-P9-DELTA, artifact:program.impact-selection.phase9.v1], predecessor_id: artifact:program.gate-ledger.g7.v06, predecessor_relation: replaces, replaced_by: artifact:program.gate-ledger.phase9-verdict.v08, lifecycle: replaced, terminal_stage: phase9-delta, gate_state: pending}
      - {sequence: 55, artifact_id: artifact:program.phase9-branch-selection.v1, concept_id: artifact-concept:program.phase9-branch-selection, produced_in: wave-8-delta-calibration, inputs: [ART-P9-EVIDENCE-INPUT, artifact:program.gate-ledger.phase9-pending.v07, ART-P0-AUTH, ART-G0-AUTH], predecessor_id: null, predecessor_relation: root, replaced_by: null, lifecycle: active, terminal_stage: phase9-delta, selected_branch: runtime, conditional_input_ids: [ART-P0-AUTH, ART-G0-AUTH]}
      - {sequence: 56, artifact_id: ART-P9-REVALIDATION, concept_id: artifact-concept:program.phase9-revalidation, produced_in: wave-8-delta-calibration, inputs: [ART-P9-DELTA, artifact:program.impact-selection.phase9.v1, artifact:program.gate-ledger.phase9-pending.v07, artifact:program.phase9-branch-selection.v1, ART-P9-EVIDENCE-INPUT, ART-P0-AUTH, ART-G0-AUTH], predecessor_id: null, predecessor_relation: root, replaced_by: null, lifecycle: active, terminal_stage: phase9-delta}
      - {sequence: 57, artifact_id: artifact:program.gate-ledger.phase9-verdict.v08, concept_id: artifact-concept:program.gate-ledger, produced_in: wave-8-delta-calibration, inputs: [artifact:program.gate-ledger.phase9-pending.v07, ART-P9-REVALIDATION], predecessor_id: artifact:program.gate-ledger.phase9-pending.v07, predecessor_relation: replaces, replaced_by: null, lifecycle: active, terminal_stage: phase9-delta, gate_state: post-revalidation-verdict}
      - {sequence: 58, artifact_id: ART-P9-CALIBRATION, concept_id: artifact-concept:program.phase9-calibration, produced_in: wave-8-delta-calibration, inputs: [ART-P9-DELTA, ART-P9-REVALIDATION, artifact:program.gate-ledger.phase9-verdict.v08], predecessor_id: null, predecessor_relation: root, replaced_by: null, lifecycle: active, terminal_stage: phase9-delta}
      - {sequence: 59, artifact_id: ART-P9-LEARNING, concept_id: artifact-concept:program.phase9-learning, produced_in: wave-8-delta-calibration, inputs: [ART-P9-CALIBRATION], predecessor_id: null, predecessor_relation: root, replaced_by: null, lifecycle: active, terminal_stage: phase9-delta}
      - {sequence: 60, artifact_id: artifact:program.delta-ledger.phase9.v02, concept_id: artifact-concept:program.delta-ledger, produced_in: wave-8-delta-calibration, inputs: [artifact:program.delta-ledger.phase8.v01, ART-P9-DELTA, artifact:program.impact-selection.phase9.v1, artifact:program.gate-ledger.phase9-pending.v07, ART-P9-REVALIDATION, artifact:program.gate-ledger.phase9-verdict.v08, ART-P9-CALIBRATION, ART-P9-LEARNING, ART-P8-FREEZE], predecessor_id: artifact:program.delta-ledger.phase8.v01, predecessor_relation: replaces, replaced_by: null, lifecycle: active, terminal_stage: phase9-delta}
      - {sequence: 61, artifact_id: artifact:program.phase-hash-index.wave8.v08, concept_id: artifact-concept:program.phase-hash-index, produced_in: wave-8-delta-calibration, inputs: [artifact:program.phase-hash-index.phase8.v07, ART-P9-DELTA, artifact:program.gate-ledger.phase9-verdict.v08, ART-P9-REVALIDATION, ART-P9-CALIBRATION, ART-P9-LEARNING, artifact:program.delta-ledger.phase9.v02], predecessor_id: artifact:program.phase-hash-index.phase8.v07, predecessor_relation: replaces, replaced_by: null, lifecycle: active, terminal_stage: phase9-delta}
      - {sequence: 62, artifact_id: artifact:program.phase-summary-index.wave8.v08, concept_id: artifact-concept:program.phase-summary-index, produced_in: wave-8-delta-calibration, inputs: [artifact:program.phase-summary-index.phase8.v07, artifact:program.phase-hash-index.wave8.v08, artifact:program.gate-ledger.phase9-verdict.v08, ART-P9-CALIBRATION, ART-P9-LEARNING], predecessor_id: artifact:program.phase-summary-index.phase8.v07, predecessor_relation: parent, replaced_by: null, lifecycle: active, terminal_stage: phase9-delta}
    final_snapshot_ids:
      - artifact:program.phase-hash-index.phase8.v07
      - artifact:program.phase-summary-index.phase8.v07
      - artifact:program.review-cadence.phase8.v04
      - artifact:program.gate-ledger.g7.v06
      - artifact:program.delta-ledger.phase8.v01
  terminal_sequence:
    - stage: phase8-content
      artifact_ids: [artifact:program.cluster-split-freeze-ledger.phase8.v1, ART-P8-REWRITE, ART-P8-MIGRATION, ART-P8-REPLACEMENT, ART-P8-DUE-DILIGENCE, ART-P8-COMPETITOR, artifact:program.purpose-delivery.phase8.v1, ART-P8-RELEASE, artifact:program.review-cadence.phase8.v04, artifact:program.delta-ledger.phase8.v01]
    - stage: human-approval
      artifact_ids: [ART-P8-APPROVAL]
    - stage: derived-g7
      artifact_ids: [ART-G7-RELEASE]
    - stage: child-phase-summaries
      artifact_ids: [artifact:program.gate-ledger.g7.v06, artifact:program.phase-hash-index.phase8.v07, artifact:program.phase-summary-index.phase8.v07]
    - stage: root-summary
      artifact_ids: [ART-P8-ROOT-SUMMARY]
    - stage: detached-freeze
      artifact_ids: [ART-P8-FREEZE]
    - stage: profile-exit-verification
      artifact_ids: [artifact:program.profile-exit-verification.phase8.v1]
```
