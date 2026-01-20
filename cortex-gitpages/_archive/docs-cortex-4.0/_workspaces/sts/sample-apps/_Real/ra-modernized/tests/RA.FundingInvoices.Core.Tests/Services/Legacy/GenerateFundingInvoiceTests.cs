using FluentAssertions;
using FluentValidation;
using Microsoft.Extensions.Logging;
using Moq;
using RA.FundingInvoices.Core.Adapters;
using RA.FundingInvoices.Core.DTOs;
using RA.FundingInvoices.Core.Entities;
using RA.FundingInvoices.Core.Repositories;
using RA.FundingInvoices.Infrastructure.Services;
using Xunit;

namespace RA.FundingInvoices.Core.Tests.Services.Legacy;

/// <summary>
/// Unit tests for GenerateFundingInvoiceAsync (WCF: XGenerateFundingInvoice migration)
/// </summary>
public class GenerateFundingInvoiceTests
{
    private readonly Mock<IFundingInvoiceRepository> _invoiceRepositoryMock;
    private readonly Mock<IFundingBatchRepository> _batchRepositoryMock;
    private readonly Mock<ISubaccountRepository> _subaccountRepositoryMock;
    private readonly Mock<ICashInOutRepository> _cashInOutRepositoryMock;
    private readonly Mock<IReimbursementPlanAdapter> _paragonAdapterMock;
    private readonly Mock<ILogger<FundingInvoiceService>> _loggerMock;
    private readonly FundingInvoiceService _service;

    public GenerateFundingInvoiceTests()
    {
        _invoiceRepositoryMock = new Mock<IFundingInvoiceRepository>();
        _batchRepositoryMock = new Mock<IFundingBatchRepository>();
        _subaccountRepositoryMock = new Mock<ISubaccountRepository>();
        _cashInOutRepositoryMock = new Mock<ICashInOutRepository>();
        _paragonAdapterMock = new Mock<IReimbursementPlanAdapter>();
        _loggerMock = new Mock<ILogger<FundingInvoiceService>>();

        var createValidatorMock = new Mock<IValidator<CreateFundingInvoiceRequest>>();
        var generateValidatorMock = new Mock<IValidator<GenerateFundingInvoiceRequest>>();
        var batchValidatorMock = new Mock<IValidator<CreateBatchFundingInvoiceRequest>>();

        _service = new FundingInvoiceService(
            _invoiceRepositoryMock.Object,
            _batchRepositoryMock.Object,
            _subaccountRepositoryMock.Object,
            _cashInOutRepositoryMock.Object,
            _paragonAdapterMock.Object,
            createValidatorMock.Object,
            generateValidatorMock.Object,
            batchValidatorMock.Object,
            _loggerMock.Object
        );
    }

    [Fact]
    public async Task GenerateFundingInvoiceAsync_WithBalanceBelowPeg_CreatesInvoice()
    {
        // Arrange
        var dto = new GenerateFundingInvoiceDto
        {
            SubaccountId = 1001,
            InvoiceAmount = 1000m,
            EffectiveDate = new DateTime(2025, 12, 15),
            Description = "Monthly peg invoice"
        };

        _subaccountRepositoryMock.Setup(r => r.GetByIdAsync("1001"))
            .ReturnsAsync(new Subaccount { SubaccountId = "1001", AccountNumber = "ACC1001" });

        // Balance: 300, Invoice: 1000 → Peg: 700
        _paragonAdapterMock.Setup(p => p.GetReimbursementPlansAsync("1001"))
            .ReturnsAsync(new List<ReimbursementPlan> { new ReimbursementPlan { Balance = 300m } });

        // Act
        var result = await _service.GenerateFundingInvoiceAsync(dto);

        // Assert
        result.Should().NotBeNull();
        result.InvoiceCreated.Should().BeTrue();
        result.PegAmount.Should().Be(700m); // 1000 - 300
        result.Reason.Should().Be("Balance below peg amount");
        result.InvoiceId.Should().NotBeNull();

        _invoiceRepositoryMock.Verify(r => r.CreateAsync(It.IsAny<FundingInvoice>()), Times.Once);
    }

    [Fact]
    public async Task GenerateFundingInvoiceAsync_WithBalanceMeetsPeg_DoesNotCreateInvoice()
    {
        // Arrange
        var dto = new GenerateFundingInvoiceDto
        {
            SubaccountId = 1001,
            InvoiceAmount = 1000m,
            EffectiveDate = new DateTime(2025, 12, 15)
        };

        _subaccountRepositoryMock.Setup(r => r.GetByIdAsync("1001"))
            .ReturnsAsync(new Subaccount { SubaccountId = "1001", AccountNumber = "ACC1001" });

        // Balance: 1200, Invoice: 1000 → Peg: -200 (no invoice needed)
        _paragonAdapterMock.Setup(p => p.GetReimbursementPlansAsync("1001"))
            .ReturnsAsync(new List<ReimbursementPlan> { new ReimbursementPlan { Balance = 1200m } });

        // Act
        var result = await _service.GenerateFundingInvoiceAsync(dto);

        // Assert
        result.Should().NotBeNull();
        result.InvoiceCreated.Should().BeFalse();
        result.PegAmount.Should().Be(-200m);
        result.Reason.Should().Be("Balance meets peg requirement");
        result.InvoiceId.Should().BeNull();

        _invoiceRepositoryMock.Verify(r => r.CreateAsync(It.IsAny<FundingInvoice>()), Times.Never);
    }

