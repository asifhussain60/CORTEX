using FluentAssertions;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using PaymentProcessor.TransactionInvoices.Core.Entities;
using PaymentProcessor.TransactionInvoices.Core.Interfaces;
using PaymentProcessor.TransactionInvoices.Infrastructure.Mock;
using PaymentProcessor.TransactionInvoices.Infrastructure.Persistence;
using PaymentProcessor.TransactionInvoices.Infrastructure.Persistence.Repositories;
using Xunit;

namespace PaymentProcessor.TransactionInvoices.IntegrationTests.SchemaValidation;

/// <summary>
/// Phase 5a - Integration Parity Tests.
/// Validates Mock and EF Core repositories return identical data.
/// MANDATORY: All tests must pass before production deployment.
/// </summary>
public class IntegrationParityTests : IDisposable
{
    private readonly TransactionInvoicesDbContext _dbContext;

    public IntegrationParityTests()
    {
        var options = new DbContextOptionsBuilder<TransactionInvoicesDbContext>()
            .UseInMemoryDatabase(databaseName: $"TestDb_{Guid.NewGuid()}")
            .Options;

        _dbContext = new TransactionInvoicesDbContext(options);
        
        // Seed EF Core context with same data as Mock repositories
        SeedDatabaseWithMockData();
    }

    [Theory]
    [InlineData("MOCK-INVOICE-001")]
    [InlineData("MOCK-INVOICE-002")]
    [InlineData("MOCK-INVOICE-003")]
    public async Task GetInvoiceById_MockVsEFCore_MustReturnIdenticalData(string invoiceId)
    {
        // Arrange
        var mockRepo = new MockTransactionInvoiceRepository();
        var efCoreRepo = new EFCoreTransactionInvoiceRepository(_dbContext);

        // Act
        var mockResult = await mockRepo.GetByIdAsync(invoiceId);
        var efResult = await efCoreRepo.GetByIdAsync(invoiceId);

        // Assert
        if (mockResult == null && efResult == null)
        {
            // Both null - acceptable
            return;
        }

        mockResult.Should().NotBeNull($"Mock repository should return invoice {invoiceId}");
        efResult.Should().NotBeNull($"EF Core repository should return invoice {invoiceId}");

        // Compare properties (exclude navigation properties and timestamps)
        mockResult!.InvoiceId.Should().Be(efResult!.InvoiceId);
        mockResult.BatchId.Should().Be(efResult.BatchId);
        mockResult.AccountCategoryId.Should().Be(efResult.AccountCategoryId);
        mockResult.Amount.Should().Be(efResult.Amount);
        mockResult.Status.Should().Be(efResult.Status);
    }

    [Fact]
    public async Task GetAllInvoices_MockVsEFCore_MustReturnSameCount()
    {
        // Arrange
        var mockRepo = new MockTransactionInvoiceRepository();
        var efCoreRepo = new EFCoreTransactionInvoiceRepository(_dbContext);

        // Act
        var mockResults = await mockRepo.GetAllAsync();
        var efResults = await efCoreRepo.GetAllAsync();

        // Assert
        mockResults.Should().HaveCount(efResults.Count, 
            "Mock and EF Core repositories must return same number of invoices");
    }

    [Theory]
    [InlineData("MOCK-BATCH-001")]
    [InlineData("MOCK-BATCH-002")]
    public async Task GetBatchById_MockVsEFCore_MustReturnIdenticalData(string batchId)
    {
        // Arrange
        var mockRepo = new MockTransactionBatchRepository();
        var efCoreRepo = new EFCoreTransactionBatchRepository(_dbContext);

        // Act
        var mockResult = await mockRepo.GetByIdAsync(batchId);
        var efResult = await efCoreRepo.GetByIdAsync(batchId);

        // Assert
        if (mockResult == null && efResult == null)
        {
            return;
        }

        mockResult.Should().NotBeNull($"Mock repository should return batch {batchId}");
        efResult.Should().NotBeNull($"EF Core repository should return batch {batchId}");

        mockResult!.BatchId.Should().Be(efResult!.BatchId);
        mockResult.BatchName.Should().Be(efResult.BatchName);
        mockResult.Status.Should().Be(efResult.Status);
    }

