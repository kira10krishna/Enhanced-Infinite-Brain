#!/bin/bash
# Audit and interactively organize vault structure
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/organize_vault.py" "$@"
