# CORTEX 4.0 Adapter Development Guide

**Version:** 1.0  
**Author:** Asif Hussain  
**Created:** December 19, 2025  
**Status:** 🟢 ACTIVE  
**Audience:** CORTEX Contributors, Enterprise Users, Custom Adapter Developers

---

## 🎯 Purpose

This guide explains how to create custom adapters for CORTEX 4.0's Universal Adapter System. Adapters enable CORTEX to work with ANY tech stack by implementing standardized interfaces.

**Architecture Reference:** See `cortex-brain/documents/architecture/TECH-STACK-AGNOSTIC-ARCHITECTURE.md`

---

## 🏗️ Adapter Types

CORTEX 4.0 supports 4 adapter categories:

| Adapter Type | Interface | Purpose | Examples |
|--------------|-----------|---------|----------|
| **Test Framework** | `ITestFrameworkAdapter` | Execute tests, parse results, collect coverage | xUnit, pytest, JUnit, Jest, GoTest, RSpec |
| **Logging** | `ILoggingAdapter` | Parse production logs, extract errors, sanitize PII | NLog, Serilog, log4j, Winston, zap, logrus |
| **Feature Flags** | `IFeatureFlagAdapter` | Initialize provider, evaluate flags, track events | LaunchDarkly, Unleash, ConfigCat, Split.io |
| **Build Tools** | `IBuildToolAdapter` | Build, test, publish artifacts | dotnet, maven, gradle, npm, yarn, cargo |

---

## 📋 Development Workflow

### Step 1: Choose Your Adapter Type

Determine which interface your adapter will implement. Each interface is a Python Protocol class defining required methods.

**Example:** Creating a NUnit adapter (Test Framework)

### Step 2: Implement the Interface

All adapters must implement their interface's required methods. CORTEX uses structural typing (Protocol classes), so inheritance is optional but recommended for clarity.

#### Example: ITestFrameworkAdapter Implementation

