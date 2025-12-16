# Quick Start Guide - 5 Minutes to Running

**Audience:** New developers joining the PaymentProcessor Transaction Invoices migration project  
**Time Required:** 5-10 minutes  
**Prerequisites:** .NET 8 SDK, Visual Studio 2022 or VS Code

---

## 🚀 Fastest Path to Running Code

### Step 1: Clone & Navigate (30 seconds)

```bash
cd C:\PROJECTS\Platform.Classic\cortex\ra-modernized
```

### Step 2: Restore Dependencies (1 minute)

```bash
dotnet restore
```

### Step 3: Run Tests (2 minutes)

```bash
dotnet test
```

**Expected Output:**
```
Test Run Successful.
Total tests: 87
     Passed: 87
 Total time: 1.5 minutes
```

### Step 4: Start API (30 seconds)

```bash
cd src/PaymentProcessor.TransactionInvoices.API
dotnet run
```

**Expected Output:**
```
info: Microsoft.Hosting.Lifetime[14]
      Now listening on: https://localhost:7001
      Now listening on: http://localhost:5001
```

### Step 5: Open Swagger UI (10 seconds)

Navigate to: **https://localhost:7001/swagger**

🎉 **You're running!** Try creating a transaction invoice via the interactive UI.

---

## 📁 Project Structure (30 seconds to understand)

```
ra-modernized/
├── src/
│   ├── PaymentProcessor.TransactionInvoices.API/              # REST API (Controllers + Middleware)
│   ├── PaymentProcessor.TransactionInvoices.Core/             # Business logic (Services + DTOs)
│   └── PaymentProcessor.TransactionInvoices.Infrastructure/   # Data access (Repositories)
└── tests/
    ├── PaymentProcessor.TransactionInvoices.UnitTests/        # Fast isolated tests
    ├── PaymentProcessor.TransactionInvoices.IntegrationTests/ # Database + API tests
    ├── PaymentProcessor.TransactionInvoices.ContractTests/    # Schema validation
    └── PaymentProcessor.TransactionInvoices.API.Tests/        # HTTP endpoint tests
```

**Key Principle:** Clean Architecture - dependencies flow inward (API → Core ← Infrastructure)

---

## 🧪 Verify Your Setup

### Run Individual Test Projects

```bash
# Unit tests (fastest - no dependencies)
dotnet test tests/PaymentProcessor.TransactionInvoices.UnitTests/

# Integration tests (requires test DB - currently uses Mock)
dotnet test tests/PaymentProcessor.TransactionInvoices.IntegrationTests/

# Contract tests (schema validation)
dotnet test tests/PaymentProcessor.TransactionInvoices.ContractTests/
```

### Try the API

**Using Swagger UI:** https://localhost:7001/swagger

**Using cURL:**
```bash
# Create a transaction invoice
curl -X POST https://localhost:7001/api/v1/transaction-invoices \
  -H "Content-Type: application/json" \
  -d '{
    "employerId": "EMP-001",
    "account_categoryId": "SA-001",
    "paymentPlanId": "RP-001",
    "employerTransactionDefault": 500.00,
    "employeeTransactionDefault": 250.00,
    "effectiveDate": "2025-12-15T00:00:00Z",
    "invoiceDescription": "Payroll transaction",
    "isLSA": false,
    "updateTemplate": true,
    "createdBy": "system"
  }'
```

**Expected Response:**
```json
{
  "invoiceId": "guid-here",
  "invoiceNumber": "INV-0001",
  "amount": 750.00,
  "status": "Pending",
  "createdDate": "2025-12-12T..."
}
```

---

## 🔧 Configuration (Currently: Mock Mode)

### appsettings.Development.json

```json
{
  "DataLayer": {
    "Provider": "Mock",  // ← In-memory data (no database required)
    "ConnectionString": ""
  },
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning"
    }
  }
}
```

**Current Mode:** Mock (in-memory storage)
- ✅ Fast development iteration
- ✅ No database setup required
- ✅ 100+ pre-seeded test scenarios
- ⚠️ Data lost on restart

**Future Mode:** EF Core (production database)
- See [03-EFCORE-MIGPaymentProcessorTION.md](./03-EFCORE-MIGPaymentProcessorTION.md) for migration guide

---

## 🎯 Your First Change (10 minutes)

### Task: Add a New Test

**File:** `tests/PaymentProcessor.TransactionInvoices.UnitTests/Services/TransactionInvoiceServiceTests.cs`

**Add this test:**