    [Theory]
    [InlineData("MOCK-SUB-001")]
    [InlineData("MOCK-SUB-002")]
    public async Task GetAccountCategoryById_MockVsEFCore_MustReturnIdenticalData(string account_categoryId)
    {
        // Arrange
        var mockRepo = new MockAccountCategoryRepository();
        var efCoreRepo = new EFCoreAccountCategoryRepository(_dbContext);

        // Act
        var mockResult = await mockRepo.GetByIdAsync(account_categoryId);
        var efResult = await efCoreRepo.GetByIdAsync(account_categoryId);

        // Assert
        if (mockResult == null && efResult == null)
        {
            return;
        }

        mockResult.Should().NotBeNull($"Mock repository should return account_category {account_categoryId}");
        efResult.Should().NotBeNull($"EF Core repository should return account_category {account_categoryId}");

        mockResult!.AccountCategoryId.Should().Be(efResult!.AccountCategoryId);
        mockResult.AccountCategoryName.Should().Be(efResult.AccountCategoryName);
        mockResult.Balance.Should().Be(efResult.Balance);
    }

    [Fact]
    public async Task CreateInvoice_MockVsEFCore_MustBehaveSimilarly()
    {
        // Arrange
        var mockRepo = new MockTransactionInvoiceRepository();
        var efCoreRepo = new EFCoreTransactionInvoiceRepository(_dbContext);

        var newInvoice = new TransactionInvoice
        {
            InvoiceId = "TEST-INVOICE-NEW",
            BatchId = "MOCK-BATCH-001",
            AccountCategoryId = "MOCK-SUB-001",
            Amount = 5000.00m,
            Status = "Pending",
            CreatedDate = DateTime.UtcNow
        };

        // Act
        await mockRepo.AddAsync(newInvoice);
        
        var efInvoice = new TransactionInvoice
        {
            InvoiceId = "TEST-INVOICE-EF",
            BatchId = "MOCK-BATCH-001",
            AccountCategoryId = "MOCK-SUB-001",
            Amount = 5000.00m,
            Status = "Pending",
            CreatedDate = DateTime.UtcNow
        };
        await efCoreRepo.AddAsync(efInvoice);
        await _dbContext.SaveChangesAsync();

        // Assert - Verify both created successfully
        var mockRetrieved = await mockRepo.GetByIdAsync("TEST-INVOICE-NEW");
        var efRetrieved = await efCoreRepo.GetByIdAsync("TEST-INVOICE-EF");

        mockRetrieved.Should().NotBeNull("Mock repository should persist new invoice");
        efRetrieved.Should().NotBeNull("EF Core repository should persist new invoice");
        mockRetrieved!.Amount.Should().Be(efRetrieved!.Amount);
    }

    [Fact]
    public async Task UpdateInvoice_MockVsEFCore_MustBehaveSimilarly()
    {
        // Arrange
        var mockRepo = new MockTransactionInvoiceRepository();
        var efCoreRepo = new EFCoreTransactionInvoiceRepository(_dbContext);

        var mockInvoice = await mockRepo.GetByIdAsync("MOCK-INVOICE-001");
        var efInvoice = await efCoreRepo.GetByIdAsync("MOCK-INVOICE-001");

        mockInvoice.Should().NotBeNull();
        efInvoice.Should().NotBeNull();

        // Act - Update status
        mockInvoice!.Status = "Approved";
        efInvoice!.Status = "Approved";

        await mockRepo.UpdateAsync(mockInvoice);
        await efCoreRepo.UpdateAsync(efInvoice);
        await _dbContext.SaveChangesAsync();

        // Assert
        var mockUpdated = await mockRepo.GetByIdAsync("MOCK-INVOICE-001");
        var efUpdated = await efCoreRepo.GetByIdAsync("MOCK-INVOICE-001");

        mockUpdated!.Status.Should().Be("Approved");
        efUpdated!.Status.Should().Be("Approved");
    }

