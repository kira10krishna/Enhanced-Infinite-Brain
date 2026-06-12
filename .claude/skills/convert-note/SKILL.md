---
name: convert-note
description: Ingest a raw source (a file in raw/, pasted text, or a URL) into the typed knowledge graph — decompose it into atomic typed nodes, write frontmatter and typed edges, link to existing nodes, create a source node, update INDEX, move the original to raw/processed, and append to LOG. Use whenever the user wants to add/ingest/process a document, article, paper, transcript, or note into the vault/second brain.
---

# /convert-note

Turn raw source material into atomic typed nodes. This is the core ingest pipeline. Implements [AGENTS.md](../../../_system/AGENTS.md) §2.1.

## Inputs
- `$ARGUMENTS`: a path under `raw/`, pasted text, or a URL. If empty, ask what to ingest.
- Optional `--mode supervised|hybrid|autonomous` (default: the mode in AGENTS.md §0, currently `supervised`).

## Before you start
Read these every run (they are the rules):
- `_system/SCHEMA.md` — valid node types, edge types, frontmatter, confidence guide.
- `_system/AGENTS.md` — workflow modes, edge/confidence discipline, hard rules.
- `_system/INDEX.md` — existing nodes, so new edges can target them.

## Steps

1. **Read** the source fully. For large files, page through — don't decompose from a partial view.
2. **Decompose** into *atomic* concepts — **one concept per node** (SCHEMA §7, 50–300 lines). A document covering several distinct ideas becomes several nodes, not one.
3. **Type** each node (SCHEMA §1). Use the "Distinct from" column when torn between two types.
   - **Fidelity rules:** Do **not** mint a `pillar` from a source — pillars encode the *user's* foundational beliefs. Do **not** mint a `decision` for choices made by actors *inside* a source — those are `event`s. Forecasts → `hypothesis`; cited real-world claims → `fact`; defined mechanisms → `concept`; dated beats → `event`.
4. **Confidence semantics:** confidence = certainty of the *content*, not importance. A forecast is uncertain even if central. Default new synthesis `0.6`; verified/cited facts higher; speculation lower (SCHEMA §3).
5. **Draft the manifest** — a table of proposed nodes: filename, type, one-line summary, key edges.
   - **supervised:** present the manifest and **wait for approval** before writing any files.
   - **hybrid:** write nodes, then report; pause only on contradictions/type-changes.
   - **autonomous:** write without prompting; still log everything.
6. **Write each node** from the matching `_system/templates/<type>.md`. Lead with a precise `summary`. Fill all required frontmatter. `created`/`modified`/`verified_at` = today.
7. **Create typed edges** — among new nodes and to existing graph nodes (scan INDEX first). Prefer specific edges over `related_to`. Declare edges on the source (A) side.
8. **Write a `source/` node** synthesizing the material, with `authored_by` edges to any `contact` nodes and `source_refs` to the raw file. New nodes carry `derived_from` edges back to it.
9. **Update `_system/INDEX.md`** — add every new node under its type heading as `- [[name]] — summary (confidence)`. Update the node count.
10. **Move** the raw file to `raw/processed/` (never modify the original; only move). Update any `source_refs` paths to the new location.
11. **Append to `_system/LOG.md`** (AGENTS §3 format): created nodes, edges touched, contradictions flagged, nodes-touched count.

## Output
A short report: N nodes created (by type), M existing nodes edged, contradictions found, and where the source now lives.

## Hard rules
- Never modify `raw/` content; only read and move.
- Atomic only — split anything covering >1 concept or >~300 lines.
- Every node validates against SCHEMA; every edge target is a real node (or flagged missing).
- Keep INDEX in sync; log the operation.
