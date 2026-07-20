# 反模式：Stop、Quit、超时和失败各自拥有收尾逻辑

## 一句话结论

一个录制会话只能有一个 finalization owner；Stop、Cmd-Q、自动时长和运行时失败都只能竞争同一次状态转换，不能各自启动 teardown。

## 场景

macOS 录屏在 arming、recording 和 finalizing 阶段同时可能收到菜单停止、Cmd-Q、定时停止、SCStream 错误或麦克风错误。

## 失败表现

- `finishWriting` 或文件 publish 被调用两次。
- 一个路径取消 writer，另一个路径仍尝试发布临时文件。
- Cmd-Q 在非 cooperative 的 `beginRecording` 挂起期间到达，begin 返回后仍安排自动停止。
- 多次退出请求导致多次 completion 或应用永不退出。

## 根因

事件处理器各自实现“如果正在录制就收尾”，检查与状态转换不是同一个原子决策；异步 suspension 会扩大竞态窗口。

## 正确做法

建立 AppKit-independent 的 session driver：

- 统一持有 arming task、自动停止任务和失败 watcher。
- 所有终止原因调用同一个 `claimFinalization(cause:)`。
- 只有第一次 phase 转换创建 finalization task。
- begin 的每个 suspension 返回后重新检查 cancellation。
- exit completion 也由同一 owner 保证 exactly once。

## 验证清单

- 十个并发 Stop/Quit 请求只触发一次 finalizer。
- 挂起 begin、发两次 Quit、恢复 begin：取消一次、无自动停止、退出一次。
- Stop/Quit/runtime failure 同时竞争：只有一个终态结果。
- 行为测试直接覆盖生产 driver，不只做源码字符串审计。

## 相关

- [运行时源失败未路由到会话所有者](runtime-source-failure-not-routed-to-session-owner.md)
- [停止截止点与事件 admission 未线性化](stop-cutoff-and-event-admission-are-not-linearized.md)

