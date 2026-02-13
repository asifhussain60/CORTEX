using FluentAssertions;
using FluentValidation;
using FluentValidation.Results;
using Microsoft.Extensions.Logging;
using Moq;
using RA.FundingInvoices.Core.Adapters;
using RA.FundingInvoices.Core.DTOs;
using RA.FundingInvoices.Core.Entities;
using RA.FundingInvoices.Core.Repositories;
using RA.FundingInvoices.Infrastructure.Services;
using Xunit;

namespace RA.FundingInvoices.UnitTests.Services;

public class FundingInvoiceServiceTests
{
    private readonly Mock<IFundingInvoiceRepository> _mockInvoiceRepo;
    private readonly Mock<IFundingBatchRepository> _mockBatchRepo;
    private readonly Mock<ISubaccountRepository> _mockSubaccountRepo;
    private readonly Mock<ICashInOutRepository> _mockCashInOutRepo;
    private readonly Mock<IReimbursementPlanAdapter> _mockParagonAdapter;
    private readonly Mock<IValidator<CreateFundingInvoiceRequest>> _mockCreateValidator;
    private readonly Mock<IValidator<GenerateFundingInvoiceRequest>> _mockGenerateValidator;
    private readonly Mock<IValidator<CreateBatchFundingInvoiceRequest>> _mockBatchValidator;
    private readonly Mock<ILogger<FundingInvoiceService>> _mockLogger;
    private readonly FundingInvoiceService _service;

