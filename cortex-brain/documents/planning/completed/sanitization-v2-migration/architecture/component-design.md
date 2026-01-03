# Sanitization v2 - Component Design Specification

**Created:** January 3, 2026  
**Phase:** 1 - Design Architecture  
**Version:** 1.0

---

## 🎯 Overview

Detailed component specifications for Sanitization Orchestrator v2, following the proven engine-based modular architecture pattern from ADO v2, Cleanup v2, and Vacuum v2.

---

## 📦 Component Hierarchy

```
SanitizationOrchestratorV2 (Main Orchestrator)
├── CodeAnalyzerEngine (Analysis & Risk Assessment)
├── TransformerEngine (Code Transformation with Transactions)
├── ValidatorEngine (Build/Test Validation)
├── MappingEngine (Domain→Generic Mapping) [70% REUSE]
└── ReportGeneratorEngine (Audit Reporting) [60% REUSE]
```

---

## 🏛️ SanitizationOrchestratorV2

**File:** `src/orchestrators/sanitization/sanitization_orchestrator_v2.py`  
**Lines:** 600-700  
**Inheritance:** `BaseOrchestrator` (v4.1)

### Responsibilities

1. **Workflow Orchestration** - 5-phase execution (ANALYZE → MAPPING → TRANSFORM → VALIDATE → COMPLETE)
2. **State Management** - PlanningStateDB integration for resumability
3. **Engine Coordination** - Initialize and coordinate 5 engines
4. **Error Recovery** - Handle failures with rollback
5. **Progress Reporting** - Real-time progress updates

### Key Methods

```python
class SanitizationOrchestratorV2(BaseOrchestrator):
    def __init__(
        self,
        target_directory: str,
        dry_run: bool = True,  # Default to dry-run
        config_path: Optional[str] = None,
        state_db: Optional[PlanningStateDB] = None
    ):
        """Initialize orchestrator with engines."""
        
    def execute(self, **kwargs) -> SanitizationResult:
        """Main entry point - executes 5-phase workflow."""
        
    def execute_phase_analyze(self) -> AnalysisResult:
        """Phase 1: Scan files, extract terms, classify risk."""
        
    def execute_phase_mapping(self, analysis: AnalysisResult) -> MappingResult:
        """Phase 2: Generate mappings, get approval (wizard mode)."""
        
    def execute_phase_transform(self, mappings: MappingResult) -> TransformResult:
        """Phase 3: Apply transformations transactionally."""
        
    def execute_phase_validate(self, transform: TransformResult) -> ValidationResult:
        """Phase 4: Run builds/tests, rollback on failure."""
        
    def execute_phase_complete(self, validation: ValidationResult) -> SanitizationResult:
        """Phase 5: Generate reports, clean up."""
        
    def rollback_to_checkpoint(self, checkpoint_id: str) -> bool:
        """Rollback all changes to checkpoint state."""
```

### Configuration Structure

```yaml
# cortex-brain/config/sanitization-orchestrator-v2.yaml
orchestrator:
  name: "sanitization_orchestrator_v2"
  version: "2.0.0"
  type: "autonomous"
  
execution:
  default_mode: "dry_run"
  auto_approve_safe_changes: true  # SAFE + LOW_RISK only
  require_approval_threshold: "MEDIUM"  # MEDIUM, HIGH, CRITICAL need approval
  
analysis:
  progressive_parsing: true
  ast_cache_ttl_hours: 24
  parallel_workers: 4
  
transformation:
  checkpoint_before_transform: true
  create_backups: true
  backup_location: "cortex-brain/backups/sanitization/"
  atomic_operations: true
  
validation:
  run_build: true
  run_tests: true
  test_timeout_seconds: 300
  rollback_on_failure: true
  
reporting:
  generate_diff_summary: true
  generate_mapping_manifest: true
  output_directory: "cortex-brain/documents/reports/sanitization/"
```

---

## 🔍 CodeAnalyzerEngine

**File:** `src/orchestrators/sanitization/engines/code_analyzer_engine.py`  
**Lines:** 400-500  
**Reuse:** 50% from `src/operations/utilities/sanitization/code_analyzer.py`

### Responsibilities

1. **File Scanning** - Recursive directory traversal with filtering
2. **AST Parsing** - Python AST parsing with caching (progressive)
3. **Term Extraction** - Domain-specific terminology identification
4. **Risk Classification** - Assign risk levels to each term/transformation
5. **Sensitive Data Detection** - PII, credentials, internal paths

### Key Methods

