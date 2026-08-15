# 反模式：让 Windows PowerShell 自动猜测 UTF-8 无 BOM 清单编码

## 一句话结论

Windows PowerShell 2–5 下，不要用默认 `Get-Content` 读取含非 ASCII 路径的 UTF-8 无 BOM 哈希清单；必须显式指定 UTF-8，并将路径集差异与内容哈希分开验证。

## 场景

遗留 Windows 环境中生成排序后的 SHA-256 证据清单。为了跨平台稳定，清单使用 UTF-8 无 BOM，其中包含中文目录和文件名；复核器运行在 Windows PowerShell 2 兼容路径。

## 失败表现

- 清单本身的 SHA-256 稳定，但复核器报告大量“文件缺失”。
- 纯 ASCII 路径通过，只有中文等非 ASCII 路径失败。
- 实际文件集数量与清单数量一致，但字符串路径无法匹配。
- 将同一清单用明确 UTF-8 解码后，所有缺失立即消失。

一次实测中，默认读取导致中文路径被 ANSI 误解码；改为显式 UTF-8 后，1,460 个清单条目与 1,460 个实际文件完全对齐，路径差异 0、哈希不匹配 0。

## 根因

Windows PowerShell 的历史默认编码与现代 PowerShell Core 不同。UTF-8 无 BOM 没有可供老版本自动识别的标记，`Get-Content` 可按当前 ANSI 代码页解码。哈希的 ASCII 部分仍看似正常，而路径字符串已被破坏，容易被误判为文件丢失或证据篡改。

## 正确做法

- 生成端固定一种编码和换行符，并将编码写入清单规范。
- 在旧 Windows PowerShell 中用 `[IO.File]::ReadAllLines($path, [Text.Encoding]::UTF8)` 或等价的显式 UTF-8 API，不依赖默认 `Get-Content`。
- 解析时把每行拆成固定长度哈希和原始相对路径；不允许静默丢弃解码失败的行。
- 先比较“清单路径集”和“实际路径集”，分别报告缺失和额外路径；只对交集计算内容哈希差异。
- 对清单文件自身另行计算摘要，但不把清单放入自己的被封印集，避免循环自证。
- 最终结果至少包含：清单条目数、实际文件数、路径集差异、哈希不匹配和清单摘要。

## 验证清单

- 夹具同时包含 ASCII、中文、空格和 Unicode 组合字符路径。
- 用目标 Windows PowerShell 版本执行，不只在 PowerShell 7 或 Linux/macOS 上测试。
- 人为新增一个未入清单文件，必须出现 1 个额外路径。
- 人为删除一个清单文件，必须出现 1 个缺失路径。
- 只改文件内容不改名，必须出现 1 个哈希不匹配且路径集差异为 0。
- 以默认 ANSI 读取作为负对照，确认非 ASCII 路径会重现失败；再以显式 UTF-8 读取证明修复。

## 适用范围

适用于遗留 Windows 取证、部署清单、备份验证、软件物料清单和任何由 Windows PowerShell 2–5 消费跨平台 UTF-8 文件的流程。它不替代独立签名或脱离复核。

## 相关

- `ignored-evidence-without-durable-manifest.md`
- `post-validation-code-change-without-revalidation.md`
