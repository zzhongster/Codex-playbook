# 反模式：验证后改运行时代码却不重新取证

## 一句话结论

实机 PASS 只属于产生证据的那份代码和二进制；验证后修改 readiness、光标、编码或捕获配置，必须重新构建并重新采集最终证据。

## 场景

六组区域录屏已通过，随后整分支复审发现：

- 探针不应等待系统音频回调。
- 视觉验证应关闭光标。

修复很小，单元测试全绿，容易认为旧实机证据仍足够。

## 失败表现

最终文档声称验证当前 HEAD，但表格和二进制哈希实际来自旧 commit。代码评审无法判断新配置是否改变 ScreenCaptureKit 运行时行为。

## 根因

把“修复逻辑上与坐标无关”当成“运行时证据仍代表新二进制”。对系统 API 来说，任何配置变化都可能改变采样、权限、时序或像素。

## 正确做法

建立代码—证据线性关系：

~~~text
code commit
  -> build/sign
  -> capture-time binary hash
  -> fresh evidence root
  -> independent verification
  -> validation document
  -> docs-only commits
~~~

若验证后又有代码 commit，回到 build/sign 重新开始。后续只允许文档审计修正，且文档要明确“从验证 commit 到最终 HEAD 只有 docs 变化”。

## 验证清单

- 报告写完整代码 commit。
- 录制前和最终打包后的二进制哈希一致。
- 旧证据根保留但明确排除。
- 新证据使用全新根且完整重跑，不混用旧 PASS。
- 整分支复审确认验证 commit 后无代码变化。

## 相关

- [忽略大型证据却不提交可审计清单](ignored-evidence-without-durable-manifest.md)
- [重试掉第一份实机失败证据](retrying-away-first-live-failure.md)