    [Fact]
    public async Task GenerateFundingInvoiceAsync_WithBalanceEqualsPeg_DoesNotCreateInvoice()
    {
        // Arrange
        var dto = new GenerateFundingInvoiceDto
        {
            SubaccountId = 1001,
            InvoiceAmount = 1000m,
            EffectiveDate = new DateTime(2025, 12, 15)
        };

        _subaccountRepositoryMock.Setup(r => r.GetByIdAsync("1001"))
            .ReturnsAsync(new Subaccount { SubaccountId = "1001", AccountNumber = "ACC1001" });

        // Balance: 1000, Invoice: 1000 → Peg: 0 (no invoice needed)
        _paragonAdapterMock.Setup(p => p.GetReimbursementPlansAsync("1001"))
            .ReturnsAsync(new List<ReimbursementPlan> { new ReimbursementPlan { Balance = 1000m } });

        // Act
        var result = await _service.GenerateFundingInvoiceAsync(dto);

        // Assert
        result.InvoiceCreated.Should().BeFalse();
        result.PegAmount.Should().Be(0m);
        result.Reason.Should().Be("Balance meets peg requirement");
    }

    [Fact]
    public async Task GenerateFundingInvoiceAsync_WithBalanceOneCentBelow_CreatesInvoice()
    {
        // Arrange
        var dto = new GenerateFundingInvoiceDto
        {
            SubaccountId = 1001,
            InvoiceAmount = 1000m,
            EffectiveDate = new DateTime(2025, 12, 15)
        };

        _subaccountRepositoryMock.Setup(r => r.GetByIdAsync("1001"))
            .ReturnsAsync(new Subaccount { SubaccountId = "1001", AccountNumber = "ACC1001" });

        // Balance: 999.99, Invoice: 1000 → Peg: 0.01
        _paragonAdapterMock.Setup(p => p.GetReimbursementPlansAsync("1001"))
            .ReturnsAsync(new List<ReimbursementPlan> { new ReimbursementPlan { Balance = 999.99m } });

        // Act
        var result = await _service.GenerateFundingInvoiceAsync(dto);

        // Assert
        result.InvoiceCreated.Should().BeTrue();
        result.PegAmount.Should().Be(0.01m);

        _invoiceRepositoryMock.Verify(r => r.CreateAsync(It.Is<FundingInvoice>(inv => inv.Amount == 0.01m)), Times.Once);
    }

    [Fact]
    public async Task GenerateFundingInvoiceAsync_WithAutoDebitEnabled_CreatesPaymentRecord()
    {
        // Arrange
        var dto = new GenerateFundingInvoiceDto
        {
            SubaccountId = 1001,
            InvoiceAmount = 1000m,
            EffectiveDate = new DateTime(2025, 12, 15, 0, 0, 0, DateTimeKind.Utc) // Monday
        };

        _subaccountRepositoryMock.Setup(r => r.GetByIdAsync("1001"))
            .ReturnsAsync(new Subaccount { SubaccountId = "1001", AccountNumber = "ACC1001AutoDebit" }); // Mock auto-debit

        _paragonAdapterMock.Setup(p => p.GetReimbursementPlansAsync("1001"))
            .ReturnsAsync(new List<ReimbursementPlan> { new ReimbursementPlan { Balance = 500m } });

        // Act
        var result = await _service.GenerateFundingInvoiceAsync(dto);

        // Assert
        result.InvoiceCreated.Should().BeTrue();

        // Verify payment record created with 2 business days later (Mon → Wed)
        _cashInOutRepositoryMock.Verify(r => r.CreateAsync(It.Is<CashInOut>(
            p => p.TransactionType == "RAFundingPayment" && 
                 p.Amount == 500m &&
                 p.TransactionDate.Date == new DateTime(2025, 12, 17).Date // Wed (Mon + 2 business days)
        )), Times.Once);
    }

    [Fact]
    public async Task GenerateFundingInvoiceAsync_WithAutoDebitDisabled_DoesNotCreatePayment()
    {
        // Arrange
        var dto = new GenerateFundingInvoiceDto
        {
            SubaccountId = 1001,
            InvoiceAmount = 1000m,
            EffectiveDate = new DateTime(2025, 12, 15)
        };

        _subaccountRepositoryMock.Setup(r => r.GetByIdAsync("1001"))
            .ReturnsAsync(new Subaccount { SubaccountId = "1001", AccountNumber = "ACC1001" }); // No auto-debit

        _paragonAdapterMock.Setup(p => p.GetReimbursementPlansAsync("1001"))
            .ReturnsAsync(new List<ReimbursementPlan> { new ReimbursementPlan { Balance = 500m } });

        // Act
        var result = await _service.GenerateFundingInvoiceAsync(dto);

        // Assert
        result.InvoiceCreated.Should().BeTrue();

        // Verify no payment record created
        _cashInOutRepositoryMock.Verify(r => r.CreateAsync(It.IsAny<CashInOut>()), Times.Never);
    }

