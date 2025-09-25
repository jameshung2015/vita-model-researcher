# Phase 1 开发任务（分类与采集基础 — Taxonomy & Harvest）
> 基于 agentToolrequirement.md 的 Phase 1 要求，并结合栈：n8n + LangChain，MongoDB（JSON），Chatbot 同时支持两种 Agent 框架。

## 目标与验收
- [x] 采集与本地化缓存：整合 arXiv / HuggingFace / 官方页面，离线快照入库（Mongo）。
- [x] 分类法版本化：生成 `taxonomy_versions/<date>.json`，覆盖 ≥95% 现有模型目录（按有效模型文件统计）。
- [x] 变更审计：新增/重命名/合并标签的 diff 报告（JSON+MD）。
- [x] 人工分类新增 ≤ 2 小时/模型；提供操作手册与模板（见 `agents-toolchain/governance/MANUAL_CLASSIFICATION.md`）。

## 环境与数据层（MongoDB）
- [x] `.env`：`MONGO_URI`, `DB_NAME=agents_kb`（见 `.env.example`）。
- [x] 集合：`sources_cache`, `taxonomy_versions`, `entity_change_log`, `models_idx`（docker 初始化脚本创建）。
- [x] 建索引：`sources_cache(url,fingerprint[unique])`，`entity_change_log(entity_id, ts)`（见 `docker/mongo-init/01-init.js`）。

## 采集与缓存（n8n + LangChain）
- [x] n8n 工作流：`wf_fetch_sources`（Webhook → HTTP Request → Summarize → Mongo Insert）。
- [x] LangChain Loader：HTML/JSON 解析器，规范化字段（provider, io_modalities, size_params, tags）。
- [x] 去重与指纹：内容指纹 `fingerprint = sha256(url + body)`；Mongo 唯一索引避免重复。

## 分类法版本化（Taxonomy）
- [x] 生成器脚本：`agents-toolchain/governance/build_taxonomy.py`（从 `models/*.json` 汇总）。
- [x] 版本产出：`taxonomy_versions/taxonomy_YYYYMMDD.json`，含 `version`, `categories`, `mappings`。
- [x] 快照对比：`diff_taxonomy.py old new --out reports` 生成 `taxonomy_diff_<ts>.{json,md}`。

## 变更审计与日志
- [x] 追加 `logs/entity_change.jsonl`（预留，供后续脚本写入）。
- [x] 审计规则：重命名/合并/新增触发 diff 项，输出统计与人工复核清单（`agents-toolchain/governance/audit_changes.py`）。

## Chatbot 双框架对接（接口层）
- [x] 统一消息契约：`{session_id, user_query, route: [n8n|langchain], payload}`。
- [x] n8n 路由：`/webhook/chat_ingest`（n8n webhook），将消息转为抓取任务。
- [x] LangChain 路由：`agents-toolchain/orchestration/chains/taxonomy_assistant.py`（最小链）。
- [x] Demo：同一聊天入口可切换两条链路并返回结构化响应（JSON）。

## 校验与脚本
- [x] 扩展 `scripts/validate_models.py`：校验 benchmark 引用；若存在 `required_capabilities[]` 则校验能力 ID。
- [x] 新增 `scripts/ingest/snapshot_export.py`：Mongo → 本地 JSONL 快照（离线可查）。

## 文档与示例
- [x] `agents-toolchain/ingestion/README.md`：工作流结构、环境、失败回退。
- [x] `taxonomy_versions/README.md`：字段定义与发布流程。
- [x] 操作示例：`agents-toolchain/orchestration/README.md` 与本清单中的 PowerShell 示例。

## 里程碑
- [x] M1（采集最小闭环，Mongo 入库，n8n/LC 各完成 1 源）。
- [x] M2（taxonomy 首个版本 + diff 报告）。
- [x] M3（Chatbot 双框架路由 Demo + 文档）。

备注：Phase 1 聚焦“分类与采集”；评测与基线对齐（Phase 2/3）将在后续 PR 中推进。
