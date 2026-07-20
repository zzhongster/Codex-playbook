# 反模式：变化驱动视频结束时不补合法尾帧

## 一句话结论

ScreenCaptureKit 画面静止时不会持续给 30 fps 新帧；停止录制时只调用 `endSession(t1)`，不保证视频轨真的延伸到 `t1`。应按帧率下界重推最后完整帧，且不能制造重复 PTS。

## 场景

桌面最后几秒静止，但系统音频和麦克风仍持续到停止时刻。目标视频帧率为 30 fps。

## 失败表现

- 音频轨到达 `t1`，视频轨停在最后一次屏幕变化处。
- 容器时长正确，但播放器结尾黑帧、冻结策略不一致或 A/V endpoint delta 超标。
- 直接把最后帧重定时到 `t1`，与上一帧间隔不足 1/30 秒，生成重复或过密 PTS。
- backpressure 时丢掉恰好位于 `t1` 的最后帧，finish 再无 owned frame 可重试。

## 根因

把变化驱动的输入流误当成固定帧率流；或者只跟踪“看见的最后 PTS”，没有区分“成功 append 的最后 PTS”和可拥有的最新完整帧。

## 正确做法

- 保存最新完整帧的 owned copy。
- 分别记录 observed latest 与 appended latest PTS。
- 停止时计算最早合法 tail PTS：至少比最后成功 append 晚一个帧周期，且不晚于 `t1`。
- 若最早合法 PTS 等于 `t1`，无需额外帧也可结束；否则 retime 并 append tail。
- tail backpressure 只在有界期限内重试，超时转 terminal failure。
- 最后 `endSession(atSourceTime: t1)` 并 mark inputs finished。

## 验证清单

- 静止画面结束、1/60 秒源 duration、恰好 `t1`、`t1±1 ms`。
- 解码后的相邻视频 PTS 至少相隔 1/30 秒。
- 最终视频覆盖请求结束时间且不越过 `t1`。
- 模拟一次 tail backpressure，证明 owned latest frame 可重试。