```python
class CodeAnalyzerEngine:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.ast_cache: Dict[str, ast.Module] = {}
        self.file_scanner = FileScanner()
        self.term_extractor = TermExtractor()
        self.risk_classifier = RiskClassifier()
        
    def analyze_directory(self, directory: Path) -> AnalysisResult:
        """
        Progressive analysis pipeline:
        1. Quick scan (file types, sizes, patterns)
        2. AST parsing (cached for performance)
        3. Deep analysis (term extraction, risk classification)
        """
        
    def scan_files(self, directory: Path) -> List[FileInfo]:
        """Scan directory structure, return file metadata."""
        
    def parse_ast(self, file_path: Path, use_cache: bool = True) -> ast.Module:
        """Parse Python file to AST with caching."""
        
    def extract_domain_terms(self, files: List[FileInfo]) -> List[DomainTerm]:
        """Extract domain-specific terminology from code."""
        
    def classify_risk(self, term: DomainTerm) -> RiskLevel:
        """Classify transformation risk for each term."""
        
    def detect_sensitive_data(self, files: List[FileInfo]) -> List[SensitiveData]:
        """Detect PII, credentials, internal paths."""
```

### Risk Classification (5 Levels)

```python
class RiskLevel(Enum):
    SAFE = 1           # Low-impact renames (comments, docs)
    LOW_RISK = 2       # Simple variable renames
    MEDIUM = 3         # Function/class renames (needs validation)
    HIGH = 4           # API changes, public interfaces
    CRITICAL = 5       # Core logic, entry points, external contracts
```

### Risk Classification Rules

| Risk Level | Examples | Auto-Approve | Validation Required |
|------------|----------|--------------|---------------------|
| SAFE | Comments, docstrings, README | ✅ Yes | Build only |
| LOW_RISK | Local variables, private methods | ✅ Yes | Build + smoke tests |
| MEDIUM | Public methods, class names | ❌ No | Build + full tests |
| HIGH | Module names, API endpoints | ❌ No | Build + integration tests |
| CRITICAL | Entry points, external contracts | ❌ No | Build + full suite + manual review |

---

## 🔄 TransformerEngine

**File:** `src/orchestrators/sanitization/engines/transformer_engine.py`  
**Lines:** 500-600  
**Reuse:** 20% from `src/operations/utilities/sanitization/transformer.py`

### Responsibilities

1. **Transactional Operations** - Atomic commit/rollback via TransformationTransaction
2. **AST Transformation** - Python code transformations using ast.NodeTransformer
3. **File/Directory Renaming** - Filesystem operations with safety checks
4. **Checkpoint Management** - Create/restore checkpoint backups
5. **Verification** - SHA256 hashing to verify transformations

### Key Methods

```python
class TransformerEngine:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.transaction: Optional[TransformationTransaction] = None
        self.checkpoint_manager = CheckpointManager()
        
    def transform_directory(
        self, 
        directory: Path, 
        mappings: Dict[str, str],
        dry_run: bool = False
    ) -> TransformResult:
        """
        Execute transformations with transaction safety:
        1. Create checkpoint
        2. Begin transaction
        3. Apply transformations
        4. Verify integrity
        5. Commit (or rollback on error)
        """
        
    def create_checkpoint(self, directory: Path) -> str:
        """Create backup checkpoint before transformations."""
        
    def begin_transaction(self) -> TransformationTransaction:
        """Begin atomic transformation transaction."""
        
    def apply_ast_transformation(
        self, 
        file_path: Path, 
        mappings: Dict[str, str]
    ) -> TransformationOp:
        """Apply AST-based code transformations."""
        
    def rename_file(self, old_path: Path, new_path: Path) -> TransformationOp:
        """Rename file with collision detection."""
        
    def rename_directory(self, old_path: Path, new_path: Path) -> TransformationOp:
        """Rename directory with recursive updates."""
        
    def verify_transformations(self, operations: List[TransformationOp]) -> bool:
        """Verify SHA256 checksums of transformed files."""
        
    def commit_transaction(self) -> bool:
        """Commit all transformation operations."""
        
    def rollback_transaction(self) -> bool:
        """Rollback to checkpoint state."""
```

### TransformationTransaction Interface

```python
@dataclass
class TransformationOp:
    """Single transformation operation."""
    op_type: str  # 'ast_transform', 'file_rename', 'dir_rename'
    target: Path
    old_content: Optional[str]  # For rollback
    new_content: Optional[str]
    old_path: Optional[Path]
    new_path: Optional[Path]
    checksum_before: str
    checksum_after: str
    timestamp: datetime
    risk_level: RiskLevel

class TransformationTransaction:
    """Atomic transaction for transformations."""
    
    def __init__(self, checkpoint_id: str):
        self.checkpoint_id = checkpoint_id
        self.operations: List[TransformationOp] = []
        self.committed = False
        self.rolled_back = False
        
    def add_operation(self, operation: TransformationOp):
        """Add operation to transaction."""
        
    def commit(self) -> bool:
        """Commit all operations atomically."""
        
    def rollback(self) -> bool:
        """Rollback all operations to checkpoint."""
        
    def __enter__(self):
        """Context manager support."""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Auto-rollback on exception."""
        if exc_type:
            self.rollback()
```

