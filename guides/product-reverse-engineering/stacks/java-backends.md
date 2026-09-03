# Java 后端产品逆向工程指南

**证据成熟度：`proposed`**

**适用范围：** 适用于在明确授权下分析 JVM 上的 Java 后端，包括 Maven/Gradle 源码工程、JAR/WAR 与 class 制品、配置和部署元数据，以及另行获准的日志、只读数据库和运行观察；不授予构建、下载依赖、执行代码、读取秘密、访问生产数据或修改任何环境的权限。

本页把通用方法落到 Java 服务端栈。开始前必须通过[授权、隐私与安全](../core/authorization-privacy-and-safety.md)的 G0；只有部分源码、制品或元数据时使用[灰盒访问轨道](../access-tracks/gray-box.md)，完整源码可读时使用[白盒访问轨道](../access-tracks/white-box.md)，而构建、日志、调试、数据库和运行仍分别授权。所有证据项、主张状态、限定稳定 ID 和类型化链接沿用[证据与置信度](../core/evidence-and-confidence.md)，运行实验沿用[运行时实验](../core/runtime-experiments.md)。

## 构建与依赖图

先冻结仓库提交或工作树、构建根、wrapper、JDK/工具链版本、离线缓存状态与内容哈希。Maven 盘点父子 POM、modules、dependencyManagement/BOM、profiles、插件、生成源码和 effective model；Gradle 盘点 settings、included builds、version catalog、buildSrc/约定插件、configuration、task、toolchain 和 wrapper。目录邻近或相同 group/name 不等于模块依赖。

把依赖分为声明依赖、解析依赖、打包依赖和运行加载事实。依赖树需保存坐标、版本选择原因、scope/configuration、排除、冲突结果、仓库来源与工具版本；插件和 annotation processor 另建节点。只有获准执行构建且网络、插件脚本与输出目录已审查时，才运行 Maven/Gradle 命令；否则从已登记文件形成 `statically-supported` 构建图并记录解析缺口。

构建成功只证明该输入与工具组合能产生制品，不证明该制品已经部署。将源码身份、有效构建模型、生成输入、测试、JAR/WAR 哈希、镜像层和部署身份分别登记，使用 `derived-from` 等类型化链接连接，不用版本字符串代替内容身份。

## 模块与启动身份

模块盘点覆盖聚合根、可执行应用、共享库、Web 模块、消费者、批任务、迁移工具和生成器；包名与目录名只是线索。对每个模块登记稳定 ID、构建坐标、输入哈希、输出制品、依赖方向和可能的进程/部署单元，循环、可选模块和运行时插件保持显式。

启动入口按证据选择：`public static void main`、manifest `Main-Class`、Spring Boot launcher、Servlet initializer、`web.xml`、应用服务器部署描述、容器 entrypoint、启动脚本或框架生成入口都可能出现，但没有任何一个是通用必需项。JAR/WAR 内有一个入口类只支持制品结构主张；启动脚本、容器命令和平台配置决定哪个候选实际使用。

建立“模块源码/提交 → 构建输入 → JAR/WAR 哈希 → 启动入口候选 → 部署实例 → JVM 进程”的启动身份链。端口、应用名、线程名或进程显示名不能替代制品哈希、镜像 digest、JVM/Java 版本、启动参数和部署 revision；任何断链都限制为静态或部署事实。

## 框架识别与条件分支

Spring Boot、Spring MVC、Jakarta REST、Quarkus、Micronaut 与 Vert.x 都是条件分支；Jakarta API 的存在也不自动确认具体容器或实现。只为实际发现且证据可定位的框架组件建节点和边，记录来源坐标、注解/注册、启动装配、配置条件、部署身份和运行观察。

Spring 可从启动类、auto-configuration imports、bean 定义、component scan、Actuator 元数据候选和条件报告建立结构；Jakarta REST 可从 `Application`、资源类、provider 与容器描述建立结构；Quarkus、Micronaut、Vert.x 或其他框架使用各自实际出现的构建插件、生成元数据、注册表和启动入口。通用框架文档只说明能力，不证明目标应用启用该能力。

