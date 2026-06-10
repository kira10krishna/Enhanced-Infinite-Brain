---
name: convert-note
description: Convert a raw note or text file into atomic, typed knowledge graph nodes.
---

# Instructions
Run this command to process a raw note from the `raw/` directory or a pasted block of text. This will analyze the note, decompose it into atomic entities, ask for confirmation in supervised mode, and link them to the graph.

Usage:
```bash
./_system/scripts/convert-note.sh <path-to-raw-file-or-text> --mode=<supervised|hybrid|autonomous>
```

Replace `<path-to-raw-file-or-text>` with the path of the file you want to ingest.
Use `$ARGUMENTS` to capture user arguments.
E.g., run:
```bash
./_system/scripts/convert-note.sh $ARGUMENTS
```
