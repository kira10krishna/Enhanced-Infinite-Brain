# Implementation Plan: LLM Knowledge Graph (Second Brain)

Build an AI-first knowledge graph system in the existing Obsidian vault at `/Users/kira/Documents/Brains/Knowledge`, implementing the enhanced LLM Wiki pattern described in [llm_knowledge_graph.md](file:///Users/kira/.gemini/antigravity-ide/brain/4948fc23-0ede-4c5c-9ac0-05dfd22a2374/llm_knowledge_graph.md).

## Resolved Questions

1. **LLM Agent**: Both Claude Code (`.claude/skills/`) AND Antigravity/Gemini. Also create `AGENTS.md` as a universal instructions file.
2. **Domain**: Knowledge & research vault. (Separate vaults planned for personal and business later.)
3. **Workflow**: All three modes — Supervised (primary), Hybrid, and Autonomous. Controlled via a flag.
4. **Implementation**: All formats — Claude Code skills, shell scripts, AND AGENTS.md instructions.
5. **Confidence decay**: `-0.05/month` rate, `0.4` review threshold. Gentle defaults for a research vault.

---

## Proposed Changes

### Phase 1: Vault Scaffolding & Schema

Create the directory structure, system files, and node templates that define the knowledge graph.

---

#### [NEW] Directory Structure

Scaffold all 16 node-type folders + system + raw directories in the vault:

```
/Users/kira/Documents/Brains/Knowledge/
├── _system/
│   ├── AGENTS.md            # Master agent instructions
│   ├── INDEX.md             # Graph table of contents
│   ├── SCHEMA.md            # Node/edge type definitions + templates
│   ├── LOCAL-TYPES.md       # Custom types (starts empty)
│   ├── LOG.md               # Chronological operation record
│   └── HEALTH-REPORT.md     # Latest vault health audit
├── raw/
│   ├── articles/
│   ├── papers/
│   ├── transcripts/
│   ├── images/
│   ├── processed/
│   └── assets/
├── pillar/
├── concept/
├── decision/
├── question/
├── playbook/
├── task/
├── event/
├── pattern/
├── hypothesis/
├── fact/
├── source/
├── bookmark/
├── note/
├── contact/
├── reference/
├── custom/
└── .obsidian/               # (existing — Obsidian config)
```

---

#### [NEW] [AGENTS.md](file:///Users/kira/Documents/Brains/Knowledge/_system/AGENTS.md)

The master instructions file. Defines:
- Role: "You are a Knowledge Architect maintaining a typed knowledge graph"
- Node creation rules (atomic, 50–300 lines, one type per file)
- Edge creation rules (when to use each of the 10 types, weight guidelines)
- Frontmatter schema (all required and optional fields)
- Ingest workflow (read → decompose → create nodes → create edges → update index → log)
- Query workflow (read index → traverse edges → load summaries → load full nodes if needed)
- Organize workflow (scan for contradictions, orphans, staleness, gaps)
- Health check workflow (apply decay, generate report)
- Pillar auto-injection rules
- Naming conventions (kebab-case filenames, e.g., `pricing-philosophy.md`)

---

#### [NEW] [SCHEMA.md](file:///Users/kira/Documents/Brains/Knowledge/_system/SCHEMA.md)

Complete reference for:
- All 16 node types with descriptions and when to use each
- All 10 edge types with direction semantics, weight defaults, and usage examples
- Trust metadata field definitions
- Visibility levels
- YAML frontmatter template for each node type (slight variations per type)
- Naming conventions

---

#### [NEW] [INDEX.md](file:///Users/kira/Documents/Brains/Knowledge/_system/INDEX.md)

Starts as a skeleton:
```markdown
# Knowledge Graph Index
> Last updated: 2026-06-11

## Pillars
_No nodes yet._

## Concepts
_No nodes yet._

[...for each of the 16 types...]
```

---

#### [NEW] [LOG.md](file:///Users/kira/Documents/Brains/Knowledge/_system/LOG.md)

Starts with the init entry:
```markdown
# Operation Log

## [2026-06-11] init | Vault scaffolded
- Created directory structure (16 type folders + _system + raw)
- Created AGENTS.md, SCHEMA.md, INDEX.md, LOG.md
- Vault ready for first ingest
```

---

#### [NEW] Node templates

Obsidian Templater-compatible templates stored in `_system/templates/` for each node type. Each template pre-fills the correct `node_type`, required frontmatter fields, and body structure guidance.

---

### Phase 2: Agent Operations (Skills / Instructions)

Build the 5 core operations. Implementation format depends on your answer to Open Question #4.

---

#### [NEW] `/init-vault` operation

- Creates all directories if they don't exist
- Writes starter `AGENTS.md`, `SCHEMA.md`, `INDEX.md`, `LOG.md`
- Idempotent (safe to run on an existing vault)

#### [NEW] `/convert-note` operation

The most complex operation:
1. Accept a file path (in `raw/`) or raw text
2. Read and analyze the content
3. Identify atomic concepts (each becomes a node)
4. Assign types to each node
5. Generate frontmatter (summary, confidence, edges)
6. Create node files in the appropriate type folders
7. Scan existing graph for edge targets (related nodes)
8. Create a `source` node linking back to the raw material
9. Update `INDEX.md` with new entries
10. Move original to `raw/processed/`
11. Append to `LOG.md`

#### [NEW] `/query-vault` operation

1. Parse the question
2. Read `INDEX.md` to find candidate nodes by scanning summaries
3. Traverse edges from candidate nodes to find supporting context
4. Read full body of most relevant nodes
5. Auto-inject matching `pillar` nodes
6. Synthesize answer with citations
7. Optionally: file the answer as a new node

#### [NEW] `/organize-vault` operation

Interactive audit:
1. Scan all nodes for structural issues
2. Present findings grouped by issue type
3. Propose fixes (new edges, type changes, new nodes)
4. Apply fixes only with human approval

#### [NEW] `/vault-health` operation

Automated maintenance:
1. Apply confidence decay to all nodes based on `verified_at` age
2. Scan for nodes below confidence threshold
3. Generate `HEALTH-REPORT.md` with stats and recommendations
4. In `auto` mode: silent operation, no prompts
5. In interactive mode: present findings and ask for approval

---

### Phase 3: Tooling Integration

#### [MODIFY] Obsidian Configuration

- Configure Templater plugin to use `_system/templates/`
- Configure attachment folder to `raw/assets/`
- Install/configure Dataview plugin for frontmatter queries
- Set up graph view with type-based coloring (one color per node type)

#### [NEW] Git initialization

```bash
cd /Users/kira/Documents/Brains/Knowledge
git init
echo ".obsidian/workspace.json" >> .gitignore
git add -A && git commit -m "init: scaffold knowledge graph vault"
```

---

### Phase 4: Seed Content & Test

#### First ingest test

- Take an existing article or note and run `/convert-note` on it
- Verify: correct node types, proper frontmatter, edges created, index updated, log entry written
- Run `/query-vault` against the new content
- Run `/organize-vault` to check for structural issues

---

## Verification Plan

### Automated Tests
- Validate all node files have required frontmatter fields (script to check YAML)
- Validate all edge targets resolve to existing files
- Validate INDEX.md entries match actual files on disk
- Lint for orphan nodes (no inbound edges)

### Manual Verification
- Browse the vault in Obsidian and verify graph view shows typed connections
- Run a test ingest and review the decomposition quality
- Ask a query and verify the answer uses graph traversal (check token count)
- Run vault-health and verify confidence decay applies correctly
