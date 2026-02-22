// ✅ SMELL-3 FIXED: Accounts domain extracted into own module
// ✅ SMELL-9 FIXED: /api/v1/ versioning
// ✅ SMELL-4 FIXED: Transfer business logic in AccountService, not inline here
// ✅ SMELL-14 FIXED: Atomic transfer in AccountService (SQLite transaction)

using CortexLabs.FinTrack.Application.Interfaces;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace CortexLabs.FinTrack.Api.Endpoints;

/// <summary>Registers all /api/v1/accounts endpoints.</summary>
public static class AccountEndpoints
{
    public static void MapAccountEndpoints(this WebApplication app)
    {
        var group = app.MapGroup("/api/v1/accounts").WithTags("Accounts").RequireAuthorization();

        group.MapGet("/", async (
            [FromServices] IAccountService accountService,
            [FromQuery] int page = 1,
            [FromQuery] int pageSize = 25) =>
            Results.Ok(await accountService.GetAccountsAsync(page, pageSize)));

        group.MapPost("/transfer", async (
            [FromServices] IAccountService accountService,
            [FromQuery] int fromId,
            [FromQuery] int toId,
            [FromQuery] decimal amount,
            HttpContext ctx) =>
        {
            var actorId = int.TryParse(
                ctx.User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier)?.Value, out var aid) ? aid : 0;

            var result = await accountService.TransferAsync(fromId, toId, amount, actorId);

            return result.Success
                ? Results.Ok(new { Message = "Transfer complete", FromId = fromId, ToId = toId, Amount = amount })
                : Results.BadRequest(new { Error = result.Error });
        });
    }
}
