# 反模式：运行时源失败没有路由到会话所有者

## 一句话结论

捕获、混音器和 writer 等终止性 post-`t0` 失败必须进入一次性 session-health 通道；允许降级的来源也必须路由到会话所有者，但要使用独立 source-health 通道，由会话策略决定降级还是终止。

## 场景

录屏开始后，SCStream 可能意外停止，输入设备可能变化，混音可能失败，AVAssetWriter append 也可能返回 false。

## 失败表现

- UI 计时仍继续，但某条媒体轨已经不再产生数据。
- 最终 MP4 被正常命名和发布，却缺音频、结尾或后半段画面。
- 各组件都有错误日志，但 coordinator 不知道会话已经不可信。
- 多个错误同时发生，最终提示随机被最后一个错误覆盖。

## 根因

组件健康状态被局部封装，没有会话级失败语义；或失败通道是无界、多值的，无法定义第一个真正破坏会话的原因。

## 正确做法

- 向 writer、mixer、screen 注入同一个 terminal one-shot health channel。
- 对产品允许降级的来源（例如有系统声音兜底的麦克风）注入独立 source-health channel；会话所有者收到后关闭该来源、解除混音 watermark，并向用户显示非模态警告。
- 如果唯一音频来源失败，可让混音器在收尾时补静音到 `t1`；如果产品不允许无声继续，则把该 source-health 提升为 terminal failure。
- 只接受并保存第一个运行时失败。
- 会话正式 admission 后立刻启动 watcher；`t0` 边界期间已缓冲的失败也会马上被看见。
- P0 策略明确 fail closed：取消并保留临时文件，不发布 partial output。
- 正常 `t1` 开始时关闭失败 admission，避免 teardown 噪声篡改成功停止。

## 验证清单

- 分别注入 stream stop、设备变化、mixer failure、video/audio append failure。
- 同时覆盖“麦克风是唯一音频源”和“麦克风 + 系统声音”两种降级路径。
- 每个用例只产生一次 session finalization。
- 失败会话不执行原子 publish。
- cancellation 与真正 runtime failure 保持不同错误类型。
- 并发失败测试确认 first-wins 语义。

## 相关

- [多重录制收尾所有者](multiple-recording-finalization-owners.md)
- [停止截止点与事件 admission 未线性化](stop-cutoff-and-event-admission-are-not-linearized.md)
