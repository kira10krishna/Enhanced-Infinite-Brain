---
id: "<% tp.file.title %>"
title: "<% tp.file.title.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase()) %>"
node_type: "pattern"
summary: ""
status: "active"
confidence: 0.7
created_at: "<% tp.date.now('YYYY-MM-DD') %>"
verified_at: "<% tp.date.now('YYYY-MM-DD') %>"
verified_by: "human"
volatility: "stable"
visibility: "public"
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
<!-- Describe the pattern in 1-3 sentences. -->

## Observation
<!-- Where and how was this pattern observed? What data supports it? -->

## Mechanism
<!-- Why does this pattern occur? Hypothesized or known causal mechanism. -->

## When It Applies
<!-- Conditions under which the pattern holds. Scope and boundaries. -->

## When It Breaks
<!-- Known exceptions, edge cases, or conditions that invalidate the pattern. -->

## Examples
<!-- 2-3 concrete instances of this pattern in action. -->
