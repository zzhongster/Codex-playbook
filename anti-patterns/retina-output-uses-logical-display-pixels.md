# 反模式：Retina 输出使用逻辑显示尺寸

## 一句话结论

屏幕选区用点坐标，编码输出用物理像素；不要用逻辑宽高或兼容性显示尺寸 API 代替当前显示模式的 `pixelWidth` / `pixelHeight`。

## 场景

macOS 屏幕录制需要把 AppKit 选区映射为 ScreenCaptureKit `sourceRect`，再设置编码 `width` / `height`。

## 失败表现

- 2x Retina 上录制输出只有预期一半分辨率。
- 选区位置正确，但文字明显发虚。
- 单元测试用 1x 外屏都通过，内屏实录才暴露问题。

## 根因

三种量被混为一谈：

| 量 | 单位 | 用途 |
| --- | --- | --- |
| `NSScreen.frame` / 选区 | point | AppKit 全局布局 |
| `SCStreamConfiguration.sourceRect` | point | 显示器本地裁剪 |
| 当前 `CGDisplayMode.pixelWidth/pixelHeight` | physical pixel | 源像素与编码尺寸 |

在缩放模式下，逻辑点、模式逻辑宽高和实际 backing 像素并不等价。

## 正确做法

1. 使用 `CGDisplayCopyDisplayMode(displayID)` 获取当前激活模式。
2. 使用 `mode.pixelWidth` / `mode.pixelHeight`。
3. 验证 `logicalSize × backingScale` 与物理像素在容差内一致，不一致则 fail closed。
4. `sourceRect` 保持点单位；只把对齐后的源范围和输出尺寸表示为整数物理像素。
5. 用 2x 内屏和 1x 外屏分别实测。

## 验证清单

- 代码中禁止退回 `CGDisplayPixelsWide/High` 或 `mode.width/height`。
- 测试同时断言 `sourceRect` 与 `sourcePixelRect`。
- 2x 用例包含半点坐标和向外像素对齐。
- 编码尺寸与首帧 PNG 尺寸一致。

## 相关

- [macOS 区域录屏坐标空间实验](../experiments/2026-07-20-macos-region-capture-coordinate-spaces.md)

