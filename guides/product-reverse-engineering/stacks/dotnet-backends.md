# .NET 后端产品逆向工程指南

**证据成熟度：`proposed`**

**适用范围：** 适用于在明确授权下分析 .NET 与 .NET Framework 后端的源码工程、DLL/EXE 制品、配置和部署元数据，以及另行获准的日志、只读数据库与运行观察；不授予构建、下载包、执行服务、读取秘密、访问生产数据或修改环境的权限。

本页把通用方法落到 .NET 服务端栈。开始前必须通过[授权、隐私与安全](../core/authorization-privacy-and-safety.md)的 G0；只有制品、配置或部分源码时采用[灰盒访问轨道](../access-tracks/gray-box.md)，完整源码可读时采用[白盒访问轨道](../access-tracks/white-box.md)。所有具体技术与拓扑都是条件分支：只为实际发现且能定位证据的组件建节点和边。

所有证据项、主张状态、限定稳定 ID 和类型化链接沿用[证据与置信度](../core/evidence-and-confidence.md)，运行实验沿用[运行时实验](../core/runtime-experiments.md)。不得把 IIS、Kestrel、ASP.NET Core、EF Core、消息系统、WCF 或 COM 写成必经层；控制台进程、Worker、自托管 HTTP、传统 ASP.NET、Windows Service 或无数据库程序均可能是实际分支。

## Solution、Project、TFM 与构建身份

先冻结仓库提交或工作树、`.sln`、`.csproj`/`.fsproj`/`.vbproj`、`Directory.Build.props`/`Directory.Build.targets`、`global.json`、NuGet 配置与锁定/资产文件。逐项目记录 SDK、`TargetFramework` 或 `TargetFrameworks`、输出类型、项目引用、包引用、analyzer/source generator、条件属性、构建配置、平台、RID、restore 来源和实际使用的 MSBuild/.NET SDK 身份；Solution 中出现项目只证明聚合关系，不证明部署。

构建身份链至少区分“源码身份 → restore 输入与解析结果 → 属性/target 与生成输入 → DLL/EXE 哈希 → publish 输出 → 部署 revision/image digest → 进程”。目标框架不等于目标部署实际使用的运行时；TFM、Runtime Framework、host/runtime 版本、架构/RID、framework-dependent/self-contained 和目标机器原生依赖需分别取证。构建成功只支持该输入组合可构建，不证明产物已部署、已启动或承载过目标请求。

多目标构建为每个 TFM 建不同制品身份；同名 DLL、AssemblyVersion、FileVersion、InformationalVersion 与包版本不能替代内容哈希。未获准执行 restore/build 时，只从登记输入形成 `statically-supported` 构建图，并记录缺失的 imported targets、生成输出和包内容。

## Host 启动、IIS、Kestrel 与部署身份

按实际版本识别入口：顶级语句/`Main`、Generic Host、`Host.CreateDefaultBuilder`、`WebApplication.CreateBuilder`、较早的 `WebHostBuilder`/`Startup`、Worker 或自研 host 都是候选。记录入口方法、content root、环境名、host lifetime、服务注册、监听器、启动/关闭钩子和异常；模板惯例不是目标程序事实。

IIS、ASP.NET Core Module、Kestrel、HTTP.sys、Windows Service、容器 entrypoint 或直接进程启动按部署证据选择。保存进程命令、工作目录、账号/服务身份、父进程、监听地址的脱敏表示、assembly 哈希、运行时版本、架构、部署 revision/image digest、环境与配置快照引用；端口、站点名和进程显示名不能单独绑定源码或制品。

建立“部署清单/服务配置 → 进程命令 → host 入口 → 实际加载 assembly → 监听与健康状态”的身份链。IIS 前置不证明一定是进程内托管，Kestrel 引用也不证明外部流量直接到达；必须结合目标版本的托管模型、模块配置、代理头和运行相关性判断。

## ASP.NET Core Middleware 顺序与 Endpoint Routing

Middleware 的注册顺序、条件分支、短路和响应回程顺序分别记录。解析 `Use`/`Run`/`Map`、扩展方法展开、环境分支和框架自动装配；请求向内、响应反向经过管道，终止 middleware 可能阻止后续节点。源码顺序只支持静态主张，部署生效和某请求实际经过仍需绑定配置与 trace/log/probe。

