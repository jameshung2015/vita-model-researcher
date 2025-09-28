CREATE SCHEMA IF NOT EXISTS bi;

-- models dimension
CREATE TABLE IF NOT EXISTS bi.models (
  id TEXT PRIMARY KEY,
  name TEXT,
  family TEXT,
  vendor TEXT,
  params JSONB,
  tags TEXT[],
  owner TEXT,
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ
);

-- scenarios dimension (aligned to repository JSON)
CREATE TABLE IF NOT EXISTS bi.scenarios (
  id TEXT PRIMARY KEY,
  name TEXT,
  description TEXT,
  required_atomic_capabilities JSONB,
  recommended_agents JSONB,
  priority_indicators JSONB,
  minimal_test_cases JSONB,
  extra JSONB,
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ
);

-- indicators dimension
CREATE TABLE IF NOT EXISTS bi.indicators (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  category TEXT,
  unit TEXT,
  higher_is_better BOOLEAN,
  source TEXT,
  owner TEXT,
  aliases TEXT[]
);

-- runs fact table: flattened unified_v1 items
CREATE TABLE IF NOT EXISTS bi.runs_flat (
  run_id TEXT,
  model_id TEXT REFERENCES bi.models(id),
  scenario_id TEXT REFERENCES bi.scenarios(id),
  indicator_id TEXT REFERENCES bi.indicators(id),
  value DOUBLE PRECISION,
  ci JSONB,
  samples_used INT,
  started_at TIMESTAMPTZ,
  env JSONB,
  cost JSONB,
  PRIMARY KEY (run_id, model_id, indicator_id)
);

CREATE INDEX IF NOT EXISTS idx_runs_flat_model ON bi.runs_flat(model_id);
CREATE INDEX IF NOT EXISTS idx_runs_flat_scenario ON bi.runs_flat(scenario_id);
CREATE INDEX IF NOT EXISTS idx_runs_flat_indicator ON bi.runs_flat(indicator_id);
CREATE INDEX IF NOT EXISTS idx_runs_flat_started_at ON bi.runs_flat(started_at);

-- benchmarks dimension (metadata)
CREATE TABLE IF NOT EXISTS bi.benchmarks (
  id TEXT PRIMARY KEY,
  name TEXT,
  source TEXT,
  tasks JSONB,
  metrics JSONB,
  models_referenced JSONB,
  description TEXT,
  license TEXT
);

-- qa history (from qa/qa_history.jsonl)
CREATE TABLE IF NOT EXISTS bi.qa_log (
  ts BIGINT,
  phase TEXT,
  q TEXT,
  a TEXT,
  tags TEXT[],
  ref TEXT,
  status TEXT,
  commit_id TEXT,
  paths JSONB,
  PRIMARY KEY (ts, q)
);

-- registration docs index (Markdown in registration/)
CREATE TABLE IF NOT EXISTS bi.registration_docs (
  path TEXT PRIMARY KEY,
  title TEXT,
  category TEXT,
  updated_at TIMESTAMPTZ
);

-- optional sql log table (can be disabled at runtime via SQL_LOG_ENABLED=0)
CREATE TABLE IF NOT EXISTS bi.sql_log (
  id BIGSERIAL PRIMARY KEY,
  ts TIMESTAMPTZ DEFAULT now(),
  question TEXT,
  sql TEXT,
  rows_returned INT,
  llm_model TEXT,
  raw_output TEXT,
  warning TEXT
);
