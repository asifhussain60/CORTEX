using FluentAssertions;
using FluentValidation;
using FluentValidation.Results;
using Microsoft.Extensions.Logging;
using Moq;
using PaymentProcessor.TransactionInvoices.Core.Adapters;
using PaymentProcessor.TransactionInvoices.Core.DTOs;
using PaymentProcessor.TransactionInvoices.Core.Entities;
using PaymentProcessor.TransactionInvoices.Core.Repositories;
using PaymentProcessor.TransactionInvoices.Infrastructure.Services;
using Xunit;

namespace PaymentProcessor.TransactionInvoices.UnitTests.Services;

public class TransactionInvoiceServiceTests
{
    private readonly Mock<ITransactionInvoiceRepository> _mockInvoiceRepo;
    private readonly Mock<ITransactionBatchRepository> _mockBatchRepo;
    private readonly Mock<IAccountCategoryRepository> _mockAccountCategoryRepo;
    private readonly Mock<ICashInOutRepository> _mockCashInOutRepo;
    private readonly Mock<IPaymentPlanAdapter> _mockParagonAdapter;
    private readonly Mock<IValidator<CreateTransactionInvoiceRequest>> _mockCreateValidator;
    private readonly Mock<IValidator<GenerateTransactionInvoiceRequest>> _mockGenerateValidator;
    private readonly Mock<IValidator<CreateBatchTransactionInvoiceRequest>> _mockBatchValidator;
    private readonly Mock<ILogger<TransactionInvoiceService>> _mockLogger;
    private readonly TransactionInvoiceService _service;

    public TransactionInvoiceServiceTests()
    {
        _mockInvoiceRepo = new Mock<ITransactionInvoiceRepository>();
        _mockBatchRepo = new Mock<ITransactionBatchRepository>();
        _mockAccountCategoryRepo = new Mock<IAccountCategoryRepository>();
        _mockCashInOutRepo = new Mock<ICashInOutRepository>();
        _mockParagonAdapter = new Mock<IPaymentPlanAdapter>();
        _mockCreateValidator = new Mock<IValidator<CreateTransactionInvoiceRequest>>();
        _mockGenerateValidator = new Mock<IValidator<GenerateTransactionInvoiceRequest>>();
        _mockBatchValidator = new Mock<IValidator<CreateBatchTransactionInvoiceRequest>>();
        _mockLogger = new Mock<ILogger<TransactionInvoiceService>>();

        _service = new TransactionInvoiceService(
            _mockInvoiceRepo.Object,
            _mockBatchRepo.Object,
            _mockAccountCategoryRepo.Object,
            _mockCashInOutRepo.Object,
            _mockParagonAdapter.Object,
            _mockCreateValidator.Object,
            _mockGenerateValidator.Object,
            _mockBatchValidator.Object,
            _mockLogger.Object
        );
    }

    [Fact]
    public async Task CreateAsync_WithValidRequest_CreatesInvoiceAndCashInOut()
    {
        // Arrange
        var request = new CreateTransactionInvoiceRequest
        {
            EmployerId = "EMP-001",
            AccountCategoryId = "SA-001",
            PaymentPlanId = "RP-001",
            EmployerTransactionDefault = 500m,
            EmployeeTransactionDefault = 250m,
            EffectiveDate = DateTime.Today,
            InvoiceDescription = "Test invoice",
            CreatedBy = "TestUser"
        };

        _mockCreateValidator.Setup(v => v.ValidateAsync(request, default))
            .ReturnsAsync(new ValidationResult());

        _mockAccountCategoryRepo.Setup(r => r.GetByIdAsync(request.AccountCategoryId))
            .ReturnsAsync(new AccountCategory { AccountCategoryId = request.AccountCategoryId, Balance = 1000m });

        _mockCashInOutRepo.Setup(r => r.CreateAsync(It.IsAny<CashInOut>()))
            .Returns(Task.CompletedTask);

        _mockInvoiceRepo.Setup(r => r.CreateAsync(It.IsAny<TransactionInvoice>()))
            .Returns(Task.CompletedTask);

        // Act
        var result = await _service.CreateAsync(request);

        // Assert
        result.Should().NotBeNull();
        result.Amount.Should().Be(750m); // 500 + 250
        result.AccountCategoryId.Should().Be(request.AccountCategoryId);
        result.Status.Should().Be("Pending");
        result.CreatedBy.Should().Be("TestUser");

        _mockCashInOutRepo.Verify(r => r.CreateAsync(It.Is<CashInOut>(c => c.Amount == 750m)), Times.Once);
        _mockInvoiceRepo.Verify(r => r.CreateAsync(It.Is<TransactionInvoice>(i => i.Amount == 750m)), Times.Once);
    }

