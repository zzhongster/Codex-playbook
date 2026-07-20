# 反模式：公开构造器校验了，Decoder 却绕过边界

## 一句话结论

Codable/序列化模型的 invariant 必须同时约束直接构造和 decode；只在 public initializer 校验，合成 decoder 仍可注入非法 schema、路径、哈希或逻辑键。

## 场景

实机证据报告包含 schema version、artifact logical name、basename、SHA-256、failure reason 和 verdict。

## 失败表现

- 直接构造会拒绝非法值，手工 JSON decode 却接受。
- artifact filename 可带 `/`、`..`、反斜杠或 `file:` URL。
- SHA-256 接受大写、非 hex 或非 64 字符。
- 未知 schema 被默默装进当前模型。
- logical key 经“清洗”后碰撞，覆盖另一条 artifact。

## 根因

把 Swift 合成 `Decodable` 当成对已有 initializer 的调用。实际上合成 decoder 直接给 stored properties 赋值，不会自动复用自定义校验。

## 正确做法

- 把 invariant 放进单一验证函数或 throwing initializer。
- 自定义 `init(from:)`，decode 后显式走同一验证边界。
- schema version 采用精确 allowlist，不做未知版本 best effort。
- logical name 使用狭窄 ASCII 语法并拒绝非法值，不做有碰撞风险的 rewrite。
- artifact filename 只允许 basename；hash 只允许 canonical lowercase SHA-256。
- failure reason 若检测到路径标记，宁可整字段替换为 `[path]`。

## 验证清单

- 每个非法值同时测试 direct init 和 JSON decode。
- 覆盖 POSIX、Windows separator、file URL、Unicode、空白、超长 key。
- 未知 schema decode 必须失败。
- 报告 verdict 由 validator 产生，不能由调用者随意伪造。

## 相关

- [忽略大型证据却不提交可审计清单](ignored-evidence-without-durable-manifest.md)

