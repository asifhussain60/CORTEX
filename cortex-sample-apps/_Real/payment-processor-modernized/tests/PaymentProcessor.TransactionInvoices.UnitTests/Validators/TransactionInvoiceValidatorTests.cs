using FluentAssertions;
using PaymentProcessor.TransactionInvoices.Core.DTOs;
using PaymentProcessor.TransactionInvoices.Core.Validators;
using Xunit;

namespace PaymentProcessor.TransactionInvoices.UnitTests.Validators;

public class TransactionInvoiceValidatorTests
{
    [Fact]
    public void CreateTransactionInvoiceRequestValidator_WithValidRequest_PassesValidation()
    {
        // Arrange
        var validator = new CreateTransactionInvoiceRequestValidator();
        var request = new CreateTransactionInvoiceRequest
        {
            EmployerId = "EMP-001",
            AccountCategoryId = "SA-001",
            PaymentPlanId = "RP-001",
            EmployerTransactionDefault = 500m,
            EmployeeTransactionDefault = 250m,
            EffectiveDate = DateTime.Today,
            InvoiceDescription = "Test invoice",
            CreatedBy = "TestUser"
        };

        // Act
        var result = validator.Validate(request);

        // Assert
        result.IsValid.Should().BeTrue();
        result.Errors.Should().BeEmpty();
    }

    [Fact]
    public void CreateTransactionInvoiceRequestValidator_WithEmptyEmployerId_FailsValidation()
    {
        // Arrange
        var validator = new CreateTransactionInvoiceRequestValidator();
        var request = new CreateTransactionInvoiceRequest
        {
            EmployerId = "",
            AccountCategoryId = "SA-001",
            PaymentPlanId = "RP-001",
            EmployerTransactionDefault = 100m,
            InvoiceDescription = "Test",
            CreatedBy = "TestUser"
        };

        // Act
        var result = validator.Validate(request);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.PropertyName == "EmployerId");
    }

    [Fact]
    public void CreateTransactionInvoiceRequestValidator_WithBothAmountsZero_FailsValidation()
    {
        // Arrange
        var validator = new CreateTransactionInvoiceRequestValidator();
        var request = new CreateTransactionInvoiceRequest
        {
            EmployerId = "EMP-001",
            AccountCategoryId = "SA-001",
            PaymentPlanId = "RP-001",
            EmployerTransactionDefault = 0m,
            EmployeeTransactionDefault = 0m,
            InvoiceDescription = "Test",
            CreatedBy = "TestUser"
        };

        // Act
        var result = validator.Validate(request);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.ErrorMessage.Contains("At least one transaction amount"));
    }

    [Fact]
    public void GenerateTransactionInvoiceRequestValidator_WithValidRequest_PassesValidation()
    {
        // Arrange
        var validator = new GenerateTransactionInvoiceRequestValidator();
        var request = new GenerateTransactionInvoiceRequest
        {
            AccountCategoryId = "SA-001",
            InvoiceAmount = 500m,
            InvoiceDate = DateTime.Today.AddDays(1),
            CreatedBy = "TestUser"
        };

        // Act
        var result = validator.Validate(request);

        // Assert
        result.IsValid.Should().BeTrue();
    }

    [Fact]
    public void GenerateTransactionInvoiceRequestValidator_WithNegativeAmount_FailsValidation()
    {
        // Arrange
        var validator = new GenerateTransactionInvoiceRequestValidator();
        var request = new GenerateTransactionInvoiceRequest
        {
            AccountCategoryId = "SA-001",
            InvoiceAmount = -100m,
            InvoiceDate = DateTime.Today,
            CreatedBy = "TestUser"
        };

        // Act
        var result = validator.Validate(request);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.ErrorMessage.Contains("Invalid invoice amount"));
    }

    [Fact]
    public void GenerateTransactionInvoiceRequestValidator_WithPastDate_FailsValidation()
    {
        // Arrange
        var validator = new GenerateTransactionInvoiceRequestValidator();
        var request = new GenerateTransactionInvoiceRequest
        {
            AccountCategoryId = "SA-001",
            InvoiceAmount = 500m,
            InvoiceDate = DateTime.Today.AddDays(-1),
            CreatedBy = "TestUser"
        };

        // Act
        var result = validator.Validate(request);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.ErrorMessage.Contains("today or later"));
    }

    [Fact]
    public void CreateBatchTransactionInvoiceRequestValidator_WithValidRequest_PassesValidation()
    {
        // Arrange
        var validator = new CreateBatchTransactionInvoiceRequestValidator();
        var request = new CreateBatchTransactionInvoiceRequest
        {
            EmployerIds = new List<string> { "EMP-001", "EMP-002" },
            CreatedBy = "TestUser"
        };

        // Act
        var result = validator.Validate(request);

        // Assert
        result.IsValid.Should().BeTrue();
    }

    [Fact]
    public void CreateBatchTransactionInvoiceRequestValidator_WithEmptyCreatedBy_FailsValidation()
    {
        // Arrange
        var validator = new CreateBatchTransactionInvoiceRequestValidator();
        var request = new CreateBatchTransactionInvoiceRequest
        {
            EmployerIds = new List<string> { "EMP-001" },
            CreatedBy = ""
        };

        // Act
        var result = validator.Validate(request);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.PropertyName == "CreatedBy");
    }
}
