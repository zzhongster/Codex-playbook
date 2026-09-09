# Pattern: PowerShell 5.1 脚本调用与 JSON 数组边界

## 一句话结论

在 Windows PowerShell 5.1 中，直接调用 `.ps1` 脚本后不要依赖 `$LASTEXITCODE`，解析顶层 JSON 数组后也不要假设 `@(...)` 会展开元素；前者用终止错误传播，后者先从原始 JSON 验证 DOM 根形状，再直接保存 `ConvertFrom-Json` 的结果。

## 适用场景

- 控制器、payload、导出器和独立验证器由多个 `.ps1` 组成。
- 脚本启用 `Set-StrictMode -Version Latest` 并要求确定性失败传播。
- 独立验证器需要在 Windows PowerShell 5.1 下读取由 `ConvertTo-Json` 产生的顶层数组。

## 已观察到的对照

- 直接使用 `& $scriptPath ...` 调用 PowerShell 脚本后读取 `$LASTEXITCODE`，在 strict mode 下因变量未定义而失败；去掉该检查并让终止错误向上传播后，脚本链正常完成。
- `ConvertFrom-Json` 返回含 19 个元素的顶层 JSON 数组时，`@($decoded)` 在 PowerShell 5.1 中可得到一个“数组对象”，导致数量被误判为 1；显式遍历并追加后得到正确的 19 个元素。
- 后续 29 阶段协议进一步发现，`@(Get-Content ... | ConvertFrom-Json)` 可能把顶层数组再次包装成单元素数组。仅检查解析结果类型和数量无法证明原始 JSON 根就是“对象数组”，必须先验证原始 DOM 根和每个直接子项，再把 `ConvertFrom-Json` 结果直接赋值。
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

### 验证并保存顶层 JSON 数组

```powershell
$raw = Get-Content -LiteralPath $Path -Raw -Encoding UTF8

# 先验证原始 JSON 的容器身份，防止 ConvertFrom-Json 的流水线展开/包装语义
# 掩盖“根不是对象数组”或“数组中又嵌套数组”的输入。
Add-Type -AssemblyName System.Web.Extensions -ErrorAction Stop | Out-Null
$serializer = New-Object System.Web.Script.Serialization.JavaScriptSerializer
$dom = $serializer.DeserializeObject($raw)
if ($null -eq $dom -or $dom.GetType() -ne [object[]]) {
    throw 'JSON root must be an array.'
}
foreach ($directItem in $dom) {
    if (
        $null -eq $directItem -or
        $directItem -is [array] -or
        $directItem -isnot [System.Collections.IDictionary]
    ) {
        throw 'JSON root must contain direct objects only.'
    }
}

$items = $raw | ConvertFrom-Json
if ($items.GetType() -ne [object[]] -or $items.Count -ne $ExpectedCount) {
    throw 'Decoded array shape mismatch.'
}
```

后续数量、顺序、唯一性和封闭词表检查全部基于 `$items`。不要用 `@($raw | ConvertFrom-Json)`，也不要让后续业务枚举承担根容器验证职责。

## 应写入的合约测试

- 禁止在直接 `.ps1` 调用后读取 `$LASTEXITCODE`。
- 允许且要求原生可执行文件调用立即保存 `$LASTEXITCODE`。
- 顶层 JSON 数组必须先从原始 JSON 验证根类型和直接子项类型，再直接保存 `ConvertFrom-Json` 结果；不接受 `@($decoded)` 或 `@(... | ConvertFrom-Json)`。
- 使用 Windows PowerShell 5.1 实际解析全部脚本，并对代表性多元素 JSON 执行真实数量断言。
- 最终验证器必须同时校验数量、顺序、唯一性和允许值，防止“解析成功但形状错误”。

## 常见误判

- “`$LASTEXITCODE` 是任何外部调用的通用返回码”：它主要对应原生程序，不是 `.ps1` 调用的可靠状态通道。
- “外层 `@(...)` 一定会展开 JSON 数组”：Windows PowerShell 5.1 的 `ConvertFrom-Json` 有顶层数组形状差异，外层数组运算符还可能二次包装；必须验证原始 DOM 根。
- “JSON 能解析就证明验证器正确”：必须再验证容器形状和预期元素数。

## 边界

该模式针对 Windows PowerShell 5.1。PowerShell 7 的 JSON 行为可能不同，但为保持跨版本确定性，显式标准化仍是更稳妥的协议边界。