可能是纯 Servlet、JAX-RS、gRPC、消息消费者、命令行或自研容器，也可能组合多个分支。不得把 Spring、Jakarta、JPA 或消息系统写成必经层；没有发现时记录已搜索分母、版本和工具，不创建占位框架节点，也不声称全局不存在。

## 配置、Profile 与环境优先级

枚举源码默认值、properties/YAML/XML、profile 文件、JVM system property、环境变量、命令行、Servlet/JNDI、远程配置、feature flag、挂载文件和平台注入；密钥只记录秘密引用的角色与来源，不读取或保存值。相同键在构建时、启动时和请求时可能由不同机制解析，应分别登记加载点和生命周期。

配置优先级必须按每个部署实测，并绑定框架/库版本、激活 profile、启动参数、环境、远程配置 revision 和最终值的脱敏证明；不得假定一条跨框架、跨版本的固定优先级。源码中的默认值、配置文件存在、部署清单注入和进程实际解析值是四个不同事实。

profile 名称不证明运行环境，环境变量名不证明值已注入，远程配置条目不证明客户端已获取。无法获准读取最终解析值时，保留候选优先级、冲突键和判别方法；不得通过打印整个环境或错误页来提取凭据。

## HTTP/RPC 入口与过滤链

从明确产品/API 入口向内追踪协议、方法、媒体类型、路由模板、参数绑定、响应和错误契约。Servlet mapping、Spring MVC/WebFlux handler、Jakarta REST resource、gRPC service、GraphQL resolver 与自研 dispatcher 都是条件入口；注解扫描命中只是静态候选，不能证明当前部署注册或流量到达。

过滤器链按真实机制区分 Servlet Filter、framework interceptor、reactive WebFilter、JAX-RS filter、gRPC interceptor、网关和容器层。记录顺序来源、匹配条件、认证上下文、请求改写、短路、异常与响应改写；配置顺序与观察顺序分别成证据，不以常见框架默认值补齐。

路由注册、过滤链与上游代理/网关分别建节点。运行相关性需要同一版本场景中的 route/handler 名、trace/span、请求关联 ID 或经批准探针；HTTP 状态相同不证明经过同一处理器，RPC 接受也不等于业务完成。

## 控制器、服务与仓储边界

控制器、应用服务、领域服务和 repository/DAO 是分析标签，不是每个工程必须存在的层。通过接口实现、构造注入、调用点、模块边界、测试和运行关联识别实际责任；类名或 package 包含 `controller`、`service`、`repository` 只提供候选。

控制器关注输入绑定、协议响应和异常映射；服务关注用例编排、规则、事务所有权与外部效应；repository/DAO 关注数据访问。若逻辑直接位于 handler、entity、mapper 或 SQL 中，就按证据描述真实结构，不能为了套分层架构移动责任或创建占位边。

每次纵向追踪要记录参数/DTO/领域对象/持久化对象之间的转换和字段损失，并区分同步返回、事务提交与后续可见结果。接口调用只证明静态关系；动态 bean 选择、条件实现或远程 client 需要配置和部署证据才能唯一解析。

## DI、代理、AOP、反射与生成代码

盘点构造器/字段/方法注入、bean 或 provider 注册、qualifier、scope、生命周期、条件装配和循环依赖。注解、反射、自动配置、`ServiceLoader`、模块层、代理、字节码增强和运行时注册均可能产生静态搜索看不到的边；每条动态边保留候选集合、cardinality 和解析证据。

只有证据确认使用相应代理机制时，才提出代理拦截与 self-invocation 问题；普通对象或非代理调用不得套用该结论。先确认 JDK interface proxy、class proxy、weaving、agent 或其他增强机制，再检查 final/private 方法、代理取得方式、调用方向和实际 advice；“有 AOP 依赖”不证明目标对象被代理。

Lombok、MapStruct、annotation processor、jOOQ/JPA metamodel、protobuf/gRPC stub 与框架索引等生成代码要追到生成器版本、输入和输出哈希。生成代码、手写源码、反射注册和编译器 synthetic/bridge 成员分别标记；缺失生成输出时不能凭调用处补写实现。

## 校验、认证与授权

输入校验分别追踪协议解析、手写校验、Jakarta Bean Validation/框架校验、业务守卫和数据库约束。记录校验组、级联、默认值、时点、错误字段、状态码与是否产生副作用；注解存在不证明触发了 validator，客户端校验也不替代服务端校验。

