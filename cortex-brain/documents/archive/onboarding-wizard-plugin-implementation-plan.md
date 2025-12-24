# CORTEX Onboarding Wizard Plugin - Implementation Plan

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**Date:** 2025-11-15  
**Status:** Planning Phase - Ready for Review  
**Version:** 1.0.0

---

## 🎯 Executive Summary

This document outlines the implementation strategy for the **Onboarding Wizard Plugin**, which transforms the comprehensive onboarding flow design (cortex-onboarding-flow-design.yaml) into an executable CORTEX plugin that leverages the existing EPM (Execution Plan Module) foundation.

**Key Achievement:** We have a complete EPM foundation (`src/epm/`) ready to use. This plan focuses on building the plugin layer that orchestrates the 4-phase onboarding experience.

---

## 📚 Foundation Review

### ✅ What We Already Have

**EPM Foundation (src/epm/):**
- ✅ `OnboardingStep` - Base class for all steps with status tracking
- ✅ `StepRegistry` - Central registry with dependency resolution
- ✅ `OnboardingOrchestrator` - Execution engine with progress tracking
- ✅ `OnboardingProfile` - Quick/Standard/Comprehensive support
- ✅ `StepResult` - Rich result tracking with errors/warnings
- ✅ `StepDisplayFormat` - Multiple visualization options

**Plugin System:**
- ✅ `BasePlugin` - Foundation for all plugins
- ✅ Plugin Registry - Auto-discovery and registration
- ✅ Command Registry - Slash command integration

**Onboarding Design:**
- ✅ 4-Phase Architecture defined (Self-Setup, Introduction, Tutorial, Analysis)
- ✅ Progressive revelation strategy
- ✅ Leadership metrics identified
- ✅ Success criteria established

---

## 🏗️ Architecture Overview

```
User Says: "/CORTEX onboard yourself"
         ↓
┌────────────────────────────────────┐
│  Onboarding Wizard Plugin          │
│  (src/plugins/onboarding_wizard_   │
│   plugin.py)                        │
└────────────────────────────────────┘
         ↓
┌────────────────────────────────────┐
│  Onboarding Orchestrator            │
│  (src/epm/onboarding_orchestrator.  │
│   py)                               │
└────────────────────────────────────┘
         ↓
┌────────────────────────────────────┐
│  Step Registry                      │
│  (src/epm/step_registry.py)         │
│  - Dependency resolution            │
│  - Execution ordering               │
└────────────────────────────────────┘
         ↓
┌────────────────────────────────────┐
│  Individual Steps                   │
│  (src/epm/steps/*.py)                │
│  - EnvironmentDetectionStep         │
│  - DependencyInstallationStep       │
│  - BrainInitializationStep          │
│  - AgentActivationStep              │
│  - etc.                             │
└────────────────────────────────────┘
```

**Key Insight:** The orchestrator and registry are DONE. We need to:
1. Create the plugin wrapper (entry point integration)
2. Implement concrete step classes
3. Wire everything together

---

## 📋 Implementation Milestones

### Milestone 1: MVP - Self-Setup Only (2-3 days)

**Goal:** Get Phase 1 (Self-Setup) working end-to-end

**Scope:**
- Create `OnboardingWizardPlugin` with basic integration
- Implement core Phase 1 steps:
  - EnvironmentDetectionStep
  - DependencyInstallationStep
  - BrainInitializationStep
  - ValidationStep
- Basic CLI output (no fancy visualizations yet)
- Integration with CORTEX entry point

**Deliverables:**
- [ ] `src/plugins/onboarding_wizard_plugin.py`
- [ ] `src/epm/steps/__init__.py`
- [ ] `src/epm/steps/phase1_environment_detection.py`
- [ ] `src/epm/steps/phase1_dependency_installation.py`
- [ ] `src/epm/steps/phase1_brain_initialization.py`
- [ ] `src/epm/steps/phase1_validation.py`
- [ ] Test suite for Phase 1 steps
- [ ] Integration test for full Phase 1 flow

**Success Criteria:**
- User runs `/CORTEX onboard yourself`
- All Phase 1 steps execute successfully
- Brain directories created
- Dependencies installed
- Validation passes
- Progress tracked and displayed

---

### Milestone 2: Enhanced - Introduction & Basic Tutorial (3-4 days)

**Goal:** Add Phase 2 (Introduction) and simplified Phase 3 (Tutorial)

