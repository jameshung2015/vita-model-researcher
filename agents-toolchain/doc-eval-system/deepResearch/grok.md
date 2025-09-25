### 国际（海外）模型评测机构与学术单位

以下是目前全球主要的AI/LLM模型评测机构和学术单位，主要基于开源社区、研究机构和大学。它们通常提供基准数据集（benchmarks）和排行榜（leaderboards），用于评估模型在知识、推理、编码等能力上的表现。主流模型（如GPT-4o、Claude 3.5、Gemini、Llama系列）会在这些基准上进行测试。评分方案多为标准化指标，如准确率（Accuracy）、F1分数或平均分数。接入要求一般为开源免费，使用门槛低（通过GitHub或Hugging Face运行评估工具），但提交排行榜需验证结果。数据量因基准而异，通常数千到数万样本。

1. **Allen Institute for AI (AI2)**  
   - **主要基准**：AI2 Reasoning Challenge (ARC)、WinoGrande、CommonGen-Eval。  
   - **主流模型评分方案**：以准确率为主，例如ARC使用多选题正确率（o1模型在ARC上达75.7%-87.5%）；WinoGrande为填空任务准确率（主流模型如Claude 3.5 Sonnet达高分）。  
   - **接入要求与使用门槛**：数据集公开，通过Hugging Face或GitHub下载；排行榜提交需上传结果到AllenAI leaderboard（免费，无需特殊权限）。门槛低，适合开源模型，使用LM Evaluation Harness工具运行。  
   - **数据量**：ARC约7700道科学题（分Easy和Challenge集）；WinoGrande 44000任务；CommonGen-Eval基于CommonGen-lite数据集（数千样本）。

2. **EleutherAI**  
   - **主要基准**：LM Evaluation Harness（综合评估框架）、Pythia系列基准、GPT-Neo评估。  
   - **主流模型评分方案**：多任务平均准确率或困惑度（Perplexity），如在HumanEval编码基准上，US模型领先中国模型3.7pp（2024数据）。  
   - **接入要求与使用门槛**：开源工具，通过GitHub访问；提交需运行Harness并上传到EleutherAI leaderboard。免费，开源模型门槛低，闭源需API调用。  
   - **数据量**：The Pile数据集825GB（用于训练评估）；典型基准如数千到数万样本。

3. **Hugging Face**  
   - **主要基准**：Open LLM Leaderboard（综合多个基准如ARC、HellaSwag、MMLU、TruthfulQA）。  
   - **主流模型评分方案**：平均分数（Average Score），如o1-preview在MMLU上92.3%；主流模型需在多个子任务平均。  
   - **接入要求与使用门槛**：仅限开源模型提交，通过Spaces平台运行评估；免费，但需模型权重公开。门槛中，需计算资源运行全评估。  
   - **数据量**：综合基准，总数据超10万样本（如MMLU 15000+多选题）。

4. **Stanford University (HAI/CRFM)**  
   - **主要基准**：HELM（Holistic Evaluation of Language Models）、FMTI（Foundation Model Transparency Index）。  
   - **主流模型评分方案**：多维度指标，包括准确率、公平性、鲁棒性；如在MATH上，o1达94.8%。FMTI评估透明度（100项指标）。  
   - **接入要求与使用门槛**：数据集公开，通过网站访问；提交需遵循协议，免费但学术导向。门槛低，适合研究使用。  
   - **数据量**：HELM覆盖多个数据集，总量数万样本；FMTI无固定数据，但评估100+指标。

5. **Google Research**  
   - **主要基准**：BigBench（Beyond the Imitation Game Benchmark）。  
   - **主流模型评分方案**：任务特定指标平均，如知识和推理准确率。  
   - **接入要求与使用门槛**：GitHub公开；提交到leaderboard免费。门槛低，使用JSON格式任务。  
   - **数据量**：200+任务，覆盖数万样本。

6. **LMSYS Org**  
   - **主要基准**：Chatbot Arena（用户偏好投票）。  
   - **主流模型评分方案**：Elo分数（基于对战投票），如Gemini-Exp-1206在编码上1369分；o1在数学领先。  
   - **接入要求与使用门槛**：提交模型到arena（开源/闭源均可），免费但需API支持。门槛中，需处理实时查询。  
   - **数据量**：340000+投票（2024-2025），覆盖181模型。

其他国际基准如SuperGLUE（NYU等合作，数据量多样，评分聚合指标）、TruthfulQA（准确率+GPT-Judge，800题）等，通常由多机构协作。

### 国内（中国）模型评测机构与学术单位

中国评测聚焦中文能力、法律/医疗等本土场景，机构多为大学实验室或企业AI部门。主流模型（如DeepSeek、Qwen、Baichuan）性能接近国际（如MMLU上中美差距0.3pp）。评分方案类似国际，接入多开源免费，门槛低但需中文数据处理能力。数据量从数百到数万不等。

1. **Shanghai AI Laboratory (上海人工智能实验室)**  
   - **主要基准**：OpenCompass（综合评估）、MathBench。  
   - **主流模型评分方案**：多任务准确率，如数学问题解决率。  
   - **接入要求与使用门槛**：GitHub公开；提交需运行框架，免费。门槛低，集成多种基准。  
   - **数据量**：MathBench覆盖多子集，数千数学题。

2. **OpenBMB (开源大模型社区，由清华/北大等支持)**  
   - **主要基准**：UltraEval（轻量评估）。  
   - **主流模型评分方案**：灵活指标平均，如NLP任务准确率。  
   - **接入要求与使用门槛**：GitHub访问；免费提交。门槛低，快速运行。  
   - **数据量**：多数据集集成，数万样本。

3. **Tsinghua University NLP Lab (THU-NLP)**  
   - **主要基准**：ChatEval、CLUE/SuperCLUE（中文理解评估）。  
   - **主流模型评分方案**：人类-like评估准确率，如SuperCLUE多任务平均。  
   - **接入要求与使用门槛**：网站/GitHub公开；提交免费。门槛低，专注中文。  
   - **数据量**：SuperCLUE数万题；ChatEval多样样本。

4. **Fudan University**  
   - **主要基准**：TRACE（连续学习评估）。  
   - **主流模型评分方案**：准确率+遗忘率。  
   - **接入要求与使用门槛**：ArXiv/GitHub；免费学术使用。门槛低。  
   - **数据量**：8个数据集，数千样本。

5. **Institute of Automation, Chinese Academy of Sciences (IACAS)**  
   - **主要基准**：ZhuJiu（多维度中文基准）。  
   - **主流模型评分方案**：综合分数（知识、生成等），51任务平均。  
   - **接入要求与使用门槛**：网站访问；免费提交。门槛低，中文导向。  
   - **数据量**：51任务，数万样本。

6. **其他中文特定基准**（多机构协作，如NeurIPS会议、华为等）：  
   - **LexEval**（法律基准）：23任务，准确率评分；数据量14150题；公开数据集，免费。  
   - **FLAMES**（价值对齐）：对抗性提示准确率；数据量2251提示；开源。  
   - **C-Eval/CMMLU**（中文知识）：多选准确率；数据量数万；GitHub免费。  
   - **MedGPTEval**（医疗）：综合指标；数据量多样，基准评估3模型；开源。

总体上，国际基准更通用，中国基准强调本土化（如法律、医疗）。2024-2025中美差距缩小（e.g., MATH上1.6pp），数据量多为开源可查。更多细节可查GitHub Awesome-LLM-Eval列表。

https://grok.com/c/6524cba9-be3b-4d45-a4ee-517b6d1dae0d 