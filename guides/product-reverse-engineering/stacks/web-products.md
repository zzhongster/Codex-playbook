# Web 产品逆向工程指南

**证据成熟度：`proposed`**

**适用范围：** 适用于在明确授权下分析浏览器访问的 Web 产品，包括公开页面、合法账号的当前会话、获准的浏览器观察，以及按黑盒、灰盒或白盒轨道取得的前端源码、构建产物、部署材料和有限后端证据；不授予访问其他账号、租户、套餐、环境、数据或未公开接口的权限。

本页把通用方法落到 Web 栈。开始前仍须通过[授权、隐私与安全](../core/authorization-privacy-and-safety.md)的 G0，按当前证据选择[黑盒](../access-tracks/black-box.md)、[灰盒](../access-tracks/gray-box.md)或[白盒](../access-tracks/white-box.md)轨道，并沿用[证据与置信度](../core/evidence-and-confidence.md)的主张状态、限定稳定 ID 和类型化追踪链接。浏览器能显示、缓存或下载某项内容，不会自动扩大授权。

## 路由与产品地图

先按“角色 × 套餐 × 语言/地区 × 设备/视口 × 数据状态”冻结观察分母，再从用户目标、入口和可见结果建立产品地图。每个格子绑定产品版本、部署、当前合法会话、租户、配置、观察时间与证据；未获授权或无法建立的格子记为缺口，不尝试进入。

数据状态至少区分空、有数据、加载中、错误和权限拒绝；按产品实际情况再记录首次使用、分页末页、过期会话、部分成功和后台处理中。相同 URL 在不同角色、套餐、语言或响应式布局下可能是不同产品表面，不能只按路径字符串去重。

浏览器路由与后端端点使用不同稳定 ID：前者是用户可导航的产品表面，例如 `product-surface:sample.browser-route`；后者是当前会话动作实际调用的集成边界，例如 `integration:sample.current-session-endpoint`。路由参数、搜索参数、hash、重定向和历史导航用于描述前端入口；HTTP/GraphQL/流式地址用于描述网络契约，二者不得因文本相似而合并。

| 产品地图字段 | 最低记录 |
| --- | --- |
| 用户边界 | 角色、套餐、租户、语言/地区、设备/视口和当前会话身份 |
| 入口 | 可见导航、浏览器路由、进入方式、前置状态与重定向 |
| 页面状态 | 空、有数据、加载中、错误、权限拒绝及等待条件 |
| 结果 | 即时反馈、最终可见状态、下载/通知或后台处理中状态 |
| 证据 | 版本、时间、脱敏截图/录制、DOM/可访问性或网络引用 |

## 渲染模式与水合

对每个已观察表面分别记录初始 HTML、脚本执行后的 DOM、网络时序和交互可用时点，形成 SSR、CSR、静态生成或混合渲染候选。服务器返回内容只证明该响应，客户端后来渲染的内容只证明该浏览器场景；框架名称、文件名或页面外观不能单独裁决渲染模式。

检查首屏内容来自响应 HTML、内联状态、后续数据请求还是客户端计算，并把 streaming SSR、延迟边界、客户端导航和预取分开。只有当前授权会话实际产生的资源与时序可进入运行证据；没有对应捕获时保持 `inferred` 或 `unsupported`。

hydration 观察应保存脚本启用前后差异、交互何时生效、控制台中已脱敏的水合错误和重复请求。水合不一致、闪烁、占位替换或事件丢失是场景事实，不自动证明框架缺陷或服务端模板原因。

## DOM 与可访问性树

DOM 快照说明某一时点的节点、属性和关系；可访问性树说明辅助技术可感知的名称、角色、状态与层级。两者分别登记并关联到同一表面和时点，不能用 CSS 选择器、视觉位置或 DOM 文本代替可访问性语义。

按获准场景记录标题层级、landmark、表单名称、错误关联、live region、焦点顺序、键盘操作和焦点恢复。可见元素、DOM 中存在的元素与可访问性树暴露的元素是三个观察面；隐藏、遮挡、虚拟化和 portal 可能使它们不一致。

重复回放时固定浏览器、缩放、字体、首选项、视口和辅助技术版本。截图支持视觉观察，DOM 与可访问性树支持结构观察，键盘和焦点回放支持交互观察；单一观察面不替代另外两个。

## 组件、客户端状态、表单与校验

