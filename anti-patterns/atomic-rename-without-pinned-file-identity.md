# 反模式：只调用 rename 就声称文件发布原子且安全

## 一句话结论

同目录 no-replace rename 只解决名称切换的原子性；若目录或临时文件可在检查后被替换，仍有 TOCTOU、symlink 和误覆盖风险。发布前后应固定目录与文件 identity。

## 场景

录制先写隐藏临时 MP4，成功后改名为用户可见文件；同秒重名要自动增加序号。

## 失败表现

- `fileExists` 检查后目标名被并发创建，rename 覆盖或失败。
- 目标目录在 prepare 与 publish 之间被换成 symlink。
- 临时路径被替换成另一个文件、FIFO 或 symlink。
- 返回的最终 URL 指向的 inode 不是刚写完的临时文件。

## 根因

路径是可变名称，不是文件身份。把多个 path-based 检查拼起来不会消除检查与使用之间的竞态。

## 正确做法

- 临时文件和最终文件必须在同一真实目录，保证 rename 不跨 volume。
- 以 `O_DIRECTORY | O_NOFOLLOW` 打开目录并记录 `device+inode`。
- 相对目录 fd 以 `O_NOFOLLOW` 打开临时文件，验证 regular file 并记录 identity。
- 使用 no-replace rename；遇到 `EEXIST` 递增序号重试，其他 errno 立即失败。
- rename 前再次验证目录/临时文件 identity，rename 后验证最终名仍指向原 inode。
- prepare 阶段也明确拒绝 symlink destination。

## 验证清单

- 注入目录替换、临时文件替换、目标竞争创建和发布后替换。
- 重名测试证明永不覆盖已有文件。
- 失败时保留临时文件并返回具体 POSIX errno。
- 不用跨文件系统 copy+delete 冒充原子发布。

## 适用范围

适用于录制、下载、导出、配置落盘和任何“临时文件完成后公开”的流程。

