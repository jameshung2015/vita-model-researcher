"""
示例：把仓库内的 f1.py 包装进一个简单的 eval harness（示例脚本，供参考）
用法（本地）：
python tools/examples/evals_example.py --model path/to/model.pt --data path/to/val.json --out out.json
"""
import argparse
import subprocess
import json
import os

parser = argparse.ArgumentParser()
parser.add_argument('--model', required=True)
parser.add_argument('--data', required=True)
parser.add_argument('--out', required=True)
args = parser.parse_args()

# 调用仓库内的评测脚本
cmd = ["python", "scripts/eval/f1.py", "--model", args.model, "--data", args.data, "--out", args.out]
print('Running:', ' '.join(cmd))
ret = subprocess.run(cmd)
if ret.returncode != 0:
    raise SystemExit('f1 evaluation failed')

# 简单地读取并打印结果
with open(args.out,'r',encoding='utf-8') as f:
    data = json.load(f)
print('F1 eval result:', data)
