# Cortex Implants Integration Guide

**Version:** 1.0.0 | **Updated:** December 15, 2025

---

## 🎯 Overview

This guide shows how to integrate cortex-implants into CORTEX orchestrators and workflows.

**Key Principle:** Integration is **100% optional** - CORTEX works normally without implants present (graceful degradation).

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│           CORTEX Orchestrators                  │
│  (Planning, TDD, Maintenance, etc.)            │
└──────────────────┬──────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────┐
│      CortexImplantsIntegrator                   │
│   (Optional loader with graceful degradation)   │
└──────────────────┬──────────────────────────────┘
                   │
          ┌────────┴────────┐
          ↓                 ↓
┌──────────────────┐  ┌──────────────────┐
│  CortexImplants  │  │  No Implants     │
│  (per-repo rules)│  │  (CORTEX only)   │
└──────────────────┘  └──────────────────┘
```

---

## 🔌 Integration Points

### 1. Planning Orchestrator

**Location:** `src/orchestration_3_0/orchestrators/planning/planning_orchestrator.py`

**Integration:**

```python
from src.tier0.cortex_implants_integrator import get_implants_integrator

class PlanningOrchestrator:
    def execute_workflow(self, context):
        # ... normal planning logic ...
        
        # Validate against cortex-implants (optional)
        implants_violations = self._validate_against_implants(plan)
        
        return {
            'plan': plan_dict,
            'implants_violations': implants_violations,  # Empty if no implants
            'success': True
        }
    
    def _validate_against_implants(self, plan):
        """Optional validation - returns [] if no implants."""
        integrator = get_implants_integrator()
        
        if not integrator.has_implants():
            return []  # No implants = no violations
        
        violations = []
        
        # Validate tech stack
        violations.extend(integrator.validate_tech_stack(plan.dependencies))
        
        # Validate architecture
        violations.extend(integrator.validate_architecture(plan))
        
        return violations
```

**Behavior:**
- ✅ **With implants:** Validates and warns about violations
- ✅ **Without implants:** Returns empty list, no errors

---

### 2. Governance Engine

**Location:** `src/tier0/governance_engine.py`

**Integration:**

```python
from src.tier0.cortex_implants_integrator import get_implants_integrator

class GovernanceEngine:
    def __init__(self):
        self.cortex_rules = self._load_cortex_rules()
        self.implants_integrator = get_implants_integrator()
    
    def get_coding_standards(self):
        """Get coding standards (CORTEX + implants)."""
        # Start with CORTEX standards
        standards = self.cortex_rules['coding_standards']
        
        # Merge with implants if present
        if self.implants_integrator.has_implants():
            implant_standards = self.implants_integrator.get_coding_standards()
            if implant_standards:
                # Merge based on priority
                if self.implants_integrator.should_override_cortex():
                    standards = implant_standards  # Override
                else:
                    standards = {**standards, **implant_standards}  # Merge
        
        return standards
```

---

### 3. Context Loader

**Location:** `src/tier0/optimized_context_loader.py`

**Integration:**

```python
from src.tier0.cortex_implants_integrator import get_implants_integrator

class OptimizedContextLoader:
    def load_optimized_context(self, intent, query, available_tiers):
        # Load CORTEX context
        context = self._load_cortex_context(intent, query, available_tiers)
        
        # Add implants context if present
        integrator = get_implants_integrator()
        if integrator.has_implants():
            context['implants_summary'] = integrator.get_context_summary()
        
        return context
```

---

## 🛠️ Helper Utilities

### CortexImplantsIntegrator

**Purpose:** Unified interface for optional implants access

**Key Methods:**

```python
from src.tier0.cortex_implants_integrator import get_implants_integrator

integrator = get_implants_integrator()

# Check presence
if integrator.has_implants():
    print("Implants loaded!")

# Get priority
priority = integrator.get_priority()  # HIGH/MEDIUM/LOW/NONE

# Check override behavior
if integrator.should_override_cortex():
    # Use company rules first
    pass

# Get specific rules
coding_standards = integrator.get_coding_standards()
arch_patterns = integrator.get_architecture_patterns()
tech_stack = integrator.get_tech_stack_restrictions()
business_rules = integrator.get_business_rules()
security_reqs = integrator.get_security_requirements()

# Validate
violations = integrator.validate_tech_stack(['pandas', 'numpy'])
violations = integrator.validate_architecture(plan_dict)

# Get summary for context
summary = integrator.get_context_summary()
```

---

## 📋 Integration Checklist

### For New Orchestrators

- [ ] Import `get_implants_integrator`
- [ ] Call `integrator.has_implants()` before using implants
- [ ] Handle gracefully if implants absent (return defaults)
- [ ] Log implants usage: `logger.info("🧬 Cortex implants active")`
- [ ] Include implants violations in output (if any)
- [ ] Test both with and without implants present

### For Existing Orchestrators

- [ ] Identify validation points
- [ ] Add optional implants validation
- [ ] Ensure no breaking changes if implants missing
- [ ] Add integration tests
- [ ] Update documentation

---

## 🧪 Testing Integration

### Unit Test Pattern

```python
import pytest
from pathlib import Path
from src.tier0.cortex_implants_integrator import CortexImplantsIntegrator

