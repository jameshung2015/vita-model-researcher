import json, sys, argparse, time
from pathlib import Path

# NOTE: Network access may be restricted. This stub reads from a saved snapshot or placeholder.
# Replace `_load_leaderboard()` with real fetch/parsing when API/HTML structure is available.

def _load_leaderboard(snapshot: Path | None):
    if snapshot and snapshot.exists():
        with open(snapshot, 'r', encoding='utf-8') as f:
            return json.load(f)
    # Fallback placeholder structure
    return [
        {"model": "Llama-3-70B-Instruct", "elo": 1250.3, "rank": 5, "votes": 12000, "win_rate": 0.56},
        {"model": "GPT-4o", "elo": 1325.8, "rank": 2, "votes": 20000, "win_rate": 0.61}
    ]


def main():
    p = argparse.ArgumentParser(description='Pull LM Arena leaderboard snapshot (stub).')
    p.add_argument('--models', type=str, default='', help='Comma-separated model names to filter')
    p.add_argument('--out', type=Path, required=True, help='Output JSON/JSONL path')
    p.add_argument('--fields', type=str, default='model,elo,rank,votes,win_rate', help='Fields to keep')
    p.add_argument('--from-snapshot', type=Path, default=None, help='Existing local snapshot JSON to load')
    args = p.parse_args()

    models = [m.strip() for m in args.models.split(',') if m.strip()] if args.models else []
    keep = [f.strip() for f in args.fields.split(',') if f.strip()]

    data = _load_leaderboard(args.from_snapshot)
    ts = int(time.time())

    rows = []
    for row in data:
        if models and row.get('model') not in models:
            continue
        out = {k: row.get(k) for k in keep if k in row}
        out['snapshot_ts'] = ts
        rows.append(out)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    # JSON array for simplicity
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)

    print(f'Wrote {len(rows)} records to {args.out}')


if __name__ == '__main__':
    main()
