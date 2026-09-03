# 数据、消息与基础设施逆向工程指南

**证据成熟度：`proposed`**

**适用范围：** 适用于在明确授权下盘点和追踪产品实际依赖的数据存储、缓存、搜索、消息、调度、文件/对象交换、第三方集成、网关、部署平台和可观测性；不授予扫描网络、读取秘密、访问生产数据、触发任务、重放消息或修改任何基础设施的权限。

本页连接[端到端工作流](../core/end-to-end-workflow.md)中的产品切片与跨服务基础设施。开始前必须通过[授权、隐私与安全](../core/authorization-privacy-and-safety.md)的 G0，每类控制面、数据面、日志、运行探针和写操作分别授权；所有证据、主张与类型化链接沿用[证据与置信度](../core/evidence-and-confidence.md)。

所有组件类别和拓扑都按实际证据条件化。不得把数据库、缓存、搜索、消息、任务、对象存储、网关或容器平台写成必经层；单体文件程序、托管服务、自研中间件或没有某类组件都可能是正确事实。未发现只能限定为已搜索分母内“未发现”，不能推成全局不存在。

## 组件记录契约

每个实际发现的组件都必须逐项记录下表字段；不适用写 `not-applicable` 并说明理由，未知值写 `unknown` 并附验证缺口。组件记录描述一个有明确版本和边界的实例/服务，不用产品名、主机别名或连接串代替稳定 ID。

| 字段 | 记录要求 |
| --- | --- |
| `component ID` | 限定稳定 ID、组件类别和显示名称 |
| `owner` | 业务、运行与数据责任方；未知时记录确认人 |
| `version` | 软件版本、服务 revision、image digest 或内容哈希 |
| `namespace/tenant` | namespace、cluster、account、project、tenant 等脱敏隔离边界 |
| `schema` | 数据、消息、索引、文件或 API schema 及版本 |
| `readers` | 读取者稳定 ID、读取入口与权限角色 |
| `writers` | 写入者稳定 ID、写入入口与权限角色 |
| `consistency` | 原子范围、可见时点、复制或最终一致性边界 |
| `ordering` | 全局/分区/key/对象级顺序与无保证区域 |
| `idempotency` | key、作用域、保留窗、并发与响应重放语义 |
| `retry` | 所有者、触发条件、次数、退避、抖动与终态 |
| `retention` | 数据、消息、日志、备份与墓碑保留/删除规则 |
| `encryption` | 传输/静态加密机制与密钥引用；不保存密钥值 |
| `backup` | 覆盖对象、频率、不可变性、校验与责任方 |
| `restore` | 恢复单元、依赖顺序、演练证据、RPO/RTO 与回切 |
| `observability` | log/metric/trace/audit、关联字段、采样和访问边界 |
| `failure effect` | 对用户、数据、下游、积压、恢复和告警的影响 |

读者/写者、owner 和 failure effect 是独立字段：平台团队管理集群不代表拥有业务语义，调用者存在也不证明其已执行。每次版本、tenant/namespace 或 schema 变化都要产生新版本记录并保留历史。

## 关系型数据库与 NoSQL

关系型数据库按 engine/version、cluster/instance、database、schema/catalog、表/视图/过程、约束、索引、分区和复制拓扑登记；NoSQL 按实际模型记录 keyspace/database、collection/table、partition/shard key、document/item schema、secondary index 和 change feed。连接地址和凭据不进入知识库，只保存受控引用和脱敏身份。

从业务入口分别追踪读者、写者、账号角色、connection pool、路由/读写分离、query/command、事务与可见结果。ORM 映射、SQL、存储过程、触发器和数据库 job 都是可选实现；对象存在只支持结构事实，运行 SQL/trace 或副本状态才支持限定执行/复制主张。

迁移文件、schema registry 或 desired state 不证明目标实例已应用。记录 migration/checksum、目标 schema 版本、兼容窗、回滚/roll-forward 和复制延迟；只读检查也需独立授权，验证默认在脱敏副本中进行。

## 缓存

按实际发现区分进程内、分布式、HTTP/CDN、查询/ORM 和业务物化缓存。登记 key 构造、租户/角色维度、value schema、TTL、容量/淘汰、读写者、序列化、加密、失败回退和 stampede 控制；client 依赖或配置 key 存在不证明缓存启用或命中。