**Scope:**
- Phase 2: Full name reveal, mission statement, leadership metrics
- Phase 3 (Simplified): Memory demo, code analysis (no mermaid yet)
- Enhanced display formatting (progress bars, status reports)
- Session persistence (save/resume capability)

**Deliverables:**
- [ ] `src/epm/steps/phase2_introduction.py`
- [ ] `src/epm/steps/phase3_memory_demo.py`
- [ ] `src/epm/steps/phase3_code_analysis.py`
- [ ] Display formatters (progress bars, animated text)
- [ ] Session state persistence (JSON/YAML)
- [ ] Resume command support

**Success Criteria:**
- Full Phase 1 + Phase 2 + Basic Phase 3
- Leadership metrics displayed with formatting
- Memory demo shows Tier 1 conversations
- Code analysis generates insights (text format)
- Can pause and resume onboarding

---

### Milestone 3: Full - Complete Experience (4-5 days)

**Goal:** Complete all 4 phases with full visualization

**Scope:**
- Phase 3 (Full): All 7 tutorial modules
- Phase 4: Live application analysis with mermaid diagrams
- Advanced visualizations (mermaid rendering, interactive dashboards)
- Profile selection (Quick/Standard/Comprehensive)
- Executive summary generation

**Deliverables:**
- [ ] All Phase 3 modules (test generation, PR review, refactoring, health)
- [ ] Phase 4 application analysis with tech stack detection
- [ ] Mermaid diagram generator integration
- [ ] Profile selection UI
- [ ] Executive summary report generation
- [ ] Complete test coverage
- [ ] Documentation and examples

**Success Criteria:**
- All 4 phases working flawlessly
- Mermaid diagrams render correctly
- Profile selection works for Quick/Standard/Comprehensive
- Application analysis provides actionable insights
- Executive summary impresses leadership
- 100% test coverage for critical paths

---

## 🔧 Technical Specification: Phase 1 (MVP)

### Plugin Structure

```python
# src/plugins/onboarding_wizard_plugin.py

from src.plugins.base_plugin import BasePlugin, PluginMetadata
from src.plugins.command_registry import CommandMetadata
from src.epm.onboarding_orchestrator import OnboardingOrchestrator, OnboardingProfile
from src.epm.step_registry import StepRegistry
from typing import Dict, List

class OnboardingWizardPlugin(BasePlugin):
    """
    Onboarding Wizard Plugin
    
    Orchestrates the full CORTEX onboarding experience:
    - Phase 1: Self-Setup (automated installation)
    - Phase 2: Introduction (capabilities showcase)
    - Phase 3: Interactive Tutorial (live demos)
    - Phase 4: Application Analysis (real-time insights)
    """
    
    def _get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="onboarding_wizard_plugin",
            name="Onboarding Wizard",
            version="1.0.0",
            description="Comprehensive CORTEX onboarding experience"
        )
    
    def initialize(self) -> bool:
        """Initialize orchestrator and register steps"""
        self.orchestrator = OnboardingOrchestrator()
        self._register_phase1_steps()
        return True
    
    def execute(self, request: str, context: Dict) -> Dict:
        """Execute onboarding flow"""
        # Detect profile from request
        profile = self._detect_profile(request)
        
        # Start onboarding
        session = self.orchestrator.start_onboarding(
            profile=profile,
            context=context
        )
        
        # Return results
        return {
            "success": True,
            "session_id": session.session_id,
            "report": self.orchestrator.generate_report()
        }
    
    def register_commands(self) -> List[CommandMetadata]:
        return [
            CommandMetadata(
                command="/onboard",
                natural_language_equivalent="onboard yourself",
                plugin_id=self.metadata.plugin_id,
                description="Start CORTEX onboarding experience"
            )
        ]
    
    def _register_phase1_steps(self):
        """Register Phase 1 steps"""
        from src.epm.steps.phase1_environment_detection import EnvironmentDetectionStep
        from src.epm.steps.phase1_dependency_installation import DependencyInstallationStep
        from src.epm.steps.phase1_brain_initialization import BrainInitializationStep
        from src.epm.steps.phase1_validation import ValidationStep
        
        self.orchestrator.registry.register(EnvironmentDetectionStep())
        self.orchestrator.registry.register(DependencyInstallationStep())
        self.orchestrator.registry.register(BrainInitializationStep())
        self.orchestrator.registry.register(ValidationStep())
```

---

### Step Implementation Example

