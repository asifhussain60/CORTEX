# CORTEX 4.0 Tech-Stack Agnostic Architecture
## Universal Adapter System ("Lego Blocks")

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX  
**Date:** December 18, 2025  
**Version:** 1.0 - Initial Design  
**Status:** ✅ APPROVED - Core Architecture Pattern  
**MASTER-PLAN Integration:** Phase 4 (Weeks 14-16) - MCP Gateway Enhancement

---

## 🧠 CORTEX Universal Adapter Architecture

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

### 🎯 Vision Statement

**CORTEX 4.0 is tech-stack agnostic.** Users configure their technology stack once, and CORTEX adapts automatically—no code changes, no lock-in, no limitations.

**Lego Block Philosophy:** Mix and match adapters like Lego blocks. Want pytest + LaunchDarkly + NLog? Done. Want xUnit + Unleash + Serilog? Done. Want JUnit + Split.io + log4j? Done.

**Zero Lock-In:** Change your tech stack tomorrow without CORTEX migration. Update config, restart, continue working.

---

### ⚡ Core Principles

1. **Configuration Over Code:** Declare tech stack in `cortex.config.json`, not in CORTEX codebase
2. **Common Interfaces:** All adapters implement universal interfaces (language-agnostic)
3. **Auto-Discovery:** Adapter registry auto-discovers available adapters at runtime
4. **Pluggable Architecture:** Add new adapter = create adapter file + register in catalog
5. **Community Extensible:** Users can create custom adapters without CORTEX core changes
6. **MCP Integration:** All adapters use MCP Gateway for cross-language execution

---

### 💬 Architecture Overview

## Universal Adapter System

```
┌─────────────────────────────────────────────────────────────────┐
│                 CORTEX 4.0 Universal Adapter System             │
│                      "Tech Stack Agnostic"                      │
│                        Lego Block Design                         │
└─────────────────────────────────────────────────────────────────┘

USER CONFIGURATION
┌────────────────────────────────────────────────────────────────┐
│ cortex.config.json                                              │
│  {                                                              │
│    "tech_stack": {                                              │
│      "language": "csharp",         # Python, Java, JS, Go, etc.│
│      "test_framework": "xunit",    # pytest, JUnit, Jest, etc. │
│      "build_tool": "dotnet",       # maven, npm, cargo, etc.   │
│      "logging": "nlog",            # log4j, Winston, zap, etc. │
│      "feature_flags": "launchdarkly" # Unleash, ConfigCat, etc.│
│    }                                                            │
│  }                                                              │
└────────────────────────────────────────────────────────────────┘
                              ↓
                      RUNTIME RESOLUTION
┌────────────────────────────────────────────────────────────────┐
│ Adapter Registry (Lego Block Catalog)                          │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Test Framework Adapters (6+ supported)                   │ │
│  │ ├─ xUnitAdapter (C#)        - dotnet test integration    │ │
│  │ ├─ pytestAdapter (Python)   - pytest integration         │ │
│  │ ├─ JUnitAdapter (Java)      - maven/gradle test          │ │
│  │ ├─ JestAdapter (JavaScript) - npm test integration       │ │
│  │ ├─ GoTestAdapter (Go)       - go test integration        │ │
│  │ └─ RSpecAdapter (Ruby)      - rspec integration          │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Logging Framework Adapters (6+ supported)                │ │
│  │ ├─ NLogAdapter (C#)         - NLog parser                │ │
│  │ ├─ SerilogAdapter (C#)      - Serilog parser             │ │
│  │ ├─ Log4jAdapter (Java)      - log4j parser               │ │
│  │ ├─ WinstonAdapter (JS)      - Winston parser             │ │
│  │ ├─ ZapAdapter (Go)          - zap parser                 │ │
│  │ └─ StructuredLogAdapter     - Universal JSON logs        │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Feature Flag Adapters (5+ supported)                     │ │
│  │ ├─ LaunchDarklyAdapter      - LaunchDarkly SDK patterns  │ │
│  │ ├─ UnleashAdapter           - Unleash SDK patterns       │ │
│  │ ├─ ConfigCatAdapter         - ConfigCat SDK patterns     │ │
│  │ ├─ SplitIOAdapter           - Split.io SDK patterns      │ │
│  │ └─ EnvVarAdapter            - Environment variables      │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Build Tool Adapters (6+ supported)                       │ │
│  │ ├─ DotnetAdapter (C#)       - dotnet build/run           │ │
│  │ ├─ MavenAdapter (Java)      - mvn build/test             │ │
│  │ ├─ GradleAdapter (Java)     - gradle build/test          │ │
│  │ ├─ NPMAdapter (JavaScript)  - npm build/test             │ │
│  │ ├─ CargoAdapter (Rust)      - cargo build/test           │ │
│  │ └─ GoModAdapter (Go)        - go build/test              │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
                              ↓
                      COMMON INTERFACES
┌────────────────────────────────────────────────────────────────┐
│ Universal Interfaces (Language-Agnostic)                       │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ ITestFrameworkAdapter                                    │ │
│  │ ├─ execute_tests(path, filter) -> TestResults           │ │
│  │ ├─ parse_results(output) -> Dict                         │ │
│  │ ├─ generate_test_template(name, type) -> str            │ │
│  │ ├─ detect_test_files(path) -> List[str]                 │ │
│  │ └─ get_coverage_command() -> List[str]                   │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ ILoggingAdapter                                          │ │
│  │ ├─ parse_logs(file_path) -> List[LogEntry]              │ │
│  │ ├─ detect_pii(log_message) -> List[PII]                 │ │
│  │ ├─ sanitize_log(log_message) -> str                     │ │
│  │ ├─ parse_stack_trace(trace) -> Dict                     │ │
│  │ └─ get_log_format() -> str                              │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ IFeatureFlagAdapter                                      │ │
│  │ ├─ detect_flags(code_path) -> List[Flag]                │ │
│  │ ├─ get_sdk_patterns() -> List[str]                      │ │
│  │ ├─ generate_flag_test(flag_name, states) -> str         │ │
│  │ ├─ analyze_flag_dependencies(flags) -> Dict             │ │
│  │ └─ detect_edge_cases(code_path, flags) -> List[Dict]    │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ IBuildToolAdapter                                        │ │
│  │ ├─ build_project(path) -> BuildResult                   │ │
│  │ ├─ run_tests(path, filter) -> TestResults               │ │
│  │ ├─ get_dependencies(path) -> List[Dependency]           │ │
│  │ ├─ detect_project_files(path) -> List[str]              │ │
│  │ └─ get_build_command() -> List[str]                     │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
                              ↓
                  CORTEX ORCHESTRATORS (Agnostic)
┌────────────────────────────────────────────────────────────────┐
│ TDDOrchestrator                                                │
│ ├─ Uses: ITestFrameworkAdapter (language-agnostic)            │
│ ├─ Uses: IBuildToolAdapter (language-agnostic)                │
│ └─ Generates tests for: pytest, xUnit, JUnit, Jest, etc.      │
├────────────────────────────────────────────────────────────────┤
│ ObservabilityOrchestrator                                      │
│ ├─ Uses: ILoggingAdapter (framework-agnostic)                 │
│ ├─ Uses: ITestFrameworkAdapter (metrics collection)           │
│ └─ Monitors: NLog, Serilog, log4j, Winston, zap, etc.         │
├────────────────────────────────────────────────────────────────┤
│ IntelligenceOrchestrator                                       │
│ ├─ Uses: ILoggingAdapter (defect correlation)                 │
│ ├─ Uses: IFeatureFlagAdapter (flag analysis)                  │
│ └─ Correlates: Production logs → Test coverage gaps           │
├────────────────────────────────────────────────────────────────┤
│ PlanningOrchestrator                                           │
│ ├─ Uses: All adapters (tech-stack-aware planning)             │
│ └─ Generates: Language-specific plans (C#, Python, Java, etc.)│
└────────────────────────────────────────────────────────────────┘
```

