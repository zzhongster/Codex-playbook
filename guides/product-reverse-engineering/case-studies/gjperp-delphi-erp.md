# gjpERP Delphi ERP 逆向案例

**证据成熟度：`project-validated`**

**适用范围：** 本案例只总结 gjpERP 单一遗留 Delphi ERP 项目中，从已提交来源摘录并经脱敏的事实所支持的方法与边界；它不是目标产品的完整需求，也不证明这些方法已经跨项目成立。

## 案例背景

目标是先建立可审计的 As-Is 事实库，再把事实映射到重写决策，而不是逐行翻译 Delphi。研究对象同时包含桌面 UI、多份源码视图、数据库目录、中间件边界、安装资源、历史文档和隔离 Windows 运行证据。

案例采用“横向资产分母 + 纵向业务链”双轴：横向防止只追熟悉入口造成遗漏，纵向回答一个能力如何从产品入口到持久化状态和可见结果。设计依据来自 `source:gjperp.reverse-design`，阶段执行边界来自 `source:gjperp.program-roadmap`。

## 项目约束

- As-Is 事实与 To-Be 设计分仓治理；旧 PRD 只能作为检索线索，不能直接升级为产品事实。
- 多份源码树是等权变体证据，目录名和记忆中的版本不能替代可执行文件、配置、数据库与运行行为的身份绑定。
- 自动提取只建立结构地图；业务语义、特殊值、副作用、异常路径和界面行为必须由源码解释、运行证据或领域裁决补足。
- 原始截图、日志、数据库输出和环境身份不进入公开知识页；Git 只保存脱敏引用、内容摘要、结论和复现协议。
- 原始来源文档与本公开案例采用不同发布边界；不得因来源已经提交，就推断其中所有内容均适合转录或公开。
- 破坏性或写入实验只允许在可恢复副本中执行；授权漂移、身份不符、源数据变化或清理失败立即停止。

## 横向分母

Phase 0 先按路径、大小、哈希、资产类别和 Git 策略冻结全仓资产，再保留主源码视图与变体之间的相同、不同和缺失关系。正式分母见 `outcome:gjperp.phase0-denominator`；它是资产库存，不是某份源码已对应部署版本的证明。

Phase 2 将源码、DFM 派生文本、数据库目录和脱敏校准引用投影为类型化节点与关系。每一层分别报告分母、已覆盖、未知和排除项；后续 Phase 3 至 Phase 6D 继续使用各自冻结分母，不用单一“完成率”混合结构、静态语义、运行行为和领域确认。

分母变化只能通过新版本和影响分析进入；不能删除未知项来提高覆盖率，也不能用父阶段重新扫描原始资产改写子阶段事实。

## 纵向证据链

| chain_id | ordered_path | claim_status | evidence_refs | boundary |
| --- | --- | --- | --- | --- |
| `trace:gjperp.menu-to-persistence` | 动态菜单或配置入口 → 窗体与 Action → 事件或例程 → 客户端数据边界 → 中间件方法 → 过程、表与字段 | statically-supported | source:gjperp.reverse-design, source:gjperp.phase2-runtime, source:gjperp.phase3-runtime | 结构链可定位，但未回放的具体按钮、参数和值语义不能升级为运行确认 |
| `trace:gjperp.action-to-reversible-state` | 授权 UI 动作 → 可见校验或确认 → 保存与状态迁移 → 数据库前后快照 → 重载验证 → 依赖逆序清理 | runtime-confirmed | source:gjperp.phase1-runtime, source:gjperp.phase4-runtime | 只确认已绑定版本、授权场景和一次性副本中的窄行为，不外推到未执行模块 |
| `trace:gjperp.child-to-parent-freeze` | 子阶段记录 → 子摘要与内容哈希 → 父阶段关系 → 跨模块不变量 → 未支持联合行为 → 冻结边界 | statically-supported | source:gjperp.phase5-trade, source:gjperp.phase6-finance | 父阶段连接冻结事实，不重新解释子阶段，也不把静态一致性改写成联合 UI 已运行 |

链路必须保留每个跃迁的关系类型、证据引用与主张状态。动态分派无法唯一闭合时保留候选或显式 seed，并登记后续验证方法；禁止按短名称选择第一个目标。

## 稳定 ID

