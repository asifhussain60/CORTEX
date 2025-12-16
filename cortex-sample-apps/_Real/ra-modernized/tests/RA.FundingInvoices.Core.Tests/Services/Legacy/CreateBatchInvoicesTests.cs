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
/// Unit tests for CreateBatchInvoicesAsync (WCF: Updater_CreateRAFundingInvoices migration)
/// </summary>
public class CreateBatchInvoicesTests
{
    private readonly Mock<IFundingInvoiceRepository> _invoiceRepositoryMock;
    private readonly Mock<IFundingBatchRepository> _batchRepositoryMock;
    private readonly Mock<ISubaccountRepository> _subaccountRepositoryMock;
    private readonly Mock<ICashInOutRepository> _cashInOutRepositoryMock;
    private readonly Mock<IReimbursementPlanAdapter> _paragonAdapterMock;
    private readonly Mock<ILogger<FundingInvoiceService>> _loggerMock;
    private readonly FundingInvoiceService _service;

    public CreateBatchInvoicesTests()
    {
        _invoiceRepositoryMock = new Mock<IFundingInvoiceRepository>();
        _batchRepositoryMock = new Mock<IFundingBatchRepository>();
        _subaccountRepositoryMock = new Mock<ISubaccountRepository>();
        _cashInOutRepositoryMock = new Mock<ICashInOutRepository>();
        _paragonAdapterMock = new Mock<IReimbursementPlanAdapter>();
        _loggerMock = new Mock<ILogger<FundingInvoiceService>>();

        // Mock validators (permissive for legacy methods)
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
    public async Task CreateBatchInvoicesAsync_WithValidSubaccounts_ReturnsSuccessResult()
    {
        // Arrange
        var dto = new CreateBatchInvoicesDto
        {
            EmployerId = "EMP123",
            SubaccountIds = new List<int> { 1001, 1002, 1003 },
            EffectiveDate = new DateTime(2025, 12, 15),
            Description = "Q4 2025 Funding"
        };

        // Mock subaccounts
        _subaccountRepositoryMock.Setup(r => r.GetByIdAsync("1001"))
            .ReturnsAsync(new Subaccount { SubaccountId = "1001", AccountNumber = "ACC1001" });
        _subaccountRepositoryMock.Setup(r => r.GetByIdAsync("1002"))
            .ReturnsAsync(new Subaccount { SubaccountId = "1002", AccountNumber = "ACC1002" });
        _subaccountRepositoryMock.Setup(r => r.GetByIdAsync("1003"))
            .ReturnsAsync(new Subaccount { SubaccountId = "1003", AccountNumber = "ACC1003" });

        // Mock no existing invoices (no duplicates)
        _invoiceRepositoryMock.Setup(r => r.GetBySubaccountIdAsync(It.IsAny<string>()))
            .ReturnsAsync(new List<FundingInvoice>());

        // Mock reimbursement plans (balance below peg)
        _paragonAdapterMock.Setup(p => p.GetReimbursementPlansAsync(It.IsAny<string>()))
            .ReturnsAsync(new List<ReimbursementPlan>
            {
                new ReimbursementPlan { Balance = 500m } // Below 1000 peg → creates invoice
            });

        // Act
        var result = await _service.CreateBatchInvoicesAsync(dto);

        // Assert
        result.Should().NotBeNull();
        result.SuccessCount.Should().Be(3);
        result.FailureCount.Should().Be(0);
        result.TotalInvoices.Should().Be(3);
        result.FailedSubaccounts.Should().BeEmpty();

        _batchRepositoryMock.Verify(r => r.CreateAsync(It.IsAny<FundingBatch>()), Times.Once);
        _invoiceRepositoryMock.Verify(r => r.CreateAsync(It.IsAny<FundingInvoice>()), Times.Exactly(3));
    }

    [Fact]
    public async Task CreateBatchInvoicesAsync_WithPartialSuccess_ReturnsPartialResult()
    {
        // Arrange
        var dto = new CreateBatchInvoicesDto
        {
            EmployerId = "EMP123",
            SubaccountIds = new List<int> { 1001, 1002, 9999 }, // 9999 doesn't exist
            EffectiveDate = new DateTime(2025, 12, 15)
        };

        // Mock existing subaccounts
        _subaccountRepositoryMock.Setup(r => r.GetByIdAsync("1001"))
            .ReturnsAsync(new Subaccount { SubaccountId = "1001", AccountNumber = "ACC1001" });
        _subaccountRepositoryMock.Setup(r => r.GetByIdAsync("1002"))
            .ReturnsAsync(new Subaccount { SubaccountId = "1002", AccountNumber = "ACC1002" });
        
        // Mock non-existent subaccount
        _subaccountRepositoryMock.Setup(r => r.GetByIdAsync("9999"))
            .ReturnsAsync((Subaccount?)null);

        _invoiceRepositoryMock.Setup(r => r.GetBySubaccountIdAsync(It.IsAny<string>()))
            .ReturnsAsync(new List<FundingInvoice>());

        _paragonAdapterMock.Setup(p => p.GetReimbursementPlansAsync(It.IsAny<string>()))
            .ReturnsAsync(new List<ReimbursementPlan> { new ReimbursementPlan { Balance = 500m } });

        // Act
        var result = await _service.CreateBatchInvoicesAsync(dto);

        // Assert
        result.SuccessCount.Should().Be(2);
        result.FailureCount.Should().Be(1);
        result.FailedSubaccounts.Should().HaveCount(1);
        result.FailedSubaccounts[0].SubaccountId.Should().Be(9999);
        result.FailedSubaccounts[0].ErrorType.Should().Be("NotFound");
    }

    [Fact]
    public async Task CreateBatchInvoicesAsync_WithDuplicateInvoices_SkipsDuplicates()
    {
        // Arrange
        var effectiveDate = new DateTime(2025, 12, 15);
        var dto = new CreateBatchInvoicesDto
        {
            EmployerId = "EMP123",
            SubaccountIds = new List<int> { 1001, 1002 },
            EffectiveDate = effectiveDate
        };

        _subaccountRepositoryMock.Setup(r => r.GetByIdAsync("1001"))
            .ReturnsAsync(new Subaccount { SubaccountId = "1001", AccountNumber = "ACC1001" });
        _subaccountRepositoryMock.Setup(r => r.GetByIdAsync("1002"))
            .ReturnsAsync(new Subaccount { SubaccountId = "1002", AccountNumber = "ACC1002" });

        // Mock existing invoice for subaccount 1001 on same date (duplicate)
        _invoiceRepositoryMock.Setup(r => r.GetBySubaccountIdAsync("1001"))
            .ReturnsAsync(new List<FundingInvoice>
            {
                new FundingInvoice { InvoiceDate = effectiveDate, SubaccountId = "1001" }
            });

        // Mock no existing invoice for subaccount 1002
        _invoiceRepositoryMock.Setup(r => r.GetBySubaccountIdAsync("1002"))
            .ReturnsAsync(new List<FundingInvoice>());

        _paragonAdapterMock.Setup(p => p.GetReimbursementPlansAsync(It.IsAny<string>()))
            .ReturnsAsync(new List<ReimbursementPlan> { new ReimbursementPlan { Balance = 500m } });

        // Act
        var result = await _service.CreateBatchInvoicesAsync(dto);

        // Assert
        result.SuccessCount.Should().Be(1); // Only 1002 succeeds
        result.FailureCount.Should().Be(1); // 1001 is duplicate
        result.FailedSubaccounts.Should().HaveCount(1);
        result.FailedSubaccounts[0].ErrorType.Should().Be("Duplicate");

        _invoiceRepositoryMock.Verify(r => r.CreateAsync(It.IsAny<FundingInvoice>()), Times.Once);
    }

    [Fact]
    public async Task CreateBatchInvoicesAsync_WithBalanceMeetsPeg_SkipsInvoice()
    {
        // Arrange
        var dto = new CreateBatchInvoicesDto
        {
            EmployerId = "EMP123",
            SubaccountIds = new List<int> { 1001 },
            EffectiveDate = new DateTime(2025, 12, 15)
        };

        _subaccountRepositoryMock.Setup(r => r.GetByIdAsync("1001"))
            .ReturnsAsync(new Subaccount { SubaccountId = "1001", AccountNumber = "ACC1001" });

        _invoiceRepositoryMock.Setup(r => r.GetBySubaccountIdAsync(It.IsAny<string>()))
            .ReturnsAsync(new List<FundingInvoice>());

        // Mock high balance (meets peg requirement)
        _paragonAdapterMock.Setup(p => p.GetReimbursementPlansAsync("1001"))
            .ReturnsAsync(new List<ReimbursementPlan>
            {
                new ReimbursementPlan { Balance = 1500m } // Above 1000 peg → no invoice needed
            });

        // Act
        var result = await _service.CreateBatchInvoicesAsync(dto);

        // Assert
        result.SuccessCount.Should().Be(0);
        result.FailureCount.Should().Be(1);
        result.FailedSubaccounts[0].ErrorType.Should().Be("NotNeeded");
        result.FailedSubaccounts[0].Reason.Should().Contain("Balance meets peg");

        _invoiceRepositoryMock.Verify(r => r.CreateAsync(It.IsAny<FundingInvoice>()), Times.Never);
    }

    [Fact]
    public async Task CreateBatchInvoicesAsync_WithNoReimbursementPlans_ReturnsFailure()
    {
        // Arrange
        var dto = new CreateBatchInvoicesDto
        {
            EmployerId = "EMP123",
            SubaccountIds = new List<int> { 1001 },
            EffectiveDate = new DateTime(2025, 12, 15)
        };

        _subaccountRepositoryMock.Setup(r => r.GetByIdAsync("1001"))
            .ReturnsAsync(new Subaccount { SubaccountId = "1001", AccountNumber = "ACC1001" });

        _invoiceRepositoryMock.Setup(r => r.GetBySubaccountIdAsync(It.IsAny<string>()))
            .ReturnsAsync(new List<FundingInvoice>());

        // Mock no reimbursement plans
        _paragonAdapterMock.Setup(p => p.GetReimbursementPlansAsync("1001"))
            .ReturnsAsync(new List<ReimbursementPlan>());

        // Act
        var result = await _service.CreateBatchInvoicesAsync(dto);

        // Assert
        result.SuccessCount.Should().Be(0);
        result.FailureCount.Should().Be(1);
        result.FailedSubaccounts[0].ErrorType.Should().Be("MissingData");
        result.FailedSubaccounts[0].Reason.Should().Contain("No reimbursement plans found");
    }

    [Fact]
    public async Task CreateBatchInvoicesAsync_CalculatesCorrectPegAmount()
    {
        // Arrange
        var dto = new CreateBatchInvoicesDto
        {
            EmployerId = "EMP123",
            SubaccountIds = new List<int> { 1001 },
            EffectiveDate = new DateTime(2025, 12, 15)
        };

        _subaccountRepositoryMock.Setup(r => r.GetByIdAsync("1001"))
            .ReturnsAsync(new Subaccount { SubaccountId = "1001", AccountNumber = "ACC1001" });

        _invoiceRepositoryMock.Setup(r => r.GetBySubaccountIdAsync(It.IsAny<string>()))
            .ReturnsAsync(new List<FundingInvoice>());

        // Balance: 300, Invoice Amount: 1000 → Peg: 700
        _paragonAdapterMock.Setup(p => p.GetReimbursementPlansAsync("1001"))
            .ReturnsAsync(new List<ReimbursementPlan> { new ReimbursementPlan { Balance = 300m } });

        FundingInvoice? capturedInvoice = null;
        _invoiceRepositoryMock.Setup(r => r.CreateAsync(It.IsAny<FundingInvoice>()))
            .Callback<FundingInvoice>(inv => capturedInvoice = inv)
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
            SubaccountIds = new List<int> { 1001, 1002 },
            EffectiveDate = new DateTime(2025, 12, 15)
        };

        _subaccountRepositoryMock.Setup(r => r.GetByIdAsync("1001"))
            .ReturnsAsync(new Subaccount { SubaccountId = "1001", AccountNumber = "ACC1001" });
        _subaccountRepositoryMock.Setup(r => r.GetByIdAsync("1002"))
            .ReturnsAsync(new Subaccount { SubaccountId = "1002", AccountNumber = "ACC1002" });

        _invoiceRepositoryMock.Setup(r => r.GetBySubaccountIdAsync(It.IsAny<string>()))
            .ReturnsAsync(new List<FundingInvoice>());

        _paragonAdapterMock.Setup(p => p.GetReimbursementPlansAsync(It.IsAny<string>()))
            .ReturnsAsync(new List<ReimbursementPlan> { new ReimbursementPlan { Balance = 500m } });

        FundingBatch? capturedBatch = null;
        _batchRepositoryMock.Setup(r => r.UpdateAsync(It.IsAny<FundingBatch>()))
            .Callback<FundingBatch>(b => capturedBatch = b)
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
            SubaccountIds = new List<int> { 1001 },
            EffectiveDate = new DateTime(2025, 12, 15)
        };