```python
# src/adapters/test_frameworks/nunit_adapter.py
from typing import Dict, List, Optional, Any
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

from src.adapters.interfaces.test_framework_adapter import ITestFrameworkAdapter

class NUnitAdapter(ITestFrameworkAdapter):
    """
    NUnit test framework adapter for C#/.NET projects.
    Executes tests via nunit3-console.exe and parses XML results.
    """
    
    # Adapter metadata (required for registration)
    name = "nunit"
    version = "1.0.0"
    supported_languages = ["csharp", "dotnet"]
    configuration_schema = {
        "nunit_console_path": {
            "type": "string",
            "description": "Path to nunit3-console.exe",
            "default": "nunit3-console.exe"
        },
        "test_assembly_pattern": {
            "type": "string",
            "description": "Pattern to find test assemblies",
            "default": "**/*Tests.dll"
        },
        "results_format": {
            "type": "string",
            "description": "NUnit result format (nunit3 or nunit2)",
            "default": "nunit3"
        }
    }
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize NUnit adapter with configuration.
        
        Args:
            config: Configuration dict from cortex.config.json tech_stack section
        """
        self.nunit_console = config.get("nunit_console_path", "nunit3-console.exe")
        self.test_pattern = config.get("test_assembly_pattern", "**/*Tests.dll")
        self.results_format = config.get("results_format", "nunit3")
        self.config = config
    
    def execute_tests(
        self,
        project_path: str,
        test_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute NUnit tests and return standardized results.
        
        Args:
            project_path: Path to project directory or test assembly
            test_filter: Optional test filter (e.g., "namespace.ClassName.MethodName")
        
        Returns:
            Standardized test results dict:
            {
                "total": 45,
                "passed": 42,
                "failed": 2,
                "skipped": 1,
                "duration_ms": 3500,
                "tests": [
                    {
                        "name": "Test_UserLogin_Success",
                        "status": "passed",
                        "duration_ms": 250,
                        "error_message": null,
                        "stack_trace": null
                    },
                    ...
                ]
            }
        """
        # Build NUnit command
        cmd = [self.nunit_console]
        
        # Find test assemblies matching pattern
        project_dir = Path(project_path)
        if project_dir.is_file() and project_dir.suffix == ".dll":
            cmd.append(str(project_dir))
        else:
            # Search for test assemblies
            test_assemblies = list(project_dir.glob(self.test_pattern))
            if not test_assemblies:
                raise ValueError(f"No test assemblies found matching pattern: {self.test_pattern}")
            cmd.extend([str(a) for a in test_assemblies])
        
        # Add test filter if provided
        if test_filter:
            cmd.extend(["--where", f"test =~ /{test_filter}/"])
        
        # Add result file path
        result_file = project_dir / "nunit-results.xml"
        cmd.extend([f"--result={result_file};format={self.results_format}"])
        
        # Execute tests
        try:
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(project_dir),
                timeout=self.config.get("timeout", 600)  # 10 min default
            )
        except subprocess.TimeoutExpired:
            return {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "duration_ms": 0,
                "error": "Test execution timed out",
                "tests": []
            }
        
        # Parse results XML
        return self._parse_nunit_xml(result_file)
    
    def parse_results(
        self,
        results_file_path: str
    ) -> Dict[str, Any]:
        """
        Parse NUnit results from XML file.
        
        Args:
            results_file_path: Path to nunit-results.xml
        
        Returns:
            Standardized test results dict (same format as execute_tests)
        """
        return self._parse_nunit_xml(results_file_path)
    
    def get_coverage(
        self,
        project_path: str,
        coverage_file_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get code coverage metrics.
        
        Args:
            project_path: Path to project directory
            coverage_file_path: Optional path to coverage file (e.g., coverage.xml from OpenCover)
        
        Returns:
            Standardized coverage dict:
            {
                "line_coverage": 85.5,
                "branch_coverage": 78.3,
                "files": [
                    {
                        "path": "src/PaymentProcessor.cs",
                        "line_coverage": 90.0,
                        "uncovered_lines": [45, 67, 89]
                    },
                    ...
                ]
            }
        """
        # NUnit doesn't have built-in coverage, needs OpenCover or similar
        if not coverage_file_path:
            # Look for common coverage files
            project_dir = Path(project_path)
            coverage_candidates = [
                project_dir / "coverage.xml",
                project_dir / "opencover.xml",
                project_dir / "coverage" / "coverage.xml"
            ]
            coverage_file_path = next(
                (str(f) for f in coverage_candidates if f.exists()),
                None
            )
        
        if not coverage_file_path:
            return {
                "line_coverage": 0.0,
                "branch_coverage": 0.0,
                "files": [],
                "warning": "No coverage file found. Run tests with OpenCover or similar."
            }
        
        # Parse OpenCover XML format
        return self._parse_opencover_xml(coverage_file_path)
    
    def _parse_nunit_xml(self, xml_path: str) -> Dict[str, Any]:
        """Parse NUnit XML results into standardized format."""
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # NUnit 3 format
        if root.tag == "test-run":
            total = int(root.get("total", 0))
            passed = int(root.get("passed", 0))
            failed = int(root.get("failed", 0))
            skipped = int(root.get("skipped", 0)) + int(root.get("inconclusive", 0))
            duration = float(root.get("duration", 0)) * 1000  # Convert to ms
            
            tests = []
            for test_case in root.findall(".//test-case"):
                tests.append({
                    "name": test_case.get("fullname"),
                    "status": self._map_nunit_status(test_case.get("result")),
                    "duration_ms": float(test_case.get("duration", 0)) * 1000,
                    "error_message": self._get_error_message(test_case),
                    "stack_trace": self._get_stack_trace(test_case)
                })
            
            return {
                "total": total,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "duration_ms": int(duration),
                "tests": tests
            }
        
        # NUnit 2 format (legacy)
        elif root.tag == "test-results":
            total = int(root.get("total", 0))
            failures = int(root.get("failures", 0))
            not_run = int(root.get("not-run", 0))
            passed = total - failures - not_run
            
            # ... similar parsing logic ...
            
            return {
                "total": total,
                "passed": passed,
                "failed": failures,
                "skipped": not_run,
                "duration_ms": 0,  # NUnit 2 doesn't have duration in root
                "tests": []  # Parse test-case elements
            }
        
        else:
            raise ValueError(f"Unknown NUnit XML format: {root.tag}")
    
    def _map_nunit_status(self, result: str) -> str:
        """Map NUnit result to standardized status."""
        mapping = {
            "Passed": "passed",
            "Failed": "failed",
            "Skipped": "skipped",
            "Inconclusive": "skipped",
            "Ignored": "skipped"
        }
        return mapping.get(result, "unknown")
    
    def _get_error_message(self, test_case: ET.Element) -> Optional[str]:
        """Extract error message from test-case."""
        failure = test_case.find("failure")
        if failure is not None:
            message = failure.find("message")
            return message.text if message is not None else None
        return None
    
    def _get_stack_trace(self, test_case: ET.Element) -> Optional[str]:
        """Extract stack trace from test-case."""
        failure = test_case.find("failure")
        if failure is not None:
            stack_trace = failure.find("stack-trace")
            return stack_trace.text if stack_trace is not None else None
        return None
    
    def _parse_opencover_xml(self, xml_path: str) -> Dict[str, Any]:
        """Parse OpenCover XML into standardized coverage format."""
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # Calculate overall coverage
        summary = root.find(".//Summary")
        if summary is None:
            return {"line_coverage": 0.0, "branch_coverage": 0.0, "files": []}
        
        line_coverage = (
            float(summary.get("visitedSequencePoints", 0)) /
            float(summary.get("numSequencePoints", 1)) * 100
        )
        branch_coverage = (
            float(summary.get("visitedBranchPoints", 0)) /
            float(summary.get("numBranchPoints", 1)) * 100
        )
        
        # Parse file-level coverage
        files = []
        for file_elem in root.findall(".//File"):
            file_path = file_elem.get("fullPath")
            sequence_points = file_elem.findall(".//SequencePoint")
            
            if not sequence_points:
                continue
            
            visited = sum(1 for sp in sequence_points if int(sp.get("vc", 0)) > 0)
            total = len(sequence_points)
            uncovered = [
                int(sp.get("sl"))
                for sp in sequence_points
                if int(sp.get("vc", 0)) == 0
            ]
            
            files.append({
                "path": file_path,
                "line_coverage": (visited / total * 100) if total > 0 else 0.0,
                "uncovered_lines": sorted(uncovered)
            })
        
        return {
            "line_coverage": round(line_coverage, 2),
            "branch_coverage": round(branch_coverage, 2),
            "files": files
        }
```

