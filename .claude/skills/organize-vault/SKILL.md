---
name: organize-vault
description: Interactive structural audit of the knowledge graph — scan for contradictions, orphans, stale nodes, missing/weak edges, missing nodes, gaps, and type mismatches, then propose fixes for approval. Proposes, never auto-fixes (except non-destructive fixes in autonomous mode). Use when the user wants to lint, tidy, audit structure, or check the health of the graph's connections.
---

# /organize-vault

Interactive structural audit. Implements [AGENTS.md](../../../_system/AGENTS.md) §2.3. **Propose, don't auto-fix** — structural changes require approval (except non-destructive fixes in autonomous mode).

## Before you start
Read `_system/SCHEMA.md`, `_system/AGENTS.md`, and `_system/INDEX.md`. Then scan node frontmatter across the type folders (grep for `node_type:`, `edges:`, `confidence:`, `verified_at:` is cheaper than reading bodies).

## What to scan for
- **Contradictions** — `contradicts` edges, and pairs of nodes making conflicting claims.
- **Stale nodes** — effective confidence below `0.4` (apply decay: `stored − 0.05 × months_since(verified_at)`; pillars/system exempt).
- **Orphans** — nodes with no inbound edges.
- **Missing nodes** — wikilink/edge targets that have no file on disk.
- **Weak edges** — `related_to` links that could be a stronger, specific type.
- **Missing cross-references** — nodes that clearly relate but aren't linked.
- **Gaps** — topics implied by existing nodes but not yet covered.
- **Type mismatches** — nodes that would fit another type better (incl. oversized nodes that should split — Pillar 1 enforcement).
- **INDEX drift** — INDEX entries that don't match files on disk.

## Output
Findings **grouped by issue type**, each with: the node(s) involved, why it's flagged, and a **concrete proposed fix** (add edge X, split node Y, retype Z, create missing node W).

## Applying fixes
- supervised/hybrid: apply only the fixes the user approves.
- autonomous: apply non-destructive fixes (adding edges, fixing INDEX drift); still defer deletes, merges, and type changes for confirmation.
- After applying, update INDEX and append an `organize` entry to `_system/LOG.md`.