Endpoint Routing 按实际版本核对 `UseRouting`、`UseAuthentication`、`UseAuthorization`、`UseEndpoints`、`MapControllers`、`MapGet` 和其他 endpoint data source。某些 hosting 模型会在条件满足时自动添加部分 middleware，不能只搜索显式调用就宣称不存在；也不能把官方模板的推荐顺序当作目标应用的已观察顺序。

对每个入口记录 route pattern、HTTP 方法、host/metadata 条件、endpoint display name、filter、授权元数据、参数绑定和最终 handler。网关、IIS 模块、middleware、endpoint filter、MVC filter 与 handler 分层建节点，HTTP 状态相同不能证明经过同一路径。

## 传统 ASP.NET 条件分支

发现 .NET Framework、`System.Web` 或相应部署材料时，再进入传统 ASP.NET 条件分支：盘点 `web.config`、`Global.asax`、HTTP module/handler、route table、ASP.NET MVC、Web API、Web Forms、OWIN/Katana、IIS application pool、虚拟目录与 shadow copy。任何一个名称出现都不自动证明其余机制存在。

分别追踪 application/session/request 生命周期、module/handler 顺序、MVC/Web API filter、页面事件、依赖解析器、身份模拟和错误页。经典 pipeline 与 ASP.NET Core middleware 不能混成一条通用顺序；混合迁移、反向代理或多个站点必须以进程、应用域、assembly 和部署配置拆分。

`assembly binding`、GAC、binding redirect、machine/app/web config 和 probing path 是 .NET Framework 条件机制；较新的 .NET 使用不同的依赖加载模型。先确认运行时家族与版本，再解释实际 assembly resolution，不把某一代机制外推到另一代。

## DI 生命周期、Options 与配置优先级

盘点内置容器或第三方容器的注册点、扩展方法展开、open generic、named/keyed service、factory、decorator、scope 和条件分支。对 Singleton、Scoped、Transient 记录服务/实现、注册顺序、所有者、创建与释放边界；`ValidateScopes` 配置、captured scoped service、手工 scope 和 hosted service 内解析都作为版本与运行证据问题。

区分 `IOptions`、`IOptionsSnapshot`、`IOptionsMonitor`、直接 `IConfiguration` 读取、启动时绑定和自定义 reload。记录 options 类型、名称、validator、读取时点、缓存/刷新语义和消费者生命周期；接口存在不证明值已绑定或刷新通知已发生。

配置优先级必须按目标部署、框架版本和实际 provider 链取证，不得假定一条跨版本、跨宿主的固定优先级。分别登记代码默认值、JSON/XML/INI、user secrets 的引用、环境变量、命令行、Key-per-file、远程 provider、平台注入和后加 provider；只保存秘密引用和脱敏来源，不读取或提交秘密值。配置文件存在、部署注入与进程最终解析值是不同主张。

## Controller、Minimal API 与服务边界

Controller、Razor handler、Minimal API、gRPC service、SignalR hub、endpoint filter 和自研 dispatcher 都按实际发现建入口。对 Controller/action 解析 attribute/conventional routing、model binding、filter 和 action result；对 Minimal API 展开 route group、`MapGet`/其他 Map 方法、delegate/lambda、endpoint metadata、filter 和 DI 参数。

Controller、应用服务、领域服务、repository 与外部 client 是分析标签而非强制层。通过调用点、接口实现、DI 解析、source generator 输出、测试和运行关联识别实际责任；逻辑若直接位于 endpoint、filter、entity 或 SQL，就记录真实位置，不补造“标准分层”。

沿路径记录 DTO、command/query、domain model 和 persistence model 的字段转换、默认值与损失。静态 endpoint 到服务调用最多支持 `statically-supported`；动态注册、多实现选择和反射调用保留 candidate set，直到配置或运行证据唯一解析。

## 校验、认证与授权

校验链分别检查协议解析、模型绑定、DataAnnotations、FluentValidation 或实际发现的其他 validator、endpoint/MVC filter、业务守卫和数据库约束。记录触发时点、规则组、字段路径、错误 schema、是否短路及副作用；声明 attribute 或客户端校验不证明服务端已执行。