---

## ✅ ValidatorEngine

**File:** `src/orchestrators/sanitization/engines/validator_engine.py`  
**Lines:** 300-400  
**Reuse:** 40% from `src/operations/utilities/sanitization/validator.py`

### Responsibilities

1. **Build System Detection** - Identify build tool (pytest, unittest, tox, etc.)
2. **Build Execution** - Run builds with timeout and output capture
3. **Test Execution** - Run test suites with comparison
4. **Functionality Verification** - Compare test results before/after
5. **Rollback Trigger** - Trigger rollback on validation failure

### Key Methods

```python
class ValidatorEngine:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.build_detector = BuildSystemDetector()
        self.test_runner = TestRunner()
        
    def validate_transformations(
        self, 
        directory: Path,
        baseline_results: Optional[TestResults] = None
    ) -> ValidationResult:
        """
        Validation pipeline:
        1. Detect build system
        2. Run build
        3. Execute tests
        4. Compare results with baseline
        5. Trigger rollback if validation fails
        """
        
    def detect_build_system(self, directory: Path) -> BuildSystem:
        """Detect build system (pytest, unittest, tox, etc.)."""
        
    def run_build(self, directory: Path, build_system: BuildSystem) -> BuildResult:
        """Execute build with timeout."""
        
    def run_tests(self, directory: Path, build_system: BuildSystem) -> TestResults:
        """Execute test suite."""
        
    def compare_test_results(
        self, 
        baseline: TestResults, 
        current: TestResults
    ) -> ComparisonResult:
        """Compare test results for functionality parity."""
        
    def should_rollback(self, validation: ValidationResult) -> bool:
        """Determine if rollback is required."""
```

### Validation Rules

| Scenario | Action |
|----------|--------|
| Build fails | ❌ **ROLLBACK** immediately |
| Tests fail (new failures) | ❌ **ROLLBACK** immediately |
| Tests pass (same as baseline) | ✅ **COMMIT** transformations |
| Tests pass (more pass than baseline) | ⚠️ **WARN** + COMMIT |
| Tests skipped (baseline had tests) | ❌ **ROLLBACK** (possible breakage) |

---

## 🗺️ MappingEngine

**File:** `src/orchestrators/sanitization/engines/mapping_engine.py`  
**Lines:** 300-400  
**Reuse:** 70% from `src/operations/utilities/sanitization/mapping_engine.py`

### Responsibilities

1. **Mapping Generation** - Create domain→generic mappings
2. **Conflict Detection** - Identify naming collisions
3. **Mapping Persistence** - Save/load mappings to JSON
4. **Approval Workflow** - Interactive wizard for approval (wizard mode)
5. **Heuristic Naming** - Generate generic names with context

### Key Methods

```python
class MappingEngine:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.mapping_store = MappingStore()
        self.conflict_detector = ConflictDetector()
        self.name_generator = GenericNameGenerator()
        
    def generate_mappings(
        self, 
        domain_terms: List[DomainTerm]
    ) -> Dict[str, str]:
        """Generate domain→generic mappings."""
        
    def detect_conflicts(self, mappings: Dict[str, str]) -> List[Conflict]:
        """Detect naming collisions in generated mappings."""
        
    def resolve_conflicts(
        self, 
        conflicts: List[Conflict],
        auto_resolve: bool = False
    ) -> Dict[str, str]:
        """Resolve conflicts (auto or interactive)."""
        
    def approve_mappings(
        self, 
        mappings: Dict[str, str],
        auto_approve_safe: bool = True
    ) -> ApprovalResult:
        """
        Approval workflow (wizard mode):
        - Auto-approve SAFE + LOW_RISK if enabled
        - Present MEDIUM/HIGH/CRITICAL for interactive review
        - Allow individual approval/rejection
        """
        
    def persist_mappings(self, mappings: Dict[str, str], output_path: Path):
        """Save mappings to JSON for audit trail."""
        
    def load_mappings(self, input_path: Path) -> Dict[str, str]:
        """Load previously saved mappings."""
```

---

## 📊 ReportGeneratorEngine

