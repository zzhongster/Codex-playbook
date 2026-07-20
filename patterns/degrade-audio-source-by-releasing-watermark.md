# Pattern: Degrade an audio source by releasing its watermark

## 一句话结论

多源音频混音中，来源失效不能只停止它的回调；必须从 enabled-source 集合移除它并释放其 watermark，否则健康来源最终会被缓冲上限拖死。

## 背景

实时混音器通常只渲染到所有启用来源 watermark 的最小值。这个设计能等待迟到的来源并保持对齐，但也意味着任一来源永久停止后，输出 cursor 会卡住。

## 正确降级流程

1. 失效来源通过独立 source-health channel 通知 session owner。
2. 停止该捕获服务，关闭后续 callback admission。
3. 向混音 worker 排队一个有序的 `disable(source)` 事件。
4. worker 先处理失效前已接收的 buffer，再移除该来源的 segments、watermark 和 enabled 标记。
5. 重新计算剩余来源的 render end，并立即释放之前被卡住的数据。
6. disable 事件之后到达的迟到 buffer 必须被忽略，不能升级成 mixer terminal failure。

若失效的是唯一音频源，不应把 enabled set 变为空；可以保留该来源并在 `finish(t1)` 渲染静音，或按产品策略终止整个会话。

## 常见错误

- 只把 microphone service 置空：系统声音仍在积压，直到 `maximumBufferedFrames` 触发失败。
- 直接在 callback 线程修改 mixer：破坏事件顺序和实时边界。
- disable 后把迟到 buffer 当成 `sourceDisabled` 错误：正常竞态变成全局失败。

## 验证清单

- 双来源下禁用一个来源后，另一个来源立即继续渲染。
- disable 前后的事件顺序确定。
- 迟到 buffer 不触发 terminal health。
- buffered frame 计数会扣除被移除 segments。
- 最终音频持续到统一 `t1`。