对 cache-aside 链路从数据库提交追到删除/更新失效、事件传播、miss、回填和用户读取；对 write-through/write-behind 记录真正的 durable owner 与失败窗。提交成功不证明失效成功，删除成功不证明所有副本/CDN 已刷新，命中率也不证明缓存值正确。

缓存清除、过期缩短、故障注入和重复请求都是写/扰动操作，只能在获准隔离环境进行。无法观察 key 或 payload 时，保存哈希/计数/时间窗和候选构造规则，不导出敏感值。

## 搜索与索引

登记 engine/service version、cluster/index/collection、索引 schema、mapping/analyzer、文档 ID、routing/tenant、source 数据、写入器、refresh/commit、别名、权限过滤、retention 和重建流程。搜索 SDK 或索引模板存在不证明目标索引已部署、已写入或被查询。

端到端索引链区分数据库提交、CDC/outbox/event、indexer 消费、transform、bulk 写入、刷新、别名切换、查询与可见结果。数据库行存在不证明索引已刷新；搜索缺失不证明源数据不存在；索引文档存在也不证明当前别名或权限允许用户看到。

验证删除传播、重放、乱序、schema 兼容和重建时只使用合成哨兵与隔离索引。生产 reindex、别名切换或 mapping 修改属于高风险写操作，未获专门批准立即停止。

## 消息与 Outbox/Inbox

消息组件按 broker/service、namespace/tenant、topic/queue/stream、partition/shard、consumer group/subscription、schema、key、producer、consumer 和版本登记。逐项验证 ack/commit、顺序范围、并发、幂等、retry、delay、dead-letter/死信、retention、重复与积压；“至少一次”或“有序”必须限定 broker、client、配置、key 和副作用。

Outbox 方法需要证明业务写与 Outbox 写的原子范围、relay 选择/锁、发布标记、崩溃窗口和重复发布。Inbox 方法需要证明 message ID、去重 key/唯一约束、处理结果、保留窗和与业务副作用的事务关系；表名或类名包含 Outbox/Inbox 不证明协议完整。

一条完整链分别记录业务提交、relay 读取、publish 接受、broker 持久化、delivery attempt、consumer ack/commit、Inbox/业务副作用和用户可见终态。未经授权不得创建 consumer、移动 offset、purge 队列、requeue 或向生产 topic 发送探针。

## 调度任务

只在实际发现时登记应用内 scheduler、平台 Cron、数据库 job、云调度器、队列触发或人工批处理。记录调度注册、表达式、时区、calendar、leader/lock、misfire、并发策略、部署副本、触发输入、deadline、retry、补跑和运行记录；定义存在不证明启用或按时执行。

端到端方法区分计划时间、调度器触发、任务领取、开始、heartbeat、业务 checkpoint、副作用、完成/失败、重试与告警。运行记录要绑定 job definition version、executor revision 和数据窗；同一时间出现日志只能作为候选，不证明因果。

手工触发、暂停、补跑、改时区或抢锁会改变系统状态，必须在隔离环境另行授权。只读权限不足时，用配置与历史记录形成静态/观察主张，并明确无法验证的 misfire 和并发语义。

## 文件与对象存储交换

登记 bucket/container/share、namespace/tenant、对象 key/文件路径的脱敏模式、内容 schema、命名版本、producer、consumer、ACL 角色、内容哈希、metadata、encryption、retention 和 lifecycle。目录或对象存在不证明上传完成、消费者已处理或内容可信。

端到端文件交换追踪临时名、分块/上传 session、校验和、原子重命名或完成标记、通知/轮询、claim/move、解析、隔离/错误目录、重复导入和业务终态。对象存储通常没有文件系统式原子重命名时，应按实际 copy/put/delete 与一致性语义记录，不能套用本地文件假设。

只使用脱敏合成文件和一次性目录/bucket prefix；不得下载未授权对象、枚举租户 key 或覆盖同名生产文件。删除、retention 变更和恢复都需单独批准并保留前后身份。

## 第三方集成与回调

登记第三方系统稳定 ID、owner、合同/API/schema 版本、脱敏 endpoint、认证方式的引用、调用方向、网络边界、timeout、retry、rate limit、幂等和数据分类。SDK、URL 或 webhook 配置存在只证明候选，不证明连接成功或目标租户采用。

