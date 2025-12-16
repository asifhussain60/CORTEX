# Phase 5 Implementation Plan - Legacy Service Migration

**Project:** PaymentProcessor Transaction Invoices Migration (Product.PaymentProcessor.Api)  
**Phase:** 5 - Legacy Service Migration  
**Timeline:** Week 10-11 (2 weeks)  
**Dependencies:** Phase 4 ✅ Complete, Phase 4a ⚠️ Framework Complete (Execution Pending)  
**Target Completion:** End of Week 11

---

## Executive Summary

Phase 5 migrates the remaining legacy WCF service operations to the modernized .NET 8 service layer. This phase focuses on two critical WCF transactions:

1. **Updater_CreatePaymentTransactionInvoices** → `TransactionInvoiceBatchService`
2. **XGenerateTransactionInvoice** → `TransactionInvoiceTransactionService`

Both services already have partial implementations from Phase 3. This phase completes the migration by adding the missing WCF transaction equivalents, comprehensive testing, and shadow testing validation.

---

## Phase 5 Tasks Breakdown

### Task 5.1: Migrate Updater_CreatePaymentTransactionInvoices

**Effort:** 1 day  
**Priority:** High  
**Complexity:** Medium

**Current State:**
- `ITransactionInvoiceBatchService` exists with `CreateBatchAsync()` method
- Method creates a transaction batch but doesn't process individual invoices

**Target State:**
- New `CreateBatchInvoicesAsync(CreateBatchInvoicesDto dto)` method
- Processes list of account_category IDs
- Creates individual invoices for each account_category
- Validates each invoice (balance vs peg amount)
- Handles partial success (some invoices succeed, others fail)
- Returns `BatchInvoiceResultDto` with success/failure counts

**WCF Contract (Legacy):**
```xml
<operation name="Updater_CreatePaymentTransactionInvoices">
  <input>
    <EmployerId>12345</EmployerId>
    <AccountCategoryIds>
      <AccountCategoryId>1001</AccountCategoryId>
      <AccountCategoryId>1002</AccountCategoryId>
      <!-- ... up to 1000 account_categorys -->
    </AccountCategoryIds>
    <EffectiveDate>2025-12-15</EffectiveDate>
    <Description>Q4 2025 Transaction</Description>
  </input>
  <output>
    <BatchId>550e8400-e29b-41d4-a716-446655440000</BatchId>
    <TotalInvoices>2</TotalInvoices>
    <SuccessCount>2</SuccessCount>
    <FailureCount>0</FailureCount>
    <FailedAccountCategorys></FailedAccountCategorys>
  </output>
</operation>
```

**REST Equivalent (Target):**
```http
POST /api/transactioninvoices/batch
Content-Type: application/json

{
  "employerId": "12345",
  "account_categoryIds": [1001, 1002],
  "effectiveDate": "2025-12-15",
  "description": "Q4 2025 Transaction"
}

Response 201 Created:
{
  "batchId": "550e8400-e29b-41d4-a716-446655440000",
  "totalInvoices": 2,
  "successCount": 2,
  "failureCount": 0,
  "failedAccountCategorys": []
}
```

**Implementation Steps:**

1. **Create DTO Classes**
   - `CreateBatchInvoicesDto` (request)
   - `BatchInvoiceResultDto` (response)
   - `FailedInvoiceDto` (failure details)

2. **Update ITransactionInvoiceBatchService Interface**
   ```csharp
   Task<BatchInvoiceResultDto> CreateBatchInvoicesAsync(CreateBatchInvoicesDto dto);
   ```

3. **Implement in TransactionInvoiceBatchService**
   - Validate employer exists
   - Create transaction batch
   - For each account_category ID:
     - Get account_category details
     - Calculate peg amount (invoice amount - balance)
     - If peg > 0, create transaction invoice
     - Track success/failure
   - Return batch result with counts

4. **Business Logic Requirements**
   - Skip account_categorys that already have invoices for the effective date (duplicate prevention)
   - Continue processing even if individual invoices fail (partial success)
   - Calculate batch total amount (sum of all successful invoices)
   - Set batch status to "Pending" (awaiting payment)

