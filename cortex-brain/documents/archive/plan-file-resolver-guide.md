# Plan File Resolver - Implementation Guide

## Overview

The Plan File Resolver enables **transparent MD ↔ YAML translation** for CORTEX orchestrators. Users can naturally reference `.md` files, while orchestrators automatically use efficient structured YAML internally.

## Architecture

```
User Input: "#file:00-master-plan.md"
    ↓
PlanFileResolver.resolve_plan_file()
    ↓
Priority Resolution:
    1. Check manifests/orchestrators/{name}.yaml  (native YAML)
    2. Find documents/planning/**/{file}.md      (convert if needed)
    3. Convert MD → YAML + cache
    4. Return structured dict
    ↓
Orchestrator: Uses YAML dict (fast, typed access)
```

## Usage

### In Orchestrators

All orchestrators inherit from `BaseOperationModule` and can use:

```python
class MyOrchestrator(BaseOperationModule):
    def execute(self, context):
        # User says: "continue with #file:00-master-plan.md"
        
        # Automatically resolves to YAML (transparent to user)
        plan_data = self.resolve_plan_file("#file:00-master-plan.md")
        
        # Access structured data
        plan_id = plan_data['metadata']['plan_id']
        progress = plan_data['progress']['percentage']
        phases = plan_data['phases']
        
        # Current phase
        current = next(p for p in phases if 'IN PROGRESS' in p['status'])
        print(f"Working on: {current['name']}")
```

### Standalone Usage

```python
from src.utils.plan_file_resolver import resolve_plan_file
from pathlib import Path

# Resolve plan file
result = resolve_plan_file(
    "#file:00-master-plan.md",
    brain_path=Path("cortex-brain")
)

if result.success:
    plan_data = result.data
    print(f"Plan: {plan_data['metadata']['plan_id']}")
    print(f"Progress: {plan_data['progress']['percentage']}%")
```

## File Reference Formats

All of these work:

```python
# Just filename (searches recursively)
"00-master-plan.md"

# With #file: prefix (Copilot Chat format)
"#file:00-master-plan.md"

# Relative path (recommended - avoids ambiguity)
"active/cortex-rearchitecture-v1/00-master-plan.md"

# Absolute path
"/full/path/to/00-master-plan.md"
```

**⚠️ Best Practice:** Use relative paths when multiple plans exist with same filename:
```python
# ✅ GOOD - Explicit
"active/cortex-rearchitecture-v1/00-master-plan.md"

# ⚠️ OK - But may find wrong file if duplicates exist
"00-master-plan.md"
```

## Parsed Data Structure

```yaml
metadata:
  plan_id: cortex-rearchitecture-v1
  title: CORTEX Rearchitecture Master Plan
  date: December 15, 2025
  complexity_tier: 4 (Complex - Incremental Delivery)

summary: |
  Reorganize CORTEX architecture with ZERO files in folder roots...

progress:
  percentage: 16
  phases_complete: "2.25/14 Phases Complete"
  actual_time: "10.5h"
  elapsed_time: "12h"

phases:
  - id: "0"
    name: Governance Foundation
    status: ✅ COMPLETE
    actual_time: "4h"
    elapsed_time: "4.5h"
  
  - id: "1"
    name: Visual Tracker Migration
    status: ✅ COMPLETE
    actual_time: "1h 25m"
    elapsed_time: "1.5h"
  
  - id: "1.5.7"
    name: Autonomous Enhancements
    status: ⏳ IN PROGRESS (40%)
    actual_time: "1.5h"
    elapsed_time: "1.5h"

continuation_prompt: |
  Continue work on plan `cortex-rearchitecture-v1`. Current status: 2.25/14 phases (16%)...

source_file: D:\PROJECTS\CORTEX\cortex-brain\documents\planning\active\...
```

## Caching

### Cache Location
```
cortex-brain/cache/plan-conversions/
└── 00-master-plan_{hash}.yaml
```

### Cache Validation
- Cached YAML used if newer than source MD
- Automatic regeneration if MD modified
- Hash-based naming prevents collisions

### Performance
```
First call:  ~15ms (parse MD + write YAML)
Second call: ~0ms  (load cached YAML)
Speedup:     ∞ (instant)
```

## Error Handling

### File Not Found
```python
result = resolve_plan_file("nonexistent.md", brain_path)

if not result.success:
    print(result.error_message)
    # Output:
    # Plan file not found: nonexistent.md
    #   Searched in:
    #     - cortex-brain/manifests/orchestrators/nonexistent.yaml
    #     - cortex-brain/documents/planning/**/nonexistent.md
```

