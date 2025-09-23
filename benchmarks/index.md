```markdown
# 基准（Benchmarks）知识库

本目录用于记录常见公开 benchmark（例如 MMLU、GSM8K、BLEU 等）的元信息：指标定义、测试方法/Runbook、数据集来源链接、示例分数与注意事项。目标是为模型评估提供统一引用与快速查阅。

## 现有条目：

### 传统基准
- `mmlu.json` — MMLU（Massive Multitask Language Understanding）
- `gsm8k.json` — GSM8K（Grade School Math 8K）
- `bleu.json` — BLEU（机器翻译质量评估指标）

### 综合评测框架
- `opencompass.json` — OpenCompass 司南评测（上海人工智能实验室）
- `superclue.json` — SuperCLUE 中文大模型综合测评基准
- `modelscope_leaderboard.json` — ModelScope LLM 排行榜

### 指令跟随与人类偏好
- `alpacaeval.json` — AlpacaEval 自动化指令跟随评估
- `chatbot_arena.json` — Chatbot Arena 人类偏好投票平台

### AGI与专业能力
- `agieval.json` — AGI-Eval 人类标准化考试基准

### Agent能力评测
- `agentbench.json` — AgentBench LLM代理能力评测

### AI安全与对齐
- `anthropic_eval_suite.json` — Anthropic 评估套件（安全对齐）

添加条目请遵循 `templates/benchmark_template.json` 的字段规范。

维护提示：
- 所有条目必须包含 `id`, `name`, `source`, `datasets`, `test_method` 和 `example_scores` 字段。
- 对于示例分数，请注明是否为公开论文中报告的值或仓库/跑分复现值。

```
