---
id: "<% tp.file.title %>"
title: "<% tp.file.title.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase()) %>"
node_type: "fact"
summary: ""
status: "active"
confidence: 0.9
created_at: "<% tp.date.now('YYYY-MM-DD') %>"
verified_at: "<% tp.date.now('YYYY-MM-DD') %>"
verified_by: "human"
volatility: "stable"
visibility: "public"
data_date: ""
source_url: ""
staleness_signal: ""
derived_from: []
source_refs: []
tags: []
edges:
  - type: "derived_from"
    target: ""
    weight: 0.9
    note: ""
---

# <% tp.file.title.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase()) %>

## Summary
<!-- State the fact precisely in 1-3 sentences. Must be verifiable. -->

## Data
<!-- The specific data point, measurement, or statement. Include units, dates, and context. -->

## Source
<!-- Where this fact comes from. Link to source node if available. -->

## Caveats
<!-- Limitations, conditions, or qualifications on this fact. -->
