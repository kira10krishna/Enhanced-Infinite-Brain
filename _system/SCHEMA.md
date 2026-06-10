# Knowledge Graph Schema (SCHEMA.md)

Complete reference for node types, edge types, metadata fields, and frontmatter templates.

> Agents: refer to [AGENTS.md](AGENTS.md) for operational workflows. This file is the **data dictionary**.

---

## 1. Node Types (16)

### Foundational

| Type | Folder | Description | When to Use | Decay |
|------|--------|-------------|-------------|-------|
| `pillar` | `pillar/` | Foundational identity, core field of interest, or index node. Auto-injected into relevant queries. | For top-level domains, core beliefs, or subjects that anchor the entire graph. Keep short (50–100 lines). | **Exempt** |
| `decision` | `decision/` | A concrete choice made between alternatives. ADR-style: context → options → rationale → consequences. | When a strategic or architectural decision has been made and you want to record *why*. | **Exempt** |
| `concept` | `concept/` | A defined term, framework, model, or abstract idea the agent should reason from. | For definitions, mental models, theoretical frameworks, or any reusable abstraction. | Base (-0.04/mo) |
| `question` | `question/` | A known unknown being actively tracked. Becomes a hypothesis once testable. | For open research questions, unresolved puzzles, or "things I want to find out." | Base (-0.04/mo) |

### Procedural

| Type | Folder | Description | When to Use | Decay |
|------|--------|-------------|-------------|-------|
| `playbook` | `playbook/` | A repeatable procedure with steps, triggers, and expected outcomes. | For how-to guides, standard operating procedures, checklists, or methodologies. | **Exempt** |
| `task` | `task/` | An actionable item with status tracking. | For specific todo items, work units, or execution steps with deadlines. | Base (-0.04/mo) |
| `event` | `event/` | A dated occurrence the agent should reason about temporally. | For meetings, milestones, incidents, launches, or any time-bound happening. | Base (-0.04/mo) |
| `pattern` | `pattern/` | An observed regularity in data or behavior. Heuristic. | For recurring solutions, behavioral trends, design patterns, or "things that keep happening." | Base (-0.04/mo) |

### Evidential

| Type | Folder | Description | When to Use | Decay |
|------|--------|-------------|-------------|-------|
| `hypothesis` | `hypothesis/` | A falsifiable prediction with a measurable test condition. | For unproven theories, experimental predictions, or claims awaiting validation. Must include test criteria. | Base (-0.04/mo) |
| `fact` | `fact/` | A verified atomic statement with a specific source and date. | For empirical data points, statistics, measurements, or objectively verifiable claims. Always cite source. | **Fast** (-0.08/mo) |
| `source` | `source/` | An external reference (book, paper, talk, video, article) plus your synthesis. | For any external material you've consumed and want to preserve insights from. | **Fast** (-0.08/mo) |
| `bookmark` | `bookmark/` | A saved link with light annotation, not yet processed into a source. | For URLs and articles you've saved but haven't deeply analyzed yet. Upgrade to `source` after processing. | Base (-0.04/mo) |

### Structural

| Type | Folder | Description | When to Use | Decay |
|------|--------|-------------|-------------|-------|
| `note` | `note/` | Low-priority scratch, pre-atomized observation, or fleeting thought. | For raw ideas, meeting notes, brain dumps — anything not yet refined into a specific type. | Base (-0.04/mo) |
| `contact` | `contact/` | A person, organization, team, or AI agent with relationship metadata. | For people you interact with, authors you reference, or organizations relevant to your research. | Base (-0.04/mo) |
| `reference` | `reference/` | Static reference material: specs, configs, schemas, code snippets, formulas, cheatsheets. | For content that doesn't change often and serves as a lookup table or manual. | Base (-0.04/mo) |
| `custom` | `custom/` | Workspace-specific type not covered by the 15 above. | Must be documented in `_system/LOCAL-TYPES.md` before use. | Base (-0.04/mo) |

---

## 2. Edge Types (10)

Edges are stored in the `edges` array of YAML frontmatter. Every edge has `type`, `target`, `weight`, and an optional `note`.

| Edge Type | Direction | Description | Default Weight | Example |
|-----------|-----------|-------------|----------------|---------|
| `supports` | A → B | A provides evidence, data, or logical backing for B. | 0.7 | `fact/revenue-q2` supports `hypothesis/pricing-works` |
| `contradicts` | A ↔ B | A conflicts with, refutes, or invalidates B. **Must register in CONTRADICTIONS.md.** | 1.0 | `fact/new-study` contradicts `hypothesis/old-theory` |
| `depends_on` | A → B | A requires B to be understood or to hold true. | 0.8 | `concept/backprop` depends_on `concept/gradient-descent` |
| `derived_from` | A → B | A was created from, summarized from, or extracted from B. Lineage edge. | 0.9 | `concept/attention` derived_from `source/transformer-paper` |
| `related_to` | A ↔ B | Topical connection; no stronger relationship known. Fallback type. | 0.5 | `concept/rust` related_to `concept/cpp` |
| `part_of` | A → B | A is a sub-component or sub-section of B. | 0.8 | `concept/query-parser` part_of `pillar/search-engines` |
| `preceded_by` | A → B | B happened before A in time. | 0.7 | `event/launch` preceded_by `event/code-freeze` |
| `followed_by` | A → B | B happened after A in time. | 0.7 | `event/code-freeze` followed_by `event/launch` |
| `authored_by` | A → B | B (a contact node) is the author or creator of A. | 1.0 | `source/paper` authored_by `contact/vaswani` |
| `tagged_with` | A → B | B (a concept or tag node) categorizes A. | 0.5 | `note/thoughts` tagged_with `concept/alignment` |

