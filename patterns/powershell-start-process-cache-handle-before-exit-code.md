# Pattern: PowerShell Start-Process 重定向输出时先缓存原生句柄

## 一句话结论

Windows PowerShell 5.1 使用 `Start-Process -PassThru` 并重定向标准输出/错误时，应在进程启动后立即访问一次 `.Handle`，再等待退出并读取严格类型的 `.ExitCode`；否则进程对象可能在输出泵和退出状态同步前失去可用句柄，导致退出码不可用或读取异常。

## 适用场景

- 控制器启动 payload、验证器或其他子进程。
- 使用 `-RedirectStandardOutput` 和 `-RedirectStandardError` 收集诊断。
- 需要把子进程退出码作为不可伪造的门禁，而不是只看结果文件或控制台文本。
- 运行环境是 Windows PowerShell 5.1 / .NET Framework。

## 已观察到的失败

Phase 8C Windows 校准中，子进程已经正常生成结果，控制器也调用了 `WaitForExit()`，但随后读取 `.ExitCode` 仍可能得到不可用状态。将 `Process` 对象保存到集合并不等同于固定其原生句柄；重定向输出又增加了异步输出泵与进程终止的竞态窗口。

## 实现模式

```powershell
$process = Start-Process `
    -FilePath $Executable `
    -ArgumentList $Arguments `
    -RedirectStandardOutput $stdoutPath `
    -RedirectStandardError $stderrPath `
    -PassThru

# 启动成功边界立即强制 Process 对象取得并缓存原生句柄。
$null = $process.Handle

$process.WaitForExit()
$process.Refresh()

$exitCode = $process.ExitCode
if ($null -eq $exitCode -or $exitCode.GetType() -ne [int]) {
    throw 'child_exit_code_unavailable'
}
```

控制器还应记录由自身启动的 PID、进程创建时间和角色，并且清理时只停止能够重新证明身份的自有进程。读取日志尾部只能用于诊断，不能代替退出码。

## 为什么要在启动后立即缓存

- `Start-Process -PassThru` 返回托管 `System.Diagnostics.Process` 对象，但其底层句柄的生命周期不是“变量还在，句柄就一定可读”。
- 首次访问 `.Handle` 会迫使对象在进程仍明确存活的边界取得原生句柄。
- `WaitForExit()` 负责等待进程完成；`Refresh()` 刷新托管属性；严格 `[int]` 检查防止 `$null`、字符串或隐式转换被当成成功。
- 输出文件出现、结果 JSON 存在或成功标记打印，都不能证明子进程最终退出码为 0。

## 合约测试

- 静态检查要求 `Start-Process -PassThru` 后、返回包装对象前访问 `.Handle`。
- payload 和独立验证器都必须通过同一退出码读取函数。
- 退出码缺失、非 `[int]` 或非零时 fail closed。
- 失败测试覆盖：启动失败、运行中失败、已生成部分结果后失败、重定向日志仍在写入。
- 最终成功必须同时满足子进程退出码、结果 Schema、独立验证器和清理门禁，任何单一信号不能替代其他信号。

## 常见误判

- “已经 `WaitForExit()`，所以 `.ExitCode` 必然可读”：等待完成不等于之前已取得稳定原生句柄。
- “保存了 `$process` 变量，所以句柄不会丢”：托管对象引用与原生句柄状态不是同一件事。
- “结果文件存在即可视为成功”：子进程可能在写出中间结果后失败。
- “把异常吞掉并默认退出码 0”：这会让安全验证从 fail closed 变成 fail open。

## 相关

- [PowerShell 5.1 脚本调用与 JSON 数组边界](powershell-51-script-invocation-and-json-array-boundaries.md)
