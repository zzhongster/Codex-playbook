# 反模式：媒体 append 失败后让 writer 继续存活

## 一句话结论

`AVAssetWriterInput.append` 返回 false 或媒体深拷贝失败后，writer 必须进入单一终态并释放所有资源；把失败当作普通丢帧继续录制，会导致挂起、伪成功或损坏输出。

## 场景

异步视频/音频 worker 向同一个 `AVAssetWriter` 写数据，输入 backpressure 与真正失败需要区分。

## 失败表现

- append false 后后续调用仍排队，直到 finalizing 超时。
- 某个 caller 收到错误，其他正在等待 `finish()` 的 continuation 永不恢复。
- 失败后仍调用 publish，生成部分可播放但不完整的 MP4。
- cancel/finish 重复释放 pixel buffer adaptor 或 writer input。

## 根因

把 `isReadyForMoreMediaData == false`、`append == false`、copy OSStatus 和 writer `.failed` 混为同一种“稍后重试”。同时没有一个串行 owner 管理 terminal result。

## 正确做法

- readiness false 可返回明确的 backpressure 结果；append false 是 terminal error。
- writer 的 start、append、tail、finish、cancel 都在同一串行状态机执行。
- 第一个 terminal failure 保存诊断、取消 underlying writer、释放输入与最新帧，并恢复全部等待者。
- cancellation、finish timeout 和 append failure 使用不同错误。
- 失败会话禁止原子发布，但保留临时路径供诊断。

## 验证清单

- 对 video、audio、tail append 和 buffer copy 分别注入失败。
- 多个并发 `finish()` waiter 得到同一个终态。
- cancel 幂等，资源快照最终全部为空。
- append 失败后任何新 append 都立即返回 terminal error。

## 相关

- [变化驱动视频结束时不补尾帧](variable-rate-video-finish-without-tail-frame.md)
- [错误脱敏抹掉操作诊断](error-redaction-destroys-operational-diagnostics.md)

