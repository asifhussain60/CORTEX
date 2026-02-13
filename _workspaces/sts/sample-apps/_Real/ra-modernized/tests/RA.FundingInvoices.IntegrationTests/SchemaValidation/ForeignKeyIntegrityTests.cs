using FluentAssertions;
using Microsoft.EntityFrameworkCore;
using RA.FundingInvoices.Core.Entities;
using RA.FundingInvoices.Infrastructure.Mock;
using RA.FundingInvoices.Infrastructure.Persistence;
using RA.FundingInvoices.Infrastructure.Validation;
using Xunit;

namespace RA.FundingInvoices.IntegrationTests.SchemaValidation;

/// <summary>
/// Phase 5a - Foreign Key Integrity Tests.
/// Validates mock data foreign keys reference valid database records.
/// MANDATORY: All tests must pass before production deployment.
/// </summary>
public class ForeignKeyIntegrityTests : IDisposable
{
    private readonly FundingInvoicesDbContext _dbContext;
    private readonly RelationshipValidator _validator;

    public ForeignKeyIntegrityTests()
    {
        var options = new DbContextOptionsBuilder<FundingInvoicesDbContext>()
            .UseInMemoryDatabase(databaseName: $"TestDb_{Guid.NewGuid()}")
            .Options;

        _dbContext = new FundingInvoicesDbContext(options);
        _validator = new RelationshipValidator(_dbContext);

        // Seed database with referenced entities
        SeedReferencedEntities();
    }

    [Fact]
    public async Task MockFundingInvoice_BatchId_MustReferenceValidBatch()
    {
        // Arrange
        var mockRepository = new MockFundingInvoiceRepository();
        var mockInvoice = await mockRepository.GetByIdAsync("MOCK-INVOICE-001");
        mockInvoice.Should().NotBeNull();

        // Act
        var batchExists = await _dbContext.FundingBatches
            .AnyAsync(b => b.BatchId == mockInvoice!.BatchId);

        // Assert
        batchExists.Should().BeTrue(
            $"Invoice {mockInvoice!.InvoiceId} references BatchId {mockInvoice.BatchId} which must exist in FundingBatches table");
    }

    [Fact]
    public async Task MockFundingInvoice_SubaccountId_MustReferenceValidSubaccount()
    {
        // Arrange
        var mockRepository = new MockFundingInvoiceRepository();
        var mockInvoice = await mockRepository.GetByIdAsync("MOCK-INVOICE-001");
        mockInvoice.Should().NotBeNull();

        // Act
        var subaccountExists = await _dbContext.Subaccounts
            .AnyAsync(s => s.SubaccountId == mockInvoice!.SubaccountId);

        // Assert
        subaccountExists.Should().BeTrue(
            $"Invoice {mockInvoice!.InvoiceId} references SubaccountId {mockInvoice.SubaccountId} which must exist in Subaccounts table");
    }

    [Fact]
    public async Task AllMockFundingInvoices_ForeignKeys_MustReferenceValidRecords()
    {
        // Arrange
        var mockRepository = new MockFundingInvoiceRepository();
        var mockInvoices = await mockRepository.GetAllAsync();

        // Act
        var failures = new List<string>();

        foreach (var invoice in mockInvoices)
        {
            // Check BatchId FK
            var batchExists = await _dbContext.FundingBatches
                .AnyAsync(b => b.BatchId == invoice.BatchId);
            if (!batchExists)
            {
                failures.Add($"Invoice {invoice.InvoiceId}: BatchId {invoice.BatchId} not found in FundingBatches");
            }

            // Check SubaccountId FK
            var subaccountExists = await _dbContext.Subaccounts
                .AnyAsync(s => s.SubaccountId == invoice.SubaccountId);
            if (!subaccountExists)
            {
                failures.Add($"Invoice {invoice.InvoiceId}: SubaccountId {invoice.SubaccountId} not found in Subaccounts");
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
                var invoiceExists = await _dbContext.FundingInvoices
                    .AnyAsync(i => i.InvoiceId == cash.InvoiceId);
                
                if (!invoiceExists)
                {
                    failures.Add($"CashInOut {cash.CashInOutId}: InvoiceId {cash.InvoiceId} not found in FundingInvoices");
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
        var result = await _validator.ValidateForeignKeyAsync<FundingBatch, string>(
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
        var result = await _validator.ValidateForeignKeyAsync<FundingBatch, string>(
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
        var result = await _validator.ValidateForeignKeyAsync<FundingBatch, string?>(
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
        // Seed FundingBatches that mock invoices will reference
        _dbContext.FundingBatches.AddRange(
            new FundingBatch { BatchId = "MOCK-BATCH-001", BatchName = "Test Batch 1", CreatedDate = DateTime.UtcNow },
            new FundingBatch { BatchId = "MOCK-BATCH-002", BatchName = "Test Batch 2", CreatedDate = DateTime.UtcNow },
            new FundingBatch { BatchId = "MOCK-BATCH-003", BatchName = "Test Batch 3", CreatedDate = DateTime.UtcNow }
        );

        // Seed Subaccounts that mock invoices will reference
        _dbContext.Subaccounts.AddRange(
            new Subaccount { SubaccountId = "MOCK-SUB-001", SubaccountName = "Test Subaccount 1", CreatedDate = DateTime.UtcNow },
            new Subaccount { SubaccountId = "MOCK-SUB-002", SubaccountName = "Test Subaccount 2", CreatedDate = DateTime.UtcNow },
            new Subaccount { SubaccountId = "MOCK-SUB-003", SubaccountName = "Test Subaccount 3", CreatedDate = DateTime.UtcNow }
        );

        // Seed FundingInvoices that CashInOut records will reference
        _dbContext.FundingInvoices.AddRange(
            new FundingInvoice 
            { 
                InvoiceId = "MOCK-INVOICE-001", 
                BatchId = "MOCK-BATCH-001", 
                SubaccountId = "MOCK-SUB-001",
                Amount = 1000.00m,
                CreatedDate = DateTime.UtcNow 
            },
            new FundingInvoice 
            { 
                InvoiceId = "MOCK-INVOICE-002", 
                BatchId = "MOCK-BATCH-002", 
                SubaccountId = "MOCK-SUB-002",
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
