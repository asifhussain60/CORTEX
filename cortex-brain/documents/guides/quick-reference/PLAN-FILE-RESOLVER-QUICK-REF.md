# Plan File Resolver - Quick Reference

## TL;DR

**Problem:** Users reference `.md` files (readable), orchestrators need `.yaml` (efficient)

**Solution:** Automatic transparent translation

```python
# User says: "continue with #file:00-master-plan.md"
# Orchestrator does:
plan_data = self.resolve_plan_file("#file:00-master-plan.md")  # Auto-converts to YAML
```

---

## 🚀 Quick Start

### In Any Orchestrator

```python
class MyOrchestrator(BaseOperationModule):
    def execute(self, context):
        # Auto-resolves MD → YAML
        plan = self.resolve_plan_file("#file:00-master-plan.md")
        
        # Use structured data
        plan_id = plan['metadata']['plan_id']
        progress = plan['progress']['percentage']
        phases = plan['phases']
```

### File Reference Formats

```python
# All of these work:
"00-master-plan.md"                                           # Searches recursively
"#file:00-master-plan.md"                                     # Copilot Chat format
"active/cortex-rearchitecture-v1/00-master-plan.md"          # Recommended (no ambiguity)
```

---

## 📊 Data Structure

```python
plan_data = {
    'metadata': {
        'plan_id': str,
        'title': str,
        'date': str,
        'complexity_tier': str
    },
    'summary': str,
    'progress': {
        'percentage': int,
        'phases_complete': str,
        'actual_time': str,
        'elapsed_time': str
    },
    'phases': [
        {
            'id': str,
            'name': str,
            'status': str,  # '✅ COMPLETE', '⏳ IN PROGRESS', '⏸️ PENDING'
            'actual_time': str,
            'elapsed_time': str
        }
    ],
    'continuation_prompt': str,
    'source_file': str
}
```

---

## 🎯 Common Patterns

### Get Current Phase
```python
plan = self.resolve_plan_file("#file:00-master-plan.md")
current = next(p for p in plan['phases'] if 'IN PROGRESS' in p['status'])
print(f"Working on: {current['name']}")
```

### Calculate Progress
```python
plan = self.resolve_plan_file("#file:00-master-plan.md")
total = len(plan['phases'])
completed = len([p for p in plan['phases'] if '✅' in p['status']])
print(f"Progress: {completed}/{total} phases ({plan['progress']['percentage']}%)")
```

### Get Next Phase
```python
plan = self.resolve_plan_file("#file:00-master-plan.md")
current_idx = next(i for i, p in enumerate(plan['phases']) if 'IN PROGRESS' in p['status'])
next_phase = plan['phases'][current_idx + 1] if current_idx + 1 < len(plan['phases']) else None
```

---

## ⚡ Performance

| Call | Time | Notes |
|------|------|-------|
| First | ~15ms | Parse MD + write YAML cache |
| Second+ | ~0ms | Load cached YAML |

**Cache location:** `cortex-brain/cache/plan-conversions/`

---

## ✅ Best Practices

### DO ✅
- Use relative paths for clarity: `"active/plan-name/00-master-plan.md"`
- Let resolver handle format conversion automatically
- Access structured data via dict keys

### DON'T ❌
- Manually parse MD files
- Hardcode YAML paths
- Bypass resolver with direct file reads

---

## 🔧 Troubleshooting

### Multiple Matches Warning
```
Multiple matches found for 00-master-plan.md:
  - active/cortex-lens-v3/00-master-plan.md
  - active/cortex-rearchitecture-v1/00-master-plan.md
💡 Tip: Provide full path to avoid ambiguity
```

**Fix:** Use full path
```python
# ✅ GOOD
self.resolve_plan_file("active/cortex-rearchitecture-v1/00-master-plan.md")
```

### File Not Found
```python
# Raises FileNotFoundError with search paths
try:
    plan = self.resolve_plan_file("missing.md")
except FileNotFoundError as e:
    print(f"Plan not found: {e}")
```

---

## 📚 Full Documentation

See: `cortex-brain/documents/implementation-guides/plan-file-resolver-guide.md`

---

**Author:** Asif Hussain  
**Version:** 1.0.0
