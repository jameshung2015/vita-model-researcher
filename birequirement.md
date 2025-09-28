好的！下面是一份**可以直接给 Codex/Copilot 执行的实现需求说明**（含目录、接口、DDL、脚本骨架、验收标准），面向你的仓库 **vita-model-researcher**，采用**Postgres-only（文件 → Postgres/DuckDB 分析表 → Metabase → LangChain NL2SQL）**。默认以 **PostgreSQL** 为主，**DuckDB** 为可选扩展；不使用 MongoDB。

---

# 项目目标

把 `vita-model-researcher` 产生的评测数据（仓库内文件：`models/*.json`、`indicators/*.json`、`scenarios/**/scn_*.json`、`reports/**` 下的统一输出 unified_v1）同步到 **PostgreSQL** 的“分析友好表”，在 **Metabase** 做仪表盘；并提供一个 **LangChain FastAPI Agent** 将自然语言转换为 SQL（查询 Postgres）以返回结果（表格 + 结论）。不依赖 MongoDB。

---

# 一、目录与组件

在现有仓库根目录下新增：

```
/infra/
  docker-compose.bi.yml
  metabase.env.example
  postgres-init/
    01_schema.sql
    02_materialized_views.sql

/bi_etl/
  extract_runs.py
  extract_common.py
  settings.py
  requirements.txt
  README.md
  tests/
    test_extract_runs.py
    fixtures/
      sample_runs.json

/bi_agent/
  app.py
  prompt.py
  db.py
  requirements.txt
  README.md

/bi_docs/
  metabase_dashboards.md
  nl2sql_examples.md

Makefile
```

> 说明：
>
> * `infra/`: 一键起服务（Postgres、Metabase、Agent），以及 Postgres 初始化 SQL。
> * `bi_etl/`: 从仓库文件读取 JSON（models/、indicators/、scenarios/、reports），展平写入 Postgres（或 DuckDB）。
> * `bi_agent/`: LangChain + FastAPI，自然语言问答（SQL）。
> * `bi_docs/`: 使用手册与示例。
> * 维持你原有目录（如 `scripts/`, `agents-toolchain/`, `benchmarks/`），本需求不破坏现有结构。

---

# 二、环境变量（.env）

在仓库根创建 `.env`（不要提交）：

```
# Postgres
PG_HOST=postgres
PG_PORT=5432
PG_DB=vita_bi
PG_USER=vita
PG_PASSWORD=vita_pwd

# Metabase
MB_JETTY_PORT=3000

# Agent
AGENT_PORT=8088

# Optional: DuckDB path（如果启用）
DUCKDB_PATH=/workspace/vita_bi.duckdb
```

---

# 三、PostgreSQL 表结构（DDL）

`/infra/postgres-init/01_schema.sql`：

```sql
CREATE SCHEMA IF NOT EXISTS bi;

-- 维表：模型
CREATE TABLE IF NOT EXISTS bi.models (
  id TEXT PRIMARY KEY,              -- 使用 models/*.json 的 model_name 作为主键
  name TEXT,                        -- 可与 id 相同或短描述
  family TEXT,                      -- 映射 architecture_family
  vendor TEXT,                      -- 映射 provenance.provider
  params JSONB,                     -- variants/size/capabilities 等完整 JSON
  tags TEXT[],
  owner TEXT,
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ
);

-- 维表：场景（贴合 scenarios/**/scn_*.json 结构）
CREATE TABLE IF NOT EXISTS bi.scenarios (
  id TEXT PRIMARY KEY,              -- scenario_id
  name TEXT,
  description TEXT,
  required_atomic_capabilities JSONB,
  recommended_agents JSONB,
  priority_indicators JSONB,
  minimal_test_cases JSONB,
  extra JSONB,                      -- 兼容将来新增字段
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ
);

-- 维表：指标（来自 indicators/*.json）
CREATE TABLE IF NOT EXISTS bi.indicators (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  category TEXT,
  unit TEXT,
  higher_is_better BOOLEAN,
  source TEXT,
  owner TEXT,
  aliases TEXT[]                    -- 指标别名，如 toxicity_rate -> toxicity
);

-- 核心事实表：将 reports/** 中 unified_v1 项展平为“行”（Postgres-only，文件来源）
CREATE TABLE IF NOT EXISTS bi.runs_flat (
  run_id TEXT,                      -- 如目录名 qwen3_phase3_1758821165
  model_id TEXT REFERENCES bi.models(id),
  scenario_id TEXT REFERENCES bi.scenarios(id),
  indicator_id TEXT REFERENCES bi.indicators(id),
  value DOUBLE PRECISION,
  ci JSONB,                         -- 置信区间（可空），保持灵活
  samples_used INT,
  started_at TIMESTAMPTZ,
  env JSONB,                        -- 统一存放 meta（p50/p90/p99、concurrency、rank、votes、snapshot_ts 等）
  cost JSONB,                       -- 预留（time_s/gpu_hours/usd）
  PRIMARY KEY (run_id, model_id, indicator_id)
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_runs_flat_model ON bi.runs_flat(model_id);
CREATE INDEX IF NOT EXISTS idx_runs_flat_scenario ON bi.runs_flat(scenario_id);
CREATE INDEX IF NOT EXISTS idx_runs_flat_indicator ON bi.runs_flat(indicator_id);
CREATE INDEX IF NOT EXISTS idx_runs_flat_started_at ON bi.runs_flat(started_at);
```

