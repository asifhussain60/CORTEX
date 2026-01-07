---
title: Data Model & Brain Tiers
---

CORTEX persists durable state and uses a tiered “brain”:

- **Tier 0**: immutable core governance
- **Tier 1**: working memory (active instruction set, execution context)
- **Tier 2**: knowledge graph (learned patterns, lessons learned)
- (Optionally) **Tier 3**: development context

Execution state and artifacts live in SQLite (WAL mode) to support concurrency and reliability.
