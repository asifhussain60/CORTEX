# CORTEX Tooling Installation Guide

**Last Updated:** January 9, 2025  
**Status:** ✅ Python Dependencies Installed | ⊘ Node.js Optional

---

## 📦 Installed Dependencies

### Python Dependencies (✅ INSTALLED)

| Package | Version | Purpose |
|---------|---------|---------|
| **pytest** | 8.4.2 | Testing framework |
| **pytest-cov** | 4.1.0+ | Test coverage reporting |
| **pytest-mock** | 3.11.1+ | Mocking utilities |
| **PyYAML** | 6.0.3 | YAML parsing (migration scripts) |
| **black** | 23.0.0+ | Code formatting |
| **flake8** | 6.0.0+ | Linting |
| **mypy** | 1.0.0+ | Type checking |
| **faker** | 19.0.0+ | Test data generation |
| **freezegun** | 1.2.2+ | Mock datetime for tests |

### SQLite (✅ VALIDATED)

| Feature | Version | Status |
|---------|---------|--------|
| SQLite | 3.43.2 | ✅ Installed |
| FTS5 Full-Text Search | Enabled | ✅ Supported |

### Node.js Dependencies (⊘ OPTIONAL - for performance testing)

| Package | Version | Purpose |
|---------|---------|---------|
| @playwright/test | 1.40.0+ | Browser automation testing |
| sql.js | 1.10.2+ | SQLite in browser (Phase -1 tests) |
| TypeScript | 5.3.0+ | Type-safe JavaScript |

---

## 🚀 Quick Start

### 1. Verify Installation

```bash
# Run the installation script
python3 scripts/install-cortex.py --skip-node

# Expected output:
# ✓ CORTEX installation complete!
```

### 2. Run Tests

```bash
# Run Tier 1 test suite (18 tests)
pytest tests/tier1/test_tier1_suite.py -v

# Run with coverage report
pytest tests/tier1/test_tier1_suite.py -v --cov=CORTEX/src/brain/tier1 --cov-report=term-missing

# Expected: 18 passed in <5 seconds
```

### 3. Run Migrations

```bash
# Migrate all data to SQLite (Tiers 1-3)
python scripts/migrate-all-tiers.py

# Or migrate specific tier
python scripts/migrate-tier1-to-sqlite.py
python scripts/migrate-tier2-to-sqlite.py
python scripts/migrate-tier3-to-sqlite.py
```

### 4. Validate Migrations

```bash
# Validate all migrations
python scripts/validate-migrations.py

# Validate with performance benchmarks
python scripts/validate-migrations.py --benchmark

# Validate specific tier
python scripts/validate-migrations.py --tier 1
```

---

## 📂 Directory Structure

```
CORTEX/
├── CORTEX/
│   ├── src/
│   │   └── brain/
│   │       ├── tier1/          # ✅ Tier 1 implementation
│   │       │   ├── __init__.py
│   │       │   ├── tier1_api.py
│   │       │   ├── conversation_manager.py
│   │       │   ├── entity_extractor.py
│   │       │   ├── file_tracker.py
│   │       │   └── request_logger.py
│   │       ├── tier2/          # ⏳ Tier 2 (pending)
│   │       └── tier3/          # ⏳ Tier 3 (pending)
│   └── requirements.txt
├── cortex-brain/
│   ├── cortex-brain.db         # SQLite database (created after migration)
│   ├── backups/                # Auto-backups during migration
│   ├── schema.sql              # Database schema
│   └── *.jsonl, *.yaml         # Source data files
├── scripts/
│   ├── install-cortex.py       # ✅ Installation script
│   ├── migrate-all-tiers.py    # ✅ Migration orchestrator
│   ├── migrate-tier1-to-sqlite.py
│   ├── migrate-tier2-to-sqlite.py
│   ├── migrate-tier3-to-sqlite.py
│   ├── migrate-cortex-brain.ps1  # PowerShell wrapper
│   └── validate-migrations.py  # ✅ Validation script
├── tests/
│   ├── tier1/
│   │   ├── test_tier1_suite.py # ✅ 18 tests
│   │   ├── requirements.txt
│   │   └── README.md
│   ├── tier2/                  # ⏳ Pending
│   └── tier3/                  # ⏳ Pending
└── pytest.ini                  # Pytest configuration
```

---

## 🛠️ Development Workflow

### Daily Development

```bash
# 1. Run tests before making changes
pytest tests/tier1/test_tier1_suite.py -v

# 2. Make your changes
# ...

# 3. Run tests again
pytest tests/tier1/test_tier1_suite.py -v

# 4. Format code
black CORTEX/src/brain/tier1/*.py

# 5. Check types
mypy CORTEX/src/brain/tier1/*.py
```

### Using CORTEX Brain Tier 1

