#!/usr/bin/env python3
"""Intelligence aggregator for first-phase agent toolchain."""
import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List

BASE_DIR = Path(__file__).parent
STORAGE_DIR = BASE_DIR / "storage"
ENTRY_PATH = STORAGE_DIR / "intel_entries.jsonl"


def ensure_storage() -> None:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    ENTRY_PATH.touch(exist_ok=True)


def load_entries() -> List[Dict]:
    ensure_storage()
    entries: List[Dict] = []
    with ENTRY_PATH.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise SystemExit(f"Failed to parse entry line: {line}\n{exc}")
    return entries


def write_entries(entries: Iterable[Dict]) -> None:
    ensure_storage()
    with ENTRY_PATH.open("w", encoding="utf-8") as handle:
        for entry in entries:
            handle.write(json.dumps(entry, ensure_ascii=False))
            handle.write("\n")


def parse_key_values(pairs: Iterable[str]) -> Dict[str, str]:
    data: Dict[str, str] = {}
    if not pairs:
        return data
    for item in pairs:
        if "=" not in item:
            raise SystemExit(f"Invalid field '{item}'. Expected format key=value.")
        key, value = item.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise SystemExit(f"Missing key in field '{item}'.")
        data[key] = value
    return data


def ingest(args: argparse.Namespace) -> None:
    ensure_storage()
    fields = parse_key_values(args.field)
    timestamp = datetime.now(timezone.utc).isoformat()
    entry = {
        "entry_id": args.entry_id or uuid.uuid4().hex[:10],
        "entity_type": args.entity_type,
        "entity_name": args.name,
        "source": args.source,
        "source_type": args.source_type,
        "url": args.url,
        "summary": args.summary,
        "notes": args.notes,
        "fields": fields,
        "collected_at": timestamp,
        "collected_by": args.author,
        "verified": False,
        "verified_by": None,
        "verified_at": None,
        "linked_tags": [],
        "tags": args.tag or [],
    }
    with ENTRY_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False))
        handle.write("\n")
    print(f"Recorded entry {entry['entry_id']} for {entry['entity_type']} '{entry['entity_name']}'.")


def list_entries(args: argparse.Namespace) -> None:
    entries = load_entries()
    filtered = []
    for entry in entries:
        if args.entity_type and entry["entity_type"] != args.entity_type:
            continue
        if args.name and entry["entity_name"].lower() != args.name.lower():
            continue
        filtered.append(entry)
    if not filtered:
        print("No entries found for the given filters.")
        return
    for entry in filtered:
        verified_flag = "yes" if entry.get("verified") else "no"
        print(
            f"- {entry['entry_id']} | {entry['entity_type']} | {entry['entity_name']} | "
            f"source={entry['source']} | verified={verified_flag}"
        )


def compare(args: argparse.Namespace) -> None:
    entries = load_entries()
    matches = []
    for entry in entries:
        if entry["entity_name"].lower() != args.name.lower():
            continue
        if args.entity_type and entry["entity_type"] != args.entity_type:
            continue
        matches.append(entry)
    if not matches:
        print("No entries available for comparison.")
        return
    matches.sort(key=lambda item: item["source"])
    sources = [m["source"] for m in matches]
    field_keys = set()
    for match in matches:
        field_keys.update(match.get("fields", {}).keys())
    include_notes = any(m.get("notes") for m in matches)
    include_summary = any(m.get("summary") for m in matches)
    include_verified = any(m.get("verified") for m in matches)
    rows = []
    if include_summary:
        rows.append(("summary", [m.get("summary", "") or "" for m in matches]))
    for key in sorted(field_keys):
        rows.append((key, [m.get("fields", {}).get(key, "") for m in matches]))
    if include_notes:
        rows.append(("notes", [m.get("notes", "") or "" for m in matches]))
    if include_verified:
        rows.append(("verified", ["yes" if m.get("verified") else "no" for m in matches]))
    header = "| Field | " + " | ".join(sources) + " |"
    divider = "|---|" + "---|" * len(sources)
    print(f"## Comparison for {matches[0]['entity_type']} '{args.name}'\n")
    print(header)
    print(divider)
    for field, values in rows:
        printable = [v.replace("|", "/") if isinstance(v, str) else str(v) for v in values]
        print(f"| {field} | " + " | ".join(printable) + " |")


def update_entry(entry_id: str, mutate) -> bool:
    entries = load_entries()
    changed = False
    for entry in entries:
        if entry["entry_id"] == entry_id:
            mutate(entry)
            changed = True
            break
    if not changed:
        return False
    write_entries(entries)
    return True


