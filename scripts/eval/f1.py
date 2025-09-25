#!/usr/bin/env python3
"""Minimal F1 runbook stub with unified output.

Reads optional --gold and --pred JSON files (list of labels) and prints a JSON
result. By default emits a unified structure:
  {"metric_id","value","ci","samples_used","meta"}

Use --legacy to emit {"precision","recall","f1"} for backward compatibility.
"""
import argparse
import json
import sys

def compute_f1(gold, pred):
    # simple micro-precision/recall for exact-match labels
    tp = sum(1 for g,p in zip(gold, pred) if g==p)
    precision = tp / len(pred) if pred else 0.0
    recall = tp / len(gold) if gold else 0.0
    f1 = (2*precision*recall/(precision+recall)) if (precision+recall)>0 else 0.0
    return precision, recall, f1

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--gold')
    parser.add_argument('--pred')
    parser.add_argument('--output')
    parser.add_argument('--metric_id', default='accuracy_f1')
    parser.add_argument('--legacy', action='store_true', help='Emit legacy precision/recall/f1 shape')
    args = parser.parse_args()

    if args.gold and args.pred:
        try:
            gold = json.load(open(args.gold))
            pred = json.load(open(args.pred))
            p,r,f = compute_f1(gold, pred)
            if args.legacy:
                out = {"precision": round(p,4), "recall": round(r,4), "f1": round(f,4)}
            else:
                out = {
                    "metric_id": args.metric_id,
                    "value": round(f, 4),
                    "ci": None,
                    "samples_used": len(gold) if isinstance(gold, list) else None,
                    "meta": {"precision": round(p,4), "recall": round(r,4)}
                }
        except Exception as e:
            out = {"error": str(e)}
    else:
        if args.legacy:
            out = {"precision": 0.82, "recall": 0.78, "f1": 0.80, "note": "example output (no files provided)"}
        else:
            out = {
                "metric_id": args.metric_id,
                "value": 0.80,
                "ci": None,
                "samples_used": 100,
                "meta": {"precision": 0.82, "recall": 0.78, "note": "example output (no files provided)"}
            }

    text = json.dumps(out, ensure_ascii=False)
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(text)
    else:
        print(text)

if __name__ == '__main__':
    main()