从可见交互反向建立组件候选，但组件边界只有在获准的源码、框架工具或构建制品中有证据时才作为静态结构主张。DOM 子树、视觉卡片或复用样式不自动等于一个框架组件，也不证明组件在服务端或客户端的所有权。

客户端状态按来源分为 URL、内存、表单、缓存、持久存储和服务端返回，并记录初始化、更新、失效、回退与跨标签页同步。对每次动作分别保存前置状态、触发、乐观更新、回滚、最终状态和页面重载后的结果；瞬时状态不能由一张终态截图补写。

表单字段记录默认值、格式化、依赖关系、提交条件、客户端校验和错误呈现；网络契约另记服务端校验、机器错误和响应后的状态。客户端校验与服务端校验使用不同主张和证据：前端阻止提交不证明服务端会拒绝，服务端拒绝也不证明每个客户端都会提前提示。

## 当前授权会话的网络证据

- **会话证据边界：** 只记录当前合法会话中由已执行用户动作实际产生、且会话持有人获准检查的请求与响应事实；不得把偶然可见的端点扩展为枚举、重放或修改目标，超出已批准实验的请求变更一律停止。

为一个获准用户动作建立“动作时间 → 请求身份 → 响应事实 → 可见结果”的关联。请求身份至少包含脱敏后的方法、端点稳定 ID、资源类型、发起时点、关联 ID 和必要的头/体 schema 摘要；不得保存 Cookie 值、Authorization 值、会话令牌、个人信息或无关业务正文。

| 契约面 | 记录事实 |
| --- | --- |
| schema | 当前动作实际发送/接收的字段、类型、可选性和内容类型，不从单个样本推断全集 |
| 分页 | 当前会话实际观察的游标/页码、页大小、排序、终止信号和重复/遗漏结果 |
| 错误 | 状态、机器码、可见消息、重试提示、数据/页面终态和首个失败 |
| 幂等 | 实际出现的幂等身份、重复动作结果和副作用；未经批准不主动重放来测试 |
| 异步结果 | 接受、处理中、轮询/推送、完成/失败信号和最终可见状态 |

保存前按字段最小化并脱敏，记录浏览器、部署、角色、租户、时间窗、采集工具版本和内容哈希。缓存命中、Service Worker 响应、浏览器扩展流量和预取应与用户动作请求分开，避免把同一页面时段内的所有流量都归因给一次操作。

## API、流式通信与文件传输

REST 记录实际方法、资源、状态、媒体类型和错误映射；GraphQL 记录当前动作实际产生的 operation 类型/名称、变量 schema、响应 data/error 形状和分页语义，不从 schema 或 bundle 扩展查询清单。浏览器路由和上述 API 仍使用不同对象类型。

WebSocket 记录已获准连接的握手身份、消息方向、消息类型、关联 ID、顺序、断开与恢复；SSE 记录事件类型、事件 ID、重连提示、终止条件和可见消费结果。只保存当前会话实际接收/发送且允许保留的帧摘要，流式中间消息与最终业务结果分别建模。

下载记录触发动作、响应头、文件名语义、媒体类型、大小、内容哈希、完成/取消和可见错误；上传记录文件约束、分片/直传候选、进度、校验、服务端接受/拒绝、后台处理和最终对象。样本使用合成且无敏感内容的最小文件，写入、外发、费用与清理须另有批准。

轮询、流式连接、后台任务和浏览器关闭后的处理均要跟踪到明确终态或超时边界。页面显示成功、HTTP 接受、上传完成和后台业务完成是不同状态，不能合并成一个“成功”。

## 浏览器持久状态

按来源登记 Cookie、Web Storage（`localStorage`/`sessionStorage`）和 IndexedDB 的键名角色、作用域、生命周期、写入触发、清理方式与敏感级别，不提交秘密或业务值。Cookie 另记当前响应中可观察的安全属性和过期语义；技术上可读取不等于允许提取。

把身份/会话、偏好、缓存、草稿、离线队列和功能分桶候选分开。某个键存在只支持该时点的存储事实，不证明当前代码使用它，也不证明删除该键是安全实验。

核对登录/退出、租户切换、版本更新、清缓存、跨标签页和隐私模式后的状态，但只执行 `ART-P0-AUTH` 允许的动作。发现凭据、跨租户内容或无法解释的持久敏感数据时停止并走披露路径。

