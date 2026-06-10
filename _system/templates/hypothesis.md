---
id: "<% tp.file.title %>"
title: "<% tp.file.title.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase()) %>"
node_type: "hypothesis"
summary: ""
status: "active"
confidence: 0.5
created_at: "<% tp.date.now('YYYY-MM-DD') %>"
verified_at: "<% tp.date.now('YYYY-MM-DD') %>"
verified_by: "human"
volatility: "stable"
visibility: "public"
test_condition: ""
prediction: ""
outcome: ""
staleness_signal: ""
derived_from: []
source_refs: []
tags: []
edges:
  - type: "related_to"
    target: ""
    weight: 0.5
    note: ""
---

# <% tp.file.title.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase()) %>

## Summary
<!-- State the hypothesis clearly in 1-3 sentences. -->

## Prediction
<!-- What specific, measurable outcome does this hypothesis predict? -->

## Test Condition
<!-- How can this hypothesis be tested? What evidence would confirm or refute it? -->

## Supporting Evidence
<!-- Current evidence that supports this hypothesis. -->

## Counter-Evidence
<!-- Any evidence that weakens or contradicts this hypothesis. -->

## Outcome
<!-- Leave empty until tested. Record results when available and update status to "resolved". -->