    [Fact]
    public async Task DeleteInvoice_MockVsEFCore_MustBehaveSimilarly()
    {
        // Arrange
        var mockRepo = new MockTransactionInvoiceRepository();
        var efCoreRepo = new EFCoreTransactionInvoiceRepository(_dbContext);

        // Create test invoices for deletion
        var mockInvoice = new TransactionInvoice
        {
            InvoiceId = "DELETE-MOCK",
            BatchId = "MOCK-BATCH-001",
            AccountCategoryId = "MOCK-SUB-001",
            Amount = 100.00m,
            Status = "Pending",
            CreatedDate = DateTime.UtcNow
        };
        await mockRepo.AddAsync(mockInvoice);

        var efInvoice = new TransactionInvoice
        {
            InvoiceId = "DELETE-EF",
            BatchId = "MOCK-BATCH-001",
            AccountCategoryId = "MOCK-SUB-001",
            Amount = 100.00m,
            Status = "Pending",
            CreatedDate = DateTime.UtcNow
        };
        await efCoreRepo.AddAsync(efInvoice);
        await _dbContext.SaveChangesAsync();

        // Act - Delete
        await mockRepo.DeleteAsync("DELETE-MOCK");
        await efCoreRepo.DeleteAsync("DELETE-EF");
        await _dbContext.SaveChangesAsync();

        // Assert
        var mockDeleted = await mockRepo.GetByIdAsync("DELETE-MOCK");
        var efDeleted = await efCoreRepo.GetByIdAsync("DELETE-EF");

        mockDeleted.Should().BeNull("Mock repository should delete invoice");
        efDeleted.Should().BeNull("EF Core repository should delete invoice");
    }

    /// <summary>
    /// Seeds the database with same data as Mock repositories to enable comparison.
    /// </summary>
    private void SeedDatabaseWithMockData()
    {
        // Seed batches
        _dbContext.TransactionBatches.AddRange(
            new TransactionBatch { BatchId = "MOCK-BATCH-001", BatchName = "Test Batch 1", Status = "Active", CreatedDate = DateTime.UtcNow },
            new TransactionBatch { BatchId = "MOCK-BATCH-002", BatchName = "Test Batch 2", Status = "Active", CreatedDate = DateTime.UtcNow },
            new TransactionBatch { BatchId = "MOCK-BATCH-003", BatchName = "Test Batch 3", Status = "Active", CreatedDate = DateTime.UtcNow }
        );

        // Seed account_categorys
        _dbContext.AccountCategorys.AddRange(
            new AccountCategory { AccountCategoryId = "MOCK-SUB-001", AccountCategoryName = "Test AccountCategory 1", Balance = 10000.00m, CreatedDate = DateTime.UtcNow },
            new AccountCategory { AccountCategoryId = "MOCK-SUB-002", AccountCategoryName = "Test AccountCategory 2", Balance = 20000.00m, CreatedDate = DateTime.UtcNow },
            new AccountCategory { AccountCategoryId = "MOCK-SUB-003", AccountCategoryName = "Test AccountCategory 3", Balance = 30000.00m, CreatedDate = DateTime.UtcNow }
        );

        // Seed invoices
        _dbContext.TransactionInvoices.AddRange(
            new TransactionInvoice 
            { 
                InvoiceId = "MOCK-INVOICE-001", 
                BatchId = "MOCK-BATCH-001", 
                AccountCategoryId = "MOCK-SUB-001",
                Amount = 1000.00m,
                Status = "Pending",
                CreatedDate = DateTime.UtcNow 
            },
            new TransactionInvoice 
            { 
                InvoiceId = "MOCK-INVOICE-002", 
                BatchId = "MOCK-BATCH-002", 
                AccountCategoryId = "MOCK-SUB-002",
                Amount = 2000.00m,
                Status = "Pending",
                CreatedDate = DateTime.UtcNow 
            },
            new TransactionInvoice 
            { 
                InvoiceId = "MOCK-INVOICE-003", 
                BatchId = "MOCK-BATCH-003", 
                AccountCategoryId = "MOCK-SUB-003",
                Amount = 3000.00m,
                Status = "Pending",
                CreatedDate = DateTime.UtcNow 
            }
        );

        _dbContext.SaveChanges();
    }

    public void Dispose()
    {
        _dbContext?.Dispose();
    }
}
