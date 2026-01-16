using FluentAssertions;
using Microsoft.EntityFrameworkCore;
using PaymentProcessor.TransactionInvoices.Core.Entities;
using PaymentProcessor.TransactionInvoices.Infrastructure.Mock;
using PaymentProcessor.TransactionInvoices.Infrastructure.Persistence;
using PaymentProcessor.TransactionInvoices.Infrastructure.Validation;
using Xunit;

namespace PaymentProcessor.TransactionInvoices.IntegrationTests.SchemaValidation;

/// <summary>
/// Phase 5a - Foreign Key Integrity Tests.
/// Validates mock data foreign keys reference valid database records.
/// MANDATORY: All tests must pass before production deployment.
/// </summary>
public class ForeignKeyIntegrityTests : IDisposable
{
    private readonly TransactionInvoicesDbContext _dbContext;
    private readonly RelationshipValidator _validator;

    public ForeignKeyIntegrityTests()
    {
        var options = new DbContextOptionsBuilder<TransactionInvoicesDbContext>()
            .UseInMemoryDatabase(databaseName: $"TestDb_{Guid.NewGuid()}")
            .Options;

        _dbContext = new TransactionInvoicesDbContext(options);
        _validator = new RelationshipValidator(_dbContext);

        // Seed database with referenced entities
        SeedReferencedEntities();
    }

    [Fact]
    public async Task MockTransactionInvoice_BatchId_MustReferenceValidBatch()
    {
        // Arrange
        var mockRepository = new MockTransactionInvoiceRepository();
        var mockInvoice = await mockRepository.GetByIdAsync("MOCK-INVOICE-001");
        mockInvoice.Should().NotBeNull();

        // Act
        var batchExists = await _dbContext.TransactionBatches
            .AnyAsync(b => b.BatchId == mockInvoice!.BatchId);

        // Assert
        batchExists.Should().BeTrue(
            $"Invoice {mockInvoice!.InvoiceId} references BatchId {mockInvoice.BatchId} which must exist in TransactionBatches table");
    }

    [Fact]
    public async Task MockTransactionInvoice_AccountCategoryId_MustReferenceValidAccountCategory()
    {
        // Arrange
        var mockRepository = new MockTransactionInvoiceRepository();
        var mockInvoice = await mockRepository.GetByIdAsync("MOCK-INVOICE-001");
        mockInvoice.Should().NotBeNull();

        // Act
        var account_categoryExists = await _dbContext.AccountCategorys
            .AnyAsync(s => s.AccountCategoryId == mockInvoice!.AccountCategoryId);

        // Assert
        account_categoryExists.Should().BeTrue(
            $"Invoice {mockInvoice!.InvoiceId} references AccountCategoryId {mockInvoice.AccountCategoryId} which must exist in AccountCategorys table");
    }

    [Fact]
    public async Task AllMockTransactionInvoices_ForeignKeys_MustReferenceValidRecords()
    {
        // Arrange
        var mockRepository = new MockTransactionInvoiceRepository();
        var mockInvoices = await mockRepository.GetAllAsync();

        // Act
        var failures = new List<string>();

        foreach (var invoice in mockInvoices)
        {
            // Check BatchId FK
            var batchExists = await _dbContext.TransactionBatches
                .AnyAsync(b => b.BatchId == invoice.BatchId);
            if (!batchExists)
            {
                failures.Add($"Invoice {invoice.InvoiceId}: BatchId {invoice.BatchId} not found in TransactionBatches");
            }

            // Check AccountCategoryId FK
            var account_categoryExists = await _dbContext.AccountCategorys
                .AnyAsync(s => s.AccountCategoryId == invoice.AccountCategoryId);
            if (!account_categoryExists)
            {
                failures.Add($"Invoice {invoice.InvoiceId}: AccountCategoryId {invoice.AccountCategoryId} not found in AccountCategorys");
            }
        }

        // Assert
        failures.Should().BeEmpty(
            $"All foreign keys must reference valid records. Violations:\n{string.Join("\n", failures)}");
    }