出站链区分业务提交、request 构造、发送 attempt、第三方接受、同步响应、异步处理和本地终态；第三方回调链区分签名校验、时间戳/nonce、重放窗口、schema 解析、关联 ID、幂等、业务副作用、应答和终态。2xx 仅说明对应协议步骤，不自动证明远端业务成功。

不得主动调用未批准 endpoint、突破 rate limit、伪造签名、重放真实回调或收集第三方凭据。无法运行时，用契约、代码、配置和历史脱敏日志建立分层证据，并把远端内部行为保持 `unsupported`/`inferred`。

## 网关

API gateway、reverse proxy、ingress、service mesh gateway 或应用内代理只在证据出现时建模。记录版本、路由、host/path/method 匹配、rewrite、认证、授权、限流、重试（retry）、超时（timeout）、circuit breaker、TLS、header 传播、upstream、健康与配置 revision。

desired config、控制面接受、数据面加载和请求实际命中是四个事实。网关 2xx/5xx 不能唯一定位 upstream 终态；retry 可能放大副作用，timeout 可能早于下游完成，需用 trace/request ID 与服务、数据、消息观察连接。

禁止枚举隐藏 upstream、改路由、关闭认证或用越权 header 探测。配置读取范围、管理 API 与数据面捕获都必须单独授权并最小化。

## 容器与编排平台

容器分支记录 Dockerfile/build 输入、base image digest、应用 image digest、entrypoint、user、filesystem/mount、network 与发布 attestation；编排分支记录 cluster/namespace、workload revision、pod/task、副本（replica）、rollout、service、ingress、readiness/liveness/startup、资源限制、网络策略（network policy）和 service account 引用。

manifest/Helm/Kustomize/IaC 是 desired state，不证明控制面采用；控制面对象不证明每个实例已加载相同 image/config；readiness 也不证明业务路径或下游健康。滚动发布期间按 instance + image digest + config revision 分开关联，不能用逻辑服务名合并观察。

`exec`、port-forward、debug container、scale、restart、rollout 和 secret 查看都会改变访问或状态，必须单独授权。默认只读元数据并脱敏 namespace/tenant，无法唯一绑定实例时限制主张状态。

## 秘密引用与配置边界

只登记秘密引用的稳定 ID、用途、owner、provider 类型、scope、轮换策略、消费者和访问控制；不得读取或保存秘密值、token、私钥、密码或完整连接串。日志、错误页、环境 dump、core dump 和反编译常量都按敏感数据处理。

配置存在与实际注入、进程解析、连接成功和业务使用是不同主张。记录 source/provider、优先级、版本、挂载/注入点、reload 生命周期和脱敏最终选择证明；不能为确认“是否工作”而输出整个环境。

发现明文凭据、跨租户引用、过度权限或意外泄露时停止采集，保护现有证据并按组织流程通知授权负责人；不在逆向任务中自行轮换或验证凭据。

## 可观测性

分别盘点应用/平台日志、metric/指标、trace/span、audit、事件和告警的 owner、schema、版本、时钟、采样、retention、redaction 与访问边界。日志模板或 instrumentation 代码存在不证明 exporter 已启用、后端收到或目标 trace 被采样。

用 request/message/job/business 关联 ID 连接组件，同时保留各系统时钟偏移和丢失窗口。追踪失败时保存首个失败、后续 retry/包装、最终协议结果和副作用；仅靠时间邻近、相同文本或共享 host 不建立确定因果边。

可观测性本身可能泄露 PII、凭据和 payload，采集需字段 allow-list、脱敏和最短保留。不得通过扩大采样、开启 debug 日志或部署 agent 绕过单独授权。

## 备份与恢复

对数据库、消息、搜索、对象、配置和密钥引用分别记录覆盖范围、备份频率、快照一致性、增量链、加密、保留、不可变性、异地副本、校验和 owner。备份存在不等于可恢复，也不证明包含同一业务时间点的跨组件一致快照。

恢复主张必须来自获准恢复演练：记录目标隔离环境、恢复顺序、依赖、schema/version、RPO、RTO、完整性/业务校验、失败与回切。只检查文件可读或供应商状态不能升级为“恢复可用”。

禁止在生产目标覆盖恢复、删除快照或降低保留。无法演练时，分别记录备份配置 `statically-supported`、控制面对象 `observed` 和恢复能力 `unsupported`，并列入风险队列。

## 所有权、一致性与失败影响