### Step 3: Create Tests

Every adapter MUST have comprehensive tests. CORTEX enforces 90%+ coverage.

```python
# tests/adapters/test_frameworks/test_nunit_adapter.py
import pytest
from pathlib import Path
from src.adapters.test_frameworks.nunit_adapter import NUnitAdapter

@pytest.fixture
def nunit_config():
    """Default NUnit configuration for testing."""
    return {
        "nunit_console_path": "nunit3-console.exe",
        "test_assembly_pattern": "**/*Tests.dll",
        "results_format": "nunit3",
        "timeout": 600
    }

@pytest.fixture
def nunit_adapter(nunit_config):
    """NUnit adapter instance for testing."""
    return NUnitAdapter(nunit_config)

def test_nunit_adapter_initialization(nunit_adapter, nunit_config):
    """Test NUnit adapter initializes with correct configuration."""
    assert nunit_adapter.name == "nunit"
    assert nunit_adapter.version == "1.0.0"
    assert "csharp" in nunit_adapter.supported_languages
    assert nunit_adapter.nunit_console == nunit_config["nunit_console_path"]

def test_parse_nunit3_xml_success(nunit_adapter, tmp_path):
    """Test parsing NUnit 3 XML with all tests passing."""
    xml_content = """<?xml version="1.0" encoding="utf-8"?>
    <test-run id="0" result="Passed" total="3" passed="3" failed="0" skipped="0" duration="1.234">
        <test-case id="1" name="Test_UserLogin_Success" fullname="AuthTests.Test_UserLogin_Success" result="Passed" duration="0.456">
        </test-case>
        <test-case id="2" name="Test_UserLogin_InvalidPassword" fullname="AuthTests.Test_UserLogin_InvalidPassword" result="Passed" duration="0.389">
        </test-case>
        <test-case id="3" name="Test_UserLogout" fullname="AuthTests.Test_UserLogout" result="Passed" duration="0.389">
        </test-case>
    </test-run>
    """
    
    xml_file = tmp_path / "nunit-results.xml"
    xml_file.write_text(xml_content)
    
    results = nunit_adapter.parse_results(str(xml_file))
    
    assert results["total"] == 3
    assert results["passed"] == 3
    assert results["failed"] == 0
    assert results["skipped"] == 0
    assert results["duration_ms"] == 1234
    assert len(results["tests"]) == 3
    assert all(test["status"] == "passed" for test in results["tests"])

def test_parse_nunit3_xml_with_failures(nunit_adapter, tmp_path):
    """Test parsing NUnit 3 XML with test failures."""
    xml_content = """<?xml version="1.0" encoding="utf-8"?>
    <test-run id="0" result="Failed" total="2" passed="1" failed="1" skipped="0" duration="0.789">
        <test-case id="1" name="Test_Success" fullname="Tests.Test_Success" result="Passed" duration="0.123">
        </test-case>
        <test-case id="2" name="Test_Failure" fullname="Tests.Test_Failure" result="Failed" duration="0.666">
            <failure>
                <message>Expected: 42, But was: 0</message>
                <stack-trace>   at Tests.Test_Failure() in C:\\Code\\Tests.cs:line 45</stack-trace>
            </failure>
        </test-case>
    </test-run>
    """
    
    xml_file = tmp_path / "nunit-results.xml"
    xml_file.write_text(xml_content)
    
    results = nunit_adapter.parse_results(str(xml_file))
    
    assert results["total"] == 2
    assert results["passed"] == 1
    assert results["failed"] == 1
    assert results["tests"][1]["status"] == "failed"
    assert "Expected: 42" in results["tests"][1]["error_message"]
    assert "line 45" in results["tests"][1]["stack_trace"]

def test_get_coverage_with_opencover(nunit_adapter, tmp_path):
    """Test coverage parsing from OpenCover XML."""
    xml_content = """<?xml version="1.0" encoding="utf-8"?>
    <CoverageSession>
        <Summary numSequencePoints="100" visitedSequencePoints="85" numBranchPoints="40" visitedBranchPoints="30" />
        <Modules>
            <Module>
                <Files>
                    <File fullPath="C:\\Code\\PaymentProcessor.cs" />
                </Files>
                <Classes>
                    <Class>
                        <Methods>
                            <Method>
                                <SequencePoints>
                                    <SequencePoint vc="10" sl="45" />
                                    <SequencePoint vc="0" sl="67" />
                                    <SequencePoint vc="5" sl="89" />
                                </SequencePoints>
                            </Method>
                        </Methods>
                    </Class>
                </Classes>
            </Module>
        </Modules>
    </CoverageSession>
    """
    
    coverage_file = tmp_path / "coverage.xml"
    coverage_file.write_text(xml_content)
    
    coverage = nunit_adapter.get_coverage(str(tmp_path), str(coverage_file))
    
    assert coverage["line_coverage"] == 85.0
    assert coverage["branch_coverage"] == 75.0
    assert len(coverage["files"]) == 1
    assert 67 in coverage["files"][0]["uncovered_lines"]

def test_nunit_adapter_metadata_schema(nunit_adapter):
    """Test adapter metadata schema is complete."""
    schema = nunit_adapter.configuration_schema
    
    assert "nunit_console_path" in schema
    assert "test_assembly_pattern" in schema
    assert "results_format" in schema
    assert all("type" in v and "description" in v for v in schema.values())
```

