# 反模式：用 `plutil -lint` 验证 JSON

## 一句话结论

`plutil -p` 能打印 JSON，不代表 `plutil -lint` 是 JSON 语法检查器；JSON 证据应使用 `jq empty`，plist 再使用 `plutil`。

## 场景

macOS 工程同时产生 `Info.plist` 和 `report.json`，验证脚本为了“统一工具”对两者都执行 `plutil -lint`。

## 失败表现

同一个合法 JSON：

~~~text
plutil -p report.json     -> 正常解析
plutil -lint report.json  -> Unexpected character { at line 1
jq empty report.json      -> exit 0
~~~

如果把工具误报当成证据失败，流程会在产品已经 PASS 时停止；更糟的是，有人可能为了让 `plutil` 通过而把 JSON 改成 plist。

## 根因

`plutil -lint` 的帮助文本明确说它检查 property list 文件。`-p` 的输入兼容能力更宽，不构成 `-lint` 支持 JSON 的契约。

## 正确做法

~~~bash
# JSON
jq empty report.json

# plist
plutil -lint Info.plist
plutil -p Info.plist
~~~

结构化字段再用 `jq -e` 写显式断言，不要依赖人眼阅读 `plutil -p` 输出。

## 验证清单

- 工具与文件格式一一对应。
- 先读工具 `-help`，不要从另一个子命令的行为推断。
- JSON 检查后继续验证字段、哈希与引用文件，语法合法不等于证据有效。
- 验证计划中的命令在正式批量运行前先对一个样本 dry run。