## Service Worker 与离线

若当前产品实际注册 Service Worker，记录脚本/作用域/版本身份、安装—等待—激活状态、受控页面、更新提示和已观察缓存；没有注册证据时不创建必经层。Service Worker 文件或缓存项存在不证明该响应由它提供，应结合请求 initiator、响应来源、离线回放和版本身份。

离线实验只在授权允许、数据与副作用可隔离时执行，固定离线切换时点、已缓存基线、可完成/不可完成动作、离线队列、重新联网和冲突结果。浏览器网络面板的模拟离线、真实网络中断与后端不可用是不同变量。

更新观察区分发现新版本、下载、waiting、skip-waiting/激活、页面刷新和旧客户端终止。旧缓存与新 HTML/chunk 混用可能产生水合或加载错误；只有复现的版本组合可形成限定运行主张。

## 功能开关与实验

功能开关和实验记录开关稳定 ID、来源候选、当前会话观察值、角色/套餐/租户/地区条件、分桶身份的脱敏引用、有效时间和可见结果。不得改 Cookie、参数、存储、响应或账号属性来强制进入未授权分桶。

远程配置响应、内联配置、构建常量和 bundle 构建制品分支是不同证据面。某分桶在当前会话可见，只支持该会话和时间窗；实验名称、变体代码或默认值不证明流量分配、发布范围或业务意图。

功能关闭、代码未调用、入口不可见和服务端拒绝分别建主张。对照只使用授权内自然分配或明确批准的测试账号，不以规避套餐、租户或访问控制补齐矩阵。

## 角色、权限、租户与套餐

权限矩阵以“角色 × 资源 × 动作 × 租户范围 × 套餐 × 状态”为分母，分别记录入口可见、控件可用、请求实际发生、服务端响应、数据过滤和后台结果。角色名称相同但租户、套餐、代理关系或有效期不同，应拆分上下文。

授权只通过授权内角色的正常操作和可观察的允许或拒绝结果验证：记录请求身份、拒绝发生层、可见消息、数据与异步副作用，并且不猜测隐藏资源、对象 ID、租户或管理员路径。不可见、客户端禁止和服务端拒绝是不同控制点。

当前角色获准访问某条记录不能推广到其他对象或字段；一次拒绝也不能证明全局策略。后端代码、策略或日志只有在另行获准且与部署身份绑定时才能解释服务端权限实现，否则保持独立的 `inferred`、`statically-supported` 或 `unsupported` 主张。

## 遥测与可观测性

盘点当前会话实际产生且获准检查的埋点、错误上报、性能指标、日志关联 ID、trace 候选和第三方请求。记录触发动作、载荷 schema 摘要、目标稳定 ID、采样/批处理候选、发送时机、失败与隐私分类，不保留用户标识、会话秘密或无关正文。

浏览器 API 调用、网络请求和供应商文档分别是静态、运行和声明证据；埋点名称不能直接当业务能力、成功结果或使用量。客户端“已调用发送函数”也不证明第三方接收、处理或归因成功。

卸载发送、批量 flush、离线缓冲、采样和广告/隐私同意可能改变遥测。第三方外发、真实用户影响、数据驻留或保留边界不明确时停止采集，由隐私/安全负责人决定后续处置。

## 源码、构建产物与前端制品

仅在现有、获准范围内登记源码提交/工作树、锁文件、构建配置、框架清单、HTML、JS/CSS chunk、静态资源、部署清单和 source map。每项保存稳定资产 ID、内容哈希、来源、版本、获取时间和权限；文件名哈希或部署目录名不能代替内容身份。

白盒时建立“源码身份 → 构建输入 → chunk/资源哈希 → 部署身份 → 当前会话加载事实”的链；缺一环就拆分静态与运行主张。构建执行、依赖下载、插件运行、source map 读取和生产部署资料各自需要授权，源码可读不隐式授权这些动作。

动态 import、代码分割、tree shaking、条件编译、minification、CDN 缓存和旧 chunk 会限制静态搜索。source map 只有在目标范围内已存在、合法取得且明确获准读取时才作为 `derived` 或 `static` 证据；不猜测名称、不扫描位置，也不因映射到符号就声称路径已执行。

## 响应式、设备、语言与时间状态