认证记录身份来源、令牌/会话角色、网关或过滤器、principal 传播、过期/撤销和服务身份，但不保存凭据。授权按路由、方法、领域对象、数据行/租户和消费者分别定位；入口注解、方法安全、policy engine 和查询过滤是不同控制点，任一层允许或拒绝都不能推广成全局策略。

运行验证只使用授权内账号、租户与正常对象 ID，记录允许和拒绝的可观察结果。隐藏端点、修改令牌、猜测租户或绕过鉴权不属于取证；源码中的策略表达可支持静态主张，只有绑定部署和场景的执行结果可支持限定运行主张。

## 事务边界与传播

定位声明式注解、程序式 transaction manager、JTA、数据库事务和框架 callback，登记开始、加入/新建、挂起、提交、回滚、资源参与者、隔离级别和 rollback 规则。事务传播不得仅凭注解名称推定；必须结合代理/增强机制、实际调用边、manager 选择、异常类型和运行配置判断该调用是否进入预期事务。

事务不会按假设跨越异步边界。线程池、reactive pipeline、消息发布、远程 RPC 与调度执行都可能切断线程本地事务或另开事务；只有实现与 trace/数据库观察共同支持时才建立跨阶段一致性主张。`@Async`、future 或 reactive 类型存在不能自动裁决事务上下文。

区分数据库写入尝试、事务提交、响应发送、Outbox 提交、消息发布和消费者提交。回滚规则、嵌套/savepoint、只读提示、多个数据源和 chained/JTA 协调均按实际发现追踪；缺少运行证据时最多形成限定静态路径。

## 持久化、SQL 与迁移

JPA/Hibernate、MyBatis、JDBC 与动态 SQL 都按实际发现选择，也可遇到 jOOQ、R2DBC、自研 DAO、存储过程、文件或无数据库分支。登记数据源、连接角色、schema/catalog、事务 manager、mapper/entity/query、完全限定数据库对象与字段；只为有证据的技术建边。

JPA/Hibernate 映射、级联、flush、dirty checking、乐观锁和二级缓存属于实现候选。关系的 lazy/eager 是否在当前路径触发、访问发生在事务内外、序列化是否追加查询、批量策略是否形成 N+1，都必须作为证据问题记录，并以 SQL/trace、统计或获准运行结果回答，不能由默认 fetch 类型直接外推。

MyBatis XML/注解 mapper 需展开 include、result map、provider 和条件片段；JDBC 追踪参数绑定、批处理、generated key 和资源边界；动态 SQL 保存模板、输入来源、候选对象和无法静态解析部分。SQL 拼接、schema 别名、路由数据源或存储过程不能靠短名自动连边。

Flyway、Liquibase、自研迁移和 ORM schema generation 都是条件分支。迁移文件存在只证明制品内容；部署是否执行、顺序、checksum、repair/baseline 和目标 schema 状态需部署或只读数据库证据，且数据库读取与任何迁移执行分别授权。

## 消息、Outbox 与消费者

消息代理、Outbox 和消费者都是可选分支。只有发现生产/消费注册、配置、topic/queue 稳定 ID、序列化 schema、部署和可达入口时才建图；Kafka、JMS、AMQP、RabbitMQ、Pulsar 或云 SDK 的依赖存在，只说明库可用。

不能仅因依赖中出现消息库就推定重试、顺序或投递语义。对实际分支分别取证 ack/commit、delivery attempt、分区/组、prefetch、并发、死信、延迟、重复、乱序、背压和 poison message；“至少一次”“有序”“恰好一次”等结论必须限定 broker、client、配置、key、事务与消费副作用。

Outbox 需要证明业务写与 outbox 写的事务关系、relay 选择和锁定、发布标记、崩溃窗口、重复发布与消费者去重。表名带 `outbox` 或事务内调用 producer 都不证明原子发布；消息消费成功也不证明用户已看到最终结果。

## 定时任务与异步执行

搜索 `ScheduledExecutorService`、Quartz、Spring scheduling、Jakarta timer、批处理框架、平台 Cron、队列触发器和自研轮询，但只登记实际出现的机制。注解或 job 类存在不证明启用；需要配置开关、调度注册、时区、leader/lock、misfire、并发策略、部署副本数与运行记录。

