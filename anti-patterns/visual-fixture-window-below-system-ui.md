# 反模式：视觉验证窗口层级低于系统 UI

## 一句话结论

用全屏网格验证捕获边缘时，普通 floating window 仍会被菜单栏、状态项和 Dock 遮挡；若验收要求固定像素覆盖整块显示器，夹具必须使用足够高的专用层级，并限定只用于探针。

## 场景

区域录屏探针在显示器上画边缘线和 12×12 方向色块，选区可能贴近菜单栏或 Dock。

## 失败表现

顶部选区四条边误差都是 0，但左上方向色块被白色 Apple 菜单图标覆盖，导致 orientation failure。相同尺寸、远离系统 UI 的选区通过。

## 根因

`NSWindow.Level.floating` 高于普通应用窗口，却低于 main menu/status bar。验证器错误地假设“全屏无边框”意味着像素不会被其他系统表面覆盖。

## 正确做法

- 先用真实窗口测试记录各候选 level 的数值与遮挡关系。
- 对需要覆盖菜单栏/Dock 的验证夹具使用 `screenSaver` level。
- 只提升 probe fixture，不要让产品普通窗口滥用高层级。
- 视觉测试同时关闭 cursor，避免另一类动态遮挡。
- 用顶部、底部和四角选区做实机验证。

## 验证清单

- 行为测试实例化真实 backing `NSWindow` 并断言 production level。
- top-edge 首帧能看到完整方向色块。
- 远离系统 UI 的基线仍通过。
- 失败时先区分 marker 被遮挡与 crop 几何错误。

## 相关

- [鼠标污染视觉验收夹具](cursor-contaminates-visual-validation.md)
- [验证夹具 bug 冒充 API 坐标语义](fixture-bug-masquerades-as-capture-api-semantics.md)

