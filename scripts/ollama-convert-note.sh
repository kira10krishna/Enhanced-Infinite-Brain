#!/usr/bin/env bash
# /convert-note equivalent using a local Ollama model.
#
# Usage:
#   ./ollama-convert-note.sh <path-to-raw-file> [--model qwen3:27b] [--mode supervised|hybrid|autonomous]
#
# Examples:
#   ./ollama-convert-note.sh raw/articles/my-paper.md
#   ./ollama-convert-note.sh raw/articles/my-paper.md --model qwen3:27b --mode autonomous

set -euo pipefail
source "$(dirname "$0")/_lib.sh"

# ── Args ──────────────────────────────────────────────────────────────────────

SOURCE_FILE=""
MODEL="$DEFAULT_MODEL"
MODE="supervised"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --model) MODEL="$2"; shift 2 ;;
    --mode)  MODE="$2";  shift 2 ;;
    *)       SOURCE_FILE="$1"; shift ;;
  esac
done

[[ -z "$SOURCE_FILE" ]] && { echo "Usage: $0 <source-file> [--model MODEL] [--mode supervised|hybrid|autonomous]"; exit 1; }

# Resolve path relative to vault root if not absolute
[[ "$SOURCE_FILE" != /* ]] && SOURCE_FILE="$VAULT_ROOT/$SOURCE_FILE"

[[ -f "$SOURCE_FILE" ]] || { red "ERROR: File not found: $SOURCE_FILE"; exit 1; }

# ── Preflight ─────────────────────────────────────────────────────────────────

check_deps
check_ollama
check_model "$MODEL"

hr
bold "Infinite Brain — convert-note (Ollama)"
echo "  Model : $MODEL"
echo "  Mode  : $MODE"
echo "  Source: $SOURCE_FILE"
hr

# ── Load context ──────────────────────────────────────────────────────────────

SYSTEM=$(system_context)
INDEX=$(load_index)
DOC=$(cat "$SOURCE_FILE")
TODAY=$(today)
BASENAME=$(basename "$SOURCE_FILE")

# ── PHASE 1: Decomposition manifest ──────────────────────────────────────────

bold "Phase 1: Decomposing document into atomic nodes..."

MANIFEST_PROMPT="You are ingesting a source document into a typed knowledge graph.

Current graph index (existing nodes you can edge to):
<index>
$INDEX
</index>

Today's date: $TODAY

Source document:
<document>
$DOC
</document>

Task: Decompose this document into atomic nodes. Each node = one concept, fact, event, hypothesis, etc.

Return a JSON array. Each element:
{
  \"filename\": \"<type>/<slug>.md\",
  \"type\": \"<node_type>\",
  \"summary\": \"<one-line agent-optimized summary>\",
  \"confidence\": <0.0-1.0>,
  \"edges\": [\"target: [[slug]], type: <edge_type>, weight: <0.0-1.0>\"],
  \"notes\": \"<any decomposition notes>\"
}

Fidelity rules (strictly enforce):
- NO pillar nodes from external sources — pillars = user's beliefs only
- NO decision nodes for choices by actors inside the document — use event
- Forecasts → hypothesis
- Cited real-world claims → fact
- Defined mechanisms → concept
- Dated story beats → event

Return ONLY the JSON array. No explanation, no markdown fences."

yellow "Calling Ollama for manifest (this may take 1-3 minutes)..."
MANIFEST_RAW=$(ollama_chat "$MODEL" "$SYSTEM" "$MANIFEST_PROMPT" true)

# Strip markdown fences if model added them anyway
MANIFEST_JSON=$(echo "$MANIFEST_RAW" | sed 's/^```json//;s/^```//' | sed '/^```/d')

# Validate JSON
if ! echo "$MANIFEST_JSON" | jq '.' &>/dev/null; then
  red "ERROR: Model returned invalid JSON. Raw output:"
  echo "$MANIFEST_RAW"
  exit 1
fi

NODE_COUNT=$(echo "$MANIFEST_JSON" | jq 'length')
green "Manifest received: $NODE_COUNT nodes proposed"
hr

# ── Show manifest (supervised + hybrid) ───────────────────────────────────────

echo "$MANIFEST_JSON" | jq -r '.[] | "  [\(.type)] \(.filename)\n    \(.summary)\n    confidence: \(.confidence)\n"'
hr

if [[ "$MODE" == "supervised" ]]; then
  echo -n "Approve this manifest and write all nodes? [y/N] "
  read -r APPROVAL
  [[ "$APPROVAL" =~ ^[Yy]$ ]] || { yellow "Aborted by user."; exit 0; }
fi

# ── PHASE 2: Write each node ──────────────────────────────────────────────────

bold "Phase 2: Writing nodes..."

WRITTEN=()
FAILED=()

while IFS= read -r node; do
  FILENAME=$(echo "$node" | jq -r '.filename')
  TYPE=$(echo "$node" | jq -r '.type')
  SUMMARY=$(echo "$node" | jq -r '.summary')
  CONFIDENCE=$(echo "$node" | jq -r '.confidence')
  EDGES=$(echo "$node" | jq -r '.edges[]' 2>/dev/null | sed 's/^/  - /' || echo "")
  DEST="$VAULT_ROOT/$FILENAME"

  # Skip if file already exists (idempotent)
  if [[ -f "$DEST" ]]; then
    yellow "  SKIP (exists): $FILENAME"
    continue
  fi

  mkdir -p "$(dirname "$DEST")"

  NODE_PROMPT="Write a complete knowledge graph node file for the following node.

Node spec:
- filename: $FILENAME
- type: $TYPE
- summary: $SUMMARY
- confidence: $CONFIDENCE
- edges:
$EDGES
- verified_at: $TODAY
- source document: $BASENAME

The source document content (for extracting the node's body):
<document>
$DOC
</document>

Requirements:
1. Start with YAML frontmatter (---) including: node_type, summary, confidence, verified_at, verified_by (agent), visibility (public), edges, tags, created ($TODAY), modified ($TODAY), source_refs
2. Follow with a markdown body — specific, concrete, no vague summaries
3. Body length: 30-150 lines
4. Use [[wikilinks]] for cross-references in the body

Return ONLY the raw file content. No explanation. No markdown fences."

  echo -n "  Writing $FILENAME ... "
  NODE_CONTENT=$(ollama_chat "$MODEL" "$SYSTEM" "$NODE_PROMPT" false)

  # Strip fences
  NODE_CONTENT=$(echo "$NODE_CONTENT" | sed 's/^```[a-z]*//;/^```/d')

  # Must start with ---
  if [[ "$NODE_CONTENT" != ---* ]]; then
    red "WARN: $FILENAME — response didn't start with frontmatter, prepending minimal header"
    NODE_CONTENT="---
node_type: $TYPE
summary: \"$SUMMARY\"
confidence: $CONFIDENCE
verified_at: $TODAY
verified_by: agent
visibility: public
edges: []
created: $TODAY
modified: $TODAY
source_refs: [\"raw/processed/$BASENAME\"]
---

$NODE_CONTENT"
  fi

  printf '%s\n' "$NODE_CONTENT" > "$DEST"
  green "OK"
  WRITTEN+=("$FILENAME")

done < <(echo "$MANIFEST_JSON" | jq -c '.[]')

# ── PHASE 3: Bookkeeping ──────────────────────────────────────────────────────

bold "Phase 3: Updating INDEX and LOG..."

# Append new nodes to INDEX.md
for f in "${WRITTEN[@]}"; do
  TYPE=$(echo "$f" | cut -d/ -f1)
  SLUG=$(basename "$f" .md)
  NODE_SUMMARY=$(grep '^summary:' "$VAULT_ROOT/$f" | head -1 | sed 's/^summary: *"//' | sed 's/"$//')
  NODE_CONF=$(grep '^confidence:' "$VAULT_ROOT/$f" | head -1 | awk '{print $2}')

  # Capitalise type for heading match
  TYPE_HEADING=$(echo "$TYPE" | awk '{print toupper(substr($0,1,1)) substr($0,2) "s"}')

  # Insert under heading if heading exists and node not already there
  if grep -q "^## $TYPE_HEADING" "$VAULT_ROOT/_system/INDEX.md"; then
    if ! grep -q "\[\[$SLUG\]\]" "$VAULT_ROOT/_system/INDEX.md"; then
      sed -i '' "s|^## $TYPE_HEADING\$|## $TYPE_HEADING\n- [[$SLUG]] — $NODE_SUMMARY ($NODE_CONF)|" \
        "$VAULT_ROOT/_system/INDEX.md"
    fi
  fi
done

# Move source file to processed
PROCESSED_DIR="$VAULT_ROOT/raw/processed"
mkdir -p "$PROCESSED_DIR"
mv "$SOURCE_FILE" "$PROCESSED_DIR/$BASENAME"
green "Moved source → raw/processed/$BASENAME"

# Append LOG entry
LOG_ENTRY="## [$TODAY] ingest | $BASENAME (Ollama/$MODEL)
- Mode: $MODE
- Nodes written: ${#WRITTEN[@]} / $NODE_COUNT proposed
- Files: $(IFS=', '; echo "${WRITTEN[*]}")
- Source moved to: raw/processed/$BASENAME"

append_log "$LOG_ENTRY"

# ── Summary ───────────────────────────────────────────────────────────────────

hr
bold "Done."
green "  Nodes written : ${#WRITTEN[@]}"
[[ ${#FAILED[@]} -gt 0 ]] && red "  Nodes failed  : ${#FAILED[@]} — ${FAILED[*]}"
echo "  Source archived: raw/processed/$BASENAME"
hr
