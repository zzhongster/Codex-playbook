# 反模式：把很短的墙钟 deadline 当并行测试正确性判据

## 一句话结论

并行测试中的 50 ms 墙钟超时容易测到机器负载而非协议正确性；并发状态机应优先用可控 gate、虚拟时钟或事件顺序断言，真实 timeout 只保留宽松集成测试。

## 场景

异步 cancellation/readiness 测试在完整 Swift 测试套件并行运行时，要求某任务 50 ms 内完成。

## 失败表现

- 单独运行稳定通过，并行压力下偶发超时。
- gate 逻辑没有变化，换一台机器或首次冷编译就失败。
- 团队通过不断放大 sleep 来“修复”，测试仍然慢且不确定。

## 根因

测试把调度延迟、CPU 竞争和 CI 抖动纳入业务判据。短墙钟只能证明当前运行环境足够快，不能证明 cancellation 的 happens-before。

## 正确做法

- 注入可暂停/恢复的 begin、finish 或 callback seam。
- 用 one-shot gate 精确控制交错顺序。
- 断言 transition count、finalizer count、event admission 和 completion count。
- 涉及严格顺序的套件使用 `--no-parallel`。
- 仅在死锁看门狗层保留较宽松真实 timeout，失败信息区分 scheduler delay 与业务状态。

## 验证清单

- 同一用例在高并发负载下仍由事件条件结束。
- 不依赖 `sleep(0.05)` 来制造竞态。
- timeout 是测试保险丝，不是主要 PASS 条件。
- 单测与集成测试的时限职责分开。

