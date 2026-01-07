# Code Quality & Logic Issue Detection Framework

**Purpose:** Automated detection of code quality issues and logic vulnerabilities  
**Created:** December 11, 2025  
**Status:** 🟢 FRAMEWORK READY

---

## 🎯 Issue Priority Levels

### P0 - CRITICAL (Production Risk)
**Impact:** Data corruption, application crashes, security vulnerabilities

**Detection Criteria:**
- Null reference exceptions (missing null checks)
- Race conditions (shared state without synchronization)
- Transaction boundary violations (partial updates)
- Unhandled exceptions in critical paths
- SQL injection vulnerabilities
- Unclosed resources (connections, streams)
- Deadlock potential (nested locks)
- Data integrity violations (orphaned records)

**Example from Rollover Logic:**
```csharp
// P0: Potential partial update if transaction fails mid-batch
await UpdateReimbursementAccountsAsync(batch);
await PublishBalanceChangedEventsForBatchAsync(batch); // Not in same transaction!
```

---

### P1 - HIGH (Performance/Scalability Risk)
**Impact:** System slowdowns, memory exhaustion, scalability bottlenecks

**Detection Criteria:**
- N+1 query problems (missing eager loading)
- Unbounded loops (no pagination, batch limits)
- Synchronous blocking in async code
- Memory leaks (event handler subscriptions)
- Missing query timeouts
- Large object allocations in loops
- Inefficient LINQ queries
- Missing database indexes (inferred from queries)

**Example from Rollover Logic:**
```csharp
// P1: Potential memory issue with large datasets
var allAccounts = await GetAllEligibleAccountsAsync(); // No pagination!
```

---

### P2 - MEDIUM (Maintainability Risk)
**Impact:** Technical debt, harder to maintain, increased bug risk

**Detection Criteria:**
- Code duplication (DRY violations)
- Complex methods (cyclomatic complexity > 10)
- Long parameter lists (> 5 parameters)
- God classes (> 500 lines)
- Tight coupling (too many dependencies)
- Missing abstractions
- Inconsistent error handling patterns
- Magic numbers/strings

**Example from Rollover Logic:**
```csharp
// P2: Magic number - should be configuration
var batches = accounts.Split(1000); // What if we need to tune this?
```

---

### P3 - LOW (Code Quality/Style)
**Impact:** Readability issues, documentation gaps

**Detection Criteria:**
- Missing XML documentation
- Inconsistent naming conventions
- Unused code (dead code)
- Empty catch blocks
- Long methods (> 100 lines)
- TODO comments in production code
- Commented-out code
- Missing unit tests

**Example from Rollover Logic:**
```csharp
// P3: Missing documentation
public async Task<int> CalculateForefeitAndCarryoverBalanceEOYAllEmployersIdAsyncV2() 
{
    // No XML doc comment explaining complex business logic
}
```

---

## 🔍 Edge Case Analysis Methodology

### 1. Null Reference Analysis
**Objective:** Find variables that could be null without checks

**Detection Pattern:**
```csharp
// ISSUE: No null check before property access
var account = await GetAccountAsync(id);
var balance = account.Balance; // ❌ Potential NullReferenceException

// SAFE:
var account = await GetAccountAsync(id);
if (account != null) {
    var balance = account.Balance; // ✅ Protected
}
```

**Edge Cases to Identify:**
- Method returns null but caller doesn't check
- Navigation properties accessed without null check
- LINQ FirstOrDefault without null handling
- Deserialization results not validated

---

### 2. Concurrency & Race Conditions
**Objective:** Find shared state without synchronization

**Detection Pattern:**
```csharp
// ISSUE: Shared collection without thread-safe access
private List<Result> _results = new List<Result>();
Parallel.ForEach(items, item => {
    _results.Add(ProcessItem(item)); // ❌ Race condition!
});

// SAFE:
var results = new ConcurrentBag<Result>();
Parallel.ForEach(items, item => {
    results.Add(ProcessItem(item)); // ✅ Thread-safe
});
```

**Edge Cases to Identify:**
- Parallel.ForEach with non-thread-safe collections
- Async methods modifying shared state
- Static fields accessed from multiple threads
- Missing locks on critical sections

---

### 3. Transaction Boundary Violations
**Objective:** Find operations that should be atomic but aren't