认证记录 scheme/handler、cookie/token/certificate/Windows identity、challenge/forbid、claims transformation 和服务身份，但不得保存凭据。授权按 endpoint metadata、filter、policy、role/claim、资源级 handler、租户/数据过滤与下游服务分别定位；入口允许不代表资源级授权也允许，UI 隐藏不证明服务端拒绝。

运行验证只使用已授权账号、租户和对象，分别记录允许/拒绝结果与 trace。禁止修改 token、猜测租户、枚举隐藏 endpoint 或绕过访问控制；源码策略支持静态主张，只有绑定部署身份的已执行结果支持窄边界运行主张。

## EF、EF Core、Dapper 与手写 SQL

EF6、EF Core、Dapper、ADO.NET、手写 SQL、存储过程、其他 provider 或无数据库都是条件分支。登记 connection/data source 的脱敏稳定 ID、provider 与版本、schema/catalog、DbContext/connection 生命周期、entity/mapping、query/command、参数和完全限定数据库对象；包引用只证明技术可用。

对 EF/EF Core 追踪模型来源、convention/configuration/attribute、tracking/no-tracking、identity resolution、change detection、relationship fix-up、lazy/eager/explicit loading、global query filter、并发 token、`SaveChanges`、generated SQL 和数据库返回。lazy/eager 是否在当前路径触发、序列化是否追加查询、查询是否形成 N+1 都是证据问题，不能从默认值或 LINQ 外形直接外推。

Dapper 与手写 SQL 追踪 command text/template、参数绑定、transaction/connection、multi-mapping、动态对象名、批处理、返回映射和资源释放。数据库迁移可能来自 EF migrations、脚本或外部工具；迁移文件存在不证明部署已执行，目标 schema 和迁移历史需另行获准的只读证据。

## 事务、TransactionScope 与异步边界

区分 `SaveChanges` 的 provider 行为、显式 DbContext transaction、ADO.NET transaction、`TransactionScope`/ambient transaction、存储过程内部事务和跨资源协调。登记 begin/join/suspend、隔离、savepoint、提交、回滚、重试策略、资源参与者和异常条件；API 名称或 `using` 结构不能替代 provider、运行时和部署证据。

`TransactionScope` 是否跨 async/await 流动取决于构造选项、运行时和实际调用；是否升级为分布式事务还受资源、平台与 provider 支持限制。`ConfigureAwait`、ExecutionContext、SynchronizationContext、线程切换和 Task 调度分别检查，不能凭“用了 await”判断 ambient transaction、身份、locale 或 trace context 必然传播。

事务不会按假设跨越 hosted job、消息、远程 RPC 或任意异步边界。把写入尝试、数据库提交、HTTP 响应、Outbox 提交、发布、消费和最终可见结果放在同一时间线但保留独立主张；运行失败优先保存首个失败、事务终态和已发生副作用。

## 异常过滤器与协议结果

从抛出点、inner exception/aggregate、await 边界、exception filter、MVC filter、middleware、server boundary 和网关追到 HTTP/RPC/消息结果。记录匹配范围、顺序、是否标记 handled、重抛/包装、ProblemDetails 或自定义错误 schema、日志级别和响应是否已经开始。

输入错误、认证/授权拒绝、业务冲突、并发失败、依赖失败、超时、取消与未知异常分别建主张。HTTP 500 不能唯一定位内部异常，日志中出现 exception 也不证明用户请求失败；同一关联 ID 下保留首个失败、后续包装、事务结果、响应和后台终态。

异步任务未 await、fire-and-forget、hosted worker 和消息 handler 可能在响应之后失败。必须把即时协议结果与后续副作用分开验证，不能用 2xx 证明整个业务完成。

## Hosted Service、任务与消息

发现 `IHostedService`、`BackgroundService`、Worker Service、Timer、Quartz/Hangfire 或平台调度时，记录注册、host lifecycle、启动顺序、scope 创建、循环/触发、时区、并发、leader/lock、取消、关闭、超时和部署副本。类型或 `AddHostedService` 文本存在不证明目标部署启用或任务实际运行。

