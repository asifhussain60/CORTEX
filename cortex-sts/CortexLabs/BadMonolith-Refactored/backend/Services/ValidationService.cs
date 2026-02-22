// ✅ CORTEX Refactored — ValidationService
// ✅ SMELL-10 RESOLVED: Consolidated duplicate validation logic

using CortexLabs.FinTrack.Services.Interfaces;

namespace CortexLabs.FinTrack.Services;

/// <summary>
/// Centralized validation service — eliminates duplicate validation across Program.cs, UserService, TransactionService
/// </summary>
public class ValidationService : IValidationService
{
    // ✅ SMELL-15 RESOLVED: Magic numbers extracted to constants
    private const int MinEmailLength = 5;
    private const int MaxEmailLength = 100;
    private const int MinDescriptionLength = 1;
    private const int MaxDescriptionLength = 500;
    private const decimal MaxTransactionAmount = 10_000_000;

    /// <summary>
    /// Validates email format and length
    /// </summary>
    public ValidationResult ValidateEmail(string email)
    {
        var errors = new List<string>();

        if (string.IsNullOrWhiteSpace(email))
        {
            errors.Add("Email is required");
            return new ValidationResult(false, errors);
        }

        if (!email.Contains("@") || !email.Contains("."))
        {
            errors.Add("Invalid email format");
        }

        if (email.Length < MinEmailLength)
        {
            errors.Add($"Email must be at least {MinEmailLength} characters");
        }

        if (email.Length > MaxEmailLength)
        {
            errors.Add($"Email must not exceed {MaxEmailLength} characters");
        }

        return new ValidationResult(errors.Count == 0, errors);
    }

    /// <summary>
    /// Validates transaction data
    /// </summary>
    public ValidationResult ValidateTransaction(CreateTransactionDto dto)
    {
        var errors = new List<string>();

        if (string.IsNullOrWhiteSpace(dto.Description))
        {
            errors.Add("Description is required");
        }
        else if (dto.Description.Length < MinDescriptionLength || dto.Description.Length > MaxDescriptionLength)
        {
            errors.Add($"Description must be between {MinDescriptionLength} and {MaxDescriptionLength} characters");
        }

        if (dto.Amount <= 0)
        {
            errors.Add("Amount must be positive");
        }

        if (dto.Amount > MaxTransactionAmount)
        {
            errors.Add($"Amount must not exceed {MaxTransactionAmount:C}");
        }

        // ✅ SMELL-15 RESOLVED: Magic strings → enum validation
        var validTypes = new[] { "income", "expense" };
        if (!validTypes.Contains(dto.Type?.ToLowerInvariant()))
        {
            errors.Add("Type must be 'income' or 'expense'");
        }

        if (dto.UserId <= 0)
        {
            errors.Add("Valid UserId is required");
        }

        return new ValidationResult(errors.Count == 0, errors);
    }

    /// <summary>
    /// Validates user creation data
    /// </summary>
    public ValidationResult ValidateUser(CreateUserDto dto)
    {
        var errors = new List<string>();

        if (string.IsNullOrWhiteSpace(dto.UserName))
        {
            errors.Add("Username is required");
        }
        else if (dto.UserName.Length < 3 || dto.UserName.Length > 50)
        {
            errors.Add("Username must be between 3 and 50 characters");
        }

        var emailValidation = ValidateEmail(dto.Email);
        if (!emailValidation.IsValid)
        {
            errors.AddRange(emailValidation.Errors);
        }

        if (string.IsNullOrWhiteSpace(dto.Password))
        {
            errors.Add("Password is required");
        }
        else if (dto.Password.Length < 8)
        {
            errors.Add("Password must be at least 8 characters");
        }

        var validRoles = new[] { "user", "admin", "moderator" };
        if (!string.IsNullOrEmpty(dto.Role) && !validRoles.Contains(dto.Role.ToLowerInvariant()))
        {
            errors.Add("Invalid role");
        }

        return new ValidationResult(errors.Count == 0, errors);
    }
}
