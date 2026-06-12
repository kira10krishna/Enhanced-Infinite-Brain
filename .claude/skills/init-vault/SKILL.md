---
name: init-vault
description: Scaffold or repair the typed knowledge-graph structure in this vault — the 16 node-type folders, _system/ (AGENTS, SCHEMA, INDEX, LOG, templates), and raw/. Idempotent and non-destructive. Use when setting up a new vault, or to restore a missing folder/system file without touching populated content.
---

# /init-vault

Scaffold or repair the knowledge-graph structure. **Idempotent** — safe to run on an existing vault; never overwrites a populated file.

## Vault root
`/Users/kira/Documents/Brains/Knowledge` (or the current working directory if it already contains `_system/`).

## Steps

1. **Detect.** Check whether `_system/SCHEMA.md` exists. If yes, this is a repair; if no, a fresh init.
2. **Create the 16 type folders** if missing, each with a `.gitkeep`:
   `pillar concept decision question playbook task event pattern hypothesis fact source bookmark note contact reference custom`
3. **Create `raw/`** with subfolders `articles papers transcripts images processed assets` (each `.gitkeep`).
4. **Create `_system/`** and, **only if absent**, write starter versions of:
   `AGENTS.md`, `SCHEMA.md`, `INDEX.md`, `LOG.md`, `LOCAL-TYPES.md`, `HEALTH-REPORT.md`, and `templates/` (one template per node type).
   - If any already exist with content, **leave them untouched** and report that they were preserved.
5. **Add `.gitignore`** entry `.obsidian/workspace.json` if not present.
6. **Append to `_system/LOG.md`**: `## [<today>] init | Vault scaffolded/repaired` with a list of what was created vs preserved.

## Rules
- Never overwrite a file that already has content. Report preserved files explicitly.
- After running, the vault must validate against [SCHEMA.md](../../../_system/SCHEMA.md).
- Report a summary: folders created, system files created, files preserved.
