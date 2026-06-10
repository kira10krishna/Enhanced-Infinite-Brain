# LLM Knowledge Graph

A pattern for building personal knowledge bases using LLMs — enhanced with AI-first knowledge graph design.

This is an idea file. Copy-paste it to your LLM Agent (e.g. Claude Code, OpenAI Codex, Gemini CLI, or any agentic coding tool). Its goal is to communicate the high-level architecture so your agent can build out the specifics in collaboration with you.

---

## The Core Idea

Most people's experience with LLMs and documents looks like **RAG**: you upload files, the LLM retrieves relevant chunks at query time, and generates an answer. This works, but the LLM rediscoveres knowledge from scratch on every question. There's no accumulation. Ask a subtle question that requires synthesizing five documents, and the LLM has to find and piece together the relevant fragments every time. Nothing is built up.

The original improvement (Karpathy's "LLM Wiki") was to have the LLM incrementally build and maintain a **persistent wiki** — a structured, interlinked collection of markdown files. When you add a new source, the LLM reads it, extracts key information, and integrates it into existing wiki pages. Knowledge is compiled once and kept current, not re-derived on every query.

**This design takes that idea further.** The problem with a flat wiki is that notes are still written for *humans* — long-form pages, loose wikilinks, no metadata about *why* things connect. An AI agent reading a 285-line wiki essay wastes tokens on context it doesn't need, can't distinguish a verified fact from a tentative hypothesis, and has no way to know which connections matter most.

### The Mental Shift

> **Notes are written for the agent, not the human.** Humans can still read them. But the optimization target is different. You optimize for what an agent needs, and the human side comes along for free.

Instead of a flat wiki of long-form pages, the LLM builds and maintains a **typed knowledge graph** — a collection of small, atomic markdown files where every note is a **typed node** and every connection is a **typed edge**. The agent can navigate this graph precisely, reading only the 3–4 nodes it needs (~600 tokens) instead of scanning entire essays (~9,000 tokens). The structure *is* the retrieval mechanism.

---

## The Five Pillars of AI-First Design

### Pillar 1: Atomic Nodes

**One concept per file. 50 to 300 lines max.**

If a note covers pricing philosophy, monthly-versus-annual decisions, the no-free-tier decision, and an LTV calculation — that is four nodes, not one. Break monolithic documents into their atomic constituents. Each node should be self-contained: readable on its own, with a clear summary and typed frontmatter.

Why this matters: An agent retrieving "pricing philosophy" doesn't need the LTV calculation in its context window. Atomic nodes let it pull exactly what it needs.

### Pillar 2: Typed Nodes (16 types)

Every node has exactly one type. The folder name equals the type. The agent dispatches differently on a `pillar` than on a `note` — it knows a `fact` needs a source citation, a `hypothesis` needs a test, a `playbook` has steps to follow.

**The 16 node types**, organized by category:

#### Foundational (core beliefs, frameworks, and recorded choices)

| Type | Description |
|------|-------------|
| `pillar` | Foundational identity or principle. Auto-injects on matching context. |
| `decision` | A concrete choice made between alternatives. ADR style. |
| `concept` | A defined term or framework the agent should reason from. |
| `question` | A known unknown being tracked. Becomes a hypothesis once testable. |

#### Procedural (actions, processes, and temporal events)

| Type | Description |
|------|-------------|
| `playbook` | A repeatable procedure with steps, triggers, expected outcomes. |
| `task` | An actionable item, usually synced from a real task system. |
| `event` | A dated event the agent should reason about temporally. |
| `pattern` | An observed regularity in data or behavior. Heuristic. |

#### Evidential (claims, proof, and external references)

| Type | Description |
|------|-------------|
| `hypothesis` | A falsifiable prediction with a measurable test. |
| `fact` | A verified atomic statement with a specific source and date. |
| `source` | An external reference (book, article, talk) plus your synthesis. |
| `bookmark` | A saved link with light annotation, not yet a source. |

#### Structural (organizational and meta nodes)

| Type | Description |
|------|-------------|
| `note` | Low-priority scratch or pre-atomized observation. |
| `contact` | A person node with relationship metadata. |
| `reference` | A pointer to a config, schema, or pinned doc. |
| `custom` | Workspace-specific type that doesn't fit the 15 above. Documented in `_system/LOCAL-TYPES.md`. |

### Pillar 3: Typed Edges (10 relationships)

Every connection between nodes is explicit. Each edge has a **direction** (A → B or A ↔ B), a **weight** (0.0–1.0), and an optional **note** explaining why the connection exists.

| Edge Type | Direction | Description | Default Weight |
|-----------|-----------|-------------|----------------|
| `supports` | A → B | Source provides evidence for target. | 0.7 |
| `contradicts` | A ↔ B | Source disagrees with or invalidates target. | 1.0 |
| `depends_on` | A → B | Target must be true before source makes sense. | 0.8 |
| `derived_from` | A → B | Source was created based on target. Lineage edge. | 0.9 |
| `related_to` | A ↔ B | Topical connection, no stronger relationship known. | 0.5 |
| `part_of` | A → B | Source is a component of target. | 0.8 |
| `preceded_by` | A → B | Source comes after target in time. | 0.7 |
| `followed_by` | A → B | Source comes before target in time. | 0.7 |
| `authored_by` | A → B | Target is the author or originator of source. | 1.0 |
| `tagged_with` | A → B | Source carries a topic tag that is itself a node. | 0.5 |

Why typed edges matter: A wikilink `[[pricing]]` tells the agent nothing about *why* two notes connect. A typed edge `supports (0.8): "Revenue data backs this pricing model"` tells it everything.

### Pillar 4: Trust Metadata

Every node carries metadata that tells the agent how much to trust it:

```yaml
---
node_type: concept
summary: "One-line summary the agent reads first before deciding to load the full body."
confidence: 0.85          # 0.0–1.0, how certain is this content
verified_at: 2026-06-10   # when last validated
verified_by: human        # who/what validated it (human | agent | auto)
staleness_signal: "Re-check if Q3 revenue data arrives"
visibility: public        # public | namespace | private | system
edges:
  - target: "[[pricing-philosophy]]"
    type: supports
    weight: 0.8
    note: "Revenue data backs this model"
  - target: "[[ltv-cac-ratio]]"
    type: derived_from
    weight: 0.9
---
```

**Confidence decay**: Over time, nodes that haven't been re-verified lose confidence automatically. The `/vault-health` operation applies decay and flags stale nodes for human review. This prevents the knowledge base from silently rotting.

### Pillar 5: Namespaces with Visibility

Not all knowledge should be equally accessible. The `visibility` field controls scope:

- **`public`** — Any agent or human can read. Default for most knowledge.
- **`namespace`** — Scoped to a specific project or domain area.
- **`private`** — Personal notes, journal entries, sensitive data. Agent reads only when explicitly asked.
- **`system`** — Schema files, templates, agent instructions. Infrastructure.

---

## The Molecule Concept

Atomic nodes compose into **molecules** — clusters of related nodes connected by typed edges that together represent a complete topic.

**Example:** A monolithic pricing essay splits into six typed nodes:

```
┌──────────┐  ┌──────────────┐  ┌──────────────┐
│  PILLAR   │  │   DECISION   │  │     FACT     │
│ pricing-  │  │  monthly-    │  │  mrr-april-  │
│ philosophy│  │  default     │  │  2026        │
└────┬──────┘  └──────┬───────┘  └──────┬───────┘
     │                │                  │
     │    ┌───────────┴──────────┐       │
     │    │       CONCEPT        │       │
     │    │    ltv-cac-ratio     ├───────┘
     │    └───────────┬──────────┘
     │                │
┌────┴──────┐  ┌──────┴───────────┐
│  SOURCE   │  │   HYPOTHESIS     │
│ firstround│  │ creators-will-   │
│ -pricing  │  │ pay-29mo         │
│ -guide    │  │                  │
└───────────┘  └──────────────────┘
```

**The result:** The agent reads three summaries plus one auto-injected pillar to answer a pricing question. Total cost: ~600 tokens. Same content that lived as a 285-line essay in a flat wiki.

### The Summary Field is the Secret Weapon

Every node has a `summary` field in its frontmatter. This is a one-line, agent-optimized description of the node's content. When the agent traverses the graph, it reads summaries first. If a summary is sufficient, it never loads the body. If it needs depth, it loads only the specific nodes whose summaries indicate relevance.

This is what makes the graph dramatically more token-efficient than a flat wiki or RAG:
- **Flat wiki**: Read entire 285-line page → ~9,000 tokens
- **RAG**: Retrieve 5 chunks, most partially relevant → ~3,000 tokens
- **Knowledge graph**: Read 4 summaries, load 2 full nodes → ~600 tokens

---

## Architecture

There are four layers (enhanced from the original three):

### Layer 1: Raw Sources

Your curated collection of source documents. Articles, papers, images, data files, web clips, podcast transcripts. These are **immutable** — the LLM reads from them but never modifies them. This is your source of truth.

```
raw/
├── articles/
├── papers/
├── transcripts/
├── images/
├── processed/          # originals moved here after conversion
└── assets/             # downloaded images from web clips
```

### Layer 2: The Knowledge Graph (replaces flat wiki)

A directory of LLM-generated atomic markdown files, organized by node type. Each type gets its own folder. The LLM owns this layer entirely — it creates nodes, updates them when new sources arrive, maintains edges, applies trust metadata, and keeps everything consistent.

```
pillar/
concept/
decision/
question/
playbook/
task/
event/
pattern/
hypothesis/
fact/
source/
bookmark/
note/
contact/
reference/
custom/
```

### Layer 3: The System Layer (replaces single schema file)

The `_system/` directory contains everything the agent needs to understand and operate on the knowledge graph.

```
_system/
├── AGENTS.md           # Agent instructions: how to ingest, query, organize, maintain
├── INDEX.md            # The graph's table of contents — every node listed with summary
├── SCHEMA.md           # Node templates, edge type definitions, frontmatter rules
├── LOCAL-TYPES.md      # Custom domain-specific node types (extends the 16)
├── LOG.md              # Chronological record of operations
└── HEALTH-REPORT.md    # Latest vault health audit results
```

**`AGENTS.md`** is the key configuration file — it's what makes the LLM a disciplined knowledge graph maintainer rather than a generic chatbot. It defines:
- How to decompose raw material into atomic typed nodes
- Rules for edge creation (when to use `supports` vs. `related_to`, etc.)
- Confidence scoring guidelines
- Query strategies (graph traversal patterns)
- Maintenance protocols

**`INDEX.md`** is the agent's entry point. Before doing anything, the agent reads the index to understand what exists. Each entry has a link, a type badge, and the node's summary. At moderate scale (~100 sources, ~hundreds of nodes), the index + summaries is all the retrieval mechanism you need — no embedding infrastructure required.

### Layer 4: Raw Sources (unchanged)

Same as described above. Immutable source of truth.

---

## Operations

### 1. Init (`/init-vault`)

Scaffold the knowledge graph structure in any directory. Creates all type folders, `_system/` with schema templates, `raw/` for source material, and starter `AGENTS.md` with default instructions.

### 2. Ingest / Convert (`/convert-note`)

You drop a new source into `raw/` and tell the LLM to process it. The flow:

1. **Read** the source material
2. **Discuss** key takeaways with you (optional, depends on your workflow preference)
3. **Decompose** into atomic typed nodes — one file per concept, each with proper frontmatter
4. **Create edges** between the new nodes and existing graph nodes
5. **Update the index** with new entries and summaries
6. **Write a source node** in `source/` linking back to the raw material
7. **Move** the processed source to `raw/processed/`
8. **Append** an entry to the log

A single source might produce 5–15 new nodes and touch 10–20 existing ones (updating edges, revising confidence, flagging contradictions).

**Workflow flexibility:** You can ingest one source at a time and stay involved (reviewing summaries, guiding emphasis), or batch-ingest many sources with less supervision. Document your preferred workflow in `AGENTS.md`.

### 3. Query (`/query-vault`)

You ask questions against the knowledge graph. The agent:

1. **Reads the index** to identify relevant nodes by scanning summaries
2. **Traverses edges** to find connected context (supports, depends_on, derived_from chains)
3. **Loads only the nodes it needs** — summaries first, full body only when required
4. **Synthesizes an answer** with citations back to specific nodes and raw sources

Answers can take different forms: a markdown page, a comparison table, a slide deck (Marp), a chart, a canvas. **Important:** Good answers should be filed back into the knowledge graph as new nodes. A comparison you asked for, an analysis, a connection you discovered — these compound in the knowledge base rather than disappearing into chat history.

**Pillar auto-injection:** When a query matches the domain of a `pillar` node, that pillar is automatically included in the agent's context. This ensures foundational beliefs consistently inform answers without being explicitly requested.

### 4. Organize / Lint (`/organize-vault`)

Interactive audit of the knowledge graph. The agent scans for:

- **Contradictions** between nodes (edges of type `contradicts` or conflicting claims)
- **Stale nodes** whose confidence has decayed below threshold
- **Orphan nodes** with no inbound edges
- **Missing nodes** — concepts mentioned in edges but lacking their own node
- **Weak edges** — connections typed as `related_to` that could be strengthened to a more specific type
- **Missing cross-references** between nodes that should be connected
- **Gaps** — important topics suggested by existing nodes but not yet covered
- **Type mismatches** — nodes that might be better classified as a different type

The agent identifies issues and proposes fixes, but **never auto-fixes**. Structural changes require human approval.

### 5. Health Check (`/vault-health`)

Automated maintenance. Can be scheduled (e.g., weekly). The agent:

- **Applies confidence decay** — nodes not re-verified lose confidence over time
- **Generates a health report** node in `_system/HEALTH-REPORT.md`
- **Flags** nodes crossing below confidence thresholds
- **Suggests** sources to seek, questions to investigate, nodes to verify

Two modes:
- **Interactive** (`/vault-health`): Reports findings and asks for approval before changes
- **Automatic** (`/vault-health auto`): Applies decay and writes report silently, no prompts

---

## Indexing and Logging

### `_system/INDEX.md` — Content-Oriented

A catalog of every node in the graph. Each entry includes:
- A link to the node file
- The node type (badge)
- The summary from the node's frontmatter
- Optionally: confidence score, edge count, last modified date

Organized by type (pillars first, then concepts, decisions, etc.). The agent reads this before any operation to find relevant nodes. At moderate scale, this replaces the need for embedding-based RAG entirely.

### `_system/LOG.md` — Chronological

An append-only record of what happened and when — ingests, queries, lint passes, health checks. Each entry follows a consistent format:

```markdown
## [2026-06-10] ingest | Article: "Pricing Strategy for Creators"
- Created: pricing-philosophy (pillar), monthly-default (decision), ltv-cac-ratio (concept)
- Updated edges on: revenue-model, creator-economics
- New contradictions flagged: none
- Nodes touched: 12
```

The log is parseable with unix tools: `grep "^## \[" _system/LOG.md | tail -5` gives the last 5 operations.

---

## Node Template

Every node follows this template:

```markdown
---
node_type: concept
summary: "LTV-to-CAC ratio measures customer lifetime value against acquisition cost."
confidence: 0.85
verified_at: 2026-06-10
verified_by: human
staleness_signal: "Re-verify when Q3 financials arrive"
visibility: public
edges:
  - target: "[[pricing-philosophy]]"
    type: supports
    weight: 0.8
    note: "Core metric behind the pricing model"
  - target: "[[mrr-april-2026]]"
    type: derived_from
    weight: 0.9
  - target: "[[firstround-pricing-guide]]"
    type: derived_from
    weight: 0.7
    note: "Framework adapted from this source"
tags: [pricing, metrics, unit-economics]
created: 2026-06-10
modified: 2026-06-10
source_refs: ["raw/articles/firstround-pricing.md"]
---

# LTV-to-CAC Ratio

[Body content: 50–300 lines of atomic, focused content on this single concept]

The LTV-to-CAC ratio compares the total revenue expected from a customer over their
lifetime against the cost of acquiring them...

## Key Thresholds
- Healthy SaaS: 3:1 or higher
- Below 1:1: unsustainable unit economics
...
```

---

## Use Cases

This applies to many contexts. The typed knowledge graph makes each one more powerful than a flat wiki because the structure encodes domain-specific relationships:

- **Personal development**: Track goals, health, psychology. Node types: `pillar` (core values), `pattern` (behavioral observations), `hypothesis` (self-improvement experiments), `event` (journal entries).
- **Research**: Going deep on a topic over months. `source` nodes for papers, `concept` nodes for frameworks, `hypothesis` for your evolving thesis, `fact` for verified claims, `contradiction` edges for unresolved debates.
- **Reading a book**: `event` for plot points, `contact` for characters, `concept` for themes, `pattern` for motifs, `question` for unresolved mysteries. By the end: a rich companion graph, like a personal Tolkien Gateway.
- **Business/team**: Internal knowledge graph fed by Slack, meeting transcripts, project docs. `decision` nodes (ADR style), `playbook` for processes, `task` for action items, `contact` for team members.
- **Competitive analysis, due diligence, trip planning, course notes** — anything where you're accumulating knowledge and want it structured rather than scattered.

---

## Optional: CLI Tools

At small scale, the index file is sufficient for retrieval. As the graph grows, you'll want search:

- **`qmd`**: Local search engine for markdown files with hybrid BM25/vector search and LLM re-ranking, all on-device. CLI + MCP server.
- **Custom scripts**: The LLM can help you build naive search scripts as the need arises (e.g., grep over frontmatter, edge traversal scripts).
- **Obsidian Dataview**: If using Obsidian, the Dataview plugin can query node frontmatter to generate dynamic tables (e.g., "show all nodes with confidence < 0.5").

---

## Tips and Tricks

- **Obsidian Web Clipper** converts web articles to markdown — fastest way to get sources into `raw/`.
- **Download images locally**: In Obsidian settings, set attachment folder to `raw/assets/`, bind "Download attachments" to a hotkey. Lets the LLM reference images directly instead of relying on URLs that may break.
- **Obsidian's graph view** visualizes the knowledge graph — see hubs, orphans, clusters. The typed edges make the graph view dramatically more informative than in a flat wiki.
- **Marp** for generating slide decks directly from graph content.
- **Dataview** for dynamic queries over node frontmatter (tags, confidence, dates).
- **Git** — the knowledge graph is just a git repo of markdown files. Version history, branching, and collaboration for free.
- **Pillar auto-injection** — keep your most important `pillar` nodes short and high-confidence. They'll be automatically included in relevant queries, anchoring the agent's reasoning to your core beliefs.

---

## Why This Works Better Than a Flat Wiki

| Dimension | Flat Wiki (Karpathy) | Knowledge Graph (This Design) |
|-----------|---------------------|-------------------------------|
| **Unit of knowledge** | Long-form pages (500–2000 lines) | Atomic nodes (50–300 lines) |
| **Connections** | Wikilinks (`[[page]]`) — no semantics | Typed edges with direction, weight, reason |
| **Retrieval cost** | Read entire pages (~9,000 tokens) | Read summaries, load targeted nodes (~600 tokens) |
| **Trust** | None — all content treated equally | Confidence scores, verification dates, decay |
| **Contradiction handling** | Manual, often missed | Explicit `contradicts` edges, auto-flagged |
| **Maintenance** | Index + log only | Health checks, confidence decay, orphan detection |
| **Agent reasoning** | Generic chatbot on files | Typed dispatch (handles pillar ≠ note ≠ hypothesis) |

The tedious part of maintaining a knowledge base is not the reading or the thinking — it's the bookkeeping. Updating cross-references, scoring confidence, noting contradictions, maintaining consistency across hundreds of nodes. Humans abandon wikis because the maintenance burden grows faster than the value. LLMs don't get bored, don't forget to update an edge, and can touch 20 files in one pass. The knowledge graph stays maintained because the cost of maintenance is near zero.

**The human's job:** Curate sources, direct the analysis, ask good questions, think about what it all means.
**The LLM's job:** Everything else — decomposing, typing, linking, scoring, maintaining, and searching.

---

## Historical Context

The idea is related to Vannevar Bush's Memex (1945) — a personal, curated knowledge store with associative trails between documents. Bush's vision was closer to this than to what the web became: private, actively curated, with the connections between documents as valuable as the documents themselves. The part he couldn't solve was who does the maintenance. The LLM handles that. The typed knowledge graph adds something Bush couldn't have imagined: machine-readable semantics on every connection.

---

## Note

This document is intentionally abstract. It describes the pattern, not a specific implementation. The exact frontmatter schema, the confidence decay curve, the pillar auto-injection logic, the query traversal strategy — all will depend on your domain, your preferences, and your LLM. Everything is optional and modular. The right way to use this is to share it with your LLM agent and work together to build a version that fits your needs.
