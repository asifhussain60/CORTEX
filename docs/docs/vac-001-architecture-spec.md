# PHASE-VAC-001: Cleaner Plugin Architecture Specification

**Document Purpose:** Detailed technical specification for the SOLID-compliant plugin architecture for VacuumOrchestrator cleaners.

**Status:** DESIGN SPECIFICATION (before implementation)  
**Version:** 1.0  
**Date:** 2026-01-17  

---

## TABLE OF CONTENTS

1. [Architecture Overview](#architecture-overview)
2. [Component Design](#component-design)
3. [CleanerInterface Specification](#cleanerinterface-specification)
4. [Plugin Lifecycle](#plugin-lifecycle)
5. [Implementation Patterns](#implementation-patterns)
6. [Future Cleaner Examples](#future-cleaner-examples)
7. [Testing Strategy](#testing-strategy)

---

## ARCHITECTURE OVERVIEW

### System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ HousekeepingOrchestrator                                        │
│ (scheduled invocation, triggers cleaner operations)             │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ VacuumOrchestrator                                              │
│ ┌───────────────────────────────────────────────────────────┐   │
│ │ CleanerRegistry                                           │   │
│ │ • register_cleaner(cleaner: CleanerInterface)            │   │
│ │ • list_cleaners() → List[CleanerInterface]               │   │
│ │ • get_cleaner(name: str) → CleanerInterface              │   │
│ └───────────────────────────────────────────────────────────┘   │
│                                                                 │
│ ┌───────────────────────────────────────────────────────────┐   │
│ │ Plugin Coordinator                                        │   │
│ │ • analyze_all() → List[Analysis]                         │   │
│ │ • execute_all(plan) → List[Report]                       │   │
│ │ • rollback_all() → List[RollbackResult]                  │   │
│ └───────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┬─────────────────┐
        ▼              ▼              ▼                 ▼
    ┌─────────┐  ┌──────────┐   ┌──────────┐    ┌──────────┐
    │ Cleaner │  │ Cleaner  │   │ Cleaner  │    │ Cleaner  │
    │ #1      │  │ #2       │   │ #3       │    │ #N       │
    │ MD Org  │  │ PyCache  │   │ Backups  │    │ Logs     │
    │         │  │ (Future) │   │ (Future) │    │ (Future) │
    └────┬────┘  └────┬─────┘   └────┬─────┘    └────┬─────┘
         │            │              │               │
         └────────────┴──────────────┴───────────────┘
                      │
                      ▼
            ┌──────────────────────┐
            │ CleanerInterface     │
            │ (Abstract Base)      │
            │ ┌──────────────────┐ │
            │ │ analyze()        │ │
            │ │ execute(plan)    │ │
            │ │ rollback()       │ │
            │ │ config: Config   │ │
            │ └──────────────────┘ │
            └──────────────────────┘
```

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Plugin Pattern** | New cleaners added without modifying orchestrator (Open/Closed) |
| **Registry Pattern** | Dynamic cleaner discovery and registration |
| **Interface Segregation** | Minimal CleanerInterface (only essential methods) |
| **Dependency Inversion** | Orchestrator depends on CleanerInterface, not concrete implementations |
| **Config per Cleaner** | Each cleaner can override global config settings |

---

## COMPONENT DESIGN

### 1. CleanerInterface (Abstract Base)

**Location:** `cortex-brain/tier1/orchestrators/cleaners/interface.py`

**Purpose:** Define contract that all cleaners must implement

**Interface Definition:**

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any
from pathlib import Path

@dataclass
class Analysis:
    """Result of analyze() phase"""
    cleaner_id: str
    timestamp: str
    files_scanned: int
    issues_found: int
    plan: Dict[str, Any]  # Execution plan
    logs: List[str]

@dataclass
class Report:
    """Result of execute() phase"""
    cleaner_id: str
    timestamp: str
    status: str  # "SUCCESS" | "FAILED" | "PARTIAL"
    actions_taken: int
    changes: Dict[str, Any]
    errors: List[str]
    logs: List[str]

@dataclass
class RollbackResult:
    """Result of rollback() phase"""
    cleaner_id: str
    timestamp: str
    status: str  # "SUCCESS" | "FAILED"
    files_restored: int
    errors: List[str]

class CleanerInterface(ABC):
    """Abstract base for all VacuumOrchestrator cleaners
    
    All cleaners MUST implement this interface to be registered
    with VacuumOrchestrator. This ensures SOLID compliance:
    - Single Responsibility: Each cleaner handles one domain
    - Liskov Substitution: All cleaners interchangeable
    - Interface Segregation: Minimal required methods
    
    Example usage:
        cleaner = MDOrganizerCleaner(config)
        analysis = cleaner.analyze()
        report = cleaner.execute(analysis.plan)
    """
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize cleaner with configuration
        
        Args:
            config: Cleaner-specific configuration dict
        
        Raises:
            ConfigError: If required config keys missing
        """
        self.config = config
        self.cleaner_id: str = self.__class__.__name__
        self.logger = self._setup_logger()
    
    @abstractmethod
    def analyze(self) -> Analysis:
        """Non-destructive analysis phase
        
        Scan repository to:
        1. Identify items to clean
        2. Detect dependencies/references
        3. Plan execution strategy
        4. Estimate impact
        
        Returns:
            Analysis: Detailed analysis result with execution plan
        
        Note:
            - MUST NOT modify any files
            - MUST be deterministic (same input → same output)
            - MUST complete within reasonable time (<60 seconds)
            - MUST log all findings
        """
        pass
    
    @abstractmethod
    def execute(self, plan: Dict[str, Any]) -> Report:
        """Controlled execution phase
        
        Apply changes per provided plan:
        1. Create pre-execution snapshot
        2. Apply changes with logging
        3. Verify final state
        4. Enable rollback
        
        Args:
            plan: Execution plan from analyze() phase
        
        Returns:
            Report: Detailed execution result
        
        Raises:
            ExecutionError: If execution fails
        
        Note:
            - MUST create snapshot before modifications
            - MUST log all changes with timestamp
            - MUST verify final state
            - MUST support rollback
        """
        pass
    
    @abstractmethod
    def rollback(self) -> RollbackResult:
        """Rollback to pre-execution state
        
        Restore repository from snapshot:
        1. Verify snapshot exists
        2. Restore all files
        3. Verify restoration
        4. Clean up snapshot
        
        Returns:
            RollbackResult: Rollback operation result
        
        Raises:
            RollbackError: If rollback fails
        
        Note:
            - MUST verify snapshot integrity before restore
            - MUST handle partial failures
            - MUST log all restore operations
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable cleaner name
        
        Returns:
            str: Display name (e.g., "MD Organizer", "Python Cache")
        """
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Cleaner version
        
        Returns:
            str: Version string (e.g., "1.0.0")
        """
        pass
    
    @property
    @abstractmethod
    def domain(self) -> str:
        """Domain this cleaner operates on
        
        Returns:
            str: Domain identifier (e.g., "md_docs", "python_cache")
        
        Note:
            Used for configuration resolution and logging
        """
        pass
    
    def _setup_logger(self):
        """Setup cleaner-specific logger
        
        Returns:
            Logger configured with cleaner ID
        """
        import logging
        return logging.getLogger(self.cleaner_id)
```

### 2. CleanerRegistry

**Location:** `cortex-brain/tier1/orchestrators/cleaners/registry.py`

**Purpose:** Manage plugin registration and discovery

```python
from typing import Dict, List, Type, Optional
from .interface import CleanerInterface

class CleanerRegistry:
    """Registry for VacuumOrchestrator cleaner plugins
    
    SOLID Compliance:
    - Open/Closed: Registry extensible without modification
    - Dependency Inversion: Registry depends on CleanerInterface
    
    Usage:
        registry = CleanerRegistry()
        registry.register_cleaner(MDOrganizerCleaner)
        registry.register_cleaner(PythonCacheCleaner)
        
        cleaners = registry.list_all()
        md_cleaner = registry.get_cleaner("md_organizer")
    """
    
    def __init__(self) -> None:
        """Initialize empty registry"""
        self._cleaners: Dict[str, Type[CleanerInterface]] = {}
    
    def register_cleaner(
        self, 
        cleaner_class: Type[CleanerInterface],
        domain: str = None
    ) -> None:
        """Register a cleaner implementation
        
        Args:
            cleaner_class: Class implementing CleanerInterface
            domain: Override domain (uses cleaner.domain if None)
        
        Raises:
            ValueError: If cleaner_class doesn't implement interface
            DuplicateCleanerError: If domain already registered
        """
        # Verify implements interface
        if not issubclass(cleaner_class, CleanerInterface):
            raise ValueError(f"{cleaner_class} must implement CleanerInterface")
        
        # Get domain
        domain = domain or cleaner_class.domain.fget(None)
        
        # Check duplicate
        if domain in self._cleaners:
            raise DuplicateCleanerError(f"Cleaner already registered for domain: {domain}")
        
        self._cleaners[domain] = cleaner_class
    
    def get_cleaner(
        self, 
        domain: str,
        config: Dict = None
    ) -> CleanerInterface:
        """Get instantiated cleaner by domain
        
        Args:
            domain: Domain identifier
            config: Override configuration (uses global if None)
        
        Returns:
            Instantiated cleaner ready to use
        
        Raises:
            CleanerNotFoundError: If domain not registered
        """
        if domain not in self._cleaners:
            raise CleanerNotFoundError(f"No cleaner registered for: {domain}")
        
        cleaner_class = self._cleaners[domain]
        config = config or self._load_config(domain)
        return cleaner_class(config)
    
    def list_all(self) -> List[str]:
        """List all registered cleaner domains
        
        Returns:
            List of domain identifiers
        """
        return list(self._cleaners.keys())
    
    def _load_config(self, domain: str) -> Dict:
        """Load configuration for cleaner
        
        Tries in order:
        1. Per-cleaner config: cortex-brain/tier1/orchestrators/cleaners/<domain>/config.yaml
        2. Global config: cortex-brain/vacuum/config.yaml
        
        Args:
            domain: Domain identifier
        
        Returns:
            Configuration dict
        """
        import yaml
        from pathlib import Path
        
        # Per-cleaner config
        cleaner_config_path = Path(__file__).parent / domain / "config.yaml"
        if cleaner_config_path.exists():
            with open(cleaner_config_path) as f:
                return yaml.safe_load(f)
        
        # Global config
        global_config_path = Path(__file__).parent.parent.parent / "vacuum" / "config.yaml"
        if global_config_path.exists():
            with open(global_config_path) as f:
                return yaml.safe_load(f)
        
        # No config found
        return {}
```

### 3. VacuumOrchestrator Enhancement

**Location:** `cortex-brain/tier1/orchestrators/vacuum.py`

**Enhancement:** Add cleaner plugin support

```python
class VacuumOrchestrator:
    """Enhanced with cleaner plugin support
    
    NEW CAPABILITY: Plugin-based cleaners
    
    Usage:
        orchestrator = VacuumOrchestrator()
        
        # Register cleaners
        orchestrator.register_cleaner(MDOrganizerCleaner)
        
        # Analyze all
        analyses = orchestrator.analyze_all()
        
        # Execute all
        reports = orchestrator.execute_all(dry_run=True)  # Dry run first
        reports = orchestrator.execute_all(dry_run=False)  # Then real
        
        # Rollback if needed
        results = orchestrator.rollback_all()
    """
    
    def __init__(self) -> None:
        """Initialize with cleaner registry"""
        self.registry = CleanerRegistry()
        self.cleaners: Dict[str, CleanerInterface] = {}
    
    def register_cleaner(
        self, 
        cleaner_class: Type[CleanerInterface]
    ) -> None:
        """Register a cleaner plugin
        
        Args:
            cleaner_class: Class implementing CleanerInterface
        """
        self.registry.register_cleaner(cleaner_class)
        # Lazy instantiation (instantiate on first use)
    
    def analyze_all(self) -> Dict[str, Analysis]:
        """Analyze all registered cleaners
        
        Returns:
            Dict mapping cleaner domain to Analysis
        """
        results = {}
        for domain in self.registry.list_all():
            cleaner = self.registry.get_cleaner(domain)
            results[domain] = cleaner.analyze()
            self.cleaners[domain] = cleaner  # Cache for later
        return results
    
    def execute_all(
        self,
        dry_run: bool = True
    ) -> Dict[str, Report]:
        """Execute all cleaners
        
        Args:
            dry_run: If True, show what would happen
        
        Returns:
            Dict mapping cleaner domain to Report
        """
        results = {}
        for domain in self.registry.list_all():
            cleaner = self.registry.get_cleaner(domain)
            
            if not dry_run:
                # Real execution
                analysis = cleaner.analyze()
                results[domain] = cleaner.execute(analysis.plan)
            else:
                # Dry run - just show plan
                analysis = cleaner.analyze()
                results[domain] = Report(
                    cleaner_id=cleaner.cleaner_id,
                    timestamp=str(datetime.now()),
                    status="DRY_RUN",
                    actions_taken=len(analysis.plan),
                    changes=analysis.plan,
                    errors=[],
                    logs=analysis.logs
                )
        
        return results
```

---

## CleanerInterface Specification

### Lifecycle Diagram

```
START
  │
  ├─► analyze()
  │   ├─ Scan repository
  │   ├─ Identify issues
  │   ├─ Generate plan (non-destructive)
  │   └─► Analysis object
  │
  ├─► execute(plan)
  │   ├─ Create snapshot
  │   ├─ Apply changes
  │   ├─ Verify state
  │   └─► Report object
  │
  ├─ Decision Point
  │   ├─ SUCCESS? ──► END
  │   └─ FAILED? ──► rollback()
  │       ├─ Restore from snapshot
  │       ├─ Verify restoration
  │       └─► RollbackResult
  │
END
```

### Return Types

**Analysis (from analyze())**

```yaml
Analysis:
  cleaner_id: str              # Class name
  timestamp: ISO-8601          # When analysis ran
  files_scanned: int           # Total files examined
  issues_found: int            # Issues detected
  plan: Dict[str, Any]         # Execution plan (what will change)
  logs: List[str]              # Detailed logs of analysis
```

**Report (from execute())**

```yaml
Report:
  cleaner_id: str              # Class name
  timestamp: ISO-8601          # When execution ran
  status: str                  # "SUCCESS" | "FAILED" | "PARTIAL"
  actions_taken: int           # Number of changes made
  changes: Dict[str, Any]      # What actually changed
  errors: List[str]            # Any errors encountered
  logs: List[str]              # Detailed logs of execution
```

**RollbackResult (from rollback())**

```yaml
RollbackResult:
  cleaner_id: str              # Class name
  timestamp: ISO-8601          # When rollback ran
  status: str                  # "SUCCESS" | "FAILED"
  files_restored: int          # Files restored from snapshot
  errors: List[str]            # Any errors during rollback
```

---

## Plugin Lifecycle

### 1. Discovery & Registration (Startup)

```
VacuumOrchestrator.__init__()
  └─► Auto-discover cleaners in cortex-brain/tier1/orchestrators/cleaners/
      ├─ For each subdirectory (md_organizer, python_cache, etc.):
      │  ├─ Import cleaner module
      │  ├─ Verify implements CleanerInterface
      │  ├─ registry.register_cleaner()
      │  └─ Log registration
      └─► All cleaners available
```

### 2. Analysis Phase

```
analyze_all()
  └─► For each registered cleaner:
      ├─ Instantiate: cleaner = registry.get_cleaner(domain, config)
      ├─ Invoke: analysis = cleaner.analyze()
      │   ├─ Scan repository
      │   ├─ Detect issues
      │   └─ Generate execution plan (no changes)
      ├─ Store: analyses[domain] = analysis
      └─► Return all analyses
```

### 3. Execution Phase

```
execute_all(analyses)
  └─► For each analysis:
      ├─ Get cleaner: cleaner = registry.get_cleaner(domain)
      ├─ Create snapshot: snapshot = cleaner.create_snapshot()
      ├─ Invoke: report = cleaner.execute(analysis.plan)
      │   ├─ Apply changes
      │   ├─ Verify state
      │   └─ Return report
      ├─ Store: reports[domain] = report
      └─► Return all reports
```

### 4. Rollback Phase (if needed)

```
rollback_all()
  └─► For each cleaner with snapshot:
      ├─ Invoke: result = cleaner.rollback()
      │   ├─ Restore from snapshot
      │   ├─ Verify restoration
      │   └─ Clean up snapshot
      ├─ Store: results[domain] = result
      └─► Return all results
```

---

## Implementation Patterns

### Creating a New Cleaner

**Template: cortex-brain/tier1/orchestrators/cleaners/my_domain/cleaner.py**

```python
from ..interface import CleanerInterface, Analysis, Report, RollbackResult
from typing import Dict, Any
from datetime import datetime

class MyDomainCleaner(CleanerInterface):
    """Cleaner for [my_domain]
    
    Handles: [specific responsibility]
    
    Example:
        cleaner = MyDomainCleaner(config)
        analysis = cleaner.analyze()
        report = cleaner.execute(analysis.plan)
    """
    
    @property
    def name(self) -> str:
        """Human-readable name"""
        return "My Domain Cleaner"
    
    @property
    def version(self) -> str:
        """Cleaner version"""
        return "1.0.0"
    
    @property
    def domain(self) -> str:
        """Domain identifier"""
        return "my_domain"
    
    def analyze(self) -> Analysis:
        """Analyze my_domain for issues"""
        self.logger.info(f"Starting analysis for {self.domain}")
        
        # 1. Scan repository
        issues = self._scan_repository()
        
        # 2. Generate execution plan
        plan = self._generate_plan(issues)
        
        # 3. Return analysis
        return Analysis(
            cleaner_id=self.__class__.__name__,
            timestamp=datetime.now().isoformat(),
            files_scanned=len(issues),
            issues_found=len(issues),
            plan=plan,
            logs=self.logger.getvalue()
        )
    
    def execute(self, plan: Dict[str, Any]) -> Report:
        """Execute cleanup per plan"""
        self.logger.info(f"Starting execution for {self.domain}")
        
        try:
            # 1. Create snapshot
            snapshot_path = self._create_snapshot()
            
            # 2. Apply changes
            changes = self._apply_changes(plan)
            
            # 3. Verify state
            self._verify_state()
            
            return Report(
                cleaner_id=self.__class__.__name__,
                timestamp=datetime.now().isoformat(),
                status="SUCCESS",
                actions_taken=len(changes),
                changes=changes,
                errors=[],
                logs=self.logger.getvalue()
            )
        except Exception as e:
            self.logger.error(f"Execution failed: {e}")
            raise
    
    def rollback(self) -> RollbackResult:
        """Rollback to pre-execution state"""
        self.logger.info(f"Starting rollback for {self.domain}")
        
        try:
            # 1. Restore from snapshot
            restored = self._restore_snapshot()
            
            # 2. Verify restoration
            self._verify_restoration()
            
            return RollbackResult(
                cleaner_id=self.__class__.__name__,
                timestamp=datetime.now().isoformat(),
                status="SUCCESS",
                files_restored=restored,
                errors=[]
            )
        except Exception as e:
            self.logger.error(f"Rollback failed: {e}")
            raise
    
    # Implementation details...
```

### Registering in VacuumOrchestrator

**File: cortex-brain/tier1/orchestrators/cleaners/__init__.py**

```python
from .interface import CleanerInterface, Analysis, Report, RollbackResult
from .md_organizer.cleaner import MDOrganizerCleaner
from .registry import CleanerRegistry

__all__ = [
    'CleanerInterface',
    'Analysis',
    'Report',
    'RollbackResult',
    'MDOrganizerCleaner',
    'CleanerRegistry',
]
```

---

## Future Cleaner Examples

### PHASE-VAC-002: Python Cache Cleaner

```python
class PythonCacheCleaner(CleanerInterface):
    """Remove __pycache__ and *.pyc files
    
    Handles:
    - __pycache__ directories
    - *.pyc files
    - *.pyo files
    - *.pyd files
    """
    
    @property
    def domain(self) -> str:
        return "python_cache"
```

### PHASE-VAC-003: Backup Cleaner

```python
class BackupCleaner(CleanerInterface):
    """Remove backup files
    
    Handles:
    - *.bak files
    - *.backup files
    - *~* files
    - .old files
    """
    
    @property
    def domain(self) -> str:
        return "backups"
```

### PHASE-VAC-004: Log Archiver

```python
class LogArchiver(CleanerInterface):
    """Compress and archive old logs
    
    Handles:
    - Logs older than X days
    - Compresses to .tar.gz
    - Archives to logs/archive/
    """
    
    @property
    def domain(self) -> str:
        return "log_archive"
```

---

## Testing Strategy

### Test Structure

```
tests/
├── unit/
│   └── tier1/
│       └── orchestrators/
│           ├── test_cleaner_interface.py
│           │   ├── test_cleaner_interface_contract
│           │   ├── test_abstract_methods_required
│           │   └── test_return_types
│           │
│           ├── test_cleaner_registry.py
│           │   ├── test_register_cleaner
│           │   ├── test_get_cleaner
│           │   ├── test_duplicate_detection
│           │   └── test_lazy_instantiation
│           │
│           ├── test_md_organizer_cleaner.py
│           │   ├── test_analyze_detects_all_md_files
│           │   ├── test_analyze_generates_valid_plan
│           │   ├── test_execute_creates_snapshot
│           │   ├── test_execute_applies_changes
│           │   ├── test_rollback_restores_snapshot
│           │   └── test_no_modifications_during_analyze
│           │
│           └── test_vacuum_orchestrator_integration.py
│               ├── test_register_cleaner
│               ├── test_analyze_all
│               ├── test_execute_all
│               ├── test_rollback_all
│               └── test_cleaner_plugin_pattern
│
└── integration/
    └── test_md_organizer_execution.py
        ├── test_analyze_real_repository
        ├── test_execute_on_real_repository
        ├── test_verify_no_broken_references
        └── test_rollback_to_clean_state
```

### Key Test Assertions

**CleanerInterface Contract:**
- All abstract methods must be implemented
- All methods must return correct type
- Type hints present on all methods
- Docstrings present on all public methods

**Plugin Architecture:**
- New cleaners don't require orchestrator modification
- Registry.register_cleaner() works with any CleanerInterface
- Multiple cleaners can coexist
- Cleaners can be instantiated independently

**MD Organizer Specific:**
- analyze() doesn't modify any files
- execute() creates snapshot before modifications
- rollback() restores exact pre-execution state
- No broken references after execution

---

## SOLID Compliance Verification

| Principle | Verification | Status |
|-----------|--------------|--------|
| **S** | Each cleaner has ONE domain of responsibility | ✅ VAC-001-01 |
| **O** | New cleaners added WITHOUT modifying VacuumOrchestrator | ✅ VAC-001-04 |
| **L** | All cleaners interchangeable via CleanerInterface | ✅ VAC-001-01 |
| **I** | CleanerInterface minimal: analyze, execute, rollback only | ✅ VAC-001-01 |
| **D** | VacuumOrchestrator depends on CleanerInterface abstraction | ✅ VAC-001-04 |

---

## Configuration Schema

### Global Configuration

**File: cortex-brain/vacuum/config.yaml**

```yaml
cleaners:
  enabled:
    - md_organizer
    - python_cache  # Future
    - backups       # Future
    - logs          # Future
  
  execution:
    dry_run: true           # Always dry-run first
    create_snapshot: true   # Always create snapshot
    verify_state: true      # Verify after changes
    rollback_on_error: true # Auto-rollback on failure
```

### Per-Cleaner Configuration

**File: cortex-brain/tier1/orchestrators/cleaners/md_organizer/config.yaml**

```yaml
md_organizer:
  # Override global settings if needed
  dry_run: false
  
  # MD-specific settings
  patterns:
    essential:
      - "README.md"
      - ".github/**/*.md"
    
    consolidatable:
      - "SESSION-*.md"
      - "PHASE-*-*.md"
    
    deletable:
      - "*-old.md"
      - "*-backup.md"
```

---

## Conclusion

This architecture provides:

✅ **Extensibility:** New cleaners added without modification  
✅ **Maintainability:** Clear interfaces and responsibilities  
✅ **Reliability:** Plugin pattern enables testing in isolation  
✅ **Safety:** Snapshot and rollback support  
✅ **Auditability:** All operations logged  

The foundation is ready for PHASE-VAC-001-01 implementation.