```python
from CORTEX.src.brain.tier1 import Tier1API

# Initialize
api = Tier1API("cortex-brain/cortex-brain.db")

# Log a conversation (auto-extraction, auto-tracking)
conv_id = api.log_conversation(
    agent_name="copilot",
    request="Fix authentication bug in src/auth.py",
    response="Fixed by adding null check in validateToken()"
)

# Search conversations
results = api.search("authentication", limit=5)

# Get file co-modification patterns
patterns = api.get_file_patterns("src/auth.py", min_confidence=0.3)

# Get statistics
stats = api.get_stats()
print(f"Total conversations: {stats['total_conversations']}")

# Health check
health = api.health_check()
if not health['healthy']:
    print(f"Warnings: {health['warnings']}")
```

---

## 🧪 Testing Commands

### Run All Tests

```bash
# All Tier 1 tests
pytest tests/tier1/ -v

# Specific test
pytest tests/tier1/test_tier1_suite.py::test_conversation_crud -v

# Tests matching pattern
pytest tests/tier1/ -k "entity" -v
```

### Coverage Reports

```bash
# Terminal coverage
pytest tests/tier1/ --cov=CORTEX/src/brain/tier1 --cov-report=term-missing

# HTML coverage report
pytest tests/tier1/ --cov=CORTEX/src/brain/tier1 --cov-report=html
open htmlcov/index.html
```

### Performance Benchmarks

```bash
# Run validation with benchmarks
python scripts/validate-migrations.py --benchmark

# Expected results:
# - Recent conversations: <100ms ✓
# - FTS5 search: <100ms ✓
# - File patterns: <100ms ✓
```

---

## 🔧 Troubleshooting

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'CORTEX'`

**Solution:**
```bash
# Add CORTEX to PYTHONPATH
export PYTHONPATH=/Users/asifhussain/PROJECTS/CORTEX:$PYTHONPATH

# Or run from project root
cd /Users/asifhussain/PROJECTS/CORTEX
pytest tests/tier1/test_tier1_suite.py -v
```

### Database Not Found

**Problem:** `Database file not found: cortex-brain/cortex-brain.db`

**Solution:**
```bash
# Run migrations to create database
python scripts/migrate-all-tiers.py
```

### FTS5 Not Available

**Problem:** `FTS5 not supported`

**Solution:**
```bash
# Check SQLite version (must be 3.9.0+)
python3 -c "import sqlite3; print(sqlite3.sqlite_version)"

# If < 3.9.0, upgrade SQLite:
brew upgrade sqlite  # macOS
# or download from https://www.sqlite.org/download.html
```

### Node.js Dependencies (Optional)

**Problem:** `Node.js not found`

**Solution:**
```bash
# Install Node.js from https://nodejs.org/
# Then run:
cd CORTEX
npm install
npx playwright install
```

---

## 📊 Installed Features

### ✅ Tier 1: Conversation Storage

- [x] ConversationManager (CRUD, FIFO queue, FTS5 search)
- [x] EntityExtractor (files, components, features, intents)
- [x] FileTracker (co-modification detection, Tier 2 export)
- [x] RequestLogger (privacy-aware raw logging, redaction)
- [x] Tier1API (unified interface)
- [x] 18 comprehensive tests
- [x] Migration validation

### ⏳ Tier 2: Pattern Learning (Pending)

- [ ] PatternStore (pattern CRUD, confidence scoring)
- [ ] FTS5 search for patterns
- [ ] Confidence decay mechanism
- [ ] Pattern learning from Tier 1
- [ ] 20 tests

### ⏳ Tier 3: Development Metrics (Pending)

- [ ] Git metrics collector
- [ ] Test activity analyzer
- [ ] Work pattern detector
- [ ] Correlation engine
- [ ] 12 tests

---

## 📖 Documentation

| Document | Purpose |
|----------|---------|
| `docs/SUB-GROUP-3B-COMPLETE.md` | Tier 1 completion report |
| `docs/GROUP-3-PROGRESS-REPORT.md` | Overall progress tracking |
| `docs/MIGRATION-GUIDE.md` | Migration script documentation |
| `tests/tier1/README.md` | Test suite documentation |
| `CORTEX/cortex.md` | Implementation plan |

---

## 🎯 Next Steps

1. **Run Tests:** `pytest tests/tier1/test_tier1_suite.py -v`
2. **Run Migrations:** `python scripts/migrate-all-tiers.py`
3. **Validate:** `python scripts/validate-migrations.py --benchmark`
4. **Start Using:** See "Using CORTEX Brain Tier 1" section above

---

## 📞 Support

For issues or questions:
1. Check troubleshooting section above
2. Review documentation in `docs/`
3. Check test examples in `tests/tier1/`
4. Review implementation in `CORTEX/src/brain/tier1/`

---

**Installation Status:** ✅ READY  
**Version:** 1.0.0  
**Date:** January 9, 2025
