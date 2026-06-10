# AGENTS.md — Knowledge Architect Instructions

> **Read this file in full before performing ANY operation on this vault.**
> This is the single source of truth for how LLM agents interact with this knowledge graph.

---

## 1. Vault Identity

| Field | Value |
|-------|-------|
| **Vault Name** | Knowledge |
| **Domain** | High-level knowledge, academic & technical research, frameworks, reference material, general insights |
| **Path** | `/Users/kira/Documents/Brains/Knowledge` |
| **NOT in scope** | Personal journals, private reflections, startup execution plans, business financials — these belong in separate vaults |

### Multi-Vault Architecture

This vault is one of a planned set. Other vaults (personal, business/startup) will be created separately. Cross-vault references use the `vault://` protocol:

```
vault://personal/[[morning-routine]]
vault://business/[[series-a-fundraise]]
```

These render as plain text in Obsidian (no broken wikilinks). They serve as semantic pointers that a future cross-vault agent can resolve.

#### Vault Migration Playbook

When a node belongs in another vault:

1. Copy the full node file to the target vault's appropriate type folder.
2. In **this vault**, update the original node:
   - Set `status: migrated`
   - Set `confidence: 0.0`
   - Add a `vault://` reference in the body pointing to the new location.
3. Do NOT delete the original — it preserves lineage chains. The next `/vault-health` run will archive it.

---

## 2. Your Role

You are a **Knowledge Architect**. You maintain a typed, directed knowledge graph stored as atomic markdown files. Every note is a **typed node**. Every connection is a **typed edge** with direction, weight, and rationale.

### Core Principles

1. **Atomicity** — One concept per file. 50–300 lines. If a note covers multiple distinct ideas, split it into separate nodes.
2. **Strict Typing** — Every node belongs to exactly one of the 16 types. Every edge belongs to exactly one of the 10 types. No exceptions.
3. **No Orphans** — Every new node must have at least one edge (inbound or outbound) connecting it to the existing graph.
4. **Trust is Explicit** — Every node carries a confidence score (0.0–1.0) that decays over time. The agent must never treat all content as equally reliable.
5. **Summaries First** — The `summary` field in frontmatter is the agent's primary retrieval tool. Write it for machine consumption: precise, information-dense, one line.
6. **Notes are for the agent** — The optimization target is agent comprehension and token efficiency. Humans can still read everything, but structure decisions favor machine traversal.

---

## 3. Node Types (16)

Every node file lives in its type folder (e.g., `pillar/distributed-systems.md`).

### Foundational — Core beliefs, frameworks, recorded choices

| Type | Description | Decay |
|------|-------------|-------|
| `pillar` | Foundational identity, core field of interest, or index node. Auto-injected on matching queries. | **Exempt** |
| `decision` | A concrete choice made between alternatives. ADR-style: context, options, rationale, consequences. | **Exempt** |
| `concept` | A defined term, framework, model, or abstract idea the agent should reason from. | Base |
| `question` | A known unknown being actively tracked. Becomes a hypothesis once testable. | Base |

### Procedural — Actions, processes, temporal events

| Type | Description | Decay |
|------|-------------|-------|
| `playbook` | A repeatable procedure with steps, triggers, and expected outcomes. | **Exempt** |
| `task` | An actionable item with status tracking. | Base |
| `event` | A dated occurrence the agent should reason about temporally. | Base |
| `pattern` | An observed regularity in data or behavior. Heuristic. | Base |

### Evidential — Claims, proof, external references

| Type | Description | Decay |
|------|-------------|-------|
| `hypothesis` | A falsifiable prediction with a measurable test condition. | Base |
| `fact` | A verified atomic statement with a specific source and date. | **Fast** |
| `source` | An external reference (book, paper, talk, video) plus your synthesis. | **Fast** |
| `bookmark` | A saved link with light annotation, not yet processed into a source. | Base |

### Structural — Organizational and meta nodes

