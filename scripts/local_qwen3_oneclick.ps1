Param(
  [switch]$StartMongo = $false,
  [string]$MongoUri = "mongodb://root:example@localhost:27017/?authSource=admin",
  [string]$DbName = "agents_kb",
  [switch]$SkipDeps = $false,
  [switch]$NoChatbot = $false
)

function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Warn($msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Err($msg)  { Write-Host "[ERR ] $msg" -ForegroundColor Red }

$ErrorActionPreference = 'Stop'

# 0) Optionally start Mongo via Docker (local host port 27017)
if ($StartMongo) {
  try {
    Write-Info "Checking Docker..."
    docker version | Out-Null
  } catch {
    Write-Err "Docker not available. Install Docker Desktop or run without -StartMongo to use your own Mongo."
    exit 2
  }
  $existing = $(docker ps -a --filter "name=agents_local_mongo" --format '{{.Names}}')
  if (-not $existing) {
    Write-Info "Launching Mongo container on localhost:27017 (root/example)"
    docker run -d --name agents_local_mongo -p 27017:27017 `
      -e MONGO_INITDB_ROOT_USERNAME=root `
      -e MONGO_INITDB_ROOT_PASSWORD=example mongo:6 | Out-Null
    Start-Sleep -Seconds 3
  } else {
    Write-Info "Starting existing Mongo container 'agents_local_mongo'"
    docker start agents_local_mongo | Out-Null
  }
}

# 1) Python venv + deps
if (-not $SkipDeps) {
  if (-not (Test-Path .venv)) {
    Write-Info "Creating Python venv (.venv)"
    py -3 -m venv .venv
  }
  Write-Info "Activating venv and installing dependencies"
  .\.venv\Scripts\Activate.ps1
  python -m pip install -U pip | Out-Null
  pip install fastapi uvicorn[standard] requests langchain==0.2.14 langchain-core==0.2.36 pymongo | Out-Null
}

# 2) Export env for scripts and chatbot
$env:MONGO_URI = $MongoUri
$env:DB_NAME = $DbName
if (-not $env:N8N_WEBHOOK_URL) { $env:N8N_WEBHOOK_URL = 'http://localhost:5678/webhook/chat_ingest' }
$env:CHATBOT_PORT = '8080'

# 3) Bulk fetch Qwen3 sources
$sources = "agents-toolchain/ingestion/sources/qwen3_series.txt"
if (-not (Test-Path $sources)) {
  Write-Err "Sources file not found: $sources"
  exit 2
}
Write-Info "Running bulk fetch for Qwen3 series"
python agents-toolchain/ingestion/bulk_fetch.py --file $sources

# 4) Optionally start chatbot and open browser
if (-not $NoChatbot) {
  Write-Info "Starting local chatbot on http://localhost:8080/"
  $chatArgs = "agents-toolchain/orchestration/chatbot_api.py"
  Start-Process -FilePath "python" -ArgumentList $chatArgs
  Start-Sleep -Seconds 2
  try { Start-Process "http://localhost:8080/" } catch {}
}

Write-Host "`nDone. Tips:" -ForegroundColor Green
Write-Host " - List recent sources via API: POST http://localhost:8080/chat with payload {`"task`":`"list_sources`",`"limit`":5}" -ForegroundColor Green
Write-Host " - Or use the UI at http://localhost:8080/" -ForegroundColor Green

