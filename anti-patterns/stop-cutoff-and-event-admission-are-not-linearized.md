# 反模式：停止截止点与事件 admission 未线性化

## 一句话结论

`t1` 不只是一个时间值，也是事件接纳边界；设置 worker cutoff 与关闭 callback/monitor admission 必须形成同一个可证明的线性化点，否则“正在路上”的事件会随机越界。

## 场景

麦克风 worker、设备监听器和定时轮询并发运行。正常 Stop 要接受所有 `t1` 之前已接纳的数据和失败，同时忽略 teardown 触发的晚到配置变化。

## 失败表现

- 先给 worker 设置 `t1`，稍后才关闭 admission；夹在中间的 callback 被接受，却到达一个已经停止的 worker。
- 先关闭 callback，又丢掉了边界前已接纳、但尚未 drain 的真实失败。
- 停止成功与失败取决于调度时序，测试偶发。

## 根因

“设置截止点”和“还能不能提交事件”由不同锁、actor 或队列控制，没有共同的 happens-before 关系。

## 正确做法

- 用一个很短的 admission 临界区拥有 `accepting` 与 cutoff 安装。
- 正常 Stop 在同一临界区把 `accepting=false` 并提交 worker `t1`。
- 回调提交使用非阻塞 `tryLock`；抢不到或 admission 已关时立即拒绝，不能阻塞实时线程。
- 临界区后 drain 所有边界前已接受事件，再拆监听器、timer 和 engine。
- 会话级 health admission 也在异步 finalization 之前关闭。

## 验证清单

- 用测试 seam 精确挂起在旧的“worker cutoff 已设、admission 尚未关”间隙。
- 间隙内 submit 必须立即拒绝且 Stop 成功。
- 边界前已接受的失败必须 drain 并使 Stop fail closed。
- 所有 late monitor callback 都不能改写终态。

## 适用范围

适用于日志 flush、网络 shutdown、传感器停采等“截止点 + 并发事件队列”协议。

