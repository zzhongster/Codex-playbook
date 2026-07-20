# 反模式：把设备路由策略等同于设备身份监控

## 一句话结论

是否显式 pin 音频设备与是否监控设备身份是两个独立问题；即使 Bluetooth 走系统管理路由，也必须监听并轮询默认输入的 ID/UID，防止录制中静默换设备。

## 场景

内建麦克风可通过 CoreAudio audio unit 显式 pin；Bluetooth 由系统管理更稳，但产品语义要求“锁定开始录制时的默认输入”。

## 失败表现

- 代码只给 `.explicitPin` 安装 listener，Bluetooth 默认输入变化后录制继续，却已经换成另一支麦克风。
- 只监听 property change，监听安装与第一次事件之间的竞态未覆盖。
- 某些系统变化漏事件，长录制中身份悄悄改变。
- 同一变化被 listener 和 poll 同时报两次，最终错误不稳定。

## 根因

把 transport-specific routing mechanism 和 product-level identity invariant 合并成一个布尔开关。

## 正确做法

- routing mode 只决定是否显式 pin。
- 所有模式都创建初始 ID/UID identity lock。
- 安装默认输入 property listener 后立刻重新验证一次。
- 再用低频轮询兜底，例如 500 ms 检查 ID/UID。
- identity lock 只报告第一次变化并 fail closed。
- 被锁设备的 configuration change 与“默认设备切走”分别建模。

## 验证清单

- built-in explicit pin 与 Bluetooth system-managed 都要求 identity monitoring。
- 覆盖 listener 安装竞态和 poll 检出路径。
- listener+poll 同一变化只产生一个 session failure。
- 正常 Stop 后的晚回调不能改写成功结果。

## 相关

- [停止截止点与事件 admission 未线性化](stop-cutoff-and-event-admission-are-not-linearized.md)

