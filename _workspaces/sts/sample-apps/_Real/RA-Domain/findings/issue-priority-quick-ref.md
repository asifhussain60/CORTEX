# Issue Priority Quick Reference

**Purpose:** Fast lookup guide for categorizing code issues during analysis  
**Created:** December 11, 2025

---

## 🚨 P0 - CRITICAL (Fix Immediately)

**Impact:** Application crashes, data corruption, security vulnerabilities

| Issue Type | Detection Pattern | Example |
|------------|------------------|---------|
| **Null Reference** | Variable used without null check | `var x = GetAccount(); x.Name` (no null check) |
| **Race Condition** | Non-thread-safe collection in parallel code | `List<T>` used in `Parallel.ForEach` |
| **Transaction Violation** | Multiple DB writes without transaction | 2+ `await db.SaveChanges()` not in `TransactionScope` |
| **Unhandled Exception** | Try/catch missing on critical path | External API call without error handling |
| **Resource Leak** | IDisposable not disposed | `DbConnection` opened but not in `using` |
| **Async Void** | `async void` method (except event handlers) | `async void ProcessData()` |
| **Deadlock Risk** | `.Result` or `.Wait()` on async | `task.Result` in async context |
| **SQL Injection** | String concatenation in SQL | `$"SELECT * FROM {table}"` |

**Search Commands:**
```powershell
# Null references (rough heuristic)
Select-String -Path **\*.cs -Pattern "\.\w+\(" | Select-String -NotMatch "if.*null|\?\.|\!\."

# Async void
Select-String -Path **\*.cs -Pattern "async void"

# Blocking async
Select-String -Path **\*.cs -Pattern "\.Result|\.Wait\(\)"

# Non-using IDisposable
Select-String -Path **\*.cs -Pattern "new Sql|new Http|new File" | Select-String -NotMatch "using"
```

---

## ⚠️ P1 - HIGH (Fix This Sprint)

**Impact:** Performance degradation, memory exhaustion, scalability limits

| Issue Type | Detection Pattern | Example |
|------------|------------------|---------|
| **N+1 Query** | DB query inside loop | `foreach(account in accounts) { db.Requests.Where(...) }` |
| **Unbounded Loop** | Loop without pagination/limit | `while(true)` or large `foreach` with no batching |
| **Memory Leak** | Event subscription never unsubscribed | `EventHandler +=` without `-=` |
| **Sync Over Async** | Synchronous blocking in async method | `Thread.Sleep()` in async method |
| **Missing Timeout** | External call without timeout | `httpClient.GetAsync()` with no timeout config |
| **Large Allocation** | Big objects created in loops | `new byte[10000]` inside `foreach` |
| **Missing Index** | Frequent query without index (inferred) | `.Where(x => x.UnindexedColumn)` |
| **Inefficient LINQ** | Multiple enumerations | `.ToList()` called multiple times on same query |

**Search Commands:**
```powershell
# Database queries in loops
Select-String -Path **\*.cs -Pattern "foreach|for\s*\(" -Context 0,10 | Where-Object { $_.Context.PostContext -match "dbContext\.|Repository\.|\.Where\(" }

# Missing await (fire-and-forget)
Select-String -Path **\*.cs -Pattern "\w+Async\(" | Select-String -NotMatch "await"

# Thread.Sleep in async
Select-String -Path **\*.cs -Pattern "Thread\.Sleep"
```

---

## 🔶 P2 - MEDIUM (Technical Debt)

**Impact:** Harder to maintain, increased bug risk over time

| Issue Type | Detection Pattern | Example |
|------------|------------------|---------|
| **Code Duplication** | Similar code blocks repeated | Same logic in 3+ places |
| **Complex Method** | Cyclomatic complexity > 10 | Method with 10+ branches |
| **Long Parameters** | > 5 method parameters | `Method(a, b, c, d, e, f)` |
| **God Class** | Class > 500 lines | Single class doing too much |
| **Tight Coupling** | 10+ constructor dependencies | Constructor with 10+ parameters |
| **Magic Numbers** | Hardcoded values | `if (count > 1000)` without const |
| **Missing Abstraction** | Concrete types in signatures | `public void Process(SqlConnection conn)` |
| **Empty Catch** | Catch block with no action | `catch { }` |

