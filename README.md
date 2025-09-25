# 澶фā鍨嬭瘎浠锋寚鏍囦笌宸ュ叿 鈥?鐮旂┒妗嗘灦

鐩爣
- 寤虹珛涓€涓潰鍚戜骇鍝佸拰鍦烘櫙璁捐鐨勨€滃叏鏅€濆ぇ妯″瀷鑳藉姏涓庤鏍肩煡璇嗗簱锛屾敮鎸佸揩閫熸煡璇笌鏍囩鍖栬瘎浼帮紝渚夸簬鍦ㄨ璁″満鏅垨鍔熻兘鏃惰瀹氭ā鍨嬮渶姹傘€?

鎬讳綋鎬濊矾锛堥珮灞傦級
- 灏嗙爺绌跺垎涓轰袱澶т富浣擄細妯″瀷瑙勬牸涓庢爣鍑嗭紙瑙勬牸KB锛変笌鍦烘櫙鐮旂┒锛堝満鏅疜B锛夈€?
- 姣忎釜涓讳綋鐢卞涓瓙鐭ヨ瘑搴撶粍鎴愶紙鎸囨爣姹犮€佸钩鍙版搷浣滄墜鍐屻€佸妗?鍚堣銆佸師瀛愯兘鍔涗笌Agent娓呭崟銆佹祴璇曞伐鍏锋竻鍗曠瓑锛夈€?
- 浠ヨ〃鏍?缁撴瀯鍖栨枃浠讹紙JSON锛変负涓诲瓨鍌ㄥ崟鍏冿紝閰嶅悎Markdown鏂囨。鐢ㄤ簬璇存槑涓庢搷浣滄寚鍗楋紝纭繚鍙満鍣ㄨВ鏋愪笌浜哄伐缁存姢銆?