### Multiple Matches
```python
result = resolve_plan_file("00-master-plan.md", brain_path)

# Warning logged:
# Multiple matches found for 00-master-plan.md:
#   - cortex-brain/documents/planning/active/cortex-lens-v3/00-master-plan.md
#   - cortex-brain/documents/planning/active/cortex-rearchitecture-v1/00-master-plan.md
# Using first: cortex-brain/documents/planning/active/cortex-lens-v3/00-master-plan.md
# 💡 Tip: Provide full path to avoid ambiguity: 'active/plan-name/00-master-plan.md'
```

### Conversion Errors
```python
# Malformed MD → Graceful degradation
result = resolve_plan_file("broken.md", brain_path)

if not result.success:
    print(f"Conversion failed: {result.error_message}")
```

## Integration Points

### 1. BaseOperationModule
All orchestrators automatically have access:
```python
# In any orchestrator
plan_data = self.resolve_plan_file(user_input)
```

### 2. Planning Orchestrator v3.1
```python
class PlanningOrchestrator(BaseOperationModule):
    def continue_plan(self, plan_reference: str):
        # User: "continue with #file:00-master-plan.md"
        plan_data = self.resolve_plan_file(plan_reference)
        
        # Find current phase
        current_phase = next(
            p for p in plan_data['phases'] 
            if 'IN PROGRESS' in p['status']
        )
        
        # Execute tasks for current phase
        self._execute_phase(current_phase)
```

### 3. TDD Orchestrator
```python
class TDDOrchestrator(BaseOperationModule):
    def run_tests_for_plan(self, plan_reference: str):
        plan_data = self.resolve_plan_file(plan_reference)
        
        # Get phases requiring tests
        test_phases = [
            p for p in plan_data['phases']
            if 'tdd' in p['name'].lower()
        ]
```

### 4. Maintenance Orchestrator
```python
class MaintenanceOrchestratorV3(BaseOperationModule):
    def validate_all_plans(self):
        # Find all master plans
        plans_dir = Path("cortex-brain/documents/planning/active")
        
        for plan_dir in plans_dir.iterdir():
            master_plan = plan_dir / "00-master-plan.md"
            if master_plan.exists():
                # Validate structure
                plan_data = self.resolve_plan_file(str(master_plan))
                self._validate_plan_structure(plan_data)
```

## Testing

### Unit Tests
```bash
# Test resolver
python tests/test_plan_file_resolver.py

# Test specific plan
python tests/test_specific_plan.py
```

### Manual Testing
```python
from src.utils.plan_file_resolver import resolve_plan_file
from pathlib import Path

# Test 1: Just filename
result = resolve_plan_file("00-master-plan.md", Path("cortex-brain"))
print(f"Found: {result.source_path}")

# Test 2: With path
result = resolve_plan_file(
    "active/cortex-rearchitecture-v1/00-master-plan.md",
    Path("cortex-brain")
)
print(f"Plan ID: {result.data['metadata']['plan_id']}")

# Test 3: Caching
result1 = resolve_plan_file("00-master-plan.md", Path("cortex-brain"))
result2 = resolve_plan_file("00-master-plan.md", Path("cortex-brain"))
print(f"First: {result1.conversion_time:.3f}s")
print(f"Second: {result2.conversion_time:.3f}s (cached: {result2.cached})")
```

## Benefits

### For Users
✅ Natural `.md` references (human-readable)  
✅ No need to know about YAML conversion  
✅ Works with existing Copilot Chat `#file:` syntax  
✅ Helpful warnings for ambiguous references

### For Orchestrators
✅ Fast structured data access (YAML)  
✅ Type-safe dictionary access  
✅ No manual parsing required  
✅ Automatic caching (performance)

### For System
✅ Best of both worlds (MD for humans, YAML for machines)  
✅ Zero user friction  
✅ Transparent implementation  
✅ Extensible for future formats

## Future Enhancements

### Planned
1. **JSON Schema validation** - Validate YAML structure
2. **Bi-directional sync** - Update MD from YAML changes
3. **Format detection** - Auto-detect plan format versions
4. **Batch conversion** - Convert all plans at once

### Potential
- Support for `.json` plans (ADO work items)
- Real-time MD ↔ YAML sync (file watchers)
- Plan templates with schema validation
- Version migration tools

---

**Author:** Asif Hussain  
**Version:** 1.0.0  
**Date:** December 15, 2025