5. **Error Handling**
   - Empty employer ID → 400 Bad Request
   - Empty account_category list → 400 Bad Request
   - Employer not found → 404 Not Found
   - Individual account_category failures → Include in `failedAccountCategorys` list

**Test Scenarios:**
- Happy path: 10 account_categorys, all succeed
- Partial success: 10 account_categorys, 8 succeed, 2 fail (account_category not found)
- Duplicate prevention: Skip account_categorys with existing invoices
- Empty employer list → 400
- Large batch: 1000 account_categorys (performance test)

**Acceptance Criteria:**
- ✅ Method signature matches WCF contract
- ✅ All business logic migrated (duplicate prevention, partial success)
- ✅ Error handling matches WCF behavior
- ✅ 10 unit tests covering all scenarios
- ✅ Integration test with mock repository

---

### Task 5.2: Migrate XGenerateTransactionInvoice

**Effort:** 1 day  
**Priority:** High  
**Complexity:** Medium

**Current State:**
- `ITransactionInvoiceTransactionService` exists with `CreateInvoiceAsync()` method
- Method creates invoice but doesn't check balance vs peg logic

**Target State:**
- New `GenerateTransactionInvoiceAsync(GenerateTransactionInvoiceDto dto)` method
- Checks account_category balance vs peg amount
- Only creates invoice if balance < peg (invoice needed)
- Returns result indicating if invoice was created or not needed
- Handles auto-debit logic (create payment record if enabled)

**WCF Contract (Legacy):**
```xml
<operation name="XGenerateTransactionInvoice">
  <input>
    <AccountCategoryId>1001</AccountCategoryId>
    <InvoiceAmount>1000.00</InvoiceAmount>
    <EffectiveDate>2025-12-15</EffectiveDate>
    <Description>Monthly peg invoice</Description>
  </input>
  <output>
    <InvoiceId>123e4567-e89b-12d3-a456-426614174000</InvoiceId>
    <InvoiceCreated>true</InvoiceCreated>
    <Reason>Balance below peg amount</Reason>
    <PegAmount>250.00</PegAmount>
  </output>
</operation>
```

**REST Equivalent (Target):**
```http
POST /api/transactioninvoices/generate
Content-Type: application/json

{
  "account_categoryId": 1001,
  "invoiceAmount": 1000.00,
  "effectiveDate": "2025-12-15",
  "description": "Monthly peg invoice"
}

Response 201 Created (invoice created):
{
  "invoiceId": "123e4567-e89b-12d3-a456-426614174000",
  "invoiceCreated": true,
  "reason": "Balance below peg amount",
  "pegAmount": 250.00
}

Response 200 OK (invoice not needed):
{
  "invoiceId": null,
  "invoiceCreated": false,
  "reason": "Balance meets peg requirement",
  "pegAmount": 0.00
}
```

**Implementation Steps:**

1. **Create DTO Classes**
   - `GenerateTransactionInvoiceDto` (request)
   - `GenerateTransactionInvoiceResultDto` (response)

2. **Update ITransactionInvoiceTransactionService Interface**
   ```csharp
   Task<GenerateTransactionInvoiceResultDto> GenerateTransactionInvoiceAsync(GenerateTransactionInvoiceDto dto);
   ```

3. **Implement in TransactionInvoiceTransactionService**
   - Get account_category details (balance, employer ID)
   - Calculate peg amount: `InvoiceAmount - AccountCategoryBalance`
   - If peg > 0:
     - Create transaction invoice with peg amount
     - If auto-debit enabled, create payment record (effective date + 2 business days)
     - Return result with invoiceCreated=true
   - If peg <= 0:
     - Return result with invoiceCreated=false, reason="Balance meets peg requirement"

4. **Business Logic Requirements**
   - Peg calculation: `PegAmount = InvoiceAmount - CurrentBalance`
   - Only create invoice if peg > 0
   - Auto-debit logic:
     - If account_category.AutoDebitEnabled = true
     - Create payment record with amount = PegAmount
     - Set effective date = invoice effective date + 2 business days
     - Set payment status = "Scheduled"
   - Invoice status:
     - If auto-debit enabled → "Pending" (awaiting payment)
     - If auto-debit disabled → "Open" (manual payment required)

5. **Error Handling**
   - AccountCategory not found → 404 Not Found
   - Zero/negative invoice amount → 400 Bad Request
   - Invalid effective date (past date) → 400 Bad Request

