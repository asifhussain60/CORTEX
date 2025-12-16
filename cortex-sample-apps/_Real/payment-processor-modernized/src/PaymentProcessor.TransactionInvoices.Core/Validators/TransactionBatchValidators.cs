using FluentValidation;
using PaymentProcessor.TransactionInvoices.Core.DTOs;

namespace PaymentProcessor.TransactionInvoices.Core.Validators;

/// <summary>
/// Validator for CloseTransactionBatchRequest.
/// Enforces business rules extracted from XCloseTransactionBatch.
/// </summary>
public class CloseTransactionBatchRequestValidator : AbstractValidator<CloseTransactionBatchRequest>
{
    public CloseTransactionBatchRequestValidator()
    {
        RuleFor(x => x.BatchId)
            .NotEmpty()
            .WithMessage("Batch ID is required");

        RuleFor(x => x.ClosedBy)
            .NotEmpty()
            .MaximumLength(100)
            .WithMessage("Closed by is required and must not exceed 100 characters");

        RuleForEach(x => x.ExcludedInvoiceIds)
            .NotEmpty()
            .WithMessage("Excluded invoice IDs must not contain empty values");
    }
}

/// <summary>
/// Validator for ReopenTransactionBatchRequest.
/// Enforces business rules extracted from XReopenTransactionBatch.
/// </summary>
public class ReopenTransactionBatchRequestValidator : AbstractValidator<ReopenTransactionBatchRequest>
{
    public ReopenTransactionBatchRequestValidator()
    {
        RuleFor(x => x.BatchId)
            .NotEmpty()
            .WithMessage("Batch ID is required");

        RuleFor(x => x.ReopenedBy)
            .NotEmpty()
            .MaximumLength(100)
            .WithMessage("Reopened by is required and must not exceed 100 characters");
    }
}

/// <summary>
/// Validator for UpdateTransactionBatchRequest.
/// Enforces business rules extracted from XUpdateTransactionBatch.
/// </summary>
public class UpdateTransactionBatchRequestValidator : AbstractValidator<UpdateTransactionBatchRequest>
{
    private static readonly string[] ValidStatuses = { "Open", "Pending", "Closed", "Reopened" };

    public UpdateTransactionBatchRequestValidator()
    {
        RuleFor(x => x.BatchId)
            .NotEmpty()
            .WithMessage("Batch ID is required");

        RuleFor(x => x.Status)
            .Must(status => status == null || ValidStatuses.Contains(status))
            .WithMessage($"Status must be one of: {string.Join(", ", ValidStatuses)}");

        RuleFor(x => x.Description)
            .MaximumLength(500)
            .When(x => x.Description != null)
            .WithMessage("Description must not exceed 500 characters");

        RuleFor(x => x.ModifiedBy)
            .NotEmpty()
            .MaximumLength(100)
            .WithMessage("Modified by is required and must not exceed 100 characters");
    }
}

/// <summary>
/// Validator for CreateTransactionBatchRequest.
/// Enforces business rules for batch creation.
/// </summary>
public class CreateTransactionBatchRequestValidator : AbstractValidator<CreateTransactionBatchRequest>
{
    private static readonly string[] ValidStatuses = { "Open", "Pending", "Closed", "Reopened" };

    public CreateTransactionBatchRequestValidator()
    {
        RuleFor(x => x.AccountCategoryId)
            .NotEmpty()
            .WithMessage("AccountCategory ID is required");

        RuleFor(x => x.Status)
            .NotEmpty()
            .Must(status => ValidStatuses.Contains(status))
            .WithMessage($"Status must be one of: {string.Join(", ", ValidStatuses)}");

        RuleFor(x => x.Description)
            .MaximumLength(500)
            .When(x => x.Description != null)
            .WithMessage("Description must not exceed 500 characters");

        RuleFor(x => x.CreatedBy)
            .NotEmpty()
            .MaximumLength(100)
            .WithMessage("Created by is required and must not exceed 100 characters");
    }
}
