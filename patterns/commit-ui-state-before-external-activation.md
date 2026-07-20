# Pattern: Commit UI state before activating external applications

## 一句话结论

在 `@MainActor` 成功路径中，先一次性提交最终 model/state-machine 状态，再异步执行 Finder、浏览器或其他应用的激活动作；同步外部激活可能重入 AppKit 主循环，让 SwiftUI 渲染到半完成状态并丢失后续更新。

## 典型失败

录屏应用完成原子发布后依次执行：

1. 设置 `lastOutputURL`；
2. 同步调用 `NSWorkspace.activateFileViewerSelecting`；
3. 把 phase 从 `finalizing` 改成 `idle`。

Finder 激活在第 2 步触发主循环重入，SwiftUI 先渲染出“正在保存 + Finder 链接”。随后 phase 变化发生在 view update 期间，可能伴随 `Publishing changes from within view updates is not allowed`，最终界面永久停留在“正在保存”，尽管文件和底层资源都已完成。

## 正确顺序

1. 保存执行外部副作用所需的值，例如 `shouldReveal` 和最终 URL。
2. 完成状态机的 success transition。
3. 设置所有最终展示状态，例如 `phase = idle`、`lastOutputURL = finalURL`。
4. 完成会话清理和 termination reply。
5. 用新的 main-actor task/下一轮调度执行 Finder reveal 等外部激活。

## 设计原则

- 原子 publish 是不可逆的 success commit；其后不应再让展示副作用决定业务成功或失败。
- 外部应用激活属于 presentation side effect，不属于 finalization correctness。
- 在任意可能重入主循环的调用之前，当前界面状态必须已经自洽。
- 不要用“进程空闲”判断 UI 正确；同时核对文件、资源清理日志和真实界面。

## 验证清单

- 成功路径源码/单测明确约束：idle state 与最终 URL 均早于外部激活。
- 完成录制后界面立即恢复为可开始下一次录制的状态。
- Finder reveal 开关关闭和开启两条路径都通过。
- 最终文件只发布一次，Finder 失败不回滚或改写录制结果。
- 运行日志没有新的 SwiftUI view-update publication 警告。
