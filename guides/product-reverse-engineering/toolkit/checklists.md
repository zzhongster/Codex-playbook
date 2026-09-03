# 可审计阶段与技术栈检查清单

**证据成熟度：`proposed`**

**适用范围：** 用于逐项判断十阶段流程和 Delphi、Web、Java、.NET 技术切片是否达到进入或退出条件；勾选表示所列证据、产物和门禁判定均可复核，不表示执行者只是浏览过对象。

使用前先固定[项目证据仓布局](project-layout.md)和任务包。每项只有在“证据”可寻址、“产物”已验证、“门禁”由相应输入派生且当前有效时才能勾选；不满足时保持未勾选并记录未知或缺口。

## Phase 0

- [ ] PASS — 授权范围逐项列明系统、版本、账号、环境、数据、动作、有效期与禁止事项，且签署身份可复核；证据：`evidence:phase0.authorization-record` 及签名/内容哈希证据项；产物：`ART-P0-AUTH`；门禁：G0 为 `pass`
- [ ] PASS — 停止、披露、恢复和证据保全责任已由安全/隐私负责人确认；证据：`evidence:phase0.stop-owner-approval` 与恢复点核验；产物：`ART-P0-STOP`；门禁：G0 引用当前授权版本

## Phase 1

- [ ] PASS — 源码、制品、配置、数据克隆和环境身份各有时间、版本与哈希，未混用未知版本；证据：`evidence:phase1.baseline-fingerprints` 的独立指纹证据项；产物：`ART-P1-BASELINE`；门禁：G1 为 `pass`
- [ ] PASS — 八个范围维度均有稳定 ID、风险等级、纳入/排除理由和可计算目标；证据：`evidence:phase1.denominator-review` 与范围负责人确认；产物：`ART-P1-DENOM`；门禁：G1 引用冻结分母哈希

## Phase 2

- [ ] PASS — 产品表面按角色、套餐、地区、设备与前置状态记录可见性，抽样边界可复现；证据：`evidence:phase2.surface-observations` 的页面/桌面观察证据项；产物：`ART-P2-SURFACE`；门禁：G3 保持 `pending` 直至 Phase 4 完成
- [ ] PASS — 关键角色和候选场景均关联分母、进入条件、成功/失败结果与所需证据级别；证据：`evidence:phase2.scenario-review` 与角色权限核验；产物：`ART-P2-SCENARIO`；门禁：G3 的 Phase 2 输入完整

## Phase 3

- [ ] PASS — 入口、模块、部署、配置、数据和集成对象均有稳定 ID、版本身份及类型化关系；证据：`evidence:phase3.asset-inventory` 的清单哈希与定位证据项；产物：`ART-P3-ATLAS`；门禁：G2 为 `pass`
- [ ] PASS — 反射、插件、生成代码、配置路由、异步和外部依赖已进入动态边界清单而非被静态搜索遗漏；证据：`evidence:phase3.dynamic-boundaries` 与构建/部署交叉检查；产物：`ART-P3-DYNAMIC`；门禁：G2 引用盲区清单

## Phase 4

- [ ] PASS — 每个选定切片从产品入口连到实现、数据/消息和可见结果，所有边均有类型、上下文和逐边证据；证据：`evidence:phase4.vertical-links` 的节点与链接证据项；产物：`ART-P4-TRACE`；门禁：G3 为 `pass`
- [ ] PASS — 每个断点保留候选、反证、替代解释、最高主张状态和后续验证方法；证据：`evidence:phase4.gap-review` 与冲突来源索引；产物：`ART-P4-GAP`；门禁：G3 未把占位节点计为已覆盖

## Phase 5

- [ ] PASS — 运行分支的冻结协议绑定授权、环境、输入、前态、变量、预期、停止条件和恢复点；证据：`evidence:phase5.protocol-review` 与独立审批证据项；产物：`ART-P5-PROTOCOL`；门禁：G5 选择 runtime 且判定有效
- [ ] PASS — 运行结果保留首错、实际观测、关联 ID、副作用、逆序清理和独立复现，或静态分支完整记录运行缺口与人类接受；证据：`evidence:phase5.result-or-static-branch` 的结果/静态交叉证据项；产物：`ART-P5-RESULT` 或 `ART-P5-STATIC`；门禁：G5 为分支一致的 `pass`

## Phase 6

- [ ] PASS — 能力、角色、旅程、状态机、决策表、公式和异常路径逐项引用主张与证据；证据：`evidence:phase6.model-traceability` 的模型到主张抽查证据项；产物：`ART-P6-PRODUCT`；门禁：G4 为 `pass`
- [ ] PASS — 关键业务语义、跨模块不变量、历史缺陷与目标需求已分开，领域意图由具名人类确认；证据：`evidence:phase6.domain-confirmation` 与签署决定；产物：`ART-P6-SEMANTICS`；门禁：G4 引用领域确认

## Phase 7

- [ ] PASS — 九类分母按 P0/P1/P2 计算覆盖，未到达、未找到、冲突和接受项未混入已证实计数；证据：`evidence:phase7.coverage-recalculation` 的独立重算证据项；产物：`ART-P7-AUDIT`；门禁：G6 为 `pass`
- [ ] PASS — P0/P1 冲突逐项保留双方证据、决定人、期限和重开条件，未由多数票或 Agent 消解；证据：`evidence:phase7.conflict-review` 与决定记录哈希；产物：`ART-P7-CONFLICT`；门禁：G6 引用有效 `ART-P7-ACCEPTANCE`

