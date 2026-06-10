---
name: query-vault
description: Query the knowledge graph to retrieve context for answering questions.
---

# Instructions
Run this command to search the knowledge graph using keyword extraction and edge-traversal, retrieving context and auto-injecting pillars.

Usage:
```bash
./_system/scripts/query-vault.sh "$ARGUMENTS"
```
Once the context is printed, synthesize the final response referencing the retrieved nodes and tracing citations.
