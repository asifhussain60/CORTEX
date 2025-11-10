# Phase 5.3 - Edge Case Implementation Plan

**Phase:** 5.3  
**Timeline:** Week 13-14 (November 2025)  
**Machine:** Asifs-MacBook-Pro.local (macOS)  
**Estimated Duration:** 4-6 hours  
**Status:** 📋 PLANNING  
**Started:** 2025-11-10

---

## 🎯 Objectives

1. **Comprehensive edge case coverage** - Handle boundary conditions across all CORTEX systems
2. **Defensive programming** - Add robust error handling and validation
3. **Test-driven implementation** - Create tests first, then implement handlers
4. **Pattern documentation** - Document reusable edge case patterns
5. **Mac-specific validation** - Address platform-specific edge cases

---

## 📊 Task Breakdown (26 Total Tests)

### Category 1: Empty Inputs (5 tests, 1 hour)
**File:** `tests/edge_cases/test_empty_inputs.py`

```python
# Test cases to implement:
1. test_empty_string_input()          # Empty string handling
2. test_none_input()                  # None/null handling
3. test_empty_list_input()            # Empty collections
4. test_empty_dict_input()            # Empty dictionaries
5. test_whitespace_only_input()       # Whitespace-only strings

# Edge cases covered:
- Empty conversation contexts
- Missing configuration values
- Empty operation parameters
- Blank natural language inputs
```

**Implementation approach:**
```python
import pytest
from src.operations import execute_operation
from src.tier1.conversation_manager import ConversationManager

class TestEmptyInputs:
    """Test system behavior with empty/missing inputs"""
    
    def test_empty_string_input(self):
        """Should gracefully handle empty string inputs"""
        # Test empty operation command
        result = execute_operation("")
        assert result["status"] == "error"
        assert "empty" in result["message"].lower()
        
    def test_none_input(self):
        """Should handle None inputs without crashing"""
        result = execute_operation(None)
        assert result is not None
        assert result["status"] == "error"
        
    # ... continue for all 5 tests
```

---

### Category 2: Malformed Data (8 tests, 1.5 hours)
**File:** `tests/edge_cases/test_malformed_data.py`

```python
# Test cases to implement:
1. test_invalid_json_config()         # Corrupted JSON files
2. test_invalid_yaml_syntax()         # Malformed YAML
3. test_truncated_database()          # Corrupted SQLite DB
4. test_invalid_operation_name()      # Unknown operations
5. test_malformed_natural_language()  # Unparseable requests
6. test_special_characters()          # SQL injection attempts
7. test_unicode_edge_cases()          # Unicode handling
8. test_extremely_long_input()        # Buffer overflow prevention

# Edge cases covered:
- File corruption scenarios
- Syntax errors in config files
- Database integrity issues
- Invalid user inputs
- Security attack vectors
```

**Implementation approach:**
```python
import pytest
from pathlib import Path
import yaml
import sqlite3

class TestMalformedData:
    """Test system resilience to corrupted/invalid data"""
    
    def test_invalid_yaml_syntax(self):
        """Should detect and report YAML syntax errors"""
        malformed_yaml = """
        operations:
          - name: test
            invalid: [unclosed
        """
        # Test YAML loading with error handling
        # Should not crash, should return clear error
        
    def test_special_characters(self):
        """Should prevent SQL injection attacks"""
        malicious_input = "'; DROP TABLE conversations; --"
        # Test that special chars are escaped
        # Database should remain intact
        
    # ... continue for all 8 tests
```

---

### Category 3: Concurrent Access (6 tests, 1.5 hours)
**File:** `tests/edge_cases/test_concurrent_access.py`

```python
# Test cases to implement:
1. test_parallel_conversations()      # Multiple simultaneous chats
2. test_database_locking()            # SQLite write conflicts
3. test_config_file_race()            # Simultaneous config updates
4. test_brain_state_consistency()     # Tier consistency
5. test_parallel_operations()         # Multiple operations running
6. test_agent_coordination()          # Agent collision handling

# Edge cases covered:
- Multi-user scenarios
- Database locking issues
- Race conditions
- State synchronization
- Resource contention
```

**Implementation approach:**
```python
import pytest
import threading
import multiprocessing
from src.tier1.conversation_manager import ConversationManager

class TestConcurrentAccess:
    """Test system behavior under concurrent access"""
    
    def test_parallel_conversations(self):
        """Should handle multiple conversations simultaneously"""
        def create_conversation(conv_id):
            manager = ConversationManager()
            return manager.create_conversation(f"test_{conv_id}")
        
        # Launch 10 parallel conversations
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_conversation, i) for i in range(10)]
            results = [f.result() for f in futures]
        
        # All should succeed without corruption
        assert len(results) == 10
        assert all(r["status"] == "success" for r in results)
        
    # ... continue for all 6 tests
```