    [Fact]
    public async Task CreateAsync_WithInvalidRequest_ThrowsValidationException()
    {
        // Arrange
        var request = new CreateTransactionInvoiceRequest
        {
            EmployerId = "",  // Invalid - empty
            AccountCategoryId = "SA-001"
        };

        var validationFailures = new List<ValidationFailure>
        {
            new ValidationFailure("EmployerId", "Employer ID is required")
        };

        _mockCreateValidator.Setup(v => v.ValidateAsync(request, default))
            .ReturnsAsync(new ValidationResult(validationFailures));

        // Act & Assert
        await Assert.ThrowsAsync<ValidationException>(() => _service.CreateAsync(request));
    }

    [Fact]
    public async Task CreateAsync_WhenAccountCategoryNotFound_ThrowsInvalidOperationException()
    {
        // Arrange
        var request = new CreateTransactionInvoiceRequest
        {
            EmployerId = "EMP-001",
            AccountCategoryId = "SA-NONEXISTENT",
            EmployerTransactionDefault = 100m,
            InvoiceDescription = "Test",
            CreatedBy = "TestUser"
        };

        _mockCreateValidator.Setup(v => v.ValidateAsync(request, default))
            .ReturnsAsync(new ValidationResult());

        _mockAccountCategoryRepo.Setup(r => r.GetByIdAsync(request.AccountCategoryId))
            .ReturnsAsync((AccountCategory?)null);

        // Act & Assert
        await Assert.ThrowsAsync<InvalidOperationException>(() => _service.CreateAsync(request));
    }

    [Fact]
    public async Task GenerateAsync_WhenPegAmountNotMet_ReturnsInvoiceNotNeeded()
    {
        // Arrange
        var request = new GenerateTransactionInvoiceRequest
        {
            AccountCategoryId = "SA-001",
            InvoiceAmount = 500m,
            InvoiceDate = DateTime.Today,
            CreatedBy = "TestUser"
        };

        _mockGenerateValidator.Setup(v => v.ValidateAsync(request, default))
            .ReturnsAsync(new ValidationResult());

        _mockAccountCategoryRepo.Setup(r => r.GetByIdAsync(request.AccountCategoryId))
            .ReturnsAsync(new AccountCategory { AccountCategoryId = request.AccountCategoryId, Balance = 5000m }); // High balance

        _mockParagonAdapter.Setup(a => a.GetPaymentPlansAsync(request.AccountCategoryId))
            .ReturnsAsync(new List<PaymentPlan>
            {
                new PaymentPlan { PaymentPlanId = "RP-001", PlanShortDescription = "Test Plan" }
            });

        // Act
        var result = await _service.GenerateAsync(request);

        // Assert
        result.Result.Should().Be("invoice not needed");
        result.Invoice.Should().BeNull();
        result.CashInOutId.Should().BeNull();
    }

    [Fact]
    public async Task GenerateAsync_WhenPegAmountMet_CreatesInvoice()
    {
        // Arrange
        var request = new GenerateTransactionInvoiceRequest
        {
            AccountCategoryId = "SA-001",
            InvoiceAmount = 500m,
            InvoiceDate = DateTime.Today,
            CreatedBy = "TestUser"
        };

        _mockGenerateValidator.Setup(v => v.ValidateAsync(request, default))
            .ReturnsAsync(new ValidationResult());

        _mockAccountCategoryRepo.Setup(r => r.GetByIdAsync(request.AccountCategoryId))
            .ReturnsAsync(new AccountCategory { AccountCategoryId = request.AccountCategoryId, Balance = 100m }); // Low balance triggers invoice

        _mockParagonAdapter.Setup(a => a.GetPaymentPlansAsync(request.AccountCategoryId))
            .ReturnsAsync(new List<PaymentPlan>
            {
                new PaymentPlan { PaymentPlanId = "RP-001", PlanShortDescription = "Test Plan", EmployerId = "EMP-001" }
            });

        _mockParagonAdapter.Setup(a => a.GetPaymentAuthorizationsAsync(It.IsAny<string>(), It.IsAny<string>(), It.IsAny<List<string>>()))
            .ReturnsAsync(new List<PaymentAuthorization>());

        _mockCashInOutRepo.Setup(r => r.CreateAsync(It.IsAny<CashInOut>()))
            .Returns(Task.CompletedTask);

        _mockInvoiceRepo.Setup(r => r.CreateAsync(It.IsAny<TransactionInvoice>()))
            .Returns(Task.CompletedTask);

        // Act
        var result = await _service.GenerateAsync(request);

        // Assert
        result.Result.Should().Be("invoice created");
        result.Invoice.Should().NotBeNull();
        result.Invoice!.Amount.Should().Be(500m);
        result.CashInOutId.Should().NotBeNullOrEmpty();
    }

