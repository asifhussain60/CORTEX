# Tier 1 Test Suite

Comprehensive test coverage for all CORTEX Brain Tier 1 components.

## Test Coverage

**Total: 18 tests** covering:

### ConversationManager (5 tests)
- ✅ CRUD operations (create, read, update, delete)
- ✅ Message operations (add, retrieve, sequence)
- ✅ Full-text search using FTS5
- ✅ Recent conversations retrieval
- ✅ Context resolution

### FIFO Queue (2 tests)
- ✅ Automatic deletion of oldest conversation when exceeding 20
- ✅ Cascade deletion of messages when deleting conversation

### EntityExtractor (4 tests)
- ✅ File path extraction
- ✅ Component name extraction
- ✅ Intent detection (PLAN, EXECUTE, TEST)
- ✅ Reference resolution ("it", "that" → concrete entities)

### FileTracker (3 tests)
- ✅ File modification tracking
- ✅ Co-modification pattern detection
- ✅ Export to Tier 2 format

### Integration (1 test)
- ✅ Full Tier1API workflow (log → search → patterns → stats → health)

### RequestLogger (3 bonus tests)
- ✅ Raw request/response logging
- ✅ Sensitive data redaction (API keys, passwords, tokens)
- ✅ Redaction statistics

## Installation

```bash
# Install test dependencies
pip install -r tests/tier1/requirements.txt

# Or install pytest directly
pip install pytest pytest-cov
```

## Running Tests

```bash
# Run all Tier 1 tests
pytest tests/tier1/test_tier1_suite.py -v

# Run with coverage report
pytest tests/tier1/test_tier1_suite.py -v --cov=CORTEX/src/brain/tier1 --cov-report=term-missing

# Run specific test
pytest tests/tier1/test_tier1_suite.py::test_conversation_crud -v

# Run tests matching a pattern
pytest tests/tier1/test_tier1_suite.py -k "entity" -v

# Run with detailed output
pytest tests/tier1/test_tier1_suite.py -vv -s
```

## Test Structure

Each test follows this pattern:

```python
def test_feature_name(fixture):
    """Test description: What is being tested."""
    # Arrange: Set up test data
    # Act: Execute the functionality
    # Assert: Verify expected behavior
```

## Fixtures

- `temp_db`: Temporary SQLite database with schema
- `api`: Tier1API instance
- `conv_manager`: ConversationManager instance
- `entity_extractor`: EntityExtractor instance
- `file_tracker`: FileTracker instance
- `request_logger`: RequestLogger instance

## Test Data

Tests use:
- Temporary databases (auto-cleaned after each test)
- Synthetic data (no real user data)
- Deterministic test cases (reproducible)

## Performance Targets

All tests should complete in:
- Unit tests: <100ms each
- Integration test: <500ms
- Full suite: <5 seconds

## Exit Criteria

All 18 tests must pass before Tier 1 implementation is considered complete.

```bash
# Expected output:
======================== 18 passed in 2.34s =========================
```

## Troubleshooting

### Import errors
```bash
# Ensure CORTEX package is in PYTHONPATH
export PYTHONPATH=/path/to/CORTEX:$PYTHONPATH
pytest tests/tier1/test_tier1_suite.py -v
```

### Database schema errors
```bash
# Ensure schema.sql is up to date
cat cortex-brain/schema.sql  # Verify Tier 1 tables exist
```

### FTS5 not available
```bash
# Check SQLite version (must be 3.9.0+)
python -c "import sqlite3; print(sqlite3.sqlite_version)"
```

## Future Enhancements

- [ ] Async tests for concurrent operations
- [ ] Performance benchmarks (query speed, bulk operations)
- [ ] Stress tests (1000+ conversations)
- [ ] Fuzzing tests (malformed inputs)
- [ ] Property-based tests (Hypothesis)
