## Ingestion on Docker (n8n + MongoDB)

This sets up n8n and MongoDB on Docker Desktop and provides a minimal workflow to cache sources (HTTP → fingerprint → Mongo insert).

### Quick Start
- Copy env template:
  - `cp .env.example .env` (Windows PowerShell: `Copy-Item .env.example .env`)
  - Adjust `MONGO_ROOT_PASSWORD` if needed.
- Start services:
  - `docker compose up -d`
  - n8n UI: `http://localhost:5678/`
  - Scripts connect via: `MONGO_URI=mongodb://root:example@mongodb:27017/?authSource=admin`

### Configure n8n credentials
- n8n → Credentials → MongoDB: host `mongodb`, port `27017`, user `root`, password from `.env`, auth DB `admin`.
- Name it: `Mongo Local`.

### Import workflow
- n8n → Workflows → Import from File → `agents-toolchain/ingestion/n8n/wf_fetch_sources.json`.
- Activate the workflow. Webhook URL is shown in the UI, e.g. `POST http://localhost:5678/webhook/chat_ingest`.

### Workflow Contract
- Request body (JSON): `{ "url": "https://example.com/modelcard" }` or `{ "urls": [ ... ] }`.
- Stores into MongoDB collection `sources_cache` in DB `agents_kb`.
- Fields: `url`, `status`, `content_snippet`, `fetched_at`, `fingerprint` (sha256), `source_len`.

### Batch ingestion options
- Via n8n (webhook): send `{ "urls": ["https://arxiv.org/...", "https://huggingface.co/..."] }` to the same webhook.
- Via script: `python agents-toolchain/ingestion/bulk_fetch.py --file agents-toolchain/ingestion/sources/samples.txt`

### Notes
- n8n uses internal storage (SQLite in the container). MongoDB here is the knowledge-base store.
- The Docker network name `mongodb` lets n8n reach Mongo at `mongodb:27017`.
- For production, enable n8n basic auth (see `docker-compose.yml`) and rotate credentials.