异步执行登记 executor、队列容量、拒绝策略、线程/虚拟线程、context propagation、超时、取消、重试和关闭语义。请求的安全/租户/trace 上下文、事务、MDC 和 class loader 不假定跨线程传播；提交成功、开始执行和业务完成是不同事件。

任务与消费者可能没有 HTTP 上游，应从调度/消息入口独立建立切片。若它们由请求触发，使用关联 ID、业务哨兵和时间线连接，时间邻近只能作为候选，不能替代因果证据。

## 缓存与搜索

缓存按本地缓存、分布式缓存、HTTP/CDN、ORM 缓存和框架抽象的实际使用建模。记录 key 构造、租户/权限维度、value schema、TTL、写入/失效、穿透、并发填充和失败回退；`@Cacheable` 或 Redis client 存在不证明某方法被代理、缓存命中或跨实例一致。

将数据库提交、cache aside/write-through、事件失效和用户可见结果放在时间线上。命中率指标只能说明其口径内的测量，不能证明返回值正确；缓存清除属于写操作，必须单独授权并在隔离环境中执行。

搜索分支记录索引 schema、分析器、文档 ID、写入/刷新、别名切换、权限过滤、删除传播和重建。数据库行存在不证明索引已刷新，搜索结果缺失也不证明源数据不存在；Elasticsearch/Lucene/OpenSearch 依赖只形成技术候选。

## 异常映射

从抛出点、cause 链、框架边界和异步完成追到协议结果。`@ControllerAdvice`/exception handler、Jakarta `ExceptionMapper`、gRPC status mapper、reactive error operator、Servlet error page 与网关重写都是条件机制；记录优先级、匹配范围、包装/解包、日志和响应 schema。

区分输入校验、认证/授权拒绝、业务冲突、依赖失败、超时、并发失败和未知故障，并把 HTTP/RPC 状态、机器码、用户文案、重试提示、事务结果和消息状态分别记录。捕获异常并返回 2xx、异步失败晚于响应或统一错误处理器掩盖根因都需要端到端观察。

日志中出现异常不等于请求失败，HTTP 500 也不能唯一定位内部异常。静态 catch/throw 路径最高支持静态候选；运行确认须绑定同一请求/消息身份、部署版本、首个失败与最终结果。

## 重试、幂等与一致性

分别识别客户端、网关、HTTP/RPC client、数据库、事务、消息代理、消费者和 job 的重试所有者。记录触发异常/状态、次数、退避、抖动、超时预算、不可重试条件与终态；依赖自带 retry 模块或 `@Retryable` 不证明目标路径启用，更不证明重复副作用安全。

幂等机制可能是请求 key、业务唯一键、数据库约束、去重表、消息 ID、状态机守卫或自然幂等操作。记录 key 来源、作用域、保留窗口、并发竞争、失败缓存、响应重放和清理；未经批准不得主动重复生产请求来“证明”幂等。

把本地原子性、跨资源协调、Outbox、补偿、最终一致性和用户可见完成分成独立主张。只有实际不变量、失败窗口和对照实验才能限定一致性保证；框架营销术语、接口命名或一次成功不能证明 exactly-once 或全局一致。

## 仅编译制品与反编译边界

对每个 JAR、WAR、嵌套 JAR、class、容器镜像层和原始清单登记制品 SHA-256、大小、来源、Java/class 版本、manifest/module descriptor、依赖与 package 元数据、签名可用性、调试符号可用性以及封装/混淆迹象。保存中央目录、`pom.properties`、服务注册、框架索引、资源和部署描述的原始哈希；时间戳与文件名只作线索。

任何 `javap`、字节码扫描、反编译、解包或 SBOM 派生输出都要记录输入哈希、命令/参数、JDK、反编译器与工具版本、插件版本和输出哈希。class 的 Signature、MethodParameters、LineNumberTable、LocalVariableTable、注解及 Kotlin/Scala 元数据分别记录是否存在，不能用一个“有符号”布尔值概括。

反编译结果不是原始源码，不得据此解释开发者意图。优化、混淆、desugaring、inlining、lambda、synthetic 成员、bridge 方法、生成代码、名称缺失和资源外置会改变可见结构；反编译器还可能重建不可编译或语义近似的控制流。将派生文本标为 `derived`，把原始命名、源行、泛型细节、未见分支和业务理由保持未知。