| object_id | kind | role | claim_status | evidence_refs |
| --- | --- | --- | --- | --- |
| `capability:gjperp.dynamic-menu-dispatch` | capability | 将配置驱动入口连接到产品能力 | statically-supported | source:gjperp.reverse-design, source:gjperp.phase3-runtime |
| `interaction:gjperp.menu-action-open` | interaction | 表示一次有角色与状态边界的可见动作 | observed | source:gjperp.phase2-runtime |
| `code:gjperp.client-data-boundary` | code | 隔离窗体逻辑与共享数据访问边界 | statically-supported | source:gjperp.phase3-runtime |
| `integration:gjperp.middleware-call` | integration | 表示客户端到中间件的类型化调用 | statically-supported | source:gjperp.phase3-runtime |
| `data:gjperp.persisted-field-transition` | data-object | 表示过程、表、字段及状态变化 | runtime-confirmed | source:gjperp.phase1-runtime |
| `claim:gjperp.unplayed-joint-ui-action` | claim | 保留尚未联合回放的 UI 行为 | unsupported | source:gjperp.phase5-trade, source:gjperp.phase6-finance |

项目内部的图谱 ID 由对象种类与限定逻辑键确定，重命名保留别名，对象消失保留 tombstone，旧 ID 不分配给新对象。公开案例使用上表的脱敏 ID 说明关系，不泄露本地对象键或运行身份。

## 证据状态

| claim_status | meaning | case_rule |
| --- | --- | --- |
| observed | 在获授权表面直接看见 | 只描述当时角色、版本和状态下可见的事实 |
| statically-supported | 由源码、配置、结构或数据库定义支持 | 不声称该路径在部署环境实际执行 |
| runtime-confirmed | 由绑定身份的可复现实验确认 | 只覆盖实际回放的输入、分支和副作用 |
| domain-confirmed | 由具名领域责任人确认 | 必须保留决策记录与适用边界 |
| inferred | 多条证据支持但尚未闭环 | 写明替代解释和下一步验证 |
| conflicting | 证据互相冲突 | 阻断相关冻结，不能静默择一 |
| unsupported | 证据不足或场景未执行 | 保留在覆盖分母与验证队列中 |
| deprecated | 目标版本仍可定位但已废弃 | 保留历史可达性和替代关系 |
| superseded | 主张已被新版本取代 | 旧记录仍可寻址，不能覆盖删除 |

项目来源中的 `confirmed`、`partial`、`unsupported` 和 `conflicting` 是项目阶段词汇；导入通用指南时必须检查底层证据，再映射到上表状态，不能仅凭同名或父阶段通过自动升级。

## Windows 实验室

实验室把应用制品、数据库兼容层、区域设置、权限、配置和运行协议固定为同一实验身份，但公开页只保留脱敏引用与摘要。先做只读兼容性和资产校准，再按动作逐项授权写入实验；旧客户端返回、截图、日志与独立数据库断言是不同观察面。

每个实验先冻结协议、输入和预期差异，使用此前不存在的证据根；第一次失败必须保留并停止正式批次，修复后在新证据根完整重跑。相关实机经验见[Delphi/VCL 隔离桌面自动化实验](../../../experiments/2026-08-15-delphi-vcl-session-zero-ui-automation.md)和[不要重试掉第一份实机失败](../../../anti-patterns/retrying-away-first-live-failure.md)。

点击成功、窗口出现或聚合查询通过均不是业务状态成立的充分条件。重要动作至少需要可见结果、重载结果和数据状态相互校准；阻塞分支还要证明预期反馈与数据零变化。

## 安全克隆协议

1. 对源数据做只读身份与逻辑指纹，生成一次性可恢复副本，并验证副本基线与源基线在声明口径上一致。
2. 把客户端和数据连接显式绑定到副本；写入前设置只能命中副本的安全门禁，并使用纯合成、可检索的实验标记。
3. 每个动作保存前后状态、外部效应和清理义务；任何源数据差异、越界写入或未声明副作用立即停止。
4. 按依赖逆序撤销业务对象，复核活动业务键、余额与关系，执行数据库一致性检查，再删除副本和临时对象。
5. 分开报告“逻辑恢复”和“字节级恢复”：identity、高水位、审计事件或缓存归一化可能按历史语义继续变化，不能为了做平差而直接修改源或副本。

Phase 4 的窄证据表明源侧无业务变化且一次性副本完成清理，但该安全结论不证明主数据或单据 UI 状态机已经逐项运行。这个边界也见[数据库聚合探针不能证明 UI 行为](../../../anti-patterns/aggregate-probe-used-as-ui-behavior-proof.md)。