---

## 📋 Implementation Details

### 1. Common Interface Definitions

#### ITestFrameworkAdapter

```python
# src/adapters/interfaces/test_framework_adapter.py
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class TestStatus(Enum):
    """Universal test status (framework-agnostic)."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"

@dataclass
class TestResult:
    """
    Universal test result format (tech-stack agnostic).
    Maps from any test framework output to this common format.
    """
    name: str
    status: TestStatus
    duration_ms: int
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None

@dataclass
class TestExecutionResult:
    """
    Aggregated test execution results.
    Used by TDDOrchestrator, ObservabilityOrchestrator.
    """
    total: int
    passed: int
    failed: int
    skipped: int
    errors: int
    duration_ms: int
    coverage_percentage: Optional[float] = None
    results: List[TestResult] = None

class ITestFrameworkAdapter(ABC):
    """
    Universal interface for test framework adapters.
    
    Implementations:
    - xUnitAdapter (C#)
    - pytestAdapter (Python)
    - JUnitAdapter (Java)
    - JestAdapter (JavaScript)
    - GoTestAdapter (Go)
    - RSpecAdapter (Ruby)
    
    All adapters MUST implement these methods to work with CORTEX.
    """
    
    @abstractmethod
    def get_framework_name(self) -> str:
        """
        Return framework name (e.g., 'xunit', 'pytest', 'junit').
        Used for logging and diagnostics.
        """
        pass
    
    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        """
        Return supported languages (e.g., ['csharp'], ['python']).
        Used for validation.
        """
        pass
    
    @abstractmethod
    def execute_tests(
        self,
        project_path: str,
        test_filter: Optional[str] = None,
        coverage: bool = False
    ) -> TestExecutionResult:
        """
        Execute tests using framework-specific runner.
        
        Args:
            project_path: Path to project root
            test_filter: Optional filter (framework-specific syntax)
            coverage: Whether to collect code coverage
        
        Returns:
            TestExecutionResult in universal format
        
        Example:
            xUnit: test_filter = "FullyQualifiedName~AuthTests"
            pytest: test_filter = "-k auth"
            JUnit: test_filter = "-Dtest=AuthTest"
        """
        pass
    
    @abstractmethod
    def parse_test_output(self, output: str) -> TestExecutionResult:
        """
        Parse framework-specific test output to universal format.
        
        Args:
            output: Raw test runner output
        
        Returns:
            TestExecutionResult in universal format
        """
        pass
    
    @abstractmethod
    def generate_test_template(
        self,
        test_name: str,
        test_type: str = "unit",  # unit, integration, e2e
        class_under_test: Optional[str] = None
    ) -> str:
        """
        Generate framework-specific test template.
        
        Args:
            test_name: Name of test
            test_type: Type of test (unit, integration, e2e)
            class_under_test: Optional class being tested
        
        Returns:
            Test template code in target language
        
        Examples:
            xUnit: Returns C# class with [Fact] attribute
            pytest: Returns Python function with def test_*
            JUnit: Returns Java class with @Test annotation
        """
        pass
    
    @abstractmethod
    def detect_test_files(self, project_path: str) -> List[str]:
        """
        Find all test files using framework-specific patterns.
        
        Args:
            project_path: Path to project root
        
        Returns:
            List of test file paths (relative to project_path)
        
        Examples:
            xUnit: **/*Tests.cs, **/*Test.cs
            pytest: test_*.py, *_test.py
            JUnit: **/*Test.java, **/*Tests.java
            Jest: **/*.test.js, **/*.spec.js
        """
        pass
    
    @abstractmethod
    def get_coverage_command(self, project_path: str) -> List[str]:
        """
        Return framework-specific coverage command.
        
        Args:
            project_path: Path to project root
        
        Returns:
            Command as list (suitable for subprocess.run)
        
        Examples:
            xUnit: ["dotnet", "test", "--collect:\"XPlat Code Coverage\""]
            pytest: ["pytest", "--cov=src", "--cov-report=xml"]
            JUnit: ["mvn", "test", "jacoco:report"]
        """
        pass
    
    @abstractmethod
    def validate_environment(self) -> Dict[str, bool]:
        """
        Validate test framework is installed and configured.
        
        Returns:
            Dict with validation results
        
        Example:
        {
            "framework_installed": True,
            "version": "2.4.2",
            "runner_available": True,
            "configuration_valid": True
        }
        """
        pass
```