---

### Category 4: Resource Limits (4 tests, 1 hour)
**File:** `tests/edge_cases/test_resource_limits.py`

```python
# Test cases to implement:
1. test_large_conversation_history()  # 10,000+ messages
2. test_memory_constraints()          # Limited RAM scenarios
3. test_disk_space_exhaustion()       # Full disk handling
4. test_token_limit_exceeded()        # Context window overflow

# Edge cases covered:
- Scalability limits
- Memory management
- Disk space monitoring
- Token budget management
```

**Implementation approach:**
```python
import pytest
from src.tier1.conversation_manager import ConversationManager

class TestResourceLimits:
    """Test system behavior at resource boundaries"""
    
    def test_large_conversation_history(self):
        """Should handle large conversation histories efficiently"""
        manager = ConversationManager()
        
        # Create conversation with 10K messages
        for i in range(10000):
            manager.add_message(f"Message {i}")
        
        # Should still be responsive
        result = manager.get_recent_messages(limit=20)
        assert len(result) == 20
        
        # Memory usage should be reasonable
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        assert memory_mb < 500  # Less than 500MB
        
    # ... continue for all 4 tests
```

---

### Category 5: Mac-Specific Edge Cases (3 tests, 1 hour)
**File:** `tests/platform/test_macos_edge_cases.py`

```python
# Test cases to implement:
1. test_case_sensitive_filesystem()   # Case sensitivity handling
2. test_unix_path_edge_cases()        # Path separator issues
3. test_homebrew_python_conflicts()   # Multiple Python installs
4. test_macos_sandboxing()            # File access restrictions

# Mac-specific edge cases:
- HFS+ vs APFS filesystem differences
- /usr/bin/python3 vs Homebrew Python
- macOS Gatekeeper restrictions
- SIP (System Integrity Protection) limits
```

**Implementation approach:**
```python
import pytest
import platform
import subprocess
from pathlib import Path

@pytest.mark.skipif(platform.system() != "Darwin", reason="macOS only")
class TestMacOSEdgeCases:
    """Test Mac-specific edge cases and platform quirks"""
    
    def test_case_sensitive_filesystem(self):
        """Should handle both case-sensitive and insensitive filesystems"""
        # macOS can be either!
        test_path = Path("/tmp/cortex_test")
        test_path.mkdir(exist_ok=True)
        
        # Try creating files with different cases
        (test_path / "Test.txt").touch()
        (test_path / "test.txt").touch()
        
        # Check if both exist (case-sensitive) or only one (case-insensitive)
        files = list(test_path.glob("*.txt"))
        
        # CORTEX should handle both scenarios correctly
        # Clean up
        import shutil
        shutil.rmtree(test_path)
        
    def test_homebrew_python_conflicts(self):
        """Should detect and use correct Python installation"""
        # Find all Python installations
        python_paths = [
            "/usr/bin/python3",
            "/opt/homebrew/bin/python3",
            "/usr/local/bin/python3"
        ]
        
        available = [p for p in python_paths if Path(p).exists()]
        
        # CORTEX should prefer venv Python, fallback to system
        # Should never use wrong Python version
        
    # ... continue for all 4 tests
```

---

## 🔧 Implementation Strategy

### Step 1: Create Test Infrastructure (30 minutes)
```bash
# Create directory structure
mkdir -p tests/edge_cases
mkdir -p tests/platform

# Create __init__.py files
touch tests/edge_cases/__init__.py
touch tests/platform/__init__.py

# Create test files
touch tests/edge_cases/test_empty_inputs.py
touch tests/edge_cases/test_malformed_data.py
touch tests/edge_cases/test_concurrent_access.py
touch tests/edge_cases/test_resource_limits.py
touch tests/platform/test_macos_edge_cases.py

# Create pytest configuration
cat >> pytest.ini << EOL
[pytest]
markers =
    edge_case: Edge case tests
    macos: macOS-specific tests
    slow: Slow-running tests
EOL
```

### Step 2: Implement Tests (Category by Category)
```bash
# Week 13, Day 1: Empty inputs + Malformed data
# Implement 5 + 8 = 13 tests (2.5 hours)

# Week 13, Day 2: Concurrent access + Resource limits
# Implement 6 + 4 = 10 tests (2.5 hours)

# Week 14, Day 1: Mac-specific edge cases
# Implement 4 tests (1 hour)
```

### Step 3: Create Edge Case Handlers (Parallel)
As tests are written, implement defensive code:

