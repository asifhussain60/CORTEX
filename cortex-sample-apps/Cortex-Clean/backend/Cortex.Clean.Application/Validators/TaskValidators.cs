using FluentValidation;
using Cortex.Clean.Application.Commands;
using Cortex.Clean.Domain.Services;

namespace Cortex.Clean.Application.Validators;

/// <summary>
/// Validator for CreateTaskCommand.
/// </summary>
public class CreateTaskCommandValidator : AbstractValidator<CreateTaskCommand>
{
    public CreateTaskCommandValidator()
    {
        RuleFor(x => x.Title)
            .NotEmpty().WithMessage("Task title is required.")
            .MaximumLength(TaskValidationService.MaxTitleLength)
            .WithMessage($"Task title cannot exceed {TaskValidationService.MaxTitleLength} characters.");
    }
}

/// <summary>
/// Validator for UpdateTaskCommand.
/// </summary>
public class UpdateTaskCommandValidator : AbstractValidator<UpdateTaskCommand>
{
    public UpdateTaskCommandValidator()
    {
        RuleFor(x => x.Id)
            .GreaterThan(0).WithMessage("Task ID must be greater than 0.");

        RuleFor(x => x.Title)
            .NotEmpty().WithMessage("Task title is required.")
            .MaximumLength(TaskValidationService.MaxTitleLength)
            .WithMessage($"Task title cannot exceed {TaskValidationService.MaxTitleLength} characters.");
    }
}

/// <summary>
/// Validator for DeleteTaskCommand.
/// </summary>
public class DeleteTaskCommandValidator : AbstractValidator<DeleteTaskCommand>
{
    public DeleteTaskCommandValidator()
    {
        RuleFor(x => x.Id)
            .GreaterThan(0).WithMessage("Task ID must be greater than 0.");
    }
}

/// <summary>
/// Validator for ToggleTaskCompletionCommand.
/// </summary>
public class ToggleTaskCompletionCommandValidator : AbstractValidator<ToggleTaskCompletionCommand>
{
    public ToggleTaskCompletionCommandValidator()
    {
        RuleFor(x => x.Id)
            .GreaterThan(0).WithMessage("Task ID must be greater than 0.");
    }
}
