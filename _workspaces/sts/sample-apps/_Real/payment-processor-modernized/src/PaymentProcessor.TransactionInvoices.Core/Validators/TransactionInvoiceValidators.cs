using FluentValidation;
using PaymentProcessor.TransactionInvoices.Core.DTOs;

namespace PaymentProcessor.TransactionInvoices.Core.Validators;

/// <summary>
/// Validator for CreateTransactionInvoiceRequest.
/// Enforces business rules extracted from XAddTransactionInvoice.
/// </summary>
public class CreateTransactionInvoiceRequestValidator : AbstractValidator<CreateTransactionInvoiceRequest>
{
    public CreateTransactionInvoiceRequestValidator()
    {
        RuleFor(x => x.EmployerId)
            .NotEmpty()
            .WithMessage("Employer ID is required");

        RuleFor(x => x.AccountCategoryId)
            .NotEmpty()
            .WithMessage("AccountCategory ID is required");

        RuleFor(x => x.PaymentPlanId)
            .NotEmpty()
            .WithMessage("Payment Plan ID is required");

        RuleFor(x => x.EmployerTransactionDefault)
            .GreaterThanOrEqualTo(0)
            .WithMessage("Employer transaction default must be non-negative");

        RuleFor(x => x.EmployeeTransactionDefault)
            .GreaterThanOrEqualTo(0)
            .WithMessage("Employee transaction default must be non-negative");

        RuleFor(x => x)
            .Must(x => x.EmployerTransactionDefault > 0 || x.EmployeeTransactionDefault > 0)
            .WithMessage("At least one transaction amount (employer or employee) must be greater than zero");

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
/// Validator for GenerateTransactionInvoiceRequest.
/// Enforces business rules extracted from XGenerateTransactionInvoice.
/// </summary>
public class GenerateTransactionInvoiceRequestValidator : AbstractValidator<GenerateTransactionInvoiceRequest>
{
    public GenerateTransactionInvoiceRequestValidator()
    {
        RuleFor(x => x.AccountCategoryId)
            .NotEmpty()
            .WithMessage("AccountCategory ID is required");

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
/// Validator for CreateBatchTransactionInvoiceRequest.
/// Enforces business rules extracted from Updater_CreatePaymentTransactionInvoices.
/// </summary>
public class CreateBatchTransactionInvoiceRequestValidator : AbstractValidator<CreateBatchTransactionInvoiceRequest>
{
    public CreateBatchTransactionInvoiceRequestValidator()
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
