#!/usr/bin/env python3
"""
Generate a Phase 2 + Phase 3 check summary after research ingestion.

Writes to reports/phase_checks_<ts>/summary.md
"""
from pathlib import Path
import re
import subprocess
import time


ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'reports'


def newest_dir(prefix: str) -> Path | None:
    dirs = sorted([p for p in REPORTS.glob(f'{prefix}_*') if p.is_dir()], key=lambda p: p.stat().st_mtime, reverse=True)
    return dirs[0] if dirs else None


def run_validator() -> Path | None:
    cmd = ['python', str(ROOT / 'agents-toolchain' / 'governance' / 'validate_models_cli.py'), '--report']
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    # Try to extract reports/validation_<ts> from output
    m = re.search(r'reports\\validation_(\d+)', proc.stdout + proc.stderr)
    if m:
        return REPORTS / f'validation_{m.group(1)}'
    return newest_dir('validation')


def find_latest_qwen3_phase3() -> Path | None:
    dirs = sorted([p for p in REPORTS.glob('qwen3_phase3_*') if p.is_dir()], key=lambda p: p.stat().st_mtime, reverse=True)
    return dirs[0] if dirs else None


def main():
    ts = int(time.time())
    out_dir = REPORTS / f'phase_checks_{ts}'
    out_dir.mkdir(parents=True, exist_ok=True)

    ingest_dir = newest_dir('doc_eval_ingest')
    val_dir = run_validator()
    qwen3_dir = find_latest_qwen3_phase3()

    lines = [
        '# Phase 2/3 Checks Summary',
        '',
        'Research Ingestion',
        f'- Ingestion report: {ingest_dir.relative_to(ROOT) if ingest_dir else "(none)"}',
        '',
        'Phase 2 (Validation)',
        f'- Validation report: {val_dir.relative_to(ROOT) if val_dir else "(none)"}',
        '',
        'Phase 3 (Qwen3 smoke)',
        f'- Qwen3 reports: {qwen3_dir.relative_to(ROOT) if qwen3_dir else "(none)"}',
        '',
        'Notes',
        '- Benchmarks updated with research_doc links to doc-eval-system.',
        '- Indicators unified for win_rate/elo via runner.',
        '- LM Arena snapshots retained under benchmarks/snapshots/lmarena/.',
    ]
    (out_dir / 'summary.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'Wrote {out_dir / "summary.md"}')


if __name__ == '__main__':
    main()

