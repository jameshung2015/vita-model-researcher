# agents-toolchain

First-phase tooling that supports foundational research workflows described in `agentToolrequirement.md`.

## Multi-Source Intelligence Aggregator
`python agents-toolchain/intel_aggregator.py ingest model "Qwen3-8B" HuggingFace https://huggingface.co/Qwen/Qwen3-8B --field license=Apache-2.0 --field architecture=Decoder --summary "Open 8B chat model with 32k context" --author lj`
- Appends structured rows to `agents-toolchain/storage/intel_entries.jsonl` with timestamps and URLs.
- `compare` renders side-by-side Markdown across sources: `python agents-toolchain/intel_aggregator.py compare "Qwen3-8B"`
- `verify` captures manual validation: `python agents-toolchain/intel_aggregator.py verify <entry_id> --actor lj`
- `link` pushes a recorded entry into the taxonomy as an example instance.

## Collaborative Taxonomy Builder
`python agents-toolchain/taxonomy_builder.py add-tag perception.lidar --definition "Scene perception using LiDAR sensors" --author lj`
- Maintains `agents-toolchain/taxonomy/taxonomy.json` with history and parent/child relationships.
- `update-tag` revises definitions or parents while tracking authorship.
- `link-instance` associates models/scenes with tags and writes traceability metadata.
- `snapshot` exports frozen baselines into `agents-toolchain/taxonomy/versions/` for milestone reviews.

## Workflow Tips
1. Capture external research with `intel_aggregator.py ingest`, then review using `compare` to detect conflicts.
2. After analyst review, run `verify` to mark trusted sources and `link` to create taxonomy references without retyping metadata.
3. Use taxonomy history when preparing governance reviews; `history` highlights who modified definitions and when.
4. Commit the JSONL/JSON artifacts alongside documentation updates so downstream tooling (schemas, benchmarks) can consume consistent taxonomies.
