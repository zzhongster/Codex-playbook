# Codex Playbook

经过实战验证、带证据、可复用的 Codex 工程经验。

这里不收集命令大全。每篇文档都回答一个更具体的问题：什么做法会失败、为什么失败、如何验证修复、结论能推广到哪里。

## 内容结构

~~~text
Codex-playbook/
├── patterns/          # 至少在两个项目验证过的工程模式
├── anti-patterns/     # 有具体踩坑经历和替代方案的反模式
├── experiments/       # 有对照组、数据和结论的实验
└── CONTRIBUTING.md
~~~

## Anti-patterns

### 坐标、显示与视觉验证

| 文档 | 一句话结论 |
| --- | --- |
| [显式屏幕窗口误用全局 contentRect](anti-patterns/explicit-screen-global-content-rect-double-origin.md) | `NSWindow(contentRect:..., screen:)` 的 `contentRect` 是屏幕本地坐标；再传 `screen.frame` 会把非主屏原点加两次 |
| [验证夹具 bug 冒充 API 坐标语义](anti-patterns/fixture-bug-masquerades-as-capture-api-semantics.md) | 实机证据异常时先独立验证夹具位置，不能直接重写生产坐标模型 |
| [Retina 输出使用逻辑像素 API](anti-patterns/retina-output-uses-logical-display-pixels.md) | 输出尺寸必须取当前显示模式的物理像素，不能把逻辑点或缩放后的兼容 API 当物理像素 |
| [无条件 clamp 像素边界](anti-patterns/clamping-rounded-pixel-edges-hides-geometry-mismatch.md) | 只容忍可证明的浮点边界误差，不能把描述符错误静默裁掉 |
| [鼠标污染视觉验收夹具](anti-patterns/cursor-contaminates-visual-validation.md) | 固定色块/角标验收应关闭鼠标渲染或显式遮罩鼠标区域 |
| [视觉夹具低于系统 UI](anti-patterns/visual-fixture-window-below-system-ui.md) | 全屏像素夹具要覆盖菜单栏/Dock，并限制高层级只用于探针 |

### 时间轴、音频与采集边界

| 文档 | 一句话结论 |
| --- | --- |
| [时间戳校正前双重重采样](anti-patterns/double-resampling-before-timestamp-correction.md) | 采样率转换与漂移校正应由一个时间戳对齐重采样器完成 |
| [用浮点增量累积媒体时间轴](anti-patterns/floating-point-media-timeline-accumulation.md) | 长时媒体时间应由绝对 host time 映射到固定有理 timescale |
| [实时回调的借用媒体逃逸](anti-patterns/realtime-callback-escapes-borrowed-media.md) | 回调内先取得 ownership，再做有界、非阻塞 handoff |
| [用回调计数判定源就绪](anti-patterns/callback-count-used-as-source-readiness.md) | ready 要证明当前 attempt 产生了 schema 合法且成功写入的事件 |
| [倒计时结束后才启动采集](anti-patterns/capture-started-after-countdown.md) | 倒计时期间 prewarm，统一 `t0` 后裁掉 pre-roll |
| [跨 t0 音频过早写入](anti-patterns/pre-t0-audio-released-before-video-origin.md) | crossing audio 要等 t0 视频帧成功 admission 后才能释放 |
| [原始端点差作为同步 gate](anti-patterns/raw-end-drift-as-audio-sync-gate.md) | callback 端点差不能替代每源相对 host/video 的时钟 residual |
| [共享 readiness 强制等待无关信号](anti-patterns/shared-readiness-gate-requires-irrelevant-signal.md) | 不同工作流必须使用能力特定的就绪条件 |
| [路由策略等同设备身份监控](anti-patterns/device-routing-confused-with-device-identity-monitoring.md) | 是否 pin 与是否监控 ID/UID 是两个独立问题 |

### 生命周期、writer 与文件发布

