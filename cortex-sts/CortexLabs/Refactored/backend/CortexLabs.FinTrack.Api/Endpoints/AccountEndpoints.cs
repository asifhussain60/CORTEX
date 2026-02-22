using CortexLabs.FinTrack.Application.DTOs;
using CortexLabs.FinTrack.Application.Services;

namespace CortexLabs.FinTrack.Api.Endpoints;

/// <summary>
/// Account endpoints — thin handlers delegating to AccountService.
/// Fixes SMELL-01 (God Class → separate endpoint file per domain).
/// </summary>
public static class AccountEndpoints
{
    public static void MapAccountEndpoints(this WebApplication app)
    {
        var group = app.MapGroup("/api/v1/accounts").WithTags("Accounts");

        group.MapGet("/", async (AccountService svc, int page = 1, int pageSize = 20) =>
            Results.Ok(await svc.GetAllAsync(page, pageSize)));

        group.MapGet("/{id:int}", async (AccountService svc, int id) =>
        {
            var account = await svc.GetByIdAsync(id);
            return account is null ? Results.NotFound() : Results.Ok(account);
        });

        group.MapGet("/user/{userId:int}", async (AccountService svc, int userId) =>
            Results.Ok(await svc.GetByUserIdAsync(userId)));

        group.MapPost("/", async (AccountService svc, CreateAccountDto dto) =>
        {
            var (account, error) = await svc.CreateAsync(dto);
            return error is not null
                ? Results.BadRequest(new { error })
                : Results.Created($"/api/v1/accounts/{account!.Id}", account);
        });

        group.MapDelete("/{id:int}", async (AccountService svc, int id) =>
        {
            var deleted = await svc.DeleteAsync(id);
            return deleted ? Results.NoContent() : Results.NotFound();
        });
    }
}
