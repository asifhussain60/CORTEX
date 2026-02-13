using FluentValidation;
using RA.FundingInvoices.Core.DTOs;

namespace RA.FundingInvoices.Core.Validators;

/// <summary>
/// Validator for CloseFundingBatchRequest.
/// Enforces business rules extracted from XCloseFundingBatch.
/// </summary>
public class CloseFundingBatchRequestValidator : AbstractValidator<CloseFundingBatchRequest>
{
    public CloseFundingBatchRequestValidator()
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
/// Validator for ReopenFundingBatchRequest.
/// Enforces business rules extracted from XReopenFundingBatch.
/// </summary>
public class ReopenFundingBatchRequestValidator : AbstractValidator<ReopenFundingBatchRequest>
{
    public ReopenFundingBatchRequestValidator()
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
/// Validator for UpdateFundingBatchRequest.
/// Enforces business rules extracted from XUpdateFundingBatch.
/// </summary>
public class UpdateFundingBatchRequestValidator : AbstractValidator<UpdateFundingBatchRequest>
{
    private static readonly string[] ValidStatuses = { "Open", "Pending", "Closed", "Reopened" };

    public UpdateFundingBatchRequestValidator()
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
/// Validator for CreateFundingBatchRequest.
/// Enforces business rules for batch creation.
/// </summary>
public class CreateFundingBatchRequestValidator : AbstractValidator<CreateFundingBatchRequest>
{
    private static readonly string[] ValidStatuses = { "Open", "Pending", "Closed", "Reopened" };

    public CreateFundingBatchRequestValidator()
    {
        RuleFor(x => x.SubaccountId)
            .NotEmpty()
            .WithMessage("Subaccount ID is required");

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
