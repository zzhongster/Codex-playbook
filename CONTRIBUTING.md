# 贡献规范

## 分类

| 类型 | 目录 | 最低要求 |
| --- | --- | --- |
| Guide | `guides/` | 覆盖跨阶段或跨角色的完整工作流，明确受众、边界、导航和方法/建议的证据成熟度 |
| Pattern | `patterns/` | 至少在两个项目中验证，写清适用边界 |
| Anti-pattern | `anti-patterns/` | 有具体失败现象、根因、修复和验证方式 |
| Experiment | `experiments/` | 有假设、对照、数据、结论 |

一次项目中发现的可复用做法，如果尚未跨项目复现，不要提前包装成 Pattern；先记录为 Anti-pattern 或 Experiment。

## Guide 收录条件

Guide 用于组织端到端方法：它应当连接多个阶段或角色，并给出可执行的选型路径、证据要求、安全边界、导航和验证入口。只解释一个局部技巧、一次故障或一组实验数据的内容，应分别进入 Pattern、Anti-pattern 或 Experiment，而不是单独建立 Guide。

Guide 可以汇总成熟度不同的做法，但每项关键方法或建议必须标注以下证据成熟度之一。文档头部的“证据成熟度”是“本指南方法或建议的支撑证据成熟度”的机器可读简称。四个标签只描述逆向工程方法或建议的支撑证据成熟度，不描述目标产品主张的真假。目标产品主张使用主张状态、置信度和证据引用表达可信程度。

| 标签 | 含义 |
| --- | --- |
| `cross-project-validated` | 方法或建议已在至少两个相互独立的项目中验证，并记录各自证据和适用边界 |
| `project-validated` | 方法或建议已在一个真实项目中验证，尚未完成独立项目复现 |
| `industry-established` | 方法或建议有行业标准、权威规范或稳定公开实践支持，并注明可追溯来源与本地适用边界 |
| `proposed` | 方法或建议仍待验证，不得表述为已经验证的做法 |

结构校验通过只说明 Guide 文档完整，不能自动提升任何方法或建议的证据成熟度，更不能改变产品主张的状态或置信度。

## 从 Guide 提炼正式条目

- 提炼为 Pattern：必须达到 `cross-project-validated`，并继续满足“至少在两个相互独立的项目中验证”的硬性要求；Guide 中出现或结构校验通过都不能替代项目证据。
- 提炼为 Anti-pattern：必须记录具体失败现象、根因、修复和验证方式，并明确证据来自哪个项目或环境。
- 提炼为 Experiment：必须保留假设、环境与控制变量、对照、数据、结论和未覆盖范围。
- `project-validated`、`industry-established` 或 `proposed` 内容不会仅凭标签自动晋升；应按目标类型补齐上述证据后再移动或新建正式条目。

## 文件名

- 英文小写短横线，例如 `shared-readiness-gate-requires-irrelevant-signal.md`。
- 实验以日期开头，例如 `2026-07-20-macos-region-capture-coordinate-spaces.md`。

## Anti-pattern 模板

~~~markdown
# 标题

## 一句话结论
## 场景
## 失败表现
## 根因
## 正确做法
## 验证清单
## 适用范围
## 相关
~~~

## Experiment 模板

~~~markdown
# 实验：标题

**日期**：
**项目**：

## 假设
## 环境与控制变量
## 对照
## 数据
## 结论
## 可复用发现
## 未覆盖范围
~~~

## 质量要求

- 观察值与推断分开写。
- 精确记录单位、坐标空间、版本和验收阈值。
- 不把未运行的平台、拓扑或硬件写成已通过。
- 大型证据不提交时，说明保存位置、可用性限制，并提交内容哈希。
- 不包含密钥、访问令牌、用户名、绝对用户目录或其他敏感信息。
- 机器可读示例的身份字段和业务主体的 identity/name/id/address/contact 字段必须使用明确的虚构标记（例如 `Sample`、`Synthetic` 或 `REPLACE`）；这同样适用于 schema 必需的 `owner`、`reviewer`、`project_id` / `project_name`。customer/client/company/tenant 的 status、role 等枚举元数据不属于身份字段。
- 机器可读示例扫描所有字符串中的 IPv4/IPv6 和符合 DNS 主机语法、以 2–63 个小写字母结尾的点分名称；非保留名称默认按主机拒绝，不依赖固定 TLD 清单。域名只使用 `example.invalid`、`example.com` 等明确文档域（也可使用 `.example`、`.test`、`.localhost`），IPv4 只使用 TEST-NET `192.0.2.0/24`、`198.51.100.0/24`、`203.0.113.0/24`，IPv6 只使用文档网段 `2001:db8::/32`。type/class/symbol/package/namespace/assembly/module 等明确技术字段按字段语义允许合法点分标识符；普通字段只窄放行标准 Java 平台根、PascalCase .NET 命名空间和反向域 package 的纯技术全值。`version`、`assembly_version`、`file_version`、`product_version` 等版本字段允许合法四段版本；同样的值出现在普通文本或网络字段时仍按 IPv4 扫描。已知安全文件扩展的纯文件名不按网络主机处理。任何豁免都不能遮蔽 URL、host 标签、凭据或绝对用户路径。
- `authorization` 对象按普通元数据递归扫描；标量只允许明确的安全状态枚举。Basic、Bearer、Negotiate、Digest、自定义 scheme 加 payload，以及 username/nonce/response/signature 等认证参数一律视作凭据材料。
- 即使值声称是占位符，也不提交 password/token/API key 形态、真实或疑似客户/企业身份记录、非保留主机名或绝对用户路径；普通稳定 ID 和 SHA-256 不应被误报。
