```markdown
# 基准（Benchmarks）知识库

本目录用于记录常见公开 benchmark（例如 MMLU、GSM8K、BLEU 等）的元信息：指标定义、测试方法/Runbook、数据集来源链接、示例分数与注意事项。目标是为模型评估提供统一引用与快速查阅。

当前条目：

- `mmlu.json` — MMLU（Massive Multitask Language Understanding）
- `gsm8k.json` — GSM8K（Grade School Math 8K）
- `bleu.json` — BLEU（机器翻译质量评估指标）

添加条目请遵循 `templates/benchmark_template.json` 的字段规范。

维护提示：
- 所有条目必须包含 `id`, `name`, `source`, `datasets`, `test_method` 和 `example_scores` 字段。
- 对于示例分数，请注明是否为公开论文中报告的值或仓库/跑分复现值。

```
