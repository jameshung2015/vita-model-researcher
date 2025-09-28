BI (Postgres-only) under agents-toolchain/bi

- Infra: `infra/docker-compose.bi.yml` (Postgres, Metabase, Agent)
- DDL: `infra/postgres-init/*.sql`
- ETL: `etl/extract_runs.py`（调度入口） + `etl/extract_common.py`（具体 upsert 逻辑）+ `etl/settings.py`（连接配置）
- Agent: `agent/` (FastAPI + OpenAI/Ollama 兼容 LLM 的真实 NL->SQL 生成器，含 few-shot 与安全校验)
 - Dashboards: `dashboards/qa_demo.md`（基于 QA 的示意仪表盘 SQL）

Quickstart
1. Copy `agents-toolchain/bi/infra/metabase.env.example` to project root `.env` (or merge variables) and adjust credentials if needed.
2. Start services:
  - `make up` (requires GNU make) or `docker compose -f agents-toolchain/bi/infra/docker-compose.bi.yml up -d --build`
3. Run ETL to load warehouse tables:
  - `make etl`
4. (Optional) Auto create demo dashboard (idempotent):
  - `make metabase-setup`
5. Query NL->SQL agent (示例直接 POST)：
  - `make agent-test` （简单 smoke）
  - PowerShell:
    ```powershell
    $body = @{ question = "列出平均指标最高的10个模型" } | ConvertTo-Json -Compress
    Invoke-RestMethod -Uri http://localhost:8088/qa -Method POST -ContentType "application/json" -Body $body | ConvertTo-Json -Depth 6
    ```
6. Refresh materialized view when needed:
  - `make refresh-mv`

Notes
- The ETL flattens unified_v1 items in `reports/**` into `bi.runs_flat`.
- `runs_flat.env` stores meta as JSONB (use `->>` to extract text fields in SQL).
- Demo Metabase automation script: `scripts/setup_metabase.py` (uses `MB_ADMIN_EMAIL/MB_ADMIN_PASS`).
- Make targets provided in root `Makefile` for convenience (up/down/etl/refresh-mv/agent-test/ps/psql/logs).
- LLM 集成：通过 OpenAI 兼容端点（默认指向 Ollama）。已内置 few-shot 提示与只读 SQL 约束。
- SQL 日志：表 `bi.sql_log` 默认开启（Agent 启动自动确保），可用 `SQL_LOG_ENABLED=0` 关闭，`SQL_LOG_RAW=1` 记录原始 LLM 输出（当前保留钩子）。

Security & Hardening
- Change default `MB_ADMIN_PASS` in production.
- Use a read-only Postgres role for the agent if exposing externally (adjust connection URL in `agent/db.py`).
- Limit queries via prompt instructions; current agent 使用 LLM，但有安全过滤（仅允许 SELECT + `bi.` 前缀表）。
- 通过环境变量切换/配置 LLM：
  - `LLM_BASE_URL` (默认 `http://host.docker.internal:11434/v1`)
  - `LLM_MODEL` (默认 `deepseek-v3.1:671b-cloud`)
  - `LLM_API_KEY` (OpenAI 兼容接口需要非空，Ollama 可占位)
  - `LLM_MODE` 可选 `auto|openai|ollama`（自动先尝试 OpenAI 风格再回退 Ollama 原生 `/api/chat`）。

NL→SQL Agent 说明
------------------
Few-shot 示例见 `agent/fewshots.py`，会与系统提示 & 动态 schema introspection 合并形成最终 messages：
1. system: 规则 & 表列元数据
2. 多组 (user, assistant) few-shot
3. user: 实际问题

安全策略：
- 仅允许首语句以 `SELECT` 开头。
- FROM/JOIN 引用表必须以 `bi.` 开头（CTE 名不算表）。
- 自动补 `LIMIT 200`（若用户查询无 limit 且非纯聚合）。
- 失败或 LLM 不可用时回退到稳定聚合查询。

典型问题示例（中文 / 英文均可）：
- “最近两次每个模型 toxicity 指标变化最大的前5”
- “Top 10 models by average value across all indicators”
- “过去30天每天的指标记录数”

返回 JSON 字段：
- `sql`: 执行的 SQL（或 fallback）
- `rows`: 查询结果
- `llm_model`: 当前模型名
- `debug`: 调试标志（请求体可加 `debug: true` 保留统一接口逻辑）

Gap / TODO 对照（与原始 birequirement）
-------------------------------------
已实现：
- Postgres schema、ETL（models / scenarios / indicators / reports / qa / registration）
- 物化视图 `mv_latest_indicator`
- Metabase 自动化创建仪表盘骨架 + cards（fallback: ordered_cards PUT）
- NL→SQL Agent（真实 LLM、few-shot、安全过滤）
- ETL 模块化拆分（`extract_common.py` / `settings.py`）
- SQL 查询日志落库（`bi.sql_log` 可开关）
- 轻量测试目录 `etl/tests`（基础导入与连接字符串测试）
- CI 工作流 `.github/workflows/bi-ci.yml`（跑 ETL + 行数 sanity + pytest 软失败）
- Makefile 常用命令

未完全实现 / 可补充：
- 独立文档 `bi_docs/nl2sql_examples.md`（demo 查询案例集中化）
- 更完善的单元 / 集成测试（当前仅 smoke）
- DuckDB 可选支持（本地轻量分析）
- 只读数据库专用角色初始化脚本 & agent 使用只读凭据
- 高级安全策略：CTE 解析、列级白名单、正则防注入细化
- SQL 原始输出持久化（raw_output 目前未填充）
- 更完备的 dashboard 布局与指标可视化规范化

后续可以按优先级补齐这些项。
