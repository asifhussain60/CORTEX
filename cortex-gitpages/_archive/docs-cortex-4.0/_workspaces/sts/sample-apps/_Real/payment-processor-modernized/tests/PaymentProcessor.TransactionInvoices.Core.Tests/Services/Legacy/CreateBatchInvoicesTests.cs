using FluentAssertions;
using FluentValidation;
using Microsoft.Extensions.Logging;
using Moq;
using PaymentProcessor.TransactionInvoices.Core.Adapters;
using PaymentProcessor.TransactionInvoices.Core.DTOs;
using PaymentProcessor.TransactionInvoices.Core.Entities;
using PaymentProcessor.TransactionInvoices.Core.Repositories;
using PaymentProcessor.TransactionInvoices.Infrastructure.Services;
using Xunit;

namespace PaymentProcessor.TransactionInvoices.Core.Tests.Services.Legacy;

/// <summary>
/// Unit tests for CreateBatchInvoicesAsync (WCF: Updater_CreatePaymentTransactionInvoices migration)
/// </summary>
public class CreateBatchInvoicesTests
{
    private readonly Mock<ITransactionInvoiceRepository> _invoiceRepositoryMock;
    private readonly Mock<ITransactionBatchRepository> _batchRepositoryMock;
    private readonly Mock<IAccountCategoryRepository> _account_categoryRepositoryMock;
    private readonly Mock<ICashInOutRepository> _cashInOutRepositoryMock;
    private readonly Mock<IPaymentPlanAdapter> _paragonAdapterMock;
    private readonly Mock<ILogger<TransactionInvoiceService>> _loggerMock;
    private readonly TransactionInvoiceService _service;

    public CreateBatchInvoicesTests()
    {
        _invoiceRepositoryMock = new Mock<ITransactionInvoiceRepository>();
        _batchRepositoryMock = new Mock<ITransactionBatchRepository>();
        _account_categoryRepositoryMock = new Mock<IAccountCategoryRepository>();
        _cashInOutRepositoryMock = new Mock<ICashInOutRepository>();
        _paragonAdapterMock = new Mock<IPaymentPlanAdapter>();
        _loggerMock = new Mock<ILogger<TransactionInvoiceService>>();

        // Mock validators (permissive for legacy methods)
        var createValidatorMock = new Mock<IValidator<CreateTransactionInvoiceRequest>>();
        var generateValidatorMock = new Mock<IValidator<GenerateTransactionInvoiceRequest>>();
        var batchValidatorMock = new Mock<IValidator<CreateBatchTransactionInvoiceRequest>>();

        _service = new TransactionInvoiceService(
            _invoiceRepositoryMock.Object,
            _batchRepositoryMock.Object,
            _account_categoryRepositoryMock.Object,
            _cashInOutRepositoryMock.Object,
            _paragonAdapterMock.Object,
            createValidatorMock.Object,
            generateValidatorMock.Object,
            batchValidatorMock.Object,
            _loggerMock.Object
        );
    }

    [Fact]
    public async Task CreateBatchInvoicesAsync_WithValidAccountCategorys_ReturnsSuccessResult()
    {
        // Arrange
        var dto = new CreateBatchInvoicesDto
        {
            EmployerId = "EMP123",
            AccountCategoryIds = new List<int> { 1001, 1002, 1003 },
            EffectiveDate = new DateTime(2025, 12, 15),
            Description = "Q4 2025 Transaction"
        };

        // Mock account_categorys
        _account_categoryRepositoryMock.Setup(r => r.GetByIdAsync("1001"))
            .ReturnsAsync(new AccountCategory { AccountCategoryId = "1001", AccountNumber = "ACC1001" });
        _account_categoryRepositoryMock.Setup(r => r.GetByIdAsync("1002"))
            .ReturnsAsync(new AccountCategory { AccountCategoryId = "1002", AccountNumber = "ACC1002" });
        _account_categoryRepositoryMock.Setup(r => r.GetByIdAsync("1003"))
            .ReturnsAsync(new AccountCategory { AccountCategoryId = "1003", AccountNumber = "ACC1003" });

        // Mock no existing invoices (no duplicates)
        _invoiceRepositoryMock.Setup(r => r.GetByAccountCategoryIdAsync(It.IsAny<string>()))
            .ReturnsAsync(new List<TransactionInvoice>());

        // Mock payment plans (balance below peg)
        _paragonAdapterMock.Setup(p => p.GetPaymentPlansAsync(It.IsAny<string>()))
            .ReturnsAsync(new List<PaymentPlan>
            {
                new PaymentPlan { Balance = 500m } // Below 1000 peg → creates invoice
            });

        // Act
        var result = await _service.CreateBatchInvoicesAsync(dto);

        // Assert
        result.Should().NotBeNull();
        result.SuccessCount.Should().Be(3);
        result.FailureCount.Should().Be(0);
        result.TotalInvoices.Should().Be(3);
        result.FailedAccountCategorys.Should().BeEmpty();

        _batchRepositoryMock.Verify(r => r.CreateAsync(It.IsAny<TransactionBatch>()), Times.Once);
        _invoiceRepositoryMock.Verify(r => r.CreateAsync(It.IsAny<TransactionInvoice>()), Times.Exactly(3));
    }

