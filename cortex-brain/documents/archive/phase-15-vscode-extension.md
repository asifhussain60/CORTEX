# Phase 15: VS Code Extension Development

**Version:** 1.0 | **Status:** 📋 PLANNED | **Priority:** HIGH (POST-GA Enhancement)  
**Owner:** Asif Hussain | **Created:** December 23, 2025 | **Estimated Duration:** 8-10 weeks

---

## 🎯 Phase Overview

**Objective:** Package CORTEX as a VS Code extension for universal deployment across all user repositories without per-repo configuration.

**Current State:** CORTEX operates through GitHub Copilot using prompt files that users must manually reference in each repository.

**Target State:** One-click installation from VS Code Marketplace, automatic loading in ALL workspaces, centralized updates.

**Business Value:**
- **User Adoption:** 10x easier onboarding (one-click vs git clone + manual setup)
- **Distribution:** Professional channel (VS Code Marketplace = 40M+ developers)
- **Updates:** Automatic delivery via Marketplace (no manual git pull)
- **Reach:** Works across ALL repos instantly (no per-repo configuration)
- **Monetization:** Enables freemium model (free tier + premium features)

---

## 📋 Phase Structure

### Sub-Phase 15.1: Core Extension Framework (3 weeks)

**Tasks:**
- 15.1.1: Extension project setup (package.json, tsconfig, build system)
- 15.1.2: VS Code extension activation and lifecycle management
- 15.1.3: GitHub Copilot Chat participant registration
- 15.1.4: Embedded brain system (4-tier architecture in extension storage)
- 15.1.5: Context detection (CORTEX repo vs user repos, admin mode)
- 15.1.6: Command palette integration (cortex.help, cortex.plan, etc.)
- 15.1.7: Settings UI (VS Code native configuration)

**Deliverables:**
- Extension manifest with activation events
- TypeScript entry point with activation/deactivation
- Copilot Chat participant (@cortex)
- Embedded cortex-brain/ in extension bundle
- Context-aware operation filtering
- 8+ command palette entries
- Settings UI for brain path, admin mode

**Acceptance Criteria:**
- ✅ Extension activates on VS Code startup
- ✅ @cortex available in Copilot Chat
- ✅ Commands appear in Command Palette
- ✅ Context detection works (admin vs user mode)
- ✅ Settings persisted across sessions

### Sub-Phase 15.2: Orchestrator Integration (4 weeks)

**Tasks:**
- 15.2.1: Python environment detection (leverage Python extension API)
- 15.2.2: Bundle Python orchestrators in extension package
- 15.2.3: Planning System integration (via Python subprocess)
- 15.2.4: TDD Orchestrator integration
- 15.2.5: Code Sanitization Orchestrator integration
- 15.2.6: System Maintenance/Refinement integration
- 15.2.7: ADO Operations integration
- 15.2.8: Error handling and fallback mechanisms

**Deliverables:**
- Python environment resolver (uses VS Code Python API)
- Bundled Python orchestrators (src/ directory)
- TypeScript→Python bridge (subprocess communication)
- All 16 orchestrators callable from extension
- Streaming output for long-running operations
- Graceful degradation if Python unavailable

**Acceptance Criteria:**
- ✅ Extension detects Python environment
- ✅ All orchestrators execute from Copilot Chat
- ✅ Real-time progress updates visible
- ✅ Errors surface to user with actionable messages
- ✅ Works with Python 3.9+ (all versions)

### Sub-Phase 15.3: Advanced Features (2 weeks)

**Tasks:**
- 15.3.1: Multi-workspace support (handle multiple folders)
- 15.3.2: Workspace-specific brain storage (segmentation)
- 15.3.3: Telemetry system (opt-in usage analytics)
- 15.3.4: Error reporting (crash logs, diagnostics)
- 15.3.5: Performance optimization (lazy loading, caching)
- 15.3.6: Extension API for third-party integrations

**Deliverables:**
- Multi-root workspace handler
- Isolated brain storage per workspace
- Telemetry dashboard (anonymized metrics)
- Sentry/AppInsights error reporting
- <200ms activation time
- Public extension API