## 覆盖与冻结

覆盖表按证据平面分别计算：结构、静态语义、UI 动作、数据对象、运行场景、追踪链和跨模块不变量不能合并成一个百分比。`unsupported` 与 P2 保留在分母中并携带下一步验证，P0/P1 的清零也不表示 P2 语义已经确认。

子阶段发布确定性输出白名单、输入身份、内容哈希和摘要；父阶段只引用冻结子摘要，再增加跨模块关系与边界。做法与[按阶段冻结证据目录](../../../patterns/freeze-phase-scoped-evidence-catalogs.md)一致；动态数据库边的补强原则见[显式登记动态数据库调用](../../../patterns/seed-dynamic-database-calls-explicitly.md)。

原始大证据留在受控存储时，Git 中必须有完整内容清单与摘要；“存在哈希”仍不等于有独立签名或外部不可变归档。案例来源明确保留了待独立复核边界，相关风险见[忽略大证据却不提交清单](../../../anti-patterns/ignored-evidence-without-durable-manifest.md)。

## 实测结果

以下只列可由本页来源逐项复核的阶段结果。每条精确计数都同时绑定 Phase、测量时间和不可变来源；不同 Phase 的分母不能横向相减，也不能脱离边界合并成总完成率。

### 计数注脚

| outcome_id | measurement | phase | measured_at | source_id | boundary |
| --- | --- | --- | --- | --- | --- |
| `outcome:gjperp.phase0-denominator` | 8,342 assets; 5,632 track; 2,692 manifest-only; 18 ignore | Phase 0 | 2026-07-17T19:59:32+00:00 | source:gjperp.phase0-baseline | 资产与 Git 策略库存；主版本映射仍待运行身份确认 |
| `outcome:gjperp.phase2-atlas` | 4,314/4,314 source files parsed; 0 silent omissions; 66,672 nodes; 175,432 relations; P2=91,993 | Phase 2 | 2026-09-01T16:15:00+08:00 | source:gjperp.phase2-runtime | 图谱结构与诊断；P2 是校准队列，不是已确认语义 |
| `outcome:gjperp.phase3-coverage` | structural 5,705/5,705; static_semantic 3,133/5,705; runtime 10/5,705; database 147/1,373 | Phase 3 | 2026-09-01T00:00:00Z | source:gjperp.phase3-runtime | 系统框架阶段的分层覆盖，不可折算为单一完成率 |
| `outcome:gjperp.phase4-coverage` | database_field 386/386; runtime_scenario 19/19; static_semantic 476/476; structural 5,064/5,064; trace_chain 0/82; source delta 0; clone not removed 0 | Phase 4 | 2026-09-02T00:00:00Z | source:gjperp.phase4-runtime | 克隆安全与聚合矩阵通过，不代表业务 UI 写入链已重放 |
| `outcome:gjperp.phase5-parent` | boundary 1/1; child_checkpoint 4/4; cross_invariant 7/10; cross_link 10/10; cross_projection 10/10; runtime_scenario 0/10 | Phase 5 | 2026-09-02T00:00:00Z | source:gjperp.phase5-trade | 父级静态冻结；未运行场景仍为 unsupported |
| `outcome:gjperp.phase6-parent` | 8 invariant families; P0=0; P1=0; P2=8; P3=0 | Phase 6D | 2026-09-03T06:45:00+08:00 | source:gjperp.phase6-finance | 静态跨模块一致性；联合旧 UI 动作未运行 |

这些结果展示了分母、已覆盖与未知项可以同时保留。较早阶段的精确数量只属于当时冻结输入；后续修订必须建立新结果和影响关系，而不是静默改写表中事实。

## 已验证方法

