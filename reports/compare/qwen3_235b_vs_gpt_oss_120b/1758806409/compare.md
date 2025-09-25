# Qwen3‑235B vs GPT‑OSS‑120B 性能对比（示例）

说明
- 指标来源：仓库内 stub 工具（latency_profiler, load_test），用于流程演示与对比格式样例；非真实性能结论。
- 统一输出：unified_v1，汇总见 summary.md。

结论摘要（本次样例）
- 延迟（p99, ms）：GPT‑OSS‑120B 优于 Qwen3‑235B（116.48 vs 124.14）。
- 吞吐（rps @ concurrency=80）：两者持平（430 rps，stub 结果）。

建议
- 在一致硬件/推理栈（vLLM/SGLang/TensorRT‑LLM 等）与一致 prompt/上下文设置下复测。
- 对长上下文/复杂推理场景，建议加入 `win_rate/elo`、鲁棒性与毒性指标，生成同一格式 unified_v1 后合并对比。