**Acceptance Criteria:**
- ✅ Works with multi-root workspaces
- ✅ Brain data isolated by workspace
- ✅ Telemetry opt-in during first run
- ✅ Errors auto-reported (with consent)
- ✅ Fast activation (<200ms)
- ✅ Third-party extensions can call CORTEX

### Sub-Phase 15.4: Testing & Quality (2 weeks)

**Tasks:**
- 15.4.1: Unit tests (VS Code extension test framework)
- 15.4.2: Integration tests (orchestrator invocation)
- 15.4.3: E2E tests (Copilot Chat scenarios)
- 15.4.4: Cross-platform validation (Windows/macOS/Linux)
- 15.4.5: Performance benchmarking
- 15.4.6: Security audit (extension permissions, data handling)

**Deliverables:**
- 90%+ test coverage
- CI/CD pipeline (GitHub Actions)
- Cross-platform test matrix
- Performance baselines
- Security review report

**Acceptance Criteria:**
- ✅ All tests pass on 3 platforms
- ✅ No security vulnerabilities (npm audit clean)
- ✅ <200ms activation, <50ms command response
- ✅ Passes VS Code extension security review

### Sub-Phase 15.5: Marketplace Publishing (1 week)

**Tasks:**
- 15.5.1: Publisher account setup (Azure DevOps)
- 15.5.2: Extension branding (icon, screenshots, videos)
- 15.5.3: README and documentation
- 15.5.4: Marketplace listing optimization (SEO)
- 15.5.5: Initial VSIX package generation
- 15.5.6: Publish to VS Code Marketplace
- 15.5.7: Post-launch monitoring

**Deliverables:**
- Azure DevOps publisher account
- High-quality icon (256x256)
- 3+ screenshots, 1 demo video
- Comprehensive README
- Published extension (v1.0.0)
- Launch announcement

**Acceptance Criteria:**
- ✅ Extension live on Marketplace
- ✅ Search ranking top 5 for "AI assistant"
- ✅ Zero critical bugs in first 48 hours
- ✅ 100+ installs in first week

---

## 🔧 Technical Architecture

### Extension Structure
```
cortex-extension/
├── package.json              # Extension manifest
├── tsconfig.json             # TypeScript config
├── src/
│   ├── extension.ts          # Entry point
│   ├── brain/
│   │   └── cortex-brain.ts   # Brain wrapper
│   ├── integrations/
│   │   └── copilot.ts        # Copilot Chat participant
│   ├── orchestrators/
│   │   └── python-bridge.ts  # Python subprocess manager
│   └── commands/
│       └── command-registry.ts
├── brain/                    # Embedded cortex-brain/
│   ├── tier0/
│   ├── tier1/
│   ├── tier2/
│   ├── tier3/
│   └── response-templates-v4.yaml
├── python/                   # Bundled orchestrators
│   └── src/                  # Full CORTEX src/
├── test/
│   ├── unit/
│   ├── integration/
│   └── e2e/
└── assets/
    ├── icon.png
    └── screenshots/
```

### Key Components

**1. Extension Activation**
```typescript
export function activate(context: vscode.ExtensionContext) {
  const brain = new CortexBrain(context.globalStorageUri.fsPath);
  const copilot = new GitHubCopilotIntegration(brain);
  
  copilot.register(context);
  registerCommands(context, brain);
  detectWorkspaceContext(context, brain);
}
```

**2. Copilot Chat Participant**
```typescript
vscode.chat.createChatParticipant('cortex', async (request, context, stream) => {
  const workspace = context.workspaceFolder;
  const isAdmin = await brain.detectCortexRepo(workspace);
  const operations = brain.getOperations(isAdmin);
  
  const response = await routeRequest(request.prompt, workspace, operations);
  stream.markdown(response);
});
```

**3. Python Bridge**
```typescript
class PythonBridge {
  async executePlanningOrchestrator(feature: string): Promise<string> {
    const pythonPath = await this.getPythonPath();
    const script = path.join(extensionPath, 'python/src/orchestrators/planning_orchestrator.py');
    
    return execAsync(`${pythonPath} ${script} --feature "${feature}"`);
  }
}
```

### Storage Layout

**Extension Storage (Read-Only):**
```
~/.vscode/extensions/asifhussain.cortex-4.0.0/
├── brain/ (embedded, immutable)
└── python/ (embedded, immutable)
```

