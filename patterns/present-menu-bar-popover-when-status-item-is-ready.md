# Pattern: Present a menu-bar popover only after its status item is ready

## 一句话结论

macOS 菜单栏应用首次启动时，`NSStatusItem` 的 button 可能已经存在但尚未挂到 window；此时调用 `NSPopover.show` 会无报错地失效。首次展示应等待 `button.window != nil`，并进行短间隔、有上限的重试。

## 适用场景

`LSUIElement` 或 `.accessory` 应用没有 Dock 图标和主窗口，希望用户从 Finder 双击后立刻看到菜单栏控制面板。

## 失败表现

- Finder 双击后没有窗口、Dock 图标或错误提示，看起来像应用没有启动。
- 进程和状态项实际已经创建。
- 再次双击应用，或稍后手动点击状态项，popover 才能正常出现。
- `NSPopover.show(relativeTo:of:preferredEdge:)` 不抛错，也不保证此刻已经显示。

## 正确做法

1. 创建并强持有 `NSStatusItem`、`NSPopover` 和菜单栏 controller。
2. 首次展示前检查 `statusItem.button?.window != nil`。
3. 未就绪时在主 actor 上以 50 ms 左右的间隔重试，并限制总次数/总时长。
4. 调用 `show` 后检查 `popover.isShown`；仍未显示时继续剩余重试。
5. 实现 `applicationShouldHandleReopen`，让用户再次双击运行中的应用也能重新显示控制面板。
6. 仅在展示时激活应用，不改变长期的 accessory/menu-bar 生命周期。

## 为什么不能只 `Task.yield()`

一次 event-loop yield 只保证当前任务让出执行权，不保证 Control Center/status-item scene 已完成挂载。在菜单栏拥挤、状态项由系统托管或冷启动时，scene attachment 可能跨越多个循环。

## 验证清单

- 先终止旧进程，再从 Finder/Open 命令只启动一次，控制面板立即可见。
- 关闭面板但不退出，再次双击 `.app`，控制面板重新出现。
- 严格并发构建通过；重试任务保持在 main actor。
- 重试有明确上限，状态项永远无法挂载时不会形成永久定时循环。
- 用桌面截图或窗口枚举验证真实可见性，不能只用“进程存在”代替 UI 验证。