    [Fact]
    public async Task GenerateAsync_WithAutoDebit_CreatesPayment()
    {
        // Arrange
        var request = new GenerateTransactionInvoiceRequest
        {
            AccountCategoryId = "SA-001",
            InvoiceAmount = 500m,
            InvoiceDate = DateTime.Today,
            CreatedBy = "TestUser"
        };

        _mockGenerateValidator.Setup(v => v.ValidateAsync(request, default))
            .ReturnsAsync(new ValidationResult());

        _mockAccountCategoryRepo.Setup(r => r.GetByIdAsync(request.AccountCategoryId))
            .ReturnsAsync(new AccountCategory { AccountCategoryId = request.AccountCategoryId, Balance = 100m });

        _mockParagonAdapter.Setup(a => a.GetPaymentPlansAsync(request.AccountCategoryId))
            .ReturnsAsync(new List<PaymentPlan>
            {
                new PaymentPlan { PaymentPlanId = "RP-001", PlanShortDescription = "Test Plan", EmployerId = "EMP-001" }
            });

        _mockParagonAdapter.Setup(a => a.GetPaymentAuthorizationsAsync(It.IsAny<string>(), It.IsAny<string>(), It.IsAny<List<string>>()))
            .ReturnsAsync(new List<PaymentAuthorization>
            {
                new PaymentAuthorization { PaymentAuthorizationId = "PA-001", IsAutoDebit = true }
            });

        _mockCashInOutRepo.Setup(r => r.CreateAsync(It.IsAny<CashInOut>()))
            .Returns(Task.CompletedTask);

        _mockInvoiceRepo.Setup(r => r.CreateAsync(It.IsAny<TransactionInvoice>()))
            .Returns(Task.CompletedTask);

        // Act
        var result = await _service.GenerateAsync(request);

        // Assert
        result.Result.Should().Be("invoice created");
        result.PaymentId.Should().NotBeNullOrEmpty();
    }

    [Fact]
    public async Task GetByIdAsync_WhenInvoiceExists_ReturnsInvoice()
    {
        // Arrange
        var invoiceId = "INV-001";
        var invoice = new TransactionInvoice
        {
            InvoiceId = invoiceId,
            Amount = 500m,
            Status = "Pending"
        };

        _mockInvoiceRepo.Setup(r => r.GetByIdAsync(invoiceId))
            .ReturnsAsync(invoice);

        // Act
        var result = await _service.GetByIdAsync(invoiceId);

        // Assert
        result.Should().NotBeNull();
        result!.InvoiceId.Should().Be(invoiceId);
        result.Amount.Should().Be(500m);
    }

    [Fact]
    public async Task GetByIdAsync_WhenInvoiceNotFound_ReturnsNull()
    {
        // Arrange
        _mockInvoiceRepo.Setup(r => r.GetByIdAsync(It.IsAny<string>()))
            .ReturnsAsync((TransactionInvoice?)null);

        // Act
        var result = await _service.GetByIdAsync("NONEXISTENT");

        // Assert
        result.Should().BeNull();
    }

    [Fact]
    public async Task GetByBatchIdAsync_ReturnsAllInvoicesInBatch()
    {
        // Arrange
        var batchId = "BATCH-001";
        var invoices = new List<TransactionInvoice>
        {
            new TransactionInvoice { InvoiceId = "INV-001", BatchId = batchId, Amount = 100m },
            new TransactionInvoice { InvoiceId = "INV-002", BatchId = batchId, Amount = 200m }
        };

        _mockInvoiceRepo.Setup(r => r.GetByBatchIdAsync(batchId))
            .ReturnsAsync(invoices);

        // Act
        var result = await _service.GetByBatchIdAsync(batchId);

        // Assert
        result.Should().HaveCount(2);
        result.Sum(r => r.Amount).Should().Be(300m);
    }

    [Fact]
    public async Task GetByAccountCategoryIdAsync_ReturnsAllInvoicesForAccountCategory()
    {
        // Arrange
        var account_categoryId = "SA-001";
        var invoices = new List<TransactionInvoice>
        {
            new TransactionInvoice { InvoiceId = "INV-001", AccountCategoryId = account_categoryId, Amount = 500m },
            new TransactionInvoice { InvoiceId = "INV-002", AccountCategoryId = account_categoryId, Amount = 750m }
        };

        _mockInvoiceRepo.Setup(r => r.GetByAccountCategoryIdAsync(account_categoryId))
            .ReturnsAsync(invoices);

        // Act
        var result = await _service.GetByAccountCategoryIdAsync(account_categoryId);

        // Assert
        result.Should().HaveCount(2);
        result.Sum(r => r.Amount).Should().Be(1250m);
    }
}