#### ILoggingAdapter

```python
# src/adapters/interfaces/logging_adapter.py
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class LogLevel(Enum):
    """Universal log levels (framework-agnostic)."""
    TRACE = "trace"
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
    FATAL = "fatal"

@dataclass
class LogEntry:
    """
    Universal log entry format (tech-stack agnostic).
    Maps from any logging framework to this common format.
    """
    timestamp: datetime
    level: LogLevel
    message: str
    logger_name: Optional[str] = None
    exception: Optional[str] = None
    stack_trace: Optional[str] = None
    correlation_id: Optional[str] = None
    properties: Optional[Dict[str, any]] = None

@dataclass
class PIIDetection:
    """PII detection result."""
    type: str  # email, ssn, credit_card, phone, ip_address, api_key
    value: str
    position: int
    confidence: float  # 0.0-1.0

class ILoggingAdapter(ABC):
    """
    Universal interface for logging framework adapters.
    
    Implementations:
    - NLogAdapter (C#)
    - SerilogAdapter (C#)
    - Log4jAdapter (Java)
    - WinstonAdapter (JavaScript)
    - ZapAdapter (Go)
    - StructuredLogAdapter (Universal JSON)
    
    All adapters MUST implement these methods to work with CORTEX.
    """
    
    @abstractmethod
    def get_framework_name(self) -> str:
        """Return logging framework name (e.g., 'nlog', 'serilog')."""
        pass
    
    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        """Return supported languages (e.g., ['csharp'], ['java'])."""
        pass
    
    @abstractmethod
    def parse_log_file(
        self,
        file_path: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        min_level: LogLevel = LogLevel.INFO
    ) -> List[LogEntry]:
        """
        Parse log file to universal format.
        
        Args:
            file_path: Path to log file
            start_time: Optional start time filter
            end_time: Optional end time filter
            min_level: Minimum log level to include
        
        Returns:
            List of LogEntry in universal format
        """
        pass
    
    @abstractmethod
    def parse_log_message(self, log_line: str) -> Optional[LogEntry]:
        """
        Parse single log message to universal format.
        
        Args:
            log_line: Single log line
        
        Returns:
            LogEntry or None if unparseable
        """
        pass
    
    @abstractmethod
    def detect_pii(self, log_message: str) -> List[PIIDetection]:
        """
        Detect PII in log message.
        
        Args:
            log_message: Log message to scan
        
        Returns:
            List of detected PII instances
        
        Patterns Detected:
        - Email addresses
        - SSN (Social Security Numbers)
        - Credit card numbers
        - Phone numbers
        - IP addresses
        - API keys (32+ char alphanumeric)
        """
        pass
    
    @abstractmethod
    def sanitize_log(self, log_message: str) -> str:
        """
        Remove PII from log message.
        
        Args:
            log_message: Log message to sanitize
        
        Returns:
            Sanitized log message (PII replaced with [TYPE])
        
        Example:
            Input:  "User john@example.com logged in from 192.168.1.1"
            Output: "User [EMAIL] logged in from [IP_ADDRESS]"
        """
        pass
    
    @abstractmethod
    def parse_stack_trace(self, stack_trace: str) -> Dict[str, any]:
        """
        Parse stack trace to structured format.
        
        Args:
            stack_trace: Stack trace string
        
        Returns:
            Dict with parsed stack trace components
        
        Example:
        {
            "exception_type": "NullReferenceException",
            "message": "Object reference not set...",
            "frames": [
                {
                    "file": "PaymentProcessor.cs",
                    "line": 156,
                    "method": "ProcessPayment",
                    "class": "PaymentProcessor"
                }
            ]
        }
        """
        pass
    
    @abstractmethod
    def get_log_format(self) -> str:
        """
        Return expected log format string.
        
        Returns:
            Format string description
        
        Examples:
            NLog: "${longdate}|${level}|${logger}|${message}"
            Serilog: "[{Timestamp:yyyy-MM-dd HH:mm:ss} {Level}] {Message}"
            log4j: "%d{yyyy-MM-dd HH:mm:ss} %-5p %c{1}:%L - %m%n"
        """
        pass
```

