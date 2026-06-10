---
name: vault-health
description: Audit vault health and apply confidence decay to nodes.
---

# Instructions
Run this command to audit the confidence of nodes, apply standard and volatile decay rates, update the contradictions list, and generate the health report.

Usage:
```bash
./_system/scripts/vault-health.sh $ARGUMENTS
```
Add `--auto` to apply decay updates automatically without prompts.