    [Fact]
    public async Task AllMockCashInOut_InvoiceId_MustReferenceValidInvoice()
    {
        // Arrange
        var mockRepository = new MockCashInOutRepository();
        var mockCashTransactions = await mockRepository.GetAllAsync();

        // Act
        var failures = new List<string>();

        foreach (var cash in mockCashTransactions)
        {
            if (!string.IsNullOrEmpty(cash.InvoiceId))
            {
                var invoiceExists = await _dbContext.TransactionInvoices
                    .AnyAsync(i => i.InvoiceId == cash.InvoiceId);
                
                if (!invoiceExists)
                {
                    failures.Add($"CashInOut {cash.CashInOutId}: InvoiceId {cash.InvoiceId} not found in TransactionInvoices");
                }
            }
        }

        // Assert
        failures.Should().BeEmpty(
            $"All CashInOut records must reference valid invoices. Violations:\n{string.Join("\n", failures)}");
    }

    [Fact]
    public async Task RelationshipValidator_ValidateForeignKey_MustDetectInvalidReferences()
    {
        // Arrange - Use a BatchId that doesn't exist in seeded data
        var invalidBatchId = "INVALID-BATCH-999";

        // Act
        var result = await _validator.ValidateForeignKeyAsync<TransactionBatch, string>(
            "BatchId",
            invalidBatchId);

        // Assert
        result.Should().NotBeNull();
        result.IsValid.Should().BeFalse("Invalid foreign key should be detected");
        result.Errors.Should().NotBeEmpty("Validation should report FK not found");
    }

    [Fact]
    public async Task RelationshipValidator_ValidateForeignKey_MustAcceptValidReferences()
    {
        // Arrange - Use a BatchId that exists in seeded data
        var validBatchId = "MOCK-BATCH-001";

        // Act
        var result = await _validator.ValidateForeignKeyAsync<TransactionBatch, string>(
            "BatchId",
            validBatchId);

        // Assert
        result.Should().NotBeNull();
        result.IsValid.Should().BeTrue("Valid foreign key should pass validation");
        result.Errors.Should().BeEmpty("No errors for valid FK");
    }

    [Fact]
    public async Task RelationshipValidator_NullForeignKey_MustBeAllowedForNullableColumns()
    {
        // Arrange - Null FK value
        string? nullBatchId = null;

        // Act
        var result = await _validator.ValidateForeignKeyAsync<TransactionBatch, string?>(
            "OptionalBatchId",
            nullBatchId);

        // Assert
        result.Should().NotBeNull();
        result.IsValid.Should().BeTrue("Null FK should be allowed for nullable columns");
        result.Message.Should().Contain("null", "Message should acknowledge null FK");
    }

    /// <summary>
    /// Seeds the database with entities that mock data will reference.
    /// This simulates the production database state.
    /// </summary>
    private void SeedReferencedEntities()
    {
        // Seed TransactionBatches that mock invoices will reference
        _dbContext.TransactionBatches.AddRange(
            new TransactionBatch { BatchId = "MOCK-BATCH-001", BatchName = "Test Batch 1", CreatedDate = DateTime.UtcNow },
            new TransactionBatch { BatchId = "MOCK-BATCH-002", BatchName = "Test Batch 2", CreatedDate = DateTime.UtcNow },
            new TransactionBatch { BatchId = "MOCK-BATCH-003", BatchName = "Test Batch 3", CreatedDate = DateTime.UtcNow }
        );

        // Seed AccountCategorys that mock invoices will reference
        _dbContext.AccountCategorys.AddRange(
            new AccountCategory { AccountCategoryId = "MOCK-SUB-001", AccountCategoryName = "Test AccountCategory 1", CreatedDate = DateTime.UtcNow },
            new AccountCategory { AccountCategoryId = "MOCK-SUB-002", AccountCategoryName = "Test AccountCategory 2", CreatedDate = DateTime.UtcNow },
            new AccountCategory { AccountCategoryId = "MOCK-SUB-003", AccountCategoryName = "Test AccountCategory 3", CreatedDate = DateTime.UtcNow }
        );

        // Seed TransactionInvoices that CashInOut records will reference
        _dbContext.TransactionInvoices.AddRange(
            new TransactionInvoice 
            { 
                InvoiceId = "MOCK-INVOICE-001", 
                BatchId = "MOCK-BATCH-001", 
                AccountCategoryId = "MOCK-SUB-001",
                Amount = 1000.00m,
                CreatedDate = DateTime.UtcNow 
            },
            new TransactionInvoice 
            { 
                InvoiceId = "MOCK-INVOICE-002", 
                BatchId = "MOCK-BATCH-002", 
                AccountCategoryId = "MOCK-SUB-002",
                Amount = 2000.00m,
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
