# 产品逆向工程操作工具箱

**证据成熟度：`proposed`**

**适用范围：** 用于发现、复制和校验本指南发布的项目布局、检查清单、任务包、13 份记录模板、8 份 JSON Schema 与 14 份正反样例；不授予目标系统或数据的访问、运行或修改权限，也不证明产品事实或替代人工门禁。

## 使用边界

工具箱把通用证据契约落到可复制记录和机器校验，不是自动取证系统。使用任何模板前，先完成目标项目的授权与数据边界；把模板复制到目标项目后，必须替换占位符、绑定真实输入身份并按项目保留策略存放证据。模板页面的 `proposed` 只描述模板方法的证据成熟度，不会提高产品主张状态；Schema 或测试通过只证明结构满足当前规则，不证明记录内容真实、完整、获准或足以支持决定。

以下三个操作文档说明如何组织项目与人工协作：

- [项目证据仓布局](project-layout.md)
- [阶段与技术栈检查清单](checklists.md)
- [AI Agent 可复制任务包](prompts.md)

## 人工可读记录模板（13）

| 模板 | 记录用途 |
| --- | --- |
| [项目章程](templates/project-charter.md) | 固定目标、授权、环境、数据、输出、风险和审批边界 |
| [技术资产记录](templates/asset-record.md) | 登记源码、制品、配置、数据与部署资产身份 |
| [业务能力记录](templates/capability-record.md) | 组织角色、结果、产品表面和场景 |
| [交互记录](templates/interaction-record.md) | 描述前置状态、用户动作、系统反应与可见结果 |
| [业务规则记录](templates/rule-record.md) | 登记规则、优先级、冲突和证据引用 |
| [数据对象记录](templates/data-object-record.md) | 关联业务身份、技术别名和数据分类 |
| [API 与集成记录](templates/api-integration-record.md) | 描述协议、生产者、消费者和契约版本 |
| [运行时实验记录](templates/experiment-record.md) | 分离冻结协议、执行结果和副作用清理证据 |
| [主张与证据关联记录](templates/claim-evidence-record.md) | 维护原子主张状态、置信度和支持/反驳关系 |
| [决定记录](templates/decision-record.md) | 保存有权人类的选项、决定、影响和取代关系 |
| [覆盖与冻结记录](templates/coverage-and-freeze.md) | 固定分母、覆盖桶、门禁与冻结身份 |
| [As-Is 到 To-Be 追踪](templates/as-is-to-be-trace.md) | 把已登记事实追踪到需求和人类处置决定 |
| [竞品洞察记录](templates/competitor-insight.md) | 约束竞品观察、比较边界和战略责任人 |

## 机器可读 Schema（8）

全部 Schema 使用 JSON Schema Draft 2020-12。`definitions` 提供共享定义，其余七份用于验证对应 JSON 记录；引用在本仓库本地注册，不依赖运行时联网解析。

| Schema | 用途 |
| --- | --- |
| [共享定义](schemas/definitions.schema.json) | 稳定 ID、状态、关系、引用和通用字段 |
| [资产](schemas/asset.schema.json) | 资产身份、来源、分类与可达性 |
| [证据](schemas/evidence.schema.json) | 证据来源、保管、完整性和方法 |
| [主张](schemas/claim.schema.json) | 原子产品主张、状态、置信度和边界 |
| [追踪链接](schemas/trace-link.schema.json) | 类型化来源、关系、目标和证据闭包 |
| [实验](schemas/experiment.schema.json) | 协议、运行、结果、副作用和清理 |
| [决定](schemas/decision.schema.json) | 备选、选择、审批输入和影响 |
| [覆盖摘要](schemas/coverage-summary.schema.json) | 分母分区、门禁和冻结控制 |

## 正反样例（14）

每类记录都提供一个应通过 Schema 与语义校验的正例，以及一个必须被拒绝的反例。样例只用于验证工具行为，不能复制为产品证据。

| 记录类型 | 正例 | 反例 |
| --- | --- | --- |
| 资产 | [asset.valid.json](schemas/examples/asset.valid.json) | [asset.invalid.json](schemas/examples/asset.invalid.json) |
| 证据 | [evidence.valid.json](schemas/examples/evidence.valid.json) | [evidence.invalid.json](schemas/examples/evidence.invalid.json) |
| 主张 | [claim.valid.json](schemas/examples/claim.valid.json) | [claim.invalid.json](schemas/examples/claim.invalid.json) |
| 追踪链接 | [trace-link.valid.json](schemas/examples/trace-link.valid.json) | [trace-link.invalid.json](schemas/examples/trace-link.invalid.json) |
| 实验 | [experiment.valid.json](schemas/examples/experiment.valid.json) | [experiment.invalid.json](schemas/examples/experiment.invalid.json) |
| 决定 | [decision.valid.json](schemas/examples/decision.valid.json) | [decision.invalid.json](schemas/examples/decision.invalid.json) |
| 覆盖摘要 | [coverage-summary.valid.json](schemas/examples/coverage-summary.valid.json) | [coverage-summary.invalid.json](schemas/examples/coverage-summary.invalid.json) |

## 验证命令

在仓库根目录验证一份记录；CLI 会按记录形状推断七类记录 Schema，并同时执行当前语义规则：

```bash
python3 tools/validate_product_reverse_engineering_guide.py path/to/record.json
```

推断不合适或需要显式固定类型时使用 `--schema`，例如：

```bash
python3 tools/validate_product_reverse_engineering_guide.py --schema asset path/to/record.json
```

不带记录参数运行完整指南验证器；它覆盖文档治理、链接、模板、Schema、样例和案例契约：

```bash
python3 tools/validate_product_reverse_engineering_guide.py
```

记录 CLI 和完整验证器均默认拒绝无法解析、类型未知或契约不闭合的输入。验证成功不授予任何新权限、不证明产品事实，也不会提高产品主张状态；运行目标产品、读取数据或发布结论仍分别需要当前授权、证据和人工决定。
