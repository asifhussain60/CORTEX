// ✅ SMELL-2 FIXED: BCrypt password hashing — not plaintext storage, not SHA256
// ✅ SMELL-2 FIXED: JWT signed with key from IConfiguration (user-secrets/env var)
// ✅ SMELL-18 FIXED: Auth result never reveals which field was wrong (generic 401)
// ✅ SMELL-11 FIXED: ILogger<T> structured logging — no Console.WriteLine

using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using CortexLabs.FinTrack.Application.Interfaces;
using Microsoft.Extensions.Logging;
using Microsoft.IdentityModel.Tokens;

namespace CortexLabs.FinTrack.Infrastructure.Security;

/// <summary>
/// Authentication service using BCrypt for password verification and
/// signed JWT tokens for session management.
/// Secrets are read exclusively from IConfiguration (environment variables / user-secrets).
/// </summary>
public sealed class AuthService : IAuthService
{
    private readonly IUserService _userService;
    private readonly IConfiguration _configuration;
    private readonly ILogger<AuthService> _logger;

    public AuthService(IUserService userService, IConfiguration configuration, ILogger<AuthService> logger)
    {
        _userService = userService;
        _configuration = configuration;
        _logger = logger;
    }

    /// <inheritdoc/>
    public async Task<AuthResult> LoginAsync(string username, string password)
    {
        if (string.IsNullOrWhiteSpace(username) || string.IsNullOrWhiteSpace(password))
            return new AuthResult(false, Error: "Invalid credentials.");

        var user = await _userService.FindByUsernameAsync(username);
        if (user is null)
        {
            // ✅ SMELL-18 FIXED: Generic message — does not reveal whether username exists
            _logger.LogWarning("Login attempt for unknown user {Username}", username);
            return new AuthResult(false, Error: "Invalid credentials.");
        }

        if (!VerifyPassword(password, user.PasswordHash))
        {
            _logger.LogWarning("Failed login attempt for user {UserId}", user.Id);
            return new AuthResult(false, Error: "Invalid credentials.");
        }

        var token = GenerateJwt(user.Id, user.UserName, user.Role);
        _logger.LogInformation("User {UserId} authenticated successfully", user.Id);
        return new AuthResult(true, Token: token, Role: user.Role);
    }

    /// <inheritdoc/>
    public string HashPassword(string plainText)
    {
        // ✅ SMELL-2 / AP-003 FIXED: BCrypt — not SHA256/MD5
        return BCrypt.Net.BCrypt.HashPassword(plainText, workFactor: 12);
    }

    /// <inheritdoc/>
    public bool VerifyPassword(string plainText, string hash)
    {
        return BCrypt.Net.BCrypt.Verify(plainText, hash);
    }

    private string GenerateJwt(int userId, string username, string role)
    {
        // ✅ SMELL-2 FIXED: Secret from config — never hardcoded
        var secret = _configuration["JwtSettings:Secret"]
            ?? throw new InvalidOperationException("JwtSettings:Secret is not configured. Use user-secrets or environment variables.");

        var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(secret));
        var creds = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);

        var claims = new[]
        {
            new Claim(ClaimTypes.NameIdentifier, userId.ToString()),
            new Claim(ClaimTypes.Name, username),
            new Claim(ClaimTypes.Role, role)
        };

        var expiry = int.TryParse(_configuration["JwtSettings:ExpiryMinutes"], out var mins) ? mins : 60;
        var token = new JwtSecurityToken(
            issuer: _configuration["JwtSettings:Issuer"] ?? "cortexlabs-fintrack",
            audience: _configuration["JwtSettings:Audience"] ?? "cortexlabs-fintrack-users",
            claims: claims,
            expires: DateTime.UtcNow.AddMinutes(expiry),
            signingCredentials: creds);

        return new JwtSecurityTokenHandler().WriteToken(token);
    }
}
