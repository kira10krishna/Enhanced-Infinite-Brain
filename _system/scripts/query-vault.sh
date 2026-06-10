#!/bin/bash
# Query the knowledge graph to retrieve context
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/query_vault.py" "$@"
