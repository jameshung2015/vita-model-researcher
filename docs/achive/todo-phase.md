# TODO (Phase 5 Governance)

- [x] CI: 集成一键检查到 PR/Push（.github/workflows/phase5.yml）。
- [x] README: 添加 Phase 5 快速入口与命令。
- [x] 敏感扫描: 忽略 `.venv/**`、`node_modules/**` 以减少噪声（保留 `.env` 检测）。
- [x] 时区修正: 将 `utcnow()` 迁移为 `datetime.now(timezone.utc)`（治理脚本）。
- [ ] OWNERS: 更新 `platforms/governance/OWNERS.json` 为真实联系人与路径覆盖范围。
- [ ] Taxonomy: 每周生成 `taxonomy_versions/taxonomy_YYYYMMDD.json` 并运行审计（`agents-toolchain/governance/audit_changes.py`）。
- [ ] README 徽章（可选）: 添加 CI 状态徽章与治理覆盖率展示。
- [ ] Bench/Index: 在 `benchmarks/index.md` 增加条目所有权映射（如需要）。