只能从制品支持其包含的类、字节码、元数据和资源事实。没有来源—构建—制品链时不得声称反编译类对应某仓库文件；没有部署—进程关联时不得声称该 class 已加载或执行。

## 运行时关联

运行、日志与数据库操作必须分别授权，并绑定当前 `ART-G0-AUTH` 且确认其 `verdict` 为 `pass`；只读为默认。启动应用、附加 debugger/agent/profiler、打开管理端点、提高日志级别、执行 SQL、清缓存、发布消息和触发任务都是不同动作，任何一项获准都不授权其他项。

运行记录冻结制品哈希/镜像 digest、部署 revision、JVM/JDK、启动参数、有效配置的脱敏哈希、实例/pod、角色、租户、数据哨兵和时间窗。用获准的 request/message/business correlation ID 连接网关、线程、span、SQL、消息、任务和可见结果；若 ID 缺失，只保留有限候选时间线，不按时间邻近强连。

日志采集限定 logger、级别、字段、时间和行数，并在源端最小化/脱敏；只读数据库探针限定连接角色、schema、SQL、行/字段上限、锁与超时。运行观察只能确认被测版本和场景；日志缺失、trace 采样、代理未附加或只读查询未返回均不能证明事件不存在。

## 证据平面与主张上限

源码结构、配置解析候选、部署装配事实和已观察运行行为必须分别建证据项与主张。它们可用类型化链接相互支持或冲突，但静态证据不得直接升级为 `runtime-confirmed`，部署清单也不能替代进程或请求观察。

| 证据平面 | 最高起始状态 | 最低身份 | 不可跨越的边界 |
| --- | --- | --- | --- |
| 源码结构 | `statically-supported` | 提交/工作树、文件哈希、生成来源和分析工具 | 不证明配置生效、制品已部署或路径已执行 |
| 配置解析候选 | `statically-supported` | 配置来源、加载实现、框架版本与候选优先级 | 不证明该值在目标部署生效 |
| 部署装配事实 | `observed` | 制品/镜像、部署 revision、注入引用和采集时间 | 只证明已检查部署元数据中的装配事实，不证明请求经过该路径 |
| 已观察运行行为 | `runtime-confirmed` | G0、版本、部署、有效配置、角色、输入、时间窗与可重复结果 | 只限绑定版本、部署、配置、角色、输入和时间窗的场景 |

可见/API 契约结果和内部实现链使用不同主张。可重复、获准且绑定身份的响应或外部可见结果可以独立成为限定 `runtime-confirmed` 主张；缺少内部源码、事务或消息链接只限制内部主张。反过来，完整源码链也不能确认该路径在部署中执行。

## 常见盲区与停止规则

| 盲区 | 默认处理 | 禁止的外推 |
| --- | --- | --- |
| 自动配置与条件 bean | 保存条件、候选 bean 与配置缺口 | 依赖存在不等于 bean 已装配 |
| 代理、增强与 self-invocation | 先识别代理/增强机制与调用方向 | 不把框架常见问题套到普通对象 |
| 动态 SQL 与路由数据源 | 保存表达式、候选对象、schema 和验证方法 | 不按短名选择数据库对象 |
| lazy/eager、缓存与 N+1 | 作为按路径测量的问题 | 不由默认配置推断查询数量或正确性 |
| 异步、消息与调度 | 分开事务、提交、投递、执行和可见终态 | 不由库或注解推断可靠性语义 |
| 多版本与旧实例 | 分别绑定源码、制品、部署、JVM 和配置 | 不把一个实例的结果推广到整个集群 |
| 反编译与混淆 | 保留原制品和派生工具链 | 不还原原始意图、名称或精确源行 |