### Step 4: Register with AdapterRegistry

The AdapterRegistry auto-discovers adapters from the `src/adapters/` directory structure. Place your adapter in the correct subdirectory:

```
src/adapters/
├── interfaces/               # Protocol classes (don't register)
│   ├── test_framework_adapter.py
│   ├── logging_adapter.py
│   ├── feature_flag_adapter.py
│   └── build_tool_adapter.py
├── test_frameworks/          # ITestFrameworkAdapter implementations
│   ├── xunit_adapter.py
│   ├── pytest_adapter.py
│   ├── junit_adapter.py
│   ├── nunit_adapter.py      ← Your new adapter
│   └── ...
├── logging/                  # ILoggingAdapter implementations
├── feature_flags/            # IFeatureFlagAdapter implementations
└── build_tools/              # IBuildToolAdapter implementations
```

**Auto-Discovery Rules:**
- Adapter classes must have `name`, `version`, `supported_languages`, `configuration_schema` attributes
- Adapter classes must implement the appropriate interface (duck typing via Protocol)
- Adapter module filename must end with `_adapter.py`
- AdapterRegistry scans `src/adapters/` on startup and validates all found adapters

**Manual Registration (Optional):**

```python
# If you need to register an adapter from outside src/adapters/
from src.core.adapter_registry import AdapterRegistry
from my_custom_module.my_adapter import MyCustomAdapter

registry = AdapterRegistry()
registry.register_adapter(
    adapter_type="test_framework",
    adapter_class=MyCustomAdapter
)
```

