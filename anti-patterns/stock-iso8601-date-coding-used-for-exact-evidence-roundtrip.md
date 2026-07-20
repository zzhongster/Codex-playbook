# 反模式：用默认 ISO-8601 日期编码做精确证据往返

## 一句话结论

当证据发布要求 `decode(encode(value)) == value` 时，Foundation 默认 `.iso8601` 日期策略可能丢失亚秒精度；必须先用含任意亚秒的测试证明编码契约，或采用能精确恢复内部时间值的格式。

## 场景

探针生成 Codable JSON，写入临时文件后重新读取、解码并与内存报告严格相等，验证通过才原子改名。

## 失败表现

- 整秒 fixture 测试通过，实机 `Date()` 报告全部 `roundTripFailed`。
- JSON 肉眼看起来正常，但 `createdAt`/`finishedAt` 解码后不等于原值。
- 为了“让实机通过”删除回读校验，失去 fail-closed 证据边界。

## 根因

测试数据只覆盖整秒；默认 ISO-8601 字符串不承诺保存 `Date` 的任意亚秒表示。即使打印出的时间相同，`Date` 的底层 Double 仍可能不相等。把 Unix epoch 与 Foundation reference date 相互换算也可能引入舍入。

## 正确做法

- 测试至少包含 `Date()` 和手工构造的非整秒时间。
- 区分三层验证：临时文件 bytes 等于预期、JSON 可解码、解码模型重新执行全部不变量。
- 若业务需要对象严格相等，可把 `timeIntervalSinceReferenceDate` 用 Swift 的 round-trip decimal string 编码，再从同一 reference date 恢复。
- 在 schema 文档中明确 epoch、单位和类型；不要默默更换日期格式。
- 保留 `RENAME_EXCL`/不覆盖发布，失败时删除临时文件而不污染最终路径。

## 验证清单

- 整秒、随机亚秒、相邻 created/finished 时间都能严格往返。
- timeout/failure 型报告与 PASS 报告走同一个 writer。
- 解码器拒绝非有限值和错误类型。
- 发布失败不覆盖旧证据、不遗留临时文件。

## 相关

- [有验证初始化器、无验证解码器](validated-initializer-with-unvalidated-decoder.md)
- [忽略证据却没有持久清单](ignored-evidence-without-durable-manifest.md)