可选物化视图 `/infra/postgres-init/02_materialized_views.sql`：

```sql
-- 模型-场景-指标 最新期快照
CREATE MATERIALIZED VIEW IF NOT EXISTS bi.mv_latest_indicator AS
SELECT DISTINCT ON (model_id, scenario_id, indicator_id)
  model_id, scenario_id, indicator_id, value, started_at
FROM bi.runs_flat
ORDER BY model_id, scenario_id, indicator_id, started_at DESC;

CREATE INDEX IF NOT EXISTS idx_mv_latest_indicator
ON bi.mv_latest_indicator(model_id, scenario_id, indicator_id);
```

---

# 四、Docker Compose（自托管，免费；Postgres-only）

`/infra/docker-compose.bi.yml`：

```yaml
version: "3.9"
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: ${PG_DB}
      POSTGRES_USER: ${PG_USER}
      POSTGRES_PASSWORD: ${PG_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./postgres-init:/docker-entrypoint-initdb.d
    ports: ["5432:5432"]
  metabase:
    image: metabase/metabase:latest
    env_file: ../.env
    environment:
      MB_JETTY_PORT: ${MB_JETTY_PORT}
    ports: ["3000:${MB_JETTY_PORT}"]
    depends_on: [postgres]
  agent:
    build:
      context: ../bi_agent
    env_file: ../.env
    ports: ["8088:${AGENT_PORT}"]
    depends_on: [postgres]
volumes:
  pgdata: {}
```

说明：仓库根已有 `docker-compose.yml`（包含 Mongo/n8n/chatbot）。为避免破坏现有功能，BI 相关环境使用独立的 `infra/docker-compose.bi.yml`，不依赖 Mongo。

`/bi_agent/Dockerfile`：

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

---

# 五、ETL：文件（unified_v1 与元数据）→ Postgres（Python）

`/bi_etl/requirements.txt`：

```
psycopg[binary]==3.2.1
python-dotenv==1.0.1
python-slugify==8.0.4
```

`/bi_etl/settings.py`（读取 `.env`）
`/bi_etl/extract_common.py`：封装连接与 upsert
`/bi_etl/extract_runs.py`（核心逻辑，示例骨架）：

