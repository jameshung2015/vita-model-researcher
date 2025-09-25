## Chatbot Router (LangChain + n8n)

Runs a small FastAPI service that accepts chat requests and routes them to either an n8n workflow (webhook) or a lightweight LangChain chain.

### Endpoints
- `POST /chat`
  - Body: `{ "session_id": "s1", "user_query": "build taxonomy", "route": "langchain" }`
  - Or: `{ "session_id": "s1", "user_query": "https://example.com", "route": "n8n", "payload": {"url": "https://..."} }`

### Run (Docker)
- After `docker compose up -d`, the router is available at `http://localhost:${CHATBOT_PORT}` (default 8080).

### Examples (PowerShell)
- LangChain assistant (hint-only):
  `Invoke-RestMethod -Method Post -Uri http://localhost:8080/chat -Body (@{ session_id='s1'; user_query='build taxonomy snapshot'; route='langchain' } | ConvertTo-Json) -ContentType 'application/json'`
- LangChain loader (normalize URL):
  `Invoke-RestMethod -Method Post -Uri http://localhost:8080/chat -Body (@{ session_id='s1'; user_query='https://example.com'; route='langchain'; payload = @{ task='normalize_url'; url='https://example.com' } } | ConvertTo-Json) -ContentType 'application/json'`
- Build taxonomy via API:
  `Invoke-RestMethod -Method Post -Uri http://localhost:8080/chat -Body (@{ session_id='s1'; user_query='build'; route='langchain'; payload = @{ task='build_taxonomy' } } | ConvertTo-Json) -ContentType 'application/json'`
- Diff taxonomy via API:
  `Invoke-RestMethod -Method Post -Uri http://localhost:8080/chat -Body (@{ session_id='s1'; user_query='diff'; route='langchain'; payload = @{ task='diff_taxonomy'; old='taxonomy_versions/taxonomy_20240101.json'; new='taxonomy_versions/taxonomy_20240201.json' } } | ConvertTo-Json) -ContentType 'application/json'`
- n8n path (enqueue ingestion):
  `Invoke-RestMethod -Method Post -Uri http://localhost:8080/chat -Body (@{ session_id='s1'; user_query='https://example.com/modelcard'; route='n8n' } | ConvertTo-Json) -ContentType 'application/json'`