**Test Scenarios:**
- Happy path: Balance below peg → invoice created
- Balance meets peg → invoice not created
- Balance equals invoice → peg = 0, invoice not created
- Balance one cent below invoice → peg = 0.01, invoice created
- Auto-debit enabled → payment record created
- Auto-debit disabled → no payment record
- Zero invoice amount → 400
- Negative invoice amount → 400
- AccountCategory not found → 404

**Acceptance Criteria:**
- ✅ Method signature matches WCF contract
- ✅ Peg calculation logic correct (InvoiceAmount - Balance)
- ✅ Auto-debit logic implemented
- ✅ Error handling matches WCF behavior
- ✅ 9 unit tests covering all scenarios
- ✅ Integration test with mock repository

---

### Task 5.3: Create Automated Test Suite

**Effort:** 2 days  
**Priority:** Critical  
**Complexity:** High

**Target:** 90% overall test coverage

**Test Categories:**

1. **Unit Tests (Service Layer)**
   - TransactionInvoiceBatchService (new methods)
   - TransactionInvoiceTransactionService (new methods)
   - Mock all repository dependencies
   - Test business logic in isolation

2. **Integration Tests (End-to-End)**
   - API → Service → Repository → In-Memory Database
   - Test complete workflows
   - Validate database persistence
   - Check audit logging

3. **Edge Case Tests**
   - Boundary conditions (zero amounts, maximum decimals)
   - Large data volumes (1000 account_categorys)
   - Concurrent requests
   - Timeout scenarios

4. **Error Handling Tests**
   - Validation errors (400)
   - Not found errors (404)
   - Conflict errors (409)
   - Server errors (500)

5. **Performance Tests**
   - Batch processing: 100 account_categorys <5 seconds
   - Single invoice generation: <500ms
   - Database query optimization

**Test File Organization:**
```
tests/PaymentProcessor.TransactionInvoices.Core.Tests/
├── Services/
│   ├── TransactionInvoiceBatchServiceTests.cs
│   ├── TransactionInvoiceTransactionServiceTests.cs
│   └── Legacy/
│       ├── CreateBatchInvoicesTests.cs (Task 5.1 tests)
│       └── GenerateTransactionInvoiceTests.cs (Task 5.2 tests)
└── Integration/
    ├── BatchInvoiceWorkflowTests.cs
    └── GenerateInvoiceWorkflowTests.cs
```

**Coverage Targets:**
- Service layer: 95%
- Repository layer: 95% (already achieved in Phase 2)
- Overall: 90%

**Test Execution:**
```bash
dotnet test --collect:"XPlat Code Coverage"
dotnet reportgenerator -reports:**/coverage.cobertura.xml -targetdir:coverage-report
```

**Acceptance Criteria:**
- ✅ 40+ new tests added (20 unit, 15 integration, 5 edge case)
- ✅ All tests passing (100% pass rate)
- ✅ Code coverage ≥ 90%
- ✅ No skipped or ignored tests

---

### Task 5.4: Validate Unit Test Coverage

**Effort:** 0.5 days  
**Priority:** High  
**Complexity:** Low

**Target:**
- Service layer: 95% coverage
- Repository layer: 95% coverage

**Validation Steps:**

1. **Run Coverage Analysis**
   ```bash
   dotnet test --collect:"XPlat Code Coverage" --results-directory ./coverage
   ```

2. **Generate HTML Report**
   ```bash
   reportgenerator -reports:./coverage/**/coverage.cobertura.xml -targetdir:./coverage-report -reporttypes:Html
   ```

3. **Review Coverage Report**
   - Open `coverage-report/index.html`
   - Check service layer coverage (target: 95%)
   - Check repository layer coverage (target: 95%)
   - Identify uncovered lines

4. **Add Missing Tests**
   - Focus on uncovered branches (if/else, switch)
   - Add edge case tests
   - Cover error handling paths

5. **Re-validate**
   - Run coverage again
   - Confirm 95% target achieved

**Acceptance Criteria:**
- ✅ Service layer ≥ 95% coverage
- ✅ Repository layer ≥ 95% coverage
- ✅ Coverage report generated and reviewed
- ✅ All critical paths covered (business logic, error handling)

