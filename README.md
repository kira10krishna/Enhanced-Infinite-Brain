# Enhanced Infinite Brain

A typed knowledge graph built on Obsidian — an AI-first upgrade to Andrej Karpathy's LLM Wiki method. Every idea lives as an atomic node with typed edges, confidence scores, and decay — so your notes stay honest, traversable, and agent-readable.

---

## What makes it different

| Plain notes | Enhanced Infinite Brain |
|---|---|
| Free-form files, flat folders | Atomic typed nodes, 16 distinct types |
| No structure between ideas | 10 typed directed edges with weight + reason |
| Static text | Confidence scores that decay over time |
| Human-only | Agent-readable from any LLM (Claude, Gemini, Ollama) |
| Manual upkeep | 5 Claude Code skills automate the graph ops |

---

## How it works

Each piece of knowledge is a **node** — a single `.md` file with a typed YAML frontmatter and a structured body. Nodes are connected by **edges** declared in that frontmatter. A universal `AGENTS.md` file tells any LLM agent how to read and maintain the graph.

```
_system/
  SCHEMA.md       ← canonical rules: types, edges, confidence
  AGENTS.md       ← operating instructions for any LLM
  INDEX.md        ← table of contents; agent entry point
  LOG.md          ← append-only operation history
  templates/      ← 16 type templates

.claude/skills/   ← 5 Claude Code skills (slash commands)

pillar/ concept/ fact/ hypothesis/ event/ ...  ← node folders (16 types)
raw/articles/     ← source documents waiting to be ingested
raw/processed/    ← ingested source documents
```

---

## Node types

16 types covering the full range of knowledge:

`pillar` `concept` `fact` `hypothesis` `pattern` `decision` `event` `question` `playbook` `task` `note` `source` `bookmark` `contact` `reference` `custom`

Each node has a mandatory **summary** field — one agent-optimized line read before the body. This keeps traversal token-efficient.

---

## Edge types

10 typed directed edges, each with `weight` (0.0–1.0) and an optional `note`:

`supports` · `contradicts` · `depends_on` · `derived_from` · `related_to` · `part_of` · `preceded_by` · `followed_by` · `authored_by` · `tagged_with`

---

## Confidence & decay

Every node carries a `confidence` score (0.0–1.0) and a `verified_at` date. Effective confidence decays **−0.05 per month** since last verification. Nodes below **0.4** are flagged for review. Pillar and system nodes are exempt.

```yaml
confidence: 0.8
verified_at: 2026-06-13   # decay clock starts here
```

---

## The 5 skills

Invoke these as Claude Code slash commands:

| Skill | Command | What it does |
|---|---|---|
| Init vault | `/init-vault` | Idempotent scaffold — creates folders, system files, templates |
| Convert note | `/convert-note` | Ingests a raw document → decomposes into atomic typed nodes |
| Query vault | `/query-vault` | Graph traversal → answer a question with citations |
| Organize vault | `/organize-vault` | Audit for orphans, contradictions, stale nodes, INDEX drift |
| Vault health | `/vault-health` | Decay pass → compute effective confidence, write health report |

All skills support three workflow modes: `supervised` (approve before write), `hybrid` (write then report), `autonomous` (silent).

---

## Fidelity rules

The system enforces clean category boundaries during ingest:

- **Pillars** only from the user's own beliefs — never from external sources
- **Forecasts** → `hypothesis`, not `fact`
- **Cited real-world claims** → `fact`
- **Defined mechanisms** → `concept`
- **Choices made by actors inside a source** → `event`, not `decision`

---

## Quick start

```bash
# 1. Open this vault in Obsidian
# 2. Start a Claude Code session in the vault directory
# 3. Scaffold (idempotent — safe to run on existing vault)
/init-vault

# 4. Drop a document into raw/articles/ and ingest it
/convert-note raw/articles/my-paper.md

# 5. Ask a question across the graph
/query-vault "What are the main risks of automated AI R&D?"
```

---

## Agent compatibility

`_system/AGENTS.md` is the universal entry point — written for any LLM, not just Claude. Ollama, Gemini, or any model with file access can read it and operate the graph using the same rules.

---

## Design credit

Built on Andrej Karpathy's [LLM Wiki method](https://x.com/karpathy) — extended with typed nodes, edge semantics, confidence decay, and agentic operations.
