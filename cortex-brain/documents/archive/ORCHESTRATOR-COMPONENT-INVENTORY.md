# CORTEX Orchestrator Component Inventory
**Executive Summary - Quick Reference Guide**

**Author:** Asif Hussain  
**Date:** December 19, 2024  
**Version:** 1.0  
**Purpose:** Alphabetical inventory of all Entry Point Module (EPM) orchestrators and their plugged components

---

## Overview

CORTEX uses an **Entry Point Module Orchestrator (EPMO)** architecture where specialized orchestrators coordinate modular components to accomplish complex operations. This document provides a quick reference for understanding which components are integrated into each orchestrator.

**Total Orchestrators Documented:** 10  
**Architecture Pattern:** BaseOperationModule inheritance with phase-based execution  
**Coordination Method:** Dependency resolution, topological sorting, parallel execution where applicable

---

## Alphabetical Orchestrator Inventory

### 1. Cleanup Orchestrator
**Location:** `src/operations/modules/cleanup/cleanup_orchestrator.py`  
**Purpose:** Comprehensive workspace cleanup with backup management, file reorganization, MD consolidation  
**Lines:** 76 (class) / 1,161 (total)

**Plugged Components:**
- `RemoveObsoleteTestsModule` - Removes deprecated test files
- `CleanupMetrics` (dataclass) - Tracks cleanup statistics
- `operation_header_formatter` - UI formatting (print_minimalist_header, print_completion_footer)
- `BaseOperationModule` - Core operation abstraction

**Key Features:**
- Protected paths enforcement (cortex-brain/, .git/, etc.)
- File organization rules (backups/, logs/, temp/)
- Backup pattern management
- MD file consolidation
- Bloat detection thresholds

---

### 2. Design Sync Orchestrator
**Location:** `src/operations/modules/design_sync/design_sync_orchestrator.py`  
**Purpose:** Resolves design-implementation drift through 6-phase workflow  
**Lines:** 102 (class) / 1,489 (total)

**Plugged Components:**
- `TrackConfigManager` - Multi-track configuration management
- `TrackDocumentTemplates` - Template system for track documents
- `MultiTrackConfig` (dataclass) - Multi-track configuration data
- `MachineTrack` (dataclass) - Machine-specific track definition
- `TrackMetrics` (dataclass) - Performance metrics
- `ImplementationState` (dataclass) - Current implementation state
- `DesignState` (dataclass) - Design document state
- `GapAnalysis` (dataclass) - Design-implementation gap analysis
- `SyncMetrics` (dataclass) - Synchronization metrics
- `BaseOperationModule` - Core operation abstraction
- `OperationHeaderFormatter` - UI formatting utilities

**Phases:**
1. Discovery (module/test/plugin detection)
2. Design Document Scan
3. Gap Analysis
4. Optimization Integration (runs optimize_cortex_orchestrator)
5. Document Transformation (MD → YAML)
6. Git Commit (automatic commit with audit trail)

---

### 3. Diagram Regeneration Orchestrator
**Location:** `src/operations/modules/diagrams/diagram_regeneration_orchestrator.py`  
**Purpose:** Comprehensive design analysis and visual asset generation (Mermaid diagrams, illustration prompts)  
**Lines:** 923 (total)

**Plugged Components:**
- `CortexDesignAnalyzer` - Analyzes CORTEX architecture
- `CortexFeature` (dataclass) - Feature metadata
- `DiagramSpec` (dataclass) - Diagram specifications
- `BaseOperationModule` - Core operation abstraction
- YAML configuration (`cortex-brain/diagram-definitions.yaml`)

**Analysis Targets:**
- 5-tier memory architecture (Tier 0-3 + Tier 4 real-time)
- Dual-hemisphere agent system
- TDD enforcement workflow
- Conversation tracking mechanisms
- Knowledge graph relationships
- Token optimization system

---

