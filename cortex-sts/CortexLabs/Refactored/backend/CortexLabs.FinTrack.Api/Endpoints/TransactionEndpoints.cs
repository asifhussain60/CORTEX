using CortexLabs.FinTrack.Application.DTOs;
using CortexLabs.FinTrack.Application.Services;

namespace CortexLabs.FinTrack.Api.Endpoints;

/// <summary>
/// Transaction endpoints — thin handlers delegating to TransactionService.
/// Fixes SMELL-01 (God Class → separate endpoint file per domain),
/// SMELL-20 (pagination added).
/// </summary>
public static class TransactionEndpoints
{
    public static void MapTransactionEndpoints(this WebApplication app)
    {
        var group = app.MapGroup("/api/v1/transactions").WithTags("Transactions");

        group.MapGet("/", async (TransactionService svc, int page = 1, int pageSize = 20) =>
            Results.Ok(await svc.GetAllAsync(page, pageSize)));

        group.MapGet("/{id:int}", async (TransactionService svc, int id) =>
        {
            var txn = await svc.GetByIdAsync(id);
            return txn is null ? Results.NotFound() : Results.Ok(txn);
        });

        group.MapGet("/user/{userId:int}", async (TransactionService svc, int userId, int page = 1, int pageSize = 20) =>
            Results.Ok(await svc.GetByUserIdAsync(userId, page, pageSize)));

        group.MapPost("/", async (TransactionService svc, CreateTransactionDto dto) =>
        {
            var (txn, error) = await svc.CreateAsync(dto);
            return error is not null
                ? Results.BadRequest(new { error })
                : Results.Created($"/api/v1/transactions/{txn!.Id}", txn);
        });

        group.MapDelete("/{id:int}", async (TransactionService svc, int id) =>
        {
            var deleted = await svc.DeleteAsync(id);
            return deleted ? Results.NoContent() : Results.NotFound();
        });

        group.MapGet("/user/{userId:int}/total", async (TransactionService svc, int userId) =>
            Results.Ok(new { userId, total = await svc.GetTotalByUserIdAsync(userId) }));
    }
}