#### IFeatureFlagAdapter

```python
# src/adapters/interfaces/feature_flag_adapter.py
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class FlagType(Enum):
    """Universal flag types."""
    BOOLEAN = "boolean"
    STRING = "string"
    NUMBER = "number"
    JSON = "json"

@dataclass
class FeatureFlag:
    """
    Universal feature flag representation.
    Maps from any flag provider to this common format.
    """
    name: str
    flag_type: FlagType
    default_value: any
    code_path: str  # File path where flag is used
    line_number: int
    method_name: Optional[str] = None
    dependent_flags: List[str] = None  # Nested flags

@dataclass
class FlagEdgeCase:
    """Feature flag edge case detection."""
    flag_name: str
    edge_case_type: str  # dead_code, unguarded_call, typo, missing_fallback, race_condition
    severity: str  # high, medium, low
    file_path: str
    line_number: int
    description: str
    suggested_fix: Optional[str] = None

class IFeatureFlagAdapter(ABC):
    """
    Universal interface for feature flag provider adapters.
    
    Implementations:
    - LaunchDarklyAdapter
    - UnleashAdapter
    - ConfigCatAdapter
    - SplitIOAdapter
    - EnvVarAdapter (simple environment variables)
    
    All adapters MUST implement these methods to work with CORTEX.
    """
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Return provider name (e.g., 'launchdarkly', 'unleash')."""
        pass
    
    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        """Return supported languages (e.g., ['csharp', 'python', 'javascript'])."""
        pass
    
    @abstractmethod
    def get_sdk_patterns(self, language: str) -> List[str]:
        """
        Return SDK patterns for flag detection (AST analysis).
        
        Args:
            language: Target language
        
        Returns:
            List of SDK method patterns
        
        Examples:
            LaunchDarkly (C#): ["client.Variation", "client.BoolVariation"]
            LaunchDarkly (Python): ["client.variation", "ldclient.get().variation"]
            Unleash (Java): ["unleash.isEnabled"]
        """
        pass
    
    @abstractmethod
    def detect_flags(
        self,
        file_path: str,
        language: str
    ) -> List[FeatureFlag]:
        """
        Scan file for feature flags using AST analysis.
        
        Args:
            file_path: Path to source file
            language: Programming language
        
        Returns:
            List of detected feature flags
        """
        pass
    
    @abstractmethod
    def analyze_flag_dependencies(
        self,
        flags: List[FeatureFlag]
    ) -> Dict[str, List[str]]:
        """
        Build flag dependency graph (flag A → calls code with flag B).
        
        Args:
            flags: List of detected flags
        
        Returns:
            Dict mapping flag_name → dependent_flag_names
        
        Example:
        {
            "new-auth-flow": ["user-permissions", "mfa-enabled"],
            "user-permissions": []
        }
        """
        pass
    
    @abstractmethod
    def detect_edge_cases(
        self,
        code_path: str,
        flags: List[FeatureFlag],
        language: str
    ) -> List[FlagEdgeCase]:
        """
        Detect dangerous edge cases in feature-flagged code.
        
        Args:
            code_path: Path to source file
            flags: List of flags to analyze
            language: Programming language
        
        Returns:
            List of detected edge cases
        
        Edge Cases Detected:
        1. Dead code path (flag ON but code never executes)
        2. Unguarded call (flag OFF but feature code called)
        3. Flag typo (unrecognized flag name)
        4. Missing fallback (no exception handling if flag unreachable)
        5. Race condition (concurrent flag state change)
        """
        pass
    
    @abstractmethod
    def generate_flag_test(
        self,
        flag: FeatureFlag,
        test_framework: str,
        language: str
    ) -> str:
        """
        Generate test template for feature flag.
        
        Args:
            flag: Feature flag to test
            test_framework: Target test framework (xunit, pytest, etc.)
            language: Target language
        
        Returns:
            Test code template
        
        Example (xUnit):
        [Theory]
        [InlineData(true)]
        [InlineData(false)]
        public void Test_NewAuthFlow_FlagStates(bool flagOn) {
            var client = MockLaunchDarklyClient("new-auth-flow", flagOn);
            // ... test logic
        }
        """
        pass
    
    @abstractmethod
    def generate_test_matrix(
        self,
        flags: List[FeatureFlag],
        strategy: str = "pairwise"  # exhaustive, pairwise, risk-based
    ) -> List[Dict[str, any]]:
        """
        Generate optimal test matrix for multiple flags.
        
        Args:
            flags: List of flags to test
            strategy: Testing strategy
        
        Returns:
            List of test scenarios
        
        Strategies:
        - exhaustive: 2^N tests (all combinations)
        - pairwise: ~N*log(N) tests (95% coverage at 20% cost)
        - risk-based: Prioritize high-risk flags
        
        Example Output (pairwise for 3 flags):
        [
            {"new-auth": True, "mfa": True, "sso": True},
            {"new-auth": True, "mfa": False, "sso": False},
            {"new-auth": False, "mfa": True, "sso": False},
            {"new-auth": False, "mfa": False, "sso": True}
        ]
        """
        pass
```

