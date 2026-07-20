# 反模式：在时间戳校正前先做一次独立重采样

## 一句话结论

独立设备音频若需要按时间戳纠漂，采样率转换和漂移校正应由同一个时间戳对齐重采样器完成；先用 `AVAudioConverter` 转到目标采样率，再按原始时间戳纠漂，会重复解释同一段速率差。

## 场景

macOS 录屏把 16 kHz Bluetooth 麦克风混入 48 kHz 系统音频。每个麦克风回调都带设备采样率和 host time，最终输出使用统一的 48 kHz RecordingClock。

## 失败表现

首轮 Bluetooth 实录中，每个 16 kHz 回调先被转换为 48 kHz。`AVAudioConverter` 产生的中间块长度并不总与源回调时间跨度严格对应；这些块再次进入时间戳对齐重采样器后，误差额度持续消耗，最终触发 `correctionLimitExceeded`。

## 根因

两级转换同时在补偿速率：

~~~text
device PCM + device timestamp
  -> 独立 16k→48k 转换
  -> 仍按源 timestamp 对齐并纠漂
  -> 同一速率差被处理两次
~~~

中间块的整数帧舍入和转换器内部状态还会制造新的边界不连续。

## 正确做法

- 回调后只做不改变时间轴的工作，例如声道 downmix。
- 保留设备原生采样率、原生帧数和原始时间戳。
- 让一个有界、时间戳对齐的重采样器同时完成 rate conversion 与 drift correction。
- 把允许校正范围、最大输入缓冲和不可补偿条件写成显式契约。

## 验证清单

- 以 16 kHz、44.1 kHz、48 kHz 原生输入分别回归。
- 合成 ±1,000 ppm、60 分钟输入，检查输出帧数、音高、RMS 和内存上界。
- 实机至少连续录制三次，确认没有 correction limit、handoff rejection 或非静音失败。
- 源码边界测试确认进入重采样器前没有第二个采样率转换器。

## 相关

- [有界时间戳重采样实验](../experiments/2026-07-17-bounded-timestamp-resampler.md)
- [Bluetooth 麦克风 60 分钟时钟实验](../experiments/2026-07-17-bluetooth-microphone-clock-drift.md)

