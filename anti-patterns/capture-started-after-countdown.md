# 反模式：倒计时结束后才启动采集

## 一句话结论

倒计时结束时才启动 ScreenCaptureKit 和 AVAudioEngine，会吃掉第一帧和第一句话；应在倒计时期间 prewarm，确定统一 `t0` 后丢弃或裁剪所有 pre-`t0` 样本。

## 场景

用户点击录制后看到 3–2–1，倒计时结束即开始演示或说话。

## 失败表现

- 文件开头数百毫秒没有画面或声音。
- 视频先到、麦克风后到，或反之。
- 为等所有源 ready，又在“1”消失后增加不可预测延迟。

## 根因

把 UI 倒计时结束和异步硬件/系统采集启动完成当成同一瞬间。SCK stream、content picker 和 audio engine 都可能有可见启动延迟。

## 正确做法

- 倒计时期间启动采集并等待能力特定 readiness。
- 倒计时窗口在 `t0` 前隐藏，避免录进成片。
- 用采集同步时钟定义共享 `t0`。
- 视频拒绝 pre-`t0` 帧；跨 `t0` 音频 buffer 精确裁剪。
- 只有 `t0` video frame 成功被 writer 接受后，才释放预热期间缓存的 crossing audio。
- 任一源 prewarm 失败则不进入 recording。

## 验证清单

- begin 被人工挂起时取消录制，不得在恢复后偷偷进入 recording。
- 第一个音频/视频样本 PTS 都为 0。
- crossing audio 在 t0 video append 成功前保持缓冲。
- 录制三次实机检查开头非静音且首帧可解码。

## 相关

- [跨 t0 音频在视频原点确认前写入](pre-t0-audio-released-before-video-origin.md)

