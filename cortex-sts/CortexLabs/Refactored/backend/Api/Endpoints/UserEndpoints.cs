// ✅ SMELL-3 FIXED: Users domain extracted into own endpoint module
// ✅ SMELL-9 FIXED: /api/v1/ versioning
// ✅ SMELL-6 FIXED: Pagination query params (page, pageSize)
// ✅ SMELL-2 FIXED: PasswordHash NOT exposed in GET response
// ✅ SMELL-18 FIXED: Auth required via [Authorize]

using CortexLabs.FinTrack.Application.Interfaces;
using CortexLabs.FinTrack.Domain.Entities;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace CortexLabs.FinTrack.Api.Endpoints;

/// <summary>Registers all /api/v1/users endpoints.</summary>
public static class UserEndpoints
{
    public static void MapUserEndpoints(this WebApplication app)
    {
        var group = app.MapGroup("/api/v1/users").WithTags("Users");

        // ✅ SMELL-9 FIXED: /api/v1/ versioned route
        // ✅ SMELL-6 FIXED: page + pageSize pagination
        // ✅ SMELL-18 FIXED: [Authorize] — admin only
        group.MapGet("/", [Authorize(Roles = "admin")] async (
            [FromServices] IUserService userService,
            [FromQuery] int page = 1,
            [FromQuery] int pageSize = 25) =>
        {
            var users = await userService.GetUsersAsync(page, pageSize);
            // ✅ SMELL-2 FIXED: PasswordHash excluded from response
            var dto = users.Select(u => new { u.Id, u.UserName, u.Email, u.Role, u.IsActive });
            return Results.Ok(dto);
        });

        group.MapGet("/search", [Authorize] async (
            [FromServices] IUserService userService,
            [FromQuery] string username,
            [FromQuery] int page = 1,
            [FromQuery] int pageSize = 25) =>
        {
            // ✅ SMELL-1 FIXED: Username goes into parameterised query inside service
            var user = await userService.FindByUsernameAsync(username);
            return user is null ? Results.NotFound() : Results.Ok(new { user.Id, user.UserName, user.Email });
        });

        group.MapPost("/", async (
            [FromServices] IUserService userService,
            [FromServices] IValidationService validationService,
            [FromServices] IAuthService authService,
            [FromBody] CreateUserRequest request) =>
        {
            // ✅ SMELL-10 FIXED: Validation via single canonical service
            var emailCheck = validationService.ValidateEmail(request.Email);
            if (!emailCheck.IsValid)
                return Results.BadRequest(new { Error = emailCheck.Error });

            var user = new User
            {
                UserName = request.UserName,
                Email = request.Email,
                // ✅ SMELL-2 FIXED: BCrypt hash — never store plaintext
                PasswordHash = authService.HashPassword(request.Password),
                Role = "user"
            };

            var created = await userService.CreateAsync(user);
            return Results.Created($"/api/v1/users/{created.Id}", new { created.Id, created.UserName, created.Email });
        });

        group.MapDelete("/{id:int}", [Authorize(Roles = "admin")] async (
            [FromServices] IUserService userService,
            [FromServices] IAuthService authService,
            HttpContext ctx,
            int id) =>
        {
            var actorId = int.TryParse(ctx.User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier)?.Value, out var aid) ? aid : 0;
            var deleted = await userService.DeleteAsync(id, actorId);
            return deleted ? Results.Ok(new { Deleted = true }) : Results.NotFound();
        });
    }
}

/// <summary>Request DTO for user creation — prevents model binding of Role/PasswordHash.</summary>
public record CreateUserRequest(string UserName, string Email, string Password);
