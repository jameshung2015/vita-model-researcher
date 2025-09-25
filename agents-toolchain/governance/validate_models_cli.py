#!/usr/bin/env python3
"""Wrapper CLI to run scripts/validate_models.py and optionally write a report.

Usage:
  - Quick:    python agents-toolchain/governance/validate_models_cli.py
  - With report: python agents-toolchain/governance/validate_models_cli.py --report
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path


def run_validator(root: Path) -> tuple[int, str]:
    """Run scripts/validate_models.py and capture combined stdout/stderr."""
    script = root / 'scripts' / 'validate_models.py'
    if not script.exists():
        return 1, f"validator not found: {script}"
    try:
        p = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
        out = (p.stdout or '') + (p.stderr or '')
        return p.returncode, out
    except Exception as e:
        return 1, f"error running validator: {e}"


def write_report(root: Path, exit_code: int, text: str) -> Path:
    ts = int(time.time())
    out_dir = root / 'reports' / f'validation_{ts}'
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = out_dir / 'validation.log'
    log_path.write_text(text, encoding='utf-8')
    # Summarize
    valid = text.count('VALID: ')
    invalid = text.count('INVALID: ')
    errors = sum(1 for line in text.splitlines() if line.startswith('ERROR'))
    xrefs = text.count('XREF ERROR')
    summary = [
        '# Validation Summary',
        '',
        f'Exit code: {exit_code}',
        f'- VALID count: {valid}',
        f'- INVALID count: {invalid}',
        f'- ERROR lines: {errors}',
        f'- XREF ERROR lines: {xrefs}',
        '',
        'See validation.log for details.'
    ]
    (out_dir / 'summary.md').write_text('\n'.join(summary), encoding='utf-8')
    return out_dir


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--report', action='store_true', help='Write report under reports/validation_<ts>')
    args = p.parse_args()
    root = Path(__file__).resolve().parents[2]

    code, text = run_validator(root)
    print(text, end='')
    if args.report:
        out_dir = write_report(root, code, text)
        print(f"\nReport written to {out_dir}")
    sys.exit(code)


if __name__ == '__main__':
    main()

