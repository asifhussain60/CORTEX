# Phase 9: Production Deployment Guide

**Phase:** 9 of 9 (Final Production Certification)  
**Timeline:** Week 3-4 (2 weeks)  
**Status:** ⚠️ 85% Complete  
**Priority:** 🔴 **CRITICAL** - Final barrier to production

---

## 📋 Overview

### What This Phase Delivers

Complete production certification through data validation, load testing, operational readiness, and final sign-off.

### Current Status (85% Complete)

| Component | Target | Current | Status |
|-----------|--------|---------|--------|
| **Functional Parity** | 100% | 95% | ⚠️ Missing 5% |
| **EF Core Testing** | Complete | Pending | ⚠️ Blocked by Phase 2 |
| **Data Validation** | 100+ scenarios | 0 | ⏳ Week 3 |
| **Load Testing** | 1000 req/sec | Unknown | ⏳ Week 3-4 |
| **Runbooks** | Complete | 0% | ⏳ Week 4 |
| **Ops Training** | Complete | 0% | ⏳ Week 4 |

### Prerequisites

- ✅ Phase 2 complete (EF Core tested)
- ✅ All integration tests passing
- ✅ Performance benchmarks met (<100ms)
- ✅ Security audit passed

---

## 🎯 Week 3: Production Data Validation

### Goal

Verify data integrity with real production scenarios using anonymized data.

---

### Task 1: Extract Anonymized Production Data (4 hours)

**Objective:** Get representative sample without exposing PII/PII

**Steps:**

```sql
-- 1. Identify representative employers (anonymize IDs)
SELECT TOP 10
    NEWID() AS AnonymizedEmployerId,
    COUNT(*) AS InvoiceCount,
    SUM(Amount) AS TotalAmount
FROM TransactionInvoices
GROUP BY EmployerId
ORDER BY COUNT(*) DESC;

-- 2. Extract sample invoices (mask PII)
SELECT
    NEWID() AS InvoiceId,
    'EMP-' + CAST(ROW_NUMBER() OVER (ORDER BY EmployerId) AS NVARCHAR) AS EmployerId,
    'SA-' + CAST(ROW_NUMBER() OVER (ORDER BY AccountCategoryId) AS NVARCHAR) AS AccountCategoryId,
    Amount,
    Status,
    InvoiceType,
    EffectiveDate,
    CreatedDate
INTO ProductionSample_Anonymized
FROM TransactionInvoices
WHERE CreatedDate >= DATEADD(MONTH, -3, GETDATE())  -- Last 3 months
    AND EmployerId IN (SELECT TOP 10 EmployerId FROM TransactionInvoices GROUP BY EmployerId ORDER BY COUNT(*) DESC);

-- 3. Export to CSV
bcp "SELECT * FROM ProductionSample_Anonymized" queryout "C:\Temp\production_sample.csv" -c -t, -S your-server -d your-database -T
```

**Deliverable:** `production_sample.csv` (100+ invoices, anonymized)

---

### Task 2: Run Schema Validation Suite (2 hours)

**Objective:** Ensure data conforms to schema and business rules

**Test Suite:**

