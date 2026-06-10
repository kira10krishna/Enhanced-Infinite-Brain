---
id: "<% tp.file.title %>"
title: "<% tp.file.title.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase()) %>"
node_type: "contact"
summary: ""
status: "active"
confidence: 0.9
created_at: "<% tp.date.now('YYYY-MM-DD') %>"
verified_at: "<% tp.date.now('YYYY-MM-DD') %>"
verified_by: "human"
volatility: "stable"
visibility: "private"
role: ""
organization: ""
relationship: ""
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
<!-- Who is this person/organization? 1-2 sentences. -->

## Role & Context
<!-- Their role, organization, and how you know them. -->

## Expertise
<!-- What domains or topics they're knowledgeable about. -->

## Interactions
<!-- Notable conversations, collaborations, or exchanges. -->
