# Pattern: Separate macOS app icons from status-item icons

## 一句话结论

macOS 应用包需要高辨识度的彩色 `.icns`，菜单栏状态项则需要自动适配明暗模式的单色 template image；不要让两者共用同一张位图，也不要依赖系统的空白默认图标。

## 为什么

- 缺少 `CFBundleIconFile` 时，Finder 可能显示通用白色应用图标，用户会误以为应用未完成或没有启动。
- 彩色 AppIcon 缩到菜单栏尺寸后通常细节丢失，且无法自动适配浅色/深色菜单栏。
- template image 会由 AppKit 自动着色，但不适合作为 Finder/Dock 中的品牌图标。

## 推荐结构

1. 在仓库保留一张至少 1024×1024、带透明圆角的 canonical AppIcon PNG。
2. 构建时生成 16、32、64、128、256、512、1024 像素的标准 `.iconset` 文件。
3. 用 `iconutil -c icns` 生成 `Contents/Resources/AppIcon.icns`。
4. 在 Info.plist 设置 `CFBundleIconFile = AppIcon.icns`，再进行 codesign。
5. 菜栏状态项使用清晰的单色 SF Symbol 或专用 template PNG，并设置 `isTemplate = true`。
6. 空闲时只显示图标；录制/暂停时再追加等宽计时文本，避免重复符号和宽度抖动。

## 验证清单

- 从最终 `.icns` 反解 1024 PNG，检查 alpha、清晰度和圆角边缘。
- `plutil` 确认最终 app bundle 包含 `CFBundleIconFile`。
- `codesign --verify --deep --strict` 通过。
- 用 Finder `open -R` 查看最终 `.app`，不能只检查源 PNG。
- 在浅色和深色菜单栏下确认 template icon 均可见。
- 16 px 下仍能识别核心轮廓，不依赖文字或细线。
