// ✅ SMELL-3 FIXED: Analytics domain extracted into own module
// ✅ SMELL-6 FIXED: DB aggregation via AnalyticsService — no in-memory full scan
// ✅ SMELL-9 FIXED: /api/v1/ versioning
// ✅ SMELL-18 FIXED: Admin stats never expose secrets, connection strings, or JWT keys

using CortexLabs.FinTrack.Application.Interfaces;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace CortexLabs.FinTrack.Api.Endpoints;

/// <summary>Registers analytics and admin monitoring endpoints.</summary>
public static class AnalyticsEndpoints
{
    public static void MapAnalyticsEndpoints(this WebApplication app)
    {
        var analyticsGroup = app.MapGroup("/api/v1/analytics").WithTags("Analytics").RequireAuthorization();
        var adminGroup = app.MapGroup("/api/v1/admin").WithTags("Admin");

        analyticsGroup.MapGet("/summary", async ([FromServices] IAnalyticsService analyticsService) =>
            Results.Ok(await analyticsService.GetSummaryAsync()));

        // ✅ SMELL-18 FIXED: Admin stats endpoint — [Authorize(admin)] + NO secrets exposed
        adminGroup.MapGet("/stats", [Authorize(Roles = "admin")] ([FromServices] IAnalyticsService analyticsService) =>
            Results.Ok(new
            {
                Status = "healthy",
                Timestamp = DateTime.UtcNow
                // ✅ SMELL-2 FIXED: ConnectionString, JwtSecret, SmtpPassword REMOVED
            }));

        // Health endpoint with real DB check
        app.MapGet("/api/v1/health", async ([FromServices] IConfiguration config) =>
        {
            var healthy = false;
            var connStr = config.GetConnectionString("DefaultConnection");
            if (connStr is not null)
            {
                try
                {
                    await using var conn = new Microsoft.Data.Sqlite.SqliteConnection(connStr);
                    await conn.OpenAsync();
                    healthy = true;
                }
                catch { /* handled below */ }
            }

            return healthy
                ? Results.Ok(new { Status = "healthy", Timestamp = DateTime.UtcNow })
                : Results.Json(new { Status = "unhealthy", Timestamp = DateTime.UtcNow },
                    statusCode: StatusCodes.Status503ServiceUnavailable);
        });
    }
}
