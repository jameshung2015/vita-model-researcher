[产品功能概览]
- 指标与评测：标准化指标定义与可执行脚本（`scripts/eval`, `scripts/bench`），统一输出格式（`unified_v1`）。
- 模型规格库：`models/*.json` + `templates/model_schema.json`，支持家族/变体、硬件建议与部署提示。
- 基准目录：`benchmarks/` 记录基准/任务与模型引用，支持快照与报告整合。
- 运维治理：Phase 5 检查（Schema/覆盖率/敏感/所有权）、分类法快照与审计、CI 工作流。
- 工具链：`agents-toolchain/` 提供治理、采集、编排；`tools/` 提供敏感扫描与示例脚本。
- 文档与追踪：`docs/` 快速开始与操作手册；`qa/qa_history.jsonl` 记录典型问答与方案。

[Phase 5 快速入口]
- 文档：`docs/PHASE5_QUICKSTART.md`
- 一键检查：`python scripts/governance/run_phase5_checks.py --report --threshold 0.95`
- CI 工作流：`.github/workflows/phase5.yml`（PR/Push 自动执行）

说明与约定
- 项目编码与平台：优先面向 Windows / PowerShell 环境，文本统一使用 UTF-8（不含 BOM）。
- 目录与格式约定：
  - `indicators/`：指标定义与模板（JSON/YAML），每个指标应包含 id、name、description、implementation（脚本引用或说明）。
  - `models/`：模型规格库（JSON），请遵循 `templates/model_schema.json`。
  - `benchmarks/`：基准目录，包含任务定义、快照与模型引用，建议维护 `benchmarks/index.md`。
  - `product_lines/`：产品线（PRD）到指标的追溯，使用 `templates/product_line*.json` 作为示例。
  - `agents-toolchain/`：治理与编排工具集合，README 包含快速启动与常用命令。
  - `scripts/`：可跑的脚本（评测、基准、校验等），遵循 Python 风格与可复用性。

快速开始（常用命令示例）
- 环境（Windows / PowerShell）：
  - python -m venv .venv; .\.venv\Scripts\Activate.ps1
  - pip install -U pip jsonschema
- 模型 schema 验证：
  - python scripts/validate_models.py
  - 或者：python agents-toolchain/governance/validate_models_cli.py --report
- VRAM 估算（示例）：
  - python scripts/estimate_vram.py --variant Qwen3-8B --seq_len 32768 --precision fp16
- 基准与压力/延迟测试（stub）：
  - python scripts/bench/latency_profiler.py --seed 42
  - python scripts/bench/load_test.py --concurrency 50
- 敏感信息扫描：
  - python tools/check_sensitive.py

实现细节与示例引用
- 指标实现示例：`indicators/accuracy_f1.json` 对应 `scripts/eval/f1.py`，输出遵循 `unified_v1` 格式。
- 统一指标运行器：`scripts/run_indicator.py`，配合 `scripts/bench/normalize_unified.py` 做后处理与汇总。

阶段快速入口
- Phase 2：模型规范检查与覆盖率验证
  - python agents-toolchain/governance/validate_models_cli.py --report
  - 对比基线：python scripts/bench/baseline_diff.py --prev reports/<dir>/baseline.json --curr reports/<dir>/current.json --threshold 0.05
- Phase 3：基准运行与汇总（示例）
  - 参考：`docs/PHASE3_QUICKSTART.md`
  - LM Arena 快照位于 `benchmarks/snapshots/lmarena/`。
  - 常见输出指标（`unified_v1`）：win_rate、elo_rating、latency_p99、throughput_rps、toxicity_rate、accuracy_f1 等。

风格与提交规范
- 文件编码：UTF-8（无 BOM）。
- 配置文件：JSON/YAML 使用 2 空格缩进，键使用 snake_case，并包含 `id`, `name`, `source/owner` 等元信息。
- Python 代码：遵循 PEP8 风格、4 空格缩进，脚本放在 `scripts/` 下。
- 提交与 PR：使用 Conventional Commits 风格（例如 `docs:`, `chore:`, `fix:`, `add:`, `refactor:` 等），PR 描述中包含目的、影响路径与验证输出。

安全与敏感信息
- 请勿将密钥或凭证提交到仓库；在提交前运行：python tools/check_sensitive.py
- 将环境变量与运行时配置放入本地 `.env`（不提交），并在 README 或相应工具文档中记录必要的变量说明。

附：常用入口命令总结
```
python scripts/governance/run_phase5_checks.py --report --threshold 0.95
python agents-toolchain/governance/validate_models_cli.py --report
python scripts/bench/latency_profiler.py --seed 42
```

完成说明：本文件已修正为 UTF-8 编码的中文说明，移除乱码并清晰列出项目结构与常用命令。


