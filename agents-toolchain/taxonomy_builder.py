#!/usr/bin/env python3
"""Collaborative taxonomy builder for agent toolchain."""
import argparse
import json
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

BASE_DIR = Path(__file__).parent
TAXONOMY_DIR = BASE_DIR / "taxonomy"
TAXONOMY_PATH = TAXONOMY_DIR / "taxonomy.json"
CHANGELOG_PATH = TAXONOMY_DIR / "changelog.jsonl"
VERSIONS_DIR = TAXONOMY_DIR / "versions"


@dataclass
class HistoryEntry:
    action: str
    author: Optional[str]
    details: Dict

    def to_dict(self) -> Dict:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": self.action,
            "author": self.author,
            "details": self.details,
        }


def ensure_taxonomy() -> None:
    TAXONOMY_DIR.mkdir(parents=True, exist_ok=True)
    VERSIONS_DIR.mkdir(parents=True, exist_ok=True)
    if not TAXONOMY_PATH.exists():
        TAXONOMY_PATH.write_text(
            json.dumps({"meta": {"version": 1, "updated_at": None}, "tags": {}}, indent=2),
            encoding="utf-8",
        )
    if not CHANGELOG_PATH.exists():
        CHANGELOG_PATH.touch()


def load_taxonomy() -> Dict:
    ensure_taxonomy()
    with TAXONOMY_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_taxonomy(data: Dict) -> None:
    ensure_taxonomy()
    meta = data.setdefault("meta", {})
    meta["version"] = meta.get("version", 0) + 1
    meta["updated_at"] = datetime.now(timezone.utc).isoformat()
    with TAXONOMY_PATH.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def write_changelog(entry: HistoryEntry) -> None:
    ensure_taxonomy()
    with CHANGELOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry.to_dict(), ensure_ascii=False))
        handle.write("\n")


def add_tag(args: argparse.Namespace) -> None:
    taxonomy = load_taxonomy()
    tags = taxonomy.setdefault("tags", {})
    if args.tag in tags:
        raise SystemExit(f"Tag '{args.tag}' already exists.")
    parent = args.parent
    if parent and parent not in tags:
        raise SystemExit(f"Parent tag '{parent}' does not exist.")
    tag_entry = {
        "tag": args.tag,
        "display_name": args.display_name or args.tag.title().replace("_", " "),
        "definition": args.definition,
        "parent": parent,
        "children": [],
        "linked_instances": [],
        "history": [],
    }
    history = HistoryEntry(
        action="created",
        author=args.author,
        details={"definition": args.definition, "parent": parent},
    )
    tag_entry["history"].append(history.to_dict())
    tags[args.tag] = tag_entry
    if parent:
        parent_children = tags[parent].setdefault("children", [])
        if args.tag not in parent_children:
            parent_children.append(args.tag)
    save_taxonomy(taxonomy)
    write_changelog(HistoryEntry(
        action="tag_created",
        author=args.author,
        details={"tag": args.tag, "parent": parent},
    ))
    print(f"Added tag '{args.tag}'.")


def update_tag(args: argparse.Namespace) -> None:
    taxonomy = load_taxonomy()
    tags = taxonomy.get("tags", {})
    if args.tag not in tags:
        raise SystemExit(f"Tag '{args.tag}' does not exist.")
    tag_entry = tags[args.tag]
    details = {}
    if args.definition is not None:
        tag_entry["definition"] = args.definition
        details["definition"] = args.definition
    if args.display_name is not None:
        tag_entry["display_name"] = args.display_name
        details["display_name"] = args.display_name
    if args.parent is not None:
        parent = args.parent or None
        if parent and parent not in tags:
            raise SystemExit(f"Parent tag '{parent}' does not exist.")
        old_parent = tag_entry.get("parent")
        if old_parent and old_parent in tags:
            children = tags[old_parent].setdefault("children", [])
            if args.tag in children:
                children.remove(args.tag)
        if parent:
            new_children = tags[parent].setdefault("children", [])
            if args.tag not in new_children:
                new_children.append(args.tag)
        tag_entry["parent"] = parent
        details["parent"] = parent
    if not details:
        print("No changes requested.")
        return
    tag_entry.setdefault("history", []).append(
        HistoryEntry(action="updated", author=args.author, details=details).to_dict()
    )
    save_taxonomy(taxonomy)
    details_copy = {**details, "tag": args.tag}
    write_changelog(HistoryEntry(action="tag_updated", author=args.author, details=details_copy))
    print(f"Updated tag '{args.tag}'.")


