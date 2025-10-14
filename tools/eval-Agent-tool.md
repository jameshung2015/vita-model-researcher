# 开源：Agent 评测工具 / 基准（3 个）

| 工具 / 基准                           | 支持的基准（代表性）                                                                           | 自定义评测/新增集                              | 本地部署                                    | 版本/数据集管理                                             | 指标与可复现性                                         | 社区认可 / 备注                                           |
| --------------------------------- | ------------------------------------------------------------------------------------ | -------------------------------------- | --------------------------------------- | ---------------------------------------------------- | ----------------------------------------------- | --------------------------------------------------- |
| **AgentBench（THUDM）**             | 8+ 环境（后续演进），多回合决策与执行任务，系统性评估 LLM-as-Agent 能力。([GitHub][1])                           | 代码开源，按环境接口扩展新任务场景可行。([GitHub][1])      | 可本地运行（标准 Python/依赖）。([GitHub][1])       | Git 版本 + 论文/官网同步演进。([arXiv][2])                      | 提供统一环境与评分脚本，便于重现；聚焦决策/工具使用等能力。([OpenReview][3]) | 早期且被广泛引用，适合作为总览型 Agent 基准入口。([arXiv][2])            |
| **WebArena / VisualWebArena**     | 真实可自托管的 Web 环境与任务集；VisualWebArena 扩展到多模态网页视觉任务；有排行榜。([GitHub][4])                    | 以站点/任务为单位扩展；支持加入新网站/任务模板。([GitHub][4]) | 可自托管/本地部署完整网站沙盒。([GitHub][4])           | 仓库 + Leaderboard 版本管理；任务更新有 release/网站。([GitHub][4]) | 采用执行式评估（任务完成率等），真实网页交互可复现实验。([WebArena][5])     | Web 代理研究主流基准之一；多模态版本用于“看图上网”类代理。([GitHub][6])       |
| **OSWorld / OSWorld-G（xlang-ai）** | 评测“电脑助手”型多模态/GUI 代理：真实 OS 环境下完成开放式桌面任务；扩展出 OSWorld-G 侧重 GUI grounding。([OSWorld][7]) | 基于任务脚本与评估管线可扩展；含评估脚本与数据。([GitHub][8])  | 提供在本地/虚拟机/Docker 的部署说明与支持。([GitHub][9]) | 仓库/论文/网站版本化；基准文件与评估脚本成套提供。([GitHub][8])              | 执行成功率等硬指标；强调可重现实验管线。([OSWorld][7])              | NeurIPS 2024/2025 相关工作，凸显“电脑实际可用性”差距。([OSWorld][7]) |

> 其他可选开源补充：**BrowserGym / AgentLab**（Web 代理统一环境与评测套件）([GitHub][10])、**WebBench**（跨 452 个真实网站、2454 任务）([GitHub][11])、**ST-WebAgentBench**（企业业务站点 222 任务+策略扰动）([GitHub][12])、**HuggingFace ScreenSuite**（GUI 代理评测套件）([GitHub][13])、**WebChoreArena**（扩展 WebArena，强调繁琐“家务式”网页任务）([WebChoreArena][14])。

# 商用 / 平台：Agent 评测与观测（3 个）

> 注：商用平台通常“评测 + 观测 + 数据集管理 + 版本/实验对照 + 团队协作”一体化，更贴近生产落地场景。

| 平台                              | 支持的场景/基准                                                                        | 自定义评测                                                       | 本地/私有化                       | 版本与数据治理                                                     | 指标 & 可复现性                                           | 典型优势 / 局限                                            |
| ------------------------------- | ------------------------------------------------------------------------------- | ----------------------------------------------------------- | ---------------------------- | ----------------------------------------------------------- | --------------------------------------------------- | ---------------------------------------------------- |
| **LangSmith（LangChain）**        | 面向 LLM/Agent 工作流评测与观测，可对接你自备数据集/基准；常与 Web/桌面代理集成做任务完成率评估。([LangChain Docs][15]) | 建数据集、定义评测、跑批评测与对比分析；支持打分器（LLM/规则/函数）。([LangChain Docs][15]) | SaaS 为主，亦支持更严格部署选项（以官方文档为准）。 | 评测运行有可追踪 run/trace、dataset 版本；便于回溯对比。([LangChain Docs][15]) | 覆盖质量/相关性/毒性/幻觉等多类指标；可脚本化复现实验。([LangChain Docs][15]) | **优**：工程集成与迭代快；**局**：不开箱即用的“标准 Agent 基准”，需自接或对接开源基准。 |
| **Scale AI GenAI Evaluation**   | 由标注/评测服务商提供的人机混合评测（含代理任务）；可引入 Web/检索/工具使用等复杂场景进行客观衡量。                           | 定制评测集合与流程（含人类标注/审稿/偏好/成对比较）。                                | 企业级私有部署/合规选项（以官方为准）。         | 企业级数据与版本治理、审计链路。                                            | 人审 + 自动指标结合，可形成“金标集”与 A/B 评测闭环。                     | **优**：人审闭环、规模化评测；**局**：商用费用、专有流程不完全开源。               |
| **Humanloop（Evaluation & Ops）** | 面向 LLM 应用/代理的评测与运维平台；支持回放、对比、指标仪表板。                                             | 自定义数据集、打分标准、离线/在线评测。                                        | 云为主，企业可洽谈私有化。                | 版本/实验对比、提示/参数版本锁定。                                          | 多维指标 + 用户反馈回收，便于可复现。                                | **优**：产品化 Ops 能力强；**局**：与开源 Agent 基准需要对接整合。          |

