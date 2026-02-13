using FluentAssertions;
using Microsoft.EntityFrameworkCore;
using RA.FundingInvoices.Core.Entities;
using RA.FundingInvoices.Infrastructure.Mock;
using RA.FundingInvoices.Infrastructure.Persistence;
using RA.FundingInvoices.Infrastructure.Validation;
using Xunit;

namespace RA.FundingInvoices.IntegrationTests.SchemaValidation;

/// <summary>
/// Phase 5a - Type Safety Validation Tests.
/// Validates decimal precision, string lengths, date formats match DB constraints.
/// MANDATORY: All tests must pass before production deployment.
/// </summary>
public class TypeSafetyValidationTests : IDisposable
{
    private readonly FundingInvoicesDbContext _dbContext;
    private readonly TypeSafetyValidator _validator;
    private readonly MockFundingInvoiceRepository _mockRepository;

    public TypeSafetyValidationTests()
    {
        var options = new DbContextOptionsBuilder<FundingInvoicesDbContext>()
            .UseInMemoryDatabase(databaseName: $"TestDb_{Guid.NewGuid()}")
            .Options;

        _dbContext = new FundingInvoicesDbContext(options);
        _validator = new TypeSafetyValidator();
        _mockRepository = new MockFundingInvoiceRepository();
    }

    [Fact]
    public async Task MockFundingInvoice_DecimalPrecision_MustMatchDatabase()
    {
        // Arrange
        var mockInvoice = await _mockRepository.GetByIdAsync("MOCK-INVOICE-001");
        mockInvoice.Should().NotBeNull();

        var dbEntityType = _dbContext.Model.FindEntityType(typeof(FundingInvoice));
        var amountProperty = dbEntityType?.FindProperty(nameof(FundingInvoice.Amount));
        amountProperty.Should().NotBeNull("Amount property must exist in database model");

        // Act
        var result = _validator.ValidateDecimalPrecision(
            mockInvoice!.Amount,
            amountProperty!,
            nameof(FundingInvoice.Amount));

        // Assert
        result.IsValid.Should().BeTrue(
            $"Amount {mockInvoice.Amount} must fit database DECIMAL precision. " +
            $"Errors: {string.Join(", ", result.Errors)}");
    }

    [Fact]
    public async Task AllMockFundingInvoices_DecimalFields_MustFitDatabaseConstraints()
    {
        // Arrange
        var mockInvoices = await _mockRepository.GetAllAsync();
        var dbEntityType = _dbContext.Model.FindEntityType(typeof(FundingInvoice));
        
        var decimalProperties = dbEntityType?.GetProperties()
            .Where(p => p.ClrType == typeof(decimal) || p.ClrType == typeof(decimal?))
            .ToList();

        decimalProperties.Should().NotBeNullOrEmpty("Database should have decimal properties");

        // Act
        var failures = new List<string>();

        foreach (var invoice in mockInvoices)
        {
            foreach (var property in decimalProperties!)
            {
                var propertyInfo = typeof(FundingInvoice).GetProperty(property.Name);
                var value = propertyInfo?.GetValue(invoice) as decimal?;

                if (value.HasValue)
                {
                    var result = _validator.ValidateDecimalPrecision(
                        value.Value,
                        property,
                        property.Name);

                    if (!result.IsValid)
                    {
                        failures.Add($"Invoice {invoice.InvoiceId}.{property.Name}: {string.Join(", ", result.Errors)}");
                    }
                }
            }
        }

        // Assert
        failures.Should().BeEmpty(
            $"All decimal values must fit database constraints. Failures:\n{string.Join("\n", failures)}");
    }

    [Fact]
    public async Task MockFundingInvoice_StringFields_MustNotExceedMaxLength()
    {
        // Arrange
        var mockInvoices = await _mockRepository.GetAllAsync();
        var dbEntityType = _dbContext.Model.FindEntityType(typeof(FundingInvoice));
        
        var stringProperties = dbEntityType?.GetProperties()
            .Where(p => p.ClrType == typeof(string))
            .ToList();

        // Act
        var failures = new List<string>();

        foreach (var invoice in mockInvoices)
        {
            foreach (var property in stringProperties!)
            {
                var propertyInfo = typeof(FundingInvoice).GetProperty(property.Name);
                var value = propertyInfo?.GetValue(invoice) as string;

                var result = _validator.ValidateStringLength(
                    value,
                    property,
                    property.Name);

                if (!result.IsValid)
                {
                    failures.Add($"Invoice {invoice.InvoiceId}.{property.Name}: {string.Join(", ", result.Errors)}");
                }
            }
        }

        // Assert
        failures.Should().BeEmpty(
            $"All string values must fit VARCHAR/NVARCHAR constraints. Failures:\n{string.Join("\n", failures)}");
    }

