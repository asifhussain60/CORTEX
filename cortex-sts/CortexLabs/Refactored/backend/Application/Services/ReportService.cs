// ✅ SMELL-1 FIXED: Parameterized queries
// ✅ SMELL-6 FIXED: Paginated report listing
// ✅ SMELL-11 FIXED: ILogger<T>
// ✅ SMELL-15 FIXED: ReportType enum — no magic strings

using CortexLabs.FinTrack.Application.Interfaces;
using CortexLabs.FinTrack.Domain.Entities;
using CortexLabs.FinTrack.Domain.Enums;
using Microsoft.Data.Sqlite;
using Microsoft.Extensions.Logging;

namespace CortexLabs.FinTrack.Application.Services;

/// <summary>Generates and retrieves financial reports.</summary>
public sealed class ReportService : IReportService
{
    private readonly string _connectionString;
    private readonly ILogger<ReportService> _logger;

    public ReportService(IConfiguration configuration, ILogger<ReportService> logger)
    {
        _connectionString = configuration.GetConnectionString("DefaultConnection")
            ?? throw new InvalidOperationException("DefaultConnection is required.");
        _logger = logger;
    }

    /// <inheritdoc/>
    public async Task<IEnumerable<Report>> GetReportsAsync(int page = 1, int pageSize = 25)
    {
        var offset = (page - 1) * pageSize;
        var reports = new List<Report>();

        await using var conn = new SqliteConnection(_connectionString);
        await conn.OpenAsync();
        var cmd = conn.CreateCommand();
        cmd.CommandText = "SELECT Id, title, Content, generated_by, generated_at FROM Reports LIMIT @limit OFFSET @offset";
        cmd.Parameters.AddWithValue("@limit", pageSize);
        cmd.Parameters.AddWithValue("@offset", offset);

        await using var reader = await cmd.ExecuteReaderAsync();
        while (await reader.ReadAsync())
        {
            reports.Add(MapReport(reader));
        }

        return reports;
    }

    /// <inheritdoc/>
    public async Task<Report> GenerateAsync(ReportType type, int requestedBy)
    {
        // ✅ SMELL-15 FIXED: Enum-driven content, no magic strings
        var content = type switch
        {
            ReportType.Monthly => "Monthly financial summary — income vs. expenses by category.",
            ReportType.Annual => "Annual financial summary — full year income, expenses, net position.",
            ReportType.Tax => "Tax report — taxable income, deductions, estimated liability.",
            ReportType.Custom => "Custom report — filtered by user-supplied parameters.",
            _ => throw new ArgumentOutOfRangeException(nameof(type))
        };

        var report = new Report
        {
            Title = $"{type} Report",
            Content = content,
            GeneratedBy = requestedBy,
            GeneratedAt = DateTime.UtcNow,
            Type = type
        };

        await using var conn = new SqliteConnection(_connectionString);
        await conn.OpenAsync();
        var cmd = conn.CreateCommand();
        // ✅ SMELL-1 FIXED: Parameterized INSERT
        cmd.CommandText = @"
            INSERT INTO Reports (title, Content, generated_by, generated_at)
            VALUES (@title, @content, @by, @at)
            RETURNING Id";
        cmd.Parameters.AddWithValue("@title", report.Title);
        cmd.Parameters.AddWithValue("@content", report.Content);
        cmd.Parameters.AddWithValue("@by", report.GeneratedBy);
        cmd.Parameters.AddWithValue("@at", report.GeneratedAt.ToString("o"));

        var id = (long)(await cmd.ExecuteScalarAsync())!;
        report.Id = (int)id;

        _logger.LogInformation("Generated {ReportType} report {ReportId} for user {UserId}",
            type, report.Id, requestedBy);
        return report;
    }

    private static Report MapReport(SqliteDataReader r) => new()
    {
        Id = r.GetInt32(0),
        Title = r.IsDBNull(1) ? string.Empty : r.GetString(1),
        Content = r.IsDBNull(2) ? string.Empty : r.GetString(2),
        GeneratedBy = r.GetInt32(3),
        GeneratedAt = DateTime.TryParse(r.GetString(4), out var dt) ? dt : DateTime.UtcNow
    };
}
