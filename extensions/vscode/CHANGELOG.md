# CORTEX Extension Changelog

All notable changes to the CORTEX VS Code extension will be documented in this file.

## [4.0.0] - 2026-01-29 (Phase 12 Development)

### Added
- **Extension Scaffold**: Initial VS Code extension structure with TypeScript
- **9 Command Palette Commands**: help, plan, startTdd, systemMaintenance, sanitize, refine, onboard, adoPlanning, showDashboard
- **Output Channel**: Centralized logging for CORTEX operations
- **Configuration Properties**: pythonPath, cortexPath, enableCopilotIntegration, autoRefreshDashboard
- **Welcome Message**: First-time activation notice with quick help access

### Architecture
- **Entry Point**: src/extension.ts with activate/deactivate lifecycle
- **Command Registry**: src/commands/index.ts with 9 command stubs
- **Utilities**: OutputChannelManager singleton for logging
- **Build System**: TypeScript compiler with ES2020 target, CommonJS modules

### In Progress
- Command implementations (Task 12.1.2)
- GitHub Copilot Chat integration (Task 12.1.3)
- CORTEX Dashboard webview (Task 12.1.4)
- Marketplace assets (Task 12.1.5)

### Notes
- Phase 12 (Native IDE Extensions) started December 29, 2025
- Package 12.1 (VS Code Foundation) - 24 hours estimated
- Dual-extension strategy: VS Code (TypeScript) + Visual Studio (C#)