#### IBuildToolAdapter

```python
# src/adapters/interfaces/build_tool_adapter.py
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class BuildResult:
    """Universal build result format."""
    success: bool
    duration_ms: int
    output: str
    errors: List[str]
    warnings: List[str]

@dataclass
class Dependency:
    """Universal dependency representation."""
    name: str
    version: str
    is_dev_dependency: bool = False

class IBuildToolAdapter(ABC):
    """
    Universal interface for build tool adapters.
    
    Implementations:
    - DotnetAdapter (C#)
    - MavenAdapter (Java)
    - GradleAdapter (Java)
    - NPMAdapter (JavaScript)
    - CargoAdapter (Rust)
    - GoModAdapter (Go)
    """
    
    @abstractmethod
    def get_tool_name(self) -> str:
        """Return build tool name (e.g., 'dotnet', 'maven')."""
        pass
    
    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        """Return supported languages."""
        pass
    
    @abstractmethod
    def build_project(self, project_path: str) -> BuildResult:
        """Build project using tool-specific command."""
        pass
    
    @abstractmethod
    def run_tests(
        self,
        project_path: str,
        test_filter: Optional[str] = None
    ) -> TestExecutionResult:
        """Run tests using build tool."""
        pass
    
    @abstractmethod
    def get_dependencies(self, project_path: str) -> List[Dependency]:
        """Get project dependencies."""
        pass
    
    @abstractmethod
    def detect_project_files(self, project_path: str) -> List[str]:
        """
        Detect build tool project files.
        
        Examples:
        - dotnet: *.csproj, *.sln
        - maven: pom.xml
        - gradle: build.gradle, settings.gradle
        - npm: package.json
        """
        pass
    
    @abstractmethod
    def get_build_command(self, project_path: str) -> List[str]:
        """Return build command as list."""
        pass
```

### 2. Adapter Registry (Lego Block Catalog)

