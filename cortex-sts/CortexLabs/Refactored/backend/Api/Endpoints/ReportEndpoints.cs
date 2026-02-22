// ✅ SMELL-3 FIXED: Reports domain extracted into own module
// ✅ SMELL-9 FIXED: /api/v1/ versioning
// ✅ SMELL-4 FIXED: Report generation logic in ReportService, not inline

using CortexLabs.FinTrack.Application.Interfaces;
using CortexLabs.FinTrack.Domain.Enums;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace CortexLabs.FinTrack.Api.Endpoints;

/// <summary>Registers all /api/v1/reports endpoints.</summary>
public static class ReportEndpoints
{
    public static void MapReportEndpoints(this WebApplication app)
    {
        var group = app.MapGroup("/api/v1/reports").WithTags("Reports").RequireAuthorization();

        group.MapGet("/", async (
            [FromServices] IReportService reportService,
            [FromQuery] int page = 1,
            [FromQuery] int pageSize = 25) =>
            Results.Ok(await reportService.GetReportsAsync(page, pageSize)));

        group.MapPost("/generate", async (
            [FromServices] IReportService reportService,
            [FromQuery] ReportType reportType,
            HttpContext ctx) =>
        {
            var actorId = int.TryParse(
                ctx.User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier)?.Value, out var aid) ? aid : 0;

            var report = await reportService.GenerateAsync(reportType, actorId);
            return Results.Ok(report);
        });
    }
}
