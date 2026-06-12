#!/usr/bin/env bash
# Shared helpers for all Infinite Brain Ollama scripts.
# Source this file: source "$(dirname "$0")/_lib.sh"

OLLAMA_URL="${OLLAMA_URL:-http://localhost:11434}"
VAULT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEFAULT_MODEL="${BRAIN_MODEL:-qwen3:27b}"

# ── Preflight ────────────────────────────────────────────────────────────────

check_deps() {
  for cmd in curl jq; do
    command -v "$cmd" &>/dev/null || { echo "ERROR: '$cmd' not found. Install it and retry."; exit 1; }
  done
}

check_ollama() {
  curl -s --max-time 3 "$OLLAMA_URL/api/tags" &>/dev/null \
    || { echo "ERROR: Ollama not running. Start it with: ollama serve"; exit 1; }
}

check_model() {
  local model="$1"
  curl -s "$OLLAMA_URL/api/tags" \
    | jq -e --arg m "$model" '.models[] | select(.name == $m or (.name | startswith($m)))' &>/dev/null \
    || { echo "WARNING: model '$model' not found locally. Pull it with: ollama pull $model"; }
}

# ── API call ─────────────────────────────────────────────────────────────────

# ollama_chat <model> <system_prompt> <user_message> [think=true|false]
# Prints the assistant's reply to stdout. Thinking blocks are stripped (returned separately in $LAST_THINKING).
ollama_chat() {
  local model="$1" system="$2" user="$3" think="${4:-true}"

  local payload
  payload=$(jq -n \
    --arg model  "$model" \
    --arg system "$system" \
    --arg user   "$user" \
    --argjson think "$think" \
    '{
      model:    $model,
      stream:   false,
      think:    $think,
      messages: [
        {role: "system", content: $system},
        {role: "user",   content: $user}
      ]
    }')

  local response
  response=$(curl -s --max-time 300 \
    -H "Content-Type: application/json" \
    -d "$payload" \
    "$OLLAMA_URL/api/chat")

  if [[ -z "$response" ]]; then
    echo "ERROR: No response from Ollama (timeout or connection refused)." >&2
    return 1
  fi

  local err
  err=$(echo "$response" | jq -r '.error // empty')
  if [[ -n "$err" ]]; then
    echo "ERROR from Ollama: $err" >&2
    return 1
  fi

  # Qwen3: thinking is in message.thinking, final answer in message.content
  LAST_THINKING=$(echo "$response" | jq -r '.message.thinking // empty')
  echo "$response" | jq -r '.message.content'
}

# ── Vault helpers ─────────────────────────────────────────────────────────────

load_schema() {
  cat "$VAULT_ROOT/_system/SCHEMA.md"
}

load_agents() {
  cat "$VAULT_ROOT/_system/AGENTS.md"
}

load_index() {
  cat "$VAULT_ROOT/_system/INDEX.md"
}

# Build the standard system context used by all operations
system_context() {
  printf '%s\n\n---\n\n%s' "$(load_agents)" "$(load_schema)"
}

append_log() {
  local entry="$1"
  printf '\n%s\n' "$entry" >> "$VAULT_ROOT/_system/LOG.md"
}

today() {
  date +%Y-%m-%d
}

# ── Output helpers ────────────────────────────────────────────────────────────

hr()      { printf '%s\n' "────────────────────────────────────────"; }
bold()    { printf '\033[1m%s\033[0m\n' "$*"; }
green()   { printf '\033[32m%s\033[0m\n' "$*"; }
yellow()  { printf '\033[33m%s\033[0m\n' "$*"; }
red()     { printf '\033[31m%s\033[0m\n' "$*"; }
