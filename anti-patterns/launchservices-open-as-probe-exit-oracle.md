# 反模式：把 `open -W` 当作探针子进程退出码

## 一句话结论

`open -W -n App.app --args ...` 适合经 LaunchServices 启动 GUI 应用，但不应当作严格 CLI 探针的退出码和 stderr oracle；需要真实 `.app` 身份的 TCC 实验应通过 LaunchServices 启动，并以显式结果文件作为唯一结论通道。

## 场景

一个 ad-hoc signed `.app` 同时显示 AppKit UI、执行自动录制并以 sysexits 状态表示 PASS/FAIL。

## 失败表现

- `open -W` 很快返回，却没有创建证据目录。
- LaunchServices 没有把子进程的真实 stderr 和 exit status 传给调用脚本。
- 自动化误把 launcher 成功当成 probe 成功。
- AppKit terminate callback 又以默认 0 覆盖内部失败状态。

## 根因

启动器进程、应用进程和 AppKit 生命周期是三个不同的终止主体。等待 launcher 不等于拥有目标 executable 的进程状态。

## 正确做法

- 普通 CLI 探针需要严格 status 时，可直接执行 `App.app/Contents/MacOS/<Executable>`；但先确认实验不依赖 LaunchServices/TCC 对应用身份的归因。
- 权限实验必须按用户真实启动方式运行 `.app`。如果直接 Mach-O 和 LaunchServices 观测到不同 TCC 状态，禁止混入同一矩阵。
- 应用内部只有一个 terminal-status owner，AppKit termination 从该状态退出。
- stdout/stderr、report verdict 和 shell exit code 三者交叉校验。
- 若必须经 LaunchServices，使用带 schema 和原子发布的 result file，并把 launcher 的 0 仅视为“已请求启动/应用已结束”，不能视为 probe PASS。
- 每次结束检查无残留 probe process。

## 验证清单

- PASS 返回 0，参数错误、运行失败和验证失败返回不同非零状态。
- report conclusion 与 shell status 一致。
- Quit/termination 路径保留此前失败 status。
- 失败 bundle 在进程退出前原子完成。
- 权限报告记录 bundle ID、签名二进制哈希、启动方式和请求前后状态。
