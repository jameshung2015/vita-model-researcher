# TODO — 大模型评价指标与工具 研究计划（初版）

工作分阶段（优先级与里程碑）

1. 启动与目录搭建（1周）
   - [x] 在本目录下创建初始子目录：`indicators/` `models/` `platforms/` `registration/` `scenarios/` `tools/` `templates/`
   - [x] 初始化 `README.md` 与 `TODO.md`（已完成）
   - [x] 在 `templates/` 中放入基础JSON样例：`abilities.json`, `agents.json`, `indicator_template.yaml`

2. 指标池初版（2周）
      - [x] 收集并整理公开指标（accuracy, latency, throughput, robustness, toxicity） — 已在 `indicators/` 下创建：`accuracy_f1.json`, `latency_p99.json`, `throughput_rps.json`, `robustness_adv.json`, `toxicity.json`, `index.md`
   - [x] 将指标条目放入 `indicators/` 目录并建立索引文件 `indicators/index.md`

3. 模型规格与标签体系（2周）
   - [x] 设计模型条目schema（字段与数据类型）并放入 `templates/model_schema.json`
   - [x] 对市面常见模型类型（LLM、VLM、speech）完成分类示例并录入 `models/`

4. 场景与能力（持续）
   - [x] 制定 `templates/abilities.json` 与 `templates/agents.json` 模板
   - [x] 填充 10 个汽车座x舱场景（知识问答、警报问答、、多模态问答等）并定义每个场景的能力与优先指标x
   - [x] 为每个场景定义最低需求依赖清单（跟每个场景关联`scenarios/<scenario>/`）

5. 平台与工具知识库（并行）
   - [x] 收集训练平台（百炼, 火山引擎, Azure, NVIDIA DGX 等）操作说明
   - [x] 收集评测平台工具（Eval harnesses, Evals, LMFlow, OpenEval 等）与使用样例
   - [x] 整理部署/台架/实车测试工具清单

6. 合规与备案（重要）
   - [ ] 收集国内外监管要求与备案指引，形成 `registration/` 知识库

7. 自动化与验证（MVP后）
   - [ ] 编写schema校验脚本（Python）并集成到CI
   - [ ] 编写基础搜索/查询脚本，支持按标签检索模型或场景需求

具体初始任务（马上开始）
- [x] 新建 `README.md`（本次完成）
- [x] 新建 `TODO.md`（本次完成）
- [x] 在 `templates/` 中加入最小json模板（abilities/agents/indicator_template）

交付物与验证标准
- 交付物：目录结构、README、TODO、templates样例、首批指标、3个示例场景
- 验证：人工审阅 + 自动schema检查，示例场景能被查到并返回所需标签

备注与假设
- 假设：团队有权访问公共评测工具与训练平台的公开文档；私有/付费工具将记录为“付费/需授权”。
- 若需对接真实平台API或自动化运行评测，将在后续任务中列入并申请凭证/访问权限。

下一步
- 请确认是否需要我继续：
  - 在 `templates/` 里创建json/JSON模板样例（我可以立刻生成并放入 `templates/`）
  - 或者开始填充第一批指标与场景示例（需明确优先场景）