    [Fact]
    public async Task GenerateFundingInvoiceAsync_WithAutoDebit_SetsInvoiceStatusPending()
    {
        // Arrange
        var dto = new GenerateFundingInvoiceDto
        {
            SubaccountId = 1001,
            InvoiceAmount = 1000m,
            EffectiveDate = new DateTime(2025, 12, 15)
        };

        _subaccountRepositoryMock.Setup(r => r.GetByIdAsync("1001"))
            .ReturnsAsync(new Subaccount { SubaccountId = "1001", AccountNumber = "ACC1001AutoDebit" });

        _paragonAdapterMock.Setup(p => p.GetReimbursementPlansAsync("1001"))
            .ReturnsAsync(new List<ReimbursementPlan> { new ReimbursementPlan { Balance = 500m } });

        FundingInvoice? capturedInvoice = null;
        _invoiceRepositoryMock.Setup(r => r.CreateAsync(It.IsAny<FundingInvoice>()))
            .Callback<FundingInvoice>(inv => capturedInvoice = inv)
            .Returns(Task.CompletedTask);

        // Act
        await _service.GenerateFundingInvoiceAsync(dto);

        // Assert
        capturedInvoice.Should().NotBeNull();
        capturedInvoice!.Status.Should().Be("Pending"); // Auto-debit → Pending
    }

    [Fact]
    public async Task GenerateFundingInvoiceAsync_WithoutAutoDebit_SetsInvoiceStatusOpen()
    {
        // Arrange
        var dto = new GenerateFundingInvoiceDto
        {
            SubaccountId = 1001,
            InvoiceAmount = 1000m,
            EffectiveDate = new DateTime(2025, 12, 15)
        };

        _subaccountRepositoryMock.Setup(r => r.GetByIdAsync("1001"))
            .ReturnsAsync(new Subaccount { SubaccountId = "1001", AccountNumber = "ACC1001" });

        _paragonAdapterMock.Setup(p => p.GetReimbursementPlansAsync("1001"))
            .ReturnsAsync(new List<ReimbursementPlan> { new ReimbursementPlan { Balance = 500m } });

        FundingInvoice? capturedInvoice = null;
        _invoiceRepositoryMock.Setup(r => r.CreateAsync(It.IsAny<FundingInvoice>()))
            .Callback<FundingInvoice>(inv => capturedInvoice = inv)
            .Returns(Task.CompletedTask);

        // Act
        await _service.GenerateFundingInvoiceAsync(dto);

        // Assert
        capturedInvoice.Should().NotBeNull();
        capturedInvoice!.Status.Should().Be("Open"); // No auto-debit → Open
    }

    [Fact]
    public async Task GenerateFundingInvoiceAsync_WithNonExistentSubaccount_ThrowsException()
    {
        // Arrange
        var dto = new GenerateFundingInvoiceDto
        {
            SubaccountId = 9999,
            InvoiceAmount = 1000m,
            EffectiveDate = new DateTime(2025, 12, 15)
        };

        _subaccountRepositoryMock.Setup(r => r.GetByIdAsync("9999"))
            .ReturnsAsync((Subaccount?)null);

        // Act & Assert
        var exception = await Assert.ThrowsAsync<InvalidOperationException>(
            () => _service.GenerateFundingInvoiceAsync(dto));

        exception.Message.Should().Contain("Subaccount not found: 9999");

        _invoiceRepositoryMock.Verify(r => r.CreateAsync(It.IsAny<FundingInvoice>()), Times.Never);
    }

    [Fact]
    public async Task GenerateFundingInvoiceAsync_WithNoReimbursementPlans_ReturnsNotNeeded()
    {
        // Arrange
        var dto = new GenerateFundingInvoiceDto
        {
            SubaccountId = 1001,
            InvoiceAmount = 1000m,
            EffectiveDate = new DateTime(2025, 12, 15)
        };

        _subaccountRepositoryMock.Setup(r => r.GetByIdAsync("1001"))
            .ReturnsAsync(new Subaccount { SubaccountId = "1001", AccountNumber = "ACC1001" });

        _paragonAdapterMock.Setup(p => p.GetReimbursementPlansAsync("1001"))
            .ReturnsAsync(new List<ReimbursementPlan>()); // Empty list

        // Act
        var result = await _service.GenerateFundingInvoiceAsync(dto);

        // Assert
        result.InvoiceCreated.Should().BeFalse();
        result.Reason.Should().Be("No reimbursement plans found");
        result.PegAmount.Should().Be(0m);

        _invoiceRepositoryMock.Verify(r => r.CreateAsync(It.IsAny<FundingInvoice>()), Times.Never);
    }
}
