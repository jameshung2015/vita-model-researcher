> 本文件基于 `README.md` 与 `background.md` 重新评估与扩展原有 Agent 研究工具需求，强化：四大核心矛盾对齐、数据契约可追溯、渐进式交付与智能体（Agents）分工。目标是在 `agents-toolchain/` 下形成可演进、可验证、可自动化扩展的“评测知识 + 执行编排”底座，为后续评测与产品线追踪提供结构化支撑。

## 1. 总体定位（Reframed Vision）
该工具链 = 结构化知识库 (Models / Scenarios / Indicators / Capabilities / Benchmarks / Product Lines) + 采集与验证 Agents + 评测执行编排 + 审计与演化治理。

核心价值：缩短“发现 → 结构化 → 评估 → 报告 → 回溯”路径，使新增模型/场景/供应商评测在 <= 1 小时内形成标准化报告，并与产品线指标自动对齐。

对应四大核心矛盾的解法映射：
| 核心矛盾 | 工具支撑机制 | 关键产物 |
|----------|--------------|----------|
| 模型分类可覆盖与扩展 | Taxonomy Registry + Schema 校验 + 自动相似检索建议 | `models/*.json` + 分类版本标签 |
| 场景分类复用 | 场景标签矩阵 (模态/功能/风险/环境) + 组合生成器 | `scenarios/*/meta.json` |
| 内部能力基线 | Benchmark Pullers + Baseline Store + 差异报告生成 | `benchmarks/*.json` / `benchmarks/models/*` |
| 可量化评测 | 指标计算脚本 + 运行上下文记录 + 报告生成器 | `reports/<model>_<scenario>_<ts>.json` |

## 2. 实体与数据契约（Canonical Entities）
所有实体统一遵循：`id`（全局唯一 snake_case）、`version`（semver 或 snapshot_ts）、`source_refs[]`（包含 url, collected_at, verified_by, verification_state），并保持 JSON Schema（位于 `templates/`）。

