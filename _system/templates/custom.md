---
id: "<% tp.file.title %>"
title: "<% tp.file.title.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase()) %>"
node_type: "custom"
summary: ""
status: "active"
confidence: 0.7
created_at: "<% tp.date.now('YYYY-MM-DD') %>"
verified_at: "<% tp.date.now('YYYY-MM-DD') %>"
verified_by: "human"
volatility: "stable"
visibility: "public"
custom_type: ""
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
<!-- Brief description. -->

## Content
<!-- Body content for this custom-typed node. -->

## Notes
<!-- Additional context. See _system/LOCAL-TYPES.md for custom type definitions. -->
