using FluentAssertions;
using PaymentProcessor.TransactionInvoices.Core.DTOs;
using PaymentProcessor.TransactionInvoices.Core.Validators;
using Xunit;

namespace PaymentProcessor.TransactionInvoices.UnitTests.Validators;

public class TransactionBatchValidatorTests
{
    [Fact]
    public void CloseTransactionBatchRequestValidator_WithValidRequest_PassesValidation()
    {
        // Arrange
        var validator = new CloseTransactionBatchRequestValidator();
        var request = new CloseTransactionBatchRequest
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
    public void CloseTransactionBatchRequestValidator_WithEmptyBatchId_FailsValidation()
    {
        // Arrange
        var validator = new CloseTransactionBatchRequestValidator();
        var request = new CloseTransactionBatchRequest
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
    public void ReopenTransactionBatchRequestValidator_WithValidRequest_PassesValidation()
    {
        // Arrange
        var validator = new ReopenTransactionBatchRequestValidator();
        var request = new ReopenTransactionBatchRequest
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
    public void UpdateTransactionBatchRequestValidator_WithValidRequest_PassesValidation()
    {
        // Arrange
        var validator = new UpdateTransactionBatchRequestValidator();
        var request = new UpdateTransactionBatchRequest
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
    public void UpdateTransactionBatchRequestValidator_WithInvalidStatus_FailsValidation()
    {
        // Arrange
        var validator = new UpdateTransactionBatchRequestValidator();
        var request = new UpdateTransactionBatchRequest
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
    public void UpdateTransactionBatchRequestValidator_WithDescriptionTooLong_FailsValidation()
    {
        // Arrange
        var validator = new UpdateTransactionBatchRequestValidator();
        var request = new UpdateTransactionBatchRequest
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
    public void CreateTransactionBatchRequestValidator_WithValidRequest_PassesValidation()
    {
        // Arrange
        var validator = new CreateTransactionBatchRequestValidator();
        var request = new CreateTransactionBatchRequest
        {
            AccountCategoryId = "SA-001",
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
    public void CreateTransactionBatchRequestValidator_WithEmptyAccountCategoryId_FailsValidation()
    {
        // Arrange
        var validator = new CreateTransactionBatchRequestValidator();
        var request = new CreateTransactionBatchRequest
        {
            AccountCategoryId = "",
            Status = "Open",
            CreatedBy = "TestUser"
        };

        // Act
        var result = validator.Validate(request);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.PropertyName == "AccountCategoryId");
    }

    [Fact]
    public void CreateTransactionBatchRequestValidator_WithInvalidStatus_FailsValidation()
    {
        // Arrange
        var validator = new CreateTransactionBatchRequestValidator();
        var request = new CreateTransactionBatchRequest
        {
            AccountCategoryId = "SA-001",
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