```python
import os, json
from datetime import datetime
from decimal import Decimal
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

PG_CONN   = f"host={os.getenv('PG_HOST')} port={os.getenv('PG_PORT')} dbname={os.getenv('PG_DB')} user={os.getenv('PG_USER')} password={os.getenv('PG_PASSWORD')}"

def as_list(x):
    if x is None: return []
    return x if isinstance(x, list) else [x]

def main():
    with psycopg.connect(PG_CONN) as pg, pg.cursor(row_factory=dict_row) as cur:
        # 1) upsert models: 遍历 models/*.json
        import glob, json
        from pathlib import Path
        ROOT = Path(__file__).resolve().parents[1]
        for mp in glob.glob(str(ROOT / 'models' / '*.json')):
            m = json.loads(Path(mp).read_text(encoding='utf-8'))
            mid = m.get('model_name')
            cur.execute("""
                INSERT INTO bi.models (id,name,family,vendor,params,tags,owner,created_at,updated_at)
                VALUES (%(id)s,%(name)s,%(family)s,%(vendor)s,%(params)s,%(tags)s,%(owner)s,%(created_at)s,%(updated_at)s)
                ON CONFLICT (id) DO UPDATE SET
                  name=EXCLUDED.name, family=EXCLUDED.family, vendor=EXCLUDED.vendor,
                  params=EXCLUDED.params, tags=EXCLUDED.tags, owner=EXCLUDED.owner, updated_at=EXCLUDED.updated_at
            """, {
                "id": mid,
                "name": m.get("short_description") or mid,
                "family": m.get("architecture_family"),
                "vendor": ((m.get("provenance") or {}).get("provider")),
                "params": json.dumps({k: m.get(k) for k in ("variants","size_params","capabilities") if m.get(k) is not None}, ensure_ascii=False),
                "tags": as_list(m.get("tags")),
                "owner": None,
                "created_at": None,
                "updated_at": m.get("updated_at") or datetime.utcnow(),
            })

        # 2) upsert scenarios: 遍历 scenarios/**/scn_*.json
        for sp in glob.glob(str(ROOT / 'scenarios' / '**' / 'scn_*.json'), recursive=True):
            s = json.loads(Path(sp).read_text(encoding='utf-8'))
            cur.execute("""
                INSERT INTO bi.scenarios (id,name,description,required_atomic_capabilities,recommended_agents,priority_indicators,minimal_test_cases,extra,created_at,updated_at)
                VALUES (%(id)s,%(name)s,%(description)s,%(rac)s,%(ra)s,%(pi)s,%(mtc)s,%(extra)s,%(created_at)s,%(updated_at)s)
                ON CONFLICT (id) DO UPDATE SET
                  name=EXCLUDED.name, description=EXCLUDED.description,
                  required_atomic_capabilities=EXCLUDED.required_atomic_capabilities,
                  recommended_agents=EXCLUDED.recommended_agents,
                  priority_indicators=EXCLUDED.priority_indicators,
                  minimal_test_cases=EXCLUDED.minimal_test_cases,
                  extra=EXCLUDED.extra,
                  updated_at=EXCLUDED.updated_at
            """, {
                "id": s.get("scenario_id"),
                "name": s.get("name"),
                "description": s.get("description"),
                "rac": json.dumps(s.get("required_atomic_capabilities")),
                "ra": json.dumps(s.get("recommended_agents")),
                "pi": json.dumps(s.get("priority_indicators")),
                "mtc": json.dumps(s.get("minimal_test_cases")),
                "extra": None,
                "created_at": None,
                "updated_at": s.get("updated_at") or datetime.utcnow(),
            })

        # 3) upsert indicators：遍历 indicators/*.json
        for ip in glob.glob(str(ROOT / 'indicators' / '*.json')):
            ind = json.loads(Path(ip).read_text(encoding='utf-8'))
            cur.execute("""
                INSERT INTO bi.indicators (id,name,category,unit,higher_is_better,source,owner,aliases)
                VALUES (%(id)s,%(name)s,%(category)s,%(unit)s,%(hib)s,%(source)s,%(owner)s,%(aliases)s)
                ON CONFLICT (id) DO UPDATE SET
                  name=EXCLUDED.name, category=EXCLUDED.category, unit=EXCLUDED.unit, higher_is_better=EXCLUDED.higher_is_better,
                  source=EXCLUDED.source, owner=EXCLUDED.owner, aliases=EXCLUDED.aliases
            """, {
                "id": ind.get("id"),
                "name": ind.get("name"),
                "category": ind.get("category"),
                "unit": ind.get("unit"),
                "hib": ind.get("higher_is_better"),
                "source": ind.get("source"),
                "owner": ind.get("owner"),
                "aliases": None,
            })

        # 4) upsert runs_flat：遍历 reports/** 下 unified_v1 产物
        import re
        ts_dir_re = re.compile(r".*_(\d{10})$")
        for dirpath in sorted(Path(ROOT / 'reports').glob('*')):
            if not dirpath.is_dir():
                continue
            run_id = dirpath.name
            m = ts_dir_re.match(run_id)
            started_at = None
            if m:
                try:
                    started_at = datetime.utcfromtimestamp(int(m.group(1)))
                except Exception:
                    started_at = None
            for fp in dirpath.rglob('*.json'):
                try:
                    arr = json.loads(fp.read_text(encoding='utf-8-sig'))
                except Exception:
                    continue
                items = arr if isinstance(arr, list) else [arr]
                for it in items:
                    metric_id = it.get('metric_id')
                    value = it.get('value')
                    meta = it.get('meta') or {}
                    # 解析 model_id：优先 meta.model，否则从文件名 *_Model.json 提取
                    model_id = meta.get('model')
                    if not model_id:
                        stem = fp.stem
                        px = stem.split('_')
                        if len(px) >= 2:
                            model_id = px[-1]
                    payload = {
                        'run_id': run_id,
                        'model_id': model_id,
                        'scenario_id': None,
                        'indicator_id': metric_id,
                        'value': float(value) if value is not None else None,
                        'ci': json.dumps(it.get('ci')) if it.get('ci') is not None else None,
                        'samples_used': it.get('samples_used'),
                        'started_at': started_at,
                        'env': json.dumps(meta, ensure_ascii=False),
                        'cost': None,
                    }
                    cur.execute("""
                        INSERT INTO bi.runs_flat
                        (run_id,model_id,scenario_id,indicator_id,value,ci,samples_used,started_at,env,cost)
                        VALUES (%(run_id)s,%(model_id)s,%(scenario_id)s,%(indicator_id)s,%(value)s,%(ci)s,%(samples_used)s,%(started_at)s,%(env)s,%(cost)s)
                        ON CONFLICT (run_id, model_id, indicator_id) DO UPDATE SET
                          value=EXCLUDED.value, ci=EXCLUDED.ci, samples_used=EXCLUDED.samples_used, started_at=EXCLUDED.started_at,
                          env=EXCLUDED.env, cost=EXCLUDED.cost
                    """, payload)

        pg.commit()

if __name__ == "__main__":
    main()
```