- 所有运行、日志、数据库、调试、消息、任务和缓存动作均以当前 G0 的逐项授权为边界；未列明就不执行，不能用技术可访问性扩大范围。
- 不得提取凭据或秘密，不得保存令牌、连接串值、个人信息或授权外业务正文；遇到敏感信息泄露时立即停止，隔离最小脱敏现场并走批准的披露路径。
- 不得对生产环境执行破坏性写入；迁移、DDL/DML、消息发布、任务触发、缓存清除、故障注入或配置修改仅可在另行批准且可恢复的隔离环境执行。
- 授权、版本或环境不匹配，制品哈希漂移、数据库不再只读、日志跨租户、探针影响真实用户或外发目标未知时立即停止；只有重新授权、新的 G0 `pass`、匹配身份与恢复核对齐全后才能恢复。

## 纵向追踪示例

下面是中性教学切片，不代表任何具体工程、框架、路由、表、topic 或业务语义。主路径写作“HTTP 输入 → 校验 → 授权 → 服务 → 事务 → 数据库变更 → 可选 Outbox/消息 → 消费者/任务 → 可观察结果”；可选分支缺失时保留缺口且不创建占位边。若实际产品没有 HTTP、数据库、消息或任务，则从真实入口选择另一条切片。

可见结果主张与内部实现主张使用不同稳定 ID。静态源码可以支持内部链，运行观察可以验证已测可见结果；可选异步边即使得到内部证据，也不能由内部链取代可见结果自己的运行证据。

### 节点注册表

| 节点 ID | 类型 | 当前状态 | 边界 |
| --- | --- | --- | --- |
| `integration:sample.http-input` | `http-input` | `observed` | 已登记的中性请求契约，不含真实路径或数据 |
| `asset:sample.validation` | `validation` | `statically-supported` | 指定源码制品中的校验候选 |
| `asset:sample.authorization` | `authorization` | `statically-supported` | 指定源码制品中的授权候选 |
| `asset:sample.java-service` | `service` | `statically-supported` | 指定源码制品中的服务调用候选 |
| `asset:sample.transaction` | `transaction` | `statically-supported` | 指定 manager 与调用路径候选 |
| `data:sample.db-mutation` | `db-mutation` | `statically-supported` | 完全限定对象的写入候选，不代表已经提交 |
| `data:sample.outbox-row` | `outbox` | `statically-supported` | 仅在发现 Outbox 时保留的可选节点 |
| `integration:sample.message` | `message` | `inferred` | 仅在部署/运行有消息迹象时保留 |
| `asset:sample.consumer-job` | `consumer-job` | `inferred` | 消费者或任务的可选候选 |
| `claim:sample.internal-db-path` | `internal-claim` | `statically-supported` | 内部实现链主张，与可见结果分立 |
| `claim:sample.visible-result` | `visible-claim` | `runtime-confirmed` | 仅限已回放部署、角色、输入和结果 |
| `evidence:sample.source-structure` | `static-evidence` | `observed` | 已哈希源码/制品与工具输出 |
| `evidence:sample.runtime-visible` | `runtime-evidence` | `observed` | 已授权且可重复的可见结果记录 |
| `evidence:sample.async-candidate` | `derived-evidence` | `observed` | 可选异步配置/部署/trace 候选 |

### 证据注册表

每个证据 ID 在本表恰好定义一次；类型化链接只能引用这里已定义的 ID。

| 证据 ID | 来源与身份 |
| --- | --- |
| `evidence:sample.source-structure` | 指定提交/制品哈希、静态位置与分析工具版本 |
| `evidence:sample.runtime-visible` | 当前 G0、部署身份、场景输入、重复步骤与脱敏结果哈希 |
| `evidence:sample.async-candidate` | 指定部署中的可选消息/任务配置或关联 trace 候选 |

### 上下文注册表

每个上下文 ID 在本表恰好定义一次；源码上下文与部署运行上下文不能互换。

| 上下文 ID | 精确边界 |
| --- | --- |
| `context:sample.source-artifact` | 指定仓库提交、构建输入、制品哈希和工具版本 |
| `context:sample.deployed-runtime` | 当前 G0、制品/镜像、部署 revision、配置哈希、角色、输入和时间窗 |

### 类型化链接

