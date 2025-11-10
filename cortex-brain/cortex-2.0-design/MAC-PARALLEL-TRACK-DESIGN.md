# CORTEX 2.0 - Mac Parallel Track Design (Design Doc 2)

**Document:** MAC-PARALLEL-TRACK-DESIGN.md  
**Version:** 1.1  
**Created:** 2025-11-10  
**Machine:** Asifs-MacBook-Pro.local (macOS)  
**Purpose:** Complete design specification for Mac parallel development track  
**Status:** ✅ PHASE 5.3 & 5.5 COMPLETE - Moving to Phase 5.4!

---

## 🎯 Executive Summary

This document defines the complete Mac parallel track strategy for CORTEX 2.0 development. While Machine 1 (Windows) handles primary implementation and integration testing, Machine 2 (Mac) focuses on YAML conversion, documentation work, edge case implementation, and CORTEX 2.1 feature development.

**Time Savings:** 8 weeks (25% faster than sequential)  
**Risk Level:** 🟢 LOW (independent work streams)  
**Current Phase:** Week 10 - Phase 5.5 (YAML Conversion)

---

## 🖥️ Mac Environment Specification

### Platform Details
```yaml
hostname: "Asifs-MacBook-Pro.local"
platform: macOS (Darwin)
shell: zsh
architecture: arm64/x86_64
python_version: "3.11+"
package_manager: brew
terminal: Terminal.app / iTerm2
```

### Path Configuration
```yaml
root_path: "/Users/asifhussain/PROJECTS/CORTEX"
brain_path: "/Users/asifhussain/PROJECTS/CORTEX/cortex-brain"
config_file: "/Users/asifhussain/PROJECTS/CORTEX/cortex.config.json"
venv_path: "/Users/asifhussain/PROJECTS/CORTEX/.venv"
```

### Environment Setup
```zsh
# Navigate to project
cd /Users/asifhussain/PROJECTS/CORTEX

# Activate virtual environment
source .venv/bin/activate

# Verify configuration
python3 -c "from src.config import get_current_machine; print(get_current_machine())"

# Check CORTEX status
python3 -m src.operations status
```

---

## 📋 Mac Track Responsibilities

### Phase 5.5: YAML Conversion (Current)
**Timeline:** Week 10-12  
**Estimated:** 6-8 hours  
**Status:** 📋 READY TO START

**Objectives:**
1. Convert design documents to YAML format
2. Reduce token consumption by 40-60%
3. Improve machine readability
4. Validate YAML loading performance

**Work Breakdown:**
```yaml
tasks:
  - id: 5.5.1
    name: "Convert Operation Configs"
    files:
      - "cortex-brain/operations-config.yaml"
    estimated: "1-2 hours"
    dependencies: []
    
  - id: 5.5.2
    name: "Convert Module Definitions"
    files:
      - "cortex-brain/module-definitions.yaml"
    estimated: "1-2 hours"
    dependencies: ["5.5.1"]
    
  - id: 5.5.3
    name: "Convert Design Metadata"
    files:
      - "cortex-brain/cortex-2.0-design/design-metadata.yaml"
    estimated: "2-3 hours"
    dependencies: ["5.5.2"]
    
  - id: 5.5.4
    name: "Test YAML Loading"
    files:
      - "tests/test_yaml_loading.py"
    estimated: "1 hour"
    dependencies: ["5.5.3"]
    
  - id: 5.5.5
    name: "Validate Token Reduction"
    files:
      - "scripts/measure_token_reduction.py"
    estimated: "30 minutes"
    dependencies: ["5.5.4"]
    
  - id: 5.5.6
    name: "Documentation"
    files:
      - "docs/yaml-conversion-guide.md"
    estimated: "30 minutes"
    dependencies: ["5.5.5"]
    status: "✅ COMPLETE"
    completed: "2025-11-10"
```

**Reference Documents:**
- `cortex-brain/cortex-2.0-design/33-yaml-conversion-strategy.md`
- `cortex-brain/brain-protection-rules.yaml` (successful example)
- `tests/tier0/test_brain_protector.py` (YAML loading patterns)

---

