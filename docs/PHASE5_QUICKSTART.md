# Phase 5 运维治理（Governance & Evolution）

本阶段目标：建立可执行的治理与演进机制，确保模型目录、指标库、分类法与文档的持续一致性、可追踪性与可审计性。

## 快速开始

- 运行聚合治理检查（生成报告）：
  - `python scripts/governance/run_phase5_checks.py --report`

- 仅校验模型 Schema：
  - `python agents-toolchain/governance/validate_models_cli.py --report`

- 生成/更新分类法快照：
  - `python agents-toolchain/governance/build_taxonomy.py`

- 对比两个分类法快照并生成差异报告：
  - `python agents-toolchain/governance/diff_taxonomy.py taxonomy_versions/taxonomy_20250101.json taxonomy_versions/taxonomy_20250201.json --out reports`

## 角色与职责（建议）

- 指标与基准维护者（Indicators/Benchmarks Maintainers）：负责 `indicators/` 与 `benchmarks/` 的新增与变更评审，确保与产品线、模型能力对齐。
- 模型目录维护者（Models Maintainers）：负责 `models/` 的元数据完整性、命名规范和版本演进。
- 平台与工具维护者（Platforms/Tools Maintainers）：负责运行脚本、CI 集成、敏感信息扫描与自动化报告归档。

## 变更与版本治理

- 版本策略：建议对模型家族使用语义版本或日期版本（示例：`YYYY.MM`），对分类法快照采用日期版本（`taxonomy_YYYYMMDD.json`）。
- 弃用策略：
  - 标记：在文档与模型条目备注 `notes` 中标记 deprecate 计划与替代项。
  - 宽限期：至少一个小版本周期或 30 天。
  - 清理：在宽限期后移除并在 `reports/` 中保留变更记录。

## 自动化检查清单

- Schema 校验：`scripts/validate_models.py`（由 `validate_models_cli.py` 封装）
- 分类法覆盖率：`agents-toolchain/governance/check_coverage.py --threshold 0.95`
- 敏感信息扫描：`python tools/check_sensitive.py`
- 归属与所有权校验：`python scripts/governance/validate_ownership.py`

## 报告与审计产物

- 校验报告：`reports/validation_<ts>/`（summary 与日志）
- 分类法快照：`taxonomy_versions/taxonomy_YYYYMMDD.json`
- 分类法审计：`reports/taxonomy_audit_<ts>.md`、`logs/entity_change.jsonl`
- 所有权校验：`reports/governance_<ts>/ownership_summary.md`

## CI/CD 建议

- 在 CI 中执行：
  - `python scripts/governance/run_phase5_checks.py --report --threshold 0.95`
  - 失败时阻断合并；报告工件作为构建产物保留。

