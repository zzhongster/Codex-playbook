# 反模式：用原始证据 URL 直接判断实体身份

## 结论

原始 URL 是证据，应完整保留；实体比较使用单独的规范化键。两者不能共用一个字段，也不能因为规范化而重写原始响应。

## 现场

2026-10-11，trade-agent-data 的 Buddy S11「按相似度找客户」在 GRUNDFOS 的真实企业库小样中失败。返回的关系证据包含本地化域名与查询参数，而目标企业页面使用规范地址。用字符串全等检查两者，错误地拒绝了同一个企业页面。

第一次真实任务目录保留失败结果；修复后另建验收目录。第二轮返回10家候选，目标20家，因此诚实交付 partial，缺口10家；没有凭网页印象补齐名单。

这是一项单项目的工程教训，先记录为 anti-pattern，不声称跨项目 Pattern。

## 根因

原实现混淆了三种不同用途：提供者的原始证据地址、页面身份键、报告展示地址。只用规范化 URL 构造的合成夹具无法暴露本地化域名、尾斜杠与追踪参数的真实组合。

## 处理方式

1. 保存完整原始响应及原始关系 URL，允许逐行回溯。
2. 在受控的公司页面 URL 范围内，单独派生规范化身份键；统一已知域名别名、路径与非身份查询参数。
3. 用该键进行目标匹配、候选去重、参考企业自身排除。保留原始次序和各条关系证据。
4. 保留不能证明的身份差异。不要把去重扩大成模糊名称合并，不要抹掉 Unicode 变音符号：Gartner 与 Gärtner 不能因此视为同一家。
5. 真实提供者的响应封装也要覆盖：SDK 的响应包装对象与手写 dict 不等价，应在源边界解包，而非在每个业务出口临时猜测。

规范化只能支持页面身份比较，不证明法人身份、采购关系或集团隶属关系。

## 回归验证

- 本地化域名 + 查询参数的原始关系 URL 能匹配规范目标页面，原始证据逐字不变。
- 同页多个写法去重，但各条原始关系证据保留。
- 参考企业自身不能进入相似候选名单。
- Gartner / Gärtner 等真实区分样例分别解析；不能以字符清洗跨企业合并。
- 使用真实 SDK 响应包装对象，而非只测试字典。
- 保存响应后重新渲染聊天与 Excel，结果一致，且不重新查询或扣费。

## 证据与保存边界

- [原始证据 URL 修复](https://github.com/yichayun/trade-agent-data/commit/1099584)：身份比较与原始 URL 保存分离。
- [参考企业自身排除](https://github.com/yichayun/trade-agent-data/commit/8a79e4b)。
- [SDK 包装对象修复](https://github.com/yichayun/trade-agent-data/commit/6cf9709)。
- [固定验收记录](https://github.com/yichayun/trade-agent-data/blob/2bb8dae9cb6c2bec9ad54d6793fc6d8e60a56308/docs/2026-10-11-buddy-company-profiles-acceptance.md)。
- [四项真实案例证据摘要](https://github.com/yichayun/trade-agent-data/blob/2bb8dae9cb6c2bec9ad54d6793fc6d8e60a56308/docs/sessions/1011-buddy-company-profiles-task-evidence.json)。

代码与证据摘要已入库；真实响应、报告与临时日志保留在开发机。这里记录的是本地真实源验证和离线回归，不把它当成生产部署、生产计费或 WorkBuddy 真机验收。
