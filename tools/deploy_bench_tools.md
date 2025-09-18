# 部署 / 台架 / 实车 测试工具清单（概要）

目的：整理支撑模型上线、台架(HIL/DTU)测试与实车(车载)验证的常用工具、平台与集成建议，便于工程团队选择与对接。

说明：每个条目包含：用途、适用场景、与本仓库评测/场景对接建议（短说明）。

## 一、部署 & 推理服务（线上/边缘）

- Docker / Kubernetes
  - 用途：容器化与大规模部署、弹性伸缩、滚动升级
  - 场景：生产化在线推理、灰度发布、A/B测试
  - 对接建议：将评测的推理镜像（ONNX/TorchScript）打包为容器，使用 Job/Deployment 运行负载测试与延迟测量，输出 `latency_p99.json` / `throughput_rps.json`。

- NVIDIA Triton Inference Server
  - 用途：高性能推理服务器（支持 TensorRT/ONNX/PyTorch 后端）
  - 场景：低延迟、高吞吐的推理部署
  - 对接建议：把模型导出为TensorRT/ONNX，使用 Triton 客户端做 p99/throughput 测试并记录指标。

- TorchServe / BentoML / KFServing (KServe)
  - 用途：模型部署与在线推理框架（支持自定义handler、模型管理）
  - 场景：中小规模服务、快速模型迭代
  - 对接建议：部署评测模型并通过 bench/load_test.py 发起请求，收集输出JSON。

- AWS SageMaker / Azure ML Endpoints / Volc Engine Model Serving
  - 用途：云厂商的托管模型服务
  - 场景：快捷部署与批量推理，方便与云端评测集成
  - 对接建议：在云端创建endpoint并通过并发负载测试获取吞吐/延迟曲线。

## 二、台架测试 / 硬件在环 (HIL) / 实时仿真

- dSPACE (HIL)
  - 用途：工业级 HIL 仿真与控制器验证
  - 场景：ECU 功能验证、闭环测试、实时信号注入
  - 对接建议：把模型或推理服务与 HIL 总线对接（通过网络/IPC），在台架上运行鲁棒性/异常注入测试并记录报警/性能。

- NI VeriStand / NI LabVIEW
  - 用途：实时测试、数据采集与自动化测试台架
  - 场景：数据记录、实时控制回路、测试序列执行
  - 对接建议：用作输入数据的回放和测量点的指标采集（延迟/正确性）。

- OPAL-RT / RTMaps
  - 用途：实时仿真与多模态传感器流处理
  - 场景：车辆动力学仿真、摄像头/雷达数据注入
  - 对接建议：在仿真中注入对抗性场景（perturbations）用于robustness评估。

- Vector CANoe / CANalyzer
  - 用途：车辆总线（CAN/LIN/FlexRay）分析与模拟
  - 场景：ECU 通信测试、总线负载与时序验证
  - 对接建议：在总线注入模拟事件并验证模型对诊断信息的反应，记录异常率/延迟。

- RT-LAB / Simulink Real-Time
  - 用途：控制器与模型的实时部署与验证
  - 场景：模型闭环行为验证
  - 对接建议：把简化模型或控制逻辑部署到实时目标机，量测响应时延与稳定性。

## 三、车辆级仿真与场景生成（虚拟测试）

- CARLA
  - 用途：开源自动驾驶模拟器（支持传感器、天气、场景脚本）
  - 场景：视觉/多模态场景、道路事件复现
  - 对接建议：用 CARLA 生成图像/视频输入并执行 `scenarios/scn_03_multimodal_query` 的测试集；记录系统的识别/问答准确率与响应时间。

- LGSVL / SVL Simulator
  - 用途：高保真自动驾驶仿真平台
  - 场景：整车感知/控制/场景交互测试
  - 对接建议：用于大型场景回放与端到端 pipeline 验证，结合 HIL 进行闭环测试。

- AirSim
  - 用途：无人机/车辆的物理仿真
  - 场景：多环境物理传感器测试
  - 对接建议：适合多传感器融合与视觉鲁棒性测试。

## 四、实车测试与远程采集