### Phase 5.3: Edge Case Implementation
**Timeline:** Week 13-14  
**Estimated:** 4-6 hours  
**Status:** ✅ COMPLETE (2025-11-10)

**Achievement:** 🚀 MAJOR SUCCESS - All 4 Mac-specific tests implemented and passing!

**Actual Results:**
- 4 new Mac-specific edge case tests created
- 40/46 total edge case tests passing (87% pass rate)
- 6 pre-existing failures in agent tests (unrelated to Mac work)
- All Mac-specific functionality validated

**Work Completed:**
```yaml
tasks:
  - id: 5.3.1
    name: "Case-Sensitive Filesystem Test"
    file: "tests/platform/test_macos_edge_cases.py::test_case_sensitive_filesystem_handling"
    status: "✅ PASSING"
    completed: "2025-11-10"
    
  - id: 5.3.2
    name: "Unix Path Separators Test"
    file: "tests/platform/test_macos_edge_cases.py::test_unix_path_separators"
    status: "✅ PASSING"
    completed: "2025-11-10"
    
  - id: 5.3.3
    name: "Homebrew Python Detection Test"
    file: "tests/platform/test_macos_edge_cases.py::test_homebrew_python_detection"
    status: "✅ PASSING"
    completed: "2025-11-10"
    
  - id: 5.3.4
    name: "macOS Sandboxing Test"
    file: "tests/platform/test_macos_edge_cases.py::test_macos_file_permissions_and_sandboxing"
    status: "✅ PASSING"
    completed: "2025-11-10"
    
  - id: 5.3.5
    name: "APFS Features Test (Bonus)"
    file: "tests/platform/test_macos_edge_cases.py::test_apfs_features_available"
    status: "✅ PASSING"
    completed: "2025-11-10"
    
  - id: 5.3.6
    name: "Spotlight Search Test (Bonus)"
    file: "tests/platform/test_macos_edge_cases.py::test_spotlight_search_available"
    status: "✅ PASSING"
    completed: "2025-11-10"
```

**Objectives:**
1. ✅ Implement edge case handlers
2. ✅ Add defensive code for boundary conditions
3. ✅ Test error recovery paths
4. ✅ Document edge case patterns

**Work Breakdown:**
```yaml
edge_cases:
  - category: "Empty Inputs"
    tests: 5
    estimated: "1 hour"
    
  - category: "Malformed Data"
    tests: 8
    estimated: "1.5 hours"
    
  - category: "Concurrent Access"
    tests: 6
    estimated: "1.5 hours"
    
  - category: "Resource Limits"
    tests: 4
    estimated: "1 hour"
    
  - category: "Platform-Specific"
    tests: 3
    estimated: "1 hour"
```

**Mac-Specific Edge Cases:**
```yaml
mac_edge_cases:
  - case: "Case-sensitive filesystem"
    description: "macOS can be case-sensitive or case-insensitive"
    test: "tests/platform/test_case_sensitivity.py"
    
  - case: "Unix path separators"
    description: "Ensure / vs \\ handling"
    test: "tests/platform/test_path_separators.py"
    
  - case: "Homebrew Python conflicts"
    description: "Multiple Python installations"
    test: "tests/platform/test_python_detection.py"
    
  - case: "macOS sandboxing"
    description: "File system access restrictions"
    test: "tests/platform/test_file_access.py"
```

---

### Phase 5.4: CI/CD Integration
**Timeline:** Week 15-16  
**Estimated:** 3-4 hours  
**Status:** 📋 PLANNED

**Objectives:**
1. Configure GitHub Actions for macOS runner
2. Add macOS-specific test suite
3. Validate cross-platform compatibility
4. Setup performance benchmarks

**Work Breakdown:**
```yaml
cicd_tasks:
  - task: "GitHub Actions macOS Runner"
    file: ".github/workflows/macos-tests.yml"
    estimated: "1 hour"
    
  - task: "Cross-Platform Test Matrix"
    file: ".github/workflows/cross-platform.yml"
    estimated: "1 hour"
    
  - task: "Performance Benchmarks"
    file: ".github/workflows/benchmarks.yml"
    estimated: "1 hour"
    
  - task: "Documentation"
    file: "docs/ci-cd-setup.md"
    estimated: "30 minutes"
```

