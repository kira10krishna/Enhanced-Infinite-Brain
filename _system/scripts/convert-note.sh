#!/bin/bash
# Ingest and convert a raw note into knowledge graph nodes
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/convert_note.py" "$@"