为每个数据对象、消息、索引、缓存 key 空间、文件契约和集成确定业务语义 owner、写入 authority、运行 owner 与故障响应 owner。多个 writer 并不自动违规，但必须记录冲突解决、版本/并发控制和谁能裁决；禁止两个未协调的 writable authority 对同一事实各自宣称权威。

一致性拆成单组件原子性、复制可见性、跨资源协调、最终一致窗口、补偿和用户可见完成。ordering、idempotency 与 retry 逐层记录，不能用一次成功或厂商术语声称 exactly-once、全局顺序或零数据损失。

failure effect 需要覆盖入口响应、已提交数据、积压、重复、乱序、陈旧读、恢复步骤、告警与用户提示。使用预先批准的故障实验或真实脱敏事故证据；无法安全注入时，保留静态 failure hypothesis 与验证缺口。

## 配置存在与部署行为

配置存在不得直接声称组件已经部署或产生业务行为。源码声明、desired state、控制面装配、数据面健康与特定业务流量分别建证据项；只有输入、版本、实例和观察面可关联时才提升相应窄主张。

| 证据面 | 最高起始状态 | 可以支持 | 不可外推 |
| --- | --- | --- | --- |
| 源码/配置文件中的组件声明 | `statically-supported` | 指定输入版本中的依赖、地址引用与配置候选 | 不证明组件已部署、已连接或被调用 |
| 控制面/部署清单中的装配事实 | `observed` | 指定 revision 声明的实例、版本、路由与注入 | 不证明运行实例健康或业务流量到达 |
| 已关联运行观测 | `runtime-confirmed` | 指定请求、消息、任务或哨兵实际经过的组件与结果 | 只限绑定部署、配置、输入和时间窗的行为 |

Outbox/Inbox、调度、缓存失效、搜索索引、文件交换和第三方回调都必须从触发到终态逐段取证。中间某段不可达时保留缺口、candidate set 和验证计划，不以配置或相邻日志补齐整链。

## 基础设施链路示例

下面是中性 Outbox—消费—搜索投影教学链。链路只示范已发现分支，不规定通用拓扑；没有消息/搜索时不创建对应节点。内部链从“业务数据与 Outbox 原子结果”开始，使用 relay、message、consumer、Inbox 去重记录和搜索文档候选；可见结果由独立运行证据验证。

表格连通只证明记录内部一致，不证明目标产品真的运行过。每条链接必须引用已登记证据与上下文；`reads` 按数据流解释为数据对象到读取者，任何未解析 ID、空引用或越界状态都阻止发布。

### 节点注册表

| 稳定 ID | 类型 | 当前状态 | 边界 |
| --- | --- | --- | --- |
| `data:sample.infra-atomic-business-outbox` | `atomic-business-outbox-outcome` | `statically-supported` | 同一事务中的业务与 Outbox 写入候选 |
| `asset:sample.infra-outbox-relay` | `outbox-relay` | `statically-supported` | 已发现的 relay 候选 |
| `integration:sample.infra-message` | `message` | `statically-supported` | 已登记 topic、schema 与 key 候选 |
| `asset:sample.infra-consumer` | `consumer` | `statically-supported` | 已登记 group 与 handler 候选 |
| `data:sample.infra-inbox-record` | `inbox-record` | `statically-supported` | message ID 去重记录候选 |
| `data:sample.infra-search-document` | `search-document` | `statically-supported` | 投影写入和刷新候选 |
| `claim:sample.infra-later-visible` | `visible-claim` | `runtime-confirmed` | 只限已回放查询与可见结果 |

### 证据注册表

| 证据 ID | 已登记身份 |
| --- | --- |
| `evidence:sample.infra-source` | 事务、relay、consumer 与投影静态输入哈希 |
| `evidence:sample.infra-deployment` | 组件版本、namespace、revision 与配置引用 |
| `evidence:sample.infra-runtime` | message/job/trace 关联与脱敏副作用 |
| `evidence:sample.infra-visible-run` | 独立查询回放与用户可见结果 |

### 上下文注册表

| 上下文 ID | 已登记边界 |
| --- | --- |
| `context:sample.infra-source-version` | 源码、schema、配置与生成物哈希 |
| `context:sample.infra-deployed-chain` | 组件版本、namespace/tenant、revision 与实例 |
| `context:sample.infra-authorized-scenario` | 当前 G0、合成哨兵、角色与时间窗 |