消息 client、producer、consumer、Outbox 与 inbox/去重均为可选分支。登记 broker/namespace、topic/queue、schema、key、group/subscription、ack/commit、ordering、retry/dead-letter、幂等、retention 和关联 ID；库存在不能证明投递语义，成功 publish 也不证明消费副作用或用户可见结果。

Hosted Service 使用 scoped 依赖时要追踪实际 scope 的创建与释放；singleton worker 捕获 scoped service 是风险候选，不因代码形状直接宣布故障。请求触发后台工作时，用业务哨兵、outbox/message ID 和 trace 连接；仅时间邻近保持 `inferred`。

## WCF、Windows Service 与 COM

WCF 分支记录 contract/operation、service implementation、host、endpoint、address 的脱敏身份、binding、behavior、serializer、session、security、timeout 和 fault contract。配置中的 endpoint 或 contract 不证明已托管、可达或调用；客户端 proxy、服务端 host 和网络运行证据分别登记。

Windows Service 分支记录服务配置、二进制哈希、进程账号、启动类型、参数、依赖、恢复动作、工作目录和 Service Control Manager 事件。服务“Running”只证明进程级状态，不证明内部 listener、job 或依赖健康。

COM/COM+ interop 分支记录 ProgID/CLSID、type library、接口 IID、注册范围、32/64 位、apartment、activation、marshalling 和真实加载模块；不导出秘密或未经授权修改注册。assembly binding、GAC、binding redirect 和 COM 注册只对已确认的 .NET Framework/Windows 分支适用，不能普遍化到所有 .NET 部署。

## DLL、EXE、IL 与反编译边界

仅有编译产物时，每个输入必须记录 assembly SHA-256、文件大小、来源、PE/CLR header、assembly name/version/MVID、TFM、运行时家族/版本、架构/RID、依赖清单、签名与 PDB 可用性。另记 framework-dependent/self-contained、ReadyToRun、single-file、trimming、AOT、混淆、资源、生成代码和原生依赖迹象；文件名或产品版本不替代内容身份。

任何 metadata/IL 浏览、反汇编、反编译、single-file 提取或符号恢复都记录输入哈希、命令、反编译器名称、版本、插件、参数与输出哈希。反编译结果不是原始源码；优化会折叠控制流，trimming/AOT 可能移除或转换成员，async/iterator 状态机、closure、dynamic、reflection 和 source generator 会改变可见结构。名称恢复与伪 C# 只能作为派生证据，不得据此解释开发者意图。

必须保留原 assembly，只把派生结果写入隔离目录。反编译不能证明源码提交、构建选项、未发布分支、运行配置或路径执行；部署身份仍需由制品哈希/image digest 与进程加载事实连接，运行主张仍需获准实验。

## 部署与运行时关联

部署盘点按实际环境选择 IIS、Windows Service、文件复制、安装包、容器、编排平台、云服务或自研发布器。登记 publish manifest、DLL/EXE 与配置哈希、image digest、revision、slot、replica、启动命令、挂载/秘密引用、路由、健康检查、回滚单元和发布时间窗；“CI 产出”不等于“部署采用”。

运行、日志、数据库、调试与外部消息操作必须分别授权，并绑定当前 `ART-G0-AUTH` 且 `verdict` 为 `pass`。只读为默认；trace/log/metric 仅采集最小必要字段并脱敏。使用 deployment/instance ID、assembly 加载信息、trace/span、request/message ID 与业务哨兵关联，不靠时间邻近或实例名称强连边。

将源码、构建、发布、部署和运行做成独立身份节点；滚动发布时一个服务名可能同时对应多个 digest。无法把某次观察唯一绑定到实例和 assembly 时，保留候选集并把结论限制在 `observed`/`inferred`，不得合并成单一版本事实。

## 证据平面与主张上限

源码、IL、配置/部署和运行观察必须分别建证据项。方法成熟度描述本指南方法，目标产品主张仍使用状态、置信度和证据引用；静态或装配证据不能因“看起来完整”而变成运行确认。

