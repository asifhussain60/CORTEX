using FluentValidation;
using RA.FundingInvoices.Core.DTOs;

namespace RA.FundingInvoices.Core.Validators;

/// <summary>
/// Validator for CreateFundingInvoiceRequest.
/// Enforces business rules extracted from XAddFundingInvoice.
/// </summary>
public class CreateFundingInvoiceRequestValidator : AbstractValidator<CreateFundingInvoiceRequest>
{
    public CreateFundingInvoiceRequestValidator()
    {
        RuleFor(x => x.EmployerId)
            .NotEmpty()
            .WithMessage("Employer ID is required");

        RuleFor(x => x.SubaccountId)
            .NotEmpty()
            .WithMessage("Subaccount ID is required");

        RuleFor(x => x.ReimbursementPlanId)
            .NotEmpty()
            .WithMessage("Reimbursement Plan ID is required");

        RuleFor(x => x.EmployerFundingDefault)
            .GreaterThanOrEqualTo(0)
            .WithMessage("Employer funding default must be non-negative");

        RuleFor(x => x.EmployeeFundingDefault)
            .GreaterThanOrEqualTo(0)
            .WithMessage("Employee funding default must be non-negative");

        RuleFor(x => x)
            .Must(x => x.EmployerFundingDefault > 0 || x.EmployeeFundingDefault > 0)
            .WithMessage("At least one funding amount (employer or employee) must be greater than zero");

        RuleFor(x => x.EffectiveDate)
            .NotEmpty()
            .WithMessage("Effective date is required");

        RuleFor(x => x.InvoiceDescription)
            .NotEmpty()
            .MaximumLength(500)
            .WithMessage("Invoice description is required and must not exceed 500 characters");

        RuleFor(x => x.CreatedBy)
            .NotEmpty()
            .MaximumLength(100)
            .WithMessage("Created by is required and must not exceed 100 characters");
    }
}

/// <summary>
/// Validator for GenerateFundingInvoiceRequest.
/// Enforces business rules extracted from XGenerateFundingInvoice.
/// </summary>
public class GenerateFundingInvoiceRequestValidator : AbstractValidator<GenerateFundingInvoiceRequest>
{
    public GenerateFundingInvoiceRequestValidator()
    {
        RuleFor(x => x.SubaccountId)
            .NotEmpty()
            .WithMessage("Subaccount ID is required");

        RuleFor(x => x.InvoiceAmount)
            .GreaterThan(0)
            .WithMessage("Invalid invoice amount - must be greater than zero");

        RuleFor(x => x.InvoiceDate)
            .GreaterThanOrEqualTo(DateTime.Today)
            .WithMessage("Invoice date must be today or later");

        RuleFor(x => x.CreatedBy)
            .NotEmpty()
            .MaximumLength(100)
            .WithMessage("Created by is required and must not exceed 100 characters");
    }
}

/// <summary>
/// Validator for CreateBatchFundingInvoiceRequest.
/// Enforces business rules extracted from Updater_CreateRAFundingInvoices.
/// </summary>
public class CreateBatchFundingInvoiceRequestValidator : AbstractValidator<CreateBatchFundingInvoiceRequest>
{
    public CreateBatchFundingInvoiceRequestValidator()
    {
        RuleFor(x => x.CreatedBy)
            .NotEmpty()
            .MaximumLength(100)
            .WithMessage("Created by is required and must not exceed 100 characters");

        RuleForEach(x => x.EmployerIds)
            .NotEmpty()
            .WithMessage("Employer IDs must not contain empty values");
    }
}