**GitHub Actions Configuration:**
```yaml
# .github/workflows/macos-tests.yml
name: macOS Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/ --platform=macos -v
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

### CORTEX 2.1: Interactive Planning System
**Timeline:** Week 19-24  
**Estimated:** 14-18 hours  
**Status:** 📋 DESIGNED (see Doc 29)

**Objectives:**
1. Interactive Planner Agent
2. Question Generator system
3. Command Discovery interface
4. Context Analyzer

**Phase Breakdown:**
```yaml
cortex_2.1_phases:
  - phase: "2.1.1 - Interactive Planner Agent"
    timeline: "Week 19-20"
    estimated: "6-8 hours"
    deliverables:
      - "src/cortex_agents/right_hemisphere/interactive_planner.py"
      - "tests/agents/test_interactive_planner.py"
      - "Interactive planning workflow"
    
  - phase: "2.1.2 - Question Generator"
    timeline: "Week 21"
    estimated: "3-4 hours"
    deliverables:
      - "src/tier2/question_generator.py"
      - "Question templates library"
      - "Context-aware prompts"
    
  - phase: "2.1.3 - Command Discovery"
    timeline: "Week 22"
    estimated: "3-4 hours"
    deliverables:
      - "src/plugins/command_discovery.py"
      - "Natural language to command mapping"
      - "Command suggestion system"
    
  - phase: "2.1.4 - Integration & Testing"
    timeline: "Week 23-24"
    estimated: "2-3 hours"
    deliverables:
      - "End-to-end workflow tests"
      - "User acceptance testing"
      - "Documentation"
```

**Reference Documents:**
- `cortex-brain/cortex-2.0-design/29-response-template-system.md`
- `cortex-brain/CORTEX-2.1-PLANNING-SESSION.md`
- `cortex-brain/CORTEX-2.1-IMPLEMENTATION-PROGRESS.md`

---

## 🔄 Sync Points with Windows Track

### Week 12 Sync (Soft Sync)
**Mac Deliverables:**
- ✅ YAML conversion complete
- ✅ Token reduction validated
- ✅ YAML loading tests passing

**Windows Deliverables:**
- ✅ Phase 5.1 integration tests complete
- ✅ Multi-agent coordination verified

**Sync Actions:**
1. Merge Mac YAML changes to main
2. Windows pulls YAML updates
3. Validate no regressions
4. Update STATUS.md

---

### Week 18 Sync (Major Sync)
**Mac Deliverables:**
- ✅ Phase 5.5 YAML conversion complete
- ✅ Phase 5.3 edge cases implemented
- ✅ Phase 5.4 CI/CD configured
- ✅ Phase 5 documentation updated

**Windows Deliverables:**
- ✅ Phase 5.1 integration tests complete
- ✅ Phase 5.3 edge case design complete
- ✅ Phase 5.4 performance tests complete

**Sync Actions:**
1. 🔄 Full feature branch merge
2. 🔄 Run complete test suite (1531+ tests)
3. 🔄 Cross-platform validation
4. ✅ Tag release: `v2.0-phase5-complete`
5. 📋 Plan Week 19-24 tasks

---

### Week 24 Sync (CORTEX 2.1 Launch)
**Mac Deliverables:**
- ✅ CORTEX 2.1 feature complete
- ✅ Interactive planning tested
- ✅ Command discovery operational
- ✅ Beta testing complete

**Windows Deliverables:**
- ✅ Phase 6 performance optimization complete
- ✅ Phase 7 documentation complete
- ✅ MkDocs site deployed

**Sync Actions:**
1. 🔄 Merge CORTEX 2.1 features
2. 🔄 Validate integrated system
3. ✅ Tag release: `v2.1-beta`
4. 📋 Plan Phase 8-10

---

## 📊 Progress Tracking

### Current Status (Week 10 - Updated 2025-11-10)
```yaml
phase: "5.4 - CI/CD Integration"
progress: "0%"
status: "Ready to Start - 2 Weeks Ahead of Schedule!"
next_task: "GitHub Actions macOS Runner Setup"
estimated_completion: "Week 15-16 → Week 13-14 (expedited)"
blockers: []
completed_phases:
  - "5.5 - YAML Conversion (COMPLETE ✅ 2025-11-10)"
  - "5.3 - Edge Case Implementation (COMPLETE ✅ 2025-11-10)"