```csharp
public class ProductionDataValidationTests
{
    private readonly List<ProductionInvoice> _sampleData;
    
    [Fact]
    public void AllInvoices_ShouldHaveValidEmployerId()
    {
        var invalidInvoices = _sampleData.Where(i => string.IsNullOrWhiteSpace(i.EmployerId));
        invalidInvoices.Should().BeEmpty("All invoices must have EmployerId");
    }
    
    [Fact]
    public void AllInvoices_ShouldHavePositiveAmounts()
    {
        var invalidInvoices = _sampleData.Where(i => i.Amount <= 0);
        invalidInvoices.Should().BeEmpty("All invoices must have positive amounts");
    }
    
    [Fact]
    public void AllInvoices_ShouldHaveValidStatus()
    {
        var validStatuses = new[] { "Pending", "Approved", "Processed", "Voided" };
        var invalidInvoices = _sampleData.Where(i => !validStatuses.Contains(i.Status));
        invalidInvoices.Should().BeEmpty("All invoices must have valid status");
    }
    
    [Fact]
    public void AllInvoices_ShouldHaveReasonableEffectiveDate()
    {
        var cutoff = DateTime.UtcNow.AddYears(-5);
        var futureLimit = DateTime.UtcNow.AddYears(1);
        var invalidInvoices = _sampleData.Where(i => 
            i.EffectiveDate < cutoff || i.EffectiveDate > futureLimit);
        invalidInvoices.Should().BeEmpty("Effective dates should be within reasonable range");
    }
    
    [Fact]
    public void BatchedInvoices_ShouldHaveValidBatchId()
    {
        var invalidInvoices = _sampleData.Where(i => 
            i.BatchId != null && i.BatchId == Guid.Empty);
        invalidInvoices.Should().BeEmpty("Non-null BatchId must be valid GUID");
    }
}
```

**Run validation:**

```bash
dotnet test tests/PaymentProcessor.TransactionInvoices.ProductionValidation/
```

**Expected Results:**
- ✅ All 100+ samples pass validation
- ✅ Zero schema violations
- ✅ Zero business rule violations

**Failure Handling:**
- Document discrepancies
- Update migration scripts if needed
- Re-run validation

---

### Task 3: Verify Data Transformations (4 hours)

**Objective:** Ensure legacy WCF data correctly transforms to modern schema

**Test Scenarios:**

| Scenario | Legacy (WCF) | Modern (REST) | Validation |
|----------|--------------|---------------|------------|
| **Employer contribution split** | `EmployerTransactionDefault` | Mapped to `InvoiceLineItems` | Sum equals invoice amount |
| **Employee contribution split** | `EmployeeTransactionDefault` | Mapped to `InvoiceLineItems` | Sum equals invoice amount |
| **Batch closure** | Status update + replenishment | Status update + new invoice | Batch totals match |
| **Invoice voiding** | Delete record | `IsVoided = true` + audit | Original data preserved |
| **Peg amount calculation** | `GenerateTransactionInvoice` logic | Service layer calculation | Amounts match |

**Test Implementation:**

```csharp
[Fact]
public async Task LegacyEmployerSplit_ShouldMatchModernLineItems()
{
    // Arrange - Legacy data
    var legacyInvoice = new
    {
        EmployerTransactionDefault = 500.00m,
        EmployeeTransactionDefault = 250.00m,
        TotalAmount = 750.00m
    };
    
    // Act - Create modern invoice
    var request = new CreateTransactionInvoiceRequest
    {
        EmployerTransactionDefault = legacyInvoice.EmployerTransactionDefault,
        EmployeeTransactionDefault = legacyInvoice.EmployeeTransactionDefault,
        // ... other fields
    };
    var modernInvoice = await _service.CreateAsync(request);
    var lineItems = await _lineItemRepo.GetByInvoiceIdAsync(modernInvoice.InvoiceId);
    
    // Assert - Verify transformation
    modernInvoice.Amount.Should().Be(legacyInvoice.TotalAmount);
    lineItems.Should().HaveCount(2);
    
    var employerLine = lineItems.First(li => li.LineItemType == "EmployerContribution");
    employerLine.Amount.Should().Be(500.00m);
    
    var employeeLine = lineItems.First(li => li.LineItemType == "EmployeeContribution");
    employeeLine.Amount.Should().Be(250.00m);
    
    lineItems.Sum(li => li.Amount).Should().Be(legacyInvoice.TotalAmount);
}
```

**Deliverable:** Transformation validation report (all scenarios pass)

---

### Task 4: Test Edge Cases (2 hours)

**Edge Cases to Validate:**

