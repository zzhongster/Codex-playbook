# Pattern: 精确恢复工作树中未物化的受控文件

## 一句话结论

当 Git 索引和提交中存在文件、但当前工作树没有真实内容时，应先判定它属于 sparse checkout、skip-worktree、LFS 指针还是异常占位，再只恢复已确认安全的精确路径；不要用全仓库 checkout/restore 覆盖用户改动。

## 典型场景

- 在独立 worktree 中，生成器依赖的历史证据或清单文件没有物化。
- `git ls-files` 能找到路径，`git show HEAD:<path>` 能读取内容，但工作树中的文件缺失、为空或仍是指针文本。
- 全仓库状态看起来正常，直到工具按实际文件系统读取时才失败。

## 诊断顺序

1. 用 `git ls-files --stage -- <path>` 确认文件受 Git 管理并记录 blob ID。
2. 用 `git cat-file -e HEAD:<path>` 和 `git show HEAD:<path>` 确认提交对象中确有内容。
3. 检查 `git sparse-checkout list`、`git ls-files -v -- <path>` 和 `.gitattributes`，区分 sparse/skip-worktree/LFS。
4. 比较工作树文件与提交 blob；若工作树有真实用户改动，立即停止，不能恢复覆盖。
5. 只对已经确认无本地改动的路径执行 `git restore --source=HEAD --worktree -- <path>`。

## 安全实现原则

- 路径必须明确，禁止 `git restore .`、`git checkout -- .` 等宽范围操作。
- 恢复前后都检查 `git status --short -- <path>`。
- 对证据文件再比较 blob/hash，确保物化内容与冻结输入一致。
- 如果文件由 Git LFS 管理，应走 LFS 的拉取/checkout 流程，不能把指针文本误当业务数据。
- 自动化脚本应把“提交中存在但工作树不可读”作为独立错误，避免误报为源文件不存在。

## 验证清单

- 精确路径在 `HEAD` 中存在。
- 恢复前确认没有用户修改。
- 恢复后的文件 hash 与目标 blob 或冻结清单一致。
- 无关文件的状态完全未变化。
- 依赖该文件的生成/验证命令能够重复通过。
