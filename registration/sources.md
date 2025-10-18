# registration/sources.md — 权威来源索引 (Authoritative Source Index)

Last Updated: 2025-10-18

本文件汇总项目中引用的法规 / 标准 / 治理框架的“权威与可信来源”链接，结构化对应 `regulations/*.json` 的 `reference_links` 字段，便于审计、自动抓取与溯源。所有链接保留原始 URL；如需镜像或缓存，请在后续增补策略中注明。

## 目录 (Table of Contents)
1. 快速导航
2. 分组来源一览
	- 欧盟 (EU)
	- 美国 / 国际框架 (Global Frameworks)
	- 中国 (China)
3. 维护说明

## 1. 快速导航 (Quick Navigation)
重点法规与框架：
- EU AI Act: 三个官方/权威入口（政策框架、法案正文、Explorer）
- NIST AI RMF: 官方出版物与正式 PDF
- OECD AI Principles: 原则页 + 观察站 + 主题扩展
- 中国重点：个人信息保护法 (PIPL)、算法推荐管理规定、生成式 AI 暂行办法、深度合成管理规定等

其他建议持续关注：
- 各国/地区监管机构发布的实施细则与二级指导
- 行业标准化组织（ISO、IEC、GB/T、AIIA、协会团体）发布的最新标准文本与草案

## 2. 分组来源一览 (Grouped Sources)

### 欧盟 (EU)
| Regulation | JSON File | Authoritative / Official Sources |
|------------|-----------|----------------------------------|
| AI Act | `eu/ai_act.json` | https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai ; https://artificialintelligenceact.eu/the-act/ ; https://artificialintelligenceact.eu/ai-act-explorer/ |
| GDPR | `eu/gdpr.json` | https://eur-lex.europa.eu/eli/reg/2016/679/oj |

### 美国 / 国际框架 (Global Frameworks)
| Framework / Principles | JSON File | Authoritative / Official Sources |
|------------------------|-----------|----------------------------------|
| NIST AI RMF | `global/nist_ai_rmf.json` | https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10 ; https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf |
| OECD AI Principles | `global/oecd_ai_principles.json` | https://oecd.ai/en/ai-principles ; https://oecd.ai/ ; https://oecd.org/en/topics/sub-issues/ai-principles.html |
| UNESCO AI Ethics Recommendation | `global/unesco_ai_ethics.json` | https://unesdoc.unesco.org/ ; https://www.unesco.org/en/artificial-intelligence/recommendation-ethics |
| ISO/IEC 23894 | `global/iso_iec_23894.json` | https://www.iso.org/standard/77304.html |
| ISO/IEC 42001 | `global/iso_iec_42001.json` | https://www.iso.org/standard/81230.html |

### 中国 (China)
| Law / Reg / Standard | JSON File | Authoritative / Official Sources |
|----------------------|-----------|----------------------------------|
| PIPL | `china/pipl.json` | https://www.cac.gov.cn/ ; http://en.npc.gov.cn.cdurl.cn/2021-12/29/c_694559.htm ; https://digichina.stanford.edu/work/translation-personal-information-protection-law-of-the-peoples-republic-of-china-effective-nov-1-2021/ ; https://iapp.org/resources/article/personal-information-protection-law-peoples-republic-of-china-english-translation/ |
| Algorithm Recommendation Provisions | `china/algorithm_recommendation_rules.json` | https://www.cac.gov.cn/ ; https://digichina.stanford.edu/work/translation-internet-information-service-algorithmic-recommendation-management-provisions-effective-march-1-2022/ |
| Deep Synthesis Regulation | `china/deep_synthesis_regulation.json` | https://www.cac.gov.cn/ ; https://digichina.stanford.edu/ |
| Generative AI Interim Measures | `china/generative_ai_measures.json` | https://www.cac.gov.cn/ ; https://digichina.stanford.edu/ ; https://www.dataguidance.com/ |
| AIIA AI1A/PG0118-2024 | `china/aiia_pg0118_2024.json` | https://www.aiiaorg.cn/ |
| CAICT Vehicle Intelligent Agent | `china/caict_vehicle_agent_eval.json` | https://www.caict.ac.cn/ |
| GB/T 45288.2-2025 | `china/gbt_45288_2_2025.json` | https://openstd.samr.gov.cn/ |
| T/TAF 255-2024 | `china/t_taf_255_2024.json` | https://www.ttia.org.cn/ |

## 3. 维护说明 (Maintenance Notes)
1. 变更流程：新增或更新来源时，同步修改对应 `regulations/*.json` 的 `reference_links` 并在提交信息中注明来源类别。
2. 链接类型：优先使用官方网站原始发布页；其次为权威翻译（如 DigiChina）、摘要与标准化组织索引；新闻报道仅作为补充（避免单一商业媒体来源）。
3. 审计追踪：CI 中可添加脚本定期校验表中链接可访问性与状态码；失效链接进入待修复队列。
4. 国际化：如需英文版汇总，可在本文件旁创建 `sources_en.md`，保持 JSON 文件引用一致。
5. 后续扩展：计划补充“案例与实施指南”、“合规评估模板”、“风险场景映射”等增强节。

---
说明：本文件为起始索引。后续将补充官方指南、样例申报材料与合规案例摘要；建议建立自动化抓取与缓存策略（版本化快照 + 哈希校验）。
