# 内部 Eval Harness 快速接入指南

目标：把仓库的评测脚本接入公司内部的 eval harness，实现统一触发、日志与产物管理。

步骤：
1. 标准化入口
   - 确保每个评测脚本都支持相同的 CLI（model/data/out），例如：
     - `python scripts/eval/f1.py --model <model> --data <data> --out <out>`
2. 创建 Task Adapter
   - 在 harness 中实现一个 Adapter（Python 函数）来调用上述命令并在结束后收集 `/out` 文件上传到 artifact 存储。
3. 上线到 Harness
   - 将 adapter 的镜像/代码推到镜像仓库，注册 Task 模板，设置资源配额与超时。
4. CI 集成
   - 在模型合并/发布流程中加入步骤：upload model -> trigger harness task -> poll for outputs -> fail if门槛不达标
5. 样例日志与监控
   - Adapter 应把评测脚本 stdout/stderr 收集到集中日志系统；同时把关键指标写入 metrics 接口（Prometheus, Cloud Metrics）。

样例 Adapter 伪代码：
```
def run_f1_task(model_path, data_path, out_path):
    cmd = ["python","scripts/eval/f1.py","--model",model_path,"--data",data_path,"--out",out_path]
    subprocess.run(cmd, check=True)
    # 上传 out_path 到 artifact storage
```

常见问题
- 权限问题：确保 harness 运行时能访问对象存储与模型仓库。
- 随机性导致波动：保存运行环境（镜像、依赖、seed）并在报告中记录。

(结束)