### Step 5: Add Configuration Example

Update `cortex.config.template.json` to show users how to configure your adapter:

```json
{
  "tech_stack": {
    "language": "csharp",
    "test_framework": "nunit",
    "test_framework_config": {
      "nunit_console_path": "C:\\Program Files\\NUnit\\nunit3-console.exe",
      "test_assembly_pattern": "**/*Tests.dll",
      "results_format": "nunit3",
      "timeout": 600
    },
    "build_tool": "dotnet",
    "logging_framework": "nlog",
    "feature_flag_provider": "launchdarkly"
  }
}
```

---

## 📚 Interface Specifications

### ITestFrameworkAdapter

```python
from typing import Dict, List, Optional, Any, Protocol

class ITestFrameworkAdapter(Protocol):
    """Universal interface for test framework execution and result parsing."""
    
    # Metadata (required)
    name: str                          # Adapter name (e.g., "pytest", "xunit")
    version: str                       # Adapter version (e.g., "1.0.0")
    supported_languages: List[str]     # Languages supported (e.g., ["python", "python3"])
    configuration_schema: Dict[str, Any]  # JSON schema for config validation
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize adapter with configuration from cortex.config.json.
        
        Args:
            config: Configuration dict from tech_stack.test_framework_config
        """
        ...
    
    def execute_tests(
        self,
        project_path: str,
        test_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute tests and return standardized results.
        
        Args:
            project_path: Path to project directory or test file
            test_filter: Optional filter (e.g., "test_user_login" or "TestClass")
        
        Returns:
            {
                "total": 45,
                "passed": 42,
                "failed": 2,
                "skipped": 1,
                "duration_ms": 3500,
                "tests": [
                    {
                        "name": "test_user_login",
                        "status": "passed",
                        "duration_ms": 250,
                        "error_message": None,
                        "stack_trace": None
                    },
                    ...
                ]
            }
        """
        ...
    
    def parse_results(
        self,
        results_file_path: str
    ) -> Dict[str, Any]:
        """
        Parse test results from file (same return format as execute_tests).
        
        Args:
            results_file_path: Path to test results file (XML, JSON, etc.)
        
        Returns:
            Same dict format as execute_tests
        """
        ...
    
    def get_coverage(
        self,
        project_path: str,
        coverage_file_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get code coverage metrics.
        
        Args:
            project_path: Path to project directory
            coverage_file_path: Optional path to coverage file
        
        Returns:
            {
                "line_coverage": 85.5,
                "branch_coverage": 78.3,
                "files": [
                    {
                        "path": "src/user.py",
                        "line_coverage": 90.0,
                        "uncovered_lines": [45, 67, 89]
                    },
                    ...
                ]
            }
        """
        ...
```

### ILoggingAdapter

```python
from typing import Dict, List, Optional, Any, Protocol
from datetime import datetime

class ILoggingAdapter(Protocol):
    """Universal interface for production log parsing and analysis."""
    
    # Metadata (required)
    name: str
    version: str
    supported_languages: List[str]
    configuration_schema: Dict[str, Any]
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize adapter with configuration from cortex.config.json.
        
        Args:
            config: Configuration dict from tech_stack.logging_framework_config
        """
        ...
    
    def parse_logs(
        self,
        log_file_path: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        level_filter: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Parse log file and extract structured log entries.
        
        Args:
            log_file_path: Path to log file
            start_time: Optional start time filter
            end_time: Optional end time filter
            level_filter: Optional log levels to include (e.g., ["ERROR", "FATAL"])
        
        Returns:
            List of log entries:
            [
                {
                    "timestamp": "2025-12-19T10:30:45.123Z",
                    "level": "ERROR",
                    "logger": "PaymentService",
                    "message": "Payment processing failed",
                    "correlation_id": "abc-123",
                    "exception": {
                        "type": "NullReferenceException",
                        "message": "Object reference not set to an instance",
                        "stack_trace": "at PaymentProcessor.Process()\\n..."
                    },
                    "properties": {
                        "user_id": "[REDACTED]",
                        "transaction_id": "txn-456"
                    }
                },
                ...
            ]
        """
        ...
    
    def extract_errors(
        self,
        log_file_path: str,
        error_level: str = "ERROR"
    ) -> List[Dict[str, Any]]:
        """
        Extract only error-level logs (convenience method).
        
        Args:
            log_file_path: Path to log file
            error_level: Minimum log level ("ERROR", "FATAL", etc.)
        
        Returns:
            List of error log entries (same format as parse_logs)
        """
        ...
    
    def sanitize_pii(
        self,
        log_entry: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Remove personally identifiable information from log entry.
        
        Args:
            log_entry: Log entry dict from parse_logs
        
        Returns:
            Sanitized log entry with PII replaced:
            - Emails → [EMAIL]
            - Credit cards → [CREDIT_CARD]
            - Phone numbers → [PHONE]
            - IP addresses → [IP_ADDRESS]
            - API keys → [API_KEY]
        """
        ...
```

