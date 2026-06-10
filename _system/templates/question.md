---
id: "<% tp.file.title %>"
title: "<% tp.file.title.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase()) %>"
node_type: "question"
summary: ""
status: "active"
confidence: 0.5
created_at: "<% tp.date.now('YYYY-MM-DD') %>"
verified_at: "<% tp.date.now('YYYY-MM-DD') %>"
verified_by: "human"
volatility: "stable"
visibility: "public"
staleness_signal: ""
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
<!-- State the question clearly in 1-2 sentences. -->

## Context
<!-- Why is this question important? What prompted it? -->

## Current Understanding
<!-- What do we know so far? Partial answers, leads, hypotheses. -->

## Research Directions
<!-- Possible approaches to answering this question. -->

## Resolution
<!-- Leave empty until resolved. When answered, link to the answer node and set status to "resolved". -->
