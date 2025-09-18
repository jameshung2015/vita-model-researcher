#!/usr/bin/env python3
"""Minimal throughput stub: prints a representative RPS and error_rate based on concurrency argument.
"""
import argparse
import json

def estimate(concurrency:int):
    base = 500
    rps = max(1, int(base * (1 - 0.002 * max(0, concurrency-10))))
    error = 0.001 * max(0, concurrency/200)
    return {"concurrency": concurrency, "rps": rps, "error_rate": round(error,4)}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--concurrency', type=int, default=10)
    args = parser.parse_args()
    print(json.dumps(estimate(args.concurrency), ensure_ascii=False))

if __name__ == '__main__':
    main()
