# 平台与指标评测集成指南

目标
- 说明如何在常见训练/推理平台（百炼、火山引擎、Azure、NVIDIA DGX）上运行本仓库内的评测脚本，以产出指标：`accuracy_f1`、`latency_p99`、`throughput_rps`、`robustness_adv`、`toxicity`。
- 给出最小作业/资源要求、数据准备、监控与产物（JSON）产出路径建议，便于工程化集成与CI自动化。

前置（仓库内可用脚本与位置）
- 准确性评测：`scripts/eval/f1.py`
- 稳健性评测：`scripts/eval/robustness_suite.py`
- 毒性检测：`scripts/eval/toxicity_check.py`
- 延迟/吞吐：`scripts/bench/latency_profiler.py`, `scripts/bench/load_test.py`

通用步骤（适用于所有平台）
1. 准备模型工件
   - 训练/导出模型并将模型文件（例如 `model.pt`, `model.onnx`）上传到平台可挂载的对象存储或模型注册表。
2. 数据准备
   - 将评测所需的数据集（验证集、对抗样本、毒性检测语料、样本音频/图像）上传到对象存储，并在作业中挂载或下载到工作目录。
3. 作业/任务定义
   - 使用平台的作业模板或CLI提交独立的评测作业（非训练作业），指定镜像、命令、资源（CPU/GPU、内存）、输入路径与输出路径。
4. 运行与收集输出
   - 评测脚本应输出标准化的JSON（示例见下），并将其上传到对象存储或artifact目录以便CI/工程系统收集。
5. 监控与告警
   - 配置日志与指标采集（Prometheus/Cloud metrics），并对超出阈值的指标触发告警（例如 P99>阈值 或 toxicity>0.1）。

建议的输出JSON契约（示例）
- accuracy_f1.json
  - {"indicator":"accuracy_f1","precision":0.82,"recall":0.78,"f1":0.80,"samples":1000}
- latency_p99.json
  - {"indicator":"latency_p99","p50_ms":20,"p90_ms":45,"p99_ms":120,"requests":10000}
- throughput_rps.json
  - {"indicator":"throughput_rps","rps":250,"concurrency":16,"duration_s":60}
- robustness_adv.json
  - {"indicator":"robustness_adv","attack_type":"fgsm","success_rate":0.12,"f1_drop":0.08}
- toxicity.json
  - {"indicator":"toxicity","toxic_ratio":0.003,"total_samples":20000}

下面针对每个平台给出具体流程与注意要点。

## 百炼（Bairui）
能力要点
- 支持文件/对象存储挂载、作业提交（Web/CLI）、多卡训练与单独的推理/评测任务。许多企业版支持自定义容器。

如何产出指标
1. 准备容器镜像：包含Python环境、依赖（requirements.txt），并把仓库的 `scripts/` 挂入或打包入镜像。
2. 数据与模型：上传到平台OSS并在作业配置中挂载为输入路径。
3. 提交评测作业：作业命令示例
   - python scripts/eval/f1.py --model /mnt/models/model.pt --data /mnt/data/val.json --out /mnt/output/accuracy_f1.json
   - python scripts/bench/latency_profiler.py --model /mnt/models/model.onnx --out /mnt/output/latency_p99.json
4. 资源建议
   - accuracy/robustness/toxicity: 单卡或多卡CPU/GPU均可，推荐至少 1 GPU（A10/A100）和 16GB RAM
   - latency/throughput: 在低延迟场景下使用更接近推理环境的实例（低CPU/memory、GPU更快的卡）
5. 产物收集
   - 将输出 JSON 上传到模型注册表 / 对象存储，并在作业结束时触发CI收集（通过API或挂载路径）。

注意事项
- 平台可能对容器网络、外部HTTP访问或GPU类型有限制，提前确认可用实例类型。

## 火山引擎（Volc Engine）
能力要点
- 云端GPU实例、对象存储（OSS）、分布式训练服务、CLI/API 可编排作业。适合做批量评测与分布式压力测试。

如何产出指标
1. 使用 `volc-cli` 或控制台创建评测作业，挂载OSS数据。
2. 对于吞吐/压力测试，推荐在云内创建负载生成器（多实例并发）运行 `scripts/bench/load_test.py`，将结果聚合到一个中心节点并输出 `throughput_rps.json`。
3. 示例分布式评测流程
   - Upload data: volc-cli upload --bucket eval-bucket --file val.json
   - Submit job: volc-cli submit-job --image my-eval:latest --cmd "python scripts/eval/f1.py --model /models/model.pt --data /data/val.json --out /out/accuracy_f1.json" --gpus 1