```csharp
[Theory]
[InlineData(0.01, 0, 0.01)]        // Minimum employer contribution
[InlineData(0, 0.01, 0.01)]        // Minimum employee contribution
[InlineData(999999.99, 0, 999999.99)]  // Maximum employer contribution
[InlineData(0, 999999.99, 999999.99)]  // Maximum employee contribution
[InlineData(500.005, 250.005, 750.01)] // Rounding test
public async Task CreateInvoice_EdgeCaseAmounts_ShouldHandle(
    decimal employerAmount,
    decimal employeeAmount,
    decimal expectedTotal)
{
    var request = new CreateTransactionInvoiceRequest
    {
        EmployerTransactionDefault = employerAmount,
        EmployeeTransactionDefault = employeeAmount,
        // ...
    };
    
    var invoice = await _service.CreateAsync(request);
    
    invoice.Amount.Should().Be(expectedTotal);
}

[Fact]
public async Task CreateInvoice_NullOptionalFields_ShouldSucceed()
{
    var request = new CreateTransactionInvoiceRequest
    {
        EmployerId = "EMP-001",
        AccountCategoryId = "SA-001",
        PaymentPlanId = "RP-001",
        EmployerTransactionDefault = 500,
        EmployeeTransactionDefault = 250,
        EffectiveDate = DateTime.UtcNow,
        CreatedBy = "test",
        // Optional fields left null:
        InvoiceDescription = null,
        BatchId = null
    };
    
    var invoice = await _service.CreateAsync(request);
    invoice.Should().NotBeNull();
}

[Fact]
public async Task CloseBatch_WithExcludedInvoices_ShouldHandleCorrectly()
{
    // Legacy behavior: Excluded invoices not included in batch total
    var batch = await CreateBatchWithInvoices(
        includedCount: 5,
        excludedCount: 2
    );
    
    await _service.CloseBatchAsync(batch.BatchId);
    
    var closedBatch = await _batchRepo.GetByIdAsync(batch.BatchId);
    closedBatch.InvoiceCount.Should().Be(5);  // Only included invoices
}
```

**Deliverable:** All edge cases pass validation

---

## 🚀 Week 4: Load Testing & Operational Readiness

### Goal

Validate performance under production load and ensure operational team is ready.

---

### Task 1: Configure Load Testing Environment (2 hours)

**Tool:** Apache JMeter or k6

**Setup (k6):**

```bash
# Install k6
choco install k6  # Windows
# or
brew install k6   # Mac

# Create load test script
```

**File:** `tests/LoadTests/transaction-invoice-load-test.js`

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
    stages: [
        { duration: '2m', target: 100 },   // Ramp up to 100 users
        { duration: '5m', target: 100 },   // Stay at 100 users
        { duration: '2m', target: 500 },   // Ramp up to 500 users
        { duration: '5m', target: 500 },   // Stay at 500 users
        { duration: '2m', target: 1000 },  // Ramp up to 1000 users
        { duration: '5m', target: 1000 },  // Stay at 1000 users (peak)
        { duration: '5m', target: 0 },     // Ramp down to 0
    ],
    thresholds: {
        http_req_duration: ['p(95)<200'],  // 95% of requests < 200ms
        http_req_failed: ['rate<0.01'],    // Error rate < 1%
    },
};

