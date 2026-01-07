---
title: Security & Performance
---

Security is enforced via governance + audit:

- Audit logging wraps orchestrator operations at runtime (not a “nice to have” hook).
- Repo isolation ensures CORTEX core never commits to user repos.

Performance goals:

- **Trie routing** targets O(1) matching for many orchestrators.
- Governance merge and state persistence are kept low-latency to support interactive use.
