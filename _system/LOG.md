# Operation Log

Append-only, chronological. One entry per operation. Grep the headings for history:
`grep "^## \[" _system/LOG.md | tail -5`

---

## [2026-06-12] init | Vault scaffolded
- Created directory structure: 16 type folders + `_system/` + `raw/` (with article/paper/transcript/image/processed/asset subfolders)
- Created system files: AGENTS.md, SCHEMA.md, INDEX.md, LOG.md, LOCAL-TYPES.md, HEALTH-REPORT.md
- Created node templates in `_system/templates/` (one per type)
- Decay config: -0.05/month, review threshold 0.4
- Default workflow mode: supervised
- Vault ready for first ingest
- Nodes touched: 4 system references