**Detection Pattern:**
```csharp
// ISSUE: Multiple database operations not in same transaction
await UpdateAccountBalance(accountId, newBalance);
await CreateAuditLog(accountId, "Balance updated"); // ❌ If this fails, inconsistent state
await PublishEvent(new BalanceChangedEvent(accountId)); // ❌ Not transactional

// SAFE:
using (var transaction = new TransactionScope(TransactionScopeAsyncFlowOption.Enabled)) {
    await UpdateAccountBalance(accountId, newBalance);
    await CreateAuditLog(accountId, "Balance updated");
    transaction.Complete(); // ✅ All or nothing
}
// Note: Event publishing typically happens AFTER transaction commits
```

**Edge Cases to Identify:**
- Database write + event publish without transaction coordination
- Multiple table updates without transaction scope
- Nested transactions without proper handling
- Long-running transactions (timeout risk)

---

### 4. N+1 Query Problems
**Objective:** Find inefficient database access patterns

**Detection Pattern:**
```csharp
// ISSUE: N+1 queries (1 for accounts + N for claims)
var accounts = await dbContext.Accounts.ToListAsync();
foreach (var account in accounts) {
    var claims = await dbContext.Requests
        .Where(c => c.AccountId == account.Id)
        .ToListAsync(); // ❌ Executes N queries!
}

// SAFE:
var accounts = await dbContext.Accounts
    .Include(a => a.Requests) // ✅ Eager load with single query
    .ToListAsync();
```

**Edge Cases to Identify:**
- Loops containing database queries
- Missing Include() for navigation properties
- Lazy loading in loops
- Repository calls inside loops

---

### 5. Exception Handling Gaps
**Objective:** Find unhandled exception scenarios

**Detection Pattern:**
```csharp
// ISSUE: External call without exception handling
var response = await httpClient.GetAsync(externalApiUrl); // ❌ Network failures unhandled
var data = await response.Content.ReadAsAsync<Data>(); // ❌ Deserialization failures unhandled

// SAFE:
try {
    var response = await httpClient.GetAsync(externalApiUrl);
    response.EnsureSuccessStatusCode();
    var data = await response.Content.ReadAsAsync<Data>();
} catch (HttpRequestException ex) {
    _logger.LogError(ex, "Failed to call external API");
    throw; // Or handle gracefully
}
```

**Edge Cases to Identify:**
- External API calls without try/catch
- File I/O without error handling
- Async operations without timeout
- Empty catch blocks (swallowing exceptions)

---

### 6. Resource Management Issues
**Objective:** Find unclosed resources (memory leaks)

**Detection Pattern:**
```csharp
// ISSUE: DbConnection not disposed
var connection = new SqlConnection(connectionString);
connection.Open();
var command = connection.CreateCommand();
// ❌ If exception occurs, connection never closed!

// SAFE:
using (var connection = new SqlConnection(connectionString)) {
    connection.Open();
    var command = connection.CreateCommand();
    // ✅ Automatically disposed even if exception
}
```

**Edge Cases to Identify:**
- IDisposable objects not in using statement
- Event handler subscriptions never unsubscribed
- HttpClient created in loops (port exhaustion)
- Streams not closed

---

### 7. Data Validation Gaps
**Objective:** Find missing input validation

**Detection Pattern:**
```csharp
// ISSUE: No validation on input parameters
public async Task ProcessCarryOver(int accountId, decimal amount) {
    // ❌ What if accountId <= 0?
    // ❌ What if amount is negative?
    await UpdateBalance(accountId, amount);
}

// SAFE:
public async Task ProcessCarryOver(int accountId, decimal amount) {
    if (accountId <= 0) throw new ArgumentException("Invalid account ID");
    if (amount < 0) throw new ArgumentException("Amount cannot be negative");
    await UpdateBalance(accountId, amount);
}
```

**Edge Cases to Identify:**
- Public methods without parameter validation
- Missing null checks on reference parameters
- No bounds checking on numeric inputs
- String inputs not validated (length, format)

---

### 8. Async/Await Anti-Patterns
**Objective:** Find incorrect async usage

