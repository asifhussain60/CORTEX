# EPM Orchestrator Enhancement - Quick Reference Cards

**Version:** 1.0.0  
**Created:** 2025-11-26  
**Format:** Copy-paste ready snippets

---

## 🎯 For Developers: Quick Integration Guide

### Adding Code Cleanup Validation to Your Orchestrator

```python
# Step 1: Import validator
from workflows.code_cleanup_validator import CodeCleanupValidator

# Step 2: Run validation
def your_completion_method(self):
    validator = CodeCleanupValidator()
    issues = validator.scan_directory(self.project_root, recursive=True)
    
    if issues:
        # Block completion with clear error
        return {
            'success': False,
            'error': 'Code cleanup required',
            'cleanup_issues': [
                {
                    'file': issue.file_path,
                    'line': issue.line_number,
                    'type': issue.issue_type,
                    'message': issue.message
                }
                for issue in issues
            ]
        }
    
    # Continue with your completion logic
    return {'success': True}
```

### Adding Lint Validation to Your Orchestrator

```python
# Step 1: Import lint integration
from workflows.lint_integration import LintIntegration

# Step 2: Run lint
def your_completion_method(self):
    lint = LintIntegration()
    results = lint.run_lint_directory(self.project_root)
    blocking = lint.get_blocking_violations(results)
    
    if blocking:
        # Block completion with lint report
        return {
            'success': False,
            'error': 'Lint violations found',
            'violations': [
                {
                    'file': v.file_path,
                    'line': v.line_number,
                    'rule': v.rule_id,
                    'message': v.message,
                    'severity': v.severity
                }
                for v in blocking
            ]
        }
    
    # Continue
    return {'success': True}
```

### Adding Document Auto-Filing

```python
# Step 1: Import organizer
from utils.document_organizer import DocumentOrganizer

# Step 2: File your document
def save_report(self, report_content: str):
    organizer = DocumentOrganizer()
    
    # Auto-determines category and generates path
    report_path = organizer.file_document(
        content=report_content,
        doc_type='tdd_session',  # or 'code_review', 'ado_work_item', etc.
        metadata={
            'session_id': self.session_id,
            'feature_name': self.feature_name,
            'timestamp': datetime.now().isoformat()
        }
    )
    
    logger.info(f"✅ Report filed to: {report_path}")
    return report_path
```

### Using Incremental Plan Generator

```python
# Step 1: Import generator and writer
from workflows.incremental_plan_generator import IncrementalPlanGenerator
from workflows.streaming_plan_writer import StreamingPlanWriter

# Step 2: Generate plan incrementally
def create_feature_plan(self, plan_request):
    generator = IncrementalPlanGenerator()
    writer = StreamingPlanWriter()
    
    # Phase 1: Skeleton (200 tokens)
    skeleton = generator.generate_skeleton(plan_request)
    print(f"📋 Plan skeleton: {len(skeleton.sections)} sections")
    
    # Phase 2: Fill sections (500 tokens each)
    yaml_stream = writer.open_stream(self.yaml_path, 'yaml')
    md_stream = writer.open_stream(self.md_path, 'markdown')
    
    for section_id in skeleton.sections:
        # Generate section
        section = generator.fill_section(skeleton, section_id)
        
        # Validate token budget
        valid, token_count = generator.validate_token_budget(section.content)
        if not valid:
            logger.warning(f"⚠️ Section {section_id} exceeds budget: {token_count} tokens")
            # Handle: split section or pause for user input
        
        # Stream to files
        writer.write_chunk(yaml_stream, section.to_yaml())
        writer.write_chunk(md_stream, section.to_markdown())
        
        print(f"✅ Section {section_id} complete ({token_count} tokens)")
    
    # Phase 3: Finalize
    yaml_path = writer.close_stream(yaml_stream)
    md_path = writer.close_stream(md_stream)
    
    return {'yaml_path': yaml_path, 'md_path': md_path}
```

---

## 🔍 For Users: Command Reference

### Checking Session Quality

```bash
# Before completion, validate your code
cortex validate session

# Output shows:
# ✅ Tests passing: 47/47
# ❌ Debug statements: 3 files
# ⚠️ Lint violations: 2 warnings
# ⚠️ TODOs remaining: 5 items
```

### Finding Session Artifacts

