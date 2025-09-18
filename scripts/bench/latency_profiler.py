#!/usr/bin/env python3
"""Minimal latency profiler stub: simulates measuring latencies and prints p50/p90/p99 in ms.
If a --seed is provided the numbers are deterministic.
"""
import argparse
import json
import random

def simulate(seed=None):
    if seed is not None:
        random.seed(int(seed))
    # generate 1000 latency samples (ms)
    samples = [random.gauss(50, 30) for _ in range(1000)]
    samples = [max(1, s) for s in samples]
    samples.sort()
    def pct(p):
        idx = int(len(samples)*p/100)
        idx = min(max(idx,0), len(samples)-1)
        return round(samples[idx],2)
    return {"p50_ms": pct(50), "p90_ms": pct(90), "p99_ms": pct(99)}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed')
    args = parser.parse_args()
    out = simulate(args.seed)
    print(json.dumps(out, ensure_ascii=False))

if __name__ == '__main__':
    main()