**Search Commands:**
```powershell
# Magic numbers (rough heuristic)
Select-String -Path **\*.cs -Pattern "\s\d{2,}\s|\s\d{2,}\)" | Select-String -NotMatch "const|readonly"

# Empty catch blocks
Select-String -Path **\*.cs -Pattern "catch.*\{" -Context 0,3 | Where-Object { $_.Context.PostContext -match "^\s*\}" }

# Long methods (> 100 lines - approximate)
Get-ChildItem -Recurse -Filter *.cs | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    if ($content -match "(?s)(public|private|protected).*?\{.*?\}") {
        # Complex regex needed - manual review recommended
    }
}
```

---

## ℹ️ P3 - LOW (Nice to Have)

**Impact:** Readability, documentation, minor improvements

| Issue Type | Detection Pattern | Example |
|------------|------------------|---------|
| **Missing XML Doc** | Public method without `///` | Public method missing doc comment |
| **Inconsistent Naming** | Violates C# conventions | `public void process_data()` |
| **Unused Code** | Private method never called | Private method with no references |
| **TODO in Production** | TODO/HACK/FIXME comments | `// TODO: Fix this later` |
| **Commented Code** | Large blocks commented out | 10+ lines of commented code |
| **Long Method** | > 100 lines (but low complexity) | Method doing simple but verbose work |
| **Missing Test** | Public method without test | No test file for class |

**Search Commands:**
```powershell
# TODO/HACK/FIXME
Select-String -Path **\*.cs -Pattern "TODO|HACK|FIXME|XXX"

# Commented code blocks
Select-String -Path **\*.cs -Pattern "^\s*//.*\w" | Group-Object Path | Where-Object { $_.Count -gt 10 }

# Missing XML docs on public methods
Select-String -Path **\*.cs -Pattern "^\s*public" | Select-String -NotMatch "^\s*///"
```

---

## 🎯 Issue Classification Decision Tree

```
Does it cause crashes/data loss?
├─ YES → P0
└─ NO → Does it impact performance/scalability?
    ├─ YES → P1
    └─ NO → Does it increase maintenance burden?
        ├─ YES → P2
        └─ NO → P3
```

---

## 📊 Rollover Logic Specific Watchlist

**Based on initial discovery, watch for:**

### P0 Risks in Rollover Processing
- [ ] Transaction scope around batch updates + event publishing
- [ ] Null checks on account retrieval before balance calculations
- [ ] Thread-safe collections in `SemaphoreSlim(10, 10)` parallel processing
- [ ] Exception handling in batch processing loops

### P1 Risks in Rollover Processing
- [ ] N+1 queries when fetching request data for accounts
- [ ] Memory usage with 1,000 account batches (unbounded?)
- [ ] Missing timeout on external service calls (if any)
- [ ] Inefficient LINQ in balance calculations

### P2 Risks in Rollover Processing
- [ ] Magic number: batch size of 1000 (should be config)
- [ ] Magic number: semaphore limit of 10 (should be config)
- [ ] Code duplication between V1 and V2 methods
- [ ] Complex calculation method (needs decomposition?)

---

## 📝 Issue Report Template (Quick)

```markdown
## Issue #{ID}: {One-line title}

**Priority:** P{0-3} | **Category:** {category} | **File:** {path}:{line}

**Risk:** {What could go wrong}

**Evidence:**
```csharp
{code snippet showing issue}
```

**Fix:**
```csharp
{suggested fix}
```
```

---

**Use this guide during Batch 16 to quickly categorize findings.**

