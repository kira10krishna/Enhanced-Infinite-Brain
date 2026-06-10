#!/bin/bash
# Audit vault health and apply confidence decay
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/vault_health.py" "$@"
