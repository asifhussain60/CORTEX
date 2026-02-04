# Dashboard Migration Notice

**Status:** MIGRATED to cortex/visualization/dashboards/

This directory has been migrated as part of Phase 21 (JSON-First Architecture rewrite).

## New Locations

| Component | Old Path | New Path |
|-----------|----------|----------|
| Landing Page | company/dashboards/index.html | cortex/visualization/dashboards/spa/index.html |
| Registry | company/dashboards/registry.json | cortex/visualization/dashboards/spa/registry.json |
| SPA Assets | company/dashboards/spa/ | cortex/visualization/dashboards/spa/ |
| Dashboard Data | company/dashboards/repos/ | cortex/visualization/dashboards/data/ |

## Why Migration?

- **Architectural Alignment:** Dashboard visualization now belongs in `cortex/visualization/` module
- **Clean Slate:** Removed SQLite dependencies for JSON-first approach
- **Future Extensibility:** New adapter pattern (JSON → SQLite → PostgreSQL) organized under `cortex/visualization/adapters/`

## References

- Phase 21 Spec: `_workspaces/cortex-plan/PHASE-21-JSON-FIRST-REWRITE.yaml`
- Implementation: `cortex/visualization/dashboards/`
- Data Layer: `cortex/visualization/adapters/`

---

Last Updated: 2026-02-04
