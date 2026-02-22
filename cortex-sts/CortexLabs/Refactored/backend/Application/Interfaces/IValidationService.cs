// ✅ SMELL-10 FIXED: Single ValidationService — no duplicate validation across services and endpoints
// ✅ SMELL-15 FIXED: Named constants — no magic numbers

namespace CortexLabs.FinTrack.Application.Interfaces;

/// <summary>Centralised validation contract (eliminates duplicated inline validation — SMELL-10).</summary>
public interface IValidationService
{
    /// <summary>Validates an email address format and length.</summary>
    ValidationResult ValidateEmail(string email);

    /// <summary>Validates a transfer request (amounts, overdraft, self-transfer).</summary>
    ValidationResult ValidateTransfer(int fromId, int toId, decimal amount, decimal currentBalance);

    /// <summary>Validates that an amount is positive and within allowed bounds.</summary>
    ValidationResult ValidateAmount(decimal amount);
}

/// <summary>Result of a validation check.</summary>
public record ValidationResult(bool IsValid, string? Error = null)
{
    public static ValidationResult Ok() => new(true);
    public static ValidationResult Fail(string error) => new(false, error);
}
