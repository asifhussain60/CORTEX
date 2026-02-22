// ✅ SMELL-2 FIXED: Auth against hashed passwords; JWT from config — no hardcoded secrets
// ✅ SMELL-18 FIXED: No rate limit concern at interface level — enforced at middleware

namespace CortexLabs.FinTrack.Application.Interfaces;

/// <summary>Contract for authentication operations.</summary>
public interface IAuthService
{
    /// <summary>Validates credentials and returns a signed JWT on success.</summary>
    Task<AuthResult> LoginAsync(string username, string password);

    /// <summary>Hashes a plain-text password using BCrypt.</summary>
    string HashPassword(string plainText);

    /// <summary>Verifies a plain-text password against a stored BCrypt hash.</summary>
    bool VerifyPassword(string plainText, string hash);
}

/// <summary>Result of an authentication attempt.</summary>
public record AuthResult(bool Success, string? Token = null, string? Role = null, string? Error = null);
