// ✅ SMELL-3 FIXED: Transactions domain extracted into own endpoint module
// ✅ SMELL-9 FIXED: /api/v1/ versioning
// ✅ SMELL-6 FIXED: Pagination
// ✅ SMELL-1 FIXED: All queries parameterised via service layer

using CortexLabs.FinTrack.Application.Interfaces;
using CortexLabs.FinTrack.Domain.Entities;
using CortexLabs.FinTrack.Domain.Enums;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace CortexLabs.FinTrack.Api.Endpoints;

/// <summary>Registers all /api/v1/transactions endpoints.</summary>
public static class TransactionEndpoints
{
    public static void MapTransactionEndpoints(this WebApplication app)
    {
        var group = app.MapGroup("/api/v1/transactions").WithTags("Transactions").RequireAuthorization();

        group.MapGet("/", async (
            [FromServices] ITransactionService transactionService,
            [FromQuery] int page = 1,
            [FromQuery] int pageSize = 25) =>
            Results.Ok(await transactionService.GetTransactionsAsync(page, pageSize)));

        group.MapGet("/search", async (
            [FromServices] ITransactionService transactionService,
            [FromQuery] TransactionCategory? category,
            [FromQuery] DateOnly? from,
            [FromQuery] int page = 1,
            [FromQuery] int pageSize = 25) =>
            Results.Ok(await transactionService.SearchAsync(category, from, page, pageSize)));

        group.MapPost("/", async (
            [FromServices] ITransactionService transactionService,
            [FromServices] IValidationService validationService,
            [FromBody] Transaction tx) =>
        {
            // ✅ SMELL-10 FIXED: Validation via single ValidationService
            var amtCheck = validationService.ValidateAmount(tx.Amount);
            if (!amtCheck.IsValid)
                return Results.BadRequest(new { Error = amtCheck.Error });

            var created = await transactionService.CreateAsync(tx);
            return Results.Created($"/api/v1/transactions/{created.Id}", created);
        });
    }
}
