# Pattern: Pause by timeline admission

## 一句话结论

录屏暂停应关闭样本 admission，并让所有音视频来源共享同一组 stream-clock pause interval；恢复后减去累计暂停时长，而不是分别用 wall clock 修补各轨时间戳。

## 适用场景

- ScreenCaptureKit 视频/系统声音与 AVAudioEngine 麦克风组合录制。
- writer 必须保持一个连续 session，成片不能包含暂停期间的空白。
- 暂停/恢复可能重复多次，Stop 也可能发生在 paused/resuming 状态。

## 实现要点

1. 以流同步时钟定义 `t0`、每个 `pauseStart`/`resumeEnd` 和最终 `t1`。
2. `RecordingClock` 保存已完成 pause interval 及当前 active pause。
3. 视频帧和音频 buffer 都通过同一个 clock 映射；暂停内样本丢弃，跨边界 buffer 在精确帧边界裁剪。
4. 暂停时保留 capture stream 和 writer，只关闭 worker admission。这样没有重建 SCStream/AVAudioEngine 的盲区，也不会出现两条流恢复时刻不一致。
5. Stop 发生在暂停中时，输出终点取 pause boundary，而不是当前 wall-clock time。
6. UI 计时同样减去累计暂停时间，但媒体正确性不能依赖 UI 计时器。

## 为什么不停止并重建流

- SCStream 和 AVAudioEngine 重启都有非确定延迟。
- 两条流无法在同一瞬间恢复，必须再做复杂的补静音/补帧。
- 重建会放大设备配置变化和权限边界的失败面。

只有在系统资源占用明确要求暂停时彻底停流，且已有可量化的恢复延迟预算时，才值得选择重建方案。

## 验证清单

- 视频、系统声音、麦克风在一次和十次暂停后仍从同一输出时刻继续。
- 跨 pause-start 和 resume-end 的音频 buffer 被精确裁剪。
- 暂停期间到达的静态/变化帧都不进入 writer。
- paused/resuming 状态下 Stop/Quit 只执行一次收尾。
- 输出 PTS 单调，成片时长等于 active duration。

