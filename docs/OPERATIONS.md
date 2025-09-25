## Docker Desktop 快速操作手册（n8n + Mongo + Chatbot）

本手册指导在 Windows 宿主机（Docker Desktop）下启动与使用本仓库的采集与 Chatbot 路由能力。

### 前提
- 已安装 Docker Desktop（Windows）。
- PowerShell 可用（示例命令基于 PowerShell）。

### 启动与检查
1) 初始化与启动
- `Copy-Item .env.example .env`
- 可按需编辑 `.env`（端口、密码）；也可使用默认值。
- `docker compose up -d --build`

2) 访问与健康检查
- n8n UI: `http://localhost:5678/`
- Chatbot 健康: `http://localhost:8080/health`
- Chatbot 前端: `http://localhost:8080/`

### n8n 配置（首次）
- n8n → Credentials → 新建 MongoDB：host `mongodb`，port `27017`，user `root`，password 见 `.env`，auth DB `admin`。
- 导入工作流：`agents-toolchain/ingestion/n8n/wf_fetch_sources.json` 并激活。

### 常用操作
- 通过 Chatbot → n8n 采集单个 URL（页面中 Route 选 n8n，User Query 填 URL）。
- 批量采集（页面 Payload 文本框）：`{"urls":["https://arxiv.org/","https://huggingface.co/"]}`。
- 查看已采集内容（Route 选 langchain，Payload）：`{"task":"list_sources","limit":5}`（可加 `search`）。
- 规范化 URL（langchain 路由）：`{"task":"normalize_url","url":"https://example.com"}`。

### 命令行调用（可选）
- 采集（Python 批量）：
  - `pip install pymongo requests`
  - `$env:MONGO_URI='mongodb://root:example@localhost:27017/?authSource=admin'`
  - `$env:DB_NAME='agents_kb'`
  - `python agents-toolchain/ingestion/bulk_fetch.py --file agents-toolchain/ingestion/sources/samples.txt`
- 导出快照：`python scripts/ingest/snapshot_export.py --collections sources_cache --out snapshots`

故障排查：
- `docker compose logs -f chatbot`、`docker compose logs -f n8n` 查看启动与请求日志。
- Chatbot 与 n8n、Mongo 在容器网络 `agents_net` 互通，宿主通过端口映射访问。