```csharp
[Fact]
public async Task CreateAsync_WithZeroAmount_ShouldThrowValidationException()
{
    // Arrange
    var request = new CreateTransactionInvoiceRequest
    {
        EmployerId = "EMP-001",
        AccountCategoryId = "SA-001",
        PaymentPlanId = "RP-001",
        EmployerTransactionDefault = 0,  // Zero amount
        EmployeeTransactionDefault = 0,  // Zero amount
        EffectiveDate = DateTime.UtcNow,
        InvoiceDescription = "Test",
        CreatedBy = "test"
    };

    // Act & Assert
    await Assert.ThrowsAsync<ValidationException>(() =>
        _service.CreateAsync(request));
}
```

**Run the test:**
```bash
dotnet test tests/PaymentProcessor.TransactionInvoices.UnitTests/ --filter "CreateAsync_WithZeroAmount"
```

**Expected:** Test should PASS (validation already implemented)

---

## 📚 What to Read Next

### Understanding the System (30 minutes)

1. **Architecture:** [02-ARCHITECTURE-OVERVIEW.md](./02-ARCHITECTURE-OVERVIEW.md)
   - Understand layers, patterns, and design decisions

2. **Code Review:** `C:\PROJECTS\Platform.Classic\cortex\ra-modernized\.review\MIGPaymentProcessorTION_ANALYSIS_REPORT.md`
   - See quality metrics, improvements, and migration details

3. **API Reference:** [06-API-REFERENCE.md](./06-API-REFERENCE.md)
   - Explore all endpoints and contracts

### Contributing (1 hour)

4. **Testing Guide:** [05-TESTING-GUIDE.md](./05-TESTING-GUIDE.md)
   - Learn testing patterns and best practices

5. **EF Core Migration:** [03-EFCORE-MIGPaymentProcessorTION.md](./03-EFCORE-MIGPaymentProcessorTION.md)
   - Understand Mock → EF Core transition plan

---

## 🚨 Common Setup Issues

### Issue: "dotnet: command not found"

**Solution:** Install .NET 8 SDK
- Download: https://dotnet.microsoft.com/download/dotnet/8.0
- Verify: `dotnet --version` (should show 8.0.x)

### Issue: "Port 7001 already in use"

**Solution:** Kill existing process or change port

```bash
# Windows: Find and kill process
netstat -ano | findstr :7001
taskkill /PID <process_id> /F

# Or change port in launchSettings.json
```

### Issue: Tests failing

**Solution:** Clean and rebuild

```bash
dotnet clean
dotnet restore
dotnet build
dotnet test
```

### Issue: Swagger UI not loading

**Solution:** Check HTTPS certificate

```bash
dotnet dev-certs https --trust
```

**More Help:** [07-TROUBLESHOOTING.md](./07-TROUBLESHOOTING.md)

---

## 🎓 Developer Workflow

### Daily Development Cycle

```bash
# 1. Pull latest changes
git pull origin main

# 2. Create feature branch
git checkout -b feature/your-feature-name

# 3. Make code changes
# ... edit files in VS Code or Visual Studio ...

# 4. Run tests (continuously)
dotnet watch test --project tests/PaymentProcessor.TransactionInvoices.UnitTests/

# 5. Commit when tests pass
git add .
git commit -m "feat: your feature description"

# 6. Push and create PR
git push origin feature/your-feature-name
```

### Before Creating Pull Request

```bash
# Run ALL tests
dotnet test

# Check code formatting
dotnet format

# Run integration tests
dotnet test tests/PaymentProcessor.TransactionInvoices.IntegrationTests/

# Verify API works
dotnet run --project src/PaymentProcessor.TransactionInvoices.API
# Test via Swagger UI
```

---

## 🎯 Success Checklist

After completing this guide, you should be able to:

- [x] Run the application locally
- [x] Execute all tests successfully
- [x] Access Swagger UI
- [x] Create a transaction invoice via API
- [x] Understand project structure
- [x] Run individual test projects
- [x] Make a simple code change
- [x] Know where to find help

**If any checkbox is unchecked, see [07-TROUBLESHOOTING.md](./07-TROUBLESHOOTING.md)**

---

## 📞 Getting Help

**Stuck?** Check these resources:

1. **Troubleshooting Guide:** [07-TROUBLESHOOTING.md](./07-TROUBLESHOOTING.md)
2. **Architecture Overview:** [02-ARCHITECTURE-OVERVIEW.md](./02-ARCHITECTURE-OVERVIEW.md)
3. **API Reference:** [06-API-REFERENCE.md](./06-API-REFERENCE.md)
4. **Team Chat:** [Your team channel]

**Still stuck?** Ask in team chat with:
- What you were trying to do
- What happened instead
- Error message (if any)
- Steps you've tried

---

**Next Step:** [Architecture Overview →](./02-ARCHITECTURE-OVERVIEW.md)

**Last Updated:** December 12, 2025