### IFeatureFlagAdapter

```python
from typing import Dict, List, Optional, Any, Protocol

class IFeatureFlagAdapter(Protocol):
    """Universal interface for feature flag providers."""
    
    # Metadata (required)
    name: str
    version: str
    supported_languages: List[str]
    configuration_schema: Dict[str, Any]
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize adapter with configuration from cortex.config.json.
        
        Args:
            config: Configuration dict from tech_stack.feature_flag_config
        """
        ...
    
    def initialize(self) -> bool:
        """
        Initialize connection to feature flag provider.
        
        Returns:
            True if initialization successful, False otherwise
        """
        ...
    
    def get_flag(
        self,
        flag_key: str,
        default: bool = False,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Evaluate boolean feature flag.
        
        Args:
            flag_key: Feature flag key/name
            default: Default value if flag not found
            context: Optional context (user, environment, etc.)
        
        Returns:
            Boolean flag value
        """
        ...
    
    def get_variant(
        self,
        flag_key: str,
        default: str = "control",
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Get multivariate feature flag value.
        
        Args:
            flag_key: Feature flag key/name
            default: Default variant if flag not found
            context: Optional context
        
        Returns:
            Variant name (e.g., "treatment-a", "control")
        """
        ...
    
    def track_event(
        self,
        event_name: str,
        context: Dict[str, Any]
    ) -> None:
        """
        Send analytics event to feature flag provider.
        
        Args:
            event_name: Event name (e.g., "feature-used")
            context: Event context and properties
        """
        ...
    
    def get_all_flags(
        self,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, bool]:
        """
        Get all feature flags and their values.
        
        Args:
            context: Optional context
        
        Returns:
            Dict mapping flag keys to boolean values
        """
        ...
```

### IBuildToolAdapter

```python
from typing import Dict, List, Optional, Any, Protocol

class IBuildToolAdapter(Protocol):
    """Universal interface for build tool execution."""
    
    # Metadata (required)
    name: str
    version: str
    supported_languages: List[str]
    configuration_schema: Dict[str, Any]
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize adapter with configuration from cortex.config.json.
        
        Args:
            config: Configuration dict from tech_stack.build_tool_config
        """
        ...
    
    def build(
        self,
        project_path: str,
        configuration: str = "Release"
    ) -> Dict[str, Any]:
        """
        Build project.
        
        Args:
            project_path: Path to project directory
            configuration: Build configuration ("Debug", "Release", etc.)
        
        Returns:
            {
                "success": True,
                "duration_ms": 5000,
                "output_path": "bin/Release/MyApp.dll",
                "warnings": 3,
                "errors": 0,
                "log": "Build output..."
            }
        """
        ...
    
    def test(
        self,
        project_path: str,
        test_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run tests (delegates to ITestFrameworkAdapter if available).
        
        Args:
            project_path: Path to project directory
            test_filter: Optional test filter
        
        Returns:
            Same format as ITestFrameworkAdapter.execute_tests
        """
        ...
    
    def publish(
        self,
        project_path: str,
        output_path: str,
        configuration: str = "Release"
    ) -> Dict[str, Any]:
        """
        Publish/package project for deployment.
        
        Args:
            project_path: Path to project directory
            output_path: Path to publish artifacts
            configuration: Build configuration
        
        Returns:
            {
                "success": True,
                "duration_ms": 3000,
                "artifacts": [
                    "publish/MyApp.dll",
                    "publish/appsettings.json"
                ],
                "size_bytes": 1048576
            }
        """
        ...
    
    def clean(
        self,
        project_path: str
    ) -> Dict[str, Any]:
        """
        Clean build artifacts.
        
        Args:
            project_path: Path to project directory
        
        Returns:
            {
                "success": True,
                "files_deleted": 45,
                "space_freed_bytes": 5242880
            }
        """
        ...
```