        _subaccountRepositoryMock.Setup(r => r.GetByIdAsync("1001"))
            .ReturnsAsync(new Subaccount { SubaccountId = "1001", AccountNumber = "ACC1001" });

        _invoiceRepositoryMock.Setup(r => r.GetBySubaccountIdAsync(It.IsAny<string>()))
            .ReturnsAsync(new List<FundingInvoice>());

        _paragonAdapterMock.Setup(p => p.GetReimbursementPlansAsync(It.IsAny<string>()))
            .ReturnsAsync(new List<ReimbursementPlan> { new ReimbursementPlan { Balance = 500m } });

        FundingBatch? capturedBatch = null;
        _batchRepositoryMock.Setup(r => r.CreateAsync(It.IsAny<FundingBatch>()))
            .Callback<FundingBatch>(b => capturedBatch = b)
            .Returns(Task.CompletedTask);

        // Act
        await _service.CreateBatchInvoicesAsync(dto);

        // Assert
        capturedBatch.Should().NotBeNull();
        capturedBatch!.Status.Should().Be("Pending");
        capturedBatch.EmployerId.Should().Be("EMP123");
    }

    [Fact]
    public async Task CreateBatchInvoicesAsync_WithEmptySubaccountList_CreatesEmptyBatch()
    {
        // Arrange
        var dto = new CreateBatchInvoicesDto
        {
            EmployerId = "EMP123",
            SubaccountIds = new List<int>(), // Empty list
            EffectiveDate = new DateTime(2025, 12, 15)
        };

        // Act
        var result = await _service.CreateBatchInvoicesAsync(dto);

        // Assert
        result.TotalInvoices.Should().Be(0);
        result.SuccessCount.Should().Be(0);
        result.FailureCount.Should().Be(0);

        _batchRepositoryMock.Verify(r => r.CreateAsync(It.IsAny<FundingBatch>()), Times.Once);
        _invoiceRepositoryMock.Verify(r => r.CreateAsync(It.IsAny<FundingInvoice>()), Times.Never);
    }
}
