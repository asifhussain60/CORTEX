---
title: Testing Strategy
---

CORTEX uses a single top-level `tests/` folder with:

- unit tests (including orchestrators)
- integration tests (end-to-end, multi-repo)
- governance tests (merge algorithm correctness)
- performance tests (routing latency, DAG operations)

This keeps test discovery and coverage visibility simple.
