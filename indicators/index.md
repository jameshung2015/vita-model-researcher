# 指标索引

说明
- 指标条目新增 `run_script_ref` 字段，指向可运行的评测脚本及参数，便于自动化执行与追溯。
- 评测脚本默认输出统一结构：`{ metric_id, value, ci, samples_used, meta }`（统一版本 unified_v1）。

本目录包含初始的指标条目（JSON 格式）、对应的 runbook（Markdown）以及样例输入/输出。当前文件一览：

## 现有指标：

### 基础准确率指标
- `accuracy_f1.json` — F1-score（准确率）

### 性能指标  
- `latency_p99.json` — P99 延迟（性能）
- `throughput_rps.json` — 吞吐（RPS）

### 安全性指标
- `toxicity.json` — 输出毒性比例（安全）
- `robustness_adv.json` — 对抗/扰动下的稳健性评估
- `safety_alignment_score.json` — 安全对齐得分

### 人类偏好指标
- `win_rate.json` — 胜率（人类偏好评估）
- `elo_rating.json` — ELO评分（排名系统）

### AGI能力指标
- `human_exam_accuracy.json` — 人类考试准确率
- `multimodal_understanding_score.json` — 多模态理解得分

### Agent能力指标
- `agent_task_completion.json` — Agent任务完成率
