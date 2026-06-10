---
id: "<% tp.file.title %>"
title: "<% tp.file.title.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase()) %>"
node_type: "task"
summary: ""
status: "active"
confidence: 0.8
created_at: "<% tp.date.now('YYYY-MM-DD') %>"
verified_at: "<% tp.date.now('YYYY-MM-DD') %>"
verified_by: "human"
volatility: "stable"
visibility: "private"
assignee: ""
due_date: ""
priority: "medium"
completion: "0%"
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
<!-- What needs to be done? 1-3 sentences. -->

## Details
<!-- Specifics, acceptance criteria, constraints. -->

## Progress
<!-- Track progress updates here. -->

- [ ] Sub-task 1
- [ ] Sub-task 2
- [ ] Sub-task 3
