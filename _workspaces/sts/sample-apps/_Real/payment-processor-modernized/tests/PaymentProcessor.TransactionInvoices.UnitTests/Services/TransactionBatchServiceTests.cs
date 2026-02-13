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

public class TransactionBatchServiceTests
{
    private readonly Mock<ITransactionBatchRepository> _mockBatchRepo;
    private readonly Mock<ITransactionInvoiceRepository> _mockInvoiceRepo;
    private readonly Mock<IAccountCategoryRepository> _mockAccountCategoryRepo;
    private readonly Mock<ICashInOutRepository> _mockCashInOutRepo;
    private readonly Mock<IPaymentPlanAdapter> _mockParagonAdapter;
    private readonly Mock<IValidator<CloseTransactionBatchRequest>> _mockCloseValidator;
    private readonly Mock<IValidator<ReopenTransactionBatchRequest>> _mockReopenValidator;
    private readonly Mock<IValidator<UpdateTransactionBatchRequest>> _mockUpdateValidator;
    private readonly Mock<IValidator<CreateTransactionBatchRequest>> _mockCreateValidator;
    private readonly Mock<ILogger<TransactionBatchService>> _mockLogger;
    private readonly TransactionBatchService _service;

    public TransactionBatchServiceTests()
    {
        _mockBatchRepo = new Mock<ITransactionBatchRepository>();
        _mockInvoiceRepo = new Mock<ITransactionInvoiceRepository>();
        _mockAccountCategoryRepo = new Mock<IAccountCategoryRepository>();
        _mockCashInOutRepo = new Mock<ICashInOutRepository>();
        _mockParagonAdapter = new Mock<IPaymentPlanAdapter>();
        _mockCloseValidator = new Mock<IValidator<CloseTransactionBatchRequest>>();
        _mockReopenValidator = new Mock<IValidator<ReopenTransactionBatchRequest>>();
        _mockUpdateValidator = new Mock<IValidator<UpdateTransactionBatchRequest>>();
        _mockCreateValidator = new Mock<IValidator<CreateTransactionBatchRequest>>();
        _mockLogger = new Mock<ILogger<TransactionBatchService>>();

        _service = new TransactionBatchService(
            _mockBatchRepo.Object,
            _mockInvoiceRepo.Object,
            _mockAccountCategoryRepo.Object,
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
        var request = new CloseTransactionBatchRequest
        {
            BatchId = "BATCH-001",
            ExcludedInvoiceIds = new List<string>(),
            ClosedBy = "TestUser"
        };

        var batch = new TransactionBatch
        {
            BatchId = request.BatchId,
            AccountCategoryId = "SA-001",
            Status = "Open"
        };

        var invoices = new List<TransactionInvoice>
        {
            new TransactionInvoice { InvoiceId = "INV-001", BatchId = request.BatchId, Amount = 500m },
            new TransactionInvoice { InvoiceId = "INV-002", BatchId = request.BatchId, Amount = 300m }
        };

        _mockCloseValidator.Setup(v => v.ValidateAsync(request, default))
            .ReturnsAsync(new ValidationResult());

        _mockBatchRepo.Setup(r => r.GetByIdAsync(request.BatchId))
            .ReturnsAsync(batch);

        _mockAccountCategoryRepo.Setup(r => r.GetByIdAsync(batch.AccountCategoryId))
            .ReturnsAsync(new AccountCategory { AccountCategoryId = batch.AccountCategoryId });

        _mockParagonAdapter.Setup(a => a.GetPaymentPlansAsync(batch.AccountCategoryId))
            .ReturnsAsync(new List<PaymentPlan>
            {
                new PaymentPlan { PaymentPlanId = "RP-001", PlanShortDescription = "Test Plan", EmployerId = "EMP-001" }
            });

        _mockInvoiceRepo.Setup(r => r.GetByBatchIdAsync(It.IsAny<string>()))
            .ReturnsAsync(invoices);

        _mockBatchRepo.Setup(r => r.CreateAsync(It.IsAny<TransactionBatch>()))
            .Returns(Task.CompletedTask);

        _mockInvoiceRepo.Setup(r => r.UpdateAsync(It.IsAny<TransactionInvoice>()))
            .Returns(Task.CompletedTask);

        _mockCashInOutRepo.Setup(r => r.CreateAsync(It.IsAny<CashInOut>()))
            .Returns(Task.CompletedTask);

        _mockBatchRepo.Setup(r => r.UpdateAsync(It.IsAny<TransactionBatch>()))
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
        _mockBatchRepo.Verify(r => r.UpdateAsync(It.Is<TransactionBatch>(b => b.Status == "Closed")), Times.Once);
    }

    [Fact]
    public async Task CloseAsync_WithZeroTotal_ThrowsException()
    {
        // Arrange
        var request = new CloseTransactionBatchRequest
        {
            BatchId = "BATCH-001",
            ExcludedInvoiceIds = new List<string>(),
            ClosedBy = "TestUser"
        };

        var batch = new TransactionBatch
        {
            BatchId = request.BatchId,
            AccountCategoryId = "SA-001",
            Status = "Reopened"
        };

        _mockCloseValidator.Setup(v => v.ValidateAsync(request, default))
            .ReturnsAsync(new ValidationResult());

        _mockBatchRepo.Setup(r => r.GetByIdAsync(request.BatchId))
            .ReturnsAsync(batch);

        _mockAccountCategoryRepo.Setup(r => r.GetByIdAsync(batch.AccountCategoryId))
            .ReturnsAsync(new AccountCategory { AccountCategoryId = batch.AccountCategoryId });

        _mockParagonAdapter.Setup(a => a.GetPaymentPlansAsync(batch.AccountCategoryId))
            .ReturnsAsync(new List<PaymentPlan>
            {
                new PaymentPlan { PaymentPlanId = "RP-001", PlanShortDescription = "Test Plan" }
            });

        _mockInvoiceRepo.Setup(r => r.GetByBatchIdAsync(It.IsAny<string>()))
            .ReturnsAsync(new List<TransactionInvoice>()); // Empty - zero total

        _mockBatchRepo.Setup(r => r.UpdateAsync(It.IsAny<TransactionBatch>()))
            .Returns(Task.CompletedTask);

        // Act & Assert
        await Assert.ThrowsAsync<InvalidOperationException>(() => _service.CloseAsync(request));

        _mockBatchRepo.Verify(r => r.UpdateAsync(It.Is<TransactionBatch>(b => b.Status == "Reopened")), Times.Once);
    }

    [Fact]
    public async Task CloseAsync_WithAutoDebit_CreatesPayment()
    {
        // Arrange
        var request = new CloseTransactionBatchRequest
        {
            BatchId = "BATCH-001",
            ExcludedInvoiceIds = new List<string>(),
            ClosedBy = "TestUser"
        };

        var batch = new TransactionBatch
        {
            BatchId = request.BatchId,
            AccountCategoryId = "SA-001",
            Status = "Reopened"
        };

        var invoices = new List<TransactionInvoice>
        {
            new TransactionInvoice { InvoiceId = "INV-001", Amount = 1000m }
        };

        _mockCloseValidator.Setup(v => v.ValidateAsync(request, default))
            .ReturnsAsync(new ValidationResult());

        _mockBatchRepo.Setup(r => r.GetByIdAsync(request.BatchId))
            .ReturnsAsync(batch);

        _mockAccountCategoryRepo.Setup(r => r.GetByIdAsync(batch.AccountCategoryId))
            .ReturnsAsync(new AccountCategory { AccountCategoryId = batch.AccountCategoryId });

        _mockParagonAdapter.Setup(a => a.GetPaymentPlansAsync(batch.AccountCategoryId))
            .ReturnsAsync(new List<PaymentPlan>
            {
                new PaymentPlan { PaymentPlanId = "RP-001", PlanShortDescription = "Test Plan", EmployerId = "EMP-001" }
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

        _mockBatchRepo.Setup(r => r.UpdateAsync(It.IsAny<TransactionBatch>()))
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
        var request = new ReopenTransactionBatchRequest
        {
            BatchId = "BATCH-001",
            ReopenedBy = "TestUser"
        };

        var batch = new TransactionBatch
        {
            BatchId = request.BatchId,
            AccountCategoryId = "SA-001",
            Status = "Closed"
        };

        _mockReopenValidator.Setup(v => v.ValidateAsync(request, default))
            .ReturnsAsync(new ValidationResult());

        _mockBatchRepo.Setup(r => r.GetByIdAsync(request.BatchId))
            .ReturnsAsync(batch);

        _mockBatchRepo.Setup(r => r.UpdateAsync(It.IsAny<TransactionBatch>()))
            .Returns(Task.CompletedTask);

        _mockInvoiceRepo.Setup(r => r.GetByBatchIdAsync(request.BatchId))
            .ReturnsAsync(new List<TransactionInvoice>());

        // Act
        var result = await _service.ReopenAsync(request);

        // Assert
        result.Status.Should().Be("Reopened");
        result.BatchId.Should().Be(request.BatchId);

        _mockBatchRepo.Verify(r => r.UpdateAsync(It.Is<TransactionBatch>(b => b.Status == "Reopened")), Times.Once);
    }

    [Fact]
    public async Task UpdateAsync_WithStatusChange_UpdatesBatch()
    {
        // Arrange
        var request = new UpdateTransactionBatchRequest
        {
            BatchId = "BATCH-001",
            Status = "Pending",
            Description = "Updated description",
            ModifiedBy = "TestUser"
        };

        var batch = new TransactionBatch
        {
            BatchId = request.BatchId,
            AccountCategoryId = "SA-001",
            Status = "Open"
        };

        _mockUpdateValidator.Setup(v => v.ValidateAsync(request, default))
            .ReturnsAsync(new ValidationResult());

        _mockBatchRepo.Setup(r => r.GetByIdAsync(request.BatchId))
            .ReturnsAsync(batch);

        _mockBatchRepo.Setup(r => r.UpdateAsync(It.IsAny<TransactionBatch>()))
            .Returns(Task.CompletedTask);

        _mockInvoiceRepo.Setup(r => r.GetByBatchIdAsync(request.BatchId))
            .ReturnsAsync(new List<TransactionInvoice>());

        // Act
        var result = await _service.UpdateAsync(request);

        // Assert
        result.Status.Should().Be("Pending");
        result.Description.Should().Be("Updated description");

        _mockBatchRepo.Verify(r => r.UpdateAsync(It.Is<TransactionBatch>(b => 
            b.Status == "Pending" && 
            b.Description == "Updated description"
        )), Times.Once);
    }

    [Fact]
    public async Task CreateAsync_WithValidRequest_CreatesBatch()
    {
        // Arrange
        var request = new CreateTransactionBatchRequest
        {
            AccountCategoryId = "SA-001",
            Status = "Open",
            Description = "New batch",
            CreatedBy = "TestUser"
        };

        _mockCreateValidator.Setup(v => v.ValidateAsync(request, default))
            .ReturnsAsync(new ValidationResult());

        _mockBatchRepo.Setup(r => r.CreateAsync(It.IsAny<TransactionBatch>()))
            .Returns(Task.CompletedTask);

        // Act
        var result = await _service.CreateAsync(request);

        // Assert
        result.Should().NotBeNull();
        result.AccountCategoryId.Should().Be(request.AccountCategoryId);
        result.Status.Should().Be("Open");
        result.Description.Should().Be("New batch");

        _mockBatchRepo.Verify(r => r.CreateAsync(It.Is<TransactionBatch>(b => 
            b.AccountCategoryId == request.AccountCategoryId &&
            b.Status == "Open"
        )), Times.Once);
    }

    [Fact]
    public async Task GetByIdAsync_WhenBatchExists_ReturnsBatchWithInvoiceCount()
    {
        // Arrange
        var batchId = "BATCH-001";
        var batch = new TransactionBatch
        {
            BatchId = batchId,
            AccountCategoryId = "SA-001",
            Status = "Open"
        };

        var invoices = new List<TransactionInvoice>
        {
            new TransactionInvoice { InvoiceId = "INV-001", Amount = 100m },
            new TransactionInvoice { InvoiceId = "INV-002", Amount = 200m }
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
        var account_categoryId = "SA-001";
        var openBatch = new TransactionBatch
        {
            BatchId = "BATCH-001",
            AccountCategoryId = account_categoryId,
            Status = "Open"
        };

        _mockBatchRepo.Setup(r => r.GetByStatusAsync("Open"))
            .ReturnsAsync(new List<TransactionBatch> { openBatch });

        _mockInvoiceRepo.Setup(r => r.GetByBatchIdAsync(openBatch.BatchId))
            .ReturnsAsync(new List<TransactionInvoice>());

        // Act
        var result = await _service.GetOpenBatchAsync(account_categoryId);

        // Assert
        result.Should().NotBeNull();
        result!.BatchId.Should().Be(openBatch.BatchId);
        result.Status.Should().Be("Open");
    }
}