    [Fact]
    public async Task CreateBatchInvoicesAsync_WithPartialSuccess_ReturnsPartialResult()
    {
        // Arrange
        var dto = new CreateBatchInvoicesDto
        {
            EmployerId = "EMP123",
            AccountCategoryIds = new List<int> { 1001, 1002, 9999 }, // 9999 doesn't exist
            EffectiveDate = new DateTime(2025, 12, 15)
        };

        // Mock existing account_categorys
        _account_categoryRepositoryMock.Setup(r => r.GetByIdAsync("1001"))
            .ReturnsAsync(new AccountCategory { AccountCategoryId = "1001", AccountNumber = "ACC1001" });
        _account_categoryRepositoryMock.Setup(r => r.GetByIdAsync("1002"))
            .ReturnsAsync(new AccountCategory { AccountCategoryId = "1002", AccountNumber = "ACC1002" });
        
        // Mock non-existent account_category
        _account_categoryRepositoryMock.Setup(r => r.GetByIdAsync("9999"))
            .ReturnsAsync((AccountCategory?)null);

        _invoiceRepositoryMock.Setup(r => r.GetByAccountCategoryIdAsync(It.IsAny<string>()))
            .ReturnsAsync(new List<TransactionInvoice>());

        _paragonAdapterMock.Setup(p => p.GetPaymentPlansAsync(It.IsAny<string>()))
            .ReturnsAsync(new List<PaymentPlan> { new PaymentPlan { Balance = 500m } });

        // Act
        var result = await _service.CreateBatchInvoicesAsync(dto);

        // Assert
        result.SuccessCount.Should().Be(2);
        result.FailureCount.Should().Be(1);
        result.FailedAccountCategorys.Should().HaveCount(1);
        result.FailedAccountCategorys[0].AccountCategoryId.Should().Be(9999);
        result.FailedAccountCategorys[0].ErrorType.Should().Be("NotFound");
    }

    [Fact]
    public async Task CreateBatchInvoicesAsync_WithDuplicateInvoices_SkipsDuplicates()
    {
        // Arrange
        var effectiveDate = new DateTime(2025, 12, 15);
        var dto = new CreateBatchInvoicesDto
        {
            EmployerId = "EMP123",
            AccountCategoryIds = new List<int> { 1001, 1002 },
            EffectiveDate = effectiveDate
        };

        _account_categoryRepositoryMock.Setup(r => r.GetByIdAsync("1001"))
            .ReturnsAsync(new AccountCategory { AccountCategoryId = "1001", AccountNumber = "ACC1001" });
        _account_categoryRepositoryMock.Setup(r => r.GetByIdAsync("1002"))
            .ReturnsAsync(new AccountCategory { AccountCategoryId = "1002", AccountNumber = "ACC1002" });

        // Mock existing invoice for account_category 1001 on same date (duplicate)
        _invoiceRepositoryMock.Setup(r => r.GetByAccountCategoryIdAsync("1001"))
            .ReturnsAsync(new List<TransactionInvoice>
            {
                new TransactionInvoice { InvoiceDate = effectiveDate, AccountCategoryId = "1001" }
            });

        // Mock no existing invoice for account_category 1002
        _invoiceRepositoryMock.Setup(r => r.GetByAccountCategoryIdAsync("1002"))
            .ReturnsAsync(new List<TransactionInvoice>());

        _paragonAdapterMock.Setup(p => p.GetPaymentPlansAsync(It.IsAny<string>()))
            .ReturnsAsync(new List<PaymentPlan> { new PaymentPlan { Balance = 500m } });

        // Act
        var result = await _service.CreateBatchInvoicesAsync(dto);

        // Assert
        result.SuccessCount.Should().Be(1); // Only 1002 succeeds
        result.FailureCount.Should().Be(1); // 1001 is duplicate
        result.FailedAccountCategorys.Should().HaveCount(1);
        result.FailedAccountCategorys[0].ErrorType.Should().Be("Duplicate");

        _invoiceRepositoryMock.Verify(r => r.CreateAsync(It.IsAny<TransactionInvoice>()), Times.Once);
    }

