示意仪表盘：QA 活动与指标总览（基于 Postgres）

包含 4 个卡片，数据源为 `vita_bi`，表：`bi.qa_log`, `bi.runs_flat`, `bi.models`。

1) QA 事件计数（总览）
SQL:
```
SELECT COUNT(*) AS qa_events FROM bi.qa_log;
```
可视化：单值卡（Big Value）。

2) QA 事件按标签分布（Top 10）
SQL:
```
SELECT tag, COUNT(*) AS cnt
FROM (
  SELECT UNNEST(tags) AS tag FROM bi.qa_log WHERE tags IS NOT NULL
) t
GROUP BY tag
ORDER BY cnt DESC
LIMIT 10;
```
可视化：条形图（Bar）。

3) QA 时间序列（按天）
SQL:
```
SELECT to_timestamp(ts)\:\:date AS day, COUNT(*) AS cnt
FROM bi.qa_log
GROUP BY 1
ORDER BY 1;
```
可视化：折线图（Line）。

4) 最近一期模型指标 Top-N（连接 runs_flat）
SQL:
```
WITH latest AS (
  SELECT DISTINCT ON (model_id, indicator_id)
    model_id, indicator_id, value, started_at
  FROM bi.runs_flat
  ORDER BY model_id, indicator_id, started_at DESC
)
SELECT m.id AS model, l.indicator_id, l.value, l.started_at
FROM latest l
JOIN bi.models m ON m.id = l.model_id
ORDER BY l.value DESC
LIMIT 50;
```
可视化：表格，支持筛选 `indicator_id`。

仪表盘布局建议：
- 第一行：卡片(1)、卡片(2)
- 第二行：卡片(3)
- 第三行：卡片(4)

Metabase 配置提示：
- 新增数据源：PostgreSQL（`PG_HOST, PG_PORT, PG_DB`）。
- 将 `bi.qa_log.ts` 标记为时间戳（可使用自定义表达式 `to_timestamp(ts)`）。
- 给 `bi.runs_flat` 设置外键：`model_id -> bi.models.id`。