### 4. Enterprise Documentation Orchestrator
**Location:** `src/operations/enterprise_documentation_orchestrator.py`  
**Purpose:** Natural language interface for comprehensive documentation generation  
**Lines:** 552 (total)

**Plugged Components:**
- `DocumentationGenerator` (from `src.epm.doc_generator`) - Core EPM documentation engine
- `create_default_registry` - Documentation component registry factory
- `StoryGeneratorPlugin` - Story narrative generation
- `BaseOperationModule` - Core operation abstraction (OperationResult, OperationStatus)

**Profiles:**
- `quick` - Fast documentation scan
- `standard` - Normal documentation generation
- `comprehensive` - Full documentation pipeline

**Execution Modes:**
- Full 6-stage pipeline
- Single stage execution
- Component registry execution (new architecture)
- Story generation plugin integration

**Stage/Component Mapping:**
- `diagrams` → ["diagrams"]
- `mkdocs` → ["mkdocs"]
- `feature-list` → ["feature_list"]
- `all` → ["diagrams", "feature_list", "mkdocs"]

---

### 5. Feature Completion Orchestrator (FCO)
**Location:** `src/agents/feature_completion_orchestrator.py`  
**Purpose:** Coordinates comprehensive documentation and system alignment when features are marked complete  
**Lines:** 733 (total)

**Plugged Components:**
- `BaseAgent` - Agent system abstraction
- `KnowledgeGraph` (Tier 2) - Pattern storage and retrieval
- `ContextIntelligence` (Tier 3) - Context analytics
- `EntityExtractor` - Entity extraction utilities
- `MetricsCollector` - Performance metrics

**Dataclasses:**
- `Entity` - Extracted entities (files, classes, functions, concepts)
- `Pattern` - Learned patterns from knowledge graph
- `ContextUpdate` - Context intelligence updates
- `ImplementationScan` - Current implementation state
- `BrainData` - Consolidated brain storage
- `CodeChange` - Code modification tracking
- `APIChange` - API endpoint changes
- `TestAnalysis` - Test coverage analysis
- `GitAnalysis` - Git commit analysis
- `ImplementationData` - Discovered implementation details
- `DocumentationGap` - Documentation inconsistencies
- `ContentUpdate` - Generated content updates

**Architecture:**
- Async pipeline with parallel processing
- 5 specialized sub-agents coordination
- Integration with CORTEX brain tiers
- Natural language trigger support

---

### 6. Operations Orchestrator (Universal)
**Location:** `src/operations/operations_orchestrator.py`  
**Purpose:** Universal orchestrator for ALL CORTEX operations (setup, cleanup, story refresh, docs, etc.)  
**Lines:** 665 (total)

**Plugged Components:**
- `BaseOperationModule` - Core operation abstraction (OperationPhase, OperationStatus, OperationResult, ExecutionMode)
- `learning_capture_agent` - Captures operation learnings (capture_operation_learning)
- `ThreadPoolExecutor` - Parallel execution engine

**Dataclasses:**
- `OperationExecutionReport` - Comprehensive execution report with parallelization metrics

**Key Features:**
- **Dependency Resolution** - Topological sort for correct execution order
- **Phase-Based Execution** - PRE_VALIDATION → VALIDATION → EXECUTION → POST_EXECUTION → REPORTING → FINALIZATION
- **Priority Ordering** - Within-phase priority management
- **Parallel Execution** - Independent modules run concurrently (configurable workers)
- **Error Handling** - Rollback capabilities
- **YAML-Driven** - Operation definitions from cortex-operations.yaml

**Supported Operations:**
- environment_setup
- refresh_cortex_story
- workspace_cleanup
- update_documentation
- (Extensible for any future operation)

**Parallelization Metrics:**
- parallel_execution_count
- parallel_groups_count
- time_saved_seconds

---

