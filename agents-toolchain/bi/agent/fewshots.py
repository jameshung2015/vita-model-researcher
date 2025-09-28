"""Few-shot NL -> SQL examples to prime the LLM.

Each example is (question, sql). The SQL must follow the same safety
constraints as runtime generation so the model mimics correct style.
"""

FEW_SHOT_EXAMPLES = [
    (
        "列出最近一次各模型 toxicity 指标值 (按值降序, 限制20)",
        """```sql
WITH latest AS (
  SELECT DISTINCT ON (model_id) model_id, value, started_at
  FROM bi.runs_flat
  WHERE indicator_id = 'toxicity'
  ORDER BY model_id, started_at DESC
)
SELECT m.id AS model_id, latest.value, latest.started_at
FROM latest
JOIN bi.models m ON m.id = latest.model_id
ORDER BY latest.value DESC
LIMIT 20;
```""",
    ),
    (
        "过去30天每日报告条目数量",  # count rows per day
        """```sql
SELECT date(started_at) AS day, COUNT(*) AS run_rows
FROM bi.runs_flat
WHERE started_at >= (NOW() - INTERVAL '30 day')
GROUP BY 1
ORDER BY 1;
```""",
    ),
    (
        "Qwen3-8B 模型所有指标的平均值 (按平均值降序, 限制50)",
        """```sql
SELECT indicator_id, AVG(value) AS avg_value, COUNT(*) AS n
FROM bi.runs_flat
WHERE model_id = 'Qwen3-8B'
GROUP BY indicator_id
ORDER BY avg_value DESC
LIMIT 50;
```""",
    ),
    (
        "最近两次每个模型 toxicity 指标的值及差值 (最新-上一次)",
        """```sql
WITH tox AS (
  SELECT model_id, value, started_at,
         ROW_NUMBER() OVER (PARTITION BY model_id ORDER BY started_at DESC) AS rn
  FROM bi.runs_flat
  WHERE indicator_id = 'toxicity'
), pivot AS (
  SELECT model_id,
         MAX(CASE WHEN rn=1 THEN value END) AS latest_value,
         MAX(CASE WHEN rn=2 THEN value END) AS prev_value,
         MAX(CASE WHEN rn=1 THEN started_at END) AS latest_started_at
  FROM tox
  WHERE rn <= 2
  GROUP BY model_id
)
SELECT model_id, latest_value, prev_value, (latest_value - prev_value) AS diff, latest_started_at
FROM pivot
ORDER BY diff DESC NULLS LAST
LIMIT 100;
```""",
    ),
]
