---
id: architecture-package-and-directory-map
title: Package and directory map
purpose: Provide a single diagram that explains where major CORTEX systems live in the repo.
audience:
  - Business Leaders
  - Product Owners
  - Software Developers
source_of_truth:
  - cortex/
  - cortex-registry/
  - tests/
last_verified: 2026-03-01
diagram_type: Architecture
render: ascii
---

# Package & Directory Map

```
Repo roots:
- cortex/          (single canonical package)
- cortex-registry/ (configuration as code)
- tests/           (mirrors cortex/)
- cortex-docs/     (GitHub Pages site)

Key internal packages:
- cortex/orchestrators/   orchestration layer
- cortex/mcp/             MCP stdio server + tools
- cortex/lens/            analysis engine
- cortex/intelligence/    reasoning + learning
- cortex/governance/      rules + enforcement
- cortex/infrastructure/  tracing/metrics/cache/security/etc
```