export default function () {
    // Create transaction invoice
    let payload = JSON.stringify({
        employerId: `EMP-${__VU}`,  // Virtual user ID
        account_categoryId: `SA-${__VU}`,
        paymentPlanId: 'RP-001',
        employerTransactionDefault: 500.00,
        employeeTransactionDefault: 250.00,
        effectiveDate: new Date().toISOString(),
        invoiceDescription: 'Load test invoice',
        createdBy: 'load-test'
    });
    
    let headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + __ENV.API_TOKEN
    };
    
    let createResponse = http.post(
        'https://your-api.com/api/v1/transaction-invoices',
        payload,
        { headers: headers }
    );
    
    check(createResponse, {
        'status is 201': (r) => r.status === 201,
        'response time < 200ms': (r) => r.timings.duration < 200,
    });
    
    if (createResponse.status === 201) {
        let invoice = JSON.parse(createResponse.body);
        
        // Get invoice details
        let getResponse = http.get(
            `https://your-api.com/api/v1/transaction-invoices/${invoice.invoiceId}`,
            { headers: headers }
        );
        
        check(getResponse, {
            'get status is 200': (r) => r.status === 200,
            'get response time < 50ms': (r) => r.timings.duration < 50,
        });
    }
    
    sleep(1);  // 1 second between iterations
}
```

---

### Task 2: Run Load Tests (4 hours)

**Execute load test:**

```bash
k6 run tests/LoadTests/transaction-invoice-load-test.js
```

**Monitor metrics during test:**

```bash
# CPU usage
Get-Counter '\Processor(_Total)\% Processor Time' -Continuous

# Memory usage
Get-Counter '\Memory\Available MBytes' -Continuous

# Requests per second
# Check application metrics dashboard
```

**Expected Results:**

| Metric | Target | Acceptable | Action if Failed |
|--------|--------|------------|------------------|
| **P95 Latency** | <200ms | <300ms | Optimize queries/add caching |
| **Error Rate** | <0.1% | <1% | Investigate failures |
| **Throughput** | 1000 req/sec | 800 req/sec | Scale infrastructure |
| **CPU Usage** | <70% | <80% | Optimize code/scale up |
| **Memory Usage** | <4GB | <6GB | Fix memory leaks |

**k6 Output Example:**

```
     ✓ status is 201
     ✓ response time < 200ms
     ✓ get status is 200
     ✓ get response time < 50ms

     checks.........................: 100.00% ✓ 48000      ✗ 0
     data_received..................: 120 MB  400 kB/s
     data_sent......................: 60 MB   200 kB/s
     http_req_blocked...............: avg=1.2ms    min=0.5ms  med=1ms     max=50ms   p(95)=2.5ms
     http_req_duration..............: avg=120ms    min=50ms   med=110ms   max=280ms  p(95)=185ms  ← PASS
     http_req_failed................: 0.05%   ✓ 24         ✗ 47976  ← PASS (<1%)
     http_reqs......................: 48000   960/s  ← PASS (near 1000 req/sec)
```

---

### Task 3: Identify Bottlenecks (2 hours)

**Use Application Insights / Performance Profiler:**

```csharp
// Add telemetry to slow operations
using (var operation = _telemetryClient.StartOperation<RequestTelemetry>("CreateTransactionInvoice"))
{
    operation.Telemetry.Properties["EmployerId"] = request.EmployerId;
    
    try
    {
        var invoice = await _service.CreateAsync(request);
        operation.Telemetry.Success = true;
        return invoice;
    }
    catch (Exception ex)
    {
        operation.Telemetry.Success = false;
        _telemetryClient.TrackException(ex);
        throw;
    }
}
```

**Common bottlenecks:**

1. **Database queries** (Solution: Add indexes, use AsNoTracking)
2. **External API calls** (Solution: Add caching, use async)
3. **Serialization** (Solution: Use System.Text.Json, pre-allocate buffers)
4. **Large result sets** (Solution: Add pagination, filter data)

---

### Task 4: Configure Monitoring Alerts (2 hours)

**Azure Monitor Alert Rules:**

```yaml
# Alert: High error rate
alert:
  name: "Transaction Invoices - High Error Rate"
  condition: "requests/failed > 1%"
  window: "5 minutes"
  severity: "Critical"
  actions:
    - email: ops-team@company.com
    - sms: +1-555-1234
    - pagerduty: incident

# Alert: Slow response time
alert:
  name: "Transaction Invoices - Slow Response"
  condition: "requests/duration P95 > 200ms"
  window: "10 minutes"
  severity: "Warning"
  actions:
    - email: dev-team@company.com

# Alert: High CPU
alert:
  name: "Transaction Invoices API - High CPU"
  condition: "cpu_percent > 80%"
  window: "15 minutes"
  severity: "Warning"
  actions:
    - email: ops-team@company.com