def verify(args: argparse.Namespace) -> None:
    if not args.revoke and not args.actor:
        raise SystemExit("--actor is required when marking an entry as verified.")
    timestamp = datetime.now(timezone.utc).isoformat()

    def mutate(entry: Dict) -> None:
        entry["verified"] = not args.revoke
        entry["verified_by"] = None if args.revoke else args.actor
        entry["verified_at"] = None if args.revoke else timestamp

    if not update_entry(args.entry_id, mutate):
        raise SystemExit(f"Entry {args.entry_id} not found.")
    status = "revoked" if args.revoke else "verified"
    print(f"Verification {status} for entry {args.entry_id}.")


def link_to_taxonomy(args: argparse.Namespace) -> None:
    try:
        from taxonomy_builder import attach_instance
    except ImportError as exc:
        raise SystemExit(f"Unable to import taxonomy_builder: {exc}")

    entries = load_entries()
    target = next((item for item in entries if item["entry_id"] == args.entry_id), None)
    if not target:
        raise SystemExit(f"Entry {args.entry_id} not found.")

    author = args.author or target.get("collected_by")
    instance_name = args.instance_name or target["entity_name"]
    attach_instance(
        tag=args.tag,
        entity_type=target["entity_type"],
        entity_name=instance_name,
        author=author,
        notes=args.notes,
        source_entry_id=target["entry_id"],
        source_url=target.get("url"),
    )

    def mutate(entry: Dict) -> None:
        linked_tags = entry.setdefault("linked_tags", [])
        if args.tag not in linked_tags:
            linked_tags.append(args.tag)

    update_entry(target["entry_id"], mutate)
    print(
        f"Linked entry {target['entry_id']} to taxonomy tag '{args.tag}' "
        f"for {target['entity_type']} '{instance_name}'."
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Multi-source intelligence aggregator tooling."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser("ingest", help="Record a new source entry.")
    ingest_parser.add_argument("entity_type", choices=["model", "scene"], help="Entity type.")
    ingest_parser.add_argument("name", help="Entity name.")
    ingest_parser.add_argument("source", help="Source name (e.g. arXiv, HuggingFace).")
    ingest_parser.add_argument("url", help="Source URL.")
    ingest_parser.add_argument(
        "--source-type",
        default="external",
        choices=["external", "internal", "vendor"],
        help="Classify the source category.",
    )
    ingest_parser.add_argument(
        "--field",
        action="append",
        help="Structured field entry in key=value form. Repeat for multiple fields.",
    )
    ingest_parser.add_argument("--summary", help="Short summary from the source.")
    ingest_parser.add_argument("--notes", help="Analyst notes or caveats.")
    ingest_parser.add_argument("--author", help="Collector name or initials.")
    ingest_parser.add_argument("--tag", action="append", help="Label entry with quick tags.")
    ingest_parser.add_argument("--entry-id", help="Optional explicit entry id for imports.")
    ingest_parser.set_defaults(func=ingest)

    list_parser = subparsers.add_parser("list", help="List stored entries.")
    list_parser.add_argument("--entity-type", choices=["model", "scene"], help="Filter by type.")
    list_parser.add_argument("--name", help="Filter by exact entity name.")
    list_parser.set_defaults(func=list_entries)

    compare_parser = subparsers.add_parser("compare", help="Render side-by-side comparison.")
    compare_parser.add_argument("name", help="Entity name to compare.")
    compare_parser.add_argument(
        "--entity-type", choices=["model", "scene"], help="Optional entity type filter."
    )
    compare_parser.set_defaults(func=compare)

    verify_parser = subparsers.add_parser("verify", help="Mark or revoke verification.")
    verify_parser.add_argument("entry_id", help="Entry identifier to update.")
    verify_parser.add_argument("--actor", help="Verifier name.")
    verify_parser.add_argument(
        "--revoke", action="store_true", help="Revoke verification instead of adding."
    )
    verify_parser.set_defaults(func=verify)

    link_parser = subparsers.add_parser(
        "link", help="Link an entry to a taxonomy tag as reference instance."
    )
    link_parser.add_argument("entry_id", help="Aggregator entry identifier.")
    link_parser.add_argument("tag", help="Taxonomy tag to link against.")
    link_parser.add_argument(
        "--instance-name",
        help="Override instance name when linking (defaults to entry entity name).",
    )
    link_parser.add_argument("--author", help="Author recorded in taxonomy history.")
    link_parser.add_argument(
        "--notes",
        help="Optional notes stored alongside the linked instance in the taxonomy.",
    )
    link_parser.set_defaults(func=link_to_taxonomy)

    return parser


def main(argv: List[str]) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main(sys.argv[1:])
