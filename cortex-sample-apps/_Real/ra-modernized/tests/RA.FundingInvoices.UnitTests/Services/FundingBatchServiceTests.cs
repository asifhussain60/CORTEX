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

public class FundingBatchServiceTests
{
    private readonly Mock<IFundingBatchRepository> _mockBatchRepo;
    private readonly Mock<IFundingInvoiceRepository> _mockInvoiceRepo;
    private readonly Mock<ISubaccountRepository> _mockSubaccountRepo;
    private readonly Mock<ICashInOutRepository> _mockCashInOutRepo;
    private readonly Mock<IReimbursementPlanAdapter> _mockParagonAdapter;
    private readonly Mock<IValidator<CloseFundingBatchRequest>> _mockCloseValidator;
    private readonly Mock<IValidator<ReopenFundingBatchRequest>> _mockReopenValidator;
    private readonly Mock<IValidator<UpdateFundingBatchRequest>> _mockUpdateValidator;
    private readonly Mock<IValidator<CreateFundingBatchRequest>> _mockCreateValidator;
    private readonly Mock<ILogger<FundingBatchService>> _mockLogger;
    private readonly FundingBatchService _service;

    public FundingBatchServiceTests()
    {
        _mockBatchRepo = new Mock<IFundingBatchRepository>();
        _mockInvoiceRepo = new Mock<IFundingInvoiceRepository>();
        _mockSubaccountRepo = new Mock<ISubaccountRepository>();
        _mockCashInOutRepo = new Mock<ICashInOutRepository>();
        _mockParagonAdapter = new Mock<IReimbursementPlanAdapter>();
        _mockCloseValidator = new Mock<IValidator<CloseFundingBatchRequest>>();
        _mockReopenValidator = new Mock<IValidator<ReopenFundingBatchRequest>>();
        _mockUpdateValidator = new Mock<IValidator<UpdateFundingBatchRequest>>();
        _mockCreateValidator = new Mock<IValidator<CreateFundingBatchRequest>>();
        _mockLogger = new Mock<ILogger<FundingBatchService>>();

        _service = new FundingBatchService(
            _mockBatchRepo.Object,
            _mockInvoiceRepo.Object,
            _mockSubaccountRepo.Object,
            _mockCashInOutRepo.Object,
            _mockParagonAdapter.Object,
            _mockCloseValidator.Object,
            _mockReopenValidator.Object,
            _mockUpdateValidator.Object,
            _mockCreateValidator.Object,
            _mockLogger.Object
        );
    }

