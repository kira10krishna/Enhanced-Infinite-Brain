---
id: "<% tp.file.title %>"
title: "<% tp.file.title.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase()) %>"
node_type: "bookmark"
summary: ""
status: "active"
confidence: 0.6
created_at: "<% tp.date.now('YYYY-MM-DD') %>"
verified_at: "<% tp.date.now('YYYY-MM-DD') %>"
verified_by: "human"
volatility: "stable"
visibility: "public"
url: ""
date_saved: "<% tp.date.now('YYYY-MM-DD') %>"
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
<!-- Brief annotation of what this link contains and why you saved it. -->

## URL
<!-- The saved link. -->

## Notes
<!-- Quick notes on why this is interesting. Upgrade to a `source` node after deeper processing. -->
