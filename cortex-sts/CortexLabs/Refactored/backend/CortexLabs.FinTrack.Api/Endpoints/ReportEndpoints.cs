using CortexLabs.FinTrack.Application.Services;

namespace CortexLabs.FinTrack.Api.Endpoints;

/// <summary>
/// Report endpoints — fixes SMELL-13 (report logic extracted to ReportService).
/// </summary>
public static class ReportEndpoints
{
    public static void MapReportEndpoints(this WebApplication app)
    {
        var group = app.MapGroup("/api/v1/reports").WithTags("Reports");

        group.MapGet("/user/{userId:int}", async (ReportService svc, int userId) =>
            Results.Ok(await svc.GenerateUserReportAsync(userId)));
    }
}