| 链接 ID | 源 ID | 关系 | 目标 ID | 当前状态 | 分支 | 证据引用 | 上下文引用 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `trace-link:sample.http-to-validation` | `integration:sample.http-input` | `calls` | `asset:sample.validation` | `statically-supported` | `required` | `evidence:sample.source-structure` | `context:sample.source-artifact` |
| `trace-link:sample.validation-to-auth` | `asset:sample.validation` | `calls` | `asset:sample.authorization` | `statically-supported` | `required` | `evidence:sample.source-structure` | `context:sample.source-artifact` |
| `trace-link:sample.auth-to-service` | `asset:sample.authorization` | `calls` | `asset:sample.java-service` | `statically-supported` | `required` | `evidence:sample.source-structure` | `context:sample.source-artifact` |
| `trace-link:sample.service-to-transaction` | `asset:sample.java-service` | `calls` | `asset:sample.transaction` | `statically-supported` | `required` | `evidence:sample.source-structure` | `context:sample.source-artifact` |
| `trace-link:sample.transaction-to-db` | `asset:sample.transaction` | `writes` | `data:sample.db-mutation` | `statically-supported` | `required` | `evidence:sample.source-structure` | `context:sample.source-artifact` |
| `trace-link:sample.service-to-outbox` | `asset:sample.java-service` | `writes` | `data:sample.outbox-row` | `statically-supported` | `optional` | `evidence:sample.source-structure` | `context:sample.source-artifact` |
| `trace-link:sample.outbox-to-message` | `data:sample.outbox-row` | `emits` | `integration:sample.message` | `inferred` | `optional` | `evidence:sample.async-candidate` | `context:sample.deployed-runtime` |
| `trace-link:sample.message-to-consumer` | `integration:sample.message` | `calls` | `asset:sample.consumer-job` | `inferred` | `optional` | `evidence:sample.async-candidate` | `context:sample.deployed-runtime` |
| `trace-link:sample.consumer-to-visible` | `asset:sample.consumer-job` | `supports` | `claim:sample.visible-result` | `inferred` | `optional` | `evidence:sample.async-candidate` | `context:sample.deployed-runtime` |
| `trace-link:sample.source-to-internal` | `evidence:sample.source-structure` | `supports` | `claim:sample.internal-db-path` | `statically-supported` | `required` | `evidence:sample.source-structure` | `context:sample.source-artifact` |
| `trace-link:sample.runtime-to-visible` | `evidence:sample.runtime-visible` | `validates` | `claim:sample.visible-result` | `runtime-confirmed` | `required` | `evidence:sample.runtime-visible` | `context:sample.deployed-runtime` |

所有节点和链接端点均使用 `kind:namespace.qualified-key` 形式的限定稳定 ID；状态只取核心封闭词汇，关系只取核心 `calls`、`writes`、`emits`、`supports` 和 `validates`。新增关系必须先登记方向、语义、版本和校验规则。证据与上下文引用均须在对应注册表精确解析一次，重复定义、空引用和未声明引用都使该链接无效。

## 有序工作流

1. 冻结源码/制品与工具身份，解析 Maven/Gradle 构建图和解析后的依赖图，分开记录声明、生成、打包与运行加载事实。
2. 枚举模块、JAR/WAR 与部署单元，从 manifest、main、Servlet/container 或实际框架注册中选择启动入口候选，并建立源码—制品—部署—JVM 的启动身份链。
3. 从获准 HTTP/RPC 入口定位路由和过滤器/拦截器顺序；静态注册、部署装配与实际请求经过的链分别取证。
4. 沿真实调用进入控制器、服务与仓储候选，记录 DTO/领域/持久化转换、动态实现选择和异常映射，不补齐不存在的分层。
5. 定位事务边界、manager、传播、回滚和异步断点；只对实际代理/增强与调用机制解释注解效果。
6. 按实际技术追踪持久化到完全限定数据库对象、SQL、迁移、缓存或搜索，并把写入尝试、提交和可见结果分开。
7. 若实际存在消息或任务分支，再追踪 Outbox/消息、消费者、调度任务、重试、幂等、顺序、投递、补偿和最终一致性；不存在就保留缺口而非占位边。
8. 将对外契约与可见结果绑定当前 G0、制品、部署、配置、角色、输入和时间窗，用独立运行证据验证，并与内部静态主张分别发布。

完成后按[覆盖、质量与冻结](../core/coverage-quality-and-freeze.md)审查资产分母、动态边、版本冲突、运行缺口、可选分支和停止记录。结构校验通过只证明本页契约存在，不提高任何目标产品主张的状态或本方法的成熟度。
