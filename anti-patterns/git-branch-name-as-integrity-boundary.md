# 反模式：把 Git 分支名当作数据完整性边界

## 一句话结论

分支名是可变的协作标签，不是不可变的内容身份；长期可复现的分析或生成任务应校验祖先提交和输入哈希，而不能要求永远运行在某个临时开发分支上。

## 场景

一个遗留系统逆向工程项目按阶段生成结构化知识库和文档。Phase 6 的输入清单记录了分析时所在分支，并在加载器中把它实现成执行门禁：

~~~python
branch = current_branch(repository)
if branch != seeds["required_branch"]:
    raise ValueError("branch contract failed")
~~~

阶段分支完成后被纯快进合并到 `main`。提交、文件树、冻结祖先和输入哈希都没有变化，但同一套工具在 `main` 上无法运行。

## 失败表现

- 同一个 commit 在阶段分支通过，在 `main`、发布分支或 CI detached HEAD 中失败。
- 默认分支改名、仓库迁移或 worktree 收口后，历史生成器突然不可复现。
- 团队被迫长期保留临时分支名，或通过伪造当前分支绕过检查。
- 测试只在功能分支上运行时全绿，合并后才暴露分支耦合。

一次实测中：

| 条件 | commit / 内容 | 结果 |
| --- | --- | --- |
| 阶段分支 | `0f85ffe` | 710 项测试通过，1538.950 秒 |
| `main` 快进到同一 commit | `0f85ffe`，文件树相同 | 全量测试报告 3 个错误；聚焦测试又定位到同源的 Phase 6B 门禁失败 |
| 移除分支名门禁，保留祖先和哈希校验 | 新的集成修复提交 | 710 项测试通过，1524.031 秒 |

观察值是“只改变分支引用就改变测试结果”；由此可确定失败依赖可变的 ref 名称，而不是仓库内容。

## 根因

混淆了三种不同概念：

1. **来源元数据**：任务最初在哪个分支执行，可用于审计说明。
2. **版本身份**：哪些不可变提交必须已经进入当前历史。
3. **输入身份**：生成器实际读取的文件、清单和上游结果是否仍是冻结内容。

分支名只能回答第一项，而且随时可以移动、改名或删除。它既不能证明所需 commit 存在，也不能证明工作树和输入文件没有漂移。

## 正确做法

把分支名保留为 provenance，但不要作为运行许可条件。完整性门禁至少由以下部分组成：

1. 使用完整 commit SHA 记录冻结基线。
2. 用 `git merge-base --is-ancestor <required-commit> HEAD` 证明当前历史包含基线。
3. 对直接输入、上游摘要和源码资产清单计算内容哈希。
4. 对生成物执行确定性生成或 `--verify-only` 比对。
5. 允许任务在功能分支、`main`、发布分支和 detached HEAD 中运行，只要不可变契约成立。

示例：

~~~python
if not is_ancestor(required_commit, head):
    raise ValueError("required commit is not an ancestor of HEAD")

for artifact in frozen_inputs:
    if sha256(artifact.path) != artifact.expected_sha256:
        raise ValueError(f"input hash drift: {artifact.name}")
~~~

如果确实需要限制可写工作流，应在发布权限、受保护分支、CI environment 或签名策略中实现，而不是把分支字符串嵌入内容加载器。

## 验证清单

- 同一 commit 在功能分支和 `main` 上得到相同结果。
- detached HEAD 中仍可执行只读验证与确定性生成。
- 缺少冻结祖先提交时明确失败。
- 任一冻结输入、上游摘要或资产清单哈希变化时明确失败。
- 分支改名或删除不影响历史结果复现。
- 合并后在目标分支重新运行完整测试，而不是只沿用功能分支的绿色结果。
- 测试断言实际读取到的 ref 只作为观测值，不要求固定分支名。

## 适用范围

适用于代码生成器、数据迁移、逆向分析、模型训练数据构建、合规取证、文档流水线和任何需要长期重放的 Git 驱动任务。

如果任务的业务语义确实由分支决定，例如预览环境路由，可以读取分支名选择环境；但它仍不能替代 commit、签名或内容哈希校验。

## 相关

- [验证后改运行时代码却不重新取证](post-validation-code-change-without-revalidation.md)
- [忽略大证据却不提交清单](ignored-evidence-without-durable-manifest.md)
- [把测试工具链故障当成 TDD 的 RED](toolchain-failure-mistaken-for-feature-red.md)
