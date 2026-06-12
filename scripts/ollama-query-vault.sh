#!/usr/bin/env bash
# /query-vault equivalent using a local Ollama model.
#
# Usage:
#   ./ollama-query-vault.sh "What are the main risks of automated AI R&D?"
#   ./ollama-query-vault.sh "..." --model qwen3:27b --save    # save answer as a note node

set -euo pipefail
source "$(dirname "$0")/_lib.sh"

# ── Args ──────────────────────────────────────────────────────────────────────

QUESTION=""
MODEL="$DEFAULT_MODEL"
SAVE_ANSWER=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --model) MODEL="$2"; shift 2 ;;
    --save)  SAVE_ANSWER=true; shift ;;
    *)       QUESTION="$1"; shift ;;
  esac
done

[[ -z "$QUESTION" ]] && {
  echo "Usage: $0 \"<question>\" [--model MODEL] [--save]"
  echo "  --save  Write the answer back as a 'note' node in the graph"
  exit 1
}

# ── Preflight ─────────────────────────────────────────────────────────────────

check_deps
check_ollama
check_model "$MODEL"

hr
bold "Infinite Brain — query-vault (Ollama)"
echo "  Model   : $MODEL"
echo "  Question: $QUESTION"
hr

# ── Load context ──────────────────────────────────────────────────────────────

SYSTEM=$(system_context)
INDEX=$(load_index)

# Auto-inject pillar nodes into context
PILLAR_CONTEXT=""
if ls "$VAULT_ROOT/pillar/"*.md &>/dev/null 2>&1; then
  for f in "$VAULT_ROOT/pillar/"*.md; do
    PILLAR_CONTEXT+="$(cat "$f")"$'\n\n---\n\n'
  done
fi

# ── Phase 1: Identify relevant nodes ─────────────────────────────────────────

bold "Phase 1: Identifying relevant nodes..."

RELEVANCE_PROMPT="A user is asking: \"$QUESTION\"

Here is the full knowledge graph index:
<index>
$INDEX
</index>

List the filenames of the most relevant nodes to load for answering this question.
Return a JSON array of filename strings only, ordered by relevance. Maximum 12 nodes.
Example: [\"concept/ai-rd-progress-multiplier.md\", \"hypothesis/superhuman-coder-by-2027.md\"]

Return ONLY the JSON array. No explanation."

NODES_RAW=$(ollama_chat "$MODEL" "$SYSTEM" "$RELEVANCE_PROMPT" false)
NODES_JSON=$(echo "$NODES_RAW" | sed 's/^```json//;s/^```//' | sed '/^```/d')

if ! echo "$NODES_JSON" | jq '.' &>/dev/null; then
  yellow "WARNING: Could not parse node list. Loading all nodes."
  NODES_JSON="[]"
fi

echo "$NODES_JSON" | jq -r '.[]' | while read -r f; do echo "  → $f"; done

# ── Phase 2: Load node contents ───────────────────────────────────────────────

bold "Phase 2: Loading node contents..."

NODE_CONTENTS=""
while IFS= read -r filepath; do
  fullpath="$VAULT_ROOT/$filepath"
  if [[ -f "$fullpath" ]]; then
    NODE_CONTENTS+="### $filepath"$'\n'
    NODE_CONTENTS+="$(cat "$fullpath")"$'\n\n---\n\n'
  else
    yellow "  MISSING: $filepath"
  fi
done < <(echo "$NODES_JSON" | jq -r '.[]')

# ── Phase 3: Answer ───────────────────────────────────────────────────────────

bold "Phase 3: Synthesising answer..."

ANSWER_PROMPT="Answer the following question using only the knowledge graph nodes provided.

Question: $QUESTION

${PILLAR_CONTEXT:+User's foundational beliefs (pillars — treat as authoritative context):
<pillars>
$PILLAR_CONTEXT
</pillars>
}

Relevant nodes:
<nodes>
$NODE_CONTENTS
</nodes>

Instructions:
- Cite specific nodes using [[node-name]] notation inline
- Note confidence levels when relevant (e.g. 'confidence 0.5 — speculative')
- Flag any contradictions between nodes
- If the graph doesn't have enough information, say so clearly
- Aim for a structured, scannable answer (use headers if the answer is long)"

hr
ollama_chat "$MODEL" "$SYSTEM" "$ANSWER_PROMPT" true
hr

# ── Optionally save as note node ──────────────────────────────────────────────

if [[ "$SAVE_ANSWER" == true ]]; then
  TODAY=$(today)
  SLUG="query-$(echo "$QUESTION" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | cut -c1-40)"
  DEST="$VAULT_ROOT/note/$SLUG.md"
  mkdir -p "$VAULT_ROOT/note"

  ANSWER=$(ollama_chat "$MODEL" "$SYSTEM" "$ANSWER_PROMPT" false)

  cat > "$DEST" <<EOF
---
node_type: note
summary: "Query answer: $QUESTION"
confidence: 0.7
verified_at: $TODAY
verified_by: agent
visibility: private
edges: []
tags: [query, auto-generated]
created: $TODAY
modified: $TODAY
---

# Query: $QUESTION

$ANSWER
EOF

  green "Answer saved as note: note/$SLUG.md"
  append_log "## [$TODAY] query | Ollama/$MODEL
- Question: $QUESTION
- Nodes loaded: $(echo "$NODES_JSON" | jq 'length')
- Answer saved: note/$SLUG.md"
fi