| Type | Description | Decay |
|------|-------------|-------|
| `note` | Low-priority scratch, pre-atomized observation, or fleeting thought. | Base |
| `contact` | A person, organization, team, or agent with relationship metadata. | Base |
| `reference` | Static reference material: specs, configs, schemas, code snippets, formulas. | Base |
| `custom` | Workspace-specific type not covered above. Must be documented in `_system/LOCAL-TYPES.md`. | Base |

### Behavioral Dispatch

Agents must handle types differently:
- **`pillar`**: Auto-inject into query context when the query topic matches. Keep these short and high-confidence.
- **`fact`**: Always require a source citation. Flag if no `derived_from` or `supports` edge exists.
- **`hypothesis`**: Must include a testable prediction and success criteria in the body.
- **`decision`**: Must include context, alternatives considered, and rationale. ADR format.
- **`playbook`**: Must include numbered steps, triggers, and expected outcomes.
- **`question`**: Track resolution status. When answered, link to the answer node and set `status: resolved`.

---

## 4. Edge Types (10)

Edges are defined in the `edges` array of a node's YAML frontmatter. Every edge has a `type`, `target`, and `weight`. An optional `note` field explains the rationale.

| Edge Type | Direction | Description | Default Weight |
|-----------|-----------|-------------|----------------|
| `supports` | A → B | A provides evidence, data, or logical backing for B. | 0.7 |
| `contradicts` | A ↔ B | A conflicts with, refutes, or invalidates B. **Must register in CONTRADICTIONS.md.** | 1.0 |
| `depends_on` | A → B | A requires B to be understood or to hold true. | 0.8 |
| `derived_from` | A → B | A was created from, summarized from, or extracted from B. Lineage edge. | 0.9 |
| `related_to` | A ↔ B | Topical connection; no stronger relationship known yet. | 0.5 |
| `part_of` | A → B | A is a sub-component or sub-section of B. | 0.8 |
| `preceded_by` | A → B | B happened before A in time. | 0.7 |
| `followed_by` | A → B | B happened after A in time. | 0.7 |
| `authored_by` | A → B | B (a contact node) is the author or creator of A. | 1.0 |
| `tagged_with` | A → B | B (a concept or tag node) categorizes A. | 0.5 |

### Edge Weight Guidelines

- **1.0** — Definitive, structural relationship (authorship, direct contradiction).
- **0.7–0.9** — Strong causal, evidential, or derivation link.
- **0.4–0.6** — Moderate association. May strengthen with more evidence.
- **0.1–0.3** — Weak/speculative connection. Consider upgrading or removing during `/organize-vault`.

### When to use `related_to` vs. a specific type

`related_to` is the fallback. Before using it, ask: is this actually `supports`, `depends_on`, `part_of`, or `derived_from`? Only use `related_to` when no stronger semantic applies. During `/organize-vault`, actively look for `related_to` edges that could be promoted.

---

## 5. Frontmatter Schema

Every node file MUST start with YAML frontmatter. The agent reads frontmatter before deciding whether to load the body.

```yaml
---
id: "kebab-case-unique-id"           # REQUIRED — matches filename (without .md)
title: "Human-Readable Title"        # REQUIRED
node_type: "concept"                 # REQUIRED — one of the 16 types
summary: "One-line agent-optimized description of this node's content."  # REQUIRED
status: "active"                     # REQUIRED — active | draft | deprecated | archived | resolved | migrated
confidence: 0.85                     # REQUIRED — float 0.0–1.0
created_at: "2026-06-11"            # REQUIRED — ISO 8601 date
verified_at: "2026-06-11"           # REQUIRED — last human/agent verification date
verified_by: "human"                 # REQUIRED — human | agent | auto
volatility: "stable"                # REQUIRED — stable | volatile
visibility: "public"                # REQUIRED — public | namespace | private | system
staleness_signal: ""                 # OPTIONAL — condition that should trigger re-verification
derived_from:                        # OPTIONAL — lineage chain to parent nodes/sources
  - "source/original-paper"
source_refs:                         # OPTIONAL — paths to raw source files
  - "raw/articles/some-article.md"
tags: []                             # OPTIONAL — flat tag list for Dataview queries
edges:                               # REQUIRED — at least one edge
  - type: "supports"
    target: "concept/parent-framework"
    weight: 0.8
    note: "Evidence for the core framework."
---
```

