```markdown
# 鍩哄噯锛圔enchmarks锛夌煡璇嗗簱

鏈洰褰曠敤浜庤褰曞父瑙佸叕寮€ benchmark锛堜緥濡?MMLU銆丟SM8K銆丅LEU 绛夛級鐨勫厓淇℃伅锛氭寚鏍囧畾涔夈€佹祴璇曟柟娉?Runbook銆佹暟鎹泦鏉ユ簮閾炬帴銆佺ず渚嬪垎鏁颁笌娉ㄦ剰浜嬮」銆傜洰鏍囨槸涓烘ā鍨嬭瘎浼版彁渚涚粺涓€寮曠敤涓庡揩閫熸煡闃呫€?

## 鐜版湁鏉＄洰锛?

### 浼犵粺鍩哄噯
- `mmlu.json` 鈥?MMLU锛圡assive Multitask Language Understanding锛?
- `gsm8k.json` 鈥?GSM8K锛圙rade School Math 8K锛?
- `bleu.json` 鈥?BLEU锛堟満鍣ㄧ炕璇戣川閲忚瘎浼版寚鏍囷級

### 缁煎悎璇勬祴妗嗘灦
- `opencompass.json` 鈥?OpenCompass 鍙稿崡璇勬祴锛堜笂娴蜂汉宸ユ櫤鑳藉疄楠屽锛?
- `superclue.json` 鈥?SuperCLUE 涓枃澶фā鍨嬬患鍚堟祴璇勫熀鍑?
- `modelscope_leaderboard.json` 鈥?ModelScope LLM 鎺掕姒?

### 鎸囦护璺熼殢涓庝汉绫诲亸濂?
- `alpacaeval.json` 鈥?AlpacaEval 鑷姩鍖栨寚浠よ窡闅忚瘎浼?
- `chatbot_arena.json` 鈥?Chatbot Arena 浜虹被鍋忓ソ鎶曠エ骞冲彴

### AGI涓庝笓涓氳兘鍔?
- `agieval.json` 鈥?AGI-Eval 浜虹被鏍囧噯鍖栬€冭瘯鍩哄噯

### Agent鑳藉姏璇勬祴
- `agentbench.json` 鈥?AgentBench LLM浠ｇ悊鑳藉姏璇勬祴

### AI瀹夊叏涓庡榻?
- `anthropic_eval_suite.json` 鈥?Anthropic 璇勪及濂椾欢锛堝畨鍏ㄥ榻愶級

娣诲姞鏉＄洰璇烽伒寰?`templates/benchmark_template.json` 鐨勫瓧娈佃鑼冦€?

缁存姢鎻愮ず锛?
- 鎵€鏈夋潯鐩繀椤诲寘鍚?`id`, `name`, `source`, `datasets`, `test_method` 鍜?`example_scores` 瀛楁銆?
- 瀵逛簬绀轰緥鍒嗘暟锛岃娉ㄦ槑鏄惁涓哄叕寮€璁烘枃涓姤鍛婄殑鍊兼垨浠撳簱/璺戝垎澶嶇幇鍊笺€?

```
\n- lmarena.json — LM Arena 人类偏好投票排行榜\n