响应式矩阵固定设备类别、视口、像素密度、缩放、输入方式和方向，记录导航变化、内容重排、虚拟化、滚动、弹层、焦点与截断。CSS breakpoint 或设备检测代码是静态候选；只有对应设备/视口回放能支持可见行为。

语言/地区状态记录 locale 来源、文案、排序、数字/货币/日期格式、复数、文字方向和 fallback。浏览器语言、账号偏好、租户配置与 URL 参数分别记录，不能从一张本地化截图推断全部翻译或业务区域规则。

时间状态固定时区、系统时钟来源、服务端时间、夏令时、日界线和相对时间更新。改变设备时钟、时区或 locale 属于实验变量，只在批准且可恢复的环境中执行；显示时间不自动证明存储时区或后端调度语义。

## 证据边界与主张拆分

| 主张面 | 最高或候选状态 | 必需证据 | 不可跨越的边界 |
| --- | --- | --- | --- |
| 可重复可见 Web 行为 | `runtime-confirmed` | 已授权、可重复的动作、环境、当前会话、实际结果和副作用 | 只限已测版本、当前合法会话、角色、套餐、租户、配置与状态 |
| 前端静态实现 | `statically-supported` | 获准源码或制品身份、位置、内容哈希和解析方法 | 不证明对应代码已部署、已执行或当前角色可达 |
| 隐藏服务端实现或数据模型 | `inferred/unsupported` | 独立的获准后端源码、部署、日志、模式或运行证据 | 与可见行为分立；没有获准静态或运行证据时保持未知 |
| 前端隐藏或禁用控件 | `observed` | 当前角色、页面状态、DOM/可访问性与可见结果 | 不是服务端授权证明 |
| bundle 代码或功能开关存在 | `observed` | 制品 ID、内容哈希、提取方法和部署绑定缺口 | 不证明能力已部署、已启用或当前角色可达 |

- **授权主张边界：** 前端隐藏或禁用按钮只支持该角色与状态下的界面观察，不是服务端授权证明；只验证授权内角色实际得到的允许或拒绝结果，不猜测或探测未授权资源。
- **可达性主张边界：** bundle 中存在代码或功能开关只支持制品结构主张，不证明该能力已部署、已启用或能由当前角色到达；可见产品行为必须另有同版本运行证据。

可重复的可见 Web 行为可在批准实验与实际覆盖边界内标为 `runtime-confirmed`，不要求伪造隐藏内部链。内部实现、服务端数据模型、事务、权限策略与异步消费者使用独立主张；只有浏览器证据时保留 `inferred` 或 `unsupported`，获准静态证据只支持其静态上限。

## 常见盲区

| 盲区 | 默认处理 | 不可越过的结论 |
| --- | --- | --- |
| 客户端可见不等于服务端实现 | 拆分页面、网络契约、后端与数据模型主张 | 不由响应形状反推表结构、事务或内部算法 |
| 缓存与旧 chunk | 记录 HTML、chunk、CDN/浏览器/Service Worker 缓存身份 | 不把混合版本观察推广到当前部署全部会话 |
| 水合与竞态 | 保存初始 HTML、DOM 变化、请求和交互时序 | 不用终态截图消除中间错误或重复动作 |
| 后台与流式终态 | 跟踪轮询、WebSocket/SSE、任务、通知到终态或超时 | 不把接受、传输完成或页面成功等同业务完成 |
| 多角色、租户与套餐 | 使用批准观察矩阵并保留未覆盖格子 | 不从一个合法账号推广权限与能力全集 |
| 响应式、语言与时区 | 固定设备/视口、locale、时区和时间边界 | 不把单一布局或格式推广到其他状态 |

其他常见缺口包括 portal/iframe、浏览器扩展注入、预取、虚拟列表、跨标签页同步、第三方脚本、动态 import、离线队列和快速导航取消。发现这些对象时为实际证据建边；未发现时只登记搜索分母和限制。

## 纵向追踪示例

以下是中性的教学切片，顺序是：用户动作 → 客户端状态与校验 → 当前授权会话网络契约 → 可选后端/异步证据 → 可见结果。它不代表任何产品的固定拓扑；可选节点缺失时保留缺口，不用浏览器现象补写服务端代码、数据模型或异步实现。

### 示例节点

表中的“当前状态”描述该节点相关主张与现有证据的关系，使用核心封闭词汇；证据项本身仍另存来源、版本、时间与完整性字段。