（Scale AI 与 Humanloop 为行业代表；如你已有偏好，也可替换为你现网在谈的供应商。）

---

## 如何把它们“放进你的维度表”里

你已有的表头可以直接复用。我给你一个**最小补充示例**（可粘进现有文档）：

### LLM / Agent（开源）

* **AgentBench** — 基准型；多环境决策任务；支持本地；Git 版本；执行成功率/策略质量复现良好。([GitHub][1])
* **WebArena（含 VisualWebArena）** — Web 代理真实网站任务；自托管；执行式评估；有排行榜与站点扩展。([GitHub][4])
* **OSWorld / OSWorld-G** — 计算机实际可用性/GUI Grounding 评测；VM/Docker 本地可跑；脚本化评估全链路。([OSWorld][7])

### Agent（商用 / 平台）

* **LangSmith** — 数据集创建 + 批量评测 + Trace 对比；工程融合度高；需自接 Agent 基准。([LangChain Docs][15])
* **Scale AI GenAI Evaluation** — 人审+自动评测闭环，企业级合规与数据治理。
* **Humanloop** — 评测与运维一体化（对话/代理回放、A/B、指标看板），便于持续优化。

---

## 选型提示（结合你的评测体系）

1. **场景优先**：

   * 浏览器/网站自动化 → 先用 **WebArena/BrowserGym 系**（可加 WebBench、WorkArena 作补充）。([GitHub][4])
   * 电脑/GUI 操作 → 用 **OSWorld / ScreenSuite**；若强调 GUI grounding，加入 **OSWorld-G**。([OSWorld][7])
   * 决策/多环境总测 → **AgentBench** 打基础。([OpenReview][3])

2. **平台协同**：

   * 工程实践里，用 **LangSmith/Humanloop** 管数据集、版本和对比，把开源基准的执行结果接入成“官方报表”。([LangChain Docs][15])

3. **版本锁定**：

   * 固定仓库 tag / commit + 任务清单 MD5，避免“基准漂移”。（开源仓库均支持）

---

需要的话，我可以把这部分**自动合并到你现有的对比 HTML**，并**生成一个可下载的 HTML 报告文件**（含上面这些表格与来源引用）。

[1]: https://github.com/THUDM/AgentBench?utm_source=chatgpt.com "THUDM/AgentBench: A Comprehensive Benchmark to ..."
[2]: https://arxiv.org/abs/2308.03688?utm_source=chatgpt.com "AgentBench: Evaluating LLMs as Agents"
[3]: https://openreview.net/forum?id=zAdUB0aCTQ&utm_source=chatgpt.com "AgentBench: Evaluating LLMs as Agents"
[4]: https://github.com/web-arena-x/webarena?utm_source=chatgpt.com "GitHub - web-arena-x/webarena: Code repo for ..."
[5]: https://webarena.dev/?utm_source=chatgpt.com "WebArena: A Realistic Web Environment for Building ..."
[6]: https://github.com/web-arena-x/visualwebarena?utm_source=chatgpt.com "VisualWebArena is a benchmark for multimodal agents."
[7]: https://os-world.github.io/?utm_source=chatgpt.com "OSWorld: Benchmarking Multimodal Agents for Open-Ended ..."
[8]: https://github.com/xlang-ai/OSWorld-G?utm_source=chatgpt.com "xlang-ai/OSWorld-G: [NeurIPS 2025 Spotlight] Scaling ..."
[9]: https://github.com/Agent-E3/OSWorld?utm_source=chatgpt.com "Agent-E3/OSWorld"
[10]: https://github.com/ServiceNow/BrowserGym?utm_source=chatgpt.com "BrowserGym, a Gym environment for web task automation"
[11]: https://github.com/Halluminate/WebBench?utm_source=chatgpt.com "Halluminate/WebBench: 📚 Benchmark your browser agent ..."
[12]: https://github.com/segev-shlomov/ST-WebAgentBench?utm_source=chatgpt.com "segev-shlomov/ST-WebAgentBench"
[13]: https://github.com/huggingface/screensuite?utm_source=chatgpt.com "huggingface/screensuite"
[14]: https://webchorearena.github.io/?utm_source=chatgpt.com "WebChoreArena: Evaluating Web Browsing Agents on ..."
[15]: https://docs.langchain.com/langsmith/evaluation?utm_source=chatgpt.com "Evaluation - Docs by LangChain"