---

## ✅ Testing Requirements

All adapters MUST meet these testing requirements for acceptance:

1. **Unit Test Coverage:** ≥90% line coverage
2. **Test Count:** Minimum 5 tests per adapter
3. **Required Test Cases:**
   - Initialization with valid config
   - Initialization with invalid config (should raise error)
   - Success path (happy path)
   - Failure path (error handling)
   - Edge cases (empty input, malformed data, timeouts)
4. **Integration Test:** At least 1 integration test with real tool (if possible) or realistic mock
5. **Configuration Validation:** Test that configuration_schema is complete and accurate

**Test Template:**

```python
# tests/adapters/{category}/test_{name}_adapter.py
import pytest
from src.adapters.{category}.{name}_adapter import {ClassName}Adapter

@pytest.fixture
def config():
    """Default configuration for testing."""
    return {...}

@pytest.fixture
def adapter(config):
    """Adapter instance for testing."""
    return {ClassName}Adapter(config)

def test_initialization_success(adapter, config):
    """Test adapter initializes with valid configuration."""
    assert adapter.name == "{name}"
    assert adapter.version
    assert len(adapter.supported_languages) > 0

def test_initialization_invalid_config():
    """Test adapter raises error with invalid configuration."""
    with pytest.raises(ValueError):
        {ClassName}Adapter({})

def test_success_path(adapter):
    """Test adapter success path with valid input."""
    # Arrange
    ...
    
    # Act
    result = adapter.some_method(...)
    
    # Assert
    assert result["success"] == True
    assert ...

def test_failure_path(adapter):
    """Test adapter handles errors gracefully."""
    # Arrange: Invalid input
    ...
    
    # Act
    result = adapter.some_method(...)
    
    # Assert
    assert result["success"] == False
    assert "error" in result

def test_edge_cases(adapter):
    """Test adapter handles edge cases (empty input, malformed data)."""
    # Empty input
    result = adapter.some_method("")
    assert ...
    
    # Malformed data
    result = adapter.some_method("garbage")
    assert ...
```

---

## 📦 Submission Process

### For CORTEX Contributors

