# 反模式：用“收到过回调”判定采集源就绪

## 一句话结论

源 readiness 必须证明当前启动尝试产生了 schema 合法且成功写入的事件；仅看到 callback、engine running 或 first buffer 都可能是假就绪。

## 场景

音频漂移探针在正式计时前等待系统音频和麦克风可用，麦克风启动失败时允许重建 engine 后再试一次。

## 失败表现

- callback 到达但 host time 无效、frames 为零或 sample rate 非有限，仍被算作 ready。
- trace writer 已失败，启动流程却因为 callback count 增长而继续。
- 第一次启动尝试留下的 callback 与第二次尝试的新 callback 合并，伪造“稳定两个 buffer”。
- engine 报 running，但有效事件从未进入持久 trace。

## 根因

readiness 测量的是 API 活动，不是工作流所需的有效进展；重试还共用了跨 attempt 的计数或 gate。

## 正确做法

- 每次 start attempt 拥有独立 readiness gate 和计数。
- callback 先验证 host time、帧数、sample rate 和 presentation time schema。
- 要求同一次 attempt 内连续有效 callback，且 engine 仍 running。
- enable recording 后，以当前 successfully-written event count 为 baseline。
- 只有 writer 确认新有效事件后才报告 source ready。
- 运行中 watchdog 监控“最后成功写入进展”，而不是最后任意 callback。

## 验证清单

- invalid callback 不 signal readiness。
- write failure 使 startup 失败而不是 ready。
- attempt 1 的一个 callback 与 attempt 2 的一个 callback不能合成阈值。
- ready 后若有效写入停滞超过阈值，进入 session health failure。

## 相关

- [共享 readiness 强制等待无关信号](shared-readiness-gate-requires-irrelevant-signal.md)
- [运行时源失败未路由到会话所有者](runtime-source-failure-not-routed-to-session-owner.md)

