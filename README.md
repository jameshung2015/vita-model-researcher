#+ 大模型评价指标与工具（Knowledge Base）

目标
- 建立“指标池 + 模型规格 + 基准库 + 工具链”的统一知识库，支持可复用的指标定义、可执行脚本引用（script-ref）、模型规格校验与历史快照追踪。
- 面向 Windows/PowerShell 友好，默认使用 UTF-8（无 BOM）。

目录结构
- `indicators/` 指标池与模板（JSON/YAML）：定义、runbook、脚本引用、示例输出。
- `models/` 模型规格（JSON；schema 见 `templates/model_schema.json`）。
- `benchmarks/` 基准目录与模型引用（JSON；索引见 `benchmarks/index.md`）。
- `product_lines/` PRD → 指标可追踪条目（模板见 `templates/product_line*.json`）。
- `agents-toolchain/` 治理、采集与验证工具（quickstart 见子目录 README）。
- `scripts/` 可运行脚本（评测、基准、估算等）。
- `templates/` 规范 Schema 与起始模板。
- `qa/qa_history.jsonl` 追加式 QA 日志（由工具写入）。

开发与校验（PowerShell）
- 创建环境与依赖：
  - `python -m venv .venv; .\.venv\Scripts\Activate.ps1`
  - `pip install -U pip jsonschema`
- Schema 检查：
  - `python scripts/validate_models.py`
  - 或写报告：`python agents-toolchain/governance/validate_models_cli.py --report`
- VRAM 估算（示例）：
  - `python scripts/estimate_vram.py --variant Qwen3-8B --seq_len 32768 --precision fp16`
- 基准与压力（stub）：
  - `python scripts/bench/latency_profiler.py --seed 42`
  - `python scripts/bench/load_test.py --concurrency 50`
- 敏感信息扫描：
  - `python tools/check_sensitive.py`

脚本引用（script-ref）
- 指标条目包含 `run_script_ref`，用于统一执行：
  - 例：`indicators/accuracy_f1.json` → `scripts/eval/f1.py`（输出格式 unified_v1）。
  - 已为胜率/EL0 统一输出：`scripts/run_indicator.py` + `scripts/bench/normalize_unified.py`。

Phase 2 Quickstart（模型/指标校验 + 示例）
- 一键校验与报告：
  - `python agents-toolchain/governance/validate_models_cli.py --report`
- 基线对比（示例）：
  - `python scripts/bench/baseline_diff.py --prev reports/<dir>/baseline.json --curr reports/<dir>/current.json --threshold 0.05`

Phase 3 Quickstart（Qwen3 全变体 smoke）
- 快速开始：见 `docs/PHASE3_QUICKSTART.md`。
- LM Arena 快照保留：`benchmarks/snapshots/lmarena/`（历史追踪）。
- 统一输出（unified_v1）指标：win_rate、elo_rating、latency_p99、throughput_rps、toxicity_rate、accuracy_f1。
- Qwen3 基线（当前）：
  - 目录：`reports/baselines/qwen3/1758819673/`
  - 含 `baseline.json` 与 `summary.md`，可作为后续 `--prev` 输入。

约定与命名
- 文件编码：UTF-8（无 BOM）。
- JSON/YAML：2 空格缩进；snake_case 键；包含 `id`、`name`、`source/owner`。
- Python：PEP8，4 空格缩进；脚本均放在 `scripts/`。
- 标识符：稳定小写 id（如 `pl_autonomous_navigation_v1`）。

提交与 PR 规范
- 约定式提交类型：`docs` `chore` `add` `fix` `refactor` `sync`。
- PR 内容：目的与范围、关联 issue、受影响路径、校验输出、必要的前后对比截图/片段。

安全与配置
- 不提交私密数据；`.env` 保持本地。提交前执行 `python tools/check_sensitive.py`。
- 如脚本需要环境变量，请在对应 README 中记录。

