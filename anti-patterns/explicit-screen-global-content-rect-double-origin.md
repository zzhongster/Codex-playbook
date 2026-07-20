# 反模式：显式屏幕窗口误用全局 `contentRect`

## 一句话结论

调用 `NSWindow(contentRect:styleMask:backing:defer:screen:)` 并显式传入 `screen` 时，`contentRect` 应使用该屏幕的本地坐标；传 `screen.frame` 会让非主屏原点被 AppKit 再加一次。

## 场景

macOS 多屏应用需要在指定显示器创建全屏覆盖窗口，例如区域选择层、坐标网格、演示遮罩或截图验证夹具。

## 失败表现

主屏完全正常，外接屏出现精确的整屏原点偏移。一个实测拓扑中：

~~~text
screen.frame = (1710, -333, 3440, 1440)
错误 window.frame = (3420, -666, 3440, 1440)
~~~

X 和 Y 原点都正好变成两倍。因为主屏原点通常是 `(0,0)`，只测主屏不会暴露问题。

## 根因

显式 `screen:` 已经告诉 AppKit 应把窗口放在哪块屏幕。此时构造器把 `contentRect` 解释为屏幕本地坐标，再转换成全局窗口坐标。若传入全局 `screen.frame`，非零原点就会被重复应用。

## 正确做法

~~~swift
let localContentRect = NSRect(
    origin: .zero,
    size: screen.frame.size
)
let window = NSWindow(
    contentRect: localContentRect,
    styleMask: .borderless,
    backing: .buffered,
    defer: false,
    screen: screen
)
~~~

必须断言最终 `window.frame == screen.frame`，而不是只断言尺寸。

## 验证清单

- 遍历每一块 `NSScreen`，不能只测 `screens.first`。
- 至少包含一个非零 X 或负 Y 原点的屏幕。
- 同时断言原点和尺寸。
- 覆盖菜单栏、状态栏、Dock 时，显式比较 window level。
- 测试完成后关闭窗口，避免夹具污染后续用例。

## 适用范围

- 适用于显式传 `screen:` 的 AppKit 窗口。
- 不适用于不传 `screen`、完全自行管理全局窗口坐标的构造路径。

## 相关

- [验证夹具 bug 冒充 API 坐标语义](fixture-bug-masquerades-as-capture-api-semantics.md)
- [macOS 区域录屏坐标空间实验](../experiments/2026-07-20-macos-region-capture-coordinate-spaces.md)