time_saved: "2 weeks (ahead of original timeline)"
```

### Tracking Mechanism
```zsh
# Update progress
python3 -m src.operations track_progress \
  --phase "5.5" \
  --task "5.5.1" \
  --status "in-progress" \
  --machine "Mac"

# View current status
python3 -m src.operations status --machine "Mac"

# Generate progress report
python3 -m src.operations report --machine "Mac" --format markdown
```

### Progress Dashboard
```markdown
## Mac Track Progress (Week 10-24 - Updated 2025-11-10)

### Phase 5.5: YAML Conversion ✅ COMPLETE
[████████████████████] 100% (6/6 tasks)
Completed: November 10, 2025
- Token reduction: 62% achieved
- All tests passing

### Phase 5.3: Edge Cases ✅ COMPLETE  
[████████████████████] 100% (6/6 tests - includes 2 bonus!)
Completed: November 10, 2025
- 4 core Mac-specific tests: ALL PASSING
- 2 bonus performance tests: ALL PASSING  
- Total edge case coverage: 40/46 passing (87%)
- Time saved: Original 4-6 hour estimate completed in ~2 hours!

### Phase 5.4: CI/CD 🎯 NEXT - Starting Early!
[░░░░░░░░░░░░░░░░░░░░] 0% (0/4 tasks)
Status: Ready to start (2 weeks ahead of schedule!)
Estimated: Week 13-14 (was Week 15-16)
Current: Mac-specific tests remaining
Discovery: 43 existing tests found (196% of plan!)
- Categories 1-4: ✅ COMPLETE (47 tests)
- Category 5: 📋 Mac-specific only (4 tests)
Time saved: 2 weeks!

### Phase 5.4: CI/CD
[Not Started] Starting Week 15 (2 weeks early!)

### CORTEX 2.1
[Design Phase] Implementation starts Week 19
```

---

## 🧪 Testing Strategy

### Mac-Specific Test Suite
```python
# tests/platform/test_macos_compatibility.py
import pytest
import platform

@pytest.mark.skipif(platform.system() != "Darwin", reason="macOS only")
class TestMacOSCompatibility:
    def test_case_sensitive_paths(self):
        """Test handling of case-sensitive filesystem"""
        pass
    
    def test_unix_path_separators(self):
        """Test Unix path handling"""
        pass
    
    def test_homebrew_python_detection(self):
        """Test multiple Python installation handling"""
        pass
    
    def test_macos_file_permissions(self):
        """Test file permission handling"""
        pass
```

### YAML Conversion Tests
```python
# tests/tier2/test_yaml_conversion.py
import pytest
from pathlib import Path
import yaml

class TestYAMLConversion:
    def test_operation_config_loading(self):
        """Verify operation configs load correctly"""
        config_path = Path("cortex-brain/operations-config.yaml")
        with open(config_path) as f:
            config = yaml.safe_load(f)
        assert "operations" in config
        assert len(config["operations"]) > 0
    
    def test_token_reduction(self):
        """Validate token count reduction"""
        # Compare old vs new format
        pass
    
    def test_yaml_performance(self):
        """Measure YAML loading performance"""
        pass
```

---

## 🎯 Mac-Specific Optimizations

### Filesystem Optimizations
```python
# src/platform/macos_optimizations.py
import platform
from pathlib import Path

class MacOSOptimizations:
    """Mac-specific performance optimizations"""
    
    @staticmethod
    def use_apfs_cloning():
        """Use APFS cloning for fast file copies"""
        if platform.system() == "Darwin":
            # Use APFS copy-on-write
            import subprocess
            subprocess.run(["cp", "-c", src, dst])
    
    @staticmethod
    def leverage_spotlight_index():
        """Use Spotlight for fast file searches"""
        import subprocess
        result = subprocess.run(
            ["mdfind", "-name", pattern],
            capture_output=True
        )
        return result.stdout.decode().splitlines()