---

### Task 5.5: Validate Integration Test Coverage

**Effort:** 1 day  
**Priority:** High  
**Complexity:** Medium

**Target:** 90% end-to-end scenario coverage

**Scenarios to Cover:**

1. **Complete Batch Workflow**
   - POST /api/transactioninvoices/batch → Create batch with 10 invoices
   - GET /api/transactionbatches/{batchId} → Retrieve batch
   - POST /api/transactionbatches/{batchId}/close → Close batch
   - Verify database state (batch status, invoice statuses, totals)

2. **Generate Invoice Workflow**
   - POST /api/transactioninvoices/generate → Create invoice (balance below peg)
   - GET /api/transactioninvoices/{invoiceId} → Retrieve invoice
   - Verify peg calculation correct
   - Verify payment record created (if auto-debit)

3. **Error Scenarios**
   - POST with invalid data → 400 response
   - GET non-existent resource → 404 response
   - Close already-closed batch → 409 response

4. **State Transitions**
   - Batch: Open → Pending → Closed
   - Invoice: Open → Pending → Paid/Void

5. **Audit Logging**
   - Verify all operations logged
   - Check user ID, timestamp, operation type

**Test Implementation:**
```csharp
[Fact]
public async Task CompleteBatchWorkflow_Success()
{
    // Arrange: Seed test data
    var client = _factory.CreateClient();
    
    // Act 1: Create batch
    var createResponse = await client.PostAsJsonAsync("/api/transactioninvoices/batch", dto);
    var batchResult = await createResponse.Content.ReadFromJsonAsync<BatchInvoiceResultDto>();
    
    // Act 2: Close batch
    var closeResponse = await client.PostAsync($"/api/transactionbatches/{batchResult.BatchId}/close", null);
    
    // Assert: Verify state
    var batch = await _dbContext.TransactionBatches.FindAsync(batchResult.BatchId);
    Assert.Equal("Closed", batch.Status);
    Assert.Equal(batchResult.SuccessCount, batch.Invoices.Count);
}
```

**Acceptance Criteria:**
- ✅ 15+ integration tests covering all workflows
- ✅ 90% scenario coverage achieved
- ✅ Database state verified after each operation
- ✅ Audit logs verified

---

### Task 5.6: Setup Shadow Testing Infrastructure

**Effort:** 1.5 days  
**Priority:** Critical  
**Complexity:** High

**Objective:** Run WCF and REST operations in parallel and compare results

**Architecture:**
```
ShadowTestingEngine
├── Orchestrator (executes both WCF and REST)
├── WCF Client (calls legacy service)
├── REST Client (calls new API)
├── Comparator (compares responses)
├── Logger (records discrepancies)
└── Reporter (generates HTML/JSON reports)
```

**Implementation:**

1. **Create ShadowTestingEngine.cs**
   ```csharp
   public class ShadowTestingEngine
   {
       public async Task<ShadowTestReport> ExecuteAsync(List<ShadowTestScenario> scenarios)
       {
           var results = new List<ShadowTestResult>();
           
           foreach (var scenario in scenarios)
           {
               // Execute WCF
               var wcfResponse = await _wcfClient.ExecuteAsync(scenario.WcfRequest);
               
               // Execute REST
               var restResponse = await _restClient.ExecuteAsync(scenario.RestRequest);
               
               // Compare
               var discrepancies = _comparator.Compare(wcfResponse, restResponse);
               
               // Record result
               results.Add(new ShadowTestResult
               {
                   ScenarioId = scenario.Id,
                   IsMatch = discrepancies.Count == 0,
                   Discrepancies = discrepancies
               });
           }
           
           return new ShadowTestReport(results);
       }
   }
   ```

2. **Create Shadow Test Scenarios**
   - Reuse 105 scenarios from Phase 4a (test-scenarios.json)
   - Add production-like data scenarios
   - Include high-volume scenarios (batch with 500+ account_categorys)

3. **Comparison Logic**
   - Status code comparison
   - Response body comparison (JSON schema)
   - Business logic validation (amounts, statuses)
   - Performance comparison (response times)

4. **Discrepancy Classification**
   - Critical: Business logic mismatch (incorrect amounts)
   - High: Status code mismatch
   - Medium: Response field mismatch
   - Low: Response time difference >20%