    [Fact]
    public async Task MockFundingInvoice_DateTimeFields_MustBeWithinSqlServerRange()
    {
        // Arrange
        var mockInvoices = await _mockRepository.GetAllAsync();
        var dbEntityType = _dbContext.Model.FindEntityType(typeof(FundingInvoice));
        
        var dateTimeProperties = dbEntityType?.GetProperties()
            .Where(p => p.ClrType == typeof(DateTime) || p.ClrType == typeof(DateTime?))
            .ToList();

        // Act
        var failures = new List<string>();

        foreach (var invoice in mockInvoices)
        {
            foreach (var property in dateTimeProperties!)
            {
                var propertyInfo = typeof(FundingInvoice).GetProperty(property.Name);
                var value = propertyInfo?.GetValue(invoice) as DateTime?;

                if (value.HasValue)
                {
                    var result = _validator.ValidateDateTimeRange(
                        value.Value,
                        property,
                        property.Name);

                    if (!result.IsValid)
                    {
                        failures.Add($"Invoice {invoice.InvoiceId}.{property.Name}: {string.Join(", ", result.Errors)}");
                    }
                }
            }
        }

        // Assert
        failures.Should().BeEmpty(
            $"All DateTime values must be within SQL Server range. Failures:\n{string.Join("\n", failures)}");
    }

    [Theory]
    [InlineData(123.45, 18, 2, true)]  // Valid: fits DECIMAL(18,2)
    [InlineData(9999999999999999.99, 18, 2, true)]  // Valid: max for DECIMAL(18,2)
    [InlineData(123.456, 18, 2, false)]  // Invalid: too many decimal places
    public void DecimalPrecisionValidator_MustEnforceConstraints(
        decimal value,
        int precision,
        int scale,
        bool shouldBeValid)
    {
        // Arrange
        var mockProperty = new MockDecimalProperty { Precision = precision, Scale = scale };

        // Act
        var result = _validator.ValidateDecimalPrecision(value, mockProperty, "TestProperty");

        // Assert
        result.IsValid.Should().Be(shouldBeValid,
            $"DECIMAL({precision},{scale}) validation for {value} should be {shouldBeValid}");
    }

    public void Dispose()
    {
        _dbContext?.Dispose();
    }

    /// <summary>
    /// Mock property for testing decimal precision validation.
    /// </summary>
    private class MockDecimalProperty : Microsoft.EntityFrameworkCore.Metadata.IProperty
    {
        public int? Precision { get; set; }
        public int? Scale { get; set; }

        // Implement required IProperty members (minimal for testing)
        public string Name => "TestProperty";
        public Microsoft.EntityFrameworkCore.Metadata.ITypeBase DeclaringType => throw new NotImplementedException();
        public Type ClrType => typeof(decimal);
        public Microsoft.EntityFrameworkCore.Metadata.IEntityType? DeclaringEntityType => throw new NotImplementedException();
        public Microsoft.EntityFrameworkCore.ChangeTracking.ValueComparer? GetValueComparer() => null;
        public Microsoft.EntityFrameworkCore.ChangeTracking.ValueComparer? GetKeyValueComparer() => null;
        public object? Sentinel => null;
        public bool IsNullable => false;
        public Microsoft.EntityFrameworkCore.Metadata.PropertySaveBehavior GetBeforeSaveBehavior() => 
            Microsoft.EntityFrameworkCore.Metadata.PropertySaveBehavior.Save;
        public Microsoft.EntityFrameworkCore.Metadata.PropertySaveBehavior GetAfterSaveBehavior() => 
            Microsoft.EntityFrameworkCore.Metadata.PropertySaveBehavior.Save;
        public Microsoft.EntityFrameworkCore.ValueGeneration.ValueGenerated ValueGenerated => 
            Microsoft.EntityFramework.Core.ValueGeneration.ValueGenerated.Never;
        public bool IsConcurrencyToken => false;
        public bool IsKey() => false;
        public bool IsPrimaryKey() => false;
        public bool IsForeignKey() => false;
        public bool IsIndex() => false;
        public bool IsShadowProperty() => false;
        public Microsoft.EntityFrameworkCore.Metadata.PropertyAccessMode GetPropertyAccessMode() => 
            Microsoft.EntityFrameworkCore.Metadata.PropertyAccessMode.PreferField;
        public System.Reflection.FieldInfo? FieldInfo => null;
        public System.Reflection.PropertyInfo? PropertyInfo => null;
        public Microsoft.EntityFrameworkCore.Metadata.IReadOnlyElementType? GetElementType() => null;
    }
}
