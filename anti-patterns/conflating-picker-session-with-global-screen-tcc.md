# 反模式：把系统 Picker 会话授权当作全局录屏 TCC

## 一句话结论

`SCContentSharingPicker` 返回的 filter 只代表用户对这次选择的显式授权；即使该 filter 能交付完整帧，也不能据此把 `CGPreflightScreenCaptureAccess()` 记为已授权。

## 场景

macOS 录屏应用同时支持：

- 全屏/窗口：系统 `SCContentSharingPicker`。
- 自绘区域：应用自行构造 display filter，需要广域屏幕捕获 TCC。

## 失败表现

- 用户成功选择一次窗口后，应用把区域模式也标成“已授权”。
- 所有来源共用一个 `screenPermissionGranted` 布尔值。
- Picker 取消、Picker 启动失败和 TCC 拒绝被显示成同一种错误。
- 为了窗口录制提前请求广域 TCC，扩大授权范围并引入额外系统提醒。

## 根因

把“用户对具体内容的逐会话选择”和“应用可广域读取屏幕”的持久 TCC 权限抽象成同一种能力。两者的授权主体、触发动作、生命周期和恢复方式都不同。

## 正确做法

- 权限状态至少拆成 Picker session、screen-capture TCC、microphone 三条路径。
- Picker 配置精确限制为 `.singleDisplay` 或 `.singleWindow`，并记录 cancel/start-failure/selection。
- Picker PASS 必须同时证明：返回 style 正确、content rect/scale 合法、真实收到一帧 `.complete` 画面。
- 区域路径先 `CGPreflightScreenCaptureAccess()`，仅在用户开始区域录制时调用 `CGRequestScreenCaptureAccess()`。
- 不让 Picker 结果修改全局 TCC 状态；请求后通过新进程再次 preflight。

## 实验证据

macOS 26.4 上，同一签名 `.app` 的 display/window Picker 都在 `globalTCCBefore=false`、`globalTCCAfter=false` 时返回 filter，并各自收到完整帧。区域 TCC 仍需单独请求，设置开启后重新启动才由 preflight 观测为 true。

## 验证清单

- 每个模式声明唯一的 prompt kind。
- status-only 模式永不调用 request。
- Picker 通过不改变区域 TCC。
- 区域请求失败时不尝试构造广域捕获流。
- 证据记录请求是否实际被调用，而不只记录最终状态。

## 相关

- [macOS 26 权限模型实验](../experiments/2026-07-20-macos26-screen-capture-permission-model.md)
- [把 LaunchServices 当探针退出码](launchservices-open-as-probe-exit-oracle.md)
