import glob
import json
import os
import sys
import re
import difflib
from jsonschema import validate, ValidationError

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SCHEMA_PATH = os.path.join(ROOT, "templates", "model_schema.json")
MODELS_GLOB = os.path.join(ROOT, "models", "*.json")
BENCHMARKS_DIR = os.path.join(ROOT, "benchmarks")
ABILITIES_PATH = os.path.join(ROOT, "templates", "abilities.json")
INDICATORS_DIR = os.path.join(ROOT, "indicators")

def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def collect_benchmarks(dir_path):
    names = set()
    # map of normalized -> set(original)
    normalized_map = {}
    for entry in os.scandir(dir_path):
        if not (entry.is_file() and entry.name.endswith('.json')):
            continue
        stem = os.path.splitext(entry.name)[0]
        names.add(stem)
        # try to load file and capture any explicit id field
        try:
            with open(entry.path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            bid = None
            if isinstance(data, dict):
                bid = data.get('id') or data.get('benchmark_id')
            if bid:
                # allow both filename stem and declared id
                if isinstance(bid, str):
                    names.add(bid)
        except Exception:
            # non-fatal: keep filename stem
            pass
        # add normalized mapping
        n = normalize_id(stem)
        normalized_map.setdefault(n, set()).add(stem)
    return names, normalized_map


def normalize_id(s: str) -> str:
    if not isinstance(s, str):
        return ''
    s = s.strip()
    # Unicode normalization and casefolding would be ideal; do simple casefold
    s = s.casefold()
    # replace separators with underscore
    s = re.sub(r"[\s\-]+", "_", s)
    # remove characters not alnum or underscore
    s = re.sub(r"[^0-9a-z_]+", "", s)
    return s


def collect_abilities(path):
    try:
        data = load(path)
        if isinstance(data, list):
            return {item.get('id') for item in data if isinstance(item, dict) and item.get('id')}
    except Exception:
        pass
    return set()


def main():
    schema = load(SCHEMA_PATH)
    model_paths = sorted(glob.glob(MODELS_GLOB))
    known_benchmarks, normalized_benchmarks = collect_benchmarks(BENCHMARKS_DIR)
    # load optional aliases file
    aliases_path = os.path.join(ROOT, "benchmarks", "aliases.json")
    aliases = {}
    if os.path.exists(aliases_path):
        try:
            aliases = load(aliases_path)
        except Exception:
            aliases = {}
    known_abilities = collect_abilities(ABILITIES_PATH)
    ok = True
    for m in model_paths:
        try:
            data = load(m)
            validate(instance=data, schema=schema)
            # cross-check evaluation.benchmarks entries exist in benchmarks/*
            eval_bm = ((data.get('evaluation') or {}).get('benchmarks')) or []
            for b in eval_bm:
                if b in known_benchmarks:
                    continue
                # resolve via aliases
                if aliases and isinstance(aliases, dict) and b in aliases:
                    target = aliases[b]
                    if target in known_benchmarks:
                        print(f"XREF WARN: {m} references benchmark alias '{b}' -> '{target}'.")
                        continue
                # try normalized exact match
                nb = normalize_id(b)
                if nb in normalized_benchmarks:
                    candidates = sorted(normalized_benchmarks[nb])
                    print(f"XREF WARN: {m} references benchmark '{b}' which normalizes to '{nb}'. Candidates: {candidates}. Consider using '{candidates[0]}'.")
                    continue
                # fuzzy suggestions
                candidates = difflib.get_close_matches(b, sorted(known_benchmarks), n=3, cutoff=0.6)
                if candidates:
                    print(f"XREF ERROR: {m} references unknown benchmark '{b}'. Did you mean: {candidates} ?")
                else:
                    print(f"XREF ERROR: {m} references unknown benchmark '{b}'.")
                ok = False
            # optional: check required_capabilities if present
            req_caps = data.get('required_capabilities') or []
            if req_caps and known_abilities:
                for cid in req_caps:
                    if cid not in known_abilities:
                        ok = False
                        print(f"XREF ERROR: {m} references unknown capability id '{cid}'.")
            print(f"VALID: {m}")
        except ValidationError as e:
            ok = False
            print(f"INVALID: {m}\n  {e.message}")
        except Exception as e:
            ok = False
            print(f"ERROR reading {m}: {e}")
    if not ok:
        sys.exit(2)

    # Extend: validate indicators' run_script_ref
    ind_ok = True
    for entry in os.scandir(INDICATORS_DIR):
        if not (entry.is_file() and entry.name.endswith('.json')):
            continue
        path = entry.path
        try:
            data = load(path)
            rsr = data.get('run_script_ref') or {}
            script_rel = rsr.get('script')
            if script_rel:
                script_abs = os.path.join(ROOT, script_rel.replace('/', os.sep))
                if not os.path.exists(script_abs):
                    ind_ok = False
                    print(f"XREF ERROR: {path} run_script_ref.script not found: {script_rel}")
            else:
                # If tooling present but run_script_ref missing, warn (Phase 2 expectation)
                if data.get('tooling'):
                    print(f"WARN: {path} has 'tooling' but missing 'run_script_ref'.")
        except Exception as e:
            ind_ok = False
            print(f"ERROR reading {path}: {e}")

    if not ind_ok:
        sys.exit(3)

if __name__ == '__main__':
    main()