```

**Test alerts:**

```bash
# Simulate high error rate
for i in 1..100; do
    curl -X POST https://your-api.com/api/v1/transaction-invoices \
        -H "Content-Type: application/json" \
        -d '{"invalid": "request"}'  # Should return 400
done

# Verify alert triggered
# Check email/SMS/PagerDuty
```

---

### Task 5: Create Runbooks (4 hours)

**Runbook Template:**

**File:** `docs/operations/RUNBOOK-HIGH-ERROR-PaymentProcessorTE.md`

```markdown
# Runbook: High Error Rate (>1%)

## Alert Details
- **Trigger:** Transaction Invoice API error rate exceeds 1% for 5 minutes
- **Severity:** Critical
- **Impact:** Users unable to create/update transaction invoices

## Immediate Actions (5 minutes)

1. **Check Service Health**
   ```bash
   curl https://your-api.com/health
   # Expected: {"status": "Healthy"}
   ```

2. **Review Recent Logs**
   ```bash
   az monitor activity-log list --resource-group your-rg --max-events 50
   # Look for exceptions in last 15 minutes
   ```

3. **Check Dependencies**
   - SQL Server: `sqlcmd -S prod-sql -Q "SELECT 1"`
   - Paragon API: `curl https://paragon-api.com/health`

## Investigation (15 minutes)

1. **Identify Error Pattern**
   ```kusto
   requests
   | where timestamp > ago(15m)
   | where success == false
   | summarize count() by resultCode, operation_Name
   | order by count_ desc
   ```

2. **Common Error Codes**
   - **400 Bad Request:** Validation failures → Check input data
   - **401 Unauthorized:** Auth token expired → Rotate credentials
   - **500 Internal Server Error:** Application error → Check logs
   - **503 Service Unavailable:** Database down → Check SQL Server

## Resolution Steps

### If Database Connection Failure (Most Common)
1. Verify SQL Server status: `Get-Service MSSQL*`
2. Test connection: `sqlcmd -S prod-sql -Q "SELECT @@VERSION"`
3. Check connection pool: Review `DbContext` logs for "pool exhaustion"
4. Scale up database if needed: `az sql db update --service-objective S3`

### If External API Failure
1. Check Paragon API status page
2. Review adapter logs for retry attempts
3. If persistent, enable circuit breaker: Update feature flag `UseCircuitBreaker=true`

### If Application Error
1. Review exception logs in Application Insights
2. Check for recent deployments (rollback if needed)
3. Increase logging: Set `LogLevel:Default=Debug` temporarily
4. Restart API if memory leak suspected

## Rollback Procedure (Last Resort)

1. **Switch to Mock Data Layer** (temporary)
   ```bash
   az webapp config appsettings set --resource-group your-rg --name your-app \
       --settings DataLayer__Provider=Mock
   az webapp restart --resource-group your-rg --name your-app
   ```

2. **Verify health restored**
   ```bash
   curl https://your-api.com/health
   ```

3. **Notify stakeholders** (email template: `OUTAGE-NOTIFICATION.md`)

## Post-Incident

1. **Root Cause Analysis** (RCA document template: `RCA-TEMPLATE.md`)
2. **Update runbook** with lessons learned
3. **Schedule post-mortem** meeting

## Contacts
- **On-Call Engineer:** See PagerDuty rotation
- **Database Team:** dba-team@company.com
- **Tech Lead:** tech-lead@company.com
```

**Create runbooks for:**
- High error rate
- Slow response time
- Database connection failures
- High CPU/memory usage
- Deployment rollback

---

### Task 6: Conduct Operations Training (4 hours)

**Training Agenda:**

```markdown
# Operations Team Training - Transaction Invoices API

## Session 1: System Overview (1 hour)
- Architecture walkthrough
- Data flow diagrams
- Key dependencies

