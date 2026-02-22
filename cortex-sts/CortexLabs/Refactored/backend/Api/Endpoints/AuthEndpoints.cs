// ✅ SMELL-3 FIXED: Auth domain extracted into own module
// ✅ SMELL-2 FIXED: JWT from config; BCrypt in AuthService
// ✅ SMELL-18 FIXED: Generic 401 — no information disclosure
// ✅ SMELL-9 FIXED: /api/v1/ versioning

using CortexLabs.FinTrack.Application.Interfaces;
using Microsoft.AspNetCore.Mvc;

namespace CortexLabs.FinTrack.Api.Endpoints;

/// <summary>Registers all /api/v1/auth endpoints.</summary>
public static class AuthEndpoints
{
    public static void MapAuthEndpoints(this WebApplication app)
    {
        var group = app.MapGroup("/api/v1/auth").WithTags("Auth");

        // ✅ SMELL-18 FIXED: Credentials in POST body (not query string)
        // ✅ Rate limiting applied via app.UseRateLimiter() in Program.cs
        group.MapPost("/login", async (
            [FromServices] IAuthService authService,
            [FromBody] LoginRequest request) =>
        {
            if (string.IsNullOrWhiteSpace(request.Username) || string.IsNullOrWhiteSpace(request.Password))
                return Results.BadRequest(new { Error = "Username and password are required." });

            var result = await authService.LoginAsync(request.Username, request.Password);

            // ✅ SMELL-18 FIXED: Generic 401 — no hint as to whether user or password is wrong
            return result.Success
                ? Results.Ok(new { result.Token, result.Role })
                : Results.Unauthorized();
        });
    }
}

/// <summary>Login request DTO — credentials come from JSON body, not query string.</summary>
public record LoginRequest(string Username, string Password);
