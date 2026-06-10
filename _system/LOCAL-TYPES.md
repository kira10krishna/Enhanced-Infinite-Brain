# Local Types (LOCAL-TYPES.md)

Define custom node types specific to this vault that don't fit the standard 16 types.

> Custom types are stored in the `custom/` folder. Register them here so agents know how to handle them.

---

## How to Define a Custom Type

Add an entry below using this format:

```markdown
### type-name

- **Description**: What this type represents.
- **When to use**: Criteria for when a node should be this type instead of a standard type.
- **Decay tier**: Base (-0.04/mo) | Fast (-0.08/mo) | Exempt
- **Required extra frontmatter fields**: Any additional YAML fields beyond the standard schema.
- **Body structure**: Expected section headings in the node body.
```

---

## Registered Custom Types

_No custom types defined yet._