def attach_instance(
    tag: str,
    entity_type: str,
    entity_name: str,
    author: Optional[str] = None,
    notes: Optional[str] = None,
    source_entry_id: Optional[str] = None,
    source_url: Optional[str] = None,
) -> None:
    if entity_type not in {"model", "scene"}:
        raise SystemExit("entity_type must be 'model' or 'scene'.")
    taxonomy = load_taxonomy()
    tags = taxonomy.get("tags", {})
    if tag not in tags:
        raise SystemExit(f"Tag '{tag}' does not exist.")
    record = {
        "entity_type": entity_type,
        "entity_name": entity_name,
        "notes": notes,
        "source_entry_id": source_entry_id,
        "source_url": source_url,
        "linked_at": datetime.now(timezone.utc).isoformat(),
        "author": author,
    }
    instances = tags[tag].setdefault("linked_instances", [])
    already_present = any(
        item.get("entity_type") == entity_type
        and item.get("entity_name") == entity_name
        and item.get("source_entry_id") == source_entry_id
        for item in instances
    )
    if already_present:
        print("Instance already linked; skipping duplicate.")
        return
    instances.append(record)
    history_entry = HistoryEntry(
        action="instance_linked",
        author=author,
        details={
            "entity_type": entity_type,
            "entity_name": entity_name,
            "source_entry_id": source_entry_id,
        },
    )
    tags[tag].setdefault("history", []).append(history_entry.to_dict())
    save_taxonomy(taxonomy)
    write_changelog(
        HistoryEntry(
            action="instance_linked",
            author=author,
            details={
                "tag": tag,
                "entity_type": entity_type,
                "entity_name": entity_name,
                "source_entry_id": source_entry_id,
            },
        )
    )


def link_instance_cli(args: argparse.Namespace) -> None:
    attach_instance(
        tag=args.tag,
        entity_type=args.entity_type,
        entity_name=args.entity_name,
        author=args.author,
        notes=args.notes,
        source_entry_id=args.source_entry_id,
        source_url=args.source_url,
    )
    print(
        f"Linked {args.entity_type} '{args.entity_name}' to tag '{args.tag}'."
    )


def show_history(args: argparse.Namespace) -> None:
    taxonomy = load_taxonomy()
    tags = taxonomy.get("tags", {})
    if args.tag not in tags:
        raise SystemExit(f"Tag '{args.tag}' does not exist.")
    print(f"History for tag '{args.tag}':")
    for item in tags[args.tag].get("history", []):
        timestamp = item.get("timestamp")
        action = item.get("action")
        author = item.get("author") or "unknown"
        details = item.get("details", {})
        print(f"- {timestamp} | {action} | author={author} | details={details}")


def list_tags(args: argparse.Namespace) -> None:
    taxonomy = load_taxonomy()
    tags = taxonomy.get("tags", {})
    if not tags:
        print("No tags defined yet.")
        return
    for tag, payload in sorted(tags.items()):
        parent = payload.get("parent") or "root"
        child_count = len(payload.get("children", []))
        instance_count = len(payload.get("linked_instances", []))
        print(
            f"- {tag} (parent={parent}, children={child_count}, instances={instance_count})"
        )


def snapshot(args: argparse.Namespace) -> None:
    ensure_taxonomy()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    label = args.label or "baseline"
    snapshot_name = f"taxonomy_{label}_{timestamp}.json"
    destination = VERSIONS_DIR / snapshot_name
    shutil.copyfile(TAXONOMY_PATH, destination)
    write_changelog(
        HistoryEntry(
            action="snapshot",
            author=args.author,
            details={"label": label, "path": destination.as_posix()},
        )
    )
    print(f"Snapshot written to {destination}.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Collaborative taxonomy builder.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add-tag", help="Create a new taxonomy tag.")
    add_parser.add_argument("tag", help="Canonical tag identifier (use dot or snake_case).")
    add_parser.add_argument("--display-name", help="Human readable name for the tag.")
    add_parser.add_argument("--definition", required=True, help="Tag definition text.")
    add_parser.add_argument("--parent", help="Optional parent tag.")
    add_parser.add_argument("--author", help="Who is adding this tag.")
    add_parser.set_defaults(func=add_tag)

    update_parser = subparsers.add_parser("update-tag", help="Modify an existing tag.")
    update_parser.add_argument("tag", help="Tag identifier to update.")
    update_parser.add_argument("--definition", help="New definition text.")
    update_parser.add_argument("--display-name", help="New display name.")
    update_parser.add_argument(
        "--parent",
        help="Move the tag under a new parent (use empty string to promote to root).",
    )
    update_parser.add_argument("--author", help="Who is making the change.")
    update_parser.set_defaults(func=update_tag)

    link_parser = subparsers.add_parser(
        "link-instance", help="Link an instance (model/scene) to a taxonomy tag."
    )
    link_parser.add_argument("tag", help="Tag identifier.")
    link_parser.add_argument("entity_type", choices=["model", "scene"], help="Instance type.")
    link_parser.add_argument("entity_name", help="Instance name.")
    link_parser.add_argument("--notes", help="Optional annotation for the link.")
    link_parser.add_argument("--author", help="Who is linking the instance.")
    link_parser.add_argument(
        "--source-entry-id",
        help="Optional reference to aggregator entry id for traceability.",
    )
    link_parser.add_argument("--source-url", help="Optional reference URL.")
    link_parser.set_defaults(func=link_instance_cli)

    history_parser = subparsers.add_parser("history", help="Show change history for a tag.")
    history_parser.add_argument("tag", help="Tag identifier.")
    history_parser.set_defaults(func=show_history)

    list_parser = subparsers.add_parser("list", help="List tags with summary stats.")
    list_parser.set_defaults(func=list_tags)

    snapshot_parser = subparsers.add_parser("snapshot", help="Snapshot taxonomy to versions folder.")
    snapshot_parser.add_argument("--label", help="Label for the snapshot (default: baseline).")
    snapshot_parser.add_argument("--author", help="Who is triggering the snapshot.")
    snapshot_parser.set_defaults(func=snapshot)

    return parser


def main(argv: List[str]) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main(sys.argv[1:])
