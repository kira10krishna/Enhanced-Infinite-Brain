---
node_type: reference
summary: "Canonical reference for all node types, edge types, frontmatter fields, and naming conventions in this knowledge graph."
confidence: 1.0
verified_at: 2026-06-12
verified_by: human
visibility: system
edges: []
tags: [schema, system, reference]
created: 2026-06-12
modified: 2026-06-12
---

# SCHEMA — Knowledge Graph Reference

This is the single source of truth for the structure of this vault. Every node and edge in the graph must conform to what is defined here. When ingesting, querying, or maintaining the graph, the agent reads this file to know the rules.

---

## 1. Node Types (16)

Every node has **exactly one** `node_type`. The folder a node lives in **equals** its type. The agent dispatches behavior on type — a `fact` requires a source; a `hypothesis` requires a test; a `playbook` has steps.

### Foundational — core beliefs, frameworks, recorded choices

| Type | Folder | Use when… | Distinct from |
|------|--------|-----------|---------------|
| `pillar` | `pillar/` | A foundational identity, value, or principle that should anchor reasoning. Auto-injects on matching context. | `concept` (a pillar is *held*, a concept is *defined*) |
| `decision` | `decision/` | A concrete choice was made between alternatives. ADR style: context, options, choice, consequences. | `pillar` (a decision is dated and reversible; a pillar is enduring) |
| `concept` | `concept/` | A defined term or framework the agent should reason **from**. | `fact` (a concept is a model; a fact is a verified datum) |
| `question` | `question/` | A known unknown being actively tracked. Promotes to `hypothesis` once testable. | `hypothesis` (a question has no proposed answer yet) |

### Procedural — actions, processes, temporal events

| Type | Folder | Use when… | Distinct from |
|------|--------|-----------|---------------|
| `playbook` | `playbook/` | A repeatable procedure: trigger, steps, expected outcome. | `decision` (a playbook is reusable; a decision is one-time) |
| `task` | `task/` | An actionable item, usually synced from a real task system. | `playbook` (a task is done once; a playbook repeats) |
| `event` | `event/` | A dated thing that happened, to reason about temporally. | `fact` (an event is located in time; a fact is timeless) |
| `pattern` | `pattern/` | An observed regularity in data or behavior. A heuristic. | `hypothesis` (a pattern is observed; a hypothesis is predicted) |

### Evidential — claims, proof, external references

| Type | Folder | Use when… | Distinct from |
|------|--------|-----------|---------------|
| `hypothesis` | `hypothesis/` | A falsifiable prediction with a **measurable test** named in the body. | `pattern` (hypothesis predicts; pattern observes) |
| `fact` | `fact/` | A verified atomic statement with a **specific source and date**. | `concept` (a fact is a datum; a concept is a framework) |
| `source` | `source/` | An external reference (book, article, talk) **plus your synthesis**. Links to `raw/`. | `bookmark` (a source is processed; a bookmark is not yet) |
| `bookmark` | `bookmark/` | A saved link with light annotation, not yet processed into the graph. | `source` (promote a bookmark to a source once ingested) |

### Structural — organizational and meta nodes

| Type | Folder | Use when… | Distinct from |
|------|--------|-----------|---------------|
| `note` | `note/` | Low-priority scratch or a pre-atomized observation awaiting decomposition. | everything (a note is a holding pen) |
| `contact` | `contact/` | A person, with relationship metadata. | `source` (a contact is a who; a source is a what) |
| `reference` | `reference/` | A pointer to a config, schema, or pinned doc (like this file). | `bookmark` (a reference is internal/pinned; a bookmark is external/transient) |
| `custom` | `custom/` | A workspace-specific type that fits none of the 15 above. **Must be documented in `LOCAL-TYPES.md`.** | — |

---

## 2. Edge Types (10)

Every connection is a typed edge declared in a node's frontmatter `edges:` list. An edge has a **target**, a **type**, a **weight** (0.0–1.0), and an optional **note**.

| Edge Type | Direction | Meaning | Default Weight |
|-----------|-----------|---------|----------------|
| `supports` | A → B | A provides evidence for B. | 0.7 |
| `contradicts` | A ↔ B | A disagrees with or invalidates B. Always flagged in audits. | 1.0 |
| `depends_on` | A → B | B must hold before A makes sense. | 0.8 |
| `derived_from` | A → B | A was created from B. Lineage / provenance. | 0.9 |
| `related_to` | A ↔ B | Topical link, nothing stronger known. The weakest edge. | 0.5 |
| `part_of` | A → B | A is a component of B. | 0.8 |
| `preceded_by` | A → B | A comes *after* B in time (B happened first). | 0.7 |
| `followed_by` | A → B | A comes *before* B in time (B happened after). | 0.7 |
| `authored_by` | A → B | B is the author/originator of A. | 1.0 |
| `tagged_with` | A → B | B is a topic-tag node that A carries. | 0.5 |

