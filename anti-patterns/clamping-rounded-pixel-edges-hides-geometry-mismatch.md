# 反模式：无条件 clamp 像素边界来掩盖几何不一致

## 一句话结论

点坐标转物理像素时，floor/ceil 后超出显示边界不应一律 clamp；clamp 会把错误的显示描述符伪装成合法裁剪。只有可证明的浮点边界误差才能容忍。

## 场景

区域录屏把 point selection 向外对齐到整数像素，并验证 `logicalSize × scale` 与显示器 physical size 一致。

## 失败表现

一个逻辑 100×100、scale=2 的全屏选区配到错误的 199×200 物理描述。旧实现把向外对齐结果无条件 clamp，返回 199×200 crop，看起来仍合法，实际已静默少一列像素。

## 根因

把“浮点运算可能得到边界外极小 epsilon”和“上游描述符差了整整一个像素”当成同一种情况。

## 正确做法

- 先验证 display logical、scale、physical descriptor 的一致性。
- point→pixel 左/上取 floor，右/下取 ceil，保证覆盖原选区。
- 只有选择恰好位于对应显示边界，且未舍入坐标与边界差小于极小 physical-pixel tolerance 时，才允许 clamp。
- 其余任何越界 fail closed，不能替用户静默缩小选区。
- 从最终 pixel edges 反建 point `sourceRect`，让裁剪与编码范围一致。

## 验证清单

- 2x 半点、四条边、负全局坐标。
- 199×200 对 100×100@2x 必须失败，不得返回裁剪结果。
- 真正的浮点 epsilon 边界仍通过。
- 非有限 frame、零/负物理尺寸明确拒绝。

## 相关

- [Retina 输出使用逻辑显示尺寸](retina-output-uses-logical-display-pixels.md)

