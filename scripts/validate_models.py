import json
import sys
from jsonschema import validate, ValidationError

SCHEMA_PATH = "../templates/model_schema.json"
MODELS = ["../models/kimi-vl.json","../models/whisper_asr.json"]

def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    schema = load(SCHEMA_PATH)
    ok = True
    for m in MODELS:
        try:
            data = load(m)
            validate(instance=data, schema=schema)
            print(f"VALID: {m}")
        except ValidationError as e:
            ok = False
            print(f"INVALID: {m}\n  {e.message}")
        except Exception as e:
            ok = False
            print(f"ERROR reading {m}: {e}")
    if not ok:
        sys.exit(2)

if __name__ == '__main__':
    main()