### 类型化链接

| 链接 ID | 源 | 关系 | 目标 | 状态 | 证据引用 | 上下文引用 |
| --- | --- | --- | --- | --- | --- | --- |
| `trace-link:sample.infra-relay-reads-outbox` | `asset:sample.infra-outbox-relay` | `reads` | `data:sample.infra-atomic-business-outbox` | `statically-supported` | `evidence:sample.infra-source` | `context:sample.infra-source-version` |
| `trace-link:sample.infra-relay-emits-message` | `asset:sample.infra-outbox-relay` | `emits` | `integration:sample.infra-message` | `statically-supported` | `evidence:sample.infra-source` | `context:sample.infra-source-version` |
| `trace-link:sample.infra-message-calls-consumer` | `integration:sample.infra-message` | `calls` | `asset:sample.infra-consumer` | `statically-supported` | `evidence:sample.infra-source` | `context:sample.infra-source-version` |
| `trace-link:sample.infra-consumer-writes-inbox` | `asset:sample.infra-consumer` | `writes` | `data:sample.infra-inbox-record` | `statically-supported` | `evidence:sample.infra-source` | `context:sample.infra-source-version` |
| `trace-link:sample.infra-consumer-writes-search` | `asset:sample.infra-consumer` | `writes` | `data:sample.infra-search-document` | `statically-supported` | `evidence:sample.infra-source` | `context:sample.infra-source-version` |
| `trace-link:sample.infra-search-supports-visible` | `data:sample.infra-search-document` | `supports` | `claim:sample.infra-later-visible` | `inferred` | `evidence:sample.infra-runtime` | `context:sample.infra-deployed-chain` |
| `trace-link:sample.infra-runtime-validates-visible` | `evidence:sample.infra-visible-run` | `validates` | `claim:sample.infra-later-visible` | `runtime-confirmed` | `evidence:sample.infra-visible-run` | `context:sample.infra-authorized-scenario` |

从原子结果到 relay 的第一条边按 `reads` 的数据流方向解析，因此链可以连续到搜索文档和可见主张；Inbox 是消费副作用和去重证据，不表示它天然保证 exactly-once。若部署/运行证据不足，静态链保持静态，可见结果的独立确认不升级内部边。

## 有序工作流

1. 通过 G0 固定系统、环境、tenant/namespace、账号、数据级别、允许控制面/数据面和禁止操作。
2. 从产品旅程和跨模块不变量选切片，冻结数据库、缓存、搜索、消息、任务、文件、集成、网关和部署组件分母。
3. 为每个实际组件填写完整记录契约，绑定 owner、version/digest、schema、readers/writers、一致性与失败影响。
4. 分开登记源码/配置声明、控制面装配、运行实例与业务流量，不由配置存在推断部署行为。
5. 从触发向终态追踪同步读写；遇到异步时用业务哨兵和关联 ID 连接 Outbox/Inbox、job、cache invalidation、index、文件或 callback。
6. 逐段验证 ordering、idempotency、retry、retention、encryption、observability 和失败窗口；不可观察处保留候选与缺口。
7. 只有相应授权与一次性环境已验证时，执行只读探针或合成数据实验，并保存首个失败、清理、完整性和恢复结果。
8. 按 owner 复核产品语义与基础设施主张，审计断链、冲突、覆盖、备份/恢复证据和停止记录，再进入冻结门禁。

完成后把技术组件映射回业务能力、规则、数据对象和用户可见结果，而不是只交付基础设施清单。结构校验通过只证明契约齐全，不证明任何目标部署成立。

## 停止与安全边界

- 未绑定当前 `ART-G0-AUTH` 或 `verdict` 不为 `pass` 时，不读取控制面、数据面、日志或备份，也不执行探针。
- 禁止端口/网络扫描、租户/对象枚举、凭据提取、绕过访问控制、生产写入、消息重放、offset 移动、缓存清除、任务触发、索引切换或恢复覆盖。
- 发现授权漂移、版本/tenant/namespace 不匹配、非合成数据、意外写入、未知外发、敏感信息泄露或无法恢复时立即停止；保存首个失败并通知负责人。
- 重新授权并确认隔离、回滚与新身份后，创建新的实验和证据记录；不得覆盖旧失败或沿用旧 gate 判定。