**User Data (Read-Write):**
```
~/.cortex/
├── conversation-history.db
├── knowledge-graph.yaml
└── workspaces/
    ├── project-a/
    └── project-b/
```

---

## 📊 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Marketplace Installs | 1,000+ in month 1 | VS Code Marketplace analytics |
| User Activation Rate | 70%+ | Telemetry (first command invoked) |
| Retention (30-day) | 50%+ | Telemetry (active users) |
| Command Invocations | 10+ per user/week | Telemetry (usage frequency) |
| Extension Rating | 4.5+ stars | Marketplace reviews |
| Search Ranking | Top 5 for "AI assistant" | Marketplace search |
| Error Rate | <1% of invocations | Error reporting system |
| Performance | <200ms activation | Performance telemetry |

---

## 🚧 Dependencies

**Required Before Start:**
- ✅ Phase 14 complete (version consolidation)
- ✅ Phase 7B complete (architectural implementation)
- ✅ Phase 8 complete (testing & validation)
- ✅ Phase 9 complete (documentation finalization)

**Blockers:**
- None (post-GA enhancement, can start after core phases)

**External Dependencies:**
- VS Code Extension API (stable)
- GitHub Copilot Chat API (stable)
- VS Code Python Extension API (stable)
- Azure DevOps (publisher account)

---

## 🎯 Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Copilot API changes | HIGH | LOW | Version locking, deprecation monitoring |
| Python bundling complexity | MEDIUM | MEDIUM | Use PyInstaller/Nuitka for standalone executable |
| Cross-platform issues | MEDIUM | MEDIUM | Extensive testing matrix, CI/CD validation |
| Marketplace rejection | HIGH | LOW | Pre-submission security audit, compliance review |
| Performance degradation | MEDIUM | LOW | Lazy loading, background processing, caching |
| User privacy concerns | HIGH | LOW | Opt-in telemetry, clear privacy policy, no PII collection |

---

## 📝 Migration Path

**Phase 1: Parallel Operation (Month 1-2)**
- Extension available alongside git clone method
- Users choose preferred installation method
- Monitor adoption rates

**Phase 2: Promotion (Month 3-4)**
- Update documentation to recommend extension
- Git clone method still documented as alternative
- Gather user feedback

**Phase 3: Primary Distribution (Month 5+)**
- Extension becomes recommended installation
- Git clone method for contributors/advanced users
- Legacy support maintained

**No Breaking Changes:**
- Git clone method remains supported indefinitely
- Extension provides same functionality + improvements
- Users can switch between methods

---

## 🔄 Post-Launch Roadmap

**v1.1 (Month 2):**
- User feedback incorporation
- Performance optimizations
- Bug fixes

**v1.5 (Month 4):**
- Premium tier features (if applicable)
- Enhanced telemetry dashboard
- Third-party extension integrations

**v2.0 (Month 6):**
- Standalone desktop app (Electron)
- Offline mode support
- Advanced AI features

---

## 📚 Resources

**Documentation:**
- [VS Code Extension API](https://code.visualstudio.com/api)
- [GitHub Copilot Chat API](https://code.visualstudio.com/api/extension-guides/chat)
- [VS Code Extension Guidelines](https://code.visualstudio.com/api/references/extension-guidelines)
- [Publishing Extensions](https://code.visualstudio.com/api/working-with-extensions/publishing-extension)

**Examples:**
- [GitHub Copilot Extension](https://github.com/features/copilot)
- [Python Extension](https://github.com/microsoft/vscode-python)
- [Extension Samples](https://github.com/microsoft/vscode-extension-samples)

**Tools:**
- [VSCE (Extension CLI)](https://github.com/microsoft/vscode-vsce)
- [Yeoman Generator](https://github.com/microsoft/vscode-generator-code)
- [Extension Test Runner](https://github.com/microsoft/vscode-test)

---

**Next Steps:**
1. Review and approve phase plan
2. Update CORTEX4-STATUS.md with Phase 15 entry
3. Wait for Phases 14, 7B, 8, 9 completion (prerequisites)
4. Begin Sub-Phase 15.1 (Core Extension Framework)

**Estimated Start Date:** Q2 2026 (after Phase 9 complete)  
**Estimated Completion:** Q3 2026 (8-10 weeks from start)
