using FluentAssertions;
using Microsoft.EntityFrameworkCore;
using RA.FundingInvoices.Core.Entities;
using RA.FundingInvoices.Infrastructure.Persistence;
using RA.FundingInvoices.Infrastructure.Persistence.Repositories;
using Xunit;

namespace RA.FundingInvoices.UnitTests.Persistence;

/// <summary>
/// Unit tests for EFCoreUnitOfWork.
/// Validates transaction management and repository coordination.
/// </summary>
public class EFCoreUnitOfWorkTests : IDisposable
{
    private readonly FundingInvoicesDbContext _context;
    private readonly EFCoreUnitOfWork _unitOfWork;

    public EFCoreUnitOfWorkTests()
    {
        var options = new DbContextOptionsBuilder<FundingInvoicesDbContext>()
            .UseSqlite("DataSource=:memory:")
            .Options;

        _context = new FundingInvoicesDbContext(options);
        _context.Database.OpenConnection();
        _context.Database.EnsureCreated();

        _unitOfWork = new EFCoreUnitOfWork(_context);
    }

    [Fact]
    public void Repositories_ShouldBeLazilyInitialized()
    {
        // Act
        var invoiceRepo = _unitOfWork.FundingInvoiceRepository;
        var batchRepo = _unitOfWork.FundingBatchRepository;
        var subaccountRepo = _unitOfWork.SubaccountRepository;
        var cashRepo = _unitOfWork.CashInOutRepository;

        // Assert
        invoiceRepo.Should().NotBeNull();
        batchRepo.Should().NotBeNull();
        subaccountRepo.Should().NotBeNull();
        cashRepo.Should().NotBeNull();

        // Verify same instance returned (singleton behavior per UoW)
        _unitOfWork.FundingInvoiceRepository.Should().BeSameAs(invoiceRepo);
    }

    [Fact]
    public async Task BeginTransactionAsync_ShouldStartTransaction()
    {
        // Act
        await _unitOfWork.BeginTransactionAsync();

        // Assert - transaction should be active
        var batch = new FundingBatch
        {
            BatchId = "BTH-TX-001",
            BatchNumber = "BATCH-TX-001",
            Status = "Open",
            CreatedBy = "TEST_USER"
        };
        await _context.FundingBatches.AddAsync(batch);
        await _context.SaveChangesAsync();

        var dbBatch = await _context.FundingBatches.FindAsync("BTH-TX-001");
        dbBatch.Should().NotBeNull();

        await _unitOfWork.RollbackTransactionAsync();
    }

    [Fact]
    public async Task CommitTransactionAsync_ShouldPersistChanges()
    {
        // Arrange
        await _unitOfWork.BeginTransactionAsync();

        var batch = new FundingBatch
        {
            BatchId = "BTH-TX-002",
            BatchNumber = "BATCH-TX-002",
            Status = "Open",
            TotalAmount = 1000m,
            CreatedBy = "TEST_USER"
        };
        var subaccount = new Subaccount
        {
            SubaccountId = "SUB-TX-001",
            AccountNumber = "ACC-TX-001",
            AccountType = "HSA",
            MemberId = "MEM-TX-001",
            Balance = 500m,
            CreatedBy = "TEST_USER"
        };

        await _context.FundingBatches.AddAsync(batch);
        await _context.Subaccounts.AddAsync(subaccount);

        // Act
        await _unitOfWork.CommitTransactionAsync();

        // Assert
        var dbBatch = await _context.FundingBatches.FindAsync("BTH-TX-002");
        var dbSubaccount = await _context.Subaccounts.FindAsync("SUB-TX-001");

        dbBatch.Should().NotBeNull();
        dbBatch!.TotalAmount.Should().Be(1000m);
        dbSubaccount.Should().NotBeNull();
        dbSubaccount!.Balance.Should().Be(500m);
    }

    [Fact]
    public async Task RollbackTransactionAsync_ShouldDiscardChanges()
    {
        // Arrange
        await _unitOfWork.BeginTransactionAsync();

        var batch = new FundingBatch
        {
            BatchId = "BTH-TX-003",
            BatchNumber = "BATCH-TX-003",
            Status = "Open",
            CreatedBy = "TEST_USER"
        };
        await _context.FundingBatches.AddAsync(batch);
        await _context.SaveChangesAsync();

        // Act
        await _unitOfWork.RollbackTransactionAsync();

        // Assert - changes should be rolled back
        var dbBatch = await _context.FundingBatches.FindAsync("BTH-TX-003");
        dbBatch.Should().BeNull();
    }

    [Fact]
    public async Task CommitTransactionAsync_ShouldRollbackOnError()
    {
        // Arrange
        await _unitOfWork.BeginTransactionAsync();

        var batch = new FundingBatch
        {
            BatchId = "BTH-TX-004",
            BatchNumber = "BATCH-TX-004",
            Status = "Open",
            CreatedBy = "TEST_USER"
        };
        await _context.FundingBatches.AddAsync(batch);

        // Add duplicate batch (will cause SaveChanges to fail)
        var duplicateBatch = new FundingBatch
        {
            BatchId = "BTH-TX-004", // Same ID - violates PK constraint
            BatchNumber = "BATCH-TX-005",
            Status = "Open",
            CreatedBy = "TEST_USER"
        };
        await _context.FundingBatches.AddAsync(duplicateBatch);

        // Act & Assert
        await Assert.ThrowsAsync<InvalidOperationException>(async () =>
        {
            await _unitOfWork.CommitTransactionAsync();
        });

        // Verify rollback occurred
        var dbBatch = await _context.FundingBatches.FindAsync("BTH-TX-004");
        dbBatch.Should().BeNull();
    }

    [Fact]
    public async Task SaveChangesAsync_ShouldPersistChanges()
    {
        // Arrange
        var batch = new FundingBatch
        {
            BatchId = "BTH-SAVE-001",
            BatchNumber = "BATCH-SAVE-001",
            Status = "Open",
            CreatedBy = "TEST_USER"
        };
        await _context.FundingBatches.AddAsync(batch);

        // Act
        var result = await _unitOfWork.SaveChangesAsync();

        // Assert
        result.Should().Be(1); // One entity saved
        var dbBatch = await _context.FundingBatches.FindAsync("BTH-SAVE-001");
        dbBatch.Should().NotBeNull();
    }

    public void Dispose()
    {
        _unitOfWork.Dispose();
        _context.Database.CloseConnection();
        _context.Dispose();
    }
}
