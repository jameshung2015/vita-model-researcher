#!/usr/bin/env python3
"""Minimal F1 runbook stub: reads optional --gold and --pred JSON files (list of labels)
and prints a JSON result with precision/recall/f1. If files not provided, prints example output.
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
    args = parser.parse_args()

    if args.gold and args.pred:
        try:
            gold = json.load(open(args.gold))
            pred = json.load(open(args.pred))
            p,r,f = compute_f1(gold, pred)
            out = {"precision": round(p,4), "recall": round(r,4), "f1": round(f,4)}
        except Exception as e:
            out = {"error": str(e)}
    else:
        out = {"precision": 0.82, "recall": 0.78, "f1": 0.80, "note": "example output (no files provided)"}

    text = json.dumps(out, ensure_ascii=False)
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(text)
    else:
        print(text)

if __name__ == '__main__':
    main()