1. **Create branch:** `feature/adapter-{name}`
2. **Implement adapter** in `src/adapters/{category}/{name}_adapter.py`
3. **Write tests** in `tests/adapters/{category}/test_{name}_adapter.py`
4. **Run tests:** `pytest tests/adapters/{category}/test_{name}_adapter.py --cov`
5. **Verify coverage:** Must be ≥90%
6. **Update config template:** Add example to `cortex.config.template.json`
7. **Document:** Add adapter to `supported_adapters.md` (create if doesn't exist)
8. **Pull request:** Submit PR with description and test results

### For Enterprise Users (External Adapters)

If you're creating a custom adapter for your organization:

1. **Place adapter anywhere** in your codebase (doesn't need to be in `src/adapters/`)
2. **Implement interface** (same requirements as above)
3. **Register manually:**

```python
# In your CORTEX initialization code
from src.core.adapter_registry import AdapterRegistry
from your_company.adapters.custom_test_adapter import CustomTestAdapter

registry = AdapterRegistry()
registry.register_adapter(
    adapter_type="test_framework",
    adapter_class=CustomTestAdapter
)
```

4. **Configure in cortex.config.json:**

```json
{
  "tech_stack": {
    "test_framework": "custom-test",
    "test_framework_config": {
      "custom_property": "value"
    }
  }
}
```

---

## 🔍 Troubleshooting

### Adapter Not Found

**Error:** `AdapterNotFoundError: No adapter found for type='test_framework' name='mytest'`

**Causes:**
1. Adapter not in `src/adapters/{category}/` directory
2. Adapter filename doesn't end with `_adapter.py`
3. Adapter class missing required metadata (`name`, `version`, etc.)
4. Typo in `cortex.config.json` tech_stack configuration

**Fix:**
```python
# Verify adapter is discoverable
from src.core.adapter_registry import AdapterRegistry

registry = AdapterRegistry()
print(registry.list_adapters("test_framework"))  # Should show your adapter
```

### Configuration Validation Failed

**Error:** `ConfigurationError: Invalid configuration for adapter 'mytest'`

**Cause:** Configuration in `cortex.config.json` doesn't match `configuration_schema`

**Fix:**
- Check `configuration_schema` has correct structure:
  ```python
  configuration_schema = {
      "property_name": {
          "type": "string",           # Required
          "description": "...",        # Required
          "default": "default_value"   # Optional
      }
  }
  ```
- Ensure `cortex.config.json` tech_stack section matches schema

### Interface Not Implemented

**Error:** `TypeError: Adapter 'mytest' does not implement required method 'execute_tests'`

**Cause:** Adapter class missing required interface methods

**Fix:**
- Verify all interface methods are implemented
- Use Protocol class for type hints (optional but recommended):
  ```python
  from src.adapters.interfaces.test_framework_adapter import ITestFrameworkAdapter
  
  class MyAdapter(ITestFrameworkAdapter):  # Optional but helps catch errors
      ...
  ```

---

## 📚 Examples

See these reference implementations in CORTEX 4.0:

| Adapter | File | Complexity | Notes |
|---------|------|------------|-------|
| pytest | `src/adapters/test_frameworks/pytest_adapter.py` | Low | Good starting point for Python tools |
| xUnit | `src/adapters/test_frameworks/xunit_adapter.py` | Medium | Shows XML parsing, cross-process execution |
| LaunchDarkly | `src/adapters/feature_flags/launchdarkly_adapter.py` | Medium | Shows SDK integration |
| NLog | `src/adapters/logging/nlog_adapter.py` | Low | Shows JSON log parsing |
| dotnet | `src/adapters/build_tools/dotnet_adapter.py` | High | Shows complex build tool with multiple commands |

---

## 🎓 Best Practices

1. **Error Handling:** Always return standardized error format instead of raising exceptions:
   ```python
   return {
       "success": False,
       "error": "Descriptive error message",
       "error_type": "TimeoutError"
   }
   ```

2. **Timeouts:** Respect `timeout` configuration parameter (default 600 seconds):
   ```python
   subprocess.run(..., timeout=self.config.get("timeout", 600))
   ```

3. **PII Protection:** If adapter handles logs, ALWAYS sanitize PII before returning:
   ```python
   from src.core.pii_sanitizer import sanitize_pii
   
   log_entry = sanitize_pii(log_entry)
   ```

4. **Cross-Platform:** Handle Windows/Linux/macOS differences:
   ```python
   from pathlib import Path
   
   # Use Path instead of string concatenation
   project_dir = Path(project_path)
   test_file = project_dir / "tests" / "test_user.py"
   ```

5. **Logging:** Log adapter operations for debugging:
   ```python
   import logging
   
   logger = logging.getLogger(__name__)
   logger.info(f"Executing tests with {self.name} adapter")
   logger.debug(f"Command: {' '.join(cmd)}")
   ```

6. **Validation:** Validate inputs in `__init__` and raise clear errors:
   ```python
   def __init__(self, config: Dict[str, Any]):
       if "sdk_key" not in config:
           raise ValueError("sdk_key is required in configuration")
       self.sdk_key = config["sdk_key"]
   ```

---

## 📖 Further Reading

- **Architecture:** `cortex-brain/documents/architecture/TECH-STACK-AGNOSTIC-ARCHITECTURE.md`
- **Enterprise Capabilities:** `cortex-brain/documents/analysis/ENTERPRISE-CAPABILITIES-CORTEX-4.0-ANALYSIS.md`
- **MASTER-PLAN:** `cortex-brain/documents/planning/active/CORTEX-3.0-4.0/MASTER-PLAN.md` (Phase 4, Weeks 14-16)
- **Adapter Interfaces:** `src/adapters/interfaces/`

---

**Questions?** Open an issue on GitHub or contact the CORTEX team.

**Version History:**
- 1.0 (December 19, 2025): Initial release
