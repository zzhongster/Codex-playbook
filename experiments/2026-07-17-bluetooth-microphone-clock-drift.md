# 实验：Bluetooth 麦克风与系统音频的 60 分钟时钟漂移

**日期**：2026-07-17  
**项目**：macOS 录屏音频漂移 P0 spike

## 假设

EDIFIER W830NB Bluetooth 麦克风和 ScreenCaptureKit 系统音频的真实 timestamp，在连续一小时内都落入 ±1,000 ppm 校正能力，且相对共同 host/video timeline 的 bounded residual 不超过 100 ms。

## 环境与控制变量

- 麦克风：EDIFIER W830NB，Bluetooth，作为系统默认输入。
- 系统声音：ScreenCaptureKit audio stream。
- 最低有效时长：每源 3,590 秒。
- 最低事件数：每源 21。
- 时钟能力：±1,000 ppm。
- residual 门槛：每源 ≤100 ms。
- timestamp discontinuity 门槛：≤250 ms。

## 数据

| 指标 | 系统音频 | 麦克风 |
| --- | ---: | ---: |
| Trace duration | 3605.180 s | 3605.400 s |
| Clock estimate | -0.000 ppm | 0.000 ppm |
| Bounded host/video residual | 0.000 ms | 0.000 ms |
| 最大 timestamp discontinuity | 0.000 ms | 0.000 ms |
| 事件数 | 180,259 | 12,018 |

补充观测：

- 原始相对端点差：220.000 ms。
- 相对时钟估计：0.000 ppm。
- 相对 bounded residual：0.000 ms，仅作为诊断。
- Host/video gate：PASS。

## 结论

本设备、本次系统和本次一小时 trace 中，两条源时间戳连续且位于重采样器的 ±1,000 ppm 容量内。220 ms 原始端点差主要反映回调 block cadence 与停止边界，不能单独判为时钟漂移失败。

## 后续集成发现

真实 16 kHz Bluetooth callback 还揭露了另一个问题：若先按 callback 独立转到 48 kHz，再进入时间戳纠漂器，会重复转换并最终超过 correction limit。修正为“原生采样率 downmix + 单一时间戳重采样”后，三次连续 10 秒全屏录制均成功；最大 A/V endpoint delta 为 0.437 ms。

## 可复用发现

- trace gate 应比较每源相对共同 host/video timeline 的 clock slope 和 residual。
- raw end drift 要保留用于诊断，但不是唯一验收指标。
- 硬件 trace 与生成可播放成片是两层不同证据，两者都需要。
- 单一设备 PASS 不能外推到 USB、其他 Bluetooth codec 或其他 macOS 版本。

## 未覆盖范围

- USB 麦克风。
- 其他 Bluetooth 型号与输入 codec。
- 录制中断连、默认设备切换或 sample-rate change。
- macOS 14/15 重复验证。

## 相关

- [原始端点差作为同步 gate](../anti-patterns/raw-end-drift-as-audio-sync-gate.md)
- [时间戳校正前双重重采样](../anti-patterns/double-resampling-before-timestamp-correction.md)
- [有界时间戳重采样实验](2026-07-17-bounded-timestamp-resampler.md)

