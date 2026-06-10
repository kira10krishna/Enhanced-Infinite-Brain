---
id: "<% tp.file.title %>"
title: "<% tp.file.title.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase()) %>"
node_type: "playbook"
summary: ""
status: "active"
confidence: 0.9
created_at: "<% tp.date.now('YYYY-MM-DD') %>"
verified_at: "<% tp.date.now('YYYY-MM-DD') %>"
verified_by: "human"
volatility: "stable"
visibility: "public"
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
<!-- 1-3 sentence description of what this playbook accomplishes. -->

## Trigger
<!-- When should this playbook be executed? What conditions activate it? -->

## Prerequisites
<!-- What must be true before starting? Dependencies, tools, permissions. -->

## Steps

1. **Step 1**: 
2. **Step 2**: 
3. **Step 3**: 

## Expected Outcome
<!-- What does success look like? How to verify the playbook worked. -->

## Failure Modes
<!-- What can go wrong and how to recover. -->