| 证据面 | 最高起始状态 | 可建立的限定关系 | 不可外推 |
| --- | --- | --- | --- |
| 源码结构 | `statically-supported` | 指定提交/工作树中的声明、调用与配置候选 | 不证明配置生效、assembly 已部署或路径已执行 |
| 反编译/IL 派生结构 | `statically-supported` | 指定哈希制品中的 metadata、IL 和控制流候选 | 不等同原始源码，不证明符号、意图或运行路径 |
| 配置与部署装配事实 | `observed` | 指定 revision/实例声明加载的制品与设置 | 不证明请求经过该配置或组件 |
| 已关联运行行为 | `runtime-confirmed` | 指定请求/任务/消息的已执行行为与副作用 | 只限绑定版本、部署、配置、角色、输入和时间窗的场景 |

同一内部路径与用户可见结果使用不同主张 ID。可见行为可由符合协议的独立运行证据确认，即使内部链仍不完整；反之，完整源码链也不能证明部署中的用户行为。

## 常见盲区与停止规则

| 盲区 | 默认处理 | 停止或降级条件 |
| --- | --- | --- |
| 多 TFM/RID 输出同名 | 以输入、TFM、RID、配置和哈希拆分 | 无法绑定目标部署时停止合并结论 |
| 自动 middleware/endpoint 注册 | 展开版本对应的 host 与 data source | 只有模板知识时不声称目标顺序 |
| DI factory/reflection/generated code | 保留候选集、生成器与配置条件 | target 不唯一时停止精确连边 |
| EF tracking 与隐式查询 | 把 query、materialization、tracking、SQL 分开 | 无 SQL/trace 时不声称查询次数或结果来源 |
| ambient transaction 与 async | 记录 provider、选项、资源和边界 | 缺少实际事务结果时不声称跨边界原子性 |
| trimmed/AOT/混淆产物 | 记录转换模型与缺失 metadata | 反编译不可恢复时保持未知 |
| 滚动部署 | 每个 instance/digest 单独登记 | 观察无法唯一绑定时不升级运行主张 |

- 不得提取连接串、token、证书私钥、用户秘密或生产数据；秘密只记录受控引用。
- 不得对生产数据库、缓存、队列、调度器、服务配置、注册表或外部 endpoint 执行破坏性写入。
- 授权、源码/assembly、运行时、配置、部署、账号或环境不匹配时立即停止；重新授权并取得新的 G0 `pass` 后新建记录，不沿用旧观察。
- 调试附加、反编译、构建、网络捕获、消息消费和 COM 激活任一项未获单独授权时，转入静态或更窄证据分支。

## 纵向追踪示例

这是中性、条件化的教学切片，不代表所有 .NET 产品都有 HTTP、数据库、Outbox 或消息。示例把 assembly/host 身份与一条“HTTP 输入 → middleware/路由 → endpoint metadata → 授权 → 模型绑定与校验 → 服务 → 事务 → 数据库变更与 Outbox 原子提交 → relay/message → consumer → 稍后可见结果”链连接；可选分支缺失时保留缺口且不创建占位边。若目标程序确有更早的自定义校验 middleware，则按实际顺序另建节点，不能由本示例外推。

内部节点以源码/制品/部署证据起步，不能因示例连通就升级为运行确认。可见结果由独立运行证据验证；内部链与可见主张状态互不替代。所有 ID、证据和上下文必须先登记，关系只使用核心词汇。

### 节点注册表

| 稳定 ID | 类型 | 当前状态 | 边界 |
| --- | --- | --- | --- |
| `asset:sample.dotnet-project` | `project` | `statically-supported` | 已哈希 project 与构建输入 |
| `asset:sample.dotnet-assembly` | `assembly` | `observed` | 已哈希目标 DLL/EXE |
| `asset:sample.dotnet-host` | `host` | `observed` | 已绑定部署与进程中的 host |
| `integration:sample.dotnet-http-input` | `http-input` | `runtime-confirmed` | 已授权场景的一次请求 |
| `asset:sample.dotnet-middleware` | `middleware` | `statically-supported` | 已解析顺序中的目标 middleware |
| `asset:sample.dotnet-endpoint` | `endpoint` | `statically-supported` | 已解析 route 与 handler |
| `asset:sample.dotnet-validation` | `validation` | `statically-supported` | 已定位输入校验 |
| `asset:sample.dotnet-authorization` | `authorization` | `statically-supported` | 已定位 policy 与资源守卫 |
| `asset:sample.dotnet-service` | `service` | `statically-supported` | 已定位用例服务 |
| `asset:sample.dotnet-transaction` | `transaction` | `statically-supported` | 已定位 transaction owner |
| `data:sample.dotnet-atomic-commit` | `atomic-business-outbox-outcome` | `statically-supported` | 业务变更与 Outbox 写入同一事务候选 |
| `asset:sample.dotnet-outbox-relay` | `outbox-relay` | `statically-supported` | 实际发现时才保留 |
| `integration:sample.dotnet-message` | `message` | `statically-supported` | 实际发现时才保留 |
| `asset:sample.dotnet-consumer` | `consumer` | `statically-supported` | 实际发现时才保留 |
| `claim:sample.dotnet-later-visible` | `visible-claim` | `runtime-confirmed` | 只限独立回放确认的稍后结果 |

