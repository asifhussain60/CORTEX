using FluentAssertions;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging.Abstractions;
using PaymentProcessor.TransactionInvoices.Core.Entities;
using PaymentProcessor.TransactionInvoices.Infrastructure.Persistence;
using PaymentProcessor.TransactionInvoices.Infrastructure.Persistence.Repositories;
using Xunit;

namespace PaymentProcessor.TransactionInvoices.UnitTests.Persistence;

/// <summary>
/// Unit tests for EFCoreTransactionInvoiceRepository.
/// Uses SQLite in-memory database for isolated testing.
/// </summary>
public class EFCoreTransactionInvoiceRepositoryTests : IDisposable
{
    private readonly TransactionInvoicesDbContext _context;
    private readonly EFCoreTransactionInvoiceRepository _repository;

    public EFCoreTransactionInvoiceRepositoryTests()
    {
        var options = new DbContextOptionsBuilder<TransactionInvoicesDbContext>()
            .UseSqlite("DataSource=:memory:")
            .Options;

        _context = new TransactionInvoicesDbContext(options);
        _context.Database.OpenConnection();
        _context.Database.EnsureCreated();

        _repository = new EFCoreTransactionInvoiceRepository(_context);
    }

    [Fact]
    public async Task CreateAsync_ShouldAddInvoice_WhenValidInvoiceProvided()
    {
        // Arrange
        var batch = new TransactionBatch
        {
            BatchId = "BTH-001",
            BatchNumber = "BATCH-001",
            Status = "Open",
            CreatedBy = "TEST_USER"
        };
        var account_category = new AccountCategory
        {
            AccountCategoryId = "SUB-001",
            AccountNumber = "ACC-001",
            AccountType = "AccountTypeA",
            CustomerId = "MEM-001",
            CreatedBy = "TEST_USER"
        };
        await _context.TransactionBatches.AddAsync(batch);
        await _context.AccountCategorys.AddAsync(account_category);
        await _context.SaveChangesAsync();

        var invoice = new TransactionInvoice
        {
            InvoiceId = "INV-001",
            BatchId = "BTH-001",
            AccountCategoryId = "SUB-001",
            InvoiceNumber = "2024-001",
            Amount = 500.00m,
            Status = "Pending",
            CreatedBy = "TEST_USER"
        };

        // Act
        var result = await _repository.CreateAsync(invoice);

        // Assert
        result.Should().NotBeNull();
        result.InvoiceId.Should().Be("INV-001");
        var dbInvoice = await _context.TransactionInvoices.FindAsync("INV-001");
        dbInvoice.Should().NotBeNull();
        dbInvoice!.Amount.Should().Be(500.00m);
    }

    [Fact]
    public async Task GetByIdAsync_ShouldReturnInvoice_WhenInvoiceExists()
    {
        // Arrange
        var batch = new TransactionBatch
        {
            BatchId = "BTH-002",
            BatchNumber = "BATCH-002",
            Status = "Open",
            CreatedBy = "TEST_USER"
        };
        var account_category = new AccountCategory
        {
            AccountCategoryId = "SUB-002",
            AccountNumber = "ACC-002",
            AccountType = "AccountTypeB",
            CustomerId = "MEM-002",
            CreatedBy = "TEST_USER"
        };
        var invoice = new TransactionInvoice
        {
            InvoiceId = "INV-002",
            BatchId = "BTH-002",
            AccountCategoryId = "SUB-002",
            InvoiceNumber = "2024-002",
            Amount = 750.00m,
            Status = "Approved",
            CreatedBy = "TEST_USER"
        };
        await _context.TransactionBatches.AddAsync(batch);
        await _context.AccountCategorys.AddAsync(account_category);
        await _context.TransactionInvoices.AddAsync(invoice);
        await _context.SaveChangesAsync();

        // Act
        var result = await _repository.GetByIdAsync("INV-002");

        // Assert
        result.Should().NotBeNull();
        result!.InvoiceId.Should().Be("INV-002");
        result.Amount.Should().Be(750.00m);
        result.TransactionBatch.Should().NotBeNull();
        result.AccountCategory.Should().NotBeNull();
    }

    [Fact]
    public async Task GetByBatchIdAsync_ShouldReturnInvoices_WhenBatchHasInvoices()
    {
        // Arrange
        var batch = new TransactionBatch
        {
            BatchId = "BTH-003",
            BatchNumber = "BATCH-003",
            Status = "Open",
            CreatedBy = "TEST_USER"
        };
        var account_category = new AccountCategory
        {
            AccountCategoryId = "SUB-003",
            AccountNumber = "ACC-003",
            AccountType = "AccountTypeC",
            CustomerId = "MEM-003",
            CreatedBy = "TEST_USER"
        };
        await _context.TransactionBatches.AddAsync(batch);
        await _context.AccountCategorys.AddAsync(account_category);
        await _context.SaveChangesAsync();

        var invoices = new List<TransactionInvoice>
        {
            new() { InvoiceId = "INV-003", BatchId = "BTH-003", AccountCategoryId = "SUB-003", InvoiceNumber = "2024-003", Amount = 100m, Status = "Pending", CreatedBy = "TEST_USER" },
            new() { InvoiceId = "INV-004", BatchId = "BTH-003", AccountCategoryId = "SUB-003", InvoiceNumber = "2024-004", Amount = 200m, Status = "Pending", CreatedBy = "TEST_USER" }
        };
        await _context.TransactionInvoices.AddRangeAsync(invoices);
        await _context.SaveChangesAsync();

        // Act
        var result = await _repository.GetByBatchIdAsync("BTH-003");

        // Assert
        result.Should().NotBeNull();
        result.Should().HaveCount(2);
        result.Should().AllSatisfy(inv => inv.BatchId.Should().Be("BTH-003"));
    }

