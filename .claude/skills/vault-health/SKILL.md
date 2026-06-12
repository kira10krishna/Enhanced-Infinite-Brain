---
name: vault-health
description: Automated maintenance pass over the knowledge graph — apply confidence decay by node age, flag nodes below the review threshold, count nodes by type, find orphans/missing targets, and write _system/HEALTH-REPORT.md. Has an interactive mode (report + confirm) and an `auto` mode (silent, schedulable). Use for a health check, decay pass, or scheduled maintenance of the vault.
---

# /vault-health

Automated maintenance and decay. Implements [AGENTS.md](../../../_system/AGENTS.md) §2.4.

## Inputs
- Optional `auto` → silent mode: write the report, no prompts. Otherwise interactive.

## Config (from AGENTS.md §0)
- Decay rate: `-0.05` / month since `verified_at`.
- Review threshold: `0.4`.
- `pillar` and `system` nodes are exempt from decay (enduring beliefs / infrastructure).

## Steps

1. **Inventory.** Count nodes by type across the 16 folders. Note total content vs system nodes.
2. **Compute effective confidence** for each content node:
   `effective = stored − 0.05 × months_since(verified_at)`.
3. **Flag** nodes with effective confidence `< 0.4`. List them with stored value, age, and effective value.
4. **Structural quick-checks:** orphans (no inbound edges), missing wikilink targets, `contradicts` edges.
5. **Write `_system/HEALTH-REPORT.md`** (overwrite — it holds only the latest run): summary table, counts by type, flagged nodes, orphans, missing targets, and **recommendations** (sources to seek, questions to investigate, nodes to re-verify).
6. **Append a `health` entry to `_system/LOG.md`.**

## Modes
- **interactive:** present findings; ask before writing back any node changes (e.g. re-verification). The report file is always written.
- **`auto`:** write report and log silently; make no node edits beyond the report. Suitable for scheduling (e.g. weekly).

## Note
This operation does **not** delete or rewrite nodes. It measures, flags, and reports. Acting on flags is a human/`/organize-vault` decision.