| 节点 ID | 节点种类 | 当前状态 | 边界 |
| --- | --- | --- | --- |
| `product-surface:sample.browser-route` | `browser-route` | `observed` | 当前会话中可见且实际进入的浏览器表面 |
| `capability:sample.accept-action` | `capability` | `statically-supported` | 仅为示例能力候选，不声明产品业务拓扑 |
| `interaction:sample.user-action` | `user-action` | `runtime-confirmed` | 已批准且可重复的单一用户动作 |
| `asset:sample.client-handler` | `client-asset` | `statically-supported` | 仅限获准前端源码或制品中的处理候选 |
| `data:sample.client-form-state` | `client-state` | `observed` | 当前表单的最小脱敏状态 |
| `evidence:sample.client-validation` | `runtime-evidence` | `observed` | 客户端错误与是否发起请求的运行记录 |
| `claim:sample.client-validation` | `claim` | `runtime-confirmed` | 只确认已测字段、输入和页面状态 |
| `integration:sample.current-session-endpoint` | `backend-endpoint` | `observed` | 当前合法会话动作实际产生的网络契约 |
| `evidence:sample.network-contract` | `runtime-evidence` | `observed` | 脱敏请求/响应和时序记录 |
| `claim:sample.network-contract` | `claim` | `runtime-confirmed` | 只确认实际 schema、错误与异步响应形状 |
| `asset:sample.backend-candidate` | `backend-asset` | `statically-supported` | 可选；只有获准且绑定部署的后端静态证据 |
| `integration:sample.async-outcome` | `async-boundary` | `inferred` | 可选；没有日志/消息/推送证据时保持候选 |
| `evidence:sample.visible-result` | `runtime-evidence` | `observed` | 当前会话最终可见结果的脱敏记录 |
| `claim:sample.visible-result` | `claim` | `runtime-confirmed` | 只限已测角色、状态、输入与等待边界 |

### 示例类型化链接

每条边也有独立状态和证据引用；`optional` 表示只有证据与授权允许时才纳入，不表示可以猜测节点。未执行的 client-handler 到 endpoint 关系只由获准前端源码或制品支持时，最高为 `statically-supported`；当前会话实际出现的请求仍由独立网络证据支持。

| 链接 ID | 来源 ID | 关系 | 目标 ID | 当前状态 | 分支 |
| --- | --- | --- | --- | --- | --- |
| `trace-link:sample.route-to-capability` | `product-surface:sample.browser-route` | `exposes` | `capability:sample.accept-action` | `observed` | `required` |
| `trace-link:sample.action-to-handler` | `interaction:sample.user-action` | `calls` | `asset:sample.client-handler` | `statically-supported` | `required` |
| `trace-link:sample.handler-to-form-state` | `asset:sample.client-handler` | `reads` | `data:sample.client-form-state` | `statically-supported` | `required` |
| `trace-link:sample.validation-evidence` | `evidence:sample.client-validation` | `validates` | `claim:sample.client-validation` | `runtime-confirmed` | `required` |
| `trace-link:sample.handler-to-endpoint` | `asset:sample.client-handler` | `calls` | `integration:sample.current-session-endpoint` | `statically-supported` | `required` |
| `trace-link:sample.network-evidence` | `evidence:sample.network-contract` | `supports` | `claim:sample.network-contract` | `runtime-confirmed` | `required` |
| `trace-link:sample.backend-to-capability` | `asset:sample.backend-candidate` | `implements` | `capability:sample.accept-action` | `statically-supported` | `optional` |
| `trace-link:sample.endpoint-to-async` | `integration:sample.current-session-endpoint` | `emits` | `integration:sample.async-outcome` | `inferred` | `optional` |
| `trace-link:sample.async-to-visible` | `integration:sample.async-outcome` | `supports` | `claim:sample.visible-result` | `inferred` | `optional` |
| `trace-link:sample.visible-evidence` | `evidence:sample.visible-result` | `validates` | `claim:sample.visible-result` | `runtime-confirmed` | `required` |

异步结果到可见结果的候选边只有在当前场景确有异步迹象时保留，并始终是 `inferred`、`optional`；它不能取代可见结果自己的独立观察与运行证据。没有异步证据时删除候选关系会创建新版本，但不得删除已经登记的历史记录。

