using System.Text.RegularExpressions;

namespace CortexLabs.FinTrack.Application.Validators;

/// <summary>
/// Email validation — extracted from inline regex scattered across endpoints (SMELL-07).
/// Single Responsibility: one class, one job.
/// </summary>
public static class EmailValidator
{
    private static readonly Regex EmailRegex = new(
        @"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        RegexOptions.Compiled | RegexOptions.IgnoreCase);

    /// <summary>
    /// Validates an email address format.
    /// </summary>
    /// <param name="email">The email to validate.</param>
    /// <returns>True if the email matches the expected format.</returns>
    public static bool IsValid(string? email)
    {
        if (string.IsNullOrWhiteSpace(email))
            return false;

        return EmailRegex.IsMatch(email);
    }
}