    [Fact]
    public async Task CloseAsync_WithValidOpenBatch_CreatesCashInOutAndClosesBatch()
    {
        // Arrange
        var request = new CloseFundingBatchRequest
        {
            BatchId = "BATCH-001",
            ExcludedInvoiceIds = new List<string>(),
            ClosedBy = "TestUser"
        };

        var batch = new FundingBatch
        {
            BatchId = request.BatchId,
            SubaccountId = "SA-001",
            Status = "Open"
        };

        var invoices = new List<FundingInvoice>
        {
            new FundingInvoice { InvoiceId = "INV-001", BatchId = request.BatchId, Amount = 500m },
            new FundingInvoice { InvoiceId = "INV-002", BatchId = request.BatchId, Amount = 300m }
        };

        _mockCloseValidator.Setup(v => v.ValidateAsync(request, default))
            .ReturnsAsync(new ValidationResult());

        _mockBatchRepo.Setup(r => r.GetByIdAsync(request.BatchId))
            .ReturnsAsync(batch);

        _mockSubaccountRepo.Setup(r => r.GetByIdAsync(batch.SubaccountId))
            .ReturnsAsync(new Subaccount { SubaccountId = batch.SubaccountId });

        _mockParagonAdapter.Setup(a => a.GetReimbursementPlansAsync(batch.SubaccountId))
            .ReturnsAsync(new List<ReimbursementPlan>
            {
                new ReimbursementPlan { ReimbursementPlanId = "RP-001", PlanShortDescription = "Test Plan", EmployerId = "EMP-001" }
            });

        _mockInvoiceRepo.Setup(r => r.GetByBatchIdAsync(It.IsAny<string>()))
            .ReturnsAsync(invoices);

        _mockBatchRepo.Setup(r => r.CreateAsync(It.IsAny<FundingBatch>()))
            .Returns(Task.CompletedTask);

        _mockInvoiceRepo.Setup(r => r.UpdateAsync(It.IsAny<FundingInvoice>()))
            .Returns(Task.CompletedTask);

        _mockCashInOutRepo.Setup(r => r.CreateAsync(It.IsAny<CashInOut>()))
            .Returns(Task.CompletedTask);

        _mockBatchRepo.Setup(r => r.UpdateAsync(It.IsAny<FundingBatch>()))
            .Returns(Task.CompletedTask);

        _mockParagonAdapter.Setup(a => a.GetPaymentAuthorizationsAsync(It.IsAny<string>(), It.IsAny<string>(), It.IsAny<List<string>>()))
            .ReturnsAsync(new List<PaymentAuthorization>());

        // Act
        var result = await _service.CloseAsync(request);

        // Assert
        result.Should().NotBeNull();
        result.CashInOutAmount.Should().Be(-800m); // Negative for replenishment
        result.CashInOutId.Should().NotBeNullOrEmpty();
        result.Batch.Status.Should().Be("Closed");

        _mockCashInOutRepo.Verify(r => r.CreateAsync(It.Is<CashInOut>(c => c.Amount == -800m)), Times.Once);
        _mockBatchRepo.Verify(r => r.UpdateAsync(It.Is<FundingBatch>(b => b.Status == "Closed")), Times.Once);
    }

    [Fact]
    public async Task CloseAsync_WithZeroTotal_ThrowsException()
    {
        // Arrange
        var request = new CloseFundingBatchRequest
        {
            BatchId = "BATCH-001",
            ExcludedInvoiceIds = new List<string>(),
            ClosedBy = "TestUser"
        };

        var batch = new FundingBatch
        {
            BatchId = request.BatchId,
            SubaccountId = "SA-001",
            Status = "Reopened"
        };

        _mockCloseValidator.Setup(v => v.ValidateAsync(request, default))
            .ReturnsAsync(new ValidationResult());

        _mockBatchRepo.Setup(r => r.GetByIdAsync(request.BatchId))
            .ReturnsAsync(batch);

        _mockSubaccountRepo.Setup(r => r.GetByIdAsync(batch.SubaccountId))
            .ReturnsAsync(new Subaccount { SubaccountId = batch.SubaccountId });

        _mockParagonAdapter.Setup(a => a.GetReimbursementPlansAsync(batch.SubaccountId))
            .ReturnsAsync(new List<ReimbursementPlan>
            {
                new ReimbursementPlan { ReimbursementPlanId = "RP-001", PlanShortDescription = "Test Plan" }
            });

        _mockInvoiceRepo.Setup(r => r.GetByBatchIdAsync(It.IsAny<string>()))
            .ReturnsAsync(new List<FundingInvoice>()); // Empty - zero total

        _mockBatchRepo.Setup(r => r.UpdateAsync(It.IsAny<FundingBatch>()))
            .Returns(Task.CompletedTask);

        // Act & Assert
        await Assert.ThrowsAsync<InvalidOperationException>(() => _service.CloseAsync(request));

        _mockBatchRepo.Verify(r => r.UpdateAsync(It.Is<FundingBatch>(b => b.Status == "Reopened")), Times.Once);
    }