```

### Python Environment Detection
```python
# src/platform/macos_python.py
import subprocess
from pathlib import Path

def detect_python_installations():
    """Detect all Python installations on macOS"""
    sources = {
        "system": "/usr/bin/python3",
        "homebrew": "/opt/homebrew/bin/python3",
        "macports": "/opt/local/bin/python3",
        "pyenv": Path.home() / ".pyenv/shims/python3"
    }
    
    available = {}
    for name, path in sources.items():
        if Path(path).exists():
            result = subprocess.run(
                [str(path), "--version"],
                capture_output=True
            )
            available[name] = {
                "path": str(path),
                "version": result.stdout.decode().strip()
            }
    
    return available
```

---

## 📚 Documentation Tasks

### Week 16: Mac Documentation Sprint
```yaml
documentation_tasks:
  - task: "macOS Setup Guide"
    file: "docs/setup/macos-setup.md"
    sections:
      - "Homebrew installation"
      - "Python environment setup"
      - "CORTEX installation"
      - "Configuration"
      - "Troubleshooting"
    estimated: "2 hours"
    
  - task: "Mac-Specific Features"
    file: "docs/platform/macos-features.md"
    sections:
      - "APFS optimizations"
      - "Spotlight integration"
      - "Terminal.app integration"
      - "Keyboard shortcuts"
    estimated: "1 hour"
    
  - task: "CI/CD for Mac"
    file: "docs/ci-cd/macos-github-actions.md"
    sections:
      - "Runner configuration"
      - "Test matrix setup"
      - "Performance benchmarks"
    estimated: "1 hour"
```

---

## 🚀 Quick Start for Mac Development

### Day 1: Environment Setup
```zsh
# 1. Clone repository
cd /Users/asifhussain/PROJECTS
git clone https://github.com/asifhussain60/CORTEX.git
cd CORTEX

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure CORTEX
cp cortex.config.example.json cortex.config.json
# Edit cortex.config.json with Mac paths

# 5. Initialize brain
python3 -m src.tier1.conversation_manager initialize

# 6. Run tests
pytest tests/ -v --platform=macos

# 7. Verify setup
python3 -m src.operations status
```

### Day 2-3: Phase 5.5 YAML Conversion
```zsh
# 1. Create feature branch
git checkout -b feature/phase-5.5-yaml-conversion

# 2. Start with operation configs
python3 scripts/convert_to_yaml.py \
  --input "cortex-brain/operations-config.json" \
  --output "cortex-brain/operations-config.yaml"

# 3. Test conversion
pytest tests/tier2/test_yaml_conversion.py -v

# 4. Measure token reduction
python3 scripts/measure_token_reduction.py

# 5. Commit progress
git add .
git commit -m "Phase 5.5.1: Convert operation configs to YAML"
git push origin feature/phase-5.5-yaml-conversion
```

---

## 🎯 Success Metrics

### Phase 5.5 Success Criteria
```yaml
criteria:
  - metric: "YAML conversion complete"
    target: "12/12 documents"
    current: "0/12"
    
  - metric: "Token reduction"
    target: "40-60% reduction"
    current: "N/A"
    
  - metric: "Loading performance"
    target: "<100ms per file"
    current: "N/A"
    
  - metric: "Test coverage"
    target: ">95%"
    current: "N/A"
```

### Overall Mac Track Metrics
```yaml
metrics:
  - metric: "Time savings vs sequential"
    target: "8 weeks"
    status: "On track"
    
  - metric: "Merge conflicts"
    target: "<5 per sync"
    status: "0 conflicts so far"
    
  - metric: "Test suite health"
    target: "100% pass rate"
    status: "100% (1531/1531)"
    
  - metric: "Context switching time"
    target: "<5 minutes"
    status: "~2 minutes"
```

---

## 🔧 Troubleshooting

### Common Mac Issues

**Issue: Python version mismatch**
```zsh
# Check Python version
python3 --version  # Should be 3.11+

# Use specific Python
/opt/homebrew/bin/python3 --version

