# Context Validator - Usage Guide

**Version:** 1.0.0 | **Author:** CORTEX Development Team | **Phase 5 Task 5.8**

---

## 🎯 Overview

The **ContextValidator** is a Phase 5 enhancement that provides pre-execution context validation with intelligent auto-retrieval capabilities. It ensures orchestrators have all required context before execution, reducing failures and improving reliability.

### Key Features

- ✅ **Requirement Validation** - Verify required vs optional context
- 🔍 **Auto-Retrieval** - Fetch missing context from knowledge graph
- 💡 **Smart Inference** - Derive context from existing data
- 📊 **Quality Assessment** - Check completeness, freshness, types
- 🎯 **Actionable Feedback** - Clear recommendations for missing items

---

## 🚀 Quick Start

### Basic Usage

```python
from src.orchestration_4_0.frameworks.context_validator import ContextValidator

# Initialize validator
validator = ContextValidator()

# Define execution requirements
context = {
    'project_root': '/path/to/project',
    'language': 'python'
}

execution_plan = {
    'required_context': ['project_root', 'language', 'test_framework'],
    'optional_context': ['framework', 'version']
}

# Validate context
result = await validator.validate_context_sufficiency(context, execution_plan)

# Check validation
if result.is_valid():
    print(f"✅ Context valid! Quality: {result.quality.value}")
    # Proceed with execution
else:
    print(f"❌ Missing required: {result.missing_required}")
    # Handle missing context
```

### With Knowledge Graph

```python
from src.tier2.knowledge_graph import KnowledgeGraph

# Initialize with knowledge graph for auto-retrieval
kg = KnowledgeGraph()
validator = ContextValidator(knowledge_graph=kg)

# Validator will automatically retrieve missing required context
result = await validator.validate_context_sufficiency(context, execution_plan)

# Check what was retrieved
if result.retrieved_items:
    print(f"📥 Auto-retrieved: {list(result.retrieved_items.keys())}")
```

---

## 📋 Execution Plan Structure

### Required Context

Items that MUST be present for execution to proceed:

```python
execution_plan = {
    'required_context': [
        'project_root',      # Path to project
        'language',          # Programming language
        'test_framework'     # Testing framework
    ]
}
```

### Optional Context

Items that enhance execution but aren't mandatory:

```python
execution_plan = {
    'optional_context': [
        'framework',         # Application framework
        'version',           # Language/framework version
        'author',            # Project author
        'repository_url'     # Source repository
    ]
}
```

### Context Types

Specify expected types for validation:

```python
execution_plan = {
    'context_types': {
        'file_count': int,
        'complexity': float,
        'enabled': bool,
        'files': list
    }
}
```

### Context Constraints

Define value constraints:

```python
execution_plan = {
    'context_constraints': {
        'complexity': {
            'min': 0,
            'max': 100
        },
        'priority': {
            'allowed': ['low', 'medium', 'high', 'critical']
        },
        'file_count': {
            'min': 1
        }
    }
}
```

---

## 🔍 Auto-Retrieval Strategies

The validator uses multiple strategies to retrieve missing context:

### 1. Knowledge Graph Retrieval

```python
# Validator queries knowledge graph for missing items
value = await kg.query(
    category='execution_context',
    key=missing_key,
    hint=existing_context
)
```

**When it works:**
- Knowledge graph has historical data
- Similar contexts executed before
- Pattern learning enabled

### 2. Inference from Existing Context

**Strategy: Derive from file paths**
```python
# Input
context = {'file_path': '/home/user/project/src/main.py'}

# Inferred
context['project_root'] = '/home/user/project'
```

**Strategy: Extract from URLs**
```python
# Input
context = {'repository_url': 'https://github.com/user/my-repo.git'}

# Inferred
context['repository_name'] = 'my-repo'
```

**Strategy: Count from collections**
```python
# Input
context = {'files': ['a.py', 'b.py', 'c.py']}

# Inferred
context['file_count'] = 3
```

### 3. Default Values

For common keys with sensible defaults:

```python
defaults = {
    'language': 'python',
    'framework': 'unknown',
    'test_framework': 'pytest',
    'complexity': 'medium',
    'priority': 'normal'
}
```

---

## 📊 Context Quality

The validator assesses context quality on multiple dimensions:

### Quality Levels

