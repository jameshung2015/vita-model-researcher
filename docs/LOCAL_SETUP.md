## 本地运行（Windows 主机直跑 LangChain + Chatbot）

适用场景：不进入容器，直接在宿主机验证采集与路由是否可用。建议仍使用 Docker Desktop 运行 n8n 与 Mongo（供采集与列表查询）。

### 1. 准备环境（PowerShell）
- 创建虚拟环境并安装依赖：
  - `py -3 -m venv .venv`
  - `.\.venv\Scripts\Activate.ps1`
  - `python -m pip install -U pip`
  - `pip install fastapi uvicorn[standard] requests langchain==0.2.14 langchain-core==0.2.36 pymongo`

### 2. 单次验证（仅 LangChain Loader）
- 规范化 Qwen3 GitHub 页面：
  - `python agents-toolchain/ingestion/langchain_loader.py https://github.com/QwenLM/Qwen3`
- 期望输出：包含 `provider`, `io_modalities`, `tags`, `raw` 等字段的 JSON。

### 3. 启动本地 Chatbot（连接 Docker 中的 n8n/Mongo）
- 设置环境变量（根据实际端口与凭据调整）：
  - `$env:N8N_WEBHOOK_URL='http://localhost:5678/webhook/chat_ingest'`
  - `$env:MONGO_URI='mongodb://root:example@localhost:27017/?authSource=admin'`
  - `$env:DB_NAME='agents_kb'`
  - `$env:CHATBOT_PORT='8080'`
- 启动服务：
  - `python agents-toolchain/orchestration/chatbot_api.py`
- 访问与健康检查：
  - 首页 `http://localhost:8080/`
  - 健康 `http://localhost:8080/health`

### 4. 本地调用示例
- LangChain（自动识别 URL 并规范化）：
  - `Invoke-RestMethod -Method Post -Uri http://localhost:8080/chat -Body (@{ session_id='s1'; user_query='https://github.com/QwenLM/Qwen3'; route='langchain' } | ConvertTo-Json) -ContentType 'application/json'`
- LangChain（显式任务）：
  - `Invoke-RestMethod -Method Post -Uri http://localhost:8080/chat -Body (@{ session_id='s1'; route='langchain'; payload = @{ task='normalize_url'; url='https://github.com/QwenLM/Qwen3' } } | ConvertTo-Json) -ContentType 'application/json'`
- 列出最近采集（需先经 n8n 入库）：
  - `Invoke-RestMethod -Method Post -Uri http://localhost:8080/chat -Body (@{ session_id='s1'; route='langchain'; payload = @{ task='list_sources'; search='qwen'; limit=5 } } | ConvertTo-Json) -ContentType 'application/json'`

### 5. 可选：通过 Chatbot → n8n 触发采集
- 在 n8n UI 导入/激活 `agents-toolchain/ingestion/n8n/wf_fetch_sources.json`，并配置 Mongo 凭据（host: `mongodb`, user: `root`, auth DB: `admin`）。
- 触发采集：
  - `Invoke-RestMethod -Method Post -Uri http://localhost:8080/chat -Body (@{ session_id='s1'; user_query='https://huggingface.co/'; route='n8n' } | ConvertTo-Json) -ContentType 'application/json'`

### 故障排查
- Windows 防火墙首次可能弹窗，允许 Python 监听 `8080` 端口。
- 若端口冲突，修改 `$env:CHATBOT_PORT` 并重启。
- 若 `list_sources` 无结果，确认 n8n 工作流已激活、Mongo 凭据正确、`sources_cache` 已有文档。

### 一键脚本（推荐）
- 使用脚本自动完成依赖安装、批量采集，并启动本地 Chatbot：
  - 基本用法（使用本机 Mongo，端口 27017）：
    - `PowerShell -ExecutionPolicy Bypass -File scripts/local_qwen3_oneclick.ps1`
  - 若需要通过 Docker 临时启动本地 Mongo：
    - `PowerShell -ExecutionPolicy Bypass -File scripts/local_qwen3_oneclick.ps1 -StartMongo`
  - 仅采集，不启动 Chatbot：
    - `PowerShell -ExecutionPolicy Bypass -File scripts/local_qwen3_oneclick.ps1 -NoChatbot`
  - 自定义 Mongo：
    - `PowerShell -ExecutionPolicy Bypass -File scripts/local_qwen3_oneclick.ps1 -MongoUri "mongodb://user:pass@localhost:27017/?authSource=admin" -DbName agents_kb`