```python
# src/epm/steps/phase1_environment_detection.py

from src.epm.onboarding_step import OnboardingStep, StepResult, StepStatus, StepDisplayFormat
from typing import Dict, Any
import platform
import sys
import shutil

class EnvironmentDetectionStep(OnboardingStep):
    """Detect OS, shell, Python version, Git, workspace root"""
    
    def __init__(self):
        super().__init__(
            step_id="detect_environment",
            name="Environment Detection",
            description="Detect platform, shell, paths, and existing tools",
            display_format=StepDisplayFormat.PROGRESS_BAR,
            estimated_duration=30,  # seconds
            skippable=False,  # Critical step
            required_for_profiles=["quick", "standard", "comprehensive"],
            dependencies=[]  # No dependencies
        )
    
    def execute(self, context: Dict[str, Any]) -> StepResult:
        """Execute environment detection"""
        try:
            data = {}
            errors = []
            warnings = []
            
            # Detect OS
            data["os"] = platform.system()  # Windows, Darwin, Linux
            data["os_version"] = platform.version()
            
            # Detect shell
            shell = self._detect_shell()
            data["shell"] = shell
            if shell == "unknown":
                warnings.append("Could not detect shell type")
            
            # Detect Python
            data["python_version"] = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            if sys.version_info < (3, 9):
                errors.append(f"Python 3.9+ required, found {data['python_version']}")
            
            # Detect Git
            git_path = shutil.which("git")
            data["git_installed"] = git_path is not None
            data["git_path"] = git_path
            if not data["git_installed"]:
                warnings.append("Git not found (Tier 3 features will be limited)")
            
            # Detect workspace root
            import os
            data["workspace_root"] = os.getcwd()
            
            # Determine success
            success = len(errors) == 0
            status = StepStatus.COMPLETED if success else StepStatus.FAILED
            
            return StepResult(
                success=success,
                status=status,
                message="Environment detected successfully" if success else "Environment detection failed",
                data=data,
                errors=errors,
                warnings=warnings
            )
        
        except Exception as e:
            return StepResult(
                success=False,
                status=StepStatus.FAILED,
                message=f"Exception during environment detection: {e}",
                errors=[str(e)]
            )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> bool:
        """No prerequisites for environment detection"""
        return True
    
    def _detect_shell(self) -> str:
        """Detect current shell"""
        import os
        shell = os.environ.get("SHELL", "")
        if "bash" in shell:
            return "bash"
        elif "zsh" in shell:
            return "zsh"
        elif os.environ.get("PSModulePath"):  # PowerShell indicator
            return "powershell"
        else:
            return "unknown"
```

---

## 🧪 Testing Strategy

### Unit Tests

**Test each step independently:**

```python
# tests/epm/steps/test_phase1_environment_detection.py

import pytest
from src.epm.steps.phase1_environment_detection import EnvironmentDetectionStep
from src.epm.onboarding_step import StepStatus

def test_environment_detection_success():
    """Test successful environment detection"""
    step = EnvironmentDetectionStep()
    context = {}
    
    result = step.execute(context)
    
    assert result.success
    assert result.status == StepStatus.COMPLETED
    assert "os" in result.data
    assert "python_version" in result.data
    assert "workspace_root" in result.data

def test_environment_detection_validates_python_version():
    """Test Python version validation"""
    step = EnvironmentDetectionStep()
    context = {}
    
    result = step.execute(context)
    
    # Should detect current Python version
    assert "python_version" in result.data
    # If running this test, Python 3.9+ is available (requirement)
    assert result.success

def test_environment_detection_handles_missing_git():
    """Test graceful handling of missing Git"""
    step = EnvironmentDetectionStep()
    context = {}
    
    result = step.execute(context)
    
    # Should still succeed even if Git missing
    assert "git_installed" in result.data
    # May have warnings about Git
    if not result.data["git_installed"]:
        assert any("Git" in w for w in result.warnings)
```

---

### Integration Tests

**Test full Phase 1 flow:**