5. **Report Generation**
   - HTML report with pass/fail rate
   - JSON data for trend analysis
   - Discrepancy details with severity
   - Performance comparison charts

**Acceptance Criteria:**
- ✅ ShadowTestingEngine implemented
- ✅ 105+ scenarios configured
- ✅ Comparison logic handles all data types (decimal, DateTime, string)
- ✅ Report generation complete (HTML/JSON)

---

### Task 5.7: Execute Shadow Testing

**Effort:** 2 days  
**Priority:** Critical  
**Complexity:** High

**Target:** <0.1% discrepancy rate (99.9%+ match rate)

**Execution Plan:**

1. **Phase 1: Automated Test Suite (1000+ scenarios)**
   - Run all 105 contract verification scenarios
   - Run 500 production-like scenarios (real employer/account_category data)
   - Run 400 edge case scenarios (large batches, boundary conditions)
   - Total: 1005 automated scenarios

2. **Phase 2: Analyze Results**
   - Calculate match rate: `(Passed / Total) * 100`
   - Group discrepancies by severity
   - Identify patterns (e.g., all decimal precision issues)

3. **Phase 3: Fix Critical Issues**
   - Address all Critical discrepancies (business logic)
   - Address all High discrepancies (status codes)
   - Re-run affected scenarios

4. **Phase 4: Re-validate**
   - Run full suite again
   - Confirm <0.1% discrepancy rate
   - Generate final report

**Discrepancy Rate Calculation:**
```
Match Rate = (Passed Scenarios / Total Scenarios) * 100
Discrepancy Rate = 100 - Match Rate

Target: Discrepancy Rate < 0.1%
Means: Match Rate > 99.9%
```

**Example:**
- Total scenarios: 1005
- Passed: 1004
- Failed: 1
- Match rate: 99.9%
- Discrepancy rate: 0.1% ✅ PASS

**Acceptance Criteria:**
- ✅ Minimum 1000 test scenarios executed
- ✅ Match rate > 99.9% (discrepancy rate < 0.1%)
- ✅ All Critical discrepancies resolved
- ✅ All High discrepancies resolved
- ✅ Shadow testing report generated

---

### Task 5.8: Obtain UAT Sign-Off

**Effort:** 1 day  
**Priority:** Critical  
**Complexity:** Low

**Objective:** Stakeholder approval to proceed to Phase 5a gate

**UAT Activities:**

1. **Preparation**
   - Compile shadow testing report
   - Create UAT presentation deck
   - Schedule stakeholder meeting (Product VP, Engineering Lead, QA Lead)

2. **Presentation**
   - Executive summary (migration progress 60% → 75%)
   - Shadow testing results (99.9%+ match rate)
   - Demo: Side-by-side WCF vs REST execution
   - Code walkthrough (new service methods)
   - Test coverage metrics (95% service, 95% repo, 90% integration)

3. **Q&A Session**
   - Address stakeholder questions
   - Explain any remaining discrepancies (Low/Medium severity)
   - Discuss Phase 5a gate readiness

4. **Sign-Off**
   - Obtain written approval from all stakeholders
   - Document sign-off in UAT-SIGN-OFF.md
   - Update progress tracker

**Deliverables:**
- UAT presentation deck (PDF)
- Shadow testing report (HTML)
- UAT-SIGN-OFF.md with stakeholder signatures
- Updated progress tracker (Phase 5 → 100%)

**Acceptance Criteria:**
- ✅ All stakeholders have reviewed shadow testing report
- ✅ Written sign-off obtained from Product VP
- ✅ Written sign-off obtained from Engineering Lead
- ✅ Written sign-off obtained from QA Lead
- ✅ UAT documentation complete

---

## Phase 5 Deliverables Summary

| Deliverable | Description | Lines of Code |
|-------------|-------------|---------------|
| CreateBatchInvoicesAsync | Batch service migration | ~150 LOC |
| GenerateTransactionInvoiceAsync | Transaction service migration | ~120 LOC |
| DTOs (6 new classes) | Request/response models | ~180 LOC |
| Unit Tests | Service layer tests | ~600 LOC |
| Integration Tests | End-to-end workflow tests | ~450 LOC |
| ShadowTestingEngine | Automated comparison framework | ~400 LOC |
| Shadow Test Report | HTML/JSON reporting | ~300 LOC |
| UAT Documentation | Sign-off and presentation | N/A |