### Weight Scale

| Range | Meaning |
|-------|---------|
| 0.9–1.0 | Definitive, structural (authorship, direct derivation, contradiction) |
| 0.7–0.8 | Strong causal, evidential, or dependency link |
| 0.4–0.6 | Moderate association, may strengthen with evidence |
| 0.1–0.3 | Weak/speculative, review during `/organize-vault` |

---

## 3. Trust Metadata Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✅ | Unique kebab-case identifier. Must match filename. |
| `title` | string | ✅ | Human-readable title. |
| `node_type` | string | ✅ | One of the 16 node types. |
| `summary` | string | ✅ | One-line, agent-optimized description. The primary retrieval signal. |
| `status` | string | ✅ | `active` \| `draft` \| `deprecated` \| `archived` \| `resolved` \| `migrated` |
| `confidence` | float | ✅ | 0.0–1.0. Decays over time unless re-verified. |
| `created_at` | string | ✅ | ISO 8601 date (e.g., `2026-06-11`). |
| `verified_at` | string | ✅ | Date of last verification. Drives decay calculation. |
| `verified_by` | string | ✅ | `human` \| `agent` \| `auto` |
| `volatility` | string | ✅ | `stable` \| `volatile`. Volatile = double decay rate. |
| `visibility` | string | ✅ | `public` \| `namespace` \| `private` \| `system` |
| `staleness_signal` | string | ❌ | Condition that should trigger re-verification. |
| `derived_from` | list | ❌ | Lineage: list of parent node paths. |
| `source_refs` | list | ❌ | Paths to raw source files in `raw/`. |
| `tags` | list | ❌ | Flat tag list for Dataview queries. |
| `needs_review` | bool | ❌ | Set by hybrid ingest for uncertain nodes. |
| `edges` | list | ✅ | Array of edge objects (see §2). At least one required. |

### Visibility Levels

| Level | Scope | Usage |
|-------|-------|-------|
| `public` | Any agent or human | Default for most knowledge nodes. |
| `namespace` | Scoped to a project or domain area | For project-specific nodes not relevant globally. |
| `private` | Personal/sensitive | Agent reads only when explicitly directed. |
| `system` | Infrastructure | Schema files, templates, agent instructions. |

---

## 4. Confidence Scoring Guidelines

| Evidence Quality | Initial Confidence |
|------------------|-------------------|
| Peer-reviewed source, replicated data | 0.95–1.0 |
| Reputable source, well-documented | 0.8–0.9 |
| Personal observation, single source | 0.6–0.7 |
| Speculative, no direct evidence | 0.3–0.5 |
| Placeholder, needs research | 0.1–0.2 |

### Decay Rules

| Tier | Applies To | Rate | Exempt? |
|------|-----------|------|---------|
| Exempt | `pillar`, `decision`, `playbook` | 0.00/month | Yes — only lose confidence if explicitly invalidated |
| Base | All other types (when `volatility: stable`) | -0.04/month | No |
| Fast | `fact`, `source`, or any node with `volatility: volatile` | -0.08/month | No |

**Formula**: `new_confidence = max(0.0, confidence - (rate × months_since_verified))`

**Review threshold**: Nodes dropping below **0.3** are flagged in `HEALTH-REPORT.md`.

---

## 5. Frontmatter Templates by Node Type

### Generic Template (base for all types)

```yaml
---
id: "node-id"
title: "Node Title"
node_type: "concept"
summary: "One-line agent-optimized description."
status: "active"
confidence: 0.85
created_at: "2026-06-11"
verified_at: "2026-06-11"
verified_by: "human"
volatility: "stable"
visibility: "public"
staleness_signal: ""
derived_from: []
source_refs: []
tags: []
edges:
  - type: "related_to"
    target: "pillar/some-pillar"
    weight: 0.5
    note: ""
---
```

### Type-Specific Additions

**`pillar`** — Add: `sub_domains: []` (list of child pillar or concept IDs)

**`decision`** — Add: `decision_date: ""`, `alternatives: []`, `rationale: ""`

**`hypothesis`** — Add: `test_condition: ""`, `prediction: ""`, `outcome: ""` (filled when resolved)

**`fact`** — Add: `data_date: ""` (when the data was measured/observed), `source_url: ""`

**`source`** — Add: `source_type: ""` (book | paper | article | video | podcast | talk), `author: ""`, `url: ""`, `date_consumed: ""`

**`task`** — Add: `assignee: ""`, `due_date: ""`, `priority: ""` (high | medium | low), `completion: ""` (percent or status)

**`event`** — Add: `event_date: ""`, `location: ""`, `participants: []`

**`contact`** — Add: `role: ""`, `organization: ""`, `relationship: ""` (colleague | mentor | author | etc.)

**`bookmark`** — Add: `url: ""`, `date_saved: ""`

---

## 6. Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Node filename | Kebab-case, lowercase, `.md` extension | `attention-mechanism.md` |
| Node ID | Matches filename without extension | `attention-mechanism` |
| Folder path | `type/filename.md` | `concept/attention-mechanism.md` |
| Edge target | Full relative path from vault root | `concept/attention-mechanism` |
| Wikilink | Obsidian format with optional display text | `[[concept/attention-mechanism\|Attention Mechanism]]` |
| Cross-vault ref | `vault://` protocol | `vault://personal/[[morning-routine]]` |