    [Fact]
    public async Task CloseAsync_WithAutoDebit_CreatesPayment()
    {
        // Arrange
        var request = new CloseFundingBatchRequest
        {
            BatchId = "BATCH-001",
            ExcludedInvoiceIds = new List<string>(),
            ClosedBy = "TestUser"
        };

        var batch = new FundingBatch
        {
            BatchId = request.BatchId,
            SubaccountId = "SA-001",
            Status = "Reopened"
        };

        var invoices = new List<FundingInvoice>
        {
            new FundingInvoice { InvoiceId = "INV-001", Amount = 1000m }
        };

        _mockCloseValidator.Setup(v => v.ValidateAsync(request, default))
            .ReturnsAsync(new ValidationResult());

        _mockBatchRepo.Setup(r => r.GetByIdAsync(request.BatchId))
            .ReturnsAsync(batch);

        _mockSubaccountRepo.Setup(r => r.GetByIdAsync(batch.SubaccountId))
            .ReturnsAsync(new Subaccount { SubaccountId = batch.SubaccountId });

        _mockParagonAdapter.Setup(a => a.GetReimbursementPlansAsync(batch.SubaccountId))
            .ReturnsAsync(new List<ReimbursementPlan>
            {
                new ReimbursementPlan { ReimbursementPlanId = "RP-001", PlanShortDescription = "Test Plan", EmployerId = "EMP-001" }
            });

        _mockInvoiceRepo.Setup(r => r.GetByBatchIdAsync(It.IsAny<string>()))
            .ReturnsAsync(invoices);

        _mockParagonAdapter.Setup(a => a.GetPaymentAuthorizationsAsync(It.IsAny<string>(), It.IsAny<string>(), It.IsAny<List<string>>()))
            .ReturnsAsync(new List<PaymentAuthorization>
            {
                new PaymentAuthorization { PaymentAuthorizationId = "PA-001", IsAutoDebit = true }
            });

        _mockCashInOutRepo.Setup(r => r.CreateAsync(It.IsAny<CashInOut>()))
            .Returns(Task.CompletedTask);

        _mockBatchRepo.Setup(r => r.UpdateAsync(It.IsAny<FundingBatch>()))
            .Returns(Task.CompletedTask);

        // Act
        var result = await _service.CloseAsync(request);

        // Assert
        result.AutoDebitProcessed.Should().BeTrue();
        result.PaymentId.Should().NotBeNullOrEmpty();
    }

    [Fact]
    public async Task ReopenAsync_WithValidBatch_UpdatesStatusToReopened()
    {
        // Arrange
        var request = new ReopenFundingBatchRequest
        {
            BatchId = "BATCH-001",
            ReopenedBy = "TestUser"
        };

        var batch = new FundingBatch
        {
            BatchId = request.BatchId,
            SubaccountId = "SA-001",
            Status = "Closed"
        };

        _mockReopenValidator.Setup(v => v.ValidateAsync(request, default))
            .ReturnsAsync(new ValidationResult());

        _mockBatchRepo.Setup(r => r.GetByIdAsync(request.BatchId))
            .ReturnsAsync(batch);

        _mockBatchRepo.Setup(r => r.UpdateAsync(It.IsAny<FundingBatch>()))
            .Returns(Task.CompletedTask);

        _mockInvoiceRepo.Setup(r => r.GetByBatchIdAsync(request.BatchId))
            .ReturnsAsync(new List<FundingInvoice>());

        // Act
        var result = await _service.ReopenAsync(request);

        // Assert
        result.Status.Should().Be("Reopened");
        result.BatchId.Should().Be(request.BatchId);

        _mockBatchRepo.Verify(r => r.UpdateAsync(It.Is<FundingBatch>(b => b.Status == "Reopened")), Times.Once);
    }