注意事项
- 分布式负载要考虑网络带宽与跨实例聚合延迟；在相同可用区内运行以减少网络抖动。
- 使用对象存储作为采样与结果汇总的中转站。

## Microsoft Azure (Azure ML / VM)
能力要点
- Azure ML 支持Experiment/Job、Compute Cluster、Model Registry、监控（Azure Monitor），容器化/Job YAML 支持很好，适合集成CI。

如何产出指标
1. 在 Azure ML 中创建 `Job`（或 Experiment）并指定 `command`，例如：
   - 使用 Azure ML SDK/CLI 或 `az ml job create --file job.yml`，job.yml 包含运行命令：
     - python scripts/eval/f1.py --model ${{inputs.model}} --data ${{inputs.data}} --out ${{outputs.metric}}
2. 使用 `Azure Monitor` / `Application Insights` 收集延迟与吞吐指标；或在容器内把延迟分布记录成JSON并上传到Blob Storage。
3. 对于吞吐测试：在 Azure VM 上运行 `scripts/bench/load_test.py`，可以使用 VMScaleSet 来并行生成请求。

资源与CI集成
- 将结果注册到 Azure Artifacts 或 Blob 并在 Pipeline（Azure DevOps/GitHub Actions）中抓取并发布为评测报告。

注意事项
- 使用 Managed Identity 与 KeyVault 管理凭证；小心GPU配额与区域可用性。

## NVIDIA DGX（本地/集群）
能力要点
- 高性能本地/机房集群，适合做低抖动的延迟/吞吐基线测量及大规模鲁棒性训练/评测。

如何产出指标
1. 在DGX节点上准备环境（NGC镜像或自建镜像），确保NCCL与网络已优化。
2. 运行评测脚本：对延迟/吞吐在受控网络下运行 `scripts/bench/latency_profiler.py`、`scripts/bench/load_test.py` 并写入输出到共享存储。
3. 对鲁棒性测试，使用多卡并行方式执行 `scripts/eval/robustness_suite.py --attack fgsm --eps 0.03` 并收集 f1_drop 结果。

注意事项
- 在DGX上进行吞吐/延迟基线测试时，禁用CPU频率调节与网络节流，确保测试可重复。

## 指标获取实现细节与范例（通用）
- 将每个评测脚本包装成可重复的作业模板（YAML/JSON）包含：模型路径、数据路径、输出路径、resource spec。
- 评测作业结束后，触发一个聚合步骤：下载所有输出JSON并合并到单一报告（CI job）。

示例作业模板（伪YAML，适配平台）
- name: eval-f1
  image: myregistry/my-eval:latest
  command: python scripts/eval/f1.py --model /models/model.pt --data /data/val.json --out /out/accuracy_f1.json
  resources:
    gpus: 1
    cpu: 4
    memory_gb: 16
  mounts:
    - /mnt/models -> <model-store>
    - /mnt/data -> <dataset-store>
    - /mnt/out  -> <artifact-store>

监控与门槛设置
- 在CI中设置门槛：f1 >= 0.75；p99_latency <= 300ms；toxicity_ratio <= 0.005；robustness f1_drop <= 0.1；throughput >= target rps
- 对低延迟场景，用容器镜像与 runtime 参数尽可能接近生产推理环境（ONNX/TensorRT）。

工程化建议（优先级）
1. 把所有评测脚本包装到统一入口（例如 `tools/run_eval.py --indicator accuracy_f1 --model ...`），便于在不同平台复用同一命令行接口。
2. 创建Job模板库（`platforms/job_templates/`），包含 `azure/job.yml`, `volc/job.json`, `bairui/job.json`, `dgx/run.sh`。
3. 在CI中实现：上传模型->触发评测作业->下载并合并指标->生成报告并阻断不合格合并。

后续我可以帮你：
- 为 `百炼`、`火山引擎`、`Azure` 分别生成 1) 作业 YAML/JSON 模板和 2) CI 示例（GitHub Actions / Azure Pipelines）。
- 把仓库中的评测脚本统一为一个 CLI 入口并加入 `--output-json` 标准输出。

---
(文件末)