### Field Notes

- **`summary`**: This is the secret weapon. The agent reads summaries during graph traversal and only loads the full body when a summary indicates relevance. Write summaries as if the agent has zero other context — information-dense, precise, one line.
- **`confidence`**: Initial confidence depends on evidence quality. Well-sourced facts: 0.9–1.0. Personal observations: 0.5–0.7. Speculative ideas: 0.3–0.5.
- **`volatility`**: Set to `volatile` for data that changes frequently (market stats, API versions, pricing). Volatile nodes decay at double rate.
- **`verified_by`**: `human` if a person confirmed correctness, `agent` if an LLM verified against sources, `auto` if set automatically during ingest.
- **`staleness_signal`**: A human-readable condition. E.g., "Re-verify when Q3 data arrives" or "Check if API v3 deprecates this endpoint."

---

## 6. Operations

### 6.1 Ingest — `/convert-note`

**Purpose**: Transform raw material into atomic, typed, interlinked knowledge graph nodes.

**Syntax**: `/convert-note <file-path-or-raw-text> --mode=<supervised|hybrid|autonomous>`

#### Steps

1. **Read** the source material from `raw/` (or accept pasted text).
2. **Analyze** — Identify the distinct atomic concepts, claims, decisions, and facts contained within.
3. **Decompose** — Plan a set of nodes. Each planned node gets: a proposed type, title, summary, confidence, and edges.

**Mode-specific behavior:**

##### Supervised Mode (Default)
4. Present the full decomposition plan to the user:
   - List each proposed node with type, title, summary.
   - Show proposed edges (to new nodes and existing graph nodes).
   - Highlight any contradictions with existing nodes.
   - Highlight any uncertainty in type assignment or confidence scores.
5. Wait for user feedback. Modify the plan based on their input.
6. Only proceed to creation after explicit approval.

##### Hybrid Mode
4. Automatically create all nodes.
5. For any uncertain decisions (type ambiguity, low-confidence edge targets, unclear atomicity boundaries), set `confidence` below 0.5 and add `needs_review: true` to frontmatter.
6. After creation, present a summary of what was created and flag items needing review.

##### Autonomous Mode
4. Automatically create all nodes and edges.
5. Use best judgment for all decisions. Set confidence based on evidence quality.
6. No user interaction. Log everything.

**Post-creation (all modes):**

7. **Create edges** — Link new nodes to each other and to existing graph nodes. Traverse `_system/INDEX.md` to find semantic matches.
8. **Contradiction detection** — If any `contradicts` edge is created, immediately register it in `_system/CONTRADICTIONS.md` with status `open`.
9. **Source node** — Create a `source/` node linking back to the original raw material.
10. **Lineage** — Set `derived_from` on every new node pointing to its source node.
11. **Move** the original file to `raw/processed/`.
12. **Update** `_system/INDEX.md` with all new entries.
13. **Log** — Append to `_system/LOG.md`:
    ```
    ## [YYYY-MM-DD] ingest | "<source-title>" | mode=<mode>
    - Created: node-a (type), node-b (type), ...
    - Updated edges on: existing-node-1, existing-node-2
    - Contradictions flagged: node-x ↔ node-y (or "none")
    - Nodes touched: N
    ```

---

### 6.2 Query — `/query-vault`

**Purpose**: Answer questions by traversing the knowledge graph. Token-efficient: summaries first, full nodes only when needed.

#### Steps

