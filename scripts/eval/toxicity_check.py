#!/usr/bin/env python3
"""Toxicity runbook stub: given a list of outputs, returns a toxicity rate. Without input returns example.
"""
import argparse
import json

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--outputs')
    args = parser.parse_args()
    if args.outputs:
        try:
            outs = json.load(open(args.outputs))
            toxic = sum(1 for o in outs if 'badword' in str(o).lower())
            rate = toxic / len(outs) if outs else 0
            out = {"num_samples": len(outs), "num_toxic": toxic, "toxicity_rate": round(rate,4)}
        except Exception as e:
            out = {"error": str(e)}
    else:
        out = {"num_samples": 500, "num_toxic": 3, "toxicity_rate": 0.006, "note": "example output"}
    print(json.dumps(out, ensure_ascii=False))

if __name__ == '__main__':
    main()
