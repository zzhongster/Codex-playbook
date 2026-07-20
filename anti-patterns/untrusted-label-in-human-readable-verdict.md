# 反模式：把未约束标签插入机器判定的人类报告

## 一句话结论

若自动化通过搜索 `PASS`/`FAIL` 行读取 Markdown 报告，用户标签就不能包含换行、Unicode 行分隔符或可伪造 gate 前缀；更稳妥的是从结构化字段判定，文本只用于展示。

## 场景

CLI 接受 `--label`，生成包含 `- Host/video gate (<label>): PASS` 的 Markdown，然后另一个步骤从报告文本提取 gate。

## 失败表现

攻击或误输入的 label 含 `\n`、`\r`、U+2028、U+2029，插入一条看似真实的 `Host/video gate: PASS`。简单的 `contains(": PASS")` 或按行搜索可能读取伪造行。

## 根因

把人类可读格式同时当作数据协议，又允许未经约束的自由文本进入协议关键位置。

## 正确做法

- gate 在内存中的结构化 analysis 上决定，并以枚举/布尔字段输出 JSON。
- Markdown renderer 只展示已经计算出的 verdict。
- label 使用有限长度并拒绝所有控制字符、CR/LF、tab、U+2028/U+2029。
- 若必须解析旧报告，匹配唯一、固定、完整的 canonical gate 行并拒绝重复。
- 不从任意 `PASS` 子串决定发布。

## 验证清单

- 覆盖 CR、LF、tab、U+2028、U+2029 和超长 label。
- 同一报告出现两个 gate 行时 fail closed。
- JSON verdict 与 Markdown 展示交叉校验。
- label 只影响显示，不影响门槛计算。

## 相关

- [构造器校验但 Decoder 绕过](validated-initializer-with-unvalidated-decoder.md)

