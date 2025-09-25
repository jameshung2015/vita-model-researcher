[产品功能概览]
- 指标与评测：标准化指标定义与可执行脚本（scripts/eval, scripts/bench），统一输出格式（unified_v1）。
- 模型规格库：`models/*.json` + `templates/model_schema.json`，支持家族/变体、硬件建议与部署提示。
- 基准目录：`benchmarks/` 记录基准/任务与模型引用，支持快照与报告整合。
- 运维治理：Phase 5 检查（Schema/覆盖率/敏感/所有权）、分类法快照与审计、CI 工作流。
- 工具链：`agents-toolchain/` 提供治理、采集、编排；`tools/` 提供敏感扫描与示例。
- 文档与追踪：`docs/` 快速开始与操作手册；`qa/qa_history.jsonl` 记录典型问答与方案。
[Phase 5 快速入口]
- 文档：docs/PHASE5_QUICKSTART.md
- 一键检查：`python scripts/governance/run_phase5_checks.py --report --threshold 0.95`
- CI 工作流：.github/workflows/phase5.yml（PR/Push 自动执行）
#+ 澶фā鍨嬭瘎浠锋寚鏍囦笌宸ュ叿锛圞nowledge Base锛?
鐩爣
- 寤虹珛鈥滄寚鏍囨睜 + 妯″瀷瑙勬牸 + 鍩哄噯搴?+ 宸ュ叿閾锯€濈殑缁熶竴鐭ヨ瘑搴擄紝鏀寔鍙鐢ㄧ殑鎸囨爣瀹氫箟銆佸彲鎵ц鑴氭湰寮曠敤锛坰cript-ref锛夈€佹ā鍨嬭鏍兼牎楠屼笌鍘嗗彶蹇収杩借釜銆?- 闈㈠悜 Windows/PowerShell 鍙嬪ソ锛岄粯璁や娇鐢?UTF-8锛堟棤 BOM锛夈€?
鐩綍缁撴瀯
- `indicators/` 鎸囨爣姹犱笌妯℃澘锛圝SON/YAML锛夛細瀹氫箟銆乺unbook銆佽剼鏈紩鐢ㄣ€佺ず渚嬭緭鍑恒€?- `models/` 妯″瀷瑙勬牸锛圝SON锛泂chema 瑙?`templates/model_schema.json`锛夈€?- `benchmarks/` 鍩哄噯鐩綍涓庢ā鍨嬪紩鐢紙JSON锛涚储寮曡 `benchmarks/index.md`锛夈€?- `product_lines/` PRD 鈫?鎸囨爣鍙拷韪潯鐩紙妯℃澘瑙?`templates/product_line*.json`锛夈€?- `agents-toolchain/` 娌荤悊銆侀噰闆嗕笌楠岃瘉宸ュ叿锛坬uickstart 瑙佸瓙鐩綍 README锛夈€?- `scripts/` 鍙繍琛岃剼鏈紙璇勬祴銆佸熀鍑嗐€佷及绠楃瓑锛夈€?- `templates/` 瑙勮寖 Schema 涓庤捣濮嬫ā鏉裤€?- `qa/qa_history.jsonl` 杩藉姞寮?QA 鏃ュ織锛堢敱宸ュ叿鍐欏叆锛夈€?
寮€鍙戜笌鏍￠獙锛圥owerShell锛?- 鍒涘缓鐜涓庝緷璧栵細
  - `python -m venv .venv; .\.venv\Scripts\Activate.ps1`
  - `pip install -U pip jsonschema`
