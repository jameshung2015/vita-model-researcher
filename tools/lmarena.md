# LM Arena 使用说明

本工具说明面向从 LM Arena 榜单获取指标与提交模型参与评测的需求，配合 `benchmarks/lmarena.json` 与 `indicators/elo_rating.json`、`indicators/win_rate.json` 使用。

- 官网：`https://lmarena.ai/leaderboard`
- 相关：`https://huggingface.co/spaces/lmsys/chatbot-arena-leaderboard`

## 参数与输入
- `--provider` 平台标识，固定为 `lmarena`
- `--models` 逗号分隔模型名（与榜单名称对齐）
- `--out` 输出文件路径（JSON 或 JSONL）
- `--fields` 需要字段，默认 `model,elo,rank,votes,win_rate`
- `--since` 可选，时间过滤（若平台接口支持）

## 结果字段
- `model`：模型名称（与榜单一致）
- `elo`：Elo 评分（数值）
- `rank`：名次（整数）
- `votes`：总投票数（整数，若可得）
- `win_rate`：胜率（0-1 或百分比，按脚本实现）
- `snapshot_ts`：抓取时间戳

## 操作步骤
1) 研究参数与命名对齐：在榜单确认目标模型的显示名称。
2) 结果拉取：运行示例脚本从公开来源抓取字段，落盘到 `qa/` 或 `benchmarks/models/`。
3) 指标计算与对齐：可将 Elo、胜率等映射到 `indicators/` 指标样例中引用。
4) 复现记录：使用 `tools/log_qa.py` 记录问答与拉取命令，保证可追溯。

## 示例命令
- `python scripts/bench/lmarena_pull.py --models "Llama-3-70B-Instruct,GPT-4o" --out benchmarks/models/lmarena_snapshot.json`
- `python tools/log_qa.py --question "拉取LM Arena Elo" --answer "已保存到 benchmarks/models/lmarena_snapshot.json"`

## 提交模型（参考）
- 通过 LMSYS 提交流程提供 API/端点，等待平台排期进入对战。
- 注意：不要提交私密密钥或数据集；遵守平台条款。

## 注意
- 未开放官方API时，脚本使用公开页面数据结构，可能随页面更新而变化。
- 输出格式遵循本仓库 JSON 两空格缩进、snake_case 字段命名。
