using FluentAssertions;
using RA.FundingInvoices.Core.DTOs;
using RA.FundingInvoices.Core.Validators;
using Xunit;

namespace RA.FundingInvoices.UnitTests.Validators;

public class FundingBatchValidatorTests
{
    [Fact]
    public void CloseFundingBatchRequestValidator_WithValidRequest_PassesValidation()
    {
        // Arrange
        var validator = new CloseFundingBatchRequestValidator();
        var request = new CloseFundingBatchRequest
        {
            BatchId = "BATCH-001",
            ExcludedInvoiceIds = new List<string> { "INV-001" },
            ClosedBy = "TestUser"
        };

        // Act
        var result = validator.Validate(request);

        // Assert
        result.IsValid.Should().BeTrue();
    }

    [Fact]
    public void CloseFundingBatchRequestValidator_WithEmptyBatchId_FailsValidation()
    {
        // Arrange
        var validator = new CloseFundingBatchRequestValidator();
        var request = new CloseFundingBatchRequest
        {
            BatchId = "",
            ClosedBy = "TestUser"
        };

        // Act
        var result = validator.Validate(request);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.PropertyName == "BatchId");
    }

    [Fact]
    public void ReopenFundingBatchRequestValidator_WithValidRequest_PassesValidation()
    {
        // Arrange
        var validator = new ReopenFundingBatchRequestValidator();
        var request = new ReopenFundingBatchRequest
        {
            BatchId = "BATCH-001",
            ReopenedBy = "TestUser"
        };

        // Act
        var result = validator.Validate(request);

        // Assert
        result.IsValid.Should().BeTrue();
    }

    [Fact]
    public void UpdateFundingBatchRequestValidator_WithValidRequest_PassesValidation()
    {
        // Arrange
        var validator = new UpdateFundingBatchRequestValidator();
        var request = new UpdateFundingBatchRequest
        {
            BatchId = "BATCH-001",
            Status = "Pending",
            Description = "Updated",
            ModifiedBy = "TestUser"
        };

        // Act
        var result = validator.Validate(request);

        // Assert
        result.IsValid.Should().BeTrue();
    }

    [Fact]
    public void UpdateFundingBatchRequestValidator_WithInvalidStatus_FailsValidation()
    {
        // Arrange
        var validator = new UpdateFundingBatchRequestValidator();
        var request = new UpdateFundingBatchRequest
        {
            BatchId = "BATCH-001",
            Status = "InvalidStatus",
            ModifiedBy = "TestUser"
        };

        // Act
        var result = validator.Validate(request);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.PropertyName == "Status");
    }

    [Fact]
    public void UpdateFundingBatchRequestValidator_WithDescriptionTooLong_FailsValidation()
    {
        // Arrange
        var validator = new UpdateFundingBatchRequestValidator();
        var request = new UpdateFundingBatchRequest
        {
            BatchId = "BATCH-001",
            Description = new string('A', 501), // 501 characters
            ModifiedBy = "TestUser"
        };

        // Act
        var result = validator.Validate(request);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.PropertyName == "Description");
    }

    [Fact]
    public void CreateFundingBatchRequestValidator_WithValidRequest_PassesValidation()
    {
        // Arrange
        var validator = new CreateFundingBatchRequestValidator();
        var request = new CreateFundingBatchRequest
        {
            SubaccountId = "SA-001",
            Status = "Open",
            Description = "New batch",
            CreatedBy = "TestUser"
        };

        // Act
        var result = validator.Validate(request);

        // Assert
        result.IsValid.Should().BeTrue();
    }

    [Fact]
    public void CreateFundingBatchRequestValidator_WithEmptySubaccountId_FailsValidation()
    {
        // Arrange
        var validator = new CreateFundingBatchRequestValidator();
        var request = new CreateFundingBatchRequest
        {
            SubaccountId = "",
            Status = "Open",
            CreatedBy = "TestUser"
        };

        // Act
        var result = validator.Validate(request);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.PropertyName == "SubaccountId");
    }

    [Fact]
    public void CreateFundingBatchRequestValidator_WithInvalidStatus_FailsValidation()
    {
        // Arrange
        var validator = new CreateFundingBatchRequestValidator();
        var request = new CreateFundingBatchRequest
        {
            SubaccountId = "SA-001",
            Status = "UnknownStatus",
            CreatedBy = "TestUser"
        };

        // Act
        var result = validator.Validate(request);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.PropertyName == "Status");
    }
}
