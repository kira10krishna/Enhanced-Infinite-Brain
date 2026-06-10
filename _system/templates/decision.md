---
id: "<% tp.file.title %>"
title: "<% tp.file.title.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase()) %>"
node_type: "decision"
summary: ""
status: "active"
confidence: 0.9
created_at: "<% tp.date.now('YYYY-MM-DD') %>"
verified_at: "<% tp.date.now('YYYY-MM-DD') %>"
verified_by: "human"
volatility: "stable"
visibility: "public"
decision_date: "<% tp.date.now('YYYY-MM-DD') %>"
alternatives: []
rationale: ""
derived_from: []
tags: []
edges:
  - type: "related_to"
    target: ""
    weight: 0.5
    note: ""
---

# <% tp.file.title.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase()) %>

## Summary
<!-- 1-3 sentence summary of the decision. -->

## Context
<!-- What situation or problem prompted this decision? -->

## Alternatives Considered
<!-- List each alternative with pros/cons. -->

### Option A
- **Pros**:
- **Cons**:

### Option B
- **Pros**:
- **Cons**:

## Decision
<!-- Which option was chosen and why. -->

## Consequences
<!-- Expected outcomes, tradeoffs, and risks of this decision. -->