节点和链接均采用 `kind:namespace.qualified-key` 限定 ID，状态只使用核心主张状态，关系只使用 `exposes`、`calls`、`reads`、`supports`、`implements`、`emits` 和 `validates` 等核心类型。后来的后端、日志或异步证据新建节点和边；它可以支持、反驳或取代候选，但不覆盖原会话观察。

## 有序工作流

1. 从 `ART-P0-AUTH` 与当前 `ART-G0-AUTH` 的 `pass` 判定复制产品、部署、账号、角色、租户、套餐、数据、动作、工具、速率和停止边界；无法绑定当前合法会话时不进入目标系统。
2. 冻结“角色 × 套餐 × 语言/地区 × 设备/视口 × 数据状态”分母，盘点公开或正常可见入口、浏览器路由、空/有数据/加载中/错误/权限拒绝状态及后台结果；未授权格子保持缺口。
3. 为浏览器路由和后端端点分配不同稳定 ID，把用户目标、导航、重定向、DOM/可访问性与可见结果建成产品地图，不从路由名推断 API 或业务能力全集。
4. 仅在观察面可用且获准时检查 SSR/CSR/静态生成、hydration、组件、客户端状态、表单与构建制品；分别记录客户端校验和服务端校验，不由前端阻断推断服务端授权或验证。
5. 仅记录当前会话已执行动作实际产生且获准检查的网络证据，保存脱敏 schema、分页、错误、幂等和异步结果；REST、GraphQL、下载、上传、WebSocket 与 SSE 按各自契约建模，不扩展端点清单。
6. 跟踪流式与后台处理到终态或明确超时，核对 Cookie/Web Storage/IndexedDB、Service Worker/离线、功能开关/实验、遥测和响应式/locale/时区状态；改变状态前确认独立实验授权与恢复方案。
7. 仅在现有、可绑定且获准的范围内检查源码、构建配置、chunk、source map、后端或日志，将静态结构、部署事实、当前会话运行和隐藏实现分别建主张，不补齐缺失内部链。
8. 用正常可见路径和授权内角色的可观察允许/拒绝结果验证权限，不猜测或探测未授权资源；最后审查盲区、反证、停止记录、主张状态和类型化链接，并按[覆盖、质量与冻结](../core/coverage-quality-and-freeze.md)冻结。

## 停止与安全边界

- 禁止认证绕过、会话劫持或改变身份材料来扩大当前会话权限。
- 禁止猜测、提取或遍历隐藏租户 ID、对象 ID、账号或管理员入口。
- 禁止凭据提取，包括令牌、Cookie 值、口令、恢复码和客户端存储中的秘密。
- 禁止规避付费功能、套餐、配额、功能分桶或计费流程。
- 禁止任意端点枚举、目录扫描、参数爆破或从偶然暴露端点扩展探测清单。
- 禁止速率滥用、无批准压力测试、批量抓取或可能影响真实用户的并发实验。
- 禁止授权范围外发现 source map，包括猜测文件名、扫描路径或从公开 chunk 扩展未获准资产。
- 禁止超出已批准实验重放或修改请求；请求变更、故障注入、重试、写入和清理都需要分别批准。

出现授权或部署身份漂移、跨租户/跨账号内容、凭据或个人数据暴露、未知外发、不可控费用、真实用户影响、无法恢复写入、速率上限或捕获范围超限时立即停止相关动作。保存最小且脱敏的现场引用，隔离材料，并按 `ART-P0-STOP` 交给安全/隐私负责人。

恢复必须重新授权并取得绑定新输入身份的 G0 `pass`；不能通过换浏览器、换账号、改请求、清缓存或换执行者绕过停止条件。只能继续不触及该边界的离线整理，所有未完成路径保持 `unsupported`、`inferred` 或明确缺口。

## 相关

- [端到端工作流](../core/end-to-end-workflow.md)
- [产品与业务建模](../core/product-and-business-modeling.md)
- [运行时实验](../core/runtime-experiments.md)
- [证据与置信度](../core/evidence-and-confidence.md)
- [授权、隐私与安全](../core/authorization-privacy-and-safety.md)
- [黑盒访问轨道](../access-tracks/black-box.md)
- [灰盒访问轨道](../access-tracks/gray-box.md)
- [白盒访问轨道](../access-tracks/white-box.md)
- [返回指南入口](../README.md)
