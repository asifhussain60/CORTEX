using FluentAssertions;
using Microsoft.EntityFrameworkCore;
using PaymentProcessor.TransactionInvoices.Core.Entities;
using PaymentProcessor.TransactionInvoices.Infrastructure.Mock;
using PaymentProcessor.TransactionInvoices.Infrastructure.Persistence;
using PaymentProcessor.TransactionInvoices.Infrastructure.Validation;
using Xunit;

namespace PaymentProcessor.TransactionInvoices.IntegrationTests.SchemaValidation;

/// <summary>
/// Phase 5a - Schema Contract Validation Tests.
/// Validates that mock entity properties exactly match database schema.
/// MANDATORY: All tests must pass before production deployment.
/// </summary>
public class SchemaContractValidationTests : IDisposable
{
    private readonly TransactionInvoicesDbContext _dbContext;
    private readonly SchemaContractValidator _validator;
    private readonly MockDataSeeder _mockSeeder;

    public SchemaContractValidationTests()
    {
        // Use in-memory SQLite database for testing
        var options = new DbContextOptionsBuilder<TransactionInvoicesDbContext>()
            .UseInMemoryDatabase(databaseName: $"TestDb_{Guid.NewGuid()}")
            .Options;

        _dbContext = new TransactionInvoicesDbContext(options);
        _validator = new SchemaContractValidator();
        _mockSeeder = new MockDataSeeder();
        _mockSeeder.SeedData();
    }

    [Theory]
    [InlineData(typeof(TransactionInvoice))]
    [InlineData(typeof(TransactionBatch))]
    [InlineData(typeof(AccountCategory))]
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
    public async Task AllMockTransactionInvoices_MustMatchDatabaseSchema()
    {
        // Arrange
        var mockRepository = new MockTransactionInvoiceRepository();
        var dbEntityType = _dbContext.Model.FindEntityType(typeof(TransactionInvoice));
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
    public async Task AllMockTransactionBatches_MustMatchDatabaseSchema()
    {
        // Arrange
        var mockRepository = new MockTransactionBatchRepository();
        var dbEntityType = _dbContext.Model.FindEntityType(typeof(TransactionBatch));
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
    public async Task AllMockAccountCategorys_MustMatchDatabaseSchema()
    {
        // Arrange
        var mockRepository = new MockAccountCategoryRepository();
        var dbEntityType = _dbContext.Model.FindEntityType(typeof(AccountCategory));
        dbEntityType.Should().NotBeNull();

        // Act
        var mockAccountCategorys = await mockRepository.GetAllAsync();
        var failures = new List<string>();

        foreach (var account_category in mockAccountCategorys)
        {
            var result = _validator.ValidateContract(account_category, dbEntityType!);
            if (!result.IsValid)
            {
                failures.Add($"AccountCategory {account_category.AccountCategoryId}: {result.GetSummary()}");
            }
        }

        // Assert
        failures.Should().BeEmpty(
            $"All mock account_categorys must match DB schema. Failures:\n{string.Join("\n", failures)}");
    }

    /// <summary>
    /// Helper method to get a sample mock instance for a given entity type.
    /// </summary>
    private object? GetSampleMockInstance(Type entityType)
    {
        if (entityType == typeof(TransactionInvoice))
        {
            var repo = new MockTransactionInvoiceRepository();
            return repo.GetByIdAsync("MOCK-INVOICE-001").Result;
        }
        else if (entityType == typeof(TransactionBatch))
        {
            var repo = new MockTransactionBatchRepository();
            return repo.GetByIdAsync("MOCK-BATCH-001").Result;
        }
        else if (entityType == typeof(AccountCategory))
        {
            var repo = new MockAccountCategoryRepository();
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
