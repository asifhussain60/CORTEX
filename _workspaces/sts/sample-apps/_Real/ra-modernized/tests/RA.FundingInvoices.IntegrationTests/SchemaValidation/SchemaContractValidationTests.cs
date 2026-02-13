using FluentAssertions;
using Microsoft.EntityFrameworkCore;
using RA.FundingInvoices.Core.Entities;
using RA.FundingInvoices.Infrastructure.Mock;
using RA.FundingInvoices.Infrastructure.Persistence;
using RA.FundingInvoices.Infrastructure.Validation;
using Xunit;

namespace RA.FundingInvoices.IntegrationTests.SchemaValidation;

/// <summary>
/// Phase 5a - Schema Contract Validation Tests.
/// Validates that mock entity properties exactly match database schema.
/// MANDATORY: All tests must pass before production deployment.
/// </summary>
public class SchemaContractValidationTests : IDisposable
{
    private readonly FundingInvoicesDbContext _dbContext;
    private readonly SchemaContractValidator _validator;
    private readonly MockDataSeeder _mockSeeder;

    public SchemaContractValidationTests()
    {
        // Use in-memory SQLite database for testing
        var options = new DbContextOptionsBuilder<FundingInvoicesDbContext>()
            .UseInMemoryDatabase(databaseName: $"TestDb_{Guid.NewGuid()}")
            .Options;

        _dbContext = new FundingInvoicesDbContext(options);
        _validator = new SchemaContractValidator();
        _mockSeeder = new MockDataSeeder();
        _mockSeeder.SeedData();
    }

    [Theory]
    [InlineData(typeof(FundingInvoice))]
    [InlineData(typeof(FundingBatch))]
    [InlineData(typeof(Subaccount))]
    [InlineData(typeof(CashInOut))]
    public void MockEntity_MustMatchDatabaseSchema(Type entityType)
    {
        // Arrange
        var dbEntityType = _dbContext.Model.FindEntityType(entityType);
        dbEntityType.Should().NotBeNull($"{entityType.Name} must be in database model");

        var mockInstance = GetSampleMockInstance(entityType);
        mockInstance.Should().NotBeNull($"Mock seeder must provide {entityType.Name} sample");

        // Act
        var result = _validator.ValidateContract(mockInstance!, dbEntityType!);

        // Assert
        result.Should().NotBeNull();
        result.IsValid.Should().BeTrue(
            $"{entityType.Name} mock must match DB schema exactly. " +
            $"Summary: {result.GetSummary()}");

        result.MissingProperties.Should().BeEmpty(
            $"All DB columns must exist in mock {entityType.Name}. " +
            $"Missing: {string.Join(", ", result.MissingProperties)}");

        result.ExtraProperties.Should().BeEmpty(
            $"No undocumented properties allowed in mock {entityType.Name}. " +
            $"Extra: {string.Join(", ", result.ExtraProperties)}");

        result.TypeMismatches.Should().BeEmpty(
            $"Property types must match exactly for {entityType.Name}. " +
            $"Mismatches: {string.Join(", ", result.TypeMismatches.Select(m => m.PropertyName))}");

        result.NullabilityMismatches.Should().BeEmpty(
            $"Nullability must match for {entityType.Name}. " +
            $"Mismatches: {string.Join(", ", result.NullabilityMismatches.Select(m => m.PropertyName))}");
    }

    [Fact]
    public async Task AllMockFundingInvoices_MustMatchDatabaseSchema()
    {
        // Arrange
        var mockRepository = new MockFundingInvoiceRepository();
        var dbEntityType = _dbContext.Model.FindEntityType(typeof(FundingInvoice));
        dbEntityType.Should().NotBeNull();

        // Act
        var mockInvoices = await mockRepository.GetAllAsync();
        var failures = new List<string>();

        foreach (var invoice in mockInvoices)
        {
            var result = _validator.ValidateContract(invoice, dbEntityType!);
            if (!result.IsValid)
            {
                failures.Add($"Invoice {invoice.InvoiceId}: {result.GetSummary()}");
            }
        }

        // Assert
        failures.Should().BeEmpty(
            $"All mock invoices must match DB schema. Failures:\n{string.Join("\n", failures)}");
    }

    [Fact]
    public async Task AllMockFundingBatches_MustMatchDatabaseSchema()
    {
        // Arrange
        var mockRepository = new MockFundingBatchRepository();
        var dbEntityType = _dbContext.Model.FindEntityType(typeof(FundingBatch));
        dbEntityType.Should().NotBeNull();

        // Act
        var mockBatches = await mockRepository.GetAllAsync();
        var failures = new List<string>();

        foreach (var batch in mockBatches)
        {
            var result = _validator.ValidateContract(batch, dbEntityType!);
            if (!result.IsValid)
            {
                failures.Add($"Batch {batch.BatchId}: {result.GetSummary()}");
            }
        }

        // Assert
        failures.Should().BeEmpty(
            $"All mock batches must match DB schema. Failures:\n{string.Join("\n", failures)}");
    }

    [Fact]
    public async Task AllMockSubaccounts_MustMatchDatabaseSchema()
    {
        // Arrange
        var mockRepository = new MockSubaccountRepository();
        var dbEntityType = _dbContext.Model.FindEntityType(typeof(Subaccount));
        dbEntityType.Should().NotBeNull();

        // Act
        var mockSubaccounts = await mockRepository.GetAllAsync();
        var failures = new List<string>();

        foreach (var subaccount in mockSubaccounts)
        {
            var result = _validator.ValidateContract(subaccount, dbEntityType!);
            if (!result.IsValid)
            {
                failures.Add($"Subaccount {subaccount.SubaccountId}: {result.GetSummary()}");
            }
        }

        // Assert
        failures.Should().BeEmpty(
            $"All mock subaccounts must match DB schema. Failures:\n{string.Join("\n", failures)}");
    }

    /// <summary>
    /// Helper method to get a sample mock instance for a given entity type.
    /// </summary>
    private object? GetSampleMockInstance(Type entityType)
    {
        if (entityType == typeof(FundingInvoice))
        {
            var repo = new MockFundingInvoiceRepository();
            return repo.GetByIdAsync("MOCK-INVOICE-001").Result;
        }
        else if (entityType == typeof(FundingBatch))
        {
            var repo = new MockFundingBatchRepository();
            return repo.GetByIdAsync("MOCK-BATCH-001").Result;
        }
        else if (entityType == typeof(Subaccount))
        {
            var repo = new MockSubaccountRepository();
            return repo.GetByIdAsync("MOCK-SUB-001").Result;
        }
        else if (entityType == typeof(CashInOut))
        {
            var repo = new MockCashInOutRepository();
            return repo.GetAllAsync().Result.FirstOrDefault();
        }

        return null;
    }

    public void Dispose()
    {
        _dbContext?.Dispose();
    }
}