- Schema 妫€鏌ワ細
  - `python scripts/validate_models.py`
  - 鎴栧啓鎶ュ憡锛歚python agents-toolchain/governance/validate_models_cli.py --report`
- VRAM 浼扮畻锛堢ず渚嬶級锛?  - `python scripts/estimate_vram.py --variant Qwen3-8B --seq_len 32768 --precision fp16`
- 鍩哄噯涓庡帇鍔涳紙stub锛夛細
  - `python scripts/bench/latency_profiler.py --seed 42`
  - `python scripts/bench/load_test.py --concurrency 50`
- 鏁忔劅淇℃伅鎵弿锛?  - `python tools/check_sensitive.py`

鑴氭湰寮曠敤锛坰cript-ref锛?- 鎸囨爣鏉＄洰鍖呭惈 `run_script_ref`锛岀敤浜庣粺涓€鎵ц锛?  - 渚嬶細`indicators/accuracy_f1.json` 鈫?`scripts/eval/f1.py`锛堣緭鍑烘牸寮?unified_v1锛夈€?  - 宸蹭负鑳滅巼/EL0 缁熶竴杈撳嚭锛歚scripts/run_indicator.py` + `scripts/bench/normalize_unified.py`銆?
Phase 2 Quickstart锛堟ā鍨?鎸囨爣鏍￠獙 + 绀轰緥锛?- 涓€閿牎楠屼笌鎶ュ憡锛?  - `python agents-toolchain/governance/validate_models_cli.py --report`
- 鍩虹嚎瀵规瘮锛堢ず渚嬶級锛?  - `python scripts/bench/baseline_diff.py --prev reports/<dir>/baseline.json --curr reports/<dir>/current.json --threshold 0.05`

Phase 3 Quickstart锛圦wen3 鍏ㄥ彉浣?smoke锛?- 蹇€熷紑濮嬶細瑙?`docs/PHASE3_QUICKSTART.md`銆?- LM Arena 蹇収淇濈暀锛歚benchmarks/snapshots/lmarena/`锛堝巻鍙茶拷韪級銆?- 缁熶竴杈撳嚭锛坲nified_v1锛夋寚鏍囷細win_rate銆乪lo_rating銆乴atency_p99銆乼hroughput_rps銆乼oxicity_rate銆乤ccuracy_f1銆?- Qwen3 鍩虹嚎锛堝綋鍓嶏級锛?  - 鐩綍锛歚reports/baselines/qwen3/1758819673/`
  - 鍚?`baseline.json` 涓?`summary.md`锛屽彲浣滀负鍚庣画 `--prev` 杈撳叆銆?
绾﹀畾涓庡懡鍚?- 鏂囦欢缂栫爜锛歎TF-8锛堟棤 BOM锛夈€?- JSON/YAML锛? 绌烘牸缂╄繘锛泂nake_case 閿紱鍖呭惈 `id`銆乣name`銆乣source/owner`銆?- Python锛歅EP8锛? 绌烘牸缂╄繘锛涜剼鏈潎鏀惧湪 `scripts/`銆?- 鏍囪瘑绗︼細绋冲畾灏忓啓 id锛堝 `pl_autonomous_navigation_v1`锛夈€?
鎻愪氦涓?PR 瑙勮寖
- 绾﹀畾寮忔彁浜ょ被鍨嬶細`docs` `chore` `add` `fix` `refactor` `sync`銆?- PR 鍐呭锛氱洰鐨勪笌鑼冨洿銆佸叧鑱?issue銆佸彈褰卞搷璺緞銆佹牎楠岃緭鍑恒€佸繀瑕佺殑鍓嶅悗瀵规瘮鎴浘/鐗囨銆?
瀹夊叏涓庨厤缃?- 涓嶆彁浜ょ瀵嗘暟鎹紱`.env` 淇濇寔鏈湴銆傛彁浜ゅ墠鎵ц `python tools/check_sensitive.py`銆?- 濡傝剼鏈渶瑕佺幆澧冨彉閲忥紝璇峰湪瀵瑰簲 README 涓褰曘€?

Phase 5 Governance锛堣繍缁存不鐞嗭級
- 蹇€熷紑濮嬶細`docs/PHASE5_QUICKSTART.md`
- 涓€閿鏌ワ細`python scripts/governance/run_phase5_checks.py --report --threshold 0.95`