甯冨眬涓庣洰褰曞缓璁紙鏈枃浠跺す锛?
- `indicators/` 鈥?鎸囨爣姹犱笌鎸囨爣妯℃澘锛堟寚鏍囧畾涔夈€佹潵婧愩€佺淮鎶ゅ洟闃熴€佸浣曟墽琛屻€佹槸鍚︿粯璐广€佸伐鍏蜂笌浜у嚭绀轰緥锛?
- `models/` 鈥?鎸夎緭鍏?杈撳嚭绫诲瀷缁勭粐鐨勬ā鍨嬭鏍间笌鏍囩锛堜緥濡傦細鏂囨湰->鏂囨湰銆佸浘鍍?>鏂囨湰銆佹枃鏈?>鍥惧儚銆佸妯℃€佷氦浜掔瓑锛?
  - 妯″瀷鏉＄洰瀛楁璇存槑锛堣ˉ鍏咃級
    - `architecture_details`锛氬彲閫夛紝鏂囨湰鎻忚堪妯″瀷鏋舵瀯缁嗚妭锛堜緥濡?MoE銆乤dapter銆乥ackbone 鍙樹綋绛夛級銆?
    - `size_params`锛氬彲閫夛紝瀵?notable variants 涓庢縺娲诲弬鏁扮瓑杩涜鎽樿銆?
    - `inference`锛氬彲閫夛紝鍖呭惈鎺ㄧ悊/閮ㄧ讲鐩稿叧浼扮畻瀛楁锛歚latency_ms`銆乣latency_level`銆乣throughput_rps`銆乣concurrency`銆乣memory_gb`銆乣quantization_friendly`銆乣supported_hardware`銆乣distributed_support`銆乣notes`銆?
- `platforms/` 鈥?璁粌骞冲彴銆佽瘎娴嬪钩鍙般€侀儴缃插钩鍙版搷浣滅煡璇嗗簱锛堟寜鍘傚晢鎴栧钩鍙扮嫭绔嬬淮鎶わ級
- `registration/` 鈥?澶фā鍨嬪妗堛€佸悎瑙勪笌鐩戠瀹炶返鏂囨。锛堝浗瀹?鍦板尯/娴佺▼锛?
- `scenarios/` 鈥?鍦烘櫙鐩綍銆佸満鏅暟鎹鐞嗐€佸満鏅墍闇€鍘熷瓙鑳藉姏涓嶢gent鏄犲皠銆佸満鏅祴璇曡鑼冧笌鏁版嵁鏍蜂緥
- `tools/` 鈥?璇勬祴宸ュ叿鎿嶄綔鎵嬪唽涓庤寖渚嬨€佸疄杞?鍙版灦娴嬭瘯宸ュ叿鍒楄〃涓庝娇鐢ㄦ寚鍗?
- `product_lines/` 鈥?骞跺湪鏉＄洰涓紩鐢?`models/` 涓殑 瑙ｅ喅浠?PRD 鍒伴噺浜ф祴璇曢獙璇佺殑杩借釜闂锛屾湰浠撳簱寮曞叆 `product_lines/` 妯″潡锛岀洰鏍囨槸鎶婁骇鍝侀渶姹傦紙PRD锛変腑鐨?feature 涓庣煡璇嗗簱涓殑鍘熷瓙鑳藉姏銆佽瘎娴嬪熀绾垮拰鐢熶骇鎸囨爣寤虹珛鍙拷婧殑閾捐矾銆備富瑕佺敤閫旓細
  - 瀵归綈锛氭妸 PRD 閲岀殑 acceptance criteria 鑷姩鏄犲皠鍒板彲娴嬮噺鐨?production metrics锛堜粠 `indicators/` 閫夋嫨鎴栬嚜瀹氫箟锛夈€?
  - 鍥炲綊锛氭瘡娆″熀绾?benchmark 鏇存柊鍚庤兘蹇€熷畾浣嶅彈褰卞搷鐨勪骇鍝佺嚎涓?feature锛屼粠鑰岃Е鍙戝洖褰掓祴璇曟垨鍛婅銆?
  - 楠屾敹锛氫綔涓?PM/QA 涓庣爺鍙戝叡鍚岀殑楠屾敹鍗曪紙鍖呭惈纭欢/妗嗘灦/鎵规绛?measurement_context锛夛紝渚夸簬閲忎骇楠岃瘉涓庡悎瑙勮褰曘€?
- `templates/` 鈥?JSON妯℃澘锛岀敤浜庡悗缁壒閲忓～鍏呬笌鑷姩鍖栧鐞?
快速上手（Docker + Chatbot + n8n + Mongo）
- 前置：安装 Docker Desktop（Windows）。
- 启动：
  - Copy-Item .env.example .env
  - docker compose up -d --build
- 访问：
  - n8n UI http://localhost:5678/（首次在 Credentials 配置 Mongo：host mongodb，user oot，auth DB dmin）
  - Chatbot UI http://localhost:8080/（首页可直接调用 /chat）
- 采集与查看：
  - Chatbot 页面 Route=n8n，User Query 填 URL 触发采集；
  - Route=langchain，Payload { "task": "list_sources", "limit": 5 } 查看最近采集数据。
- 详见：docs/OPERATIONS.md（包含批量采集与命令行用法）。- `README.md`, `TODO.md` 鈥?椤圭洰璇存槑涓庝换鍔℃竻鍗曪紙褰撳墠鏂囦欢锛?

QA 鏃ュ織
- 鏈粨搴撴彁渚涚畝鍗曠殑 QA 璁板綍宸ュ叿锛屽皢鎻愰棶涓庡洖绛旇拷鍔犲埌 `qa/qa_history.jsonl`锛圝SONL 鏍煎紡锛孶TC 鏃堕棿鎴筹級锛屼究浜庣疮绉巻鍙查棶绛斿苟杩涜鍚庣画绱㈠紩鎴栧鍑恒€?


鏁版嵁濂戠害锛圖ata Contract锛夎鐐癸細
- `product_id`锛氬瓧绗︿覆锛屼紒涓氬唴閮ㄥ敮涓€ id锛堜緥濡傦細`pl_autonomous_navigation_v1`锛夈€?
- `features[]`锛氭瘡涓?feature 鍖呭惈 `feature_id`,`required_capabilities`锛堝紩鐢?`templates/abilities.json` 鐨?id 鍒楄〃锛夈€乣acceptance_criteria`锛圥RD 绾у埆鐨勯獙鏀舵潯鐩級涓?`production_metrics`銆?
- `production_metrics`锛氭瘡鏉″寘鍚?`metric_id`锛堝弬鐓?`indicators/`锛夛紝`target_value`锛宍tolerance`锛屼互鍙?`measurement_context`锛堢‖浠躲€乫ramework銆乥atch_size銆佹祴璇曡剼鏈?寮曠敤锛夛紝骞跺彲鍖呭惈 `baseline_reference` 鎸囧悜 `benchmarks/` 鎴?`benchmarks/models/...` 鐨勫熀绾?JSON 鏉＄洰銆?
- `templates/product_line_schema.json`锛歅roduct Line 鐨?JSON Schema锛堝繀濉瓧娈碉細`product_id`,`name`,`owner`,`features[]`锛夈€?
- `templates/product_line.json`锛氱ず渚嬫ā鏉匡紝灞曠ず濡備綍濉啓 feature -> metric 鐨勬槧灏勩€傚鍒?`templates/product_line.json` 鍒?`product_lines/<product_id>.json`锛屽～鍐欏瓧娈靛苟鍦?PR 涓彁浜ゃ€?


CI 涓庢牎楠屽缓璁細
- 鍦ㄤ粨搴?CI锛堜緥濡?GitHub Actions锛変腑鍔犲叆涓€涓?job锛?
  1) `schema-check`锛氫娇鐢?`jsonschema`锛堟垨鍐呯疆鏍￠獙鑴氭湰锛夐獙璇?`product_lines/*.json` 涓?`templates/product_line_schema.json` 鐨勪竴鑷存€с€?
  2) `reference-check`锛氶獙璇?`production_metrics.baseline_reference` 鎸囧悜鐨勬枃浠跺瓨鍦ㄤ笖鏍煎紡姝ｇ‘銆?
  3) `capability-check`锛氶獙璇?feature 鐨?`required_capabilities` 寮曠敤鍦?`templates/abilities.json` 涓瓨鍦ㄣ€?

绀轰緥锛堝揩閫熸祦绋嬶級锛?
1) PM 鍦?PR 涓坊鍔?`product_lines/pl_xxx.json`锛屾弿杩?PRD 瑕佹眰涓庣洰鏍囨寚鏍囷紱
2) CI 杩愯鏍￠獙鑴氭湰骞舵姤鍛婇敊璇垨閬楁紡锛?
3) 缁存姢鍥㈤槦鎴?owner 瀹￠槄骞跺悎骞讹紱
4) 鐮斿彂/QA 鎸?`measurement_context` 杩愯鍩虹嚎娴嬭瘯骞舵妸缁撴灉涓婁紶鍒?`benchmarks/`锛岄殢鍚庤Е鍙戝洖褰?鐩戞帶娴佺▼銆?


鏍稿績鍚堝悓锛坈ontract锛?
- 杈撳叆锛氭ā鍨?鍦烘櫙/骞冲彴 鐨勫厓淇℃伅锛圝SON锛?
- 杈撳嚭锛氬彲鎼滅储鐨勬爣绛鹃泦鍚堬紙鎸夋寚鏍囦笌鍦烘櫙锛夈€佽瘎娴嬫墽琛岃鏄庛€佺ず渚嬩骇鍑?
- 鏁版嵁褰㈡€侊細
  - 鎸囨爣鏉＄洰锛圝SON锛夌ず渚嬪瓧娈碉細id, name, definition, source, owner, cost, tooling, runbook, example_output
  - 妯″瀷鏉＄洰锛圝SON锛夌ず渚嬪瓧娈碉細model_name, input_types, output_types, size_params, architecture_family, license
  - 鍦烘櫙鏉＄洰锛圝SON锛夌ず渚嬪瓧娈碉細scenario_id, name, description, required_atomic_capabilities, recommended_agents, test_data_refs
- 閿欒妯″紡锛氫笉涓€鑷存爣绛俱€佺己澶卞瓧娈点€侀噸澶嶆潯鐩紱闇€鐢–I/楠岃瘉鑴氭湰妫€娴嬪苟鎶ュ憡銆?

瑙勬牸鎷嗚В
1) 鎸囨爣姹狅紙Indicator Pool锛?
  - 鎸囨爣鍒嗙被锛氭€ц兘锛坙atency/throughput锛夈€佸噯纭€э紙F1/EM/ROUGE锛夈€佺ǔ鍋ユ€э紙瀵规姉/娉涘寲锛夈€佸畨鍏紙toxicity銆侀殣绉佹硠闇诧級銆佸榻愶紙鎸囦护閬典粠锛夈€佸妯℃€佽川閲忔寚鏍囩瓑
  - 姣忎釜鎸囨爣璁板綍锛氬畾涔夈€佽绠楁柟寮忋€佹暟鎹姹傘€佽瘎娴嬭剼鏈?宸ュ叿銆佹槸鍚︽敹璐广€佺淮鎶ゅ洟闃熴€佽褰曠ず渚?

2) 瀹氭€ф寚鏍囷紙鏍囩鍖栵級
  - 閮ㄧ讲鎬ц兘锛氭渶浣庣‖浠躲€佹帹鑽愮‖浠躲€佸GPU/CPU/TPU鐨勬敮鎸?
  - 鎺ㄧ悊鑳藉姏锛氬欢杩熺瓑绾с€佸苟鍙戣兘鍔涖€佸垎甯冨紡鎺ㄧ悊鏀寔
  - 妯″瀷瑙勬ā锛氬弬鏁伴噺銆侀噺鍖栧弸濂藉害銆佽缁冩椂闀夸笌鎴愭湰浼拌
  - 妯″瀷鑳藉姏锛氶€氱敤鐞嗚В銆佸璇濄€佹绱€佷唬鐮佺敓鎴愩€佽瑙夌悊瑙ｃ€佸妯℃€佹帹鐞嗙瓑鑳藉姏鏍囩
  - 妯″瀷鏋舵瀯锛歵ransformer鍙樹綋銆乪ncoder-only銆乨ecoder-only銆乪ncoder-decoder銆佸妯℃€佹ā鍧楁弿杩?

鎿嶄綔鎬х煡璇嗗簱锛堟寜绫诲埆鐙珛缁存姢锛?
- 璁粌骞冲彴锛堟寜鍘傚晢锛夛細鑳藉姏璇存槑銆佹敮鎸佺殑妯″瀷绫诲瀷銆佺ず渚嬭缁冩祦绋嬨€佽璐?閰嶉淇℃伅
- 璇勬祴骞冲彴锛堟寜鍘傚晢/宸ュ叿锛夛細濡備綍涓婁紶妯″瀷銆佸浣曡繍琛岃瘎娴嬨€佺ず渚嬫姤鍛婃牸寮?
- 澶фā鍨嬪妗堝悎瑙勶細娉曞姟/鍚堣瑕佹眰娓呭崟銆佸妗堟祦绋嬨€佸父瑙侀棶棰樹笌鍚堣妗堜緥
- 瀹氭€ф寚鏍囪ˉ鍏咃細閮ㄧ讲骞冲彴鏈€浣庣‖浠躲€佽缁冩暟鎹渶浣庤姹傦紙鏍锋湰閲忋€佹爣娉ㄧ被鍨嬶級

鍦烘櫙鐮旂┒锛堟瑕侊級
- 鍦烘櫙鐢扁€滃師瀛愯兘鍔涳紙atomic capabilities锛夆€濅笌鈥淎gent鑳藉姏鈥濈粍鎴愶細
  - 鍘熷瓙鑳藉姏锛氬彲缁勫悎鐨勬渶灏忓姛鑳藉崟鍏冿紙濡傦細鏂囨湰鍒嗙被銆佸疄浣撴娊鍙栥€丱CR銆佽闊宠瘑鍒€佸浘鍍忓垎鍓层€佺煡璇嗘绱級
  - Agent锛氬皝瑁呭涓師瀛愯兘鍔涗笌绛栫暐锛岀洿鎺ュ彲鐢ㄤ簬瑙ｅ喅鐗瑰畾浠诲姟锛堜緥濡傦細瀹㈡湇Agent銆佸啓浣滃姪鐞嗐€佽瑙夋娴婣gent锛?
- 寤鸿缁存姢涓ゅ紶琛細
  - 琛?锛氳兘鍔涙竻鍗曪紙`templates/abilities.json`锛?鈥?id, name, category, description, input_types, output_types, minimal_requirements
  - 琛?锛欰gent娓呭崟锛坄templates/agents.json`锛?鈥?id, name, capability_ids, orchestration_requirements, runtime_requirements, example_use_cases
- 鍦烘櫙鎸囨爣锛氫负姣忎釜鍦烘櫙瀹氫箟蹇呰鎸囨爣鏍囩锛堜粠鎸囨爣姹犻€夊彇锛夛紝骞惰褰曚紭鍏堢骇涓庡彲鎺ュ彈闃堝€?
- 鍦烘櫙娴嬭瘯宸ュ叿锛氬垪鍑哄苟鎻忚堪agent缂栨帓宸ュ叿銆佸満鏅暟鎹鐞嗗伐鍏枫€佸疄杞?鍙版灦娴嬭瘯宸ュ叿锛岀粰鍑烘祴璇曟祦绋嬬ず渚?

璐＄尞鎸囧崡锛堢畝瑕侊級
- 鏂板鎸囨爣鎴栨潯鐩細鍦ㄥ搴旂洰褰曚笅鏂板YAML锛岀劧鍚庢彁浜R锛孋I灏嗚繍琛宻chema鏍￠獙鑴氭湰
- 鏍煎紡涓庡懡鍚嶈鑼冿細浣跨敤UTF-8锛屾棤BOM锛涙枃浠跺悕浣跨敤鑻辨枃鎴栨嫾闊冲苟鍖呭惈璇箟鍓嶇紑锛屼緥濡?`indicators/accuracy/f1.yaml`

璐ㄩ噺闂紙Quality Gates / QA锛?
- 鍩烘湰鏍￠獙锛氭墍鏈夋潯鐩繀椤诲寘鍚獻D銆乶ame銆乻ource/owner锛涙寚鏍囧繀椤诲甫鏈塺unbook鎴栨墽琛岃鏄?
- 鑷姩鍖栵細鍚庣画娣诲姞CI鑴氭湰妫€鏌SON/YAML鐨剆chema涓庡繀瑕佸瓧娈

# Phase 3 Quickstart（Qwen3 全变体 smoke）

- 文档：见 docs/PHASE3_QUICKSTART.md（Windows/PowerShell 命令）。
- LM Arena 快照保存在 enchmarks/snapshots/lmarena/ 以便历史追踪。
- 统一输出（unified_v1）指标：win_rate、elo_rating、latency_p99、throughput_rps、toxicity_rate、accuracy_f1。
