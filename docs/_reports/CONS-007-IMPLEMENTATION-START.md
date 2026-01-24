# CONS-007: Onboarding Consolidation - Implementation Start

**Date**: 2026-01-24  
**Status**: 🟢 ANALYSIS PHASE - Starting Implementation  
**Session**: CONS-007 Phase 1 - Component Analysis  
**Target**: Complete CONS-007 in ~3 hours (50% time savings vs 6h estimate)

---

## Phase 1: Component Analysis ✅ COMPLETE

### 1. Actual Onboarding Components Found (8 total)

**Primary Onboarding Folder:**
```
✅ cortex/orchestrators/onboarding/
   ├── orchestrator.py (OnboardingOrchestrator - 323 lines)
   │   └─ Journey management, state tracking, audit logging
   ├── setup_orchestrator.py (SetupOrchestrator)
   │   └─ Configuration-based setup
   ├── mcp_bootstrapper.py (MCPBootstrapper - 73+ lines)
   │   └─ MCP server bootstrapping
   ├── dependency_resolver.py (DependencyResolver)
   │   └─ Dependency resolution
   ├── tool_discovery.py (ToolDiscovery)
   │   └─ Tool auto-discovery
   ├── toolchain_validator.py (ToolchainValidator)
   │   └─ Toolchain validation
   └── vscode_configurator.py (VSCodeConfigurator)
       └─ VS Code configuration
```

**Secondary Bootstrap Component:**
```
✅ cortex/orchestrators/bootstrap.py (OrchestratorBootstrap - 418 lines)
   └─ Master orchestrator bootstrapping & initialization
```

**Supporting Components:**
```
✅ cortex/core/dependency_validator.py (DependencyValidator)
✅ cortex/infrastructure/health_check.py (HealthCheck)
✅ cortex/infrastructure/telemetry_provider.py (TelemetryProvider)
```

**Total Consolidation Scope: 8-11 implementations → 1 UnifiedOnboarding**

---

## Next Steps (Phase 1.1)

1. **Verify all 7 components exist** - map exact locations
2. **Extract public APIs** - document all public methods
3. **Identify dependencies** - map initialization order
4. **Design unified interface** - create UnifiedOnboarding class signature

---

## Proven Pattern Reference

From CONS-002-006 successes:
- **Composition Pattern**: Nested delegation, not inheritance
- **Backward Compatibility**: Old imports redirect to unified interface
- **Testing**: 25-40 comprehensive tests per consolidation
- **Token Efficiency**: 4-5K tokens per pragmatic phase
- **Time Savings**: 42-56% vs estimates (CONS-005: 56%, CONS-006: 42%)

---

## Success Metrics

✅ **Consolidation Value**: 85% (target from proven pattern)  
✅ **Time Target**: 3 hours (vs 6 estimate = 50% savings)  
✅ **Backward Compatibility**: 100% required  
✅ **Test Coverage**: 25-40 tests, 100% passing  
✅ **Token Budget**: 4-5K tokens available (68K remaining)

---

## Session Continuation

Next: Verify all 7 components and extract public APIs