**File:** `src/orchestrators/sanitization/engines/report_generator_engine.py`  
**Lines:** 200-300  
**Reuse:** 60% from `src/operations/utilities/sanitization/report_generator.py`

### Responsibilities

1. **Audit Report Generation** - Comprehensive transformation report
2. **Metrics Collection** - Files transformed, mappings applied, etc.
3. **Diff Summary** - Before/after code diffs
4. **Mapping Documentation** - Human-readable mapping manifest
5. **Artifact Creation** - Export reports to markdown/JSON

### Key Methods

```python
class ReportGeneratorEngine:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.template_renderer = TemplateRenderer()
        
    def generate_report(
        self, 
        analysis: AnalysisResult,
        mappings: MappingResult,
        transform: TransformResult,
        validation: ValidationResult
    ) -> ReportResult:
        """Generate comprehensive audit report."""
        
    def collect_metrics(self, result: SanitizationResult) -> Dict[str, Any]:
        """Collect transformation metrics."""
        
    def generate_diff_summary(
        self, 
        operations: List[TransformationOp]
    ) -> str:
        """Generate before/after code diffs."""
        
    def generate_mapping_manifest(
        self, 
        mappings: Dict[str, str]
    ) -> str:
        """Generate human-readable mapping documentation."""
        
    def export_to_markdown(self, report: ReportResult, output_path: Path):
        """Export report to markdown."""
        
    def export_to_json(self, report: ReportResult, output_path: Path):
        """Export report to JSON for programmatic access."""
```

---

## 🔗 Component Interactions

### Phase 1: ANALYZE
```
SanitizationOrchestratorV2.execute_phase_analyze()
├── CodeAnalyzerEngine.analyze_directory()
│   ├── scan_files()
│   ├── parse_ast() [with caching]
│   ├── extract_domain_terms()
│   ├── classify_risk()
│   └── detect_sensitive_data()
└── Return AnalysisResult
```

### Phase 2: MAPPING
```
SanitizationOrchestratorV2.execute_phase_mapping(analysis)
├── MappingEngine.generate_mappings(analysis.domain_terms)
├── MappingEngine.detect_conflicts(mappings)
├── MappingEngine.resolve_conflicts(conflicts)
├── MappingEngine.approve_mappings(mappings) [wizard mode]
└── Return MappingResult
```

### Phase 3: TRANSFORM
```
SanitizationOrchestratorV2.execute_phase_transform(mappings)
├── TransformerEngine.create_checkpoint()
├── TransformerEngine.begin_transaction()
├── TransformerEngine.apply_ast_transformation()
├── TransformerEngine.rename_file()
├── TransformerEngine.verify_transformations()
├── TransformerEngine.commit_transaction()
└── Return TransformResult
```

### Phase 4: VALIDATE
```
SanitizationOrchestratorV2.execute_phase_validate(transform)
├── ValidatorEngine.detect_build_system()
├── ValidatorEngine.run_build()
├── ValidatorEngine.run_tests()
├── ValidatorEngine.compare_test_results()
├── IF validation fails:
│   └── TransformerEngine.rollback_transaction()
└── Return ValidationResult
```

### Phase 5: COMPLETE
```
SanitizationOrchestratorV2.execute_phase_complete(validation)
├── ReportGeneratorEngine.generate_report()
├── ReportGeneratorEngine.collect_metrics()
├── ReportGeneratorEngine.generate_diff_summary()
├── ReportGeneratorEngine.export_to_markdown()
└── Return SanitizationResult
```

---

## 📈 Performance Optimizations

### Progressive Analysis (CodeAnalyzerEngine)
- **Quick Scan:** File types, sizes, patterns (0.1s per 1000 files)
- **AST Parsing:** Lazy parsing with 24h cache (0.5s per file, amortized)
- **Deep Analysis:** Only for files needing transformation

### Parallel Processing
- 4 worker threads for file scanning
- AST parsing parallelized across files
- Safe for read operations (analysis phase)

### Transaction Optimization (TransformerEngine)
- Batch operations by risk level (SAFE first, CRITICAL last)
- Early validation for high-risk operations
- Deferred commit until all operations verified

---

## 🎯 Success Criteria

**Component Design Complete When:**
- ✅ All 5 engines specified with clear responsibilities
- ✅ Interface contracts defined (method signatures, data structures)
- ✅ TransformationTransaction interface documented
- ✅ Risk classification rules specified (5 levels)
- ✅ Component interaction flows documented
- ✅ Performance optimizations identified
- ✅ Code reuse strategy documented (45% overall)

---

**Next:** Phase 1.5 - Holistic Review #2 (validate design against Cleanup v2/Vacuum v2 implementations)