### 证据注册表

| 证据 ID | 已登记身份 |
| --- | --- |
| `evidence:sample.dotnet-build` | project 输入、SDK、restore 与 assembly 哈希 |
| `evidence:sample.dotnet-deployment` | revision、进程、runtime 与加载 assembly |
| `evidence:sample.dotnet-source` | middleware、endpoint、服务、事务与后台静态路径 |
| `evidence:sample.dotnet-runtime` | 已授权请求、trace/message 相关性与副作用 |
| `evidence:sample.dotnet-visible-run` | 独立回放得到的用户可见结果 |

### 上下文注册表

| 上下文 ID | 已登记边界 |
| --- | --- |
| `context:sample.dotnet-source-build` | 源码提交、project、SDK、TFM、RID 与构建配置 |
| `context:sample.dotnet-deployed-instance` | assembly 哈希、runtime、revision 与实例 |
| `context:sample.dotnet-authorized-scenario` | 当前 G0、角色、输入、时间窗与最小观察面 |

### 类型化链接

| 链接 ID | 源 | 关系 | 目标 | 状态 | 证据引用 | 上下文引用 |
| --- | --- | --- | --- | --- | --- | --- |
| `trace-link:sample.dotnet-assembly-from-project` | `asset:sample.dotnet-assembly` | `derived-from` | `asset:sample.dotnet-project` | `statically-supported` | `evidence:sample.dotnet-build` | `context:sample.dotnet-source-build` |
| `trace-link:sample.dotnet-host-from-assembly` | `asset:sample.dotnet-host` | `derived-from` | `asset:sample.dotnet-assembly` | `observed` | `evidence:sample.dotnet-deployment` | `context:sample.dotnet-deployed-instance` |
| `trace-link:sample.dotnet-http-to-host` | `integration:sample.dotnet-http-input` | `calls` | `asset:sample.dotnet-host` | `runtime-confirmed` | `evidence:sample.dotnet-runtime` | `context:sample.dotnet-authorized-scenario` |
| `trace-link:sample.dotnet-host-to-middleware` | `asset:sample.dotnet-host` | `calls` | `asset:sample.dotnet-middleware` | `statically-supported` | `evidence:sample.dotnet-source` | `context:sample.dotnet-deployed-instance` |
| `trace-link:sample.dotnet-middleware-to-endpoint` | `asset:sample.dotnet-middleware` | `calls` | `asset:sample.dotnet-endpoint` | `statically-supported` | `evidence:sample.dotnet-source` | `context:sample.dotnet-source-build` |
| `trace-link:sample.dotnet-endpoint-to-authorization` | `asset:sample.dotnet-endpoint` | `calls` | `asset:sample.dotnet-authorization` | `statically-supported` | `evidence:sample.dotnet-source` | `context:sample.dotnet-source-build` |
| `trace-link:sample.dotnet-authorization-to-validation` | `asset:sample.dotnet-authorization` | `calls` | `asset:sample.dotnet-validation` | `statically-supported` | `evidence:sample.dotnet-source` | `context:sample.dotnet-source-build` |
| `trace-link:sample.dotnet-validation-to-service` | `asset:sample.dotnet-validation` | `calls` | `asset:sample.dotnet-service` | `statically-supported` | `evidence:sample.dotnet-source` | `context:sample.dotnet-source-build` |
| `trace-link:sample.dotnet-service-to-transaction` | `asset:sample.dotnet-service` | `calls` | `asset:sample.dotnet-transaction` | `statically-supported` | `evidence:sample.dotnet-source` | `context:sample.dotnet-source-build` |
| `trace-link:sample.dotnet-transaction-to-atomic-commit` | `asset:sample.dotnet-transaction` | `writes` | `data:sample.dotnet-atomic-commit` | `statically-supported` | `evidence:sample.dotnet-source` | `context:sample.dotnet-source-build` |
| `trace-link:sample.dotnet-relay-reads-atomic-commit` | `asset:sample.dotnet-outbox-relay` | `reads` | `data:sample.dotnet-atomic-commit` | `statically-supported` | `evidence:sample.dotnet-source` | `context:sample.dotnet-source-build` |
| `trace-link:sample.dotnet-relay-emits-message` | `asset:sample.dotnet-outbox-relay` | `emits` | `integration:sample.dotnet-message` | `statically-supported` | `evidence:sample.dotnet-source` | `context:sample.dotnet-source-build` |
| `trace-link:sample.dotnet-message-to-consumer` | `integration:sample.dotnet-message` | `calls` | `asset:sample.dotnet-consumer` | `statically-supported` | `evidence:sample.dotnet-source` | `context:sample.dotnet-source-build` |
| `trace-link:sample.dotnet-consumer-to-visible` | `asset:sample.dotnet-consumer` | `supports` | `claim:sample.dotnet-later-visible` | `inferred` | `evidence:sample.dotnet-runtime` | `context:sample.dotnet-authorized-scenario` |
| `trace-link:sample.dotnet-runtime-validates-visible` | `evidence:sample.dotnet-visible-run` | `validates` | `claim:sample.dotnet-later-visible` | `runtime-confirmed` | `evidence:sample.dotnet-visible-run` | `context:sample.dotnet-authorized-scenario` |

