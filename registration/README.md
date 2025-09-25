# registration — 合规与备案知识库

本目录用于汇总国内外关于人工智能（尤其是大模型/生成式AI）监管要求、备案/登记指引、合规要点与操作模板，供评估、合规与产品上线参考。

包含文件（初版）：

- `eu_ai_act.md` — 欧盟 AI Act 要点与合规影响
- `nist_ai_rmf.md` — NIST AI RMF 1.0 摘要与实施要点
- `china_ai_regulations.md` — 中国关于算法推荐、生成式AI等行政措施汇总
- `pipl.md` — 中国个人信息保护法（PIPL）与数据跨境合规要点
- `oecd_ai_principles.md` — OECD AI Principles 摘要
- `registration_checklist.md` — 面向模型/服务发布的合规核查清单（可用于内部审核）
- `registration_template.md` — 登记/备案条目模板（供文档/记录使用）
- `sources.md` — 参考资料与权威链接

如何使用

1. 在准备对外服务（尤其是面向欧盟用户或在国内向公众提供生成式/推荐类服务）前，先用 `registration_checklist.md` 做一次自检。
2. 将每个需要备案或需要合规评估的模型/服务按 `registration_template.md` 建立条目，放入 `registration/entries/`（后续可扩展为数据库或CSV）。
3. 重要条目（高风险模型、涉敏数据、跨境传输）建议执行第三方评审并记录证据与报告路径。

注意：本库为整理与参考之用，不构成法律意见。具体合规义务以监管部门公布的法律法规及官方指南为准。