**Detection Pattern:**
```csharp
// ISSUE: Blocking on async code
var result = SomeAsyncMethod().Result; // ❌ Deadlock risk!
var result2 = SomeAsyncMethod().GetAwaiter().GetResult(); // ❌ Still blocking!

// SAFE:
var result = await SomeAsyncMethod(); // ✅ Proper async

// ISSUE: Async void (except event handlers)
public async void ProcessData() { // ❌ Can't be awaited, exceptions lost!
}

// SAFE:
public async Task ProcessDataAsync() { // ✅ Returns Task
}
```

**Edge Cases to Identify:**
- .Result or .Wait() on Task
- Async void methods
- Missing ConfigureAwait in libraries
- Fire-and-forget async calls (no await)

---

## 📋 Issue Detection Batch Integration

**Add to test-plan-v2-batched.md as Batch 16:**

### BATCH 16: Code Quality & Logic Issue Analysis (90 mins)

**Objective:** Detect P0-P3 issues through static code analysis

#### Tasks
- [ ] Run null reference analysis on all methods
- [ ] Detect race conditions in parallel code
- [ ] Identify transaction boundary violations
- [ ] Find N+1 query patterns
- [ ] Map exception handling gaps
- [ ] Check resource disposal (using statements)
- [ ] Validate input parameter checking
- [ ] Detect async/await anti-patterns
- [ ] Generate prioritized issue backlog

#### Expected Outputs
- `findings/p0-critical-issues.md` (production risks)
- `findings/p1-high-issues.md` (performance/scalability)
- `findings/p2-medium-issues.md` (maintainability)
- `findings/p3-low-issues.md` (code quality)
- `findings/issue-summary-dashboard.md` (executive summary)

#### AST Enhancements Needed
- Control flow graph generation (null check validation)
- Exception handling coverage analysis
- Transaction scope detection
- Thread-safety analysis
- Resource disposal tracking

---

## 🎯 Issue Report Template

**Location:** `findings/p{N}-{priority}-issues.md`

**Format:**
```markdown
# P{N} - {PRIORITY} Issues

**Total Issues:** {count}  
**Analysis Date:** {date}

---

## Issue #{ID}: {Title}

**Priority:** P{N}  
**Category:** {Null Safety | Concurrency | Transactions | Performance | etc.}  
**File:** {path/to/file.cs}  
**Line:** {line number}  
**Method:** {MethodName}

### Description
{What the issue is}

### Risk
{What could go wrong}

### Edge Case Scenario
```csharp
// Example of when this fails
{code showing the edge case}
```

### Evidence (Code Snippet)
```csharp
{actual code with issue}
```

### Recommended Fix
```csharp
{suggested code fix}
```

### Impact
- **Data Risk:** {High/Medium/Low}
- **Performance Impact:** {High/Medium/Low}
- **User Impact:** {description}

---
```

---

## 🔍 Detection Algorithms (Pseudocode)

### Null Reference Detector
```python
def detect_null_references(method_ast):
    issues = []
    for statement in method_ast.statements:
        if is_method_call(statement):
            return_type = get_return_type(statement.method)
            if is_nullable(return_type):
                # Check if next statement checks for null
                next_stmt = get_next_statement(statement)
                if not is_null_check(next_stmt, statement.variable):
                    issues.append({
                        "type": "P0",
                        "category": "Null Safety",
                        "line": statement.line,
                        "risk": "NullReferenceException",
                        "variable": statement.variable
                    })
    return issues
```

### Transaction Boundary Detector
```python
def detect_transaction_violations(method_ast):
    issues = []
    db_writes = []
    transaction_scope = None
    
    for statement in method_ast.statements:
        if is_transaction_scope(statement):
            transaction_scope = statement
        elif is_database_write(statement):
            db_writes.append(statement)
    
    # If multiple writes without transaction scope
    if len(db_writes) > 1 and not transaction_scope:
        issues.append({
            "type": "P0",
            "category": "Transaction Safety",
            "line": db_writes[0].line,
            "risk": "Partial updates, data inconsistency",
            "writes": len(db_writes)
        })
    
    return issues
```

### N+1 Query Detector
```python
def detect_n_plus_1_queries(method_ast):
    issues = []
    
    for loop in method_ast.loops:
        db_queries = find_database_queries_in_loop(loop)
        if len(db_queries) > 0:
            issues.append({
                "type": "P1",
                "category": "Performance",
                "line": loop.line,
                "risk": "N+1 query problem",
                "queries_in_loop": len(db_queries)
            })
    
    return issues
```

