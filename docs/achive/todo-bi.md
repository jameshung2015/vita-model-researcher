# TODO

## BI（Postgres-only）
- [x] infra: 新增 `agents-toolchain/bi/infra/docker-compose.bi.yml`（Postgres/Metabase/Agent），与根 `docker-compose.yml` 解耦（不依赖 Mongo/n8n）。
- [x] DDL: 添加 `agents-toolchain/bi/infra/postgres-init/01_schema.sql` 与 `02_materialized_views.sql`。
- [x] ETL: 实现 `agents-toolchain/bi/etl/extract_runs.py`（从 `models/`、`benchmarks/`、`indicators/`、`registration/`、`scenarios/`、`qa/`、`reports/` 落库到 `bi.*`）。
- [x] 指标别名: 实现 `toxicity_rate → toxicity` 基础映射（后续可扩展 aliases 列/表）。
- [x] Agent: `agents-toolchain/bi/agent`（FastAPI 可运行；`runs_flat.env` 为 JSONB）。
- [x] 文档: `agents-toolchain/bi/README.md` 与 `agents-toolchain/bi/dashboards/qa_demo.md`（示意仪表盘 SQL）。
 - [x] Metabase 初始化: 打开 `http://localhost:3000` 完成首次向导（或运行 `python3 agents-toolchain/bi/scripts/setup_metabase.py`）。
 - [x] 仪表盘创建: 运行 `python3 agents-toolchain/bi/scripts/setup_metabase.py` 自动创建 “Vita BI QA Demo” 仪表盘。
 - [x] Makefile（可选）: 在仓库根增加 up/down/etl/agent-test/refresh-mv 等命令。
- [x] 验收（部分完成）: 启服务→跑 ETL（成功）；Agent 运行中；Metabase 仪表盘待创建与验证。