```python
# src/adapters/adapter_registry.py
from typing import Dict, Type, List
from adapters.interfaces.test_framework_adapter import ITestFrameworkAdapter
from adapters.interfaces.logging_adapter import ILoggingAdapter
from adapters.interfaces.feature_flag_adapter import IFeatureFlagAdapter
from adapters.interfaces.build_tool_adapter import IBuildToolAdapter
import importlib

class AdapterRegistry:
    """
    Registry of all available adapters (Lego block catalog).
    
    Auto-discovers adapters at runtime.
    Users can register custom adapters.
    """
    
    # Test Framework Adapters (Lego Blocks)
    TEST_FRAMEWORKS: Dict[str, str] = {
        "xunit": "adapters.test_frameworks.xunit_adapter.XUnitAdapter",
        "pytest": "adapters.test_frameworks.pytest_adapter.PytestAdapter",
        "junit": "adapters.test_frameworks.junit_adapter.JUnitAdapter",
        "jest": "adapters.test_frameworks.jest_adapter.JestAdapter",
        "gotest": "adapters.test_frameworks.gotest_adapter.GoTestAdapter",
        "rspec": "adapters.test_frameworks.rspec_adapter.RSpecAdapter",
        "mocha": "adapters.test_frameworks.mocha_adapter.MochaAdapter",
        "nunit": "adapters.test_frameworks.nunit_adapter.NUnitAdapter",
    }
    
    # Logging Framework Adapters (Lego Blocks)
    LOGGING_FRAMEWORKS: Dict[str, str] = {
        "nlog": "adapters.logging.nlog_adapter.NLogAdapter",
        "serilog": "adapters.logging.serilog_adapter.SerilogAdapter",
        "log4j": "adapters.logging.log4j_adapter.Log4jAdapter",
        "log4net": "adapters.logging.log4net_adapter.Log4NetAdapter",
        "winston": "adapters.logging.winston_adapter.WinstonAdapter",
        "zap": "adapters.logging.zap_adapter.ZapAdapter",
        "logrus": "adapters.logging.logrus_adapter.LogrusAdapter",
        "structured": "adapters.logging.structured_adapter.StructuredLogAdapter",
    }
    
    # Feature Flag Provider Adapters (Lego Blocks)
    FEATURE_FLAG_PROVIDERS: Dict[str, str] = {
        "launchdarkly": "adapters.feature_flags.launchdarkly_adapter.LaunchDarklyAdapter",
        "unleash": "adapters.feature_flags.unleash_adapter.UnleashAdapter",
        "configcat": "adapters.feature_flags.configcat_adapter.ConfigCatAdapter",
        "splitio": "adapters.feature_flags.splitio_adapter.SplitIOAdapter",
        "envvar": "adapters.feature_flags.envvar_adapter.EnvVarAdapter",
        "flagsmith": "adapters.feature_flags.flagsmith_adapter.FlagsmithAdapter",
    }
    
    # Build Tool Adapters (Lego Blocks)
    BUILD_TOOLS: Dict[str, str] = {
        "dotnet": "adapters.build_tools.dotnet_adapter.DotnetAdapter",
        "maven": "adapters.build_tools.maven_adapter.MavenAdapter",
        "gradle": "adapters.build_tools.gradle_adapter.GradleAdapter",
        "npm": "adapters.build_tools.npm_adapter.NPMAdapter",
        "yarn": "adapters.build_tools.yarn_adapter.YarnAdapter",
        "cargo": "adapters.build_tools.cargo_adapter.CargoAdapter",
        "go": "adapters.build_tools.go_adapter.GoModAdapter",
        "pip": "adapters.build_tools.pip_adapter.PipAdapter",
    }
    
    @classmethod
    def get_test_framework_adapter(cls, framework_name: str) -> ITestFrameworkAdapter:
        """
        Get test framework adapter by name (Lego block retrieval).
        
        Args:
            framework_name: Framework name (e.g., 'xunit', 'pytest')
        
        Returns:
            Adapter instance implementing ITestFrameworkAdapter
        
        Raises:
            ValueError: If framework not found
        """
        if framework_name not in cls.TEST_FRAMEWORKS:
            available = list(cls.TEST_FRAMEWORKS.keys())
            raise ValueError(
                f"Unknown test framework: '{framework_name}'. "
                f"Available frameworks: {', '.join(available)}\n\n"
                f"To add custom adapter:\n"
                f"1. Create adapter implementing ITestFrameworkAdapter\n"
                f"2. Register with AdapterRegistry.register_test_framework()"
            )
        
        return cls._load_adapter(cls.TEST_FRAMEWORKS[framework_name])
    
    @classmethod
    def get_logging_adapter(cls, logging_name: str) -> ILoggingAdapter:
        """Get logging framework adapter by name."""
        if logging_name not in cls.LOGGING_FRAMEWORKS:
            available = list(cls.LOGGING_FRAMEWORKS.keys())
            raise ValueError(
                f"Unknown logging framework: '{logging_name}'. "
                f"Available frameworks: {', '.join(available)}"
            )
        
        return cls._load_adapter(cls.LOGGING_FRAMEWORKS[logging_name])
    
    @classmethod
    def get_feature_flag_adapter(cls, provider_name: str) -> IFeatureFlagAdapter:
        """Get feature flag provider adapter by name."""
        if provider_name not in cls.FEATURE_FLAG_PROVIDERS:
            available = list(cls.FEATURE_FLAG_PROVIDERS.keys())
            raise ValueError(
                f"Unknown feature flag provider: '{provider_name}'. "
                f"Available providers: {', '.join(available)}"
            )
        
        return cls._load_adapter(cls.FEATURE_FLAG_PROVIDERS[provider_name])
    
    @classmethod
    def get_build_tool_adapter(cls, tool_name: str) -> IBuildToolAdapter:
        """Get build tool adapter by name."""
        if tool_name not in cls.BUILD_TOOLS:
            available = list(cls.BUILD_TOOLS.keys())
            raise ValueError(
                f"Unknown build tool: '{tool_name}'. "
                f"Available tools: {', '.join(available)}"
            )
        
        return cls._load_adapter(cls.BUILD_TOOLS[tool_name])
    
    @classmethod
    def _load_adapter(cls, adapter_path: str):
        """
        Dynamically load adapter class.
        
        Args:
            adapter_path: Full module path (e.g., 'adapters.test_frameworks.xunit_adapter.XUnitAdapter')
        
        Returns:
            Adapter instance
        """
        module_path, class_name = adapter_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        adapter_class = getattr(module, class_name)
        return adapter_class()
    
    @classmethod
    def list_available_adapters(cls) -> Dict[str, List[str]]:
        """
        List all available adapters (Lego block catalog).
        
        Returns:
            Dict with adapter categories and names
        
        Example:
        {
            "test_frameworks": ["xunit", "pytest", "junit", ...],
            "logging_frameworks": ["nlog", "serilog", "log4j", ...],
            "feature_flag_providers": ["launchdarkly", "unleash", ...],
            "build_tools": ["dotnet", "maven", "npm", ...]
        }
        """
        return {
            "test_frameworks": list(cls.TEST_FRAMEWORKS.keys()),
            "logging_frameworks": list(cls.LOGGING_FRAMEWORKS.keys()),
            "feature_flag_providers": list(cls.FEATURE_FLAG_PROVIDERS.keys()),
            "build_tools": list(cls.BUILD_TOOLS.keys())
        }
    
    @classmethod
    def register_test_framework(cls, name: str, adapter_path: str):
        """
        Register custom test framework adapter (user extension).
        
        Args:
            name: Framework name
            adapter_path: Full module path to adapter class
        
        Example:
            AdapterRegistry.register_test_framework(
                "my_custom_framework",
                "my_adapters.custom_test_adapter.CustomAdapter"
            )
        """
        cls.TEST_FRAMEWORKS[name] = adapter_path
    
    @classmethod
    def register_logging_framework(cls, name: str, adapter_path: str):
        """Register custom logging framework adapter."""
        cls.LOGGING_FRAMEWORKS[name] = adapter_path
    
    @classmethod
    def register_feature_flag_provider(cls, name: str, adapter_path: str):
        """Register custom feature flag provider adapter."""
        cls.FEATURE_FLAG_PROVIDERS[name] = adapter_path
    
    @classmethod
    def register_build_tool(cls, name: str, adapter_path: str):
        """Register custom build tool adapter."""
        cls.BUILD_TOOLS[name] = adapter_path
```

