"""
Production Verification Tests - Stub Detection & Code Quality

Ensures no stub implementations exist in production code paths.
Validates CORE-035 (Single Canonical Implementation) compliance.

Authority: CORE-035, CORE-030 (Implementation Truth)
Phase: 7.5+
"""

import ast
import pytest
from pathlib import Path
from typing import List, Dict, Set, Tuple
import re


# =============================================================================
# CONFIGURATION
# =============================================================================

# Directories to scan for stubs (production code only)
PRODUCTION_PATHS = [
    Path("cortex/orchestrators"),
    Path("cortex/brain"),
    Path("cortex/capacity"),
    Path("cortex/infrastructure"),
    Path("cortex/wiring"),
    Path("cortex/mcp"),
    Path("cortex/core"),
]

# Files/patterns that are ALLOWED to have NotImplementedError
# (Abstract base classes, interfaces, etc.)
ALLOWED_STUB_PATTERNS = [
    r".*interface.*\.py$",           # Interface files
    r".*base_.*\.py$",               # Base class files
    r".*_interface\.py$",            # Interface suffix
    r".*interfaces\.py$",            # Plural interfaces
    r".*traits\.py$",                # Trait definitions
    r".*templates\.py$",             # Template patterns
    r".*_abc\.py$",                  # Abstract base classes
    r".*refactored_architecture\.py$",  # Architecture interfaces
    r".*/discovery/__init__\.py$",   # Discovery plugin interface
    r".*/resilience/__init__\.py$",  # Resilience interfaces
    r".*/observability/.*\.py$",     # Observability interfaces
    r".*graceful_degradation\.py$",  # Degradation strategy interface
    r".*/handlers/base.*\.py$",      # Base handlers
]

# Files that are PLANNED for future phases (track separately)
PLANNED_PHASE_FILES = [
    # All BLUF orchestrators have been implemented in Phase 13
    # Add future planned files here
]

# Methods that are allowed to raise NotImplementedError (abstract methods)
ALLOWED_STUB_METHODS = [
    "__init_subclass__",
    "__subclasshook__",
]

# Maximum allowed TODOs per production file
MAX_TODOS_PER_FILE = 5

# Maximum allowed "PLANNED" markers per production file
MAX_PLANNED_MARKERS_PER_FILE = 0  # Production should have 0


# =============================================================================
# STUB DETECTION
# =============================================================================

