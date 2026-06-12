---
name: query-vault
description: Answer a question against the knowledge graph by traversing it — read INDEX summaries, auto-inject matching pillars, follow typed edges, load only the nodes needed, and synthesize a cited answer. Optionally file the answer back as a new node. Use when the user asks a question they want answered from the vault/second brain, or wants a synthesis/comparison/analysis grounded in stored knowledge.
---

# /query-vault

Answer by traversing the graph, not by re-reading everything. Implements [AGENTS.md](../../../_system/AGENTS.md) §2.2. The goal is a correct, cited answer at minimum token cost.

## Inputs
- `$ARGUMENTS`: the question. If empty, ask for it.

## Steps

1. **Read `_system/INDEX.md`.** Scan *summaries* to pick candidate nodes. Do **not** load bodies yet.
2. **Auto-inject pillars.** If the question matches a `pillar`'s domain (tags/summary/edges), load that pillar's body now — foundational beliefs should shape every relevant answer (AGENTS §4).
3. **Traverse edges** from candidates: follow `supports`, `depends_on`, `derived_from`, `contradicts` chains. Read neighbor *summaries* first.
4. **Load full bodies** only for nodes whose summaries prove they're needed. Track roughly how many nodes/tokens you loaded — staying lean is the point of the graph.
5. **Synthesize** the answer. **Cite** specific nodes as `[[node-name]]` and raw sources by path. Surface any `contradicts` edges as open tensions rather than hiding them. Respect confidence — flag low-confidence or stale inputs.
6. **Honor visibility:** read `private` nodes only if the user explicitly asks.
7. **Offer to file the answer back** as a new node (a `concept`, `note`, or `pattern`) so the synthesis compounds instead of vanishing into chat. In supervised mode, ask first; in autonomous mode, file it and log it.

## Output
The answer, a **Sources** line listing the nodes/raw files cited, and a one-line note on traversal cost (e.g. "scanned INDEX, loaded 4 nodes").

## Notes
- If candidate summaries are thin or the answer isn't in the graph, say so plainly — don't hallucinate. Suggest a `/convert-note` if a source is missing.
- Append a brief `query` entry to `_system/LOG.md` for non-trivial queries.