    [Fact]
    public async Task UpdateAsync_ShouldModifyInvoice_WhenInvoiceExists()
    {
        // Arrange
        var batch = new TransactionBatch
        {
            BatchId = "BTH-004",
            BatchNumber = "BATCH-004",
            Status = "Open",
            CreatedBy = "TEST_USER"
        };
        var account_category = new AccountCategory
        {
            AccountCategoryId = "SUB-004",
            AccountNumber = "ACC-004",
            AccountType = "AccountTypeA",
            CustomerId = "MEM-004",
            CreatedBy = "TEST_USER"
        };
        var invoice = new TransactionInvoice
        {
            InvoiceId = "INV-005",
            BatchId = "BTH-004",
            AccountCategoryId = "SUB-004",
            InvoiceNumber = "2024-005",
            Amount = 300m,
            Status = "Pending",
            CreatedBy = "TEST_USER"
        };
        await _context.TransactionBatches.AddAsync(batch);
        await _context.AccountCategorys.AddAsync(account_category);
        await _context.TransactionInvoices.AddAsync(invoice);
        await _context.SaveChangesAsync();

        // Act
        invoice.Status = "Approved";
        invoice.Amount = 350m;
        await _repository.UpdateAsync(invoice);

        // Assert
        var updated = await _context.TransactionInvoices.FindAsync("INV-005");
        updated.Should().NotBeNull();
        updated!.Status.Should().Be("Approved");
        updated.Amount.Should().Be(350m);
    }

    [Fact]
    public async Task DeleteAsync_ShouldRemoveInvoice_WhenInvoiceExists()
    {
        // Arrange
        var batch = new TransactionBatch
        {
            BatchId = "BTH-005",
            BatchNumber = "BATCH-005",
            Status = "Open",
            CreatedBy = "TEST_USER"
        };
        var account_category = new AccountCategory
        {
            AccountCategoryId = "SUB-005",
            AccountNumber = "ACC-005",
            AccountType = "AccountTypeB",
            CustomerId = "MEM-005",
            CreatedBy = "TEST_USER"
        };
        var invoice = new TransactionInvoice
        {
            InvoiceId = "INV-006",
            BatchId = "BTH-005",
            AccountCategoryId = "SUB-005",
            InvoiceNumber = "2024-006",
            Amount = 450m,
            Status = "Pending",
            CreatedBy = "TEST_USER"
        };
        await _context.TransactionBatches.AddAsync(batch);
        await _context.AccountCategorys.AddAsync(account_category);
        await _context.TransactionInvoices.AddAsync(invoice);
        await _context.SaveChangesAsync();

        // Act
        var result = await _repository.DeleteAsync("INV-006");

        // Assert
        result.Should().BeTrue();
        var deleted = await _context.TransactionInvoices.FindAsync("INV-006");
        deleted.Should().BeNull();
    }

    [Fact]
    public async Task DeleteAsync_ShouldReturnFalse_WhenInvoiceDoesNotExist()
    {
        // Act
        var result = await _repository.DeleteAsync("NON_EXISTENT");

        // Assert
        result.Should().BeFalse();
    }

    [Fact]
    public async Task ExistsAsync_ShouldReturnTrue_WhenInvoiceExists()
    {
        // Arrange
        var batch = new TransactionBatch
        {
            BatchId = "BTH-006",
            BatchNumber = "BATCH-006",
            Status = "Open",
            CreatedBy = "TEST_USER"
        };
        var account_category = new AccountCategory
        {
            AccountCategoryId = "SUB-006",
            AccountNumber = "ACC-006",
            AccountType = "AccountTypeC",
            CustomerId = "MEM-006",
            CreatedBy = "TEST_USER"
        };
        var invoice = new TransactionInvoice
        {
            InvoiceId = "INV-007",
            BatchId = "BTH-006",
            AccountCategoryId = "SUB-006",
            InvoiceNumber = "2024-007",
            Amount = 600m,
            Status = "Paid",
            CreatedBy = "TEST_USER"
        };
        await _context.TransactionBatches.AddAsync(batch);
        await _context.AccountCategorys.AddAsync(account_category);
        await _context.TransactionInvoices.AddAsync(invoice);
        await _context.SaveChangesAsync();

        // Act
        var result = await _repository.ExistsAsync("INV-007");

        // Assert
        result.Should().BeTrue();
    }

    public void Dispose()
    {
        _context.Database.CloseConnection();
        _context.Dispose();
    }
}
