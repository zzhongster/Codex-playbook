# 贡献规范

## 分类

| 类型 | 目录 | 最低要求 |
| --- | --- | --- |
| Pattern | `patterns/` | 至少在两个项目中验证，写清适用边界 |
| Anti-pattern | `anti-patterns/` | 有具体失败现象、根因、修复和验证方式 |
| Experiment | `experiments/` | 有假设、对照、数据、结论 |

一次项目中发现的可复用做法，如果尚未跨项目复现，不要提前包装成 Pattern；先记录为 Anti-pattern 或 Experiment。

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

