using FluentAssertions;
using Microsoft.EntityFrameworkCore;
using PaymentProcessor.TransactionInvoices.Core.Entities;
using PaymentProcessor.TransactionInvoices.Infrastructure.EFCore;
using PaymentProcessor.TransactionInvoices.Infrastructure.EFCore.Repositories;
using Xunit;

namespace PaymentProcessor.TransactionInvoices.UnitTests.Repositories.EFCore;

/// <summary>
/// Unit tests for EFCoreTransactionInvoiceRepository using in-memory database.
/// Validates CRUD operations, complex queries, and relationship handling.
/// </summary>
public class EFCoreTransactionInvoiceRepositoryTests : IDisposable
{
    private readonly TransactionInvoicesDbContext _context;
    private readonly EFCoreTransactionInvoiceRepository _repository;

    public EFCoreTransactionInvoiceRepositoryTests()
    {
        // Use in-memory SQLite database for testing
        var options = new DbContextOptionsBuilder<TransactionInvoicesDbContext>()
            .UseInMemoryDatabase(databaseName: $"TestDb_{Guid.NewGuid()}")
            .Options;

        _context = new TransactionInvoicesDbContext(options);
        _repository = new EFCoreTransactionInvoiceRepository(_context);

        // Seed test data
        SeedTestData();
    }

    private void SeedTestData()
    {
        // Create test batch
        var batch = new TransactionBatch
        {
            BatchId = "BATCH-001",
            BatchNumber = "BN-001",
            Status = "Open",
            BatchDate = DateTime.UtcNow,
            TotalAmount = 1000m,
            InvoiceCount = 2,
            CreatedBy = "Test"
        };
        _context.TransactionBatches.Add(batch);

        // Create test account_category
        var account_category = new AccountCategory
        {
            AccountCategoryId = "SUB-001",
            AccountNumber = "ACC-001",
            AccountType = "AccountTypeA",
            CustomerId = "MEM-001",
            Balance = 5000m,
            Status = "Active",
            OpenedDate = DateTime.UtcNow,
            CreatedBy = "Test"
        };
        _context.AccountCategorys.Add(account_category);

        // Create test invoices
        var invoice1 = new TransactionInvoice
        {
            InvoiceId = "INV-001",
            BatchId = "BATCH-001",
            AccountCategoryId = "SUB-001",
            InvoiceNumber = "FI-001",
            Amount = 500m,
            Status = "Pending",
            InvoiceDate = DateTime.UtcNow.AddDays(-1),
            CreatedBy = "Test"
        };

        var invoice2 = new TransactionInvoice
        {
            InvoiceId = "INV-002",
            BatchId = "BATCH-001",
            AccountCategoryId = "SUB-001",
            InvoiceNumber = "FI-002",
            Amount = 500m,
            Status = "Approved",
            InvoiceDate = DateTime.UtcNow,
            CreatedBy = "Test"
        };

        _context.TransactionInvoices.AddRange(invoice1, invoice2);
        _context.SaveChanges();
    }

    [Fact]
    public async Task GetByIdAsync_WhenInvoiceExists_ReturnsInvoice()
    {
        // Act
        var result = await _repository.GetByIdAsync("INV-001");

        // Assert
        result.Should().NotBeNull();
        result!.InvoiceId.Should().Be("INV-001");
        result.Amount.Should().Be(500m);
        result.Status.Should().Be("Pending");
    }

    [Fact]
    public async Task GetByIdAsync_WhenInvoiceDoesNotExist_ReturnsNull()
    {
        // Act
        var result = await _repository.GetByIdAsync("NONEXISTENT");

        // Assert
        result.Should().BeNull();
    }

    [Fact]
    public async Task GetByIdAsync_IncludesNavigationProperties()
    {
        // Act
        var result = await _repository.GetByIdAsync("INV-001");

        // Assert
        result.Should().NotBeNull();
        result!.TransactionBatch.Should().NotBeNull();
        result.TransactionBatch!.BatchId.Should().Be("BATCH-001");
        result.AccountCategory.Should().NotBeNull();
        result.AccountCategory!.AccountCategoryId.Should().Be("SUB-001");
    }

    [Fact]
    public async Task GetAllAsync_ReturnsAllInvoices()
    {
        // Act
        var result = await _repository.GetAllAsync();

        // Assert
        result.Should().HaveCount(2);
        result.Should().Contain(i => i.InvoiceId == "INV-001");
        result.Should().Contain(i => i.InvoiceId == "INV-002");
    }