    public FundingInvoiceServiceTests()
    {
        _mockInvoiceRepo = new Mock<IFundingInvoiceRepository>();
        _mockBatchRepo = new Mock<IFundingBatchRepository>();
        _mockSubaccountRepo = new Mock<ISubaccountRepository>();
        _mockCashInOutRepo = new Mock<ICashInOutRepository>();
        _mockParagonAdapter = new Mock<IReimbursementPlanAdapter>();
        _mockCreateValidator = new Mock<IValidator<CreateFundingInvoiceRequest>>();
        _mockGenerateValidator = new Mock<IValidator<GenerateFundingInvoiceRequest>>();
        _mockBatchValidator = new Mock<IValidator<CreateBatchFundingInvoiceRequest>>();
        _mockLogger = new Mock<ILogger<FundingInvoiceService>>();

        _service = new FundingInvoiceService(
            _mockInvoiceRepo.Object,
            _mockBatchRepo.Object,
            _mockSubaccountRepo.Object,
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
        var request = new CreateFundingInvoiceRequest
        {
            EmployerId = "EMP-001",
            SubaccountId = "SA-001",
            ReimbursementPlanId = "RP-001",
            EmployerFundingDefault = 500m,
            EmployeeFundingDefault = 250m,
            EffectiveDate = DateTime.Today,
            InvoiceDescription = "Test invoice",
            CreatedBy = "TestUser"
        };

        _mockCreateValidator.Setup(v => v.ValidateAsync(request, default))
            .ReturnsAsync(new ValidationResult());

        _mockSubaccountRepo.Setup(r => r.GetByIdAsync(request.SubaccountId))
            .ReturnsAsync(new Subaccount { SubaccountId = request.SubaccountId, Balance = 1000m });

        _mockCashInOutRepo.Setup(r => r.CreateAsync(It.IsAny<CashInOut>()))
            .Returns(Task.CompletedTask);

        _mockInvoiceRepo.Setup(r => r.CreateAsync(It.IsAny<FundingInvoice>()))
            .Returns(Task.CompletedTask);

        // Act
        var result = await _service.CreateAsync(request);

        // Assert
        result.Should().NotBeNull();
        result.Amount.Should().Be(750m); // 500 + 250
        result.SubaccountId.Should().Be(request.SubaccountId);
        result.Status.Should().Be("Pending");
        result.CreatedBy.Should().Be("TestUser");

        _mockCashInOutRepo.Verify(r => r.CreateAsync(It.Is<CashInOut>(c => c.Amount == 750m)), Times.Once);
        _mockInvoiceRepo.Verify(r => r.CreateAsync(It.Is<FundingInvoice>(i => i.Amount == 750m)), Times.Once);
    }

    [Fact]
    public async Task CreateAsync_WithInvalidRequest_ThrowsValidationException()
    {
        // Arrange
        var request = new CreateFundingInvoiceRequest
        {
            EmployerId = "",  // Invalid - empty
            SubaccountId = "SA-001"
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
    public async Task CreateAsync_WhenSubaccountNotFound_ThrowsInvalidOperationException()
    {
        // Arrange
        var request = new CreateFundingInvoiceRequest
        {
            EmployerId = "EMP-001",
            SubaccountId = "SA-NONEXISTENT",
            EmployerFundingDefault = 100m,
            InvoiceDescription = "Test",
            CreatedBy = "TestUser"
        };

        _mockCreateValidator.Setup(v => v.ValidateAsync(request, default))
            .ReturnsAsync(new ValidationResult());

        _mockSubaccountRepo.Setup(r => r.GetByIdAsync(request.SubaccountId))
            .ReturnsAsync((Subaccount?)null);

        // Act & Assert
        await Assert.ThrowsAsync<InvalidOperationException>(() => _service.CreateAsync(request));
    }

    [Fact]
    public async Task GenerateAsync_WhenPegAmountNotMet_ReturnsInvoiceNotNeeded()
    {
        // Arrange
        var request = new GenerateFundingInvoiceRequest
        {
            SubaccountId = "SA-001",
            InvoiceAmount = 500m,
            InvoiceDate = DateTime.Today,
            CreatedBy = "TestUser"
        };

        _mockGenerateValidator.Setup(v => v.ValidateAsync(request, default))
            .ReturnsAsync(new ValidationResult());

        _mockSubaccountRepo.Setup(r => r.GetByIdAsync(request.SubaccountId))
            .ReturnsAsync(new Subaccount { SubaccountId = request.SubaccountId, Balance = 5000m }); // High balance

        _mockParagonAdapter.Setup(a => a.GetReimbursementPlansAsync(request.SubaccountId))
            .ReturnsAsync(new List<ReimbursementPlan>
            {
                new ReimbursementPlan { ReimbursementPlanId = "RP-001", PlanShortDescription = "Test Plan" }
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
        var request = new GenerateFundingInvoiceRequest
        {
            SubaccountId = "SA-001",
            InvoiceAmount = 500m,
            InvoiceDate = DateTime.Today,
            CreatedBy = "TestUser"
        };

        _mockGenerateValidator.Setup(v => v.ValidateAsync(request, default))
            .ReturnsAsync(new ValidationResult());

        _mockSubaccountRepo.Setup(r => r.GetByIdAsync(request.SubaccountId))
            .ReturnsAsync(new Subaccount { SubaccountId = request.SubaccountId, Balance = 100m }); // Low balance triggers invoice

        _mockParagonAdapter.Setup(a => a.GetReimbursementPlansAsync(request.SubaccountId))
            .ReturnsAsync(new List<ReimbursementPlan>
            {
                new ReimbursementPlan { ReimbursementPlanId = "RP-001", PlanShortDescription = "Test Plan", EmployerId = "EMP-001" }
            });

        _mockParagonAdapter.Setup(a => a.GetPaymentAuthorizationsAsync(It.IsAny<string>(), It.IsAny<string>(), It.IsAny<List<string>>()))
            .ReturnsAsync(new List<PaymentAuthorization>());

        _mockCashInOutRepo.Setup(r => r.CreateAsync(It.IsAny<CashInOut>()))
            .Returns(Task.CompletedTask);

        _mockInvoiceRepo.Setup(r => r.CreateAsync(It.IsAny<FundingInvoice>()))
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
        var request = new GenerateFundingInvoiceRequest
        {
            SubaccountId = "SA-001",
            InvoiceAmount = 500m,
            InvoiceDate = DateTime.Today,
            CreatedBy = "TestUser"
        };

        _mockGenerateValidator.Setup(v => v.ValidateAsync(request, default))
            .ReturnsAsync(new ValidationResult());

        _mockSubaccountRepo.Setup(r => r.GetByIdAsync(request.SubaccountId))
            .ReturnsAsync(new Subaccount { SubaccountId = request.SubaccountId, Balance = 100m });

        _mockParagonAdapter.Setup(a => a.GetReimbursementPlansAsync(request.SubaccountId))
            .ReturnsAsync(new List<ReimbursementPlan>
            {
                new ReimbursementPlan { ReimbursementPlanId = "RP-001", PlanShortDescription = "Test Plan", EmployerId = "EMP-001" }
            });

        _mockParagonAdapter.Setup(a => a.GetPaymentAuthorizationsAsync(It.IsAny<string>(), It.IsAny<string>(), It.IsAny<List<string>>()))
            .ReturnsAsync(new List<PaymentAuthorization>
            {
                new PaymentAuthorization { PaymentAuthorizationId = "PA-001", IsAutoDebit = true }
            });

        _mockCashInOutRepo.Setup(r => r.CreateAsync(It.IsAny<CashInOut>()))
            .Returns(Task.CompletedTask);

        _mockInvoiceRepo.Setup(r => r.CreateAsync(It.IsAny<FundingInvoice>()))
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
        var invoice = new FundingInvoice
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
            .ReturnsAsync((FundingInvoice?)null);

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
        var invoices = new List<FundingInvoice>
        {
            new FundingInvoice { InvoiceId = "INV-001", BatchId = batchId, Amount = 100m },
            new FundingInvoice { InvoiceId = "INV-002", BatchId = batchId, Amount = 200m }
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
    public async Task GetBySubaccountIdAsync_ReturnsAllInvoicesForSubaccount()
    {
        // Arrange
        var subaccountId = "SA-001";
        var invoices = new List<FundingInvoice>
        {
            new FundingInvoice { InvoiceId = "INV-001", SubaccountId = subaccountId, Amount = 500m },
            new FundingInvoice { InvoiceId = "INV-002", SubaccountId = subaccountId, Amount = 750m }
        };

        _mockInvoiceRepo.Setup(r => r.GetBySubaccountIdAsync(subaccountId))
            .ReturnsAsync(invoices);

        // Act
        var result = await _service.GetBySubaccountIdAsync(subaccountId);

        // Assert
        result.Should().HaveCount(2);
        result.Sum(r => r.Amount).Should().Be(1250m);
    }
}
