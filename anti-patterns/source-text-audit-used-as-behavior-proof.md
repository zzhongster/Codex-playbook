# 反模式：用源码文本审计代替行为证明

## 一句话结论

字符串搜索可以守住“回调里不出现 Task/IO”“未引用高版本符号”等静态边界，但不能证明取消、竞态、exactly-once 和状态转换；这些必须通过可执行的生产 seam 测试。

## 场景

Swift/macOS 工程需要同时验证 realtime callback 约束、macOS 14 API floor 和录制生命周期竞态。

## 失败表现

- 测试只断言源码包含 `cancel()` 或不包含某字符串，却没有执行实际 coordinator。
- 代码重排/换行让测试误报，业务行为没有变化。
- helper 中发生阻塞操作，回调函数文本本身看起来仍安全。
- source audit 通过，但 Cmd-Q arming race 仍能触发两次 finalization。

## 根因

把静态契约、结构契约与动态协议混成一种测试方法。文本审计不知道控制流、调度和对象身份。

## 正确做法

- 文本/符号审计只用于难以运行时注入的窄边界：禁止 API、callback 禁止操作、部署符号 floor。
- 把生命周期提取为无 AppKit 依赖的生产 driver。
- 用可挂起 begin、可控 failure 和计数 finalizer 直接执行竞态。
- ownership、admission、状态机和 error propagation 用行为测试。
- source audit marker 改名时，更新审计但不能因此放宽 production contract。

## 验证清单

- 每个动态声明都能指向执行生产类型的测试。
- source audit 失败信息明确它守的是哪条静态边界。
- helper call graph 也受 callback boundary 审计。
- 不用 snapshot/字符串测试声称“竞态已关闭”。