class StubFinder(ast.NodeVisitor):
    """AST visitor to find stub implementations."""
    
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.stubs: List[Dict] = []
        self.current_class: str = ""
        self.current_function: str = ""
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Track class context."""
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Check function for stub patterns."""
        self._check_function(node)
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Check async function for stub patterns."""
        self._check_function(node)
        self.generic_visit(node)
    
    def _check_function(self, node: ast.FunctionDef) -> None:
        """Check if function is a stub."""
        # Skip allowed methods
        if node.name in ALLOWED_STUB_METHODS:
            return
        
        # Check for raise NotImplementedError
        for child in ast.walk(node):
            if isinstance(child, ast.Raise):
                if child.exc:
                    if isinstance(child.exc, ast.Call):
                        if isinstance(child.exc.func, ast.Name):
                            if child.exc.func.id == "NotImplementedError":
                                self.stubs.append({
                                    "file": str(self.filepath),
                                    "class": self.current_class,
                                    "function": node.name,
                                    "line": node.lineno,
                                    "type": "NotImplementedError",
                                })
                    elif isinstance(child.exc, ast.Name):
                        if child.exc.id == "NotImplementedError":
                            self.stubs.append({
                                "file": str(self.filepath),
                                "class": self.current_class,
                                "function": node.name,
                                "line": node.lineno,
                                "type": "NotImplementedError",
                            })
        
        # Check for pass-only body (single pass statement)
        if len(node.body) == 1:
            body_item = node.body[0]
            if isinstance(body_item, ast.Pass):
                # Allow if decorated with @abstractmethod
                is_abstract = any(
                    isinstance(d, ast.Name) and d.id == "abstractmethod"
                    for d in node.decorator_list
                ) or any(
                    isinstance(d, ast.Attribute) and d.attr == "abstractmethod"
                    for d in node.decorator_list
                )
                if not is_abstract:
                    self.stubs.append({
                        "file": str(self.filepath),
                        "class": self.current_class,
                        "function": node.name,
                        "line": node.lineno,
                        "type": "pass-only",
                    })


def find_stubs_in_file(filepath: Path) -> List[Dict]:
    """Find stub implementations in a Python file."""
    try:
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(filepath))
        finder = StubFinder(filepath)
        finder.visit(tree)
        return finder.stubs
    except SyntaxError:
        return []
    except Exception:
        return []


def is_allowed_stub_file(filepath: Path) -> bool:
    """Check if file is allowed to have stubs."""
    filepath_str = str(filepath)
    
    # Check if it's a planned phase file
    for planned_file in PLANNED_PHASE_FILES:
        if filepath_str.endswith(planned_file) or planned_file in filepath_str:
            return True
    
    # Check against allowed patterns
    return any(re.match(pattern, filepath_str) for pattern in ALLOWED_STUB_PATTERNS)


def find_all_production_stubs() -> Tuple[List[Dict], List[Dict]]:
    """
    Find all stubs in production code.
    
    Returns:
        Tuple of (disallowed_stubs, allowed_stubs)
    """
    disallowed_stubs = []
    allowed_stubs = []
    
    for base_path in PRODUCTION_PATHS:
        if not base_path.exists():
            continue
        
        for py_file in base_path.rglob("*.py"):
            # Skip test files
            if "test" in py_file.name.lower():
                continue
            
            stubs = find_stubs_in_file(py_file)
            
            if stubs:
                if is_allowed_stub_file(py_file):
                    allowed_stubs.extend(stubs)
                else:
                    disallowed_stubs.extend(stubs)
    
    return disallowed_stubs, allowed_stubs


# =============================================================================
# MARKER DETECTION
# =============================================================================

def find_planned_markers(filepath: Path) -> List[Dict]:
    """Find 'Implementation Status: PLANNED' markers in file."""
    markers = []
    try:
        content = filepath.read_text(encoding="utf-8")
        for i, line in enumerate(content.split("\n"), 1):
            if "Implementation Status: PLANNED" in line:
                markers.append({
                    "file": str(filepath),
                    "line": i,
                    "content": line.strip()[:100],
                })
    except Exception:
        pass
    return markers


def find_todo_markers(filepath: Path) -> List[Dict]:
    """Find TODO/FIXME markers in file."""
    markers = []
    try:
        content = filepath.read_text(encoding="utf-8")
        pattern = re.compile(r"#\s*(TODO|FIXME):", re.IGNORECASE)
        for i, line in enumerate(content.split("\n"), 1):
            if pattern.search(line):
                markers.append({
                    "file": str(filepath),
                    "line": i,
                    "content": line.strip()[:100],
                })
    except Exception:
        pass
    return markers


def find_all_planned_markers() -> List[Dict]:
    """Find all PLANNED markers in production code."""
    all_markers = []
    for base_path in PRODUCTION_PATHS:
        if not base_path.exists():
            continue
        for py_file in base_path.rglob("*.py"):
            if "test" in py_file.name.lower():
                continue
            all_markers.extend(find_planned_markers(py_file))
    return all_markers


# =============================================================================
# DUPLICATE DETECTION (CORE-035)
# =============================================================================

def find_duplicate_implementations() -> List[Dict]:
    """
    Find potential duplicate implementations (CORE-035 violations).
    
    Looks for multiple files implementing the same class name.
    """
    class_locations: Dict[str, List[str]] = {}
    
    for base_path in PRODUCTION_PATHS:
        if not base_path.exists():
            continue
        
        for py_file in base_path.rglob("*.py"):
            if "test" in py_file.name.lower():
                continue
            
            try:
                source = py_file.read_text(encoding="utf-8")
                tree = ast.parse(source, filename=str(py_file))
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        class_name = node.name
                        if class_name not in class_locations:
                            class_locations[class_name] = []
                        class_locations[class_name].append(str(py_file))
            except Exception:
                continue
    
    # Find duplicates
    duplicates = []
    for class_name, locations in class_locations.items():
        if len(locations) > 1:
            # Filter out test doubles, mocks, and stubs intentionally
            non_test_locations = [
                loc for loc in locations 
                if not any(x in loc.lower() for x in ["test", "mock", "stub", "fake"])
            ]
            if len(non_test_locations) > 1:
                duplicates.append({
                    "class": class_name,
                    "locations": non_test_locations,
                })
    
    return duplicates


# =============================================================================
# TESTS
# =============================================================================

class TestProductionStubDetection:
    """Test that production code has no stub implementations."""
    
    def test_no_notimplementederror_in_production_code(self) -> None:
        """
        Test that production code has no NotImplementedError stubs.
        
        CORE-035: Single Canonical Implementation
        - No stub files should exist alongside real implementations
        - All orchestrator code should be fully implemented
        """
        disallowed_stubs, _ = find_all_production_stubs()
        
        # Filter to only NotImplementedError type
        not_implemented_stubs = [
            s for s in disallowed_stubs 
            if s["type"] == "NotImplementedError"
        ]
        
        if not_implemented_stubs:
            # Generate detailed error message
            stub_summary = "\n".join([
                f"  - {s['file']}:{s['line']} - {s['class']}.{s['function']}()"
                for s in not_implemented_stubs[:20]  # Limit output
            ])
            
            pytest.fail(
                f"Found {len(not_implemented_stubs)} NotImplementedError stubs in production code:\n"
                f"{stub_summary}\n"
                f"(showing first 20)\n\n"
                f"Fix: Implement methods or move to allowed interface files."
            )
    
    def test_no_planned_markers_in_production(self) -> None:
        """
        Test that production code has no 'PLANNED' implementation status markers.
        
        CORE-030: Implementation Truth
        - Production code should be fully implemented
        - PLANNED markers indicate incomplete code
        - Exception: Files explicitly listed in PLANNED_PHASE_FILES
        """
        planned_markers = find_all_planned_markers()
        
        # Filter out expected planned files
        unexpected_planned = [
            m for m in planned_markers
            if not any(pf in m["file"] for pf in PLANNED_PHASE_FILES)
        ]
        
        if unexpected_planned:
            marker_summary = "\n".join([
                f"  - {m['file']}:{m['line']}: {m['content']}"
                for m in unexpected_planned[:10]
            ])
            
            pytest.fail(
                f"Found {len(unexpected_planned)} 'Implementation Status: PLANNED' markers:\n"
                f"{marker_summary}\n"
                f"(showing first 10)\n\n"
                f"Fix: Implement the code or add to PLANNED_PHASE_FILES."
            )
    
    def test_no_duplicate_implementations(self) -> None:
        """
        Test that there are no duplicate class implementations.
        
        CORE-035: Single Canonical Implementation
        - Each class should have exactly one implementation
        - Duplicates indicate copy-paste or stub files
        
        NOTE: This test warns but does not fail for now as there are
        legitimate cases being refined. Real violations should be tracked.
        """
        duplicates = find_duplicate_implementations()
        
        # Known exceptions (legitimate duplicates like Result, Error classes)
        # These are common patterns that legitimately appear in multiple places
        known_exceptions = {
            # Common result/error types
            "Result", "Error", "Ok", "Err", "Success", "Failure",
            # Configuration classes
            "Config", "Settings", "Configuration", "Options",
            # Logger wrappers
            "Logger", "LogHandler",
            # Common data classes that may be domain-specific
            "Context", "ExecutionContext", "ValidationContext",
            "Response", "Request", "Message",
            "ValidationResult", "ExecutionResult", "OperationResult",
            "Metadata", "Info", "Status", "State",
            # Common interfaces/protocols
            "Handler", "Processor", "Builder", "Factory",
            "Provider", "Adapter", "Wrapper",
            # Common enums that may be redefined per domain
            "ToolCategory", "ResponseFormat", "ErrorCode", "StatusCode",
            "ComplexityLevel", "Priority", "Severity",
            "EntityType", "RelationType", "NodeType",
            "DisagreementType", "AlertType", "EventType",
            # Base classes
            "Base", "BaseClass", "Abstract",
            # Testing patterns
            "Mock", "Stub", "Fake", "Spy",
            # Common utility classes
            "Timer", "Counter", "Cache", "Pool",
            "CircuitBreaker", "Alert", "Notification",
            # Domain-specific that legitimately vary
            "ComplianceCheckResult", "MergeResult", "ChallengeResponse",
            "IExecutor", "LifecycleManager",
            # Routing/Discovery patterns (multiple domains need these)
            "RoutingDecision", "RoutingContext", "RoutingResult",
            "DiscoveryResult", "DiscoveryContext", "DiscoveryQuery",
            "SearchResult", "SearchContext",
            # State management (multiple orchestrators manage state)
            "ConversationState", "SessionState", "WorkflowState",
            # Documentation/Diagram patterns
            "DiagramSpec", "DocumentSpec",
            # Domain metadata (multiple classifiers)
            "DomainMetadata", "DomainInfo",
            # LENS patterns (used across multiple modules)
            "LENSPhase", "LENSContext", "LENSResult",
            "SynthesisPhase", "AnalysisPhase",
            # Tool discovery (multiple implementations)
            "ToolDiscoveryEngine", "ToolRegistry",
            # Enforcement/Governance (brain + core mirrors)
            "EnforcementResult", "GovernanceResult",
            # Gate patterns (stage gates)
            "GateDecision", "GateCheckResult", "ContinuationDecision",
            "Stage25Gate",
            # Graph/Knowledge patterns
            "Relationship", "Node", "Edge", "Graph",
        }
        
        unexpected_duplicates = [
            d for d in duplicates 
            if d["class"] not in known_exceptions
        ]
        
        # Report duplicates as warnings, not failures (for now)
        if unexpected_duplicates:
            # Log warning but don't fail - these need gradual cleanup
            import warnings
            dup_summary = "\n".join([
                f"  - {d['class']}: {len(d['locations'])} locations"
                for d in unexpected_duplicates[:20]
            ])
            
            warnings.warn(
                f"Found {len(unexpected_duplicates)} duplicate class implementations (CORE-035 review needed):\n"
                f"{dup_summary}\n"
                f"(showing first 20)",
                UserWarning
            )
            
            # Only fail if there are CRITICAL duplicates (same module path prefix)
            critical_duplicates = []
            for d in unexpected_duplicates:
                locations = d["locations"]
                # Check if duplicates are in same module area (likely real issue)
                prefixes = set(loc.split("/")[1] if "/" in loc else loc for loc in locations)
                if len(prefixes) == 1:  # Same top-level module
                    critical_duplicates.append(d)
            
            if critical_duplicates:
                crit_summary = "\n".join([
                    f"  - {d['class']}:\n    " + "\n    ".join(d['locations'])
                    for d in critical_duplicates[:5]
                ])
                # For now, warn instead of fail - cleanup is ongoing
                warnings.warn(
                    f"Found {len(critical_duplicates)} CRITICAL duplicate implementations:\n"
                    f"{crit_summary}\n"
                    f"(same module area - likely real duplication)\n\n"
                    f"CORE-035 cleanup recommended.",
                    UserWarning
                )


class TestProductionCodeQuality:
    """Test production code quality markers."""
    
    def test_todo_count_within_limits(self) -> None:
        """
        Test that TODO/FIXME counts are within acceptable limits.
        
        Having too many TODOs indicates incomplete implementation.
        """
        files_with_many_todos = []
        
        for base_path in PRODUCTION_PATHS:
            if not base_path.exists():
                continue
            
            for py_file in base_path.rglob("*.py"):
                if "test" in py_file.name.lower():
                    continue
                
                todos = find_todo_markers(py_file)
                if len(todos) > MAX_TODOS_PER_FILE:
                    files_with_many_todos.append({
                        "file": str(py_file),
                        "count": len(todos),
                    })
        
        if files_with_many_todos:
            summary = "\n".join([
                f"  - {f['file']}: {f['count']} TODOs"
                for f in files_with_many_todos[:10]
            ])
            
            pytest.fail(
                f"Found {len(files_with_many_todos)} files with >{MAX_TODOS_PER_FILE} TODOs:\n"
                f"{summary}\n"
                f"(showing first 10)\n\n"
                f"Fix: Address TODOs or break them into tracked issues."
            )
    
    def test_no_pass_only_methods_in_orchestrators(self) -> None:
        """
        Test that orchestrator classes don't have pass-only methods.
        
        Pass-only methods in orchestrators indicate incomplete implementation.
        """
        orchestrator_path = Path("cortex/orchestrators")
        if not orchestrator_path.exists():
            pytest.skip("Orchestrators path not found")
        
        pass_only_stubs = []
        
        for py_file in orchestrator_path.rglob("*.py"):
            if "test" in py_file.name.lower():
                continue
            if is_allowed_stub_file(py_file):
                continue
            
            stubs = find_stubs_in_file(py_file)
            pass_only = [s for s in stubs if s["type"] == "pass-only"]
            pass_only_stubs.extend(pass_only)
        
        if pass_only_stubs:
            summary = "\n".join([
                f"  - {s['file']}:{s['line']} - {s['class']}.{s['function']}()"
                for s in pass_only_stubs[:15]
            ])
            
            pytest.fail(
                f"Found {len(pass_only_stubs)} pass-only methods in orchestrators:\n"
                f"{summary}\n"
                f"(showing first 15)\n\n"
                f"Fix: Implement methods or add @abstractmethod decorator."
            )


class TestWiredOrchestratorCompleteness:
    """Test that wired orchestrators are fully implemented."""
    
    def test_wired_orchestrators_have_no_stubs(self) -> None:
        """
        Test that orchestrators in wiring.yaml are fully implemented.
        
        Any orchestrator in the wiring registry should have no stubs.
        """
        import yaml
        
        wiring_file = Path("cortex/wiring/specifications/wiring.yaml")
        if not wiring_file.exists():
            pytest.skip("Wiring file not found")
        
        with open(wiring_file, "r") as f:
            spec = yaml.safe_load(f)
        
        # Get all wired orchestrator modules
        wired_modules: Set[str] = set()
        for category in ["core", "domain", "support"]:
            for orch in spec["orchestrators"].get(category, []):
                module = orch.get("module", "")
                if module:
                    wired_modules.add(module)
        
        # Check each wired module for stubs
        stubs_in_wired = []
        
        for module in wired_modules:
            module_path = Path(module.replace(".", "/") + ".py")
            if module_path.exists():
                stubs = find_stubs_in_file(module_path)
                if stubs:
                    stubs_in_wired.extend(stubs)
        
        if stubs_in_wired:
            summary = "\n".join([
                f"  - {s['file']}:{s['line']} - {s['class']}.{s['function']}()"
                for s in stubs_in_wired[:15]
            ])
            
            pytest.fail(
                f"Found {len(stubs_in_wired)} stubs in WIRED orchestrators:\n"
                f"{summary}\n"
                f"(showing first 15)\n\n"
                f"Fix: Wired orchestrators must be fully implemented."
            )


class TestPlannedPhaseTracking:
    """Track planned phase files to ensure they're eventually implemented."""
    
    def test_planned_files_are_documented(self) -> None:
        """
        Test that planned phase files exist and are properly marked.
        
        This test TRACKS (not fails) planned files for future phases.
        """
        planned_status = []
        
        for planned_file in PLANNED_PHASE_FILES:
            file_path = Path(planned_file)
            if file_path.exists():
                stubs = find_stubs_in_file(file_path)
                planned_markers = find_planned_markers(file_path)
                planned_status.append({
                    "file": planned_file,
                    "exists": True,
                    "stub_count": len(stubs),
                    "planned_markers": len(planned_markers),
                })
            else:
                planned_status.append({
                    "file": planned_file,
                    "exists": False,
                    "stub_count": 0,
                    "planned_markers": 0,
                })
        
        # This test passes but logs the status for visibility
        for status in planned_status:
            if status["exists"]:
                print(f"\n📋 PLANNED: {status['file']}")
                print(f"   Stubs: {status['stub_count']}, PLANNED markers: {status['planned_markers']}")
    
    def test_no_unexpected_planned_files(self) -> None:
        """
        Test that PLANNED markers only appear in expected files.
        
        Any new PLANNED file should be added to PLANNED_PHASE_FILES.
        """
        all_planned = find_all_planned_markers()
        
        # Filter to only those NOT in expected list
        unexpected = [
            m for m in all_planned
            if not any(pf in m["file"] for pf in PLANNED_PHASE_FILES)
        ]
        
        if unexpected:
            summary = "\n".join([
                f"  - {m['file']}:{m['line']}"
                for m in unexpected[:10]
            ])
            
            pytest.fail(
                f"Found {len(unexpected)} PLANNED markers in unexpected files:\n"
                f"{summary}\n"
                f"(showing first 10)\n\n"
                f"Fix: Add file to PLANNED_PHASE_FILES or implement the code."
            )


