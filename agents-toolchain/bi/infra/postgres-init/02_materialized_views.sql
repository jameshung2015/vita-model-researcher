-- latest snapshot per model/scenario/indicator
CREATE MATERIALIZED VIEW IF NOT EXISTS bi.mv_latest_indicator AS
SELECT DISTINCT ON (model_id, scenario_id, indicator_id)
  model_id, scenario_id, indicator_id, value, started_at
FROM bi.runs_flat
ORDER BY model_id, scenario_id, indicator_id, started_at DESC;

CREATE INDEX IF NOT EXISTS idx_mv_latest_indicator
ON bi.mv_latest_indicator(model_id, scenario_id, indicator_id);