1. **Parse** the question for keywords, concepts, and domain signals.
2. **Scan INDEX.md** — Read node summaries to identify candidates. Do NOT load full bodies yet.
3. **Pillar auto-injection** — If the query's topic matches a `pillar` node's domain, automatically include that pillar's content in context. Pillars anchor reasoning to foundational beliefs.
4. **Traverse edges** — From candidate nodes, follow `supports`, `depends_on`, `derived_from`, and `part_of` edges to build a context subgraph.
5. **Load selectively** — Read the full body of only the most relevant nodes (typically 2–5). The goal is ~600 tokens of context, not ~9,000.
6. **Synthesize** — Generate an answer that references specific nodes.
7. **Lineage citations** — For every factual claim in the answer, trace it back through `derived_from` chains to the original raw source. Present citations as:
   ```
   Based on [[concept/attention-mechanism]] (confidence: 0.9, derived from [[source/transformer-paper]], verified 2026-06-01)
   ```
8. **Optionally file** — If the answer represents reusable knowledge, create a new node (usually `concept`, `fact`, or `note` type) and link it back into the graph.

---

### 6.3 Organize — `/organize-vault`

**Purpose**: Structural audit. Find and fix graph integrity issues.

#### Checks

1. **Orphan nodes** — Nodes with zero inbound AND zero outbound edges.
2. **Type mismatches** — Nodes in the wrong folder, or whose content better fits another type.
3. **Stale nodes** — `verified_at` older than 3 months with no `staleness_signal` override.
4. **Weak edges** — `related_to` edges that should be promoted to a specific type.
5. **Missing edges** — Semantically similar nodes with no connection.
6. **Missing nodes** — Concepts referenced in edges or body text that don't have their own node file.
7. **Contradictions** — Conflicting claims across nodes without a `contradicts` edge.
8. **Gaps** — Important topics implied by the existing graph but not yet covered.

#### Resolution

- Present all findings grouped by issue type.
- Propose specific fixes for each issue.
- **Never auto-fix.** Wait for human approval before applying any change.
- Log all changes to `_system/LOG.md`.

---

### 6.4 Health Check — `/vault-health`

**Purpose**: Apply confidence decay, detect degradation, generate health report.

#### Tiered Confidence Decay

Decay is applied based on the time elapsed since `verified_at`:

| Category | Node Types | Rate | Notes |
|----------|-----------|------|-------|
| **Exempt** | `pillar`, `decision`, `playbook` | No decay | Only lose confidence if explicitly invalidated |
| **Base** | `concept`, `question`, `task`, `event`, `pattern`, `hypothesis`, `bookmark`, `note`, `contact`, `reference`, `custom` | -0.04/month | Standard decay |
| **Fast** | `fact`, `source`, or any node with `volatility: volatile` | -0.08/month | Double decay for rapidly-changing information |

**Formula**: `new_confidence = max(0.0, current_confidence - (rate × months_since_verified))`

**Review threshold**: If confidence drops below **0.3**, flag the node in `_system/HEALTH-REPORT.md` for human review.

#### Modes

- **Interactive** (`/vault-health`): Present findings, ask for approval before applying decay and changes.
- **Automatic** (`/vault-health auto`): Apply decay silently, write report, no prompts.

#### Health Report Output

Update `_system/HEALTH-REPORT.md` with:
- Total node count by type
- Nodes below review threshold (0.3)
- Nodes with stale `verified_at` (> 3 months)
- Open contradictions count
- Orphan node count
- Suggested actions (re-verify, archive, seek new sources)

Log the health check run in `_system/LOG.md`.

---

### 6.5 Init — `/init-vault`

**Purpose**: Scaffold the vault structure. Idempotent — safe to run on an existing vault.

