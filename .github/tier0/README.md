# Local Governance Stub

This directory contains local governance references for the CORTEX deployment system.

## Structure
- This is a **stub** - actual governance rules are in the central hub
- Local rules can override hub defaults (if governance mode permits)
- All changes are audited through the MCP hub

## Hub Reference
See `cortex-config.yaml` in the repository root for hub endpoint and configuration.

## Governance Modes
- **strict**: Hub rules are mandatory, no local overrides (default)
- **moderate**: Hub rules + local supplements allowed
- **permissive**: Hub recommendations only

## Getting Started
1. Connect to hub via cortex-config.yaml
2. Review hub governance rules
3. Request local rule changes via hub governance flow

Generated: 2026-01-19T16:43:32Z
