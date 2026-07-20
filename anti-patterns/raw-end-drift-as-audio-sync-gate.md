# 反模式：用原始端点时长差直接判定音频同步

## 一句话结论

两个回调源的“最后一个事件时间”受 buffer cadence 和停止顺序影响，不能直接作为时钟漂移验收；应估计各源相对 host/video 的时钟斜率与有界校正后 residual。

## 场景

ScreenCaptureKit 系统音频与独立 AVAudioEngine 麦克风连续采样 60 分钟，目标是判断 ±1,000 ppm 重采样器能否把同步误差控制在 100 ms。

## 失败表现

实测系统 duration 为 3605.18 秒、麦克风为 3605.40 秒，原始端点差 220 ms。若直接比较端点会判 FAIL，但两个源的时钟估计和有界 host/video residual 都为 0 ms。

## 根因

最后一个 buffer 的结束位置同时包含：

- callback block 大小；
- start/stop admission 时刻；
- 最后事件是否刚好跨过截止点；
- 设备时钟速率。

只有最后一项才是要验证的长期漂移。

## 正确做法

- 每条 trace 保存 host time、source sample time、frame count 和 sample rate。
- 分别拟合 system→host、microphone→host 的 clock estimate。
- 对每个源计算在重采样器控制范围内可消除后的 host/video residual。
- relative residual 可作为诊断，但 gate 以每个源相对共同 host/video 的能力为准。
- 同时检查事件数、持续时间和最大 timestamp discontinuity。

## 验证清单

- 至少覆盖目标时长和最小事件数。
- clock ppm 必须在实现的 correction capacity 内。
- 每源 bounded residual ≤ 目标阈值。
- discontinuity 单独设门槛，不能被线性拟合掩盖。
- raw end drift 仍报告，但明确标为 diagnostic only。

## 相关

- [Bluetooth 麦克风 60 分钟时钟实验](../experiments/2026-07-17-bluetooth-microphone-clock-drift.md)

