# 大模型评价指标与工具 — 研究框架

目标
- 建立一个面向产品和场景设计的“全景”大模型能力与规格知识库，支持快速查询与标签化评估，便于在设计场景或功能时设定模型需求。

总体思路（高层）
- 将研究分为两大主体：模型规格与标准（规格KB）与场景研究（场景KB）。
- 每个主体由多个子知识库组成（指标池、平台操作手册、备案/合规、原子能力与Agent清单、测试工具清单等）。
- 以表格/结构化文件（JSON/YAML）为主存储单元，配合Markdown文档用于说明与操作指南，确保可机器解析与人工维护。

布局与目录建议（本文件夹）
- `indicators/` — 指标池与指标模板（指标定义、来源、维护团队、如何执行、是否付费、工具与产出示例）
- `models/` — 按输入/输出类型组织的模型规格与标签（例如：文本->文本、图像->文本、文本->图像、多模态交互等）
- `platforms/` — 训练平台、评测平台、部署平台操作知识库（按厂商或平台独立维护）
- `registration/` — 大模型备案、合规与监管实践文档（国家/地区/流程）
- `scenarios/` — 场景目录、场景所需原子能力与Agent映射、场景测试规范与数据样例
- `tools/` — agent编排、场景数据管理、实车/台架测试工具列表与使用指南
- `templates/` — JSON/YAML/MD模板，用于后续批量填充与自动化处理
- `README.md`, `TODO.md` — 项目说明与任务清单（当前文件）

核心合同（contract）
- 输入：模型/场景/平台 的元信息（JSON）
- 输出：可搜索的标签集合（按指标与场景）、评测执行说明、示例产出
- 数据形态：
  - 指标条目（YAML/JSON）示例字段：id, name, definition, source, owner, cost, tooling, runbook, example_output
  - 模型条目（JSON）示例字段：model_name, input_types, output_types, size_params, architecture_family, license
  - 场景条目（JSON）示例字段：scenario_id, name, description, required_atomic_capabilities, recommended_agents, test_data_refs
- 错误模式：不一致标签、缺失字段、重复条目；需用CI/验证脚本检测并报告。

规格拆解（建议字段与标签维度）
1) 指标池（Indicator Pool）
  - 指标分类：性能（latency/throughput）、准确性（F1/EM/ROUGE）、稳健性（对抗/泛化）、安全（toxicity、隐私泄露）、对齐（指令遵从）、多模态质量指标等
  - 每个指标记录：定义、计算方式、数据要求、评测脚本/工具、是否收费、维护团队、记录示例

2) 定性指标（标签化）
  - 部署性能：最低硬件、推荐硬件、对GPU/CPU/TPU的支持
  - 推理能力：延迟等级、并发能力、分布式推理支持
  - 模型规模：参数量、量化友好度、训练时长与成本估计
  - 模型能力：通用理解、对话、检索、代码生成、视觉理解、多模态推理等能力标签
  - 模型架构：transformer变体、encoder-only、decoder-only、encoder-decoder、多模态模块描述

操作性知识库（按类别独立维护）
- 训练平台（按厂商）：能力说明、支持的模型类型、示例训练流程、计费/配额信息
- 评测平台（按厂商/工具）：如何上传模型、如何运行评测、示例报告格式
- 大模型备案合规：法务/合规要求清单、备案流程、常见问题与合规案例
- 定性指标补充：部署平台最低硬件、训练数据最低要求（样本量、标注类型）

场景研究（概要）
- 场景由“原子能力（atomic capabilities）”与“Agent能力”组成：
  - 原子能力：可组合的最小功能单元（如：文本分类、实体抽取、OCR、语音识别、图像分割、知识检索）
  - Agent：封装多个原子能力与策略，直接可用于解决特定任务（例如：客服Agent、写作助理、视觉检测Agent）
- 建议维护两张表：
  - 表1：能力清单（`templates/abilities.json`） — id, name, category, description, input_types, output_types, minimal_requirements
  - 表2：Agent清单（`templates/agents.json`） — id, name, capability_ids, orchestration_requirements, runtime_requirements, example_use_cases
- 场景指标：为每个场景定义必要指标标签（从指标池选取），并记录优先级与可接受阈值
- 场景测试工具：列出并描述agent编排工具、场景数据管理工具、实车/台架测试工具，给出测试流程示例

维护与迭代流程
- 变更流程：提交PR -> 自动验证（schema检查/必填字段/无重复ID）-> 维护团队审阅 -> 合并
- 周期：指标池与平台文档每季度复核；场景与能力表根据产品需求即时更新
- 负责人：建议按KB模块指定Owner（维护团队）字段

贡献指南（简要）
- 新增指标或条目：在对应目录下新增YAML，然后提交PR，CI将运行schema校验脚本
- 格式与命名规范：使用UTF-8，无BOM；文件名使用英文或拼音并包含语义前缀，例如 `indicators/accuracy/f1.yaml`

质量门（Quality Gates / QA）
- 基本校验：所有条目必须包含ID、name、source/owner；指标必须带有runbook或执行说明
- 自动化：后续添加CI脚本检查JSON/YAML的schema与必要字段

快速示例（简短）
- 指标条目（YAML）示例：
  id: accuracy_f1
  name: F1-score
  definition: 调和平均的精确率与召回率
  source: 开源/标准定义
  owner: ML评估组
  cost: free
  tooling: `eval/f1.py`
  example_output: {precision: 0.82, recall: 0.78, f1: 0.80}

下一个最小可交付（MVP）
- 新建目录结构与基本模板（`templates`）
- 填写初始的能力清单与Agent清单样例（1-3条）
- 建立指标池的首批指标（性能/准确性/安全各1-2个）

联系方式与负责人
- 请在仓库中以 `OWNERS.md` 或者在每个子目录的 `OWNER` 文件中指定负责人。

---
(文档结束)