示例的有向可执行链以 `reads` 的数据流方向解释为“原子提交 → relay”，因此从 HTTP 输入可连续到达稍后可见主张。若运行相关性只覆盖可见结果而未覆盖内部节点，内部边保持静态或推断；不得用表格连通性冒充运行证据。

## 有序工作流

1. 冻结 `.sln`/project、源码、配置、NuGet、SDK、TFM、RID 和构建配置，建立源码—restore—DLL/EXE 哈希的构建身份。
2. 盘点可执行 host、库、Worker、传统 ASP.NET、Windows Service、WCF/COM 与部署单元，只保留实际发现的条件分支。
3. 绑定 publish/assembly、运行时、进程、IIS/Kestrel/容器和 revision，无法绑定时停止运行时外推。
4. 从获准入口解析 middleware/filter、Endpoint Routing、Controller/Minimal API、校验、认证与授权顺序。
5. 解析 DI 生命周期、Options 和实际配置 provider 链，再连接服务与动态实现候选。
6. 追踪 EF/EF Core/Dapper/手写 SQL、tracking、DbContext/connection、事务、提交与回滚，数据库操作另行授权。
7. 若实际存在 Hosted Service、调度、消息、Outbox、WCF 或 COM，再追踪异步/远程边界、重试、幂等和后续副作用。
8. 用独立运行证据验证对外协议与可见结果，按证据平面审计主张上限、缺口、冲突、覆盖与冻结门禁。

完成后按[覆盖、质量与冻结](../core/coverage-quality-and-freeze.md)审查模块、入口、部署、持久化与异步分母。结构验证只证明本页契约存在，不会自动提升目标产品主张。

## 参考

- [Microsoft：ASP.NET Core middleware](https://learn.microsoft.com/aspnet/core/fundamentals/middleware)
- [Microsoft：.NET configuration providers](https://learn.microsoft.com/dotnet/core/extensions/configuration-providers)
- [Microsoft：EF Core transactions](https://learn.microsoft.com/ef/core/saving/transactions)
- [Microsoft：.NET application publishing overview](https://learn.microsoft.com/dotnet/core/deploying/)
- [Microsoft：.NET Framework assembly version redirection](https://learn.microsoft.com/dotnet/framework/configure-apps/redirect-assembly-versions)