```python
# tests/integration/test_onboarding_phase1.py

import pytest
from src.plugins.onboarding_wizard_plugin import OnboardingWizardPlugin
from src.epm.onboarding_orchestrator import OnboardingProfile

def test_phase1_full_flow():
    """Test complete Phase 1 onboarding"""
    plugin = OnboardingWizardPlugin()
    plugin.initialize()
    
    result = plugin.execute(
        request="onboard yourself",
        context={"profile": "quick"}
    )
    
    assert result["success"]
    assert "session_id" in result
    
    report = result["report"]
    assert report["completed_steps"] > 0
    assert report["failed_steps"] == 0

def test_phase1_dependency_resolution():
    """Test that steps execute in correct order"""
    plugin = OnboardingWizardPlugin()
    plugin.initialize()
    
    # Get execution order
    steps = plugin.orchestrator.registry.get_execution_order(profile="quick")
    step_ids = [s.step_id for s in steps]
    
    # Verify dependency order
    env_idx = step_ids.index("detect_environment")
    deps_idx = step_ids.index("install_dependencies")
    brain_idx = step_ids.index("initialize_brain")
    
    assert env_idx < deps_idx  # Environment before dependencies
    assert deps_idx < brain_idx  # Dependencies before brain init
```

---

## 📝 Success Criteria

### MVP (Milestone 1)

- [ ] User can run `/CORTEX onboard yourself`
- [ ] Phase 1 executes without errors
- [ ] Environment detected correctly on Windows/Mac/Linux
- [ ] Dependencies installed (or skipped gracefully)
- [ ] Brain directories created
- [ ] Validation confirms success
- [ ] Progress displayed in GitHub Copilot Chat
- [ ] 100% test coverage for Phase 1 steps

### Enhanced (Milestone 2)

- [ ] Phase 1 + Phase 2 working
- [ ] Leadership metrics displayed
- [ ] Memory demo shows conversations
- [ ] Code analysis provides insights
- [ ] Session state persists
- [ ] Can pause and resume
- [ ] Formatted output (progress bars, status reports)

### Full (Milestone 3)

- [ ] All 4 phases working
- [ ] Profile selection (Quick/Standard/Comprehensive)
- [ ] Mermaid diagrams render
- [ ] Application analysis provides ROI projections
- [ ] Executive summary generated
- [ ] Complete documentation
- [ ] Video demo prepared

---

## 🚀 Next Steps

1. **Review & Approve This Plan** - Ensure alignment with vision
2. **Start Milestone 1** - Begin with MVP implementation
3. **Iterative Development** - Build, test, refine each milestone
4. **User Testing** - Validate with real users at each milestone
5. **Production Release** - After Milestone 3 complete

---

## 📊 Effort Estimates

| Milestone | Scope | Estimated Time | Dependencies |
|-----------|-------|----------------|--------------|
| **Milestone 1: MVP** | Phase 1 only | 2-3 days | EPM foundation (✅ complete) |
| **Milestone 2: Enhanced** | Phase 1-2 + Basic Phase 3 | 3-4 days | Milestone 1 complete |
| **Milestone 3: Full** | All 4 phases | 4-5 days | Milestone 2 complete |
| **Total** | Complete implementation | 9-12 days | None |

**Note:** Times assume focused development. Add buffer for reviews, testing, refinements.

---

## 🎯 Strategic Value

**For Developers:**
- Smooth onboarding experience
- Clear understanding of CORTEX capabilities
- Immediate value demonstration

**For Leadership:**
- Professional presentation
- ROI visibility (token savings, cost reduction)
- Confidence in technical sophistication

**For Project:**
- Reduces support burden (self-service onboarding)
- Increases adoption rate
- Establishes quality standards

---

## 🔍 Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Mermaid rendering issues | Medium | High | Use fallback text diagrams, test early |
| Cross-platform compatibility | Low | High | Test on Windows/Mac/Linux, use platform abstraction |
| Performance (slow steps) | Medium | Medium | Parallel execution, progress feedback, skippable steps |
| User confusion | Low | Medium | Clear instructions, good error messages, help text |

---

## 📚 References

**Related Documents:**
- Design: `cortex-brain/documents/planning/cortex-onboarding-flow-design.yaml`
- EPM Foundation: `src/epm/` (OnboardingStep, StepRegistry, OnboardingOrchestrator)
- Plugin System: `src/plugins/base_plugin.py`, `src/plugins/command_registry.py`

**Prior Art:**
- Configuration Wizard Plugin: `src/plugins/configuration_wizard_plugin.py`
- Platform Switch Plugin: `src/plugins/platform_switch_plugin.py`

---

**Status:** Planning Complete - Ready for Implementation Decision  
**Decision Required:** Approve MVP (Milestone 1) to begin development  
**Est. MVP Delivery:** 2-3 days after approval

---

*This plan represents the bridge between vision (onboarding-flow-design.yaml) and execution. The EPM foundation is ready - we just need to build the concrete steps and wire the plugin.*

**Next Action:** Review this plan and approve Milestone 1 to begin MVP implementation.