| method_id | method | maturity | project_evidence | boundary |
| --- | --- | --- | --- | --- |
| `method:gjperp.horizontal-denominator` | 先冻结全资产和变体，再按风险选择纵向链 | project-validated | source:gjperp.phase0-baseline, source:gjperp.phase2-runtime | 只在该 ERP 的阶段执行中验证 |
| `method:gjperp.qualified-stable-identity` | 用对象种类与限定逻辑键生成稳定 ID，保留别名和 tombstone | project-validated | source:gjperp.phase2-stable-id | 尚未在另一种资产体系复验 |
| `method:gjperp.layered-coverage` | 分开报告结构、静态、运行与数据覆盖 | project-validated | source:gjperp.phase3-runtime, source:gjperp.phase4-runtime | 分母仅在各自 Phase 内可比 |
| `method:gjperp.safe-disposable-clone` | 源指纹、副本绑定、前后差异、逆序清理和一致性检查 | project-validated | source:gjperp.phase1-runtime, source:gjperp.phase4-runtime | 只覆盖已授权的遗留 Windows 与数据库组合 |
| `method:gjperp.parent-child-freeze` | 子阶段摘要经哈希进入父阶段，父阶段不重写子事实 | project-validated | source:gjperp.phase5-trade, source:gjperp.phase6-finance | 仍缺独立项目证据 |
| `method:gjperp.cross-stack-transfer` | 将相同语义模型移植到 Web、Java 与 .NET 新产品 | proposed | source:gjperp.reverse-design, source:gjperp.program-roadmap | 这是下一项目要验证的假设，不是本案例结果 |

同一 ERP 内的多个业务集群只是同一项目中的重复验证，不构成 cross-project proof，也不能据此晋升为 Pattern。上表成熟度只描述方法证据，不替代产品主张的状态、置信度和证据引用。

## 失败假设

- **“目录名就是部署版本”失败。** 多份源码视图必须靠制品、配置与运行身份校准；Phase 0 的库存本身不回答部署映射。
- **“自动图谱完整就等于业务语义完整”失败。** 弱引用、动态分派和同名歧义必须进入显式队列；P2 数量不是成功或失败的快捷结论。
- **“聚合查询或表存在能证明按钮行为”失败。** 安全探针只能确认副本、连通性和声明的聚合结果；未执行 UI 场景保持 `unsupported`。
- **“业务撤销等于数据库字节回滚”失败。** 历史 identity、高水位、审计痕迹与缓存归一化可能合法保留，清理协议必须按逻辑基线判定并披露差异。
- **“失败后再跑成功即可丢弃第一次结果”失败。** 第一份实机失败属于证据历史；修复后的正式批次使用新根，不能挑选成功样本覆盖失败。
- **“阶段分支名可以充当冻结身份”失败。** 冻结依赖不可变提交、输入哈希和输出摘要，分支名只保留为 provenance。

这些反例共同说明：工具结果要按其实际观察面解释，不能跨过 UI、代码、数据或运行边界。尤其不能把多个未运行的子模块静态事实拼成一个已确认的跨模块联合行为。

## 适用边界

本案例最适合拥有 Delphi/VCL 源码、DFM、旧数据库目录、部分编译制品和获授权隔离运行环境的遗留业务系统。只有源码或只有 UI 时仍可复用稳定 ID、分母和主张状态，但应选择对应访问轨道，并降低不能闭环部分的状态上限。

它没有验证 Web、Java 或 .NET 的运行机制，也没有形成跨项目证据；相关栈只能复用语义核心，再用各自入口、代理、事务、异步和部署身份重新取证。案例未覆盖的产品面保持未知或 `unsupported`，不能由已完成业务集群外推。

公开页也不携带原始环境身份、账号、客户记录、业务明细或凭据。需要复现实验时，应先在目标项目重新完成授权、项目章程、运行身份和数据最小化审查。

## 来源链接

本案例仅从下列已提交来源中摘录经脱敏的事实；原始来源文档不是本公开案例的一部分，可能包含本地路径、历史测试身份和环境细节。访问与引用必须遵守授权与数据政策，本案例不得转录这些值；它也不读取当前工作区临时态或未提交的原始实验材料。

每行同时固定 source ID、仓内路径、提交和经审计的 Git blob OID。公开链接不依赖可移动分支名；blob OID 用于证明链接所指内容与审计 manifest 一致，不表示原始来源已经通过本案例的敏感信息扫描。

