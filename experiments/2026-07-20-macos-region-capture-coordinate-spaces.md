# 实验：macOS 区域录屏坐标空间与外接屏窗口定位

**日期**：2026-07-20  
**项目**：macOS ScreenCaptureKit 区域录屏语义探针

## 假设

需要区分两个竞争假设：

1. `SCStreamConfiguration.sourceRect` 是 display-local 点坐标。
2. `sourceRect` 需要加上 `SCDisplay.frame.origin`，成为全局点坐标。

同时验证外接屏夹具窗口是否真的位于预期位置。

## 环境与控制变量

- macOS 26.4，build 25E246。
- 内屏：AppKit `(0,0,1710,1107)`，2x，物理 `3420×2214`。
- 外屏：AppKit `(1710,-333,3440,1440)`，1x，物理 `3440×1440`。
- 外屏 SCK display frame：`(1710,0,3440,1440)`。
- 外屏 display-style filter `contentRect`：`(0,0,3440,1440)`，`pointPixelScale=1`。
- 固定全局选区：`(2630,-63,1600,900)`。
- 预期外屏本地 top-left 矩形：`(920,270,1600,900)`。
- 输出 H.264 与 PNG：`1600×900`。

## 对照

| 组 | 网格窗口构造 | `sourceRect` | 目的 |
| --- | --- | --- | --- |
| A | 全局 `screen.frame` + 显式 `screen` | 本地 `(920,270,1600,900)` | 初始模型 |
| B | 同 A | 全局 `(2630,270,1600,900)` | 测试全局 crop 假设 |
| C | 零原点本地 `contentRect` + 显式 `screen` | 本地 `(920,270,1600,900)` | 修正夹具后复测 |

## 数据

### 窗口位置

~~~text
screen.frame = (1710, -333, 3440, 1440)

传全局 contentRect:
window.frame = (3420, -666, 3440, 1440)

传零原点本地 contentRect:
window.frame = (1710, -333, 3440, 1440)
~~~

### 捕获结果

| 组 | 观测 | 结论 |
| --- | --- | --- |
| A | 先出现约 790 px 非网格内容；标记纵向偏移 +333 px | 结果可被窗口双重原点完整解释，不能用于否定本地 crop |
| B | 810 px 有效内容，随后约 790 px 黑色；纵向仍偏移 +333 px | `3440-2630=810`，说明全局 X 被当作本地 X 并在本地画布边界裁切 |
| C | 完整 `1600×900`；四个 marker 全部找到；方向正确；四边误差 `0/0/0/0` | 本地点坐标模型通过 |

修正后又在同一 2x/1x 拓扑完成 6 组全新录制：

- 6/6 `PASS_CURRENT_RUN`。
- 每组四边误差均为 0 像素。
- 报告时长范围约 3.008–3.127 秒，目标 3 秒、容差 ±250 ms。
- 严格测试 300/300 通过。
- 每个证据 bundle 的 MP4、PNG、report、log 都有独立 SHA-256。

## 结论

1. display-style filter 的 `sourceRect` 使用显示器本地、top-left、点单位坐标。
2. `width` / `height` 是编码输出物理像素，不能与 `sourceRect` 单位混用。
3. 外接屏异常来自 AppKit 夹具窗口双重应用原点，不是 SCK 要求全局 crop。
4. 主屏原点为零，无法揭露这个 bug；外接屏非零/负坐标是必要实验条件。
5. 生产坐标模型修改前，必须先独立测量 fixture `window.frame` 与 filter `contentRect`。

## 可复用发现

- 坐标实验至少同时记录：AppKit 全局 frame、实际 window frame、SCK display frame、filter contentRect、scale、sourceRect、source pixels、encoded dimensions。
- 精确偏移量是线索，但先尝试用夹具几何解释，再归因底层 API。
- 一次只改一个假设，并保留失败证据。
- 修复任何捕获配置后，用新二进制和新根完整重跑。

## 未覆盖范围

- macOS 14/15 的实机重复与权限差异。
- 外屏位于主屏左、上、下的物理拓扑。
- USB 麦克风路径。
- 其他类型的 `SCContentFilter`（窗口/应用过滤器）。

## 相关

- [显式屏幕窗口误用全局 contentRect](../anti-patterns/explicit-screen-global-content-rect-double-origin.md)
- [Retina 输出使用逻辑显示尺寸](../anti-patterns/retina-output-uses-logical-display-pixels.md)
- [验证夹具 bug 冒充 API 坐标语义](../anti-patterns/fixture-bug-masquerades-as-capture-api-semantics.md)