| 实体 | 主键 | 关键字段（增量补充） | 关系 | 典型来源 |
|------|------|---------------------|------|----------|
| Model | model_id | model_name, provider, input_types, output_types, architecture_family, size_params, inference{latency_ms, throughput_rps, memory_gb}, licenses[], tags[] | -> capabilities[], -> benchmarks | 官方文档 / LLM 评测榜 |
| Scenario | scenario_id | name, description, modality_set, risk_level, environment_factors[], required_capabilities[], recommended_agents[] | -> indicators[], -> datasets | 业务域知识 / 车规要求 |
| Indicator | metric_id | name, definition, formula, category, data_requirements, runbook, example_output, limitations | -> scripts/eval/* | 学术论文 / benchmark | 
| Capability | capability_id | name, category(tree), description, input_types, output_types, minimal_requirements | <- models / -> agents | 内部拆解 |
| Agent | agent_id | name, capability_ids[], orchestration_requirements, runtime_stack, example_use_cases[] | -> evaluation_plans | 组合能力设计 |
| Dataset/Baseline | dataset_id | modality, size, license, splits, schema_digest, provenance | -> indicators | 公共数据集 / 内部脱敏 |
| Benchmark Snapshot | benchmark_id + snapshot_ts | leaderboard_type, metrics[], model_entries[] | -> baseline_reference | 官方榜单 / 拉取脚本 |
| Product Line | product_id | owner, features[], production_metrics[] | -> indicators, -> baseline_reference | PRD / 业务链路 |

最小交付（MVP）需支持：Model / Scenario / Indicator / Benchmark Snapshot 四类实体的读取 & 关联引用校验。

## 3. 阶段化路线（Phased Roadmap）

### Phase 0 规范引导 & 引导脚手架
目标：建立最小 JSON Schema 与验证脚本扩展点；接入 QA 日志工具。 
产出：`templates/*` 差异补全说明、`scripts/validate_*.py` 扩展列表、增量校验报告格式。
验收：新增一个模型与一个场景条目 → 校验通过（<30s）。

### Phase 1 分类与采集基座 (Taxonomy & Harvest)
能力：
1. 多源情报聚合（arXiv / HuggingFace / 官方页面快照）本地化缓存（避免网络不稳定）。
2. 分类法（模型/场景/能力）版本化（`taxonomy_versions/<date>.json`）。
3. 变更审计：标签新增 / 重命名 / 合并生成 diff 报告。
验收：覆盖 >= 95% 现有模型目录；新增模型分类 ≤ 2 人工小时。

### Phase 2 指标矩阵与基线对接 (Metrics & Baselines)
能力：
1. 指标条目→脚本映射（指标 JSON 中 `run_script_ref` 指向 `scripts/eval/<metric>.py`）。
2. Benchmark 拉取器（含 `lmarena_pull`、未来扩展 `chatbot_arena_pull`、`opencompass_pull`）。
3. 基线快照对比（同一模型/指标新旧差异 + 阈值报警）。
验收：指定 1 模型 × 1 场景自动生成差异摘要（含 top N 指标变动 > 阈值）。

### Phase 3 评测编排 MVP (Evaluation Orchestrator MVP)
能力：
1. 输入：`--model_id` + `--scenario_id` → 解析所需 `indicators` + `datasets`。
2. 运行：调用指标脚本（串/并行策略 + seed 固定），记录运行上下文（硬件、依赖、git commit）。
3. 输出：结构化报告 JSON + 摘要 Markdown（差距建议 = 与最近基线对比）。
验收：端到端时长 ≤ 1 小时（含数据准备假设已缓存）。

### Phase 4 智能体增强 (Agentic Augmentation)
新增 Agents：
- Retrieval Synthesizer：基于现有实体 + QA 历史生成回答并附引用（top-k source_refs）。
- Evaluation Planner：根据场景风险等级选择增强指标（例如安全性场景自动加入 `toxicity` / `robustness_adv`）。
- Gap Analyzer：对比产品线 `target_value` 与最新报告生成整改建议（降维优先级列表）。
验收：输入自然语言问题（如："某模型在驾驶辅助场景延迟表现如何？"）→ 输出含引用编号回答。

### Phase 5 运维治理 (Governance & Evolution)
能力：基线刷新策略（季度 / 事件触发） + 指标弃用流程（deprecation_state） + 风险审计（缺失来源、可疑数值）。
验收：治理报告自动生成（含：待验证条目、近期 schema 变更、指标弃用列表）。

## 4. 功能需求分层（Functional Breakdown）
1. 数据采集层：拉取/解析/缓存 → 统一 Source Reference 结构。 
2. 语义对齐层：分类法应用 + 重复检测（基于名称/参数/模态特征指纹）。
3. 校验与合规：Schema 校验、引用完整性、数值范围（延迟/吞吐异常检测）。
4. 指标执行层：指标 → 运行脚本映射 + 运行缓存（避免重复计算）。
5. 报告与对比：基线差异、回归风险、产品线影响。
6. QA / 智能回答：检索 + 策略 + 引用链路。
7. 版本 & 审计：所有实体变更写入 `logs/entity_change.jsonl`。

## 5. 非功能要求（Non-Functional Requirements）
| 维度 | 目标 | 说明 |
|------|------|------|
| 可追溯性 | 100% 实体带来源与时间戳 | 无来源条目拒绝进入主目录 |
| 可复现性 | 评测报告含环境指纹 | hash(依赖版本+脚本+数据集清单) |
| 扩展性 | 新增指标脚本无需改核心框架 | 通过 `run_script_ref` 自注册 |
| 性能 | 单指标计算任务调度开销 < 2s | 轻量调度层，不包裹重推理 |
| 审计 | 变更 diff T+0 输出 | 每次合并后生成报告 |
| 安全/合规 | 内部数据集标记敏感级别 | 访问前检查标签 `sensitivity` |

## 6. 智能体角色设计（Agent Roles）
| Agent | 触发方式 | 输入 | 输出 | 核心算法/依赖 |
|-------|----------|------|------|---------------|
| IngestionAgent | 命令行 / 定时 | source_list | 原始快照 + 标准化条目草稿 | 正则 + HTML parser + 简单 NLP 去重 |
| TaxonomyCuratorAgent | 人工交互 | 新增/冲突条目 | 标签建议 + 冲突报告 | 相似度 (embedding) |
| MetricAdvisorAgent | model_id + scenario_id | 指标集合建议 | 指标优先级列表 | 场景风险矩阵规则 |
| EvalPlannerAgent | model_id + scenario_id | 执行 DAG | 依赖解析 + 资源估算 | Heuristic + 简单拓扑排序 |
| ReportSynthesizerAgent | run_results | Markdown 摘要 | 结构化 diff + 建议 | 指标差值阈值策略 |
| QARetrievalAgent | question | 答案 + 引用 | Top-k 检索 + 模板化回答 | 向量检索（可后置） |
| GapAnalyzerAgent | product_id | 影响报告 | 受影响 features 列表 | 指标→产品线反向索引 |

最小实现（Phase 3 前）只需：IngestionAgent（脚本化）、EvalPlannerAgent（简化规则）、ReportSynthesizerAgent（diff 模板）。

## 7. 指标编排契约（Evaluation Contract）
输入参数：`model_id`, `scenario_id`, `metrics_override[]?`, `seed`, `output_dir`。
流程：
1. 解析场景 → 取得 `required_capabilities` → 映射默认指标集合。
2. 加载模型条目 → 读取 baseline 引用（若存在）。
3. 生成执行计划（顺序 / 并行组）。
4. 执行并记录：每个指标生成 `result_item`（metric_id, value, ci, raw_artifact_ref, runtime_context_hash）。
5. 生成对比：baseline_value, delta, delta_pct, status(OK|WARN|REGRESSION)。
6. 输出：`report.json` + `summary.md`。

错误模式与处理：
| 场景 | 策略 |
|------|------|
| 指标脚本缺失 | 标记 `status=SKIPPED` 并在 summary 中汇总 |
| 数据集引用不存在 | 中止并输出 `missing_dataset` 列表 |
| 值超范围（如负延迟） | 标记异常，进入审计日志 |
| Baseline 缺失 | 只输出当前值并提示建立基线 |

## 8. 成功度量（Project Success Metrics）
| 指标 | 定义 | 目标 (Phase 3) | 目标 (Phase 5) |
|------|------|---------------|---------------|
| 分类覆盖率 | (已分类模型 / 目标列表) | ≥95% | ≥98% |
| 单次评测总耗时 | 启动→报告 | ≤60 min | ≤30 min |
| 指标脚本复用率 | 复用指标 / 总调用 | ≥70% | ≥85% |
| 回归发现平均时延 | 新基线→影响报告 | ≤1 天 | ≤4 小时 |
| QA 回复引用完整率 | 含 >=1 source_ref | ≥90% | ≥98% |

## 9. 目录与文件建议（增量）
```
agents-toolchain/
    ingestion/
        fetch_models.py
        fetch_benchmarks.py
    orchestration/
        plan_eval.py
        run_eval.py
    reporting/
        synthesize_report.py
    governance/
        diff_taxonomy.py
logs/
    entity_change.jsonl
    eval_runs.jsonl
taxonomy_versions/
    taxonomy_v1.0.json
reports/
    <model>_<scenario>_<ts>/report.json
```

（当前可先用 README 中现有脚本结构，逐步补齐上述子目录，不强制一次成型。）

## 10. 渐进 Backlog（首批 10 条）
1. 扩展 `validate_models.py` → 支持 capability / benchmark 引用校验。
2. 新增 `scripts/bench/lmarena_pull.py`（已在指南内列出）并生成快照示例。
3. 生成 `taxonomy_versions/taxonomy_seed.json`（聚合现有模型输入/输出模态与能力关键词）。
4. 指标模板补字段：`run_script_ref`, `limitations`, `example_output_ref`。
5. 添加 `scripts/eval/latency_p99.py` & `scripts/eval/f1.py` 统一输出结构（value, ci, samples_used）。
6. 设计 `reports/report_schema.json` 并给出示例。
7. 实现最小 `plan_eval.py`（解析 scenario -> metrics 列表）。
8. 实现 `synthesize_report.py`（合并运行结果 + baseline diff）。
9. QA 工具扩展：支持 `--refs metric_id=...,model_id=...` 自动追加引用元数据。
10. 生成首个端到端演示（手动 mock 一个模型与场景评测）。

## 11. 风险与缓解策略（Updated）
| 风险 | 影响 | 缓解 |
|------|------|------|
| 分类漂移（标签膨胀） | 查询噪声 | 设定标签注册流程 + 冻结主分类版本 |
| Benchmark 页面结构变化 | 拉取失败 | 提供本地快照回退 + 解析层隔离 |
| 指标脚本输出不一致 | 聚合失败 | 统一 `result_item` schema + 校验器 |
| 数据敏感泄露 | 合规风险 | 所有内部数据集要求 `sensitivity` 标签 + 访问前检查 |
| 评测耗时长 | 无法达成 1h 目标 | 预缓存数据 + 并行调度 + 轻量化指标优先级 |
| 维护成本高 | 项目放缓 | 治理报告 + 弃用流程 + 脚本注释模板 |

## 12. 下一步（Actionable Next Steps）
立即可执行：
1. 在 `templates/indicator_template.json` 中加入 `run_script_ref` 字段。
2. 新增 `reports/README.md` 描述报告结构与示例。
3. 起草 `taxonomy_versions/taxonomy_seed.json`（模型输入/输出+能力）。

---
本文件将作为后续 `agents-toolchain` 目录扩展与脚本开发的需求基线（Baseline v1）。新增阶段或角色请按“变更说明 + 影响分析 + 验收标准”格式提交。