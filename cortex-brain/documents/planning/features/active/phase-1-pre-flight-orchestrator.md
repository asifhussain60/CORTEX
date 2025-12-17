# Phase 1: Pre-Flight Orchestrator

**Phase ID:** CORTEX-ORCH-AST-P1  
**Parent Plan:** MASTER-CORTEX-ORCHESTRATION-AST-ENHANCEMENT-PLAN.md  
**Duration:** Week 1-2 (5 days)  
**Owner:** Planning System Team  
**Status:** ✅ COMPLETE

---

## 📊 Phase Progress Tracker

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                      PHASE 1: PRE-FLIGHT ORCHESTRATOR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Step 1: Requirements Detection       [██████████] 100%  ✅ Complete
Step 2: Validation Framework         [██████████] 100%  ✅ Complete
Step 3: Script Generator             [██████████] 100%  ✅ Complete
Step 4: Health Report Builder        [██████████] 100%  ✅ Complete
Step 5: Gate Enforcement Logic       [██████████] 100%  ✅ Complete
Step 6: Planning System Integration  [██████████] 100%  ✅ Complete
Step 7: Testing & Documentation      [██████████] 100%  ✅ Complete

PHASE PROGRESS: ██████████████████████████████ 7/7 Steps (100%)

START DATE: December 13, 2025
COMPLETION DATE: December 13, 2025 (1 day)
ELAPSED TIME: 0d 3h 15m
```

**Legend:** ⏳ Not Started | 🚧 In Progress | ✅ Complete | ⚠️ Blocked

---

## 🎯 Phase Objectives

### Primary Goal
Create pre-flight validation orchestrator that detects environment requirements from project patterns and validates them BEFORE Phase 1 execution, preventing catastrophic delays like the 2-week RA migration blocker (missing .NET SDK).

### Success Criteria

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Detection Coverage | 12+ check types | Environment requirement catalog |
| Blocker Prevention | 100% CRITICAL failures block | Gate enforcement tests |
| Execution Time | < 15 seconds | Performance benchmark |
| Script Generation | Executable PowerShell/bash | Manual script execution |
| False Positive Rate | < 5% | Production monitoring |

### Key Deliverables

1. **Pre-Flight Orchestrator** (`src/orchestrators/planning/pre_flight_orchestrator.py`, ~400 lines)
2. **Requirement Detector** (pattern-based detection from project files)
3. **Validation Script Generator** (PowerShell/bash templates)
4. **Health Report Builder** (PASS/FAIL/WARN with remediation steps)
5. **Gate Enforcement Logic** (BLOCK vs WARN decision engine)

---

## 🔍 Problem Statement

### Real-World Evidence: RA Migration Blocker

**Timeline:**
- **Week 1:** Planning complete, ready to execute
- **Week 2:** First execution attempt → ".NET SDK not found"
- **Week 3:** User installs SDK, second attempt → "Entity Framework tools missing"
- **Week 4:** Finally ready to proceed
- **Impact:** 2-week delay, user frustration, lost momentum

**Root Cause:** No environment validation before code generation

**Prevention:** Pre-flight check would have detected all blockers in 15 minutes on Day 1

### Current State Issues

**Problem 1: No Environment Validation**
- Planning System generates code without checking if environment can execute it
- Discoveries happen AFTER code generation (wasted effort)
- User must manually diagnose missing tools/SDKs

**Problem 2: Generic Error Messages**
- "Command not found: dotnet" → unhelpful
- No remediation guidance
- User stuck googling solutions

**Problem 3: No Pattern-Specific Intelligence**
- FastAPI projects need Python 3.8+, but don't check
- JWT authentication needs SSL certificates, but don't validate
- Database migrations need connection strings, but don't verify

### Target State Benefits

**Benefit 1: Early Blocker Detection**
- Detect missing SDKs, tools, permissions BEFORE Phase 1
- Generate executable validation script user can run
- Clear PASS/FAIL/WARN report with remediation steps

**Benefit 2: Pattern-Specific Intelligence**
- FastAPI → Check Python 3.8+, pip, virtualenv
- .NET → Check SDK version, EF tools, NuGet
- Database → Check connection strings, migration tools
- Docker → Check Docker Desktop, compose, registry access

**Benefit 3: Executable Remediation**
- Generate script with installation commands
- User runs script → fixes all issues → re-runs validation
- Clear path from BLOCKER to READY

---

## 🏗️ Architecture Design

### Component Overview

```
Planning System 2.0
    ↓