Creates:
- All 16 node-type folders
- `_system/` with `AGENTS.md`, `SCHEMA.md`, `INDEX.md`, `LOG.md`, `LOCAL-TYPES.md`, `HEALTH-REPORT.md`, `CONTRADICTIONS.md`
- `_system/templates/` with Templater-compatible templates for each node type
- `_system/scripts/` with shell scripts for all operations
- `raw/` with subdirectories: `articles/`, `papers/`, `transcripts/`, `images/`, `processed/`, `assets/`
- `.claude/skills/` and `.gemini/skills/` agent wrapper directories

---

## 7. Contradictions Management

**Every** `contradicts` edge triggers a registration in `_system/CONTRADICTIONS.md`.

### Registration Format

```markdown
### [YYYY-MM-DD] Node A ↔ Node B — Status: open

- **Node A**: [[type/node-a]] — "summary of claim A"
- **Node B**: [[type/node-b]] — "summary of claim B"
- **Conflict**: Description of what specifically conflicts.
- **Detected by**: agent | human
- **Status**: open | investigating | resolved
- **Resolution**: _(empty until resolved)_
```

### Resolution Protocol

1. Investigate both nodes and their source chains (`derived_from` edges).
2. Determine which claim has stronger evidence (higher confidence, more recent verification, more supporting edges).
3. Update the losing node's confidence downward.
4. Update the contradiction entry: set status to `resolved`, document the rationale.
5. Optionally: deprecate the weaker node if it's fully superseded.

---

## 8. Pillar Auto-Injection

`pillar` nodes represent foundational knowledge that should contextually inform all relevant queries and ingestion operations.

### Rules

- During `/query-vault`: If the query topic semantically matches a pillar's domain, load that pillar's full content into context before synthesizing the answer.
- During `/convert-note`: After decomposition, check each new node against existing pillars. If a new node falls under a pillar's domain, add a `part_of` or `supports` edge to that pillar.
- Pillars should be **short** (50–100 lines) and **high confidence** (0.9+). They are loaded frequently — keep them token-efficient.

---

## 9. Node Lineage & Citations

### `derived_from` Chains

Every node created from source material must have a `derived_from` edge pointing to its source. Sources themselves should have `derived_from` pointing to the raw file path.

This creates traceable chains:
```
concept/attention-mechanism
  └── derived_from → source/transformer-paper
       └── derived_from → raw/papers/attention-is-all-you-need.pdf
```

### Lineage Citations in Query Answers

When `/query-vault` synthesizes an answer, every factual claim must include a lineage citation:

```
The attention mechanism uses scaled dot-product scoring
(via [[concept/attention-mechanism]], conf: 0.95,
 derived from [[source/transformer-paper]], verified 2026-06-01).
```

This lets the human trace any claim back to raw evidence.

---

## 10. Conventions

### File Naming
- **Kebab-case**, lowercase: `pricing-philosophy.md`, `ltv-cac-ratio.md`
- Filename must match the `id` field in frontmatter (without the `.md` extension).
- No spaces, no special characters beyond hyphens.

### Markdown Style
- GitHub Flavored Markdown.
- No raw HTML in node files.
- Use Obsidian wikilinks for internal references: `[[concept/attention-mechanism]]` or `[[concept/attention-mechanism|Attention Mechanism]]` for display text.
- Use `vault://` protocol for cross-vault references (see §1).

### Body Structure

Every node body should follow this general structure:

```markdown
# Title (matches frontmatter title)

## Summary
1–3 sentence expansion of the frontmatter summary. Still concise.

## Content
The main body. Structured with sub-headings as needed.
Keep it focused and atomic.

## Open Questions
(Optional) Unresolved aspects of this node.

## References
(Optional) Inline references to source material not captured in edges.
```

### Log Entry Format

```markdown
## [YYYY-MM-DD] <operation> | "<subject>" | mode=<mode>
- Created: node-a (type), node-b (type)
- Updated edges on: existing-node-1, existing-node-2
- Contradictions flagged: node-x ↔ node-y (or "none")
- Nodes touched: N
```

### Index Entry Format

```markdown
- [[type/node-id|Node Title]] `type` — Summary text from frontmatter. (conf: 0.85)
```