    [Fact]
    public async Task UpdateAsync_WithStatusChange_UpdatesBatch()
    {
        // Arrange
        var request = new UpdateFundingBatchRequest
        {
            BatchId = "BATCH-001",
            Status = "Pending",
            Description = "Updated description",
            ModifiedBy = "TestUser"
        };

        var batch = new FundingBatch
        {
            BatchId = request.BatchId,
            SubaccountId = "SA-001",
            Status = "Open"
        };

        _mockUpdateValidator.Setup(v => v.ValidateAsync(request, default))
            .ReturnsAsync(new ValidationResult());

        _mockBatchRepo.Setup(r => r.GetByIdAsync(request.BatchId))
            .ReturnsAsync(batch);

        _mockBatchRepo.Setup(r => r.UpdateAsync(It.IsAny<FundingBatch>()))
            .Returns(Task.CompletedTask);

        _mockInvoiceRepo.Setup(r => r.GetByBatchIdAsync(request.BatchId))
            .ReturnsAsync(new List<FundingInvoice>());

        // Act
        var result = await _service.UpdateAsync(request);

        // Assert
        result.Status.Should().Be("Pending");
        result.Description.Should().Be("Updated description");

        _mockBatchRepo.Verify(r => r.UpdateAsync(It.Is<FundingBatch>(b => 
            b.Status == "Pending" && 
            b.Description == "Updated description"
        )), Times.Once);
    }

    [Fact]
    public async Task CreateAsync_WithValidRequest_CreatesBatch()
    {
        // Arrange
        var request = new CreateFundingBatchRequest
        {
            SubaccountId = "SA-001",
            Status = "Open",
            Description = "New batch",
            CreatedBy = "TestUser"
        };

        _mockCreateValidator.Setup(v => v.ValidateAsync(request, default))
            .ReturnsAsync(new ValidationResult());

        _mockBatchRepo.Setup(r => r.CreateAsync(It.IsAny<FundingBatch>()))
            .Returns(Task.CompletedTask);

        // Act
        var result = await _service.CreateAsync(request);

        // Assert
        result.Should().NotBeNull();
        result.SubaccountId.Should().Be(request.SubaccountId);
        result.Status.Should().Be("Open");
        result.Description.Should().Be("New batch");

        _mockBatchRepo.Verify(r => r.CreateAsync(It.Is<FundingBatch>(b => 
            b.SubaccountId == request.SubaccountId &&
            b.Status == "Open"
        )), Times.Once);
    }

    [Fact]
    public async Task GetByIdAsync_WhenBatchExists_ReturnsBatchWithInvoiceCount()
    {
        // Arrange
        var batchId = "BATCH-001";
        var batch = new FundingBatch
        {
            BatchId = batchId,
            SubaccountId = "SA-001",
            Status = "Open"
        };

        var invoices = new List<FundingInvoice>
        {
            new FundingInvoice { InvoiceId = "INV-001", Amount = 100m },
            new FundingInvoice { InvoiceId = "INV-002", Amount = 200m }
        };

        _mockBatchRepo.Setup(r => r.GetByIdAsync(batchId))
            .ReturnsAsync(batch);

        _mockInvoiceRepo.Setup(r => r.GetByBatchIdAsync(batchId))
            .ReturnsAsync(invoices);

        // Act
        var result = await _service.GetByIdAsync(batchId);

        // Assert
        result.Should().NotBeNull();
        result!.InvoiceCount.Should().Be(2);
        result.TotalAmount.Should().Be(300m);
    }

    [Fact]
    public async Task GetOpenBatchAsync_WhenOpenBatchExists_ReturnsBatch()
    {
        // Arrange
        var subaccountId = "SA-001";
        var openBatch = new FundingBatch
        {
            BatchId = "BATCH-001",
            SubaccountId = subaccountId,
            Status = "Open"
        };

        _mockBatchRepo.Setup(r => r.GetByStatusAsync("Open"))
            .ReturnsAsync(new List<FundingBatch> { openBatch });

        _mockInvoiceRepo.Setup(r => r.GetByBatchIdAsync(openBatch.BatchId))
            .ReturnsAsync(new List<FundingInvoice>());

        // Act
        var result = await _service.GetOpenBatchAsync(subaccountId);

        // Assert
        result.Should().NotBeNull();
        result!.BatchId.Should().Be(openBatch.BatchId);
        result.Status.Should().Be("Open");
    }
}