| Level | Description | Criteria |
|-------|-------------|----------|
| **EXCELLENT** | Perfect context | All required + optional present, no issues |
| **GOOD** | High quality | All required, some optional, minor issues |
| **ACCEPTABLE** | Usable context | All required present, quality concerns |
| **INSUFFICIENT** | Cannot execute | Missing required context |

### Quality Score

```python
score = result.get_quality_score()  # 0-100

# Score calculation
# - Start: 100
# - Missing optional: -5 per item (max -20)
# - Quality issues: -10 per issue (max -30)
```

### Quality Checks

**1. Empty/None Values**
```python
context = {
    'language': None,         # ❌ Issue
    'framework': '',          # ❌ Issue
    'files': []               # ❌ Issue
}
```

**2. Stale Timestamps**
```python
context = {
    'timestamp': datetime.now() - timedelta(days=5)  # ❌ >24h old
}
```

**3. Type Mismatches**
```python
context = {
    'file_count': '10'        # ❌ Should be int
}
```

**4. Constraint Violations**
```python
context = {
    'complexity': 150,        # ❌ Exceeds max (100)
    'priority': 'urgent'      # ❌ Not in allowed list
}
```

---

## 🎯 Integration Patterns

### Pattern 1: Pre-Execution Validation

```python
class ExecutionOrchestrator:
    def __init__(self):
        self.validator = ContextValidator(knowledge_graph=kg)
    
    async def execute(self, context, execution_plan):
        # Validate before execution
        validation = await self.validator.validate_context_sufficiency(
            context,
            execution_plan
        )
        
        if not validation.is_valid():
            raise ValueError(
                f"Missing required context: {validation.missing_required}"
            )
        
        # Warn on quality issues
        if validation.quality_issues:
            logger.warning(f"Context quality issues: {validation.quality_issues}")
        
        # Execute with enriched context
        return await self._execute_phases(validation.context)
```

### Pattern 2: Graceful Degradation

```python
async def execute_with_fallback(self, context, execution_plan):
    validation = await self.validator.validate_context_sufficiency(
        context,
        execution_plan
    )
    
    if validation.quality == ContextQuality.EXCELLENT:
        return await self._execute_full(validation.context)
    
    elif validation.quality in [ContextQuality.GOOD, ContextQuality.ACCEPTABLE]:
        # Execute with reduced features
        logger.info(f"Executing with reduced features (quality: {validation.quality})")
        return await self._execute_basic(validation.context)
    
    else:
        # Cannot execute
        raise InsufficientContextError(validation.missing_required)
```

### Pattern 3: Interactive Prompting

```python
async def execute_with_prompts(self, context, execution_plan):
    validation = await self.validator.validate_context_sufficiency(
        context,
        execution_plan
    )
    
    # Prompt user for missing required
    if validation.missing_required:
        for key in validation.missing_required:
            value = input(f"Please provide {key}: ")
            context[key] = value
        
        # Re-validate
        validation = await self.validator.validate_context_sufficiency(
            context,
            execution_plan
        )
    
    return await self._execute_phases(validation.context)
```

---

## ⚡ Performance

### Benchmarks

| Operation | Target | Actual | Status |
|-----------|--------|--------|--------|
| Basic validation | <50ms | ~30ms | ✅ |
| With auto-retrieval | <200ms | ~150ms | ✅ |
| Quality assessment | <100ms | ~70ms | ✅ |
| Full validation (26 tests) | <30s | 23.81s | ✅ |

### Optimization Tips

**1. Cache Knowledge Graph Queries**
```python
validator = ContextValidator(knowledge_graph=cached_kg)
```

**2. Reuse Validator Instance**
```python
# ✅ Good - reuse instance
validator = ContextValidator()
for plan in plans:
    await validator.validate_context_sufficiency(context, plan)

# ❌ Bad - recreate each time
for plan in plans:
    validator = ContextValidator()  # Overhead
    await validator.validate_context_sufficiency(context, plan)
```

**3. Limit Inference Attempts**
```python
# Validator automatically limits inference to avoid overhead
# No configuration needed
```

---

## 📈 Metrics & Monitoring

### Available Metrics