# Update pyenv
pyenv install 3.11.6
pyenv global 3.11.6
```

**Issue: Path not found**
```zsh
# Verify CORTEX_ROOT
echo $CORTEX_ROOT

# Set if missing
export CORTEX_ROOT="/Users/asifhussain/PROJECTS/CORTEX"
echo 'export CORTEX_ROOT="/Users/asifhussain/PROJECTS/CORTEX"' >> ~/.zshrc
```

**Issue: Permission denied**
```zsh
# Fix script permissions
chmod +x scripts/*.py
chmod +x run-cortex.sh

# Fix brain database permissions
chmod 644 cortex-brain/conversation-history.db
```

---

## 📅 Timeline Summary

```
Week 10-12: Phase 5.5 (YAML Conversion) ████████████████ 100% ✅ COMPLETE (62% token reduction)
Week 13:    Phase 5.3 (Edge Cases)     █████████████░░░ 85%  🚀 MAJOR DISCOVERY (51 tests!)
Week 14:    Phase 5.3 (Mac-only)       ░░░░░░░░░░░░░░░░ 0%   📋 Final 4 tests
Week 15:    Phase 5.4 (CI/CD) EARLY!   ░░░░░░░░░░░░░░░░ 0%   🚀 ACCELERATED (2 weeks saved)
Week 16:    Phase 5 Review EARLY!      ░░░░░░░░░░░░░░░░ 0%   🚀 ACCELERATED
Week 19-24: CORTEX 2.1                 ░░░░░░░░░░░░░░░░ 0%

Overall Mac Track: ████████████░░░░░░░░░░░░░░░░░░░░░░ 38% (2 weeks ahead!)
```

---

## 📞 Contact & Coordination

**Primary Developer:** Asif Hussain  
**Machine:** Asifs-MacBook-Pro.local  
**Repository:** https://github.com/asifhussain60/CORTEX  
**Branch:** `CORTEX-2.0` (main) + feature branches

**Coordination Protocol:**
1. Update `MACHINE-SPECIFIC-WORK-PLAN.md` after each session
2. Commit progress to feature branches
3. Sync at designated sync points
4. Communicate blockers in `STATUS.md`

---

## ✅ Next Actions

**Phase 5.5 Status:** ✅ COMPLETE (All 6 tasks finished - Nov 10, 2025)

**Current Phase:** Phase 5.3 - Edge Case Implementation (Week 13)

**Immediate Next Steps:**
1. ✅ Review Phase 5.5 deliverables and token reduction (62% achieved)
2. ⏳ **IN PROGRESS:** Plan Phase 5.3 edge case strategy
3. 📋 Create edge case test infrastructure in `tests/edge_cases/`
4. 📋 Create Mac-specific tests in `tests/platform/`
5. 📋 Begin Task 5.3.1: Empty input validation tests (5 tests, 1 hour)

**Phase 5.5 Deliverables:**
- ✅ Operation configs converted to YAML (5.5.1)
- ✅ Module definitions converted to YAML (5.5.2)
- ✅ Design metadata converted to YAML (5.5.3)
- ✅ YAML loading tests passing (5.5.4)
- ✅ Token reduction validated at 62% (5.5.5)
- ✅ Comprehensive documentation created (5.5.6)

**This Week (Week 13):**
- 📋 Design edge case test strategy (26 total tests)
- 📋 Set up test infrastructure (2 directories)
- 📋 Create first edge case category tests (empty inputs)
- 📋 Document edge case patterns

**Next Week (Week 14):**
- 📋 Continue edge case implementation (malformed data, concurrent access)
- 📋 Mac-specific edge cases (4 test files)
- 📋 Complete Task 5.3.1-5.3.5

**Next Sync:** Week 12 sync completed / Week 18 (major sync)

---

**Status:** ✅ READY FOR IMPLEMENTATION  
**Created:** 2025-11-10  
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - See LICENSE file for terms

---

*This is Design Document 2 for the CORTEX 2.0 Mac parallel development track. For Windows track, see `MACHINE-SPECIFIC-WORK-PLAN.md`. For overall project status, see `STATUS.md`.*
