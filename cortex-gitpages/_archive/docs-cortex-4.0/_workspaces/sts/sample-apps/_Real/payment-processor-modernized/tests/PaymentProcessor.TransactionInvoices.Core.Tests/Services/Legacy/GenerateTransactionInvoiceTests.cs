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
/// Unit tests for GenerateTransactionInvoiceAsync (WCF: XGenerateTransactionInvoice migration)
/// </summary>
public class GenerateTransactionInvoiceTests
{
    private readonly Mock<ITransactionInvoiceRepository> _invoiceRepositoryMock;
    private readonly Mock<ITransactionBatchRepository> _batchRepositoryMock;
    private readonly Mock<IAccountCategoryRepository> _account_categoryRepositoryMock;
    private readonly Mock<ICashInOutRepository> _cashInOutRepositoryMock;
    private readonly Mock<IPaymentPlanAdapter> _paragonAdapterMock;
    private readonly Mock<ILogger<TransactionInvoiceService>> _loggerMock;
    private readonly TransactionInvoiceService _service;

    public GenerateTransactionInvoiceTests()
    {
        _invoiceRepositoryMock = new Mock<ITransactionInvoiceRepository>();
        _batchRepositoryMock = new Mock<ITransactionBatchRepository>();
        _account_categoryRepositoryMock = new Mock<IAccountCategoryRepository>();
        _cashInOutRepositoryMock = new Mock<ICashInOutRepository>();
        _paragonAdapterMock = new Mock<IPaymentPlanAdapter>();
        _loggerMock = new Mock<ILogger<TransactionInvoiceService>>();

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
    public async Task GenerateTransactionInvoiceAsync_WithBalanceBelowPeg_CreatesInvoice()
    {
        // Arrange
        var dto = new GenerateTransactionInvoiceDto
        {
            AccountCategoryId = 1001,
            InvoiceAmount = 1000m,
            EffectiveDate = new DateTime(2025, 12, 15),
            Description = "Monthly peg invoice"
        };

        _account_categoryRepositoryMock.Setup(r => r.GetByIdAsync("1001"))
            .ReturnsAsync(new AccountCategory { AccountCategoryId = "1001", AccountNumber = "ACC1001" });

        // Balance: 300, Invoice: 1000 → Peg: 700
        _paragonAdapterMock.Setup(p => p.GetPaymentPlansAsync("1001"))
            .ReturnsAsync(new List<PaymentPlan> { new PaymentPlan { Balance = 300m } });

        // Act
        var result = await _service.GenerateTransactionInvoiceAsync(dto);

        // Assert
        result.Should().NotBeNull();
        result.InvoiceCreated.Should().BeTrue();
        result.PegAmount.Should().Be(700m); // 1000 - 300
        result.Reason.Should().Be("Balance below peg amount");
        result.InvoiceId.Should().NotBeNull();

        _invoiceRepositoryMock.Verify(r => r.CreateAsync(It.IsAny<TransactionInvoice>()), Times.Once);
    }

    [Fact]
    public async Task GenerateTransactionInvoiceAsync_WithBalanceMeetsPeg_DoesNotCreateInvoice()
    {
        // Arrange
        var dto = new GenerateTransactionInvoiceDto
        {
            AccountCategoryId = 1001,
            InvoiceAmount = 1000m,
            EffectiveDate = new DateTime(2025, 12, 15)
        };

        _account_categoryRepositoryMock.Setup(r => r.GetByIdAsync("1001"))
            .ReturnsAsync(new AccountCategory { AccountCategoryId = "1001", AccountNumber = "ACC1001" });

        // Balance: 1200, Invoice: 1000 → Peg: -200 (no invoice needed)
        _paragonAdapterMock.Setup(p => p.GetPaymentPlansAsync("1001"))
            .ReturnsAsync(new List<PaymentPlan> { new PaymentPlan { Balance = 1200m } });

        // Act
        var result = await _service.GenerateTransactionInvoiceAsync(dto);

        // Assert
        result.Should().NotBeNull();
        result.InvoiceCreated.Should().BeFalse();
        result.PegAmount.Should().Be(-200m);
        result.Reason.Should().Be("Balance meets peg requirement");
        result.InvoiceId.Should().BeNull();

        _invoiceRepositoryMock.Verify(r => r.CreateAsync(It.IsAny<TransactionInvoice>()), Times.Never);
    }

    [Fact]
    public async Task GenerateTransactionInvoiceAsync_WithBalanceEqualsPeg_DoesNotCreateInvoice()
    {
        // Arrange
        var dto = new GenerateTransactionInvoiceDto
        {
            AccountCategoryId = 1001,
            InvoiceAmount = 1000m,
            EffectiveDate = new DateTime(2025, 12, 15)
        };

        _account_categoryRepositoryMock.Setup(r => r.GetByIdAsync("1001"))
            .ReturnsAsync(new AccountCategory { AccountCategoryId = "1001", AccountNumber = "ACC1001" });

        // Balance: 1000, Invoice: 1000 → Peg: 0 (no invoice needed)
        _paragonAdapterMock.Setup(p => p.GetPaymentPlansAsync("1001"))
            .ReturnsAsync(new List<PaymentPlan> { new PaymentPlan { Balance = 1000m } });

        // Act
        var result = await _service.GenerateTransactionInvoiceAsync(dto);

        // Assert
        result.InvoiceCreated.Should().BeFalse();
        result.PegAmount.Should().Be(0m);
        result.Reason.Should().Be("Balance meets peg requirement");
    }

    [Fact]
    public async Task GenerateTransactionInvoiceAsync_WithBalanceOneCentBelow_CreatesInvoice()
    {
        // Arrange
        var dto = new GenerateTransactionInvoiceDto
        {
            AccountCategoryId = 1001,
            InvoiceAmount = 1000m,
            EffectiveDate = new DateTime(2025, 12, 15)
        };

        _account_categoryRepositoryMock.Setup(r => r.GetByIdAsync("1001"))
            .ReturnsAsync(new AccountCategory { AccountCategoryId = "1001", AccountNumber = "ACC1001" });

        // Balance: 999.99, Invoice: 1000 → Peg: 0.01
        _paragonAdapterMock.Setup(p => p.GetPaymentPlansAsync("1001"))
            .ReturnsAsync(new List<PaymentPlan> { new PaymentPlan { Balance = 999.99m } });

        // Act
        var result = await _service.GenerateTransactionInvoiceAsync(dto);

        // Assert
        result.InvoiceCreated.Should().BeTrue();
        result.PegAmount.Should().Be(0.01m);

        _invoiceRepositoryMock.Verify(r => r.CreateAsync(It.Is<TransactionInvoice>(inv => inv.Amount == 0.01m)), Times.Once);
    }

    [Fact]
    public async Task GenerateTransactionInvoiceAsync_WithAutoDebitEnabled_CreatesPaymentRecord()
    {
        // Arrange
        var dto = new GenerateTransactionInvoiceDto
        {
            AccountCategoryId = 1001,
            InvoiceAmount = 1000m,
            EffectiveDate = new DateTime(2025, 12, 15, 0, 0, 0, DateTimeKind.Utc) // Monday
        };

        _account_categoryRepositoryMock.Setup(r => r.GetByIdAsync("1001"))
            .ReturnsAsync(new AccountCategory { AccountCategoryId = "1001", AccountNumber = "ACC1001AutoDebit" }); // Mock auto-debit

        _paragonAdapterMock.Setup(p => p.GetPaymentPlansAsync("1001"))
            .ReturnsAsync(new List<PaymentPlan> { new PaymentPlan { Balance = 500m } });

        // Act
        var result = await _service.GenerateTransactionInvoiceAsync(dto);

        // Assert
        result.InvoiceCreated.Should().BeTrue();

        // Verify payment record created with 2 business days later (Mon → Wed)
        _cashInOutRepositoryMock.Verify(r => r.CreateAsync(It.Is<CashInOut>(
            p => p.TransactionType == "PaymentProcessorTransactionPayment" && 
                 p.Amount == 500m &&
                 p.TransactionDate.Date == new DateTime(2025, 12, 17).Date // Wed (Mon + 2 business days)
        )), Times.Once);
    }

    [Fact]
    public async Task GenerateTransactionInvoiceAsync_WithAutoDebitDisabled_DoesNotCreatePayment()
    {
        // Arrange
        var dto = new GenerateTransactionInvoiceDto
        {
            AccountCategoryId = 1001,
            InvoiceAmount = 1000m,
            EffectiveDate = new DateTime(2025, 12, 15)
        };

        _account_categoryRepositoryMock.Setup(r => r.GetByIdAsync("1001"))
            .ReturnsAsync(new AccountCategory { AccountCategoryId = "1001", AccountNumber = "ACC1001" }); // No auto-debit

        _paragonAdapterMock.Setup(p => p.GetPaymentPlansAsync("1001"))
            .ReturnsAsync(new List<PaymentPlan> { new PaymentPlan { Balance = 500m } });

        // Act
        var result = await _service.GenerateTransactionInvoiceAsync(dto);

        // Assert
        result.InvoiceCreated.Should().BeTrue();

        // Verify no payment record created
        _cashInOutRepositoryMock.Verify(r => r.CreateAsync(It.IsAny<CashInOut>()), Times.Never);
    }

    [Fact]
    public async Task GenerateTransactionInvoiceAsync_WithAutoDebit_SetsInvoiceStatusPending()
    {
        // Arrange
        var dto = new GenerateTransactionInvoiceDto
        {
            AccountCategoryId = 1001,
            InvoiceAmount = 1000m,
            EffectiveDate = new DateTime(2025, 12, 15)
        };

        _account_categoryRepositoryMock.Setup(r => r.GetByIdAsync("1001"))
            .ReturnsAsync(new AccountCategory { AccountCategoryId = "1001", AccountNumber = "ACC1001AutoDebit" });

        _paragonAdapterMock.Setup(p => p.GetPaymentPlansAsync("1001"))
            .ReturnsAsync(new List<PaymentPlan> { new PaymentPlan { Balance = 500m } });

        TransactionInvoice? capturedInvoice = null;
        _invoiceRepositoryMock.Setup(r => r.CreateAsync(It.IsAny<TransactionInvoice>()))
            .Callback<TransactionInvoice>(inv => capturedInvoice = inv)
            .Returns(Task.CompletedTask);

        // Act
        await _service.GenerateTransactionInvoiceAsync(dto);

        // Assert
        capturedInvoice.Should().NotBeNull();
        capturedInvoice!.Status.Should().Be("Pending"); // Auto-debit → Pending
    }

    [Fact]
    public async Task GenerateTransactionInvoiceAsync_WithoutAutoDebit_SetsInvoiceStatusOpen()
    {
        // Arrange
        var dto = new GenerateTransactionInvoiceDto
        {
            AccountCategoryId = 1001,
            InvoiceAmount = 1000m,
            EffectiveDate = new DateTime(2025, 12, 15)
        };

        _account_categoryRepositoryMock.Setup(r => r.GetByIdAsync("1001"))
            .ReturnsAsync(new AccountCategory { AccountCategoryId = "1001", AccountNumber = "ACC1001" });

        _paragonAdapterMock.Setup(p => p.GetPaymentPlansAsync("1001"))
            .ReturnsAsync(new List<PaymentPlan> { new PaymentPlan { Balance = 500m } });

        TransactionInvoice? capturedInvoice = null;
        _invoiceRepositoryMock.Setup(r => r.CreateAsync(It.IsAny<TransactionInvoice>()))
            .Callback<TransactionInvoice>(inv => capturedInvoice = inv)
            .Returns(Task.CompletedTask);

        // Act
        await _service.GenerateTransactionInvoiceAsync(dto);

        // Assert
        capturedInvoice.Should().NotBeNull();
        capturedInvoice!.Status.Should().Be("Open"); // No auto-debit → Open
    }

    [Fact]
    public async Task GenerateTransactionInvoiceAsync_WithNonExistentAccountCategory_ThrowsException()
    {
        // Arrange
        var dto = new GenerateTransactionInvoiceDto
        {
            AccountCategoryId = 9999,
            InvoiceAmount = 1000m,
            EffectiveDate = new DateTime(2025, 12, 15)
        };

        _account_categoryRepositoryMock.Setup(r => r.GetByIdAsync("9999"))
            .ReturnsAsync((AccountCategory?)null);

        // Act & Assert
        var exception = await Assert.ThrowsAsync<InvalidOperationException>(
            () => _service.GenerateTransactionInvoiceAsync(dto));

        exception.Message.Should().Contain("AccountCategory not found: 9999");

        _invoiceRepositoryMock.Verify(r => r.CreateAsync(It.IsAny<TransactionInvoice>()), Times.Never);
    }

    [Fact]
    public async Task GenerateTransactionInvoiceAsync_WithNoPaymentPlans_ReturnsNotNeeded()
    {
        // Arrange
        var dto = new GenerateTransactionInvoiceDto
        {
            AccountCategoryId = 1001,
            InvoiceAmount = 1000m,
            EffectiveDate = new DateTime(2025, 12, 15)
        };

        _account_categoryRepositoryMock.Setup(r => r.GetByIdAsync("1001"))
            .ReturnsAsync(new AccountCategory { AccountCategoryId = "1001", AccountNumber = "ACC1001" });

        _paragonAdapterMock.Setup(p => p.GetPaymentPlansAsync("1001"))
            .ReturnsAsync(new List<PaymentPlan>()); // Empty list

        // Act
        var result = await _service.GenerateTransactionInvoiceAsync(dto);

        // Assert
        result.InvoiceCreated.Should().BeFalse();
        result.Reason.Should().Be("No payment plans found");
        result.PegAmount.Should().Be(0m);

        _invoiceRepositoryMock.Verify(r => r.CreateAsync(It.IsAny<TransactionInvoice>()), Times.Never);
    }
}
