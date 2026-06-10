---
id: "<% tp.file.title %>"
title: "<% tp.file.title.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase()) %>"
node_type: "event"
summary: ""
status: "active"
confidence: 0.9
created_at: "<% tp.date.now('YYYY-MM-DD') %>"
verified_at: "<% tp.date.now('YYYY-MM-DD') %>"
verified_by: "human"
volatility: "stable"
visibility: "public"
event_date: "<% tp.date.now('YYYY-MM-DD') %>"
location: ""
participants: []
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
<!-- What happened? 1-3 sentences. -->

## Details
<!-- Full account of the event. Context, participants, outcomes. -->

## Key Takeaways
<!-- What was learned or decided as a result of this event. -->

## Follow-ups
<!-- Actions or questions that arose from this event. -->
