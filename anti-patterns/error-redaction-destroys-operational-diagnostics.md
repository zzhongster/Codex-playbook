# 反模式：错误脱敏时抹掉操作诊断

## 一句话结论

隐私脱敏应只删除敏感值，不应把 start/append/finish、writer status、错误 domain/code 等定位信息压成“录制失败”；安全与可诊断性可以同时保留。

## 场景

录屏失败信息需要展示给用户或写入日志，但临时路径、最终文件名和用户目录不应泄露到通用诊断。

## 失败表现

- 所有错误只显示 `Media writer failed`，无法区分 start、video append、audio append 或 finish。
- timeout 先 cancel writer，再读取 status/error，原始失败被 `.cancelled` 覆盖。
- underlying description 中仍含完整临时路径、`file://` URL 或 basename。
- 为避免泄露路径，连 POSIX errno 或 OSStatus 也一起删除。

## 根因

没有在错误产生的边界构造结构化诊断；事后只能在整段字符串上做全有或全无的处理。

## 正确做法

- 在 writer 边界保存 operation、status、safe domain/code 和 localized description。
- timeout 在 cancel 之前 snapshot diagnostics。
- 只按已知 temporary/proposed URL、file URL 字符串和 basename 做定向 redaction。
- 保留 POSIX errno、CoreMedia OSStatus、writer status 与上下文。
- UI 需要展示临时文件位置时，用单独、明确授权的字段传递，不混进通用错误。

## 验证清单

- start、video/audio append、tail retime、finish timeout 分别断言 operation。
- fake writer 在 cancel 时改变错误，证明 snapshot 发生在 cancel 前。
- 测试原始 path、file URL 和 basename 均不出现在安全诊断。
- domain/code 和非敏感描述仍保留。