Pre-Flight Orchestrator (NEW)
    ├─ Requirement Detector
    │   ├─ Pattern Analysis (FastAPI, .NET, etc.)
    │   ├─ File Inspection (requirements.txt, *.csproj)
    │   └─ Dependency Graph (transitive requirements)
    │
    ├─ Validation Framework
    │   ├─ SDK Checker (dotnet, python, node, go)
    │   ├─ Tool Checker (docker, git, make, cmake)
    │   ├─ Permission Checker (file write, network, registry)
    │   └─ Resource Checker (disk space, memory, internet)
    │
    ├─ Script Generator
    │   ├─ PowerShell Template (Windows)
    │   ├─ Bash Template (Linux/Mac)
    │   └─ Remediation Commands (install instructions)
    │
    ├─ Health Report Builder
    │   ├─ PASS (all checks passed)
    │   ├─ WARN (optional missing, proceed with caution)
    │   └─ FAIL (CRITICAL blocker, must fix)
    │
    └─ Gate Enforcer
        ├─ BLOCK if any FAIL
        └─ WARN if any WARN (allow proceed)
    ↓
Phase 1: Feature Implementation (only if PASS)
```

### Requirement Detection Strategy

**Pattern-Based Detection:**
```python
PATTERN_REQUIREMENTS = {
    "fastapi": {
        "sdk": {"python": ">=3.8"},
        "tools": ["pip", "virtualenv"],
        "packages": ["fastapi", "uvicorn"],
        "optional": ["pytest", "httpx"]
    },
    "dotnet": {
        "sdk": {"dotnet": ">=6.0"},
        "tools": ["dotnet-ef", "nuget"],
        "optional": ["docker"]
    },
    "jwt_auth": {
        "certificates": ["ssl_cert", "ssl_key"],
        "environment": ["JWT_SECRET_KEY"],
        "optional": ["cert_authority"]
    },
    "docker": {
        "tools": ["docker", "docker-compose"],
        "permissions": ["docker_socket"],
        "resources": {"disk_space": "10GB"}
    }
}
```

**File-Based Detection:**
```python
FILE_INDICATORS = {
    "requirements.txt": "python_project",
    "*.csproj": "dotnet_project",
    "package.json": "node_project",
    "Dockerfile": "docker_required",
    "docker-compose.yml": "docker_compose_required"
}
```

### Validation Check Types (12+)

1. **SDK Version Checks**
   - Python: `python --version`
   - .NET: `dotnet --version`
   - Node: `node --version`
   - Go: `go version`

2. **Tool Availability Checks**
   - Docker: `docker --version`
   - Git: `git --version`
   - Make: `make --version`
   - CMake: `cmake --version`

3. **Permission Checks**
   - File write: Create temp file in workspace
   - Network: Ping external service
   - Docker socket: Access /var/run/docker.sock
   - Registry: Connect to container registry

4. **Resource Checks**
   - Disk space: Check available space (10GB min)
   - Memory: Check available RAM (4GB min)
   - Internet: Check connectivity
   - Port availability: Check required ports (8000, 5000, etc.)

5. **Environment Variable Checks**
   - Database connection strings
   - API keys (if required)
   - JWT secrets (if auth pattern detected)
   - Cloud credentials (if cloud deployment)

6. **Certificate Checks**
   - SSL certificates (if HTTPS)
   - Code signing certs (if deployment)
   - Client certificates (if mutual TLS)

### Health Report Format

```markdown
# 🏥 Pre-Flight Health Report

**Project:** UserAuthenticationFeature  
**Generated:** 2025-12-13 10:30:00  
**Total Checks:** 15  
**Status:** ⚠️ WARNINGS DETECTED

---

## ✅ PASSED (12 checks)

### SDK Checks
- ✅ Python 3.11.0 installed (required: >=3.8)
- ✅ pip 24.0 available
- ✅ virtualenv 20.26.0 available

