# 反模式：跨 `t0` 音频在视频原点确认前写入

## 一句话结论

即使已经计算出共享 `t0`，跨界音频也应先缓冲，直到 `t0` 视频帧被 writer 成功接受；否则视频 append 失败或 backpressure 会让音频轨单独建立错误的会话开头。

## 场景

系统音频在 arming 阶段持续回调，一个 buffer 从 `t0` 之前跨到 `t0` 之后；视频首帧需要 retime 到零并写入。

## 失败表现

- 音频零点已经写入，但视频 t0 帧因 backpressure 尚未接受。
- 首帧最终失败，writer 中却残留一段只能取消的音频。
- 音视频首样本谁先到取决于 callback 调度，而不是会话协议。

## 根因

把“timestamp 可映射”误当成“recording 已被媒体 writer 正式 admission”。统一时钟不足以替代明确的起始提交屏障。

## 正确做法

- arming 阶段保存有界音频 snapshot。
- 视频 t0 帧成功 append 后，原子地切换到 recording 并按时间顺序释放音频。
- t0 video append backpressure 可有界重试；失败则取消 writer，不释放音频。
- crossing buffer 用 RecordingClock 裁到第一帧不早于零。
- arming 音频缓存超上限时 fail closed。

## 验证清单

- t0 video 尚未接受时，audio destination 没有 append。
- video 接受后 crossing audio 的输出 PTS 为零且帧数正确。
- video t0 失败时 writer cancel，缓存清空。
- arming audio 溢出有明确错误，不做静默 drop-oldest。