| source_id | phase_or_role | source_path | source_commit | blob_oid | immutable_source |
| --- | --- | --- | --- | --- | --- |
| `source:gjperp.reverse-design` | approved design | `docs/superpowers/specs/2026-07-17-ai-native-erp-reverse-engineering-design.md` | `d13d11260db5fc5286140424b182e6ab507bd983` | `6854f8d156925cf500627e9bcd8df89e8ddbec85` | [不可变提交](https://github.com/zzhongster/gjpERP/blob/d13d11260db5fc5286140424b182e6ab507bd983/docs/superpowers/specs/2026-07-17-ai-native-erp-reverse-engineering-design.md) |
| `source:gjperp.program-roadmap` | program roadmap | `docs/superpowers/plans/2026-07-18-erp-reverse-engineering-program-roadmap.md` | `0f85ffe7ebda979251335df3d28171ac186538c7` | `46bd1f4b7ba42c074b1bc064b9c599e83bef6267` | [不可变提交](https://github.com/zzhongster/gjpERP/blob/0f85ffe7ebda979251335df3d28171ac186538c7/docs/superpowers/plans/2026-07-18-erp-reverse-engineering-program-roadmap.md) |
| `source:gjperp.phase0-baseline` | Phase 0 | `docs/as-is/coverage/phase-0-baseline-report.md` | `2e7601019ee59c9cd9b1abbf328cdb1d381d6ca7` | `105986dd8fe8621e74f6e695be7a8c33b125c3e5` | [不可变提交](https://github.com/zzhongster/gjpERP/blob/2e7601019ee59c9cd9b1abbf328cdb1d381d6ca7/docs/as-is/coverage/phase-0-baseline-report.md) |
| `source:gjperp.phase2-stable-id` | Phase 2 identity | `docs/as-is/code/phase-2-schema-and-stable-id.md` | `24d428e51feefbdb9bee30595dd4a0214935b96d` | `9e45701dac8a213c65ca6749725d8dbefbb59fd3` | [不可变提交](https://github.com/zzhongster/gjpERP/blob/24d428e51feefbdb9bee30595dd4a0214935b96d/docs/as-is/code/phase-2-schema-and-stable-id.md) |
| `source:gjperp.phase1-runtime` | Phase 1 runtime | `docs/as-is/runtime/phase1-execution-report.md` | `db9883510d5ec719794707a659a4d76e72dff78a` | `9eb06de94cb56e7f495354b7a6ee2bf0274cfc59` | [不可变提交](https://github.com/zzhongster/gjpERP/blob/db9883510d5ec719794707a659a4d76e72dff78a/docs/as-is/runtime/phase1-execution-report.md) |
| `source:gjperp.phase2-runtime` | Phase 2 runtime | `docs/as-is/runtime/phase2-execution-report.md` | `24d428e51feefbdb9bee30595dd4a0214935b96d` | `37d0e948c646fc9d8b99b125cff2050a22ef4dbe` | [不可变提交](https://github.com/zzhongster/gjpERP/blob/24d428e51feefbdb9bee30595dd4a0214935b96d/docs/as-is/runtime/phase2-execution-report.md) |
| `source:gjperp.phase3-runtime` | Phase 3 runtime | `docs/as-is/runtime/phase3-execution-report.md` | `fba6908cd104f6f8f089f73062ad75509c06db1f` | `f1993582979a14960f69354f4f86d5a518bd343f` | [不可变提交](https://github.com/zzhongster/gjpERP/blob/fba6908cd104f6f8f089f73062ad75509c06db1f/docs/as-is/runtime/phase3-execution-report.md) |
| `source:gjperp.phase4-runtime` | Phase 4 runtime | `docs/as-is/runtime/phase4-execution-report.md` | `3f3fb3ec90680d4cf161ae8b7d59141eddc27a74` | `c9f6bf6c9422655bf1b93892b084717cc5d0120e` | [不可变提交](https://github.com/zzhongster/gjpERP/blob/3f3fb3ec90680d4cf161ae8b7d59141eddc27a74/docs/as-is/runtime/phase4-execution-report.md) |
| `source:gjperp.phase5-trade` | Phase 5 parent | `docs/as-is/trade/overview.md` | `30d0b0ea8fe42ce8479e84f28896999ee5dba521` | `ea5d796fd0246c57675492817a0fa28fb6b46faf` | [不可变提交](https://github.com/zzhongster/gjpERP/blob/30d0b0ea8fe42ce8479e84f28896999ee5dba521/docs/as-is/trade/overview.md) |
| `source:gjperp.phase6-finance` | Phase 6D parent | `docs/as-is/finance/overview.md` | `e8d69a48129aca0e9fd4912d2d14e72c1d459a84` | `76ec79679619bc1c46d3e742221071d7b4c61174` | [不可变提交](https://github.com/zzhongster/gjpERP/blob/e8d69a48129aca0e9fd4912d2d14e72c1d459a84/docs/as-is/finance/overview.md) |