    [Fact]
    public async Task CreateBatchInvoicesAsync_WithBalanceMeetsPeg_SkipsInvoice()
    {
        // Arrange
        var dto = new CreateBatchInvoicesDto
        {
            EmployerId = "EMP123",
            AccountCategoryIds = new List<int> { 1001 },
            EffectiveDate = new DateTime(2025, 12, 15)
        };

        _account_categoryRepositoryMock.Setup(r => r.GetByIdAsync("1001"))
            .ReturnsAsync(new AccountCategory { AccountCategoryId = "1001", AccountNumber = "ACC1001" });

        _invoiceRepositoryMock.Setup(r => r.GetByAccountCategoryIdAsync(It.IsAny<string>()))
            .ReturnsAsync(new List<TransactionInvoice>());

        // Mock high balance (meets peg requirement)
        _paragonAdapterMock.Setup(p => p.GetPaymentPlansAsync("1001"))
            .ReturnsAsync(new List<PaymentPlan>
            {
                new PaymentPlan { Balance = 1500m } // Above 1000 peg → no invoice needed
            });

        // Act
        var result = await _service.CreateBatchInvoicesAsync(dto);

        // Assert
        result.SuccessCount.Should().Be(0);
        result.FailureCount.Should().Be(1);
        result.FailedAccountCategorys[0].ErrorType.Should().Be("NotNeeded");
        result.FailedAccountCategorys[0].Reason.Should().Contain("Balance meets peg");

        _invoiceRepositoryMock.Verify(r => r.CreateAsync(It.IsAny<TransactionInvoice>()), Times.Never);
    }

    [Fact]
    public async Task CreateBatchInvoicesAsync_WithNoPaymentPlans_ReturnsFailure()
    {
        // Arrange
        var dto = new CreateBatchInvoicesDto
        {
            EmployerId = "EMP123",
            AccountCategoryIds = new List<int> { 1001 },
            EffectiveDate = new DateTime(2025, 12, 15)
        };

        _account_categoryRepositoryMock.Setup(r => r.GetByIdAsync("1001"))
            .ReturnsAsync(new AccountCategory { AccountCategoryId = "1001", AccountNumber = "ACC1001" });

        _invoiceRepositoryMock.Setup(r => r.GetByAccountCategoryIdAsync(It.IsAny<string>()))
            .ReturnsAsync(new List<TransactionInvoice>());

        // Mock no payment plans
        _paragonAdapterMock.Setup(p => p.GetPaymentPlansAsync("1001"))
            .ReturnsAsync(new List<PaymentPlan>());

        // Act
        var result = await _service.CreateBatchInvoicesAsync(dto);

        // Assert
        result.SuccessCount.Should().Be(0);
        result.FailureCount.Should().Be(1);
        result.FailedAccountCategorys[0].ErrorType.Should().Be("MissingData");
        result.FailedAccountCategorys[0].Reason.Should().Contain("No payment plans found");
    }

    [Fact]
    public async Task CreateBatchInvoicesAsync_CalculatesCorrectPegAmount()
    {
        // Arrange
        var dto = new CreateBatchInvoicesDto
        {
            EmployerId = "EMP123",
            AccountCategoryIds = new List<int> { 1001 },
            EffectiveDate = new DateTime(2025, 12, 15)
        };

        _account_categoryRepositoryMock.Setup(r => r.GetByIdAsync("1001"))
            .ReturnsAsync(new AccountCategory { AccountCategoryId = "1001", AccountNumber = "ACC1001" });

        _invoiceRepositoryMock.Setup(r => r.GetByAccountCategoryIdAsync(It.IsAny<string>()))
            .ReturnsAsync(new List<TransactionInvoice>());

        // Balance: 300, Invoice Amount: 1000 → Peg: 700
        _paragonAdapterMock.Setup(p => p.GetPaymentPlansAsync("1001"))
            .ReturnsAsync(new List<PaymentPlan> { new PaymentPlan { Balance = 300m } });

        TransactionInvoice? capturedInvoice = null;
        _invoiceRepositoryMock.Setup(r => r.CreateAsync(It.IsAny<TransactionInvoice>()))
            .Callback<TransactionInvoice>(inv => capturedInvoice = inv)
            .Returns(Task.CompletedTask);

        // Act
        var result = await _service.CreateBatchInvoicesAsync(dto);

        // Assert
        result.SuccessCount.Should().Be(1);
        capturedInvoice.Should().NotBeNull();
        // In implementation, invoice amount logic is mockeed (Balance > 0 → 1000, else 500)
        // Peg = 1000 - 300 = 700
        capturedInvoice!.Amount.Should().Be(700m);
    }

