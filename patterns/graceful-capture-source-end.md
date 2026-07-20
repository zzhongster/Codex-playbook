# Pattern: Treat expected source end separately from capture failure

## 一句话结论

窗口关闭是一个可收尾的 source-end 事件，不等同于编码器或捕获管线损坏；应冻结最后完整帧并走正常 `t1` 收尾，而不是把 worker 标记为 terminal failure。

## 适用场景

独立窗口录制时，窗口可能在录制中被关闭。ScreenCaptureKit 会停止 stream，但已经写入的帧和音频仍可能完全有效。

## 状态处理

- prewarm/倒计时中关闭：取消启动，不发布空录制。
- recording/paused/resuming 中关闭：会话所有者发起一次正常 Stop。
- stream 已自行停止时，teardown 不再调用或强求 `stopCapture()` 成功。
- output end 使用 stream clock 的 source-end 时刻；视频轨由最后完整帧补到终点。
- 非窗口来源的意外 stream stop 仍然是 terminal failure。

## 实现约束

源结束 callback 仍只能做有界、非阻塞提交；正常收尾必须由 session owner 执行。`sourceEnded` 标志要与 callback removal/stopCapture 的判断在同一锁下读取，避免把“已经停止”误判为 teardown failure。

## 验证清单

- 窗口关闭后文件被正常发布，而不是只留下临时文件。
- 倒计时期间关闭窗口不会开始冻结画面录制。
- stream 自行结束后不要求第二次 stopCapture 成功。
- display/region 的意外 stream stop 仍触发 terminal health。

