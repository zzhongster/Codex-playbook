# 运行时实验记录模板

```yaml
record_id: "REPLACE_WITH_QUALIFIED_EXPERIMENT_ID"
product_version: "REPLACE_WITH_IMMUTABLE_PRODUCT_VERSION"
scope_or_module: "REPLACE_WITH_QUALIFIED_SCOPE_OR_MODULE_ID"
status: "REPLACE_WITH_RECORD_STATUS"
evidence_references: []
owner: "REPLACE_WITH_NAMED_HUMAN_OWNER"
validation_method: "REPLACE_WITH_REPRODUCTION_AND_ACCEPTANCE_METHOD"
last_updated: "YYYY-MM-DD"
atomic_claims:
  - claim_id: "REPLACE_WITH_QUALIFIED_CLAIM_ID"
    statement: "REPLACE_WITH_ONE_PRECISE_EXPERIMENT_RESULT_CLAIM"
    status: "REPLACE_WITH_CLAIM_STATUS"
    confidence: "REPLACE_WITH_LOW_MEDIUM_OR_HIGH"
    evidence_references: []
evidence_method_entries:
  - evidence_id: "REPLACE_WITH_QUALIFIED_EVIDENCE_ID"
    method_id: "REPLACE_WITH_QUALIFIED_METHOD_ID"
    method_maturity: "proposed"
authorization_record_id: "REPLACE_WITH_ART_P0_AUTH_ID"
authorization_gate_record_id: "REPLACE_WITH_CURRENT_ART_G0_AUTH_ID"
environment_identity: "REPLACE_WITH_IMMUTABLE_ENVIRONMENT_IDENTITY_AND_HASHES"
pre_state_fingerprint: "REPLACE_WITH_BASELINE_FINGERPRINT"
sentinel: "REPLACE_WITH_UNIQUE_SYNTHETIC_SENTINEL"
expected_observations: []
actual_observations: []
first_failure: "REPLACE_WITH_FAILURE_EVIDENCE_ID_OR_EXPLICIT_NONE"
cleanup: []
residual_checks: []
```

方法成熟度只评价取证、建模或验证方法及其证据基础，不评价目标产品事实；产品主张必须另用 `status`、`confidence` 和 `evidence_references`。

顶层 `status` 是本记录的生命周期状态；产品事实只写入 `atomic_claims`。`evidence_method_entries[].method_maturity` 只评价对应 `method_id`，不得提升关联主张。

## 不可变环境与授权

- 固定 environment identity：构建、部署/克隆、运行时、依赖、配置哈希、功能开关、时区、账号和角色。
- 引用已授权动作与当前 `ART-G0-AUTH` 的 `pass`，单列读取、写入、故障注入、外发和清理权限。

## 前置状态指纹与唯一哨兵

- 保存 pre-state fingerprint：对象状态、关键只读快照、队列、缓存、外部连接、权限和资源基线。
- 使用不含个人信息或秘密的 sentinel 贯穿界面、网络、日志、数据、消息、文件和清理记录。

## 实验步骤与观测点

| step | action/input | expected observation | observation surface | stop condition |
| --- | --- | --- | --- | --- |
| REPLACE_WITH_STEP_NUMBER | REPLACE_WITH_ACTION | REPLACE_WITH_EXPECTATION | REPLACE_WITH_UI_NETWORK_LOG_DATA_OR_OTHER | REPLACE_WITH_STOP_TRIGGER |

每步只改变一个研究变量，写明等待条件、工具版本和证据捕获位置；未获准的观测面保持缺口。

## 预期与实际观察

- 执行前冻结 expected observations；执行后另填 actual observations、运行序号、时间、执行者、偏差和证据 ID。
- 界面、网络、日志、数据库、消息、缓存、文件、通知和外部效应分别记录，不用最终结果覆盖中间状态。

## 首个失败保全

- 在任何自动重试前保存 first failure 的多观察面、关联 ID、时间顺序和当时状态。
- 后续尝试使用新运行序号并链接首错；最终成功不得抹去失败、部分提交或补偿证据。

## 逆序清理与残留检查

- cleanup 按副作用逆序记录停止外发、下游撤销、队列/缓存处理、业务逆向动作和临时权限撤销。
- residual checks 用哨兵核对界面、数据、日志、消息、文件、备份可达范围和外部模拟器，并记录差异及处置证明。