**Edge discipline:**
- Prefer the most specific edge. `related_to` is a fallback, not a default — if you can name *why* two nodes connect, use a stronger type.
- Edges are declared on the **source** node (the A side). The reciprocal direction is inferred; you don't need to declare both sides.
- For symmetric edges (`contradicts`, `related_to`) declare on either node; the audit will surface the pair.
- Weight expresses **strength of the relationship**, not confidence in the node. Confidence lives in the node's own `confidence` field.

---

## 3. Frontmatter Fields

Every node carries YAML frontmatter. Fields marked **required** must be present on every node.

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `node_type` | ✅ | enum | One of the 16 types. Must match the folder. |
| `summary` | ✅ | string | One line, agent-optimized. **Read first, before the body.** The single most important field. |
| `confidence` | ✅ | float 0.0–1.0 | How certain is this content. See scoring guide below. |
| `verified_at` | ✅ | date | When last validated (ISO `YYYY-MM-DD`). Drives confidence decay. |
| `verified_by` | ✅ | enum | `human` \| `agent` \| `auto`. |
| `visibility` | ✅ | enum | `public` \| `namespace` \| `private` \| `system`. See §5. |
| `edges` | ✅ | list | Typed edges (may be empty `[]`). See §2. |
| `created` | ✅ | date | Creation date. |
| `modified` | ✅ | date | Last modification date. |
| `staleness_signal` | ⬜ | string | A human-readable condition for when to re-verify (e.g. "Re-check when Q3 data arrives"). |
| `tags` | ⬜ | list | Topic tags. May correspond to `tagged_with` edge targets. |
| `source_refs` | ⬜ | list | Paths into `raw/` this node draws from. |
| `namespace` | ⬜ | string | Required only when `visibility: namespace`. The scope name. |

### Confidence scoring guide

| Range | Meaning |
|-------|---------|
| 0.9–1.0 | Verified fact, direct quote, or first-principles certainty. |
| 0.7–0.9 | Well-supported; multiple sources or strong reasoning. |
| 0.5–0.7 | Plausible; single source or moderate reasoning. Default for new synthesis. |
| 0.3–0.5 | Tentative; speculation or weak evidence. Below 0.4 → flagged for review. |
| 0.0–0.3 | Highly uncertain; placeholder or unverified claim. |

### Edge YAML shape

```yaml
edges:
  - target: "[[ltv-cac-ratio]]"     # wikilink to the target node by filename (no extension)
    type: supports                   # one of the 10 edge types
    weight: 0.8                      # 0.0–1.0
    note: "Revenue data backs this"  # optional, why the edge exists
```

---

## 4. Confidence Decay

Nodes lose confidence over time unless re-verified. This prevents silent rot.

- **Rate:** `-0.05` per month since `verified_at`.
- **Review threshold:** `0.4`. Nodes that decay below this are flagged by `/vault-health`.
- **Formula:** `effective_confidence = stored_confidence - 0.05 × months_since(verified_at)`
- Decay is applied and **written back** by `/vault-health` (which also updates `verified_at` semantics in the report, not silently on the node). `verified_by: human` re-verification resets the clock by updating `verified_at`.
- `pillar` and `system` nodes decay slowly or not at all by convention — they encode enduring beliefs and infrastructure.

These defaults (gentle, research-vault-appropriate) are configurable in `AGENTS.md`.

---

## 5. Visibility Levels

| Level | Who reads it | Use for |
|-------|--------------|---------|
| `public` | Any agent or human. **Default.** | Most knowledge. |
| `namespace` | Scoped to one project/domain (set `namespace:`). | Project-specific knowledge. |
| `private` | Agent reads **only when explicitly asked**. | Personal notes, journal, sensitive data. |
| `system` | Infrastructure. | Schema, templates, agent instructions. |

---

## 6. Naming Conventions

- **Filenames:** `kebab-case.md`, descriptive, no dates unless the node *is* a dated event (e.g. `ltv-cac-ratio.md`, `mrr-april-2026.md`).
- **One node per file.** One concept per node.
- **Wikilinks:** reference by filename without extension: `[[ltv-cac-ratio]]`. Obsidian-compatible.
- **Uniqueness:** filenames are globally unique across all type folders (wikilinks resolve by name). If two types need the same name, disambiguate (e.g. `pricing-philosophy` pillar vs `pricing-model-2026` decision).

---

## 7. Node Body Structure

- **Length:** 50–300 lines. If a node exceeds ~300 lines or covers more than one concept, split it into a molecule of linked nodes.
- **Self-contained:** readable on its own. The summary + body should answer "what is this?" without loading neighbors.
- **Type-specific guidance** is embedded in each template under `_system/templates/`.

---

See [AGENTS.md](AGENTS.md) for the operational rules that consume this schema, and [LOCAL-TYPES.md](LOCAL-TYPES.md) for any workspace-specific `custom` types.
