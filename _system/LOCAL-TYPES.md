---
node_type: reference
summary: "Registry of workspace-specific custom node types that extend the 16 standard types. Empty until a real need arises."
confidence: 1.0
verified_at: 2026-06-12
verified_by: human
visibility: system
edges:
  - target: "[[SCHEMA]]"
    type: part_of
    weight: 0.8
    note: "Extends the type system defined in SCHEMA"
tags: [system, types, custom]
created: 2026-06-12
modified: 2026-06-12
---

# LOCAL-TYPES — Custom Node Types

Any node with `node_type: custom` **must** be registered here so the agent knows how to handle it. Don't invent a custom type until one of the 16 standard types genuinely fails to fit — most knowledge maps onto the standard set.

To add a custom type, append a section using this template:

```markdown
## `<type-name>`
- **Folder:** `custom/` (or a dedicated folder if heavily used)
- **Use when:** <the gap in the 16 standard types this fills>
- **Distinct from:** <the closest standard type and why this differs>
- **Required extra fields:** <any frontmatter beyond the standard set>
- **Default confidence:** <value>
```

---

_No custom types defined yet._
