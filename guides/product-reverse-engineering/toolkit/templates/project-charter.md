# 项目章程模板

复制下面的 YAML，替换全部 `REPLACE_WITH_...` 值并填写空数组。章程是授权与交付边界的不可变快照；不要在已批准版本上直接扩权。

```yaml
charter_id: "REPLACE_WITH_QUALIFIED_CHARTER_ID"
charter_version: "REPLACE_WITH_IMMUTABLE_VERSION"
primary_goal: "REPLACE_WITH_REWRITE_MIGRATION_REPLACEMENT_DUE_DILIGENCE_OR_COMPETITOR_RESEARCH"
authorization:
  decision_artifact_id: "REPLACE_WITH_ART_P0_AUTH_ID"
  decision_artifact_hash: "REPLACE_WITH_SHA256"
  gate_record_id: "REPLACE_WITH_ART_G0_AUTH_ID"
  gate_record_hash: "REPLACE_WITH_SHA256"
  current_gate_verdict: "REPLACE_WITH_CURRENT_VERDICT"
allowed_environments: []
data_policy:
  allowed_classifications: []
  minimization: "REPLACE_WITH_MINIMIZATION_RULE"
  redaction: "REPLACE_WITH_REDACTION_RULE"
  retention_and_disposal: "REPLACE_WITH_RETENTION_AND_DISPOSAL_RULE"
prohibited_actions: []
outputs: []
exclusions: []
risks: []
approval_owners: []
stop_conditions: []
review_date: "YYYY-MM-DD"
```

## 决策目的与完成定义

- 主要目的与待回答决定：写明唯一主要目的、决策人和必须回答的问题。
- 完成定义：冻结八个范围维度、覆盖分母、关键门槛和可接受的不确定性条件。
- 使用限制：说明交付可用于和不可用于哪些决定，避免把调查完整度当成决策授权。

## 授权与允许环境

- 绑定不可变 `ART-P0-AUTH` 及其内容哈希，并引用 `ART-G0-AUTH` 的当前 `pass` 判定与哈希。
- 逐项列出允许读取或运行的系统、账号、角色、环境、数据、时间窗、工具和动作。
- 授权变化时新建 charter 版本；不得原地扩大授权，也不得沿用旧门禁判定。

## 数据政策与禁止动作

- 写明数据分类、最小化、脱敏、外发、保留和处置责任；秘密只保存受控引用，不写入记录正文。
- 列出禁止的枚举、绕过控制、生产破坏、未批准写入、真实外发和跨租户访问。
- 每个禁止动作给出停止、保存最小现场、披露与恢复的责任人和路径。

## 范围、输出与排除

- 对版本、角色、产品表面、技术资产、能力、数据、集成和非功能维度分别写明包含与排除。
- 输出使用相对路径或记录类型允许列表，并指定验证命令、格式、接受人和发布用途。
- 排除项保留稳定 ID、理由、影响和重开条件，不得从分母静默删除。

## 风险、审批与停止条件

- 风险逐项记录 P0/P1/P2、影响、缓解、期限和有权接受人；AI Agent 不接受风险。
- 审批人写明角色、权限范围、签署产物和替代安排；缺少决定人时停止对应发布。
- 环境、身份、版本、授权、数据或隔离漂移时立即停止，记录最后安全状态与恢复条件。