```bash
# Quick access to recent sessions
cortex show recent sessions

# Output:
# 📁 TDD Sessions:
#    - 2025-11-26: SESSION-103045-auth (✅ Complete)
#    - 2025-11-25: SESSION-153022-api (✅ Complete)
#
# 📁 Code Reviews:
#    - 2025-11-26: REVIEW-120300-auth (3 smells)
#
# 📁 ADO Work Items:
#    - ADO-12345: User Authentication (In Progress)
```

### Generating Incremental Plans

```bash
# Start planning (skeleton only)
cortex plan "Complex Feature"

# Output:
# 📋 Plan Skeleton Generated:
#    1. Overview
#    2. Current State
#    3. Gap Analysis
#    4. Design Decisions
#    5. Implementation
#
# Ready to fill sections? (y/n)

# Fill one section at a time
cortex plan continue section 1

# Review checkpoint after each section
```

---

## ⚙️ Configuration Reference

### CodeCleanupValidator Configuration

```python
# In your orchestrator
validator = CodeCleanupValidator(
    # Customize detection patterns
    additional_debug_patterns=[
        "MyCustomLog(",
        "DebugHelper."
    ],
    
    # Add exemptions
    exemption_markers=[
        "# PRODUCTION_SAFE:",
        "// ALLOW_DEBUG:"
    ],
    
    # Exclude files
    excluded_paths=[
        "**/*_test.py",
        "**/debug_*.py",
        "tools/**"
    ]
)
```

### LintIntegration Configuration

```python
# In your orchestrator
lint = LintIntegration(
    # Specify linters to run
    linters=['pylint', 'eslint', 'dotnet-format'],
    
    # Set severity threshold
    blocking_severities=['error', 'fatal'],
    
    # Custom config files
    config_files={
        'pylint': '.pylintrc.custom',
        'eslint': '.eslintrc.strict.json'
    }
)
```

### IncrementalPlanGenerator Configuration

```python
# In your orchestrator
generator = IncrementalPlanGenerator(
    # Token budgets
    skeleton_token_limit=200,
    section_token_limit=500,
    
    # Chunking strategy
    chunk_on_overflow=True,
    
    # User interaction
    checkpoint_after_section=True,
    require_user_approval=True
)
```

---

## 🧪 Testing Snippets

### Unit Test Template

```python
import pytest
from pathlib import Path
from workflows.code_cleanup_validator import CodeCleanupValidator

def test_detects_print_statements():
    """Verify print statements are detected."""
    validator = CodeCleanupValidator()
    
    # Sample code with debug statement
    test_file = Path('test_sample.py')
    test_file.write_text('''
def hello():
    print("Debug message")  # Should be detected
    return "Hello"
''')
    
    # Run validation
    issues = validator.scan_file(test_file)
    
    # Assert
    assert len(issues) == 1
    assert issues[0].issue_type == 'DEBUG_STATEMENT'
    assert 'print(' in issues[0].message
    
    # Cleanup
    test_file.unlink()

def test_respects_exemption_markers():
    """Verify PRODUCTION_SAFE marker exempts code."""
    validator = CodeCleanupValidator()
    
    test_file = Path('test_sample.py')
    test_file.write_text('''
def hello():
    # PRODUCTION_SAFE: Used for audit logging
    print("Production log message")
    return "Hello"
''')
    
    issues = validator.scan_file(test_file)
    
    # Should be no issues due to exemption
    assert len(issues) == 0
    
    test_file.unlink()
```

### Integration Test Template

```python
import pytest
from pathlib import Path
from orchestrators.session_completion_orchestrator import SessionCompletionOrchestrator

@pytest.mark.integration
def test_session_completion_with_quality_validation():
    """End-to-end test with quality enforcement."""
    # Setup test session
    project_root = Path('test_project/')
    orchestrator = SessionCompletionOrchestrator(project_root)
    
    # Create sample code with issues
    sample_file = project_root / 'src/sample.py'
    sample_file.write_text('''
def process():
    print("Debug")  # Should block completion
    return True
''')
    
    # Run completion
    result = orchestrator.complete_session('test_session_123')
    
    # Assert completion blocked
    assert result['success'] is False
    assert 'cleanup_issues' in result
    assert len(result['cleanup_issues']) > 0
    
    # Fix issues
    sample_file.write_text('''
def process():
    return True
''')
    
    # Retry completion
    result = orchestrator.complete_session('test_session_123')
    
    # Assert success
    assert result['success'] is True
```

---

