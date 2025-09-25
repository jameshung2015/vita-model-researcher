#!/usr/bin/env python3
"""
Scan repository for files that should be ignored or may contain personal/sensitive data.
Prints findings and exits with code 0 (no issues) or 2 (issues found).

Usage:
  python tools/check_sensitive.py

This is a lightweight helper — not a replacement for proper secret scanning tools.
"""
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

IGNORED_NAMES = {
    '.env', 'id_rsa', 'id_ed25519', 'credentials.json', 'secrets.json'
}

SENSITIVE_EXTS = {'.pem', '.key', '.p12'}

EMAIL_RE = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
AWS_KEY_RE = re.compile(r'AKIA[0-9A-Z]{16}')
PRIVATE_KEY_HEADER = re.compile(r'-----BEGIN (RSA |)?PRIVATE KEY-----')


SKIP_DIR_PARTS = {'.git', 'node_modules', '.venv', 'venv', '__pycache__'}


def scan_files():
    findings = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        # prune unwanted directories in-place
        parts = set(dirpath.split(os.sep))
        if parts & SKIP_DIR_PARTS:
            continue
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_PARTS]
        for fn in filenames:
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, ROOT)
            lname = fn.lower()

            # name-based checks
            if fn in IGNORED_NAMES or lname in IGNORED_NAMES:
                findings.append((rel, 'sensitive filename'))
                continue
            if any(lname.endswith(ext) for ext in SENSITIVE_EXTS):
                findings.append((rel, 'sensitive extension'))
                continue

            # quick content checks for likely secrets
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    data = f.read()
            except Exception:
                continue

            if PRIVATE_KEY_HEADER.search(data):
                findings.append((rel, 'private key header in file'))
                continue
            if AWS_KEY_RE.search(data):
                findings.append((rel, 'possible AWS access key'))
            if EMAIL_RE.search(data):
                # only report emails in reasonably small, repo-authored files (not vendored)
                if len(data) < 5000 and not rel.startswith('.venv' + os.sep):
                    findings.append((rel, 'email address found'))

    return findings


def main():
    findings = scan_files()
    if not findings:
        print('No likely sensitive files found.')
        return 0

    print('Potential sensitive files found:')
    for path, reason in findings:
        print(f' - {path}: {reason}')

    print('\nRecommendation:')
    print(' - Move these files outside the repo or add to .gitignore if they must remain local.')
    print(' - Rotate any exposed credentials immediately.')
    return 2


if __name__ == '__main__':
    rc = main()
    sys.exit(rc)
