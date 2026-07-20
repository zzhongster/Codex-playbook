# Pattern: Derive media track topology from enabled sources

## 一句话结论

录屏 writer 的轨道拓扑必须由实际启用的来源决定；系统声音和麦克风都关闭时，不要创建空 AAC 轨，也不要让视频 readiness 等待不存在的音频 callback。

## 实现要点

- `hasAudio = systemAudioEnabled || microphoneEnabled` 是 writer、mixer、capture configuration 和 readiness 的共同输入。
- `hasAudio == false` 时：
  - `AVAssetWriter` 只创建 video input；
  - 不创建 mixer；
  - `SCStreamConfiguration.capturesAudio = false`；
  - readiness 只要求完整视频帧；
  - finish 只 mark video input finished。
- 只有麦克风时，SCK 不捕获系统声音，但 AVAudioEngine 和 mixer 仍生成 AAC 轨。
- 只有系统声音时，不请求麦克风权限，也不启动 AVAudioEngine。

## 验证清单

- 四种开关组合都能开始、停止和发布。
- 双关闭文件只有一个 H.264 视频轨。
- 单来源音频不会等待另一来源 watermark。
- 关闭麦克风不会出现权限弹窗。

