# 项目证据仓布局与单一权威

**证据成熟度：`proposed`**

**适用范围：** 用于把本指南落地到一个已授权目标项目，规定仓库内相对路径、人工编写记录、机器记录、运行实验、决定、覆盖状态与可重建投影的边界；它不授权创建外部证据副本，也不替代目标项目的数据分级和保留策略。

本布局以任务包声明的 `workspace_root_id` 为路径锚点。表中所有路径都相对该根解析；不得把个人目录、盘符或临时绝对路径写入记录。对象字段沿用[证据与置信度](../core/evidence-and-confidence.md)，运行产物沿用[运行时实验](../core/runtime-experiments.md)，结构化记录应通过本工具箱的[模式](schemas/definitions.schema.json)验证。

## 建议目录

```text
knowledge/
├── human/                 # 面向人类的解释、地图和交付正文
├── records/               # 资产、证据、主张、链接等机器记录
├── evidence/
│   └── indexes/           # 原始证据的脱敏索引、哈希与受控定位符
├── runtime/
│   ├── protocols/         # 运行前冻结的实验协议
│   ├── results/           # 实际观测、首错与复现结果
│   └── effects/           # 副作用、清理与残留核对
├── decisions/             # 具名人类签署的不可变决定
├── coverage/              # 分母、门禁输入、缺口和冻结状态
└── generated/             # 由上述权威记录确定性生成的只读投影
```

## 权威分区注册表

| partition_id | relative_path | content_class | provenance | authority | git_policy |
| --- | --- | --- | --- | --- | --- |
| human-docs | `knowledge/human/` | 产品地图、解释与面向决策的正文 | authored | writable-canonical | tracked-reviewed |
| machine-records | `knowledge/records/` | 资产、证据、主张和类型化链接 | authored | writable-canonical | tracked-schema-validated |
| evidence-indexes | `knowledge/evidence/indexes/` | 哈希、脱敏摘要、受控定位符和保管元数据 | authored | writable-canonical | tracked-redacted-index-only |
| runtime-protocols | `knowledge/runtime/protocols/` | 运行前冻结的协议和允许动作 | authored | writable-canonical | tracked-immutable-versioned |
| runtime-results | `knowledge/runtime/results/` | 实际观测、失败和复现结果 | authored | writable-canonical | tracked-append-only |
| runtime-effects | `knowledge/runtime/effects/` | 写入、副作用、清理和残留核对 | authored | writable-canonical | tracked-append-only |
| decisions | `knowledge/decisions/` | 授权、风险接受和发布批准 | authored | writable-canonical | tracked-human-signed |
| coverage | `knowledge/coverage/` | 分母、覆盖、门禁输入和冻结清单 | authored | writable-canonical | tracked-versioned |
| generated-outputs | `knowledge/generated/` | 报表、网站、图谱和搜索投影 | generated | read-only-projection | tracked-rebuildable |

`content_class` 描述允许出现的事实类别，`provenance` 区分人工/工具有责任地写入的权威记录与纯生成产物，`authority` 决定该分区能否成为事实修改入口。路径不能按执行者或工具另开同义目录；确需扩展时，先由逆向负责人更新注册表并记录迁移决定。

## 单一可写权威与投影

同一事实只能有一个 `writable-canonical` 分区。例如主张状态写在机器记录，面向人的报告只按稳定 ID引用该主张；实验实际值写在 result，coverage 只引用其哈希和判定。重复展示不等于重复拥有。

`read-only-projection` 必须可从已提交权威记录确定性重建，并记录生成命令、工具版本、输入 allow-list 与哈希。禁止手工修补生成投影；发现错误应修改有写权的源记录、复核其证据，再重新生成。若两个文件都可修改同一事实，先停止合并并指定唯一权威，而不是用“最后写入者获胜”。

人工编写不表示无需校验：`authored` 记录仍须有负责人、证据引用、模式验证和评审。`generated` 也不表示事实正确：它只证明投影忠实于输入，不能提高产品主张状态、置信度或方法成熟度。

## 原始与敏感证据边界

原始网络载荷、数据库导出、生产日志、二进制、屏幕录制及任何含凭据、个人信息、客户数据或跨租户数据的材料，默认保存在普通 Git 工作树之外，并服从目标项目批准的加密、访问、地域、保留与删除策略。仓库中只保存 SHA-256、采集时间窗、版本/环境身份、数据分类、保管人、受控定位符和足以复核来源的脱敏索引；不提交原始载荷。

索引中的受控定位符不得含秘密值或可公开访问的下载令牌。证据需要被移交时，由保管人通过获批通道授权访问；无法合法保留时，记录不可逆删除证明、此前内容哈希和受影响主张，不能用复制进 Git 的方式规避保留限制。

## 文件身份与命名

- 权威记录使用稳定 ID 命名，例如 `knowledge/records/claim/example.checkout-tax.json`；显示名称变化不改文件身份。
- 运行协议、结果、效应使用不同稳定 ID 和文件，result/effects 以 protocol ID 与内容哈希绑定协议，不把执行结果写回冻结协议。
- 人类决定放在 `knowledge/decisions/`，门禁生成器只引用决定 ID 与哈希；Agent 或生成器不能写入签署人和决定时间。
- 被替换文件保留旧版本和 `replaces` 关系；禁止原地删除历史证据来制造一致。
- 所有索引、记录和生成清单使用规范化相对路径；验证器从任务包声明的工作目录运行，不根据当前 shell 猜根目录。

## 最小写入流程

1. 先核对任务包的授权与工作区身份，确认目标相对路径属于上表唯一分区。
2. 对原始材料先执行数据分类；敏感或大体积证据进入 Git 外受控存储，仓库只写脱敏索引及哈希。
3. 写入或追加 canonical 记录，逐条引用证据；未知保持未知，冲突保留双方。
4. 运行 `python3 tools/validate_product_reverse_engineering_guide.py` 和目标项目声明的记录验证命令。
5. 经人类评审后生成投影；生成器校验输入 allow-list 与哈希，不反写 canonical 分区。

## 相关

- [任务包提示库](prompts.md)
- [阶段与技术栈检查清单](checklists.md)
- [人机协作](../core/human-agent-collaboration.md)
- [覆盖、质量与冻结](../core/coverage-quality-and-freeze.md)
- [返回指南入口](../README.md)
