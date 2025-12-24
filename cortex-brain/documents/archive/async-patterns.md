# ⚡ Async Patterns in CORTEX

**Estimated Time:** 20 minutes  
**Difficulty:** Intermediate  
**Prerequisites:** Basic Python async/await understanding, [SOLID Principles](./solid-principles.md)  
**Last Reviewed:** December 6, 2025

---

## 🚧 Work in Progress

This learning path is currently under development and will be available soon.

**Planned Topics:**
- Understanding async/await in Python
- Threading vs asyncio vs multiprocessing
- Progress monitoring patterns (CORTEX @with_progress decorator)
- Async context managers
- Error handling in async code
- Performance optimization with async

---

## 🎯 What You'll Learn (Coming Soon)

- How to write non-blocking asynchronous code
- When to use async vs threading vs multiprocessing
- CORTEX's progress monitoring system
- Async patterns for I/O-bound operations
- Common async pitfalls and how to avoid them

---

## 📚 Temporary Resources

While this guide is being developed, here are some excellent external resources:

### Video Resources
- [Async Python Basics (25 min)](https://www.youtube.com/watch?v=t5Bo1Je9EmE) - mCoding - Comprehensive intro
- [asyncio Explained (20 min)](https://www.youtube.com/watch?v=2IW-ZEui4h4) - ArjanCodes - Practical examples
- [Threading vs Async (15 min)](https://www.youtube.com/watch?v=9zinZmE3Ogk) - Corey Schafer - Clear comparison

### Documentation
- [Python asyncio Docs](https://docs.python.org/3/library/asyncio.html) - Official reference
- [Real Python: Async IO](https://realpython.com/async-io-python/) - Comprehensive tutorial
- [AsyncIO Best Practices](https://superfastpython.com/asyncio-best-practices/) - Practical guide

### CORTEX Examples (Available Now)

Check CORTEX's progress monitoring system for real async patterns:

**Progress Decorator:**
```python
# File: src/utils/progress_decorator.py
from src.utils.progress_decorator import with_progress, yield_progress

@with_progress(operation_name="Data Processing")
def long_operation(items):
    for i, item in enumerate(items, 1):
        yield_progress(i, len(items), f"Processing {item.name}")
        # Your work here
```

**Implementation Guide:**
- [Progress Monitoring Quick Start](../implementation-guides/progress-monitoring-quick-start.md)

---

## 🔍 CORTEX Async Patterns (Preview)

### Pattern 1: Progress Monitoring
CORTEX uses a decorator pattern for async progress tracking:
- Auto-activation for operations >5 seconds
- Thread-safe progress updates
- ETA calculation
- Hang detection

### Pattern 2: Background Tasks
Long-running operations run in background threads:
- Dashboard server (HTTP)
- Brain indexing operations
- Git history analysis

### Pattern 3: Async Context Managers
Resource management with async:
- Database connections
- File operations
- Network requests

---

## 📊 Expected Completion

**Target Date:** Q1 2025  
**Estimated Content:** 500-600 lines  
**Structure:** Similar to existing learning paths with CORTEX-specific examples

---

## 🚀 In the Meantime

1. **Review Related Paths:**
   - [SOLID Principles](./solid-principles.md) - Foundation concepts
   - [TDD Workflow](./tdd-workflow.md) - Testing async code

2. **Explore CORTEX Code:**
   - `src/utils/progress_decorator.py` - Progress monitoring pattern
   - `src/orchestrators/` - Async orchestration examples

3. **Watch Videos:**
   - Start with mCoding's async basics video
   - Progress to ArjanCodes for practical patterns

4. **Ask CORTEX:**
   - "explain progress monitoring"
   - "show me async patterns in CORTEX"

---

## 📢 Stay Updated

This document will be updated as the learning path is developed. Check back soon!

**Questions?** Ask CORTEX: `"when will async-patterns be available?"` or provide feedback via `cortex feedback`.

---

**Status:** 🚧 Under Development  
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.