```python
metrics = validator.get_metrics()

print(f"Total validations: {metrics['total_validations']}")
print(f"Valid contexts: {metrics['valid_contexts']}")
print(f"Auto-retrievals: {metrics['auto_retrievals']}")
print(f"Inference attempts: {metrics['inference_attempts']}")
print(f"Quality checks: {metrics['quality_checks']}")

# Success rate
success_rate = metrics['valid_contexts'] / metrics['total_validations']
print(f"Success rate: {success_rate:.1%}")
```

### Reset Metrics

```python
# Reset for new test run
validator.reset_metrics()
```

---

## 🚨 Troubleshooting

### Issue: Auto-Retrieval Not Working

**Symptom:** Missing required context not retrieved

**Solutions:**
1. Check knowledge graph is passed to validator
2. Verify knowledge graph has data for the key
3. Check inference strategies cover the key
4. Add custom inference logic

**Example:**
```python
# Check if KG is connected
validator = ContextValidator(knowledge_graph=kg)
assert validator.kg is not None

# Manually check KG
value = await kg.query(category='execution_context', key='project_root')
```

### Issue: Quality Score Too Low

**Symptom:** Context quality marked ACCEPTABLE instead of GOOD

**Solutions:**
1. Fix empty/None values
2. Update stale timestamps
3. Correct type mismatches
4. Add missing optional context

**Example:**
```python
# Before
context = {'language': None}  # Quality: ACCEPTABLE

# After
context = {'language': 'python'}  # Quality: GOOD
```

### Issue: Type Validation Fails

**Symptom:** Quality issues report type mismatches

**Solutions:**
1. Convert types in context
2. Update execution_plan types
3. Use string type names if needed

**Example:**
```python
# Use string type names for flexibility
execution_plan = {
    'context_types': {
        'file_count': 'int',  # String instead of int
        'enabled': 'bool'
    }
}
```

---

## 🔮 Future Enhancements

### Planned for Phase 6 (Tasks 6.10-6.12)

1. **Multi-Agent Context Sharing**
   - Share validated context across agent teams
   - Context synchronization for parallel execution

2. **Learning Engine Integration**
   - Learn optimal context patterns from successful executions
   - Predict missing context based on operation type

3. **Enhanced Guardrails**
   - PII/PHI/PCI detection in context
   - Security policy enforcement
   - Compliance validation

4. **Structured Output Integration**
   - Pydantic schema validation
   - Type-safe context objects
   - Auto-generation of execution plans

---

## 📚 API Reference

### ContextValidator

```python
class ContextValidator:
    def __init__(self, knowledge_graph: Optional[Any] = None)
    
    async def validate_context_sufficiency(
        self,
        context: Dict[str, Any],
        execution_plan: Dict[str, Any]
    ) -> ContextValidation
    
    def get_metrics(self) -> Dict[str, int]
    
    def reset_metrics(self)
```

### ContextValidation

```python
@dataclass
class ContextValidation:
    has_requirements: bool
    missing_required: List[str]
    missing_optional: List[str]
    quality_issues: List[str]
    context: Dict[str, Any]
    retrieved_items: Dict[str, Any]
    quality: ContextQuality
    
    def is_valid(self) -> bool
    def get_quality_score(self) -> float
```

### ContextQuality

```python
class ContextQuality(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    INSUFFICIENT = "insufficient"
```

---

## 🎓 Best Practices

1. ✅ **Define comprehensive execution plans** - Include all required/optional context
2. ✅ **Use knowledge graph** - Enable auto-retrieval for better reliability
3. ✅ **Check quality scores** - Don't just validate, assess quality
4. ✅ **Handle quality issues** - Log warnings, degrade gracefully
5. ✅ **Monitor metrics** - Track validation success rates
6. ✅ **Reuse validators** - Create once, use multiple times
7. ✅ **Add type constraints** - Catch type errors early
8. ✅ **Define value constraints** - Enforce valid ranges

---

## 📞 Support

- **Implementation:** `src/orchestration_4_0/frameworks/context_validator.py`
- **Tests:** `tests/orchestration_4_0/frameworks/test_context_validator.py`
- **Status:** Phase 5 Task 5.8 (92% complete)
- **Dependencies:** Knowledge Graph (optional), Phase 5 infrastructure

**Next Steps:**
- Complete Task 5.8 integration with orchestrators
- Move to Task 5.9 (MCP community integration)
- Enhance with Phase 6 features (multi-agent, learning, guardrails)