- OBD-II / CAN interface + dongles (PEAK, Kvaser, ValueCAN)
  - 用途：读取车辆总线数据、注入消息（取决于权限）
  - 场景：实车数据采集、里程/传感器同步
  - 对接建议：采集真实车载数据用于评测集（accuracy/robustness），并把数据匿名化后上传到评测数据存储。

- Telemetry / Telematics platforms (OTA、MQTT、Kafka)
  - 用途：车云双向通信、遥测数据收集
  - 场景：远程日志、OTA更新、遥测指标聚合
  - 对接建议：把模型运行时日志、延迟指标与异常事件通过 Kafka/MQTT 上报到集中监控，并触发报警。

- Mobile Device / IVI test tools (ADB automation, Appium)
  - 用途：车载应用自动化测试（UI / 人机交互）
  - 场景：语音交互、IVI 界面流测试
  - 对接建议：自动化回放用户操作并验证 dialog_management 与 personalization 行为。

## 五、负载生成与性能测试

- Locust / Vegeta / k6
  - 用途：HTTP/gRPC 负载生成与吞吐测试
  - 场景：在线推理的并发吞吐、稳定性测试
  - 对接建议：生成并发请求到模型服务，测量 RPS、P50/P90/P99，输出 `throughput_rps.json` 与 `latency_p99.json`。

- JMeter
  - 用途：企业级性能测试、协议丰富
  - 场景：复杂接口的压力测试

## 六、数据回放与对齐

- ROS / rosbag
  - 用途：传感数据记录与回放（常用于机器人与车辆研究）
  - 场景：多传感器时序对齐、离线评测
  - 对接建议：把实车采集记录成 rosbag，在台架或仿真环境中回放，保证测试可重复。

- Replay frameworks (custom playback harness)
  - 用途：用于将生产/实车日志回放到仿真或台架
  - 场景：回放真实故障场景用于诊断/鲁棒性测试

## 七、监控、日志与指标系统

- Prometheus + Grafana
  - 用途：采集、告警、可视化时序指标
  - 场景：实时监控延迟、吞吐、错误率
  - 对接建议：评测服务在关键点导出 Prometheus metrics，CI 聚合时拉取 Prometheus 数据做趋势分析。

- ELK (Elasticsearch + Logstash + Kibana)
  - 用途：结构化日志存储与搜索
  - 场景：排查失败样例与审计

- Sentry / OpenTelemetry
  - 用途：分布式追踪与异常告警

## 八、测试自动化与框架

- pytest / unit tests
  - 用途：单元/集成测试（脚本级）
  - 场景：验证评测脚本输出契约、schema 校验
  - 对接建议：对 `scripts/eval/*` 加入单元测试（happy path + 边界）并在 CI 中运行。

- Robot Framework / TestRail / Jenkins
  - 用途：自动化测试管理、用例执行与结果报告

## 九、安全、合规与隐私工具

- 数据脱敏/匿名化工具 (自研脚本 / ARX)
  - 用途：对导出的实车数据进行脱敏
  - 对接建议：在把数据上传到云或共享存储之前运行脱敏流程，满足合规要求。

- 签名与审计（KeyVault, HSM）
  - 用途：保护证书/OTA 更新与审计日志

## 十、工程化建议（如何在本仓库落地）

1. 分类目录
   - 在 `tools/` 下创建子目录：`tools/deploy_templates/`、`tools/hil_configs/`、`tools/sim_configs/` 用来保存平台特定的 job/template。
2. 标准化产物
   - 明确每次评测必须产出的 artifact（例如：`accuracy_f1.json`, `latency_p99.json`, `throughput_rps.json`, `robustness_adv.json`, `toxicity.json`），并在 CI 中实现聚合器脚本 `tools/aggregate_results.py`。
3. 数据治理
   - 对实车采集数据做脱敏并把样本路径写入 scenario 的 `minimal_requirements.json` 的 `sample_data_path` 字段。
4. 可重复性
   - 在台架/仿真中保存环境镜像与run配置（docker image + job yaml）并版本化。

---

文件末。若需要，我可以：
- 按你们现用的几套台架（例如 dSPACE / NI / Vector）生成更详细的对接步骤与示例脚本；
- 在 `tools/` 下生成 `deploy_templates/` 与 `hil_configs/` 并填入 2-3 个行业常见模板（可直接在 CI 中使用）。
