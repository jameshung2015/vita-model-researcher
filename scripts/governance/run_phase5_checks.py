#!/usr/bin/env python3
"""
Run Phase 5 governance checks in sequence and optionally emit reports.

Checks:
- Model schema validation (agents-toolchain/governance/validate_models_cli.py)
- Taxonomy coverage (agents-toolchain/governance/check_coverage.py)
- Sensitive data scan (tools/check_sensitive.py)
- Ownership validation (scripts/governance/validate_ownership.py)

Usage:
  python scripts/governance/run_phase5_checks.py [--report] [--threshold 0.95]
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def run(cmd: list[str]) -> int:
    print(f"\n>>> RUN: {' '.join(cmd)}")
    p = subprocess.run(cmd)
    return p.returncode


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--report', action='store_true')
    p.add_argument('--threshold', type=float, default=0.95)
    args = p.parse_args()

    failures = 0

    # 1) Validate models schema
    vm_cli = [sys.executable, str(ROOT / 'agents-toolchain' / 'governance' / 'validate_models_cli.py')]
    if args.report:
        vm_cli.append('--report')
    failures += (run(vm_cli) != 0)

    # 2) Taxonomy coverage
    cov_cli = [sys.executable, str(ROOT / 'agents-toolchain' / 'governance' / 'check_coverage.py'), '--threshold', str(args.threshold)]
    failures += (run(cov_cli) != 0)

    # 3) Sensitive check (non-fatal, but report)
    sens = [sys.executable, str(ROOT / 'tools' / 'check_sensitive.py')]
    run(sens)

    # 4) Ownership validation
    own = [sys.executable, str(ROOT / 'scripts' / 'governance' / 'validate_ownership.py')]
    if args.report:
        own.append('--report')
    failures += (run(own) != 0)

    if failures:
        print(f"\nPhase 5 checks: FAILED ({failures} failing step(s))")
        raise SystemExit(2)
    print("\nPhase 5 checks: OK")


if __name__ == '__main__':
    main()