## Phase 8

- [ ] PASS — 声明输出由固定 allow-list 生成，内容输出、子/阶段摘要、根摘要、分离冻结证明按无环顺序产生；证据：`evidence:phase8.rebuild-check` 的两次确定性重建证据项；产物：`ART-P8-FREEZE`；门禁：G7 为 `pass`
- [ ] PASS — 发布说明列明适用决策、版本边界、未知、接受风险与复核日期，目的决策人完成不可变签署；证据：`evidence:phase8.release-approval` 与签名/哈希；产物：`ART-P8-APPROVAL`；门禁：G7 只验证而不生成批准

## Phase 9

- [ ] PASS — 新版本或新证据先做影响分析，受影响门禁回退 `pending`，未影响项有可复核理由；证据：`evidence:phase9.impact-analysis` 的基线差异与依赖证据项；产物：`ART-P9-DELTA`；门禁：受影响的 G0–G7 已定向重验
- [ ] PASS — 预测、误判、漏判和样本边界被记录，方法改动没有回写旧冻结基线；证据：`evidence:phase9.calibration-review` 与前后记分卡证据项；产物：`ART-P9-CALIBRATION`；门禁：受影响的 G0–G7 有新判定与哈希

## Delphi

- [ ] PASS — DPR/DPK/PAS/DFM、继承/Action/事件、DataModule 与部署元数据按同一构建身份交叉索引；证据：`evidence:delphi.asset-cross-index` 的源码/窗体/制品哈希证据项；产物：`ART-P3-ATLAS`；门禁：G2 不含版本混用
- [ ] PASS — 代表性事件链连到数据/中间件候选及可见结果，静态与运行主张分别定级；证据：`evidence:delphi.event-trace` 的逐边证据项与实验/静态记录；产物：`ART-P4-TRACE`；门禁：G3 与 G5 均满足所选分支

## Web

- [ ] PASS — 路由、SSR/CSR/水合、DOM/可访问性、角色/套餐和响应式状态都进入产品分母；证据：`evidence:web.surface-matrix` 的授权会话与构建身份证据项；产物：`ART-P2-SURFACE`；门禁：G3 未把 bundle 存在当作可达
- [ ] PASS — 用户动作与轮询、推送、Service Worker、令牌刷新和第三方效应分别记录因果来源；证据：`evidence:web.session-provenance` 的网络/DOM/遥测关联证据项；产物：`ART-P4-TRACE`；门禁：G5 不越过后端主张上限

## Java

- [ ] PASS — Maven/Gradle、模块、启动类、Profile、条件 Bean、代理/AOP 与部署身份形成同版本图谱；证据：`evidence:java.runtime-identity` 的构建/配置/运行证据项；产物：`ART-P3-ATLAS`；门禁：G2 明示生成与反射盲区
- [ ] PASS — HTTP/RPC 入口经校验、授权、服务、事务、仓储连到 DB/outbox/message/consumer 和可见结果；证据：`evidence:java.transaction-trace` 的 trace/log/SQL/message 逐边证据项；产物：`ART-P4-TRACE`；门禁：G3 与 G5 保持事务和异步边界

## .NET

- [ ] PASS — Solution/Project/TFM、Host/IIS/Kestrel、配置/Options、DI 生命周期与发布目录绑定同一部署身份；证据：`evidence:dotnet.deployment-identity` 的项目/assembly/配置证据项；产物：`ART-P3-ATLAS`；门禁：G2 记录传统 ASP.NET/WCF/COM 条件分支
- [ ] PASS — Middleware/Endpoint 经认证、授权、服务、EF/Dapper/事务连到协议结果、Hosted Service 或消息效应；证据：`evidence:dotnet.request-trace` 的 trace/log/SQL/message 逐边证据项；产物：`ART-P4-TRACE`；门禁：G3 与 G5 不把 IL 可达性冒充已执行

## 跨阶段停止与范围变更

以下触发器优先于进度。停止后保留最小脱敏现场、最后安全状态和未清理副作用；只有表中恢复门禁满足后才可创建新版任务包继续。

| trigger_id | required_action | required_artifact | resume_gate |
| --- | --- | --- | --- |
| authorization-drift | 立即停止相关采集或运行，隔离已获材料，由有权限的人签署新版授权 | ART-P0-AUTH 与 ART-P0-STOP | 新授权及当前 G0 为 `pass` |
| version-mismatch | 立即停止合并证据，发起范围变更并重建受影响的基线、分母和追踪关系 | ART-P1-BASELINE 与 ART-P9-DELTA | 新身份通过 G0，受影响 G1–G7 回退后重验 |
| unsafe-write | 立即停止动作，执行获批恢复和残留核对，保存首错且升级安全负责人 | ART-P5-EFFECTS 与 ART-P0-STOP | 安全负责人确认处置且 G0 再次 `pass` |
| p0-conflict | 立即停止发布，禁止覆盖、删除或静默选择任一证据，由具名人类决定拆分或接受 | ART-P7-CONFLICT 与 ART-P7-ACCEPTANCE | 冲突仍可见且 G0、G6、G7 按影响重验 |

## 相关

- [端到端工作流](../core/end-to-end-workflow.md)
- [技术栈指南](../README.md#技术栈导航)
- [覆盖、质量与冻结](../core/coverage-quality-and-freeze.md)
- [任务包提示库](prompts.md)