### 7. Optimize Cortex Orchestrator (DEPRECATED)
**Location:** `src/operations/modules/optimize/optimize_cortex_orchestrator.py`  
**Purpose:** System health scans and optimization (DEPRECATED as of November 17, 2025)  
**Lines:** 807 (total)  
**Status:** ⚠️ **DEPRECATED** - Use `src.operations.modules.optimization.optimize_cortex_orchestrator` instead

**Plugged Components:**
- `BaseOperationModule` - Core operation abstraction
- `HealthIssue` (dataclass) - Health issue representation
- `ObsoleteTest` (dataclass) - Obsolete test tracking
- `SystemHealthReport` (dataclass) - System health metrics

**Migration Notice:**
- Emits DeprecationWarning on initialization
- Redirects to new location: `src.operations.modules.optimization.optimize_cortex_orchestrator`
- Scheduled for removal in future version

---

### 8. Publish Branch Orchestrator
**Location:** `src/operations/modules/publish/publish_branch_orchestrator.py`  
**Purpose:** Production deployment to cortex-publish branch  
**Lines:** 233 (total)

**Plugged Components:**
- `BaseOperationModule` - Core operation abstraction
- `subprocess` - External script execution
- `scripts/publish_to_branch.py` - Core publish script (wrapped)

**Command-Line Flags:**
- `--dry-run` - Preview mode (no actual changes)
- `--branch` - Target branch specification
- `--resume` - Resume interrupted publish

**Execution Model:**
- Wraps external Python script via subprocess
- Captures stdout/stderr for reporting
- Returns formatted OperationResult

---

### 9. Setup Orchestrator
**Location:** `src/setup/setup_orchestrator.py`  
**Purpose:** Coordinates all setup modules (platform, vision API, brain initialization, etc.)  
**Lines:** 459 (total)

**Plugged Components:**
- `BaseSetupModule` - Setup module abstraction
- `SetupModuleMetadata` (dataclass) - Module metadata
- `SetupResult` (dataclass) - Execution results
- `SetupStatus` (enum) - Status values
- `SetupPhase` (enum) - Phase definitions

**SOLID Principles Applied:**
- **Single Responsibility** - Only orchestrates module execution
- **Open/Closed** - Add modules via registration, no code changes
- **Dependency Inversion** - Depends on BaseSetupModule abstraction

**Key Features:**
- Automatic module discovery
- Dependency resolution via topological sort
- Phase-based execution (ENVIRONMENT_VALIDATION → INSTALLATION → CONFIGURATION → VERIFICATION)
- Failure handling with rollback
- Comprehensive reporting

**Module Registration:**
```python
orchestrator.register_module(PlatformSetupModule())
orchestrator.register_module(VisionAPISetupModule())
orchestrator.register_module(BrainInitModule())
```

---

### 10. Vision Orchestrator
**Location:** `src/tier1/vision_orchestrator.py`  
**Purpose:** Automatic image detection, Vision API analysis, and context injection  
**Lines:** 438 (total)

**Plugged Components:**
- `ImageDetector` - Detects images in user requests
- `VisionAPI` - Vision API wrapper for image analysis
- `ImageAttachment` (dataclass) - Image attachment metadata

**Configuration Keys:**
- `vision_api.enabled` - Enable/disable Vision API
- `vision_api.auto_detect_images` - Automatic image detection
- `vision_api.auto_analyze_on_detect` - Automatic analysis on detection
- `vision_api.auto_inject_context` - Context injection into conversation

**Default Prompts by Context:**
- `generic` - General image analysis
- `planning` - UI element extraction for implementation
- `debugging` - Error/warning detection and stack trace extraction
- `ado` - ADO work item detail extraction

**Workflow:**
1. Detect images in user request
2. Analyze each image with Vision API
3. Inject analysis results into context
4. Generate summary for response

**Metrics Tracked:**
- total_requests
- requests_with_images
- total_images_analyzed

---

## Component Relationship Patterns

### Common Integration Patterns