def test_orchestrator_without_implants(tmp_path):
    """Test orchestrator works without implants."""
    # Create repo without implants
    repo_path = tmp_path / "test-repo"
    repo_path.mkdir()
    
    # Initialize integrator
    integrator = CortexImplantsIntegrator(repo_path)
    
    # Should not have implants
    assert not integrator.has_implants()
    
    # Should return empty violations
    violations = integrator.validate_tech_stack(['pandas'])
    assert violations == []

def test_orchestrator_with_implants(tmp_path):
    """Test orchestrator uses implants when present."""
    # Create repo with implants
    repo_path = tmp_path / "test-repo"
    implants_dir = repo_path / ".cortex-implants"
    implants_dir.mkdir(parents=True)
    
    # Create minimal governance.yaml
    gov_file = implants_dir / "governance.yaml"
    gov_file.write_text("""
company_name: "TestCo"
project_name: "TestProject"
priority: "MEDIUM"
    """)
    
    # Initialize integrator
    integrator = CortexImplantsIntegrator(repo_path)
    
    # Should have implants
    assert integrator.has_implants()
    assert integrator.get_priority() == "MEDIUM"
```

### Integration Test Pattern

```python
def test_planning_with_implants(tmp_path):
    """Test planning orchestrator validates against implants."""
    from src.orchestration_3_0.orchestrators.planning import PlanningOrchestrator
    
    # Setup repo with implants
    repo_path = tmp_path / "test-repo"
    setup_implants_with_forbidden_libraries(repo_path, ['eval', 'pickle'])
    
    # Run planning
    orchestrator = PlanningOrchestrator()
    result = orchestrator.execute_workflow(context)
    
    # Check violations reported
    assert 'implants_violations' in result
    if 'eval' in plan_dependencies:
        assert len(result['implants_violations']) > 0
```

---

## 🔍 Debugging Integration

### Enable Debug Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('src.tier0.cortex_implants_integrator')
logger.setLevel(logging.DEBUG)
```

### Check Implants Status

```bash
# Quick status check
cortex implant status

# Full validation
cortex implant validate
```

### Common Issues

**Issue:** Implants not loading

```python
# Debug code
from src.tier0.cortex_implants_integrator import get_implants_integrator

integrator = get_implants_integrator()
print(f"Has implants: {integrator.has_implants()}")
print(f"Repo path: {integrator.repo_path}")
print(f"Implants dir: {integrator.repo_path / '.cortex-implants'}")
```

**Issue:** Violations not reported

```python
# Check if validation running
violations = integrator.validate_tech_stack(['test-lib'])
print(f"Violations: {violations}")
print(f"Tech stack rules: {integrator.get_tech_stack_restrictions()}")
```

---

## 🎯 Best Practices

### 1. Always Check Presence

```python
# ✅ Good
if integrator.has_implants():
    validate_with_implants()

# ❌ Bad
validate_with_implants()  # Crashes if no implants
```

### 2. Graceful Degradation

```python
# ✅ Good
def get_coding_standards():
    integrator = get_implants_integrator()
    
    # CORTEX defaults
    standards = load_cortex_standards()
    
    # Override with implants if present
    if integrator.has_implants():
        implant_standards = integrator.get_coding_standards()
        if implant_standards:
            standards.update(implant_standards)
    
    return standards

# ❌ Bad
def get_coding_standards():
    integrator = get_implants_integrator()
    return integrator.get_coding_standards()  # None if no implants!
```

### 3. Priority-Based Merging

```python
def merge_rules(cortex_rules, implant_rules, priority):
    if priority == "HIGH":
        # Implants override CORTEX
        return {**cortex_rules, **implant_rules}
    elif priority == "MEDIUM":
        # Balanced merge
        return merge_balanced(cortex_rules, implant_rules)
    else:  # LOW
        # CORTEX dominant
        return {**implant_rules, **cortex_rules}
```

### 4. Informative Logging

```python
if integrator.has_implants():
    logger.info("🧬 Cortex implants active")
    logger.info(f"   Company: {integrator.implants.governance.company_name}")
    logger.info(f"   Priority: {integrator.get_priority()}")
else:
    logger.debug("No cortex implants found (using CORTEX defaults)")
```

---

## 📊 Performance Considerations

### Caching

Integrator caches loaded implants:

```python
# First call loads from disk
integrator = get_implants_integrator()  # Loads YAML files

# Subsequent calls use cache
integrator = get_implants_integrator()  # Returns cached instance
```

### Lazy Loading

Implants load only when first accessed:

```python
integrator = get_implants_integrator()  # Creates instance
# ... implants not loaded yet ...
has_implants = integrator.has_implants()  # Now loads YAML
```

---

## 🔗 Related Documentation

- [Setup Guide](./cortex-implants-setup-guide.md) - Initialize and configure implants
- [Examples](./cortex-implants-examples.md) - Real-world usage patterns
- [System Design](../implementation-guides/cortex-implants-system-design.md) - Architecture details

---

**Next Steps:** See [Examples Gallery](./cortex-implants-examples.md) for real-world integration patterns.