### 3. Configuration Schema

```json
// cortex.config.json (Enhanced with tech_stack)
{
  "version": "4.0",
  "cortex": {
    "admin_email": "asif@example.com",
    "workspace_root": "/Users/asif/PROJECTS",
    "enable_analytics": true
  },
  
  "tech_stack": {
    "language": "csharp",
    "language_version": "12.0",
    
    "test_framework": "xunit",
    "test_framework_version": "2.4.2",
    
    "build_tool": "dotnet",
    "build_tool_version": "8.0",
    
    "logging_framework": "nlog",
    "logging_config_file": "NLog.config",
    
    "feature_flag_provider": "launchdarkly",
    "feature_flag_config": {
      "sdk_key_env_var": "LAUNCHDARKLY_SDK_KEY",
      "project_key": "my-project"
    },
    
    "code_coverage_tool": "coverlet",
    "linting_tool": "roslyn_analyzers",
    
    "additional_tools": {
      "static_analysis": "sonarqube",
      "security_scanner": "snyk"
    }
  },
  
  "project_structure": {
    "source_directory": "src",
    "test_directory": "tests",
    "build_output": "bin",
    "configuration_files": [
      "appsettings.json",
      "NLog.config",
      "launchdarkly.config"
    ]
  },
  
  "adapter_overrides": {
    "test_framework": {
      "custom_runner": null,
      "custom_report_parser": null,
      "additional_arguments": ["--logger:trx", "--verbosity:normal"]
    },
    "logging_framework": {
      "custom_parser": null,
      "log_file_pattern": "logs/*.log"
    },
    "feature_flags": {
      "custom_sdk_patterns": []
    }
  },
  
  "brain": {
    "tier1_conversation_limit": 70,
    "tier2_pattern_threshold": 3,
    "tier3_hotspot_threshold": 10
  }
}
```

### 4. Orchestrator Integration (Tech-Stack Agnostic)

```python
# Example: TDDOrchestrator uses adapters
from adapters.adapter_registry import AdapterRegistry
from core.config_manager import ConfigManager

class TDDOrchestrator(BaseOrchestrator):
    """
    Tech-stack agnostic TDD orchestrator.
    Works with ANY test framework through adapters.
    """
    
    def __init__(self):
        super().__init__()
        
        # Load tech stack from configuration
        config = ConfigManager.load_config()
        tech_stack = config["tech_stack"]
        
        # Get adapters (Lego blocks)
        self.test_adapter = AdapterRegistry.get_test_framework_adapter(
            tech_stack["test_framework"]
        )
        self.build_adapter = AdapterRegistry.get_build_tool_adapter(
            tech_stack["build_tool"]
        )
        
        self.logger.info(
            f"🎭 TDD Orchestrator initialized with: "
            f"{tech_stack['test_framework']} + {tech_stack['build_tool']}"
        )
    
    async def execute_red_phase(self, context: Dict) -> PhaseResult:
        """
        RED phase: Generate tests (language-agnostic).
        Works with: xUnit, pytest, JUnit, Jest, etc.
        """
        # Generate test template using adapter
        test_code = self.test_adapter.generate_test_template(
            test_name=context["feature_name"],
            test_type="unit",
            class_under_test=context.get("class_name")
        )
        
        # Write test file
        test_file = self._write_test_file(test_code, context)
        
        # Execute tests (should fail in RED phase)
        test_results = self.test_adapter.execute_tests(
            project_path=context["project_path"],
            test_filter=context.get("test_filter")
        )
        
        # Validate RED phase: tests MUST fail
        if test_results.failed == 0:
            raise ValueError(
                "RED phase violation: All tests passed. "
                "Tests must fail before implementation."
            )
        
        return PhaseResult(
            phase_name="RED",
            success=True,
            outputs={"test_file": test_file, "tests_failed": test_results.failed},
            metrics={"duration_ms": test_results.duration_ms}
        )
```

---

## 📊 Impact & Changes

### File Structure