**Total New Code:** ~2,200 lines  
**Total New Tests:** ~40 tests

---

## Phase 5 Success Criteria

| Criterion | Target | Validation Method |
|-----------|--------|-------------------|
| Service Migration | 100% | Both WCF transactions migrated |
| Unit Test Coverage | 95% | dotnet test --collect coverage |
| Integration Test Coverage | 90% | Scenario checklist completed |
| Shadow Test Match Rate | >99.9% | Shadow testing report |
| UAT Approval | 100% | Signed UAT-SIGN-OFF.md |

**Gate Pass Requirements:**
- ✅ All 8 tasks complete
- ✅ Test coverage targets met
- ✅ Shadow testing <0.1% discrepancy
- ✅ UAT sign-off obtained

---

## Phase 5 Timeline with Checkpoints

| Week | Days | Tasks | Deliverables | Checkpoint |
|------|------|-------|--------------|------------|
| Week 10 | Mon-Tue | 5.1, 5.2 | Service migrations complete | ✅ **Checkpoint 1**: Code review, method signatures verified |
| Week 10 | Wed-Fri | 5.3, 5.4 | Test suite + coverage validation | ✅ **Checkpoint 2**: All tests passing, coverage ≥95% |
| Week 11 | Mon-Tue | 5.5, 5.6 | Integration tests + shadow framework | ✅ **Checkpoint 3**: E2E tests passing, shadow engine ready |
| Week 11 | Wed-Thu | 5.7 | Shadow testing execution | ✅ **Checkpoint 4**: Match rate ≥99.9%, report generated |
| Week 11 | Fri | 5.8 | UAT sign-off | ✅ **Checkpoint 5**: Stakeholder approval obtained |

**Total Duration:** 10 working days (2 weeks)

---

## Checkpoint Details

### Checkpoint 1: Service Migration Validation (End of Day 2)

**Success Criteria:**
- ✅ Both service methods implemented (CreateBatchInvoicesAsync, GenerateTransactionInvoiceAsync)
- ✅ Code compiles without errors
- ✅ Method signatures match WCF contracts
- ✅ Business logic documented in code comments
- ✅ Peer code review completed

**Actions if Failed:**
- Review WCF contract documentation
- Fix compilation errors
- Schedule follow-up code review
- Extend timeline by 1 day if needed

**Sign-Off Required:** Engineering Lead

---

### Checkpoint 2: Unit Test Coverage Validation (End of Day 5)

**Success Criteria:**
- ✅ All unit tests passing (100% pass rate)
- ✅ Service layer coverage ≥95%
- ✅ Repository layer coverage ≥95%
- ✅ No skipped or ignored tests
- ✅ Coverage report generated and reviewed

**Actions if Failed:**
- Add missing tests for uncovered branches
- Fix failing tests (root cause analysis)
- Increase test coverage with edge cases
- Extend timeline by 0.5 days if needed

**Sign-Off Required:** QA Lead

**Verification Command:**
```bash
dotnet test --collect:"XPlat Code Coverage"
reportgenerator -reports:**/coverage.cobertura.xml -targetdir:coverage-report
# Review coverage-report/index.html
```

---

### Checkpoint 3: Integration Test & Shadow Framework Validation (End of Day 7)

**Success Criteria:**
- ✅ All integration tests passing (100% pass rate)
- ✅ End-to-end scenario coverage ≥90%
- ✅ Shadow testing framework implemented
- ✅ Shadow test scenarios configured (105+ scenarios)
- ✅ Framework dry-run successful (WCF mock + REST execution)

**Actions if Failed:**
- Add missing integration test scenarios
- Fix database seeding issues
- Debug shadow testing framework
- Extend timeline by 1 day if needed

**Sign-Off Required:** Engineering Lead + QA Lead

**Verification Commands:**
```bash
# Run integration tests
dotnet test --filter "Category=Integration"

# Dry-run shadow testing
dotnet run --project tests/PaymentProcessor.TransactionInvoices.ContractTests -- --dry-run
```

