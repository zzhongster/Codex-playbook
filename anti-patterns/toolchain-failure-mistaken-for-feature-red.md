# 反模式：把测试工具链故障当成 TDD 的 RED

## 一句话结论

TDD 的 RED 必须由缺失或错误的业务行为触发；测试框架无法链接、fixture 编译失败或环境缺 SDK 只说明 harness 坏了，不能证明测试约束了新功能。

## 场景

SwiftPM 在只有 Command Line Tools 的机器上运行 Swift Testing，测试框架可能需要显式 framework/linker 路径。

## 失败表现

- `swift test` 在测试目标前就因 `Testing` symbol unresolved 退出，仍被记录为“预期 RED”。
- fixture 的 access control 或生成媒体 helper 错误掩盖真正缺失的 production symbol。
- 修复工具链后测试直接 GREEN，说明从未观察到业务 RED。
- 一条 missing type 产生大量 contextual member cascade，被误当成多个独立失败。

## 根因

只看 exit code 非零，不检查第一个根诊断和编译阶段。

## 正确做法

1. 先让现有测试在同一严格命令下通过，证明 harness 可用。
2. 添加最小新测试。
3. 修复测试自身的语法、fixture 和工具链问题，直到失败落在缺失/错误 production contract。
4. 记录第一条业务根错误；把后续 cascade 标为派生诊断。
5. GREEN 使用完全相同的 strict flags、framework 路径和并行策略。

## 验证清单

- RED 日志能指出具体缺失 symbol、错误值或未抛异常。
- 基线测试在同一环境先通过。
- 没把网络、签名、权限或 toolchain failure 当 feature RED。
- 最终文档同时记录 focused 与 full-suite GREEN。

