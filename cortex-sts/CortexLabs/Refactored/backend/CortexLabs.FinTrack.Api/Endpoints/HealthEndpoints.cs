namespace CortexLabs.FinTrack.Api.Endpoints;

/// <summary>
/// Health check endpoint — provides /api/v1/health for monitoring.
/// </summary>
public static class HealthEndpoints
{
    public static void MapHealthEndpoints(this WebApplication app)
    {
        app.MapGet("/api/v1/health", () => Results.Ok(new
        {
            status = "healthy",
            service = "CortexLabs.FinTrack",
            version = "2.0.0",
            timestamp = DateTime.UtcNow
        })).WithTags("Health");
    }
}