---

# 六、LangChain Agent（NL→SQL）

`/bi_agent/requirements.txt`：

```
fastapi==0.115.0
uvicorn[standard]==0.30.6
langchain==0.2.16
langchain-openai==0.1.22  # 若用本地/开源大模型，替换为相应 provider
SQLAlchemy==2.0.35
psycopg[binary]==3.2.1
python-dotenv==1.0.1
```

`/bi_agent/db.py`：

```python
import os
from sqlalchemy import create_engine, text

PG_URL = f"postgresql+psycopg://{os.getenv('PG_USER')}:{os.getenv('PG_PASSWORD')}@{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/{os.getenv('PG_DB')}"
engine = create_engine(PG_URL, pool_pre_ping=True)
```

`/bi_agent/prompt.py`（限制只查 `bi.models`, `bi.scenarios`, `bi.runs_flat`, `bi.mv_*`）：

```python
SYSTEM_PROMPT = """
You are a SQL assistant for an ML evaluation warehouse.
Only generate PostgreSQL SQL.
Rules:
- Query only schemas/tables: bi.models, bi.scenarios, bi.runs_flat, bi.mv_latest_indicator
- Always add LIMIT 200 unless aggregation makes it unnecessary.
- No DDL/DML. Read-only selects only.
- Prefer GROUP BY + ORDER BY for trends.
- Time column is runs_flat.started_at (timestamptz).
- Indicator column is indicator_id, value is numeric.
- Join keys: runs_flat.model_id = models.id; runs_flat.scenario_id = scenarios.id.
 - Env dimensions live in runs_flat.env (JSONB). Extract with ->> (text) or -> (json).
Return only SQL in one code block.
"""
```

`/bi_agent/app.py`（最小骨架）：

