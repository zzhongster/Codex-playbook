# Pattern: PowerShell 5.1 脚本调用与 JSON 数组边界

## 一句话结论

在 Windows PowerShell 5.1 中，直接调用 `.ps1` 脚本后不要依赖 `$LASTEXITCODE`，解析顶层 JSON 数组后也不要假设 `@(...)` 会展开元素；前者用终止错误传播，后者用显式 `foreach` 标准化。

## 适用场景

- 控制器、payload、导出器和独立验证器由多个 `.ps1` 组成。
- 脚本启用 `Set-StrictMode -Version Latest` 并要求确定性失败传播。
- 独立验证器需要在 Windows PowerShell 5.1 下读取由 `ConvertTo-Json` 产生的顶层数组。

## 已观察到的对照

- 直接使用 `& $scriptPath ...` 调用 PowerShell 脚本后读取 `$LASTEXITCODE`，在 strict mode 下因变量未定义而失败；去掉该检查并让终止错误向上传播后，脚本链正常完成。
- `ConvertFrom-Json` 返回含 19 个元素的顶层 JSON 数组时，`@($decoded)` 在 PowerShell 5.1 中可得到一个“数组对象”，导致数量被误判为 1；显式遍历并追加后得到正确的 19 个元素。
- 对两个边界都增加静态合约测试后，同一完整流程的 payload 与独立验证器均返回 0。

## 实现模式

### 调用 PowerShell 脚本

```powershell
$ErrorActionPreference = 'Stop'
& $ScriptPath -InputPath $InputPath
# 成功时继续；失败时由终止错误向上传播。
```

只有在调用原生可执行文件时才读取 `$LASTEXITCODE`，并在同一语句边界立即保存：

```powershell
& $NativeExe @arguments
$nativeExit = $LASTEXITCODE
if ($nativeExit -ne 0) {
    throw "native command failed: $nativeExit"
}
```

### 标准化顶层 JSON 数组

```powershell
$decoded = Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
$items = @()
foreach ($item in $decoded) {
    $items += $item
}
```

后续数量、顺序、唯一性和封闭词表检查全部基于 `$items`，不直接基于 `ConvertFrom-Json` 的返回形状。

## 应写入的合约测试

- 禁止在直接 `.ps1` 调用后读取 `$LASTEXITCODE`。
- 允许且要求原生可执行文件调用立即保存 `$LASTEXITCODE`。
- 顶层 JSON 数组必须通过显式遍历展开，不接受仅用 `@($decoded)` 的实现。
- 使用 Windows PowerShell 5.1 实际解析全部脚本，并对代表性多元素 JSON 执行真实数量断言。
- 最终验证器必须同时校验数量、顺序、唯一性和允许值，防止“解析成功但形状错误”。

## 常见误判

- “`$LASTEXITCODE` 是任何外部调用的通用返回码”：它主要对应原生程序，不是 `.ps1` 调用的可靠状态通道。
- “外层 `@(...)` 一定会展开 JSON 数组”：Windows PowerShell 5.1 的 `ConvertFrom-Json` 有顶层数组形状差异，需要显式枚举。
- “JSON 能解析就证明验证器正确”：必须再验证容器形状和预期元素数。

## 边界

该模式针对 Windows PowerShell 5.1。PowerShell 7 的 JSON 行为可能不同，但为保持跨版本确定性，显式标准化仍是更稳妥的协议边界。
