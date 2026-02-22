namespace CortexLabs.FinTrack.Infrastructure.Configuration;

/// <summary>
/// Strongly-typed configuration — fixes SMELL-03 (hardcoded connection string)
/// and SMELL-04 (hardcoded secrets). Values loaded from appsettings.json via DI.
/// </summary>
public class AppSettings
{
    public string ConnectionString { get; set; } = "Data Source=fintrack.db";
    public string JwtSecret { get; set; } = string.Empty;
    public int JwtExpiryMinutes { get; set; } = 60;
    public string[] AllowedOrigins { get; set; } = Array.Empty<string>();
}