| 文档 | 一句话结论 |
| --- | --- |
| [多重录制收尾所有者](anti-patterns/multiple-recording-finalization-owners.md) | Stop、Quit、超时和失败必须竞争同一个 finalization owner |
| [运行时失败未路由到会话所有者](anti-patterns/runtime-source-failure-not-routed-to-session-owner.md) | 所有媒体组件向一个 first-wins session-health 通道报告失败 |
| [停止截止点与 admission 未线性化](anti-patterns/stop-cutoff-and-event-admission-are-not-linearized.md) | 设置 `t1` 和关闭事件接纳必须形成一个线性化边界 |
| [append 失败后 writer 继续存活](anti-patterns/media-writer-append-failure-left-nonterminal.md) | append false 是终态，不是普通 backpressure |
| [变化驱动视频不补合法尾帧](anti-patterns/variable-rate-video-finish-without-tail-frame.md) | 静止结尾要按帧率下界延伸最后完整帧且避免重复 PTS |
| [rename 未固定文件身份](anti-patterns/atomic-rename-without-pinned-file-identity.md) | 原子名称切换之外，还要防目录、临时文件和目标 inode 被替换 |
| [错误脱敏抹掉操作诊断](anti-patterns/error-redaction-destroys-operational-diagnostics.md) | 只删除敏感值，保留 operation、status、domain/code |

### 测试与证据工程

| 文档 | 一句话结论 |
| --- | --- |
| [用 plutil -lint 验证 JSON](anti-patterns/plutil-lint-for-json.md) | `plutil -p` 能读 JSON 不代表 `plutil -lint` 是 JSON lint；JSON 应使用 `jq empty` |
| [忽略大证据却不提交清单](anti-patterns/ignored-evidence-without-durable-manifest.md) | 二进制证据不进 Git 时，至少提交每个文件的哈希、代码身份和保留限制 |
| [验证后改代码却不重新取证](anti-patterns/post-validation-code-change-without-revalidation.md) | 任何影响运行时配置的后续修复都会让旧实机证据与最终代码脱节 |
| [重试掉第一份实机失败证据](anti-patterns/retrying-away-first-live-failure.md) | 实机验收必须全新根目录、失败即停、保留第一次失败，禁止“重试到绿” |
| [短墙钟 deadline 作为并行测试判据](anti-patterns/wall-clock-deadline-as-parallel-test-oracle.md) | 用可控事件顺序证明协议，短 timeout 只会测到机器负载 |
| [构造器校验但 Decoder 绕过](anti-patterns/validated-initializer-with-unvalidated-decoder.md) | 序列化模型的 direct init 与 decode 必须共享同一 invariant |
| [把 open -W 当探针退出码](anti-patterns/launchservices-open-as-probe-exit-oracle.md) | LaunchServices 启动成功不等于目标 executable 的退出状态 |
| [源码文本审计代替行为证明](anti-patterns/source-text-audit-used-as-behavior-proof.md) | 静态审计守窄边界，竞态与状态机必须执行生产 seam |
| [未约束标签插入 verdict 报告](anti-patterns/untrusted-label-in-human-readable-verdict.md) | 结构化字段决定 gate，自由文本不能伪造 PASS 行 |
| [工具链故障冒充 TDD RED](anti-patterns/toolchain-failure-mistaken-for-feature-red.md) | RED 必须落在业务契约，不是 framework、fixture 或 SDK 故障 |

## Experiments

| 文档 | 实验结论 |
| --- | --- |
| [有界时间戳重采样器实验](experiments/2026-07-17-bounded-timestamp-resampler.md) | ±1,000 ppm、60 分钟合成输入得到精确目标帧数，音高与内存上界通过 |
| [Bluetooth 麦克风 60 分钟时钟实验](experiments/2026-07-17-bluetooth-microphone-clock-drift.md) | 每源 host/video residual 为 0 ms；220 ms 原始端点差不是时钟漂移 gate |
| [macOS 区域录屏坐标空间实验](experiments/2026-07-20-macos-region-capture-coordinate-spaces.md) | 双屏对照证明 SCK display filter 的 `sourceRect` 是显示器本地点坐标；异常来自 AppKit 验证窗口双重偏移 |

## 使用方式

1. 遇到相似问题时先查 Anti-pattern，确认失败特征是否一致。
2. 复制实验中的最小诊断和验收门槛，不复制未经验证的结论。
3. 新经验按 [贡献规范](CONTRIBUTING.md) 分类；一次项目观察优先写 Anti-pattern 或 Experiment。
