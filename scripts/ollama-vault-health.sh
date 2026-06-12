#!/usr/bin/env bash
# /vault-health equivalent using a local Ollama model.
# Computes confidence decay, flags stale nodes, writes HEALTH-REPORT.md.
#
# Usage:
#   ./ollama-vault-health.sh
#   ./ollama-vault-health.sh --model qwen3:27b --fix    # auto-update verified_at on reviewed nodes

set -euo pipefail
source "$(dirname "$0")/_lib.sh"

# ── Args ──────────────────────────────────────────────────────────────────────

MODEL="$DEFAULT_MODEL"
FIX_MODE=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --model) MODEL="$2"; shift 2 ;;
    --fix)   FIX_MODE=true; shift ;;
    *)       shift ;;
  esac
done

# ── Preflight ─────────────────────────────────────────────────────────────────

check_deps
check_ollama

TODAY=$(today)
TODAY_EPOCH=$(date -j -f "%Y-%m-%d" "$TODAY" "+%s" 2>/dev/null \
  || date -d "$TODAY" "+%s")  # macOS vs Linux

hr
bold "Infinite Brain — vault-health (Ollama)"
echo "  Model : $MODEL"
echo "  Date  : $TODAY"
hr

# ── Compute decay for all nodes ───────────────────────────────────────────────

bold "Scanning all nodes for confidence decay..."

DECAY_RATE=0.05          # per month
REVIEW_THRESHOLD=0.4

STALE=()
REPORT_LINES=()
TOTAL=0
FLAGGED=0

while IFS= read -r filepath; do
  TOTAL=$((TOTAL + 1))
  RELPATH="${filepath#$VAULT_ROOT/}"

  # Read frontmatter fields
  NODE_TYPE=$(grep '^node_type:' "$filepath" | head -1 | awk '{print $2}')
  STORED_CONF=$(grep '^confidence:' "$filepath" | head -1 | awk '{print $2}')
  VERIFIED_AT=$(grep '^verified_at:' "$filepath" | head -1 | awk '{print $2}')
  SUMMARY=$(grep '^summary:' "$filepath" | head -1 | sed 's/^summary: *"//' | sed 's/"$//')

  # Skip system/exempt types
  [[ "$NODE_TYPE" == "pillar" ]] && continue
  [[ -z "$STORED_CONF" || -z "$VERIFIED_AT" ]] && continue

  # Calculate months since verified_at
  VERIFIED_EPOCH=$(date -j -f "%Y-%m-%d" "$VERIFIED_AT" "+%s" 2>/dev/null \
    || date -d "$VERIFIED_AT" "+%s" 2>/dev/null || echo "")

  if [[ -z "$VERIFIED_EPOCH" ]]; then
    yellow "  SKIP (bad date): $RELPATH"
    continue
  fi

  SECONDS_ELAPSED=$(( TODAY_EPOCH - VERIFIED_EPOCH ))
  MONTHS_ELAPSED=$(echo "scale=2; $SECONDS_ELAPSED / 2592000" | bc)

  # Effective confidence = stored - (decay_rate * months)
  EFF_CONF=$(echo "scale=3; c=$STORED_CONF - ($DECAY_RATE * $MONTHS_ELAPSED); if(c<0) 0 else c" | bc)

  # Flag if below threshold
  BELOW=$(echo "$EFF_CONF < $REVIEW_THRESHOLD" | bc)
  if [[ "$BELOW" == "1" ]]; then
    FLAGGED=$((FLAGGED + 1))
    STALE+=("$RELPATH")
    STATUS="⚠ STALE"
    REPORT_LINES+=("| $RELPATH | $STORED_CONF | $MONTHS_ELAPSED mo | **$EFF_CONF** | $STATUS |")
    yellow "  STALE: $RELPATH (stored $STORED_CONF → effective $EFF_CONF after ${MONTHS_ELAPSED}mo)"
  else
    REPORT_LINES+=("| $RELPATH | $STORED_CONF | $MONTHS_ELAPSED mo | $EFF_CONF | OK |")
  fi

done < <(find "$VAULT_ROOT" \
  -not -path "$VAULT_ROOT/_system/*" \
  -not -path "$VAULT_ROOT/.claude/*" \
  -not -path "$VAULT_ROOT/.obsidian/*" \
  -not -path "$VAULT_ROOT/scripts/*" \
  -not -path "$VAULT_ROOT/raw/*" \
  -name "*.md" 2>/dev/null)

hr
green "Scanned: $TOTAL nodes — $FLAGGED flagged below threshold ($REVIEW_THRESHOLD)"

# ── AI review of stale nodes ──────────────────────────────────────────────────

STALE_REVIEW=""
if [[ ${#STALE[@]} -gt 0 && -n "$MODEL" ]]; then
  bold "Running AI review on ${#STALE[@]} stale nodes..."

  STALE_CONTENTS=""
  for f in "${STALE[@]}"; do
    STALE_CONTENTS+="### $f"$'\n'
    STALE_CONTENTS+="$(cat "$VAULT_ROOT/$f")"$'\n\n---\n\n'
  done

  REVIEW_PROMPT="The following knowledge graph nodes have dropped below the confidence review threshold (0.4) due to time decay. For each node, assess:
1. Is the core claim still likely accurate?
2. What would need to be re-verified to restore confidence?
3. Recommended action: RETAIN / UPDATE / ARCHIVE

Nodes to review:
<nodes>
$STALE_CONTENTS
</nodes>

Format your response as a brief assessment per node: filename, verdict, reasoning (2-3 sentences max per node)."

  STALE_REVIEW=$(ollama_chat "$MODEL" "$(system_context)" "$REVIEW_PROMPT" false)
fi

# ── Write HEALTH-REPORT.md ────────────────────────────────────────────────────

REPORT_FILE="$VAULT_ROOT/_system/HEALTH-REPORT.md"

cat > "$REPORT_FILE" <<EOF
---
node_type: reference
summary: "Vault health report — confidence decay audit run $TODAY"
confidence: 1.0
verified_at: $TODAY
verified_by: agent
visibility: system
edges: []
tags: [health, system]
created: $TODAY
modified: $TODAY
---

# Vault Health Report — $TODAY

**Model:** $MODEL
**Decay rate:** ${DECAY_RATE}/month
**Review threshold:** $REVIEW_THRESHOLD
**Nodes scanned:** $TOTAL
**Nodes flagged:** $FLAGGED

---

## Confidence Decay Table

| Node | Stored | Age | Effective | Status |
|------|--------|-----|-----------|--------|
$(printf '%s\n' "${REPORT_LINES[@]}")

---

## AI Review of Stale Nodes

${STALE_REVIEW:-_No stale nodes or review skipped._}

---

## Recommended Actions

$(if [[ $FLAGGED -gt 0 ]]; then
  echo "The following nodes need review:"
  for f in "${STALE[@]}"; do echo "- $f"; done
else
  echo "_All nodes are above the confidence threshold. No action required._"
fi)
EOF

green "Health report written: _system/HEALTH-REPORT.md"

# ── Log ───────────────────────────────────────────────────────────────────────

append_log "## [$TODAY] vault-health | Ollama/$MODEL
- Nodes scanned: $TOTAL
- Nodes flagged (< $REVIEW_THRESHOLD): $FLAGGED
- Stale nodes: $(IFS=', '; echo "${STALE[*]:-none}")
- Report: _system/HEALTH-REPORT.md"

hr
bold "Done. Report at _system/HEALTH-REPORT.md"
hr
