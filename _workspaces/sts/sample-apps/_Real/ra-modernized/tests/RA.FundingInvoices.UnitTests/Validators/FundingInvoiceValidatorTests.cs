using FluentAssertions;
using RA.FundingInvoices.Core.DTOs;
using RA.FundingInvoices.Core.Validators;
using Xunit;

namespace RA.FundingInvoices.UnitTests.Validators;

public class FundingInvoiceValidatorTests
{
    [Fact]
    public void CreateFundingInvoiceRequestValidator_WithValidRequest_PassesValidation()
    {
        // Arrange
        var validator = new CreateFundingInvoiceRequestValidator();
        var request = new CreateFundingInvoiceRequest
        {
            EmployerId = "EMP-001",
            SubaccountId = "SA-001",
            ReimbursementPlanId = "RP-001",
            EmployerFundingDefault = 500m,
            EmployeeFundingDefault = 250m,
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
    public void CreateFundingInvoiceRequestValidator_WithEmptyEmployerId_FailsValidation()
    {
        // Arrange
        var validator = new CreateFundingInvoiceRequestValidator();
        var request = new CreateFundingInvoiceRequest
        {
            EmployerId = "",
            SubaccountId = "SA-001",
            ReimbursementPlanId = "RP-001",
            EmployerFundingDefault = 100m,
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
    public void CreateFundingInvoiceRequestValidator_WithBothAmountsZero_FailsValidation()
    {
        // Arrange
        var validator = new CreateFundingInvoiceRequestValidator();
        var request = new CreateFundingInvoiceRequest
        {
            EmployerId = "EMP-001",
            SubaccountId = "SA-001",
            ReimbursementPlanId = "RP-001",
            EmployerFundingDefault = 0m,
            EmployeeFundingDefault = 0m,
            InvoiceDescription = "Test",
            CreatedBy = "TestUser"
        };

        // Act
        var result = validator.Validate(request);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.ErrorMessage.Contains("At least one funding amount"));
    }

    [Fact]
    public void GenerateFundingInvoiceRequestValidator_WithValidRequest_PassesValidation()
    {
        // Arrange
        var validator = new GenerateFundingInvoiceRequestValidator();
        var request = new GenerateFundingInvoiceRequest
        {
            SubaccountId = "SA-001",
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
    public void GenerateFundingInvoiceRequestValidator_WithNegativeAmount_FailsValidation()
    {
        // Arrange
        var validator = new GenerateFundingInvoiceRequestValidator();
        var request = new GenerateFundingInvoiceRequest
        {
            SubaccountId = "SA-001",
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
    public void GenerateFundingInvoiceRequestValidator_WithPastDate_FailsValidation()
    {
        // Arrange
        var validator = new GenerateFundingInvoiceRequestValidator();
        var request = new GenerateFundingInvoiceRequest
        {
            SubaccountId = "SA-001",
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
    public void CreateBatchFundingInvoiceRequestValidator_WithValidRequest_PassesValidation()
    {
        // Arrange
        var validator = new CreateBatchFundingInvoiceRequestValidator();
        var request = new CreateBatchFundingInvoiceRequest
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
    public void CreateBatchFundingInvoiceRequestValidator_WithEmptyCreatedBy_FailsValidation()
    {
        // Arrange
        var validator = new CreateBatchFundingInvoiceRequestValidator();
        var request = new CreateBatchFundingInvoiceRequest
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
