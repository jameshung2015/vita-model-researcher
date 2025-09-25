import glob
import json
import os
import sys
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
    for entry in os.scandir(dir_path):
        if entry.is_file() and entry.name.endswith('.json'):
            names.add(os.path.splitext(entry.name)[0])
    return names


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
    known_benchmarks = collect_benchmarks(BENCHMARKS_DIR)
    known_abilities = collect_abilities(ABILITIES_PATH)
    ok = True
    for m in model_paths:
        try:
            data = load(m)
            validate(instance=data, schema=schema)
            # cross-check evaluation.benchmarks entries exist in benchmarks/*
            eval_bm = ((data.get('evaluation') or {}).get('benchmarks')) or []
            for b in eval_bm:
                if b not in known_benchmarks:
                    ok = False
                    print(f"XREF ERROR: {m} references unknown benchmark '{b}'.")
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
