using CortexLabs.FinTrack.Application.DTOs;
using CortexLabs.FinTrack.Application.Services;

namespace CortexLabs.FinTrack.Api.Endpoints;

/// <summary>
/// User endpoints — thin handlers delegating to UserService.
/// Fixes SMELL-01 (God Class → separate endpoint file per domain).
/// </summary>
public static class UserEndpoints
{
    public static void MapUserEndpoints(this WebApplication app)
    {
        var group = app.MapGroup("/api/v1/users").WithTags("Users");

        group.MapGet("/", async (UserService svc, int page = 1, int pageSize = 20) =>
            Results.Ok(await svc.GetAllAsync(page, pageSize)));

        group.MapGet("/{id:int}", async (UserService svc, int id) =>
        {
            var user = await svc.GetByIdAsync(id);
            return user is null ? Results.NotFound() : Results.Ok(user);
        });

        group.MapPost("/", async (UserService svc, CreateUserDto dto) =>
        {
            var (user, error) = await svc.CreateAsync(dto);
            return error is not null
                ? Results.BadRequest(new { error })
                : Results.Created($"/api/v1/users/{user!.Id}", user);
        });

        group.MapDelete("/{id:int}", async (UserService svc, int id) =>
        {
            var deleted = await svc.DeleteAsync(id);
            return deleted ? Results.NoContent() : Results.NotFound();
        });

        group.MapPost("/login", async (UserService svc, LoginDto dto) =>
        {
            var (user, error) = await svc.AuthenticateAsync(dto);
            return error is not null
                ? Results.Unauthorized()
                : Results.Ok(user);
        });
    }
}