### Tool Checks
- ✅ Git 2.43.0 available
- ✅ Docker 24.0.7 available
- ✅ Docker Compose 2.23.0 available

### Resource Checks
- ✅ Disk space: 250GB available (required: 10GB)
- ✅ Memory: 16GB available (required: 4GB)
- ✅ Internet connectivity: PASS

### Permission Checks
- ✅ File write access: PASS
- ✅ Docker socket access: PASS
- ✅ Network access: PASS

---

## ⚠️ WARNINGS (3 checks)

### Optional Tools
- ⚠️ pytest not installed (recommended for TDD)
  - **Remediation:** `pip install pytest`
  - **Impact:** Manual testing required without pytest

- ⚠️ httpx not installed (recommended for API testing)
  - **Remediation:** `pip install httpx`
  - **Impact:** Limited API test capabilities

### Optional Environment
- ⚠️ GITHUB_TOKEN not set (optional for deployments)
  - **Remediation:** Set environment variable
  - **Impact:** Cannot deploy to GitHub Packages

---

## ❌ FAILURES (0 checks)

No critical failures detected.

---

## 🎯 Summary

**Status:** ✅ READY TO PROCEED  
**Blockers:** 0 CRITICAL failures  
**Warnings:** 3 optional issues

**Recommendation:** Proceed to Phase 1. Consider installing pytest and httpx for enhanced testing.

**Validation Script:** `pre-flight-validation.ps1` (execute to re-check)
```

---

## 📋 Implementation Steps

### Step 1: Requirements Detection (Day 1)
**Duration:** 6 hours  
**Owner:** Senior Engineer

**Tasks:**
- [ ] Create requirement detector module
- [ ] Implement pattern-based detection (FastAPI, .NET, Docker, JWT, etc.)
- [ ] Implement file-based detection (requirements.txt, *.csproj, package.json)
- [ ] Build dependency graph (transitive requirements)
- [ ] Add support for custom patterns (user-defined)

**Code Structure:**
```python
# src/orchestrators/planning/requirement_detector.py

from typing import Dict, List, Set
from pathlib import Path

class RequirementDetector:
    """Detect environment requirements from project patterns."""
    
    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.detected_patterns = set()
        self.requirements = {}
    
    def detect(self, feature_description: str, project_context: Dict) -> Dict:
        """Detect all environment requirements."""
        
        # Pattern-based detection
        self._detect_from_description(feature_description)
        self._detect_from_files()
        self._detect_from_dependencies()
        
        # Build requirement list
        self._build_requirements()
        
        return {
            "patterns": list(self.detected_patterns),
            "requirements": self.requirements
        }
    
    def _detect_from_description(self, description: str):
        """Detect patterns from feature description."""
        description_lower = description.lower()
        
        if any(kw in description_lower for kw in ["fastapi", "api", "rest"]):
            self.detected_patterns.add("fastapi")
        
        if any(kw in description_lower for kw in ["jwt", "authentication", "auth"]):
            self.detected_patterns.add("jwt_auth")
        
        if any(kw in description_lower for kw in ["docker", "container"]):
            self.detected_patterns.add("docker")
        
        # Add more pattern detection...
    
    def _detect_from_files(self):
        """Detect patterns from workspace files."""
        for file_pattern, pattern_name in FILE_INDICATORS.items():
            if list(self.workspace_path.glob(file_pattern)):
                self.detected_patterns.add(pattern_name)
    
    def _detect_from_dependencies(self):
        """Detect transitive dependencies."""
        if "fastapi" in self.detected_patterns:
            self.detected_patterns.add("python_project")
            self.detected_patterns.add("uvicorn")
    
    def _build_requirements(self):
        """Build consolidated requirement list."""
        for pattern in self.detected_patterns:
            pattern_reqs = PATTERN_REQUIREMENTS.get(pattern, {})
            self._merge_requirements(pattern_reqs)