```python
import os
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from sqlalchemy import text
from db import engine
from prompt import SYSTEM_PROMPT

load_dotenv()

# 你可以选择开源模型（如本地 LLM），这里接口留空；如需 OpenAI，把调用换掉即可。
def llm_generate_sql(question: str, schema_hint: str="") -> str:
    # TODO: 接入你选的免费/本地 LLM；拼接 SYSTEM_PROMPT + schema
    # 暂时用一个极简模板（占位）
    return f"SELECT model_id, scenario_id, indicator_id, AVG(value) AS avg_value FROM bi.runs_flat GROUP BY 1,2,3 ORDER BY 4 DESC LIMIT 50;"

class QARequest(BaseModel):
    question: str

app = FastAPI()

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/qa")
def qa(req: QARequest):
    # 可选：动态读取数据库元数据，拼接 schema 提示
    sql = llm_generate_sql(req.question)
    with engine.connect() as conn:
        res = conn.execute(text(sql))
        rows = [dict(r._mapping) for r in res]
    # 也可返回“自然语言结论”（后续增强）
    return {"sql": sql, "rows": rows}
```

---

# 七、Metabase（开源版）配置脚本

`/bi_docs/metabase_dashboards.md`（人手操作步骤）：

1. 访问 `http://localhost:3000`，初始化管理员。
2. 添加数据源：PostgreSQL（`vita_bi`）。
3. 建两个仪表盘：

   * **全局健康**：维度筛选（model、scenario、indicator），图表：时间趋势、热力矩阵（model×scenario）。
   * **回归雷达**：对比最近两期（`started_at` 最大的两期）指标差值，阈值高亮。
4. 设置少量字段语义（时间、类别）与外键（model_id ↔ models.id）。

---

# 八、Makefile（快捷命令）

`Makefile`：

```makefile
export $(shell sed 's/=.*//' .env)

.PHONY: up down etl agent-test

up:
\tdocker compose -f infra/docker-compose.bi.yml up -d --build

down:
\tdocker compose -f infra/docker-compose.bi.yml down -v

etl:
\tpython bi_etl/extract_runs.py

agent-test:
\tcurl -X POST http://localhost:8088/qa -H "Content-Type: application/json" -d '{"question":"show top indicators"}'
```

---

# 九、测试与验收标准（Postgres-only）

**单元测试（ETL）**：`/bi_etl/tests/test_extract_runs.py`

* 用 `fixtures/sample_runs.json` 构造一个 unified_v1 样例数组（含多条 `{metric_id,value,ci,samples_used,meta}`）；
* 跑 `extract_runs.py` 的函数（建议拆函数，便于测试）；
* 断言 `bi.runs_flat` 中每个 unified_v1 项被正确“展平为一行”，类型正确（时间戳/数值/JSONB）。

**集成验收**（手工）：

1. `make up` 启动 Postgres、Metabase、Agent；
2. `python bi_etl/extract_runs.py` 首次抽取成功（无异常，主键冲突走 upsert）；
3. Metabase 能连上 Postgres，看到四张表/视图；
4. 建立“全局健康”仪表盘并渲染；
5. `make agent-test` 返回 SQL 与结果行；
6. 用真实问题测试（写入 `bi_docs/nl2sql_examples.md`）：

   * “过去三次评测中，模型 X 在场景 Y 的 `rouge_l` 趋势如何？”
   * “最近一期，哪 5 个模型在 `long_text_robust` 场景下降幅度最大（vs 上一期）？”

**性能与安全**：

* Agent 只读账号、超时 15s、默认 `LIMIT 200`。
* Postgres 对 `runs_flat` 建索引（model_id、scenario_id、indicator_id、started_at）。
* 物化视图可手动/定时刷新（后续加 cron）。

---

# 十、与现有仓库的衔接点（去 Mongo 化）

* **数据来源**：沿用你现有的评测产出（仓库文件：models/、indicators/、scenarios/、reports/），本方案不改评测脚本；不依赖 Mongo。
* **统一输出**：`bi.runs_flat` 与 `unified_v1` 指标一一对应；若你有“基线对比脚本”，其结果也可写入新的汇总表/视图。
* **CI**：在现有 CI 中新增一个“可选步骤”：当主干合入后触发一次 `bi_etl/extract_runs.py`（本地或带 Postgres 的 CI 服务环境执行）。

---

需要我把上述骨架直接生成成**可运行的初始提交**（包含占位的示例代码和 README）吗？如果你提供一小批真实的 unified_v1 示例（`reports/**`）与典型 `models/`、`scenarios/`、`indicators/` 条目，我可以把 `extract_runs.py` 中的映射（字段名与路径）精确对齐到你的数据。
