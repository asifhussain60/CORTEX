---
title: Repository Structure (Conceptual)
---

CORTEX has a **core “brain”** plus **repo‑local configuration**:

- `cortex-brain/`
  - `tier0/` core governance (immutable)
  - `tier1/` working memory (active instruction set)
  - `tier2/` knowledge graph (learned patterns)
- `{repo}/.cortex/`
  - `governance/business-tier0.yaml` (business / compliance)
  - `best-practices/` (company engineering standards)

This split enables multi‑repo support while enforcing strict company isolation.