---

### Checkpoint 4: Shadow Testing Execution Validation (End of Day 9)

**Success Criteria:**
- ✅ Minimum 1000 test scenarios executed
- ✅ Match rate ≥99.9% (discrepancy rate <0.1%)
- ✅ Zero critical discrepancies
- ✅ Zero high discrepancies
- ✅ Shadow testing report generated (HTML/JSON)
- ✅ Performance within 20% of WCF baseline

**Actions if Failed:**
- Analyze discrepancy patterns (group by type)
- Fix critical/high discrepancies in REST implementation
- Re-run shadow testing until 99.9% match achieved
- Extend timeline by 1-2 days if needed

**Sign-Off Required:** Product VP + Engineering Lead

**Verification Commands:**
```bash
# Execute full shadow testing suite
dotnet run --project tests/PaymentProcessor.TransactionInvoices.ContractTests

# Check match rate in report
cat reports/latest/verification-summary.md | grep "Match Rate"
```

**Acceptance Thresholds:**
- Match rate: ≥99.9% (required)
- Critical discrepancies: 0 (required)
- High discrepancies: 0 (required)
- Medium discrepancies: <5 (acceptable)
- Low discrepancies: <10 (acceptable)

---

### Checkpoint 5: UAT Sign-Off (End of Day 10)

**Success Criteria:**
- ✅ UAT presentation completed with all stakeholders
- ✅ Shadow testing report reviewed and accepted
- ✅ All stakeholder questions addressed
- ✅ Written sign-off obtained from Product VP
- ✅ Written sign-off obtained from Engineering Lead
- ✅ Written sign-off obtained from QA Lead
- ✅ UAT documentation archived

**Actions if Failed:**
- Schedule follow-up stakeholder meeting
- Address remaining concerns/questions
- Provide additional documentation if requested
- Extend timeline by 1 day if needed

**Sign-Off Required:** Product VP, Engineering Lead, QA Lead (all three required)

**Deliverables:**
- UAT presentation deck (PDF)
- Shadow testing report (HTML)
- UAT-SIGN-OFF.md with signatures
- Updated progress tracker (Phase 5 → 100%)

---

## Checkpoint Escalation Path

**If Checkpoint 1 Fails:**
- Notify: Engineering Lead (immediate)
- Action: Code review session within 4 hours
- Impact: Low (early in phase, easy to recover)

**If Checkpoint 2 Fails:**
- Notify: Engineering Lead + QA Lead (immediate)
- Action: Root cause analysis, add missing tests
- Impact: Medium (mid-phase, 0.5-1 day delay possible)

**If Checkpoint 3 Fails:**
- Notify: Engineering Lead + QA Lead + Product VP (within 2 hours)
- Action: Debug session, prioritize critical integration tests
- Impact: Medium-High (late in phase, 1-2 day delay possible)

**If Checkpoint 4 Fails:**
- Notify: Product VP + Engineering Lead + QA Lead (immediate)
- Action: Emergency fix session, prioritize critical discrepancies
- Impact: High (blocking gate, 1-3 day delay likely, Phase 5a delayed)

**If Checkpoint 5 Fails:**
- Notify: Executive Leadership (immediate)
- Action: Stakeholder alignment meeting, address concerns
- Impact: Critical (Phase 5a blocked, 1-5 day delay possible)

---

## Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| WCF service unavailable for shadow testing | High | Medium | Implement mock WCF proxy for isolated testing |
| Shadow test discrepancies >0.1% | Critical | Medium | Allocate 2 extra days for issue resolution |
| UAT delays (stakeholder availability) | Medium | Medium | Schedule UAT meeting in advance |
| Test coverage gaps | Medium | Low | Daily coverage monitoring during development |

---

## Next Steps After Phase 5

Upon successful completion of Phase 5 and UAT sign-off:

1. **Phase 5a: Data Layer Transition & Schema Validation** (Week 11.5) - MANDATORY GATE
2. **Phase 5b: Documentation & Knowledge Transfer** (Week 12) - MANDATORY GATE
3. **Phase 6: Deployment** (Week 13-14)

---

**Plan Author:** AI Assistant (Phase 5 Planning)  
**Plan Date:** December 12, 2025  
**Status:** Ready for Execution