---

## 📊 Issue Summary Dashboard Template

**Location:** `findings/issue-summary-dashboard.md`

```markdown
# Code Quality & Logic Issue Summary

**Analysis Date:** {date}  
**Files Analyzed:** {count}  
**Methods Analyzed:** {count}

---

## Priority Breakdown

| Priority | Count | % of Total | Critical Files |
|----------|-------|------------|----------------|
| P0 (Critical) | {count} | {%} | {top 3 files} |
| P1 (High) | {count} | {%} | {top 3 files} |
| P2 (Medium) | {count} | {%} | {top 3 files} |
| P3 (Low) | {count} | {%} | {top 3 files} |

---

## Issue Category Breakdown

| Category | P0 | P1 | P2 | P3 | Total |
|----------|----|----|----|----|-------|
| Null Safety | {#} | {#} | {#} | {#} | {#} |
| Concurrency | {#} | {#} | {#} | {#} | {#} |
| Transactions | {#} | {#} | {#} | {#} | {#} |
| Performance | {#} | {#} | {#} | {#} | {#} |
| Exception Handling | {#} | {#} | {#} | {#} | {#} |
| Resource Management | {#} | {#} | {#} | {#} | {#} |
| Data Validation | {#} | {#} | {#} | {#} | {#} |
| Async Patterns | {#} | {#} | {#} | {#} | {#} |

---

## Top 10 Risky Files

| Rank | File | P0 | P1 | P2 | P3 | Risk Score |
|------|------|----|----|----|----|------------|
| 1 | {file} | {#} | {#} | {#} | {#} | {score} |
| ... | ... | ... | ... | ... | ... | ... |

**Risk Score Formula:** `(P0 * 10) + (P1 * 5) + (P2 * 2) + (P3 * 1)`

---

## Recommended Actions

### Immediate (P0 - This Sprint)
1. {Issue description} - {File}:{Line}
2. {Issue description} - {File}:{Line}
3. ...

### High Priority (P1 - Next 2 Sprints)
1. {Issue description} - {File}:{Line}
2. ...

### Technical Debt (P2/P3 - Backlog)
- Total items: {count}
- Estimated effort: {hours}

---

## Rollover Logic Specific Findings

### Critical Issues in Rollover Processing
- [ ] {Issue in CarryoverDollarsDomainService.cs}
- [ ] {Issue in batch processing}
- [ ] {Issue in transaction handling}

### Performance Concerns
- [ ] {N+1 query in rollover batch fetch}
- [ ] {Memory allocation in parallel processing}

---
```

---

## 🚀 Execution Instructions

### Manual Execution (Without AST)
```powershell
# Search for potential null reference issues
Select-String -Path **\*.cs -Pattern "\.\w+\(" | 
    Select-String -NotMatch "if.*null|?." | 
    Select-Object -First 50

# Find async void methods
Select-String -Path **\*.cs -Pattern "async void" | 
    Select-Object Path, LineNumber

# Find .Result or .Wait() usage
Select-String -Path **\*.cs -Pattern "\.Result|\.Wait\(\)" |
    Select-Object Path, LineNumber

# Find database queries in loops
Select-String -Path **\*.cs -Pattern "foreach.*\{|for.*\{" -Context 0,5 |
    Where-Object { $_.Context.PostContext -match "dbContext\.|Repository\." }
```

### AST-Powered Execution (Future)
```powershell
# Once AST enhanced
cortex analyze-quality --path "C:\PROJECTS\Product.PaymentAccounts" --output "RA-Domain/findings"
```

---

## 📚 References

- **Static Analysis Best Practices:** Microsoft Code Analysis Guidelines
- **Async Best Practices:** https://github.com/davidfowl/AspNetCoreDiagnosticScenarios
- **Transaction Patterns:** EF Core Transaction Documentation
- **Concurrency Patterns:** .NET Threading Best Practices

---

**Status:** 🟢 FRAMEWORK READY FOR BATCH 16 EXECUTION

**Next:** Add Batch 16 to main test plan, execute after Batch 15 (Synthesis)

