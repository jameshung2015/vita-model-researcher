# 基准（Benchmarks）索引

用途
- 记录公开基准（如 MMLU、GSM8K、BLEU、AlpacaEval、Chatbot Arena、OpenCompass、SuperCLUE 等）的元信息：指标定义、数据来源、测试方法、示例分数与注意事项。
- 每个条目为独立 JSON，字段规范见 `templates/benchmark_template.json`。

条目（示例）
- `mmlu.json`、`gsm8k.json`、`bleu.json`
- `alpacaeval.json`、`chatbot_arena.json`
- `opencompass.json`、`superclue.json`
- `agentbench.json`、`agieval.json`、`anthropic_eval_suite.json`
- `modelscope_leaderboard.json`
- `musr.json` MuSR (multistep soft reasoning benchmark)
- `bbh.json` BIG-Bench Hard (chain-of-thought reasoning stress test)

维护要求
- 必备字段：`id`、`name`、`source`、`datasets`、`test_method`、`example_scores`。
- 若有外部研究归纳文档，使用 `research_doc` 字段指向 `agents-toolchain/doc-eval-system/*_research.md`。

Snapshots（历史快照）
- LM Arena 快照保存在：`benchmarks/snapshots/lmarena/`。
- 生成（stub）：
  - `python scripts/bench/lmarena_pull.py --models "Qwen3-4B,Qwen3-8B,Qwen3-30B-A3B,Qwen3-235B-A22B" --out benchmarks/snapshots/lmarena/<ts>.json`

- `mecat.json` MECAT（音频理解，Caption/QA；指标：FENSE、BLEU 等）来源：xiaomi-research/mecat
- gemini_eval.json Gemini 公开评测与链接汇总（MMLU/GSM8K/Arena 参考）