    [Fact]
    public async Task CreateBatchInvoicesAsync_UpdatesBatchTotalAmount()
    {
        // Arrange
        var dto = new CreateBatchInvoicesDto
        {
            EmployerId = "EMP123",
            AccountCategoryIds = new List<int> { 1001, 1002 },
            EffectiveDate = new DateTime(2025, 12, 15)
        };

        _account_categoryRepositoryMock.Setup(r => r.GetByIdAsync("1001"))
            .ReturnsAsync(new AccountCategory { AccountCategoryId = "1001", AccountNumber = "ACC1001" });
        _account_categoryRepositoryMock.Setup(r => r.GetByIdAsync("1002"))
            .ReturnsAsync(new AccountCategory { AccountCategoryId = "1002", AccountNumber = "ACC1002" });

        _invoiceRepositoryMock.Setup(r => r.GetByAccountCategoryIdAsync(It.IsAny<string>()))
            .ReturnsAsync(new List<TransactionInvoice>());

        _paragonAdapterMock.Setup(p => p.GetPaymentPlansAsync(It.IsAny<string>()))
            .ReturnsAsync(new List<PaymentPlan> { new PaymentPlan { Balance = 500m } });

        TransactionBatch? capturedBatch = null;
        _batchRepositoryMock.Setup(r => r.UpdateAsync(It.IsAny<TransactionBatch>()))
            .Callback<TransactionBatch>(b => capturedBatch = b)
            .Returns(Task.CompletedTask);

        // Act
        await _service.CreateBatchInvoicesAsync(dto);

        // Assert
        capturedBatch.Should().NotBeNull();
        // Each invoice: 1000 - 500 = 500, Total: 500 + 500 = 1000
        capturedBatch!.TotalAmount.Should().Be(1000m);
    }

    [Fact]
    public async Task CreateBatchInvoicesAsync_CreatesBatchWithPendingStatus()
    {
        // Arrange
        var dto = new CreateBatchInvoicesDto
        {
            EmployerId = "EMP123",
            AccountCategoryIds = new List<int> { 1001 },
            EffectiveDate = new DateTime(2025, 12, 15)
        };

        _account_categoryRepositoryMock.Setup(r => r.GetByIdAsync("1001"))
            .ReturnsAsync(new AccountCategory { AccountCategoryId = "1001", AccountNumber = "ACC1001" });

        _invoiceRepositoryMock.Setup(r => r.GetByAccountCategoryIdAsync(It.IsAny<string>()))
            .ReturnsAsync(new List<TransactionInvoice>());

        _paragonAdapterMock.Setup(p => p.GetPaymentPlansAsync(It.IsAny<string>()))
            .ReturnsAsync(new List<PaymentPlan> { new PaymentPlan { Balance = 500m } });

        TransactionBatch? capturedBatch = null;
        _batchRepositoryMock.Setup(r => r.CreateAsync(It.IsAny<TransactionBatch>()))
            .Callback<TransactionBatch>(b => capturedBatch = b)
            .Returns(Task.CompletedTask);

        // Act
        await _service.CreateBatchInvoicesAsync(dto);

        // Assert
        capturedBatch.Should().NotBeNull();
        capturedBatch!.Status.Should().Be("Pending");
        capturedBatch.EmployerId.Should().Be("EMP123");
    }

    [Fact]
    public async Task CreateBatchInvoicesAsync_WithEmptyAccountCategoryList_CreatesEmptyBatch()
    {
        // Arrange
        var dto = new CreateBatchInvoicesDto
        {
            EmployerId = "EMP123",
            AccountCategoryIds = new List<int>(), // Empty list
            EffectiveDate = new DateTime(2025, 12, 15)
        };

        // Act
        var result = await _service.CreateBatchInvoicesAsync(dto);

        // Assert
        result.TotalInvoices.Should().Be(0);
        result.SuccessCount.Should().Be(0);
        result.FailureCount.Should().Be(0);

        _batchRepositoryMock.Verify(r => r.CreateAsync(It.IsAny<TransactionBatch>()), Times.Once);
        _invoiceRepositoryMock.Verify(r => r.CreateAsync(It.IsAny<TransactionInvoice>()), Times.Never);
    }
}