## Session 2: Monitoring & Alerts (1 hour)
- Application Insights dashboard tour
- Alert rules and thresholds
- How to read logs and metrics

## Session 3: Runbook Walkthrough (1 hour)
- Practice using runbooks
- Simulate incidents (high error rate, slow response)
- Q&A

## Session 4: Hands-On Exercises (1 hour)
- Exercise 1: Diagnose slow query
- Exercise 2: Restart application
- Exercise 3: Rollback deployment
- Exercise 4: Swap data layer (Mock ↔ EF Core)
```

**Deliverable:** Signed training completion form from all ops team customers

---

## ✅ Production Deployment Checklist

### Pre-Deployment (1 week before)

- [ ] EF Core fully tested (Phase 2 complete)
- [ ] All integration tests passing
- [ ] Performance benchmarks met
- [ ] Security audit passed
- [ ] Production data validated
- [ ] Load testing completed successfully
- [ ] Monitoring alerts configured
- [ ] Runbooks created and reviewed
- [ ] Operations team trained
- [ ] Rollback procedure tested
- [ ] Stakeholder sign-off obtained

### Deployment Day

- [ ] Deploy to staging environment first
- [ ] Run smoke tests in staging
- [ ] Deploy to production (blue-green deployment)
- [ ] Verify health endpoint returns 200 OK
- [ ] Monitor error rate for 15 minutes
- [ ] Monitor P95 latency for 15 minutes
- [ ] Test 1 manual invoice creation
- [ ] Verify logs are flowing to Application Insights
- [ ] Verify alerts are active

### Post-Deployment (First 24 hours)

- [ ] Monitor error rate (target: <0.1%)
- [ ] Monitor P95 latency (target: <200ms)
- [ ] Monitor CPU usage (target: <70%)
- [ ] Monitor memory usage (target: <4GB)
- [ ] Check for memory leaks (heap should stabilize)
- [ ] Review all error logs
- [ ] On-call engineer briefed

### Post-Deployment (First Week)

- [ ] Daily metrics review
- [ ] Customer feedback collection
- [ ] Performance trend analysis
- [ ] Identify optimization opportunities
- [ ] Update documentation based on learnings

---

## 🚨 Rollback Decision Tree

```
High Error Rate Detected
  │
  ├─ Is it data layer issue?
  │   ├─ YES → Switch to Mock, investigate DB
  │   └─ NO → Continue
  │
  ├─ Is it recent deployment?
  │   ├─ YES (< 2 hours) → Rollback deployment
  │   └─ NO → Continue
  │
  ├─ Is it external dependency?
  │   ├─ YES → Enable circuit breaker, retry logic
  │   └─ NO → Continue
  │
  └─ Application error?
      ├─ YES → Review logs, restart if needed
      └─ NO → Escalate to Tech Lead
```

---

## 📊 Success Criteria

### Phase 9 is complete when:

- ✅ Production data validated (100+ scenarios, zero failures)
- ✅ Load testing passed (1000 req/sec, P95 <200ms, <1% errors)
- ✅ All alerts configured and tested
- ✅ All runbooks created and reviewed
- ✅ Operations team trained (100% attendance)
- ✅ Rollback procedure tested successfully
- ✅ Stakeholder sign-off obtained
- ✅ Production deployment successful
- ✅ Post-deployment monitoring shows stable metrics

---

## 📞 Contacts

| Role | Contact | Escalation |
|------|---------|------------|
| **Tech Lead** | [Name] | [Manager] |
| **DBA Team** | [Email/Slack] | [DBA Manager] |
| **Security Team** | [Email] | [Security Lead] |
| **Operations Team** | [On-Call Rotation] | [Ops Manager] |
| **Product Owner** | [Name] | [VP Product] |

---

**Previous Step:** [← EF Core Migration Guide](./03-EFCORE-MIGPaymentProcessorTION.md)  
**Next Step:** Production Launch! 🚀

**Last Updated:** December 12, 2025