```

**Deliverables:**
- Requirement detector module (200 lines)
- Pattern definitions (YAML config)
- Unit tests (15 test cases)

**Acceptance Criteria:**
- [ ] Detects 8+ common patterns
- [ ] File-based detection working
- [ ] Transitive dependencies resolved
- [ ] Test coverage > 85%

---

### Step 2: Validation Framework (Day 1-2)
**Duration:** 8 hours  
**Owner:** Senior Engineer

**Tasks:**
- [ ] Create validation framework base
- [ ] Implement SDK version checkers (Python, .NET, Node, Go)
- [ ] Implement tool availability checkers (Docker, Git, etc.)
- [ ] Implement permission checkers (file, network, docker socket)
- [ ] Implement resource checkers (disk, memory, internet)
- [ ] Add retry logic for transient failures

**Code Structure:**
```python
# src/orchestrators/planning/validators.py

from abc import ABC, abstractmethod
from typing import Dict, Optional
import subprocess

class Validator(ABC):
    """Base validator class."""
    
    @abstractmethod
    def validate(self) -> ValidationResult:
        """Run validation check."""
        pass

class SDKValidator(Validator):
    """Validate SDK version."""
    
    def __init__(self, sdk_name: str, required_version: str):
        self.sdk_name = sdk_name
        self.required_version = required_version
    
    def validate(self) -> ValidationResult:
        """Check SDK version."""
        try:
            if self.sdk_name == "python":
                result = subprocess.run(
                    ["python", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                version = result.stdout.strip().split()[1]
                
                if self._version_compare(version, self.required_version):
                    return ValidationResult.success(
                        f"{self.sdk_name} {version} meets requirement {self.required_version}"
                    )
                else:
                    return ValidationResult.failure(
                        f"{self.sdk_name} {version} does not meet requirement {self.required_version}",
                        remediation=f"Install Python {self.required_version} or higher"
                    )
        
        except FileNotFoundError:
            return ValidationResult.failure(
                f"{self.sdk_name} not found",
                remediation=f"Install {self.sdk_name} {self.required_version}"
            )
        
        except subprocess.TimeoutExpired:
            return ValidationResult.failure(
                f"{self.sdk_name} check timeout",
                remediation="Check if SDK is frozen or corrupted"
            )

class ToolValidator(Validator):
    """Validate tool availability."""
    
    def __init__(self, tool_name: str, is_optional: bool = False):
        self.tool_name = tool_name
        self.is_optional = is_optional
    
    def validate(self) -> ValidationResult:
        """Check if tool is available."""
        try:
            result = subprocess.run(
                [self.tool_name, "--version"],
                capture_output=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return ValidationResult.success(
                    f"{self.tool_name} is available"
                )
            else:
                severity = "WARN" if self.is_optional else "FAIL"
                return ValidationResult(
                    status=severity,
                    message=f"{self.tool_name} not found",
                    remediation=f"Install {self.tool_name}"
                )
        
        except Exception as e:
            severity = "WARN" if self.is_optional else "FAIL"
            return ValidationResult(
                status=severity,
                message=f"{self.tool_name} check failed: {e}",
                remediation=f"Install {self.tool_name}"
            )

class ResourceValidator(Validator):
    """Validate system resources."""
    
    def __init__(self, resource_type: str, required_amount: str):
        self.resource_type = resource_type
        self.required_amount = required_amount
    
    def validate(self) -> ValidationResult:
        """Check resource availability."""
        if self.resource_type == "disk_space":
            return self._check_disk_space()
        elif self.resource_type == "memory":
            return self._check_memory()
        elif self.resource_type == "internet":
            return self._check_internet()
    
    def _check_disk_space(self) -> ValidationResult:
        """Check available disk space."""
        import shutil
        
        stats = shutil.disk_usage(Path.cwd())
        available_gb = stats.free / (1024**3)
        required_gb = int(self.required_amount.replace("GB", ""))
        
        if available_gb >= required_gb:
            return ValidationResult.success(
                f"Disk space: {available_gb:.1f}GB available (required: {required_gb}GB)"
            )
        else:
            return ValidationResult.failure(
                f"Insufficient disk space: {available_gb:.1f}GB available (required: {required_gb}GB)",
                remediation="Free up disk space before proceeding"
            )
```

**Deliverables:**
- Validation framework (250 lines)
- 6 validator types implemented
- Retry logic for transient failures
- Unit tests (25 test cases)

**Acceptance Criteria:**
- [ ] All 12+ check types implemented
- [ ] Timeout handling (5 seconds max per check)
- [ ] Graceful error handling
- [ ] Test coverage > 90%

---

### Step 3: Script Generator (Day 2-3)
**Duration:** 6 hours  
**Owner:** Senior Engineer

**Tasks:**
- [ ] Create script generator module
- [ ] Implement PowerShell template (Windows)
- [ ] Implement Bash template (Linux/Mac)
- [ ] Add remediation commands (SDK installs, tool installs)
- [ ] Generate user-executable scripts

**Script Templates:**

**PowerShell Template:**
```powershell
# pre-flight-validation.ps1
# Generated: {{ timestamp }}
# Project: {{ project_name }}

Write-Host "🏥 Pre-Flight Validation Script" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

$totalChecks = 0
$passedChecks = 0
$failedChecks = 0
$warnings = 0

# SDK Checks
Write-Host "`n✓ SDK Version Checks" -ForegroundColor Green

{% for sdk in sdk_checks %}
Write-Host "  Checking {{ sdk.name }}..." -NoNewline
$totalChecks++

try {
    $version = & {{ sdk.command }} --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " PASS ($version)" -ForegroundColor Green
        $passedChecks++
    } else {
        Write-Host " FAIL" -ForegroundColor Red
        Write-Host "    Remediation: {{ sdk.remediation }}" -ForegroundColor Yellow
        $failedChecks++
    }
} catch {
    Write-Host " FAIL (not found)" -ForegroundColor Red
    Write-Host "    Remediation: {{ sdk.remediation }}" -ForegroundColor Yellow
    $failedChecks++
}
{% endfor %}

# Summary
Write-Host "`n=================================" -ForegroundColor Cyan
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "  Total Checks: $totalChecks"
Write-Host "  Passed: $passedChecks" -ForegroundColor Green
Write-Host "  Failed: $failedChecks" -ForegroundColor Red
Write-Host "  Warnings: $warnings" -ForegroundColor Yellow

if ($failedChecks -gt 0) {
    Write-Host "`n❌ VALIDATION FAILED" -ForegroundColor Red
    Write-Host "Fix the issues above before proceeding." -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "`n✅ VALIDATION PASSED" -ForegroundColor Green
    Write-Host "Environment is ready!" -ForegroundColor Green
    exit 0
}
```

**Deliverables:**
- Script generator module (150 lines)
- PowerShell template
- Bash template
- Template rendering engine

**Acceptance Criteria:**
- [ ] Generates executable scripts
- [ ] Scripts work on Windows/Linux/Mac
- [ ] Includes remediation commands
- [ ] User can run independently

---

### Step 4: Health Report Builder (Day 3)
**Duration:** 4 hours  
**Owner:** Engineer

**Tasks:**
- [ ] Create health report builder
- [ ] Implement markdown report generation
- [ ] Add severity classification (PASS/WARN/FAIL)
- [ ] Include remediation steps
- [ ] Generate summary statistics

**Code Structure:**
```python
# src/orchestrators/planning/health_report_builder.py

class HealthReportBuilder:
    """Build pre-flight health report."""
    
    def __init__(self):
        self.results = []
    
    def add_result(self, result: ValidationResult):
        """Add validation result."""
        self.results.append(result)
    
    def build(self) -> str:
        """Generate markdown report."""
        passed = [r for r in self.results if r.status == "PASS"]
        warnings = [r for r in self.results if r.status == "WARN"]
        failures = [r for r in self.results if r.status == "FAIL"]
        
        status_emoji = "❌" if failures else "⚠️" if warnings else "✅"
        status_text = "FAILURES DETECTED" if failures else "WARNINGS DETECTED" if warnings else "ALL CHECKS PASSED"
        
        report = f"""# 🏥 Pre-Flight Health Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Total Checks:** {len(self.results)}  
**Status:** {status_emoji} {status_text}

---

## ✅ PASSED ({len(passed)} checks)

{self._format_results(passed)}

---

## ⚠️ WARNINGS ({len(warnings)} checks)

{self._format_results(warnings)}

---

## ❌ FAILURES ({len(failures)} checks)

{self._format_results(failures)}

---

## 🎯 Summary

**Status:** {'❌ BLOCKED' if failures else '✅ READY TO PROCEED'}  
**Blockers:** {len(failures)} CRITICAL failures  
**Warnings:** {len(warnings)} optional issues

**Recommendation:** {self._get_recommendation(failures, warnings)}
"""
        return report
    
    def _format_results(self, results: List[ValidationResult]) -> str:
        """Format result list."""
        if not results:
            return "No issues in this category.\n"
        
        output = []
        for result in results:
            emoji = "✅" if result.status == "PASS" else "⚠️" if result.status == "WARN" else "❌"
            output.append(f"- {emoji} {result.message}")
            if result.remediation:
                output.append(f"  - **Remediation:** {result.remediation}")
        
        return "\n".join(output)
```

**Deliverables:**
- Health report builder (150 lines)
- Markdown template
- Severity classification logic
- Unit tests (10 test cases)

**Acceptance Criteria:**
- [ ] Generates readable markdown reports
- [ ] Includes all result categories
- [ ] Clear remediation steps
- [ ] Test coverage > 85%

---

### Step 5: Gate Enforcement Logic (Day 3-4)
**Duration:** 4 hours  
**Owner:** Engineer

**Tasks:**
- [ ] Create gate enforcer module
- [ ] Implement BLOCK logic (any FAIL → stop)
- [ ] Implement WARN logic (allow proceed with warnings)
- [ ] Add user override capability (force proceed)
- [ ] Log gate decisions

**Code Structure:**
```python
# src/orchestrators/planning/gate_enforcer.py

class GateEnforcer:
    """Enforce pre-flight gate checks."""
    
    def __init__(self, allow_warnings: bool = True, allow_override: bool = False):
        self.allow_warnings = allow_warnings
        self.allow_override = allow_override
    
    def enforce(self, results: List[ValidationResult]) -> GateDecision:
        """Enforce gate based on validation results."""
        
        failures = [r for r in results if r.status == "FAIL"]
        warnings = [r for r in results if r.status == "WARN"]
        
        if failures:
            if self.allow_override:
                return GateDecision.warn_blocked(
                    f"{len(failures)} CRITICAL failures detected. Override available but not recommended.",
                    failures
                )
            else:
                return GateDecision.blocked(
                    f"{len(failures)} CRITICAL failures detected. Must fix before proceeding.",
                    failures
                )
        
        if warnings and not self.allow_warnings:
            return GateDecision.blocked(
                f"{len(warnings)} warnings detected and warnings not allowed.",
                warnings
            )
        
        if warnings:
            return GateDecision.pass_with_warnings(
                f"All critical checks passed. {len(warnings)} warnings detected.",
                warnings
            )
        
        return GateDecision.passed("All checks passed. Ready to proceed.")
```

**Deliverables:**
- Gate enforcer module (100 lines)
- Decision logic (BLOCK/WARN/PASS)
- Override capability
- Unit tests (15 test cases)

**Acceptance Criteria:**
- [ ] BLOCK on any FAIL
- [ ] WARN on optional issues
- [ ] Override available (if enabled)
- [ ] All decisions logged

---

### Step 6: Planning System Integration (Day 4)
**Duration:** 6 hours  
**Owner:** Tech Lead

**Tasks:**
- [ ] Integrate pre-flight into Planning System 2.0
- [ ] Add Phase 0 (pre-flight) before Phase 1
- [ ] Update manifest with pre-flight requirements
- [ ] Test end-to-end workflow
- [ ] Update progress tracker

**Integration Points:**
```python
# src/orchestrators/planning/planning_orchestrator.py (MODIFIED)

class PlanningOrchestrator:
    def execute_plan(self, plan: Plan):
        """Execute plan with pre-flight check."""
        
        # Phase 0: Pre-Flight (NEW)
        logger.info("🎭 Phase transition: PLANNING → PRE-FLIGHT")
        pre_flight = PreFlightOrchestrator(
            workspace_path=plan.workspace_path,
            feature_description=plan.description,
            project_context=plan.context
        )
        
        gate_decision = pre_flight.execute()
        
        if gate_decision.is_blocked():
            logger.error(f"Pre-flight BLOCKED: {gate_decision.message}")
            self._generate_blocker_report(gate_decision)
            return PlanResult.blocked(gate_decision)
        
        if gate_decision.has_warnings():
            logger.warning(f"Pre-flight WARNINGS: {gate_decision.message}")
            # Continue with warnings
        
        logger.info("✅ Pre-flight PASSED")
        logger.info("🎭 Phase transition: PRE-FLIGHT → PHASE_1")
        
        # Phase 1: Feature Implementation
        # ... existing code ...
```

**Deliverables:**
- Planning System integration
- Updated manifest
- End-to-end tests
- Progress tracker updates

**Acceptance Criteria:**
- [ ] Pre-flight runs before Phase 1
- [ ] Gate enforcement working
- [ ] No breaking changes
- [ ] All tests passing

---

### Step 7: Testing & Documentation (Day 5)
**Duration:** 8 hours  
**Owner:** QA + Tech Writer

**Tasks:**
- [ ] Write integration tests (30+ test cases)
- [ ] Test all 12+ check types
- [ ] Test gate enforcement scenarios
- [ ] Create user documentation
- [ ] Create developer guide

**Test Scenarios:**
- All checks pass → READY
- One FAIL → BLOCKED
- Multiple WARN → PASS WITH WARNINGS
- Missing SDK → Generate correct remediation
- Script execution → User can fix issues

**Documentation:**
- User guide: How to interpret health reports
- Developer guide: Adding new validators
- Troubleshooting guide: Common issues

**Deliverables:**
- Integration test suite (30+ tests)
- User documentation
- Developer guide
- Troubleshooting guide

**Acceptance Criteria:**
- [ ] Test coverage > 85%
- [ ] All documentation complete
- [ ] User guide reviewed

---

## 🧪 Testing Strategy

### Unit Tests (50+ tests)
- Requirement detector (15 tests)
- Validators (25 tests)
- Script generator (5 tests)
- Health report builder (5 tests)

### Integration Tests (30+ tests)
- End-to-end pre-flight execution
- Gate enforcement scenarios
- Script generation and execution
- Planning System integration

### Performance Tests (3 benchmarks)
- Validation time (< 15 seconds)
- Script generation time (< 2 seconds)
- Memory usage (< 100MB)

---

## 📊 Success Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Detection Coverage | 12+ checks | TBD | ⏳ |
| Blocker Prevention | 100% | TBD | ⏳ |
| Execution Time | < 15s | TBD | ⏳ |
| False Positives | < 5% | TBD | ⏳ |
| Test Coverage | > 85% | TBD | ⏳ |

---

## 🚧 Risks & Mitigation

### Risk 1: Platform-Specific Validation Failures
**Probability:** Medium | **Impact:** High

**Mitigation:**
- Test on Windows, Linux, macOS
- Use cross-platform libraries (shutil, psutil)
- Fallback to generic checks if platform-specific fails

### Risk 2: False Positives (Blocking Valid Environments)
**Probability:** Medium | **Impact:** High

**Mitigation:**
- Extensive testing on diverse environments
- User override capability
- Monitor false positive rate (< 5% target)

---

## 🔗 Dependencies

### Upstream Dependencies
- Phase 0: Intent Routing (needs accurate feature detection)

### Downstream Dependents
- Phase 4: Autonomous Executor (uses pre-flight gates)
- All planning workflows (require environment validation)

---

## 📚 References

- Master Plan: `MASTER-CORTEX-ORCHESTRATION-AST-ENHANCEMENT-PLAN.md`
- PrevalidationWS Chat01: Evidence of 2-week blocker
- Planning System 2.0: `cortex-brain/manifests/orchestrators/planning-system-2.0-manifest.yaml`

---

## 🔍 Next Steps

1. **Phase 2 Kickoff:** Create Progress Synchronizer after Phase 1 complete
2. **Production Monitoring:** Track blocker prevention rate
3. **Pattern Library Expansion:** Add more domain patterns

---

**Phase Status:** 🚀 READY TO START  
**Estimated Completion:** Week 2, Day 5  
**Estimated LOC:** 400 (implementation) + 300 (tests) = 700 total

**Author:** Asif Hussain  
**Created:** December 13, 2025  
**Last Updated:** December 13, 2025