    [Fact]
    public async Task GetByBatchIdAsync_ReturnsInvoicesInBatch()
    {
        // Act
        var result = await _repository.GetByBatchIdAsync("BATCH-001");

        // Assert
        result.Should().HaveCount(2);
        result.Should().OnlyContain(i => i.BatchId == "BATCH-001");
    }

    [Fact]
    public async Task GetByAccountCategoryIdAsync_ReturnsInvoicesForAccountCategory()
    {
        // Act
        var result = await _repository.GetByAccountCategoryIdAsync("SUB-001");

        // Assert
        result.Should().HaveCount(2);
        result.Should().OnlyContain(i => i.AccountCategoryId == "SUB-001");
    }

    [Fact]
    public async Task GetByDateRangeAsync_ReturnsInvoicesWithinRange()
    {
        // Arrange
        var startDate = DateTime.UtcNow.AddDays(-2);
        var endDate = DateTime.UtcNow.AddDays(1);

        // Act
        var result = await _repository.GetByDateRangeAsync(startDate, endDate);

        // Assert
        result.Should().HaveCount(2);
    }

    [Fact]
    public async Task CreateAsync_AddsNewInvoice()
    {
        // Arrange
        var newInvoice = new TransactionInvoice
        {
            BatchId = "BATCH-001",
            AccountCategoryId = "SUB-001",
            InvoiceNumber = "FI-003",
            Amount = 750m,
            Status = "Pending",
            InvoiceDate = DateTime.UtcNow,
            CreatedBy = "Test"
        };

        // Act
        var result = await _repository.CreateAsync(newInvoice);

        // Assert
        result.Should().NotBeNull();
        result.InvoiceId.Should().NotBeNullOrEmpty();
        result.Amount.Should().Be(750m);

        // Verify persistence
        var saved = await _repository.GetByIdAsync(result.InvoiceId);
        saved.Should().NotBeNull();
        saved!.Amount.Should().Be(750m);
    }

    [Fact]
    public async Task UpdateAsync_ModifiesExistingInvoice()
    {
        // Arrange
        var invoice = await _repository.GetByIdAsync("INV-001");
        invoice!.Amount = 600m;
        invoice.Status = "Approved";

        // Act
        var result = await _repository.UpdateAsync(invoice);

        // Assert
        result.Should().NotBeNull();
        result.Amount.Should().Be(600m);
        result.Status.Should().Be("Approved");

        // Verify persistence
        var updated = await _repository.GetByIdAsync("INV-001");
        updated!.Amount.Should().Be(600m);
        updated.Status.Should().Be("Approved");
    }

    [Fact]
    public async Task UpdateAsync_WhenInvoiceDoesNotExist_ThrowsException()
    {
        // Arrange
        var nonExistentInvoice = new TransactionInvoice
        {
            InvoiceId = "NONEXISTENT",
            BatchId = "BATCH-001",
            AccountCategoryId = "SUB-001",
            Amount = 100m,
            CreatedBy = "Test"
        };

        // Act & Assert
        await Assert.ThrowsAsync<InvalidOperationException>(
            async () => await _repository.UpdateAsync(nonExistentInvoice));
    }

    [Fact]
    public async Task DeleteAsync_RemovesInvoice()
    {
        // Act
        var result = await _repository.DeleteAsync("INV-001");

        // Assert
        result.Should().BeTrue();

        // Verify deletion
        var deleted = await _repository.GetByIdAsync("INV-001");
        deleted.Should().BeNull();
    }

    [Fact]
    public async Task DeleteAsync_WhenInvoiceDoesNotExist_ReturnsFalse()
    {
        // Act
        var result = await _repository.DeleteAsync("NONEXISTENT");

        // Assert
        result.Should().BeFalse();
    }

    [Fact]
    public async Task ExistsAsync_WhenInvoiceExists_ReturnsTrue()
    {
        // Act
        var result = await _repository.ExistsAsync("INV-001");

        // Assert
        result.Should().BeTrue();
    }

    [Fact]
    public async Task ExistsAsync_WhenInvoiceDoesNotExist_ReturnsFalse()
    {
        // Act
        var result = await _repository.ExistsAsync("NONEXISTENT");

        // Assert
        result.Should().BeFalse();
    }

    public void Dispose()
    {
        _context.Database.EnsureDeleted();
        _context.Dispose();
    }
}
