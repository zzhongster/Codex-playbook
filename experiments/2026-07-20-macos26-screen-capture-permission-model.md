# 实验：macOS 26 Picker、区域 TCC 与麦克风权限分叉

**日期**：2026-07-20  
**项目**：macOS ScreenCaptureKit 录屏权限探针

## 假设

1. `SCContentSharingPicker` 的逐会话授权不要求全局屏幕录制 TCC。
2. 自绘区域路径需要 `CGPreflightScreenCaptureAccess` / `CGRequestScreenCaptureAccess`，首次设置后可能要重启。
3. 麦克风只应在状态为 `notDetermined` 且用户执行录制动作时请求。

## 环境与控制

- macOS 26.4，build `25E246`。
- 同一 ad-hoc-signed `.app`，bundle ID `com.zzhongster.PermissionModelProbe`。
- 最低系统 macOS 14.0，SDK 26.2，arm64。
- `Info.plist` 仅含真实的 `NSMicrophoneUsageDescription`，不含屏幕/系统音频用途字符串。
- 所有正式矩阵经 LaunchServices 启动；每次只执行一个 mode 并原子发布一个 JSON。

## 结果

| 模式 | 请求前 | 动作与结果 |
| --- | --- | --- |
| display Picker | global TCC false | 选择 display；TCC 仍 false；收到完整帧；PASS |
| window Picker | global TCC false | 选择 window；TCC 仍 false；收到完整帧；PASS |
| region preflight | TCC false | 未调用 request；保持 false |
| region first request | TCC false | request 被调用并返回 false；未尝试取帧 |
| region relaunch | TCC true | 跳过 request；0.336 秒收到完整帧；PASS |
| microphone status | notDetermined | 未调用 request；保持 notDetermined |
| microphone first request | notDetermined | request 被调用并 granted；变 authorized；PASS |
| microphone rerun | authorized | 跳过 request；保持 authorized；PASS |

## 额外发现

直接执行 `Contents/MacOS/PermissionModelProbe` 与通过 LaunchServices 启动 `.app`，在同一主机上观测到了不同的初始 TCC/麦克风状态。直接启动的诊断结果不得混入正式权限矩阵；`open -W` 的 launcher exit 也不能代表探针结论，正式 verdict 必须来自应用原子发布的报告。

报告 writer 的首轮实机运行还揭露了默认 ISO-8601 日期策略丢失亚秒精度的问题。writer 正确失败关闭，未发布半可信结果；加入亚秒与 timeout 报告测试后，改用 Foundation reference-date 秒的精确 decimal string。

## 结论

- Picker session、全局 screen-capture TCC、microphone 必须是三个独立状态机。
- Picker 能收到真实帧也不能推导全局 TCC。
- 区域 TCC 在本机首次开启后需要应用重新启动才能由 preflight 观测为 true。
- 已授权的 request-mode 必须跳过系统 request，避免重复弹窗。
- 权限矩阵必须固定启动方式、签名二进制、bundle ID 和账户状态。

## 有界性

结论仅为 `PASS_MACOS_26_CURRENT_ACCOUNT`。macOS 14/15、显式拒绝后恢复、周期性重新确认、系统文案和第二个干净账户仍未覆盖；不能据此宣布三代系统总门 PASS。

## 相关

- [Picker 会话授权与全局 TCC 混淆](../anti-patterns/conflating-picker-session-with-global-screen-tcc.md)
- [LaunchServices 退出码误用](../anti-patterns/launchservices-open-as-probe-exit-oracle.md)
- [默认 ISO-8601 精确往返误用](../anti-patterns/stock-iso8601-date-coding-used-for-exact-evidence-roundtrip.md)