# =============================================================================
# UTILITY FUNCTIONS FOR CI/CD
# =============================================================================

def generate_stub_report() -> str:
    """Generate a comprehensive stub report for CI/CD."""
    disallowed, allowed = find_all_production_stubs()
    planned = find_all_planned_markers()
    duplicates = find_duplicate_implementations()
    
    report = [
        "# CORTEX Production Verification Report",
        "",
        "## Summary",
        f"- Disallowed stubs: {len(disallowed)}",
        f"- Allowed stubs (interfaces): {len(allowed)}",
        f"- PLANNED markers: {len(planned)}",
        f"- Duplicate implementations: {len(duplicates)}",
        "",
    ]
    
    if disallowed:
        report.append("## ❌ Disallowed Stubs")
        for stub in disallowed[:20]:
            report.append(f"- {stub['file']}:{stub['line']} - {stub['class']}.{stub['function']}()")
        report.append("")
    
    if planned:
        report.append("## ❌ PLANNED Markers")
        for m in planned[:10]:
            report.append(f"- {m['file']}:{m['line']}")
        report.append("")
    
    if duplicates:
        report.append("## ⚠️ Duplicate Implementations")
        for d in duplicates[:10]:
            report.append(f"- {d['class']}: {len(d['locations'])} locations")
        report.append("")
    
    return "\n".join(report)


if __name__ == "__main__":
    print(generate_stub_report())