```python
# src/utils/validation.py
def validate_input(value, allow_empty=False, max_length=None):
    """Defensive input validation"""
    if value is None:
        if allow_empty:
            return ""
        raise ValueError("Input cannot be None")
    
    if isinstance(value, str):
        value = value.strip()
        if not value and not allow_empty:
            raise ValueError("Input cannot be empty")
        
        if max_length and len(value) > max_length:
            raise ValueError(f"Input exceeds max length {max_length}")
    
    return value

# src/utils/error_recovery.py
def safe_load_yaml(file_path):
    """Safely load YAML with error recovery"""
    try:
        with open(file_path) as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        logger.error(f"YAML syntax error in {file_path}: {e}")
        return None
    except FileNotFoundError:
        logger.warning(f"File not found: {file_path}")
        return {}
```

### Step 4: Document Patterns (30 minutes)
```markdown
# docs/edge-case-patterns.md

## Common Edge Case Patterns

### Pattern 1: Defensive Input Validation
Always validate inputs at system boundaries...

### Pattern 2: Graceful Degradation
When resources are constrained, degrade gracefully...

### Pattern 3: Clear Error Messages
Always provide actionable error messages...
```

---

## 🎯 Success Criteria

```yaml
success_criteria:
  - metric: "Test coverage"
    target: "26/26 tests implemented"
    validation: "pytest tests/edge_cases/ tests/platform/ -v"
    
  - metric: "All tests passing"
    target: "100% pass rate"
    validation: "No failures, no warnings"
    
  - metric: "Edge case handlers"
    target: "Defensive code for all categories"
    validation: "Code review + manual testing"
    
  - metric: "Documentation"
    target: "Edge case pattern guide complete"
    validation: "docs/edge-case-patterns.md exists"
    
  - metric: "Mac compatibility"
    target: "All Mac-specific tests passing"
    validation: "macOS test suite 100%"
```

---

## 📋 Task Checklist

### Week 13 Tasks
- [ ] Create test infrastructure (directories, __init__.py)
- [ ] Implement Category 1: Empty inputs (5 tests)
- [ ] Implement Category 2: Malformed data (8 tests)
- [ ] Implement Category 3: Concurrent access (6 tests)
- [ ] Implement Category 4: Resource limits (4 tests)
- [ ] Add defensive validation utilities

### Week 14 Tasks
- [ ] Implement Category 5: Mac-specific (4 tests)
- [ ] Create edge case handler utilities
- [ ] Document edge case patterns
- [ ] Run full test suite validation
- [ ] Update MAC-PARALLEL-TRACK-DESIGN.md
- [ ] Commit and push to feature branch

---

## 🔄 Git Workflow

```bash
# Create feature branch
git checkout -b feature/phase-5.3-edge-cases

# Commit incrementally
git add tests/edge_cases/test_empty_inputs.py
git commit -m "Phase 5.3.1: Add empty input edge case tests (5/26)"

git add tests/edge_cases/test_malformed_data.py
git commit -m "Phase 5.3.2: Add malformed data edge case tests (13/26)"

# ... continue for each category

# Final commit
git add .
git commit -m "Phase 5.3 complete: All 26 edge case tests implemented"
git push origin feature/phase-5.3-edge-cases
```

---

## 📊 Progress Tracking

```bash
# Track progress
python3 -m src.operations track_progress \
  --phase "5.3" \
  --task "5.3.1" \
  --status "in-progress" \
  --machine "Mac"

# View status
python3 -m src.operations status --machine "Mac" --phase "5.3"
```

---

## 🔍 Testing Commands

```bash
# Run all edge case tests
pytest tests/edge_cases/ -v

# Run Mac-specific tests only
pytest tests/platform/test_macos_edge_cases.py -v -m macos

# Run with coverage
pytest tests/edge_cases/ --cov=src --cov-report=html

# Run slow tests separately
pytest tests/edge_cases/ -v -m "not slow"  # Quick tests
pytest tests/edge_cases/ -v -m slow        # Slow tests
```

---

## 📚 Reference Documents

- **Main Plan:** `MAC-PARALLEL-TRACK-DESIGN.md`
- **Status:** `CORTEX2-STATUS.MD`
- **Testing Guide:** `docs/testing-guide.md` (to be created)
- **YAML Examples:** `cortex-brain/brain-protection-rules.yaml`

---

## ✅ Deliverables

1. **26 edge case tests** across 5 files
2. **Defensive validation utilities** in `src/utils/validation.py`
3. **Error recovery helpers** in `src/utils/error_recovery.py`
4. **Edge case pattern documentation** in `docs/edge-case-patterns.md`
5. **Updated progress tracking** in `MAC-PARALLEL-TRACK-DESIGN.md`

---

**Status:** 📋 READY TO START  
**Created:** 2025-11-10  
**Author:** Asif Hussain  
**Next Step:** Create test infrastructure (30 minutes)

---

*This plan is part of the Mac parallel development track (Phase 5.3). See MAC-PARALLEL-TRACK-DESIGN.md for overall timeline.*
