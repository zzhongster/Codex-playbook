# 反模式：共享 readiness 强制等待无关信号

## 一句话结论

共享采集服务可以暴露完整状态，但每个工作流必须使用自己的能力特定就绪条件；视频验证不能因为没有音频回调而拒绝开始。

## 场景

一个 ScreenCaptureKit 服务同时提供视频和系统音频。正式录屏要求音视频都就绪，但区域裁剪探针只验视频像素，音频内容不是 PASS 条件。

## 失败表现

视频帧已稳定到达，探针仍等待五秒后报 readiness timeout。原因不是视频失败，而是静音或不可用音频路径没有产生样本。

## 根因

所有调用者共用一个过强的布尔值：

~~~swift
isReady = hasCompleteVideoFrame
    && hasValidSystemAudio
    && !hasFailed
~~~

这个条件对正式音视频录制合理，却把区域视频验证与无关音频信号耦合。

## 正确做法

保留完整就绪语义，同时增加明确的能力谓词：

~~~swift
var isVideoReady: Bool {
    hasCompleteVideoFrame && !hasFailed
}

var isReady: Bool {
    isVideoReady && hasValidSystemAudio
}
~~~

- 正式全屏录制继续使用 `isReady`。
- 区域视频探针使用 `isVideoReady`。
- 捕获健康、worker 失败、mixer 失败仍然 fail closed。
- 不要为了绕过 readiness 而删除音频 writer 或收尾链路。

## 验证清单

- “有视频、无音频、无失败”时视频就绪为真、完整就绪为假。
- “有视频但失败”时两者都为假。
- 每个调用点明确选择谓词，不依赖默认猜测。
- 错误消息只描述该工作流真正等待的信号。
- 整分支复审确认其他调用者没有被弱化。

## 适用范围

适用于摄像头/麦克风、主数据/缓存、网络/本地降级等多能力共享服务。

