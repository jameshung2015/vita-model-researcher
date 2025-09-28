## Makefile: convenience targets for BI toolchain (Postgres / Metabase / Agent)
## Usage (PowerShell): `make up` (if make installed) or run the commands shown in each target manually.

ifndef ENV_FILE
ENV_FILE=.env
endif

export $(shell powershell -NoLogo -NoProfile -Command "Get-Content $(ENV_FILE) 2>$null | Where-Object { $_ -match '^[A-Za-z_][A-Za-z0-9_]*=' } | ForEach-Object { ($_ -split '=',2)[0] }")

BI_COMPOSE=agents-toolchain/bi/infra/docker-compose.bi.yml

.PHONY: up down restart etl refresh-mv agent-test metabase-setup ps logs psql

up:
	docker compose -f $(BI_COMPOSE) up -d --build

down:
	docker compose -f $(BI_COMPOSE) down -v

restart: down up

etl:
	python agents-toolchain/bi/etl/extract_runs.py

refresh-mv:
	docker compose -f $(BI_COMPOSE) exec -T postgres psql -U $$PG_USER -d $$PG_DB -c "REFRESH MATERIALIZED VIEW CONCURRENTLY bi.mv_latest_indicator;" || \
	  docker compose -f $(BI_COMPOSE) exec -T postgres psql -U $$PG_USER -d $$PG_DB -c "REFRESH MATERIALIZED VIEW bi.mv_latest_indicator;"

agent-test:
	@echo Testing NL->SQL agent...
	-curl -s -X POST http://localhost:$$AGENT_PORT/qa -H "Content-Type: application/json" -d '{"question":"top indicators"}' | jq '.'

metabase-setup:
	python agents-toolchain/bi/scripts/setup_metabase.py

ps:
	docker compose -f $(BI_COMPOSE) ps

logs:
	docker compose -f $(BI_COMPOSE) logs --tail=200 -f

psql:
	docker compose -f $(BI_COMPOSE) exec postgres psql -U $$PG_USER -d $$PG_DB