```
src/adapters/                            # NEW DIRECTORY (6,000+ LOC)
├── __init__.py
├── adapter_registry.py                  # Lego block catalog (400 LOC)
├── interfaces/                          # Common interfaces (4 files)
│   ├── __init__.py
│   ├── test_framework_adapter.py        # ITestFrameworkAdapter (250 LOC)
│   ├── logging_adapter.py               # ILoggingAdapter (200 LOC)
│   ├── feature_flag_adapter.py          # IFeatureFlagAdapter (200 LOC)
│   └── build_tool_adapter.py            # IBuildToolAdapter (150 LOC)
├── test_frameworks/                     # 8 test framework adapters
│   ├── __init__.py
│   ├── xunit_adapter.py                 # C# xUnit (350 LOC)
│   ├── pytest_adapter.py                # Python pytest (350 LOC)
│   ├── junit_adapter.py                 # Java JUnit (350 LOC)
│   ├── jest_adapter.py                  # JavaScript Jest (350 LOC)
│   ├── gotest_adapter.py                # Go test (350 LOC)
│   ├── rspec_adapter.py                 # Ruby RSpec (350 LOC)
│   ├── mocha_adapter.py                 # JavaScript Mocha (350 LOC)
│   └── nunit_adapter.py                 # C# NUnit (350 LOC)
├── logging/                             # 8 logging framework adapters
│   ├── __init__.py
│   ├── nlog_adapter.py                  # C# NLog (300 LOC)
│   ├── serilog_adapter.py               # C# Serilog (300 LOC)
│   ├── log4j_adapter.py                 # Java log4j (300 LOC)
│   ├── log4net_adapter.py               # C# log4net (300 LOC)
│   ├── winston_adapter.py               # JavaScript Winston (300 LOC)
│   ├── zap_adapter.py                   # Go zap (300 LOC)
│   ├── logrus_adapter.py                # Go logrus (300 LOC)
│   └── structured_adapter.py            # Universal JSON (250 LOC)
├── feature_flags/                       # 6 feature flag adapters
│   ├── __init__.py
│   ├── launchdarkly_adapter.py         # LaunchDarkly (350 LOC)
│   ├── unleash_adapter.py              # Unleash (350 LOC)
│   ├── configcat_adapter.py            # ConfigCat (350 LOC)
│   ├── splitio_adapter.py              # Split.io (350 LOC)
│   ├── envvar_adapter.py               # Environment variables (250 LOC)
│   └── flagsmith_adapter.py            # Flagsmith (350 LOC)
├── build_tools/                         # 8 build tool adapters
│   ├── __init__.py
│   ├── dotnet_adapter.py                # .NET dotnet (300 LOC)
│   ├── maven_adapter.py                 # Java Maven (300 LOC)
│   ├── gradle_adapter.py                # Java Gradle (300 LOC)
│   ├── npm_adapter.py                   # JavaScript npm (300 LOC)
│   ├── yarn_adapter.py                  # JavaScript yarn (300 LOC)
│   ├── cargo_adapter.py                 # Rust cargo (300 LOC)
│   ├── go_adapter.py                    # Go mod (300 LOC)
│   └── pip_adapter.py                   # Python pip (300 LOC)
└── tests/                               # Adapter tests
    ├── test_adapter_registry.py         # (200 LOC)
    ├── test_interfaces/                 # Interface tests (4 files, 400 LOC)
    ├── test_test_frameworks/            # 8 test files (~800 LOC)
    ├── test_logging/                    # 8 test files (~800 LOC)
    ├── test_feature_flags/              # 6 test files (~600 LOC)
    └── test_build_tools/                # 8 test files (~800 LOC)
```

**Total New Code:** ~10,000 LOC (universal adapter system)

### Benefits Summary

✅ **Universal Compatibility:** Works with ANY tech stack  
✅ **Future-Proof:** New framework = new adapter (1-2 days work)  
✅ **User Choice:** Users pick their tools, not CORTEX  
✅ **Lego Block Philosophy:** Mix and match adapters freely  
✅ **Community Extensions:** Users create custom adapters  
✅ **Zero Lock-In:** Change tech stack without CORTEX migration  
✅ **MCP Integration:** All adapters use MCP Gateway (cross-language)  
✅ **Testable:** Each adapter independently tested

---

## 🔍 Next Steps

### Phase 4 Integration (Weeks 14-16)

- [ ] **Week 14: Adapter Interfaces**
  - [ ] Define 4 core interfaces (ITestFrameworkAdapter, ILoggingAdapter, IFeatureFlagAdapter, IBuildToolAdapter)
  - [ ] Create AdapterRegistry with auto-discovery
  - [ ] Write comprehensive interface tests

- [ ] **Week 15: Core Adapters**
  - [ ] Implement xUnit adapter (C#)
  - [ ] Implement pytest adapter (Python)
  - [ ] Implement JUnit adapter (Java)
  - [ ] Implement Jest adapter (JavaScript)
  - [ ] Implement NLog adapter (C#)
  - [ ] Implement LaunchDarkly adapter
  - [ ] Test each adapter independently

- [ ] **Week 16: Orchestrator Integration**
  - [ ] Update TDDOrchestrator to use adapters
  - [ ] Update ObservabilityOrchestrator to use adapters
  - [ ] Update IntelligenceOrchestrator to use adapters
  - [ ] Update PlanningOrchestrator to be tech-stack aware
  - [ ] Integration testing across all adapters

### Community Expansion (Post-4.0 GA)

- [ ] **Additional Adapters:**
  - [ ] Mocha adapter (JavaScript)
  - [ ] RSpec adapter (Ruby)
  - [ ] GoTest adapter (Go)
  - [ ] More logging frameworks
  - [ ] More feature flag providers

- [ ] **Documentation:**
  - [ ] Adapter development guide (how to create custom adapters)
  - [ ] Migration guide (switching tech stacks)
  - [ ] Video tutorials for adapter creation

---

**Alignment Confirmation:** ✅ Universal adapter system fits within CORTEX 4.0 MASTER-PLAN Phase 4 (MCP Gateway) without timeline extension. This is the natural evolution of MCP's pluggable architecture.