1. **BaseOperationModule Inheritance**
   - All orchestrators inherit from BaseOperationModule
   - Provides: OperationPhase, OperationStatus, OperationResult, ExecutionMode
   - Enforces: Consistent phase-based execution model

2. **Dataclass Usage**
   - Orchestrators use dataclasses for state management
   - Common pattern: Metrics, Reports, Analysis Results
   - Benefits: Type safety, immutability, serialization

3. **External Module Integration**
   - Orchestrators compose external modules (not subclass)
   - Example: CleanupOrchestrator uses RemoveObsoleteTestsModule
   - Benefits: Loose coupling, testability, reusability

4. **Configuration-Driven**
   - YAML-based configuration (cortex-operations.yaml, brain files)
   - Profile-based execution (quick, standard, comprehensive)
   - Feature flags for optional components

5. **Parallel Execution (Where Applicable)**
   - OperationsOrchestrator supports parallel module execution
   - ThreadPoolExecutor with configurable worker count
   - Topological sort ensures dependency ordering

### Dependency Graph

```
BaseOperationModule
    ↓
    ├─ CleanupOrchestrator → RemoveObsoleteTestsModule
    ├─ DesignSyncOrchestrator → TrackConfigManager, TrackDocumentTemplates
    ├─ DiagramRegenerationOrchestrator → CortexDesignAnalyzer
    ├─ EnterpriseDocumentationOrchestrator → DocumentationGenerator, StoryGeneratorPlugin
    ├─ FeatureCompletionOrchestrator → KnowledgeGraph (Tier 2), ContextIntelligence (Tier 3)
    ├─ OperationsOrchestrator → (Orchestrates all above orchestrators)
    ├─ OptimizeCortexOrchestrator (DEPRECATED)
    ├─ PublishBranchOrchestrator → scripts/publish_to_branch.py
    └─ SetupOrchestrator → BaseSetupModule (PlatformSetupModule, VisionAPISetupModule, etc.)

VisionOrchestrator (Tier 1 Integration)
    ├─ ImageDetector
    └─ VisionAPI
```

---

## Usage Examples

### Cleanup Operation
```python
from src.operations.modules.cleanup.cleanup_orchestrator import CleanupOrchestrator

orchestrator = CleanupOrchestrator()
result = orchestrator.execute(
    profile='standard',
    dry_run=False
)
print(f"Cleaned {result.data['files_removed']} files")
```

### Design Sync Operation
```python
from src.operations.modules.design_sync.design_sync_orchestrator import DesignSyncOrchestrator

orchestrator = DesignSyncOrchestrator()
result = orchestrator.execute(
    profile='comprehensive',
    dry_run=False
)
print(f"Synchronized {result.data['gaps_resolved']} design gaps")
```

### Universal Operations (Any Operation)
```python
from src.operations.operations_orchestrator import OperationsOrchestrator

orchestrator = OperationsOrchestrator(
    operation_id='environment_setup',
    operation_name='Environment Setup',
    modules=[platform_mod, vision_mod, brain_mod],
    max_parallel_workers=4
)
report = orchestrator.execute_operation(context={'project_root': Path('...')})
print(f"Success: {report.success}")
print(f"Modules executed: {len(report.modules_executed)}")
print(f"Time saved by parallelization: {report.time_saved_seconds}s")
```

### Vision Analysis
```python
from src.tier1.vision_orchestrator import VisionOrchestrator

orchestrator = VisionOrchestrator(config)
result = orchestrator.process_request(
    user_request="analyze this screenshot",
    attachments=[{'type': 'image', 'data': '...'}],
    context_type='debugging'
)
print(result['context_summary'])
```

---

## Architecture Notes

### Phase-Based Execution Model

All orchestrators follow a consistent phase-based execution model inherited from BaseOperationModule:

1. **PRE_VALIDATION** - Validate inputs and preconditions
2. **VALIDATION** - Detailed validation of resources
3. **EXECUTION** - Main operation logic
4. **POST_EXECUTION** - Cleanup and finalization
5. **REPORTING** - Generate reports and metrics
6. **FINALIZATION** - Final commits, notifications

### Parallel Execution Strategy

The OperationsOrchestrator implements intelligent parallel execution:
- **Independent Modules** - Execute concurrently in parallel groups
- **Dependent Modules** - Execute sequentially after dependencies satisfied
- **Topological Sort** - Ensures correct execution order
- **Configurable Workers** - Default 4, adjustable per operation

### Error Handling

Common error handling patterns:
- **Try/Except Blocks** - Catch and log exceptions
- **Rollback Support** - Undo changes on failure
- **Graceful Degradation** - Continue with warnings when non-critical
- **Comprehensive Reporting** - Log errors in OperationResult

---

## Known Issues & Deprecations

### ⚠️ Deprecated Orchestrators

1. **OptimizeCortexOrchestrator** (src/operations/modules/optimize/)
   - **Status:** DEPRECATED as of November 17, 2025
   - **Replacement:** `src.operations.modules.optimization.optimize_cortex_orchestrator`
   - **Action:** Migrate all references to new location

### 🔍 Duplicate Implementations

According to EPMO-OPTIMIZATION-ANALYSIS.md, there are **3 duplicate OptimizeCortexOrchestrator implementations**:
- `src/operations/modules/optimize/` (DEPRECATED)
- `src/operations/modules/optimization/` (CURRENT)
- `src/operations/modules/system/` (Purpose unclear)

**Recommendation:** Consolidate to single canonical implementation in `optimization/`.

---

## Quick Reference Table

| Orchestrator | Location | LOC | Key Component | Status |
|--------------|----------|-----|---------------|--------|
| Cleanup | `cleanup/cleanup_orchestrator.py` | 1,161 | RemoveObsoleteTestsModule | ✅ Active |
| DesignSync | `design_sync/design_sync_orchestrator.py` | 1,489 | TrackConfigManager | ✅ Active |
| DiagramRegeneration | `diagrams/diagram_regeneration_orchestrator.py` | 923 | CortexDesignAnalyzer | ✅ Active |
| EnterpriseDocumentation | `enterprise_documentation_orchestrator.py` | 552 | DocumentationGenerator | ✅ Active |
| FeatureCompletion | `agents/feature_completion_orchestrator.py` | 733 | KnowledgeGraph, ContextIntelligence | ✅ Active |
| Operations (Universal) | `operations_orchestrator.py` | 665 | BaseOperationModule, ThreadPoolExecutor | ✅ Active |
| OptimizeCortex | `optimize/optimize_cortex_orchestrator.py` | 807 | HealthIssue, ObsoleteTest | ⚠️ DEPRECATED |
| PublishBranch | `publish/publish_branch_orchestrator.py` | 233 | scripts/publish_to_branch.py | ✅ Active |
| Setup | `setup/setup_orchestrator.py` | 459 | BaseSetupModule | ✅ Active |
| Vision | `tier1/vision_orchestrator.py` | 438 | ImageDetector, VisionAPI | ✅ Active |

**Total Lines of Code:** ~7,520 lines across all orchestrators

---

## Document Metadata

**Created:** December 19, 2024  
**Last Updated:** December 19, 2024  
**Version:** 1.0  
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - Part of CORTEX 3.0

**Related Documents:**
- `cortex-brain/documents/analysis/EPMO-OPTIMIZATION-ANALYSIS.md` - Orchestrator bloat analysis
- `cortex-operations.yaml` - Operation definitions
- `cortex-brain/module-definitions.yaml` - Module registry
- `src/operations/base_operation_module.py` - Base abstractions

**Maintenance:**
- Update when new orchestrators added
- Review quarterly for deprecated components
- Validate component relationships during major refactors

---

*This document is auto-generated from source code analysis and should be refreshed after significant architecture changes.*