## 🐛 Troubleshooting Guide

### Issue: False Positive Debug Statement Detection

**Symptom:** Validator flags legitimate production code  
**Cause:** Pattern too broad (e.g., "log" matches logging.info)

**Solution:**
```python
# Add exemption marker in code
# PRODUCTION_SAFE: This is legitimate logging
logger.info("Production message")

# OR configure validator
validator = CodeCleanupValidator(
    excluded_patterns=['logger.info', 'logger.warning']
)
```

### Issue: Lint Violations Blocking Unnecessarily

**Symptom:** Warnings treated as blocking errors  
**Cause:** Severity threshold too strict

**Solution:**
```python
# Adjust severity threshold
lint = LintIntegration(
    blocking_severities=['error', 'fatal']  # Exclude 'warning'
)

# OR suppress in lint config
# .pylintrc
[MESSAGES CONTROL]
disable=C0103,C0114  # Naming conventions, missing docstrings
```

### Issue: Plan Generation Still Exceeds Token Limit

**Symptom:** Excessive data error despite incremental generation  
**Cause:** Individual section too large

**Solution:**
```python
# Reduce section token limit
generator = IncrementalPlanGenerator(
    section_token_limit=300  # Stricter limit
)

# OR split large sections
skeleton.sections = [
    'overview_part1',
    'overview_part2',
    'current_state',
    # ...
]
```

### Issue: Documents Not Auto-Filing Correctly

**Symptom:** Documents end up in wrong folder  
**Cause:** Incorrect doc_type or metadata

**Solution:**
```python
# Use correct doc_type
organizer.file_document(
    content=report,
    doc_type='tdd_session',  # NOT 'session' or 'tdd'
    metadata={
        'session_id': 'SESSION-123',  # Required
        'feature_name': 'auth'         # Required
    }
)

# Check valid doc_types
valid_types = [
    'tdd_session',
    'code_review',
    'ado_work_item',
    'feature_plan',
    'implementation_guide',
    'system_report',
    'conversation_capture'
]
```

---

## 📊 Monitoring & Metrics

### Collecting Quality Metrics

```python
# In your orchestrator
from workflows.quality_metrics import QualityMetricsCollector

collector = QualityMetricsCollector()

# Record validation results
collector.record_validation(
    session_id='SESSION-123',
    validation_type='code_cleanup',
    passed=True,
    issues_found=0
)

# Generate weekly report
report = collector.generate_weekly_report()
print(report)

# Output:
# Quality Metrics (Week of 2025-11-26)
# ======================================
# Code Cleanup:
#   - Pass Rate: 95% (38/40 sessions)
#   - Avg Issues: 1.2 per session
#
# Lint Validation:
#   - Pass Rate: 87% (35/40 sessions)
#   - Avg Violations: 3.5 per session
#
# Production Readiness:
#   - Pass Rate: 92% (37/40 sessions)
```

---

## 🎓 Best Practices

### 1. Run Validation Early and Often

```python
# DON'T wait until session completion
# DO validate incrementally

# After refactoring phase
validator.scan_file(refactored_file)

# After each commit
lint.run_lint(committed_files)

# Before requesting review
readiness_checker.validate_session(session_data)
```

### 2. Use Exemption Markers Judiciously

```python
# GOOD: Clear reason
# PRODUCTION_SAFE: Audit logging required by compliance
print(f"User {user_id} accessed sensitive data")

# BAD: No reason
# PRODUCTION_SAFE: I need this
print("Debug")
```

### 3. Configure Linters for Your Team

```python
# Create team-specific config
# .pylintrc.team
[MESSAGES CONTROL]
disable=C0103  # Allow short variable names

[DESIGN]
max-args=7     # Allow up to 7 function arguments

# Share with team and use in CI
lint = LintIntegration(
    config_files={'pylint': '.pylintrc.team'}
)
```

### 4. Review Plans Section by Section

```python
# DON'T approve entire plan without review
# DO review each section incrementally

for section_id in skeleton.sections:
    section = generator.fill_section(skeleton, section_id)
    
    # Present to user
    print(f"\n{'='*60}")
    print(f"Section: {section_id}")
    print(f"{'='*60}")
    print(section.content)
    
    # Get approval
    if not user_approves(section):
        regenerate_section(skeleton, section_id)
```

---

**Version:** 1.0.0  
**Last Updated:** 2025-11-26  
**Author:** Asif Hussain
