// FIX SMELL-3 (report logic extracted), SMELL-15 (enum replaces magic strings)
using CortexLabs.FinTrack.Domain.Entities;
using CortexLabs.FinTrack.Domain.Interfaces;
using Microsoft.Extensions.Logging;

namespace CortexLabs.FinTrack.Application.Services;

public class ReportService
{
    private readonly IUserRepository _userRepo;
    private readonly ILogger<ReportService> _logger;

    public ReportService(IUserRepository userRepo, ILogger<ReportService> logger)
    {
        _userRepo = userRepo;
        _logger = logger;
    }

    // FIX SMELL-15: enum parameter replaces magic string
    public Task<Report> GenerateAsync(ReportType type, int userId, CancellationToken ct = default)
    {
        _logger.LogInformation("Generating {ReportType} report for userId={UserId}", type, userId);
        var content = type switch
        {
            ReportType.Monthly => "Monthly financial summary.",
            ReportType.Annual  => "Annual financial summary.",
            ReportType.Tax     => "Tax report summary.",
            _                  => throw new ArgumentOutOfRangeException(nameof(type))
        };
        var report = new Report
        {
            Title = $"{type} Report",
            Content = content,
            GeneratedBy = userId,
            GeneratedAt = DateTime.UtcNow,
            ReportType = type,
        };
        return Task.FromResult(report);
    }
}