"""
Change Coherence Engine Package.

ENH-101: Ensures all file modifications maintain coherence with entire file.

Components:
    - ChangeCoherenceEngine: Main orchestrator (pre_edit/post_edit)
    - StructureAnalyzer: Detect file structure (sections, headers, versions)
    - DuplicateScanner: Find duplicate/similar content
    - CoherenceValidator: Post-edit coherence validation
    - BestPracticeCompliance: Check against knowledge YAMLs (planned)

AC_START: AC-ENH-101-001
Authority: chat01.md analysis - fragment editing creates duplicates
"""

from cortex.orchestrators.coherence.coherence_models import (
    Change,
    ChangeType,
    CoherenceReport,
    CoherenceStatus,
    DuplicateMatch,
    FileStructure,
    PreEditContext,
    Section,
    SectionType,
    ValidationResult,
    VersionMarker,
)
from cortex.orchestrators.coherence.change_coherence_engine import (
    ChangeCoherenceEngine,
)
from cortex.orchestrators.coherence.structure_analyzer import (
    StructureAnalyzer,
    StructureMetrics,
)
from cortex.orchestrators.coherence.duplicate_scanner import (
    ConsolidationSuggestion,
    DuplicateScanner,
    ScanResult,
)
from cortex.orchestrators.coherence.coherence_validator import (
    CoherenceIssue,
    CoherenceValidator,
    ValidationConfig,
)

__all__ = [
    # Models
    "Change",
    "ChangeType",
    "CoherenceReport",
    "CoherenceStatus",
    "DuplicateMatch",
    "FileStructure",
    "PreEditContext",
    "Section",
    "SectionType",
    "ValidationResult",
    "VersionMarker",
    # Engine
    "ChangeCoherenceEngine",
    # Analyzer
    "StructureAnalyzer",
    "StructureMetrics",
    # Scanner
    "ConsolidationSuggestion",
    "DuplicateScanner",
    "ScanResult",
    # Validator
    "CoherenceIssue",
    "CoherenceValidator",
    "ValidationConfig",
]

# AC_COMPLETE: AC-ENH-101-001 ✅ Package initialization
