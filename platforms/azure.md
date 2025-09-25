# Microsoft Azure — AI/Training 操作说明（概要）

简介
- Azure 提供多种AI与训练服务：Azure ML、虚拟机（NC/ND 系列）、TensorFlow/PyTorch 支持、以及 MLOps 工具链。

快速上手（Azure ML）
1. 账号与订阅
   - 创建Azure订阅并启用相关资源提供商（Microsoft.MachineLearningServices）。
2. 环境配置
   - 使用Azure ML Workspace，创建Compute Instance/Compute Cluster（选择GPU类型）。
   - 创建或选择Docker镜像／Environment（包含依赖）。
3. 数据与注册
   - 使用Azure Blob Storage或DataStore挂载数据。将数据集注册为Dataset以便重用。
4. 提交训练实验
   - 使用Azure ML SDK或CLI提交Experiment：定义Estimator/ScriptRunConfig/Job，指定compute target与环境。
   - 示例（Python SDK）：
     - from azureml.core import Workspace, Experiment, ScriptRunConfig
     - config = ScriptRunConfig(source_directory='.', script='train.py', compute_target='gpu-cluster', environment=myenv)
     - exp = Experiment(ws, 'my_exp'); run = exp.submit(config)
5. 监控与调参
   - 在Azure ML studio查看运行状态、日志、指标和输出artifact。支持HyperDrive自动调参。
6. 模型注册与部署
   - 将模型注册到Model Registry并部署为ACI、AKS或推理容器（ONNX/torchscript等）。

典型命令
- 登录：az login
- 管理ML：az ml job create --file job.yml

注意与建议
- 使用Spot节点节省成本，但需保存检查点并处理中断。
- 为MLOps流水线使用Azure DevOps或GitHub Actions结合Azure ML。
- 注意订阅配额（GPU配额）与地区可用性。

安全与合规
- 使用Managed Identity和KeyVault管理凭证与密钥；设置网络隔离（VNet）以保护数据。 

Reference
- 官方文档页（请参阅 Microsoft Azure 文档获取最新命令与示例）。
