// ✅ SMELL-10 FIXED: Centralised validation — no duplication
// ✅ SMELL-15 FIXED: Named constants instead of magic numbers

using CortexLabs.FinTrack.Application.Interfaces;

namespace CortexLabs.FinTrack.Application.Services;

/// <summary>
/// Single canonical validation service that replaces duplicate validation logic
/// previously scattered across UserService, TransactionService, and endpoint handlers.
/// </summary>
public sealed class ValidationService : IValidationService
{
    // ✅ SMELL-15 FIXED: Named constants
    private const int EmailMinLength = 5;
    private const int EmailMaxLength = 200;
    private const decimal MaxTransferAmount = 1_000_000m;
    private const decimal MinTransferAmount = 0.01m;

    /// <inheritdoc/>
    public ValidationResult ValidateEmail(string email)
    {
        if (string.IsNullOrWhiteSpace(email))
            return ValidationResult.Fail("Email is required.");

        if (!email.Contains('@'))
            return ValidationResult.Fail("Email must contain '@'.");

        if (email.Length < EmailMinLength)
            return ValidationResult.Fail($"Email must be at least {EmailMinLength} characters.");

        if (email.Length > EmailMaxLength)
            return ValidationResult.Fail($"Email must be at most {EmailMaxLength} characters.");

        return ValidationResult.Ok();
    }

    /// <inheritdoc/>
    public ValidationResult ValidateTransfer(int fromId, int toId, decimal amount, decimal currentBalance)
    {
        if (fromId == toId)
            return ValidationResult.Fail("Source and destination accounts must be different.");

        var amountCheck = ValidateAmount(amount);
        if (!amountCheck.IsValid) return amountCheck;

        if (amount > MaxTransferAmount)
            return ValidationResult.Fail($"Single transfer cannot exceed {MaxTransferAmount:C}.");

        if (currentBalance < amount)
            return ValidationResult.Fail("Insufficient funds.");

        return ValidationResult.Ok();
    }

    /// <inheritdoc/>
    public ValidationResult ValidateAmount(decimal amount)
    {
        if (amount < MinTransferAmount)
            return ValidationResult.Fail($"Amount must be at least {MinTransferAmount:C}.");

        return ValidationResult.Ok();
    }
}
