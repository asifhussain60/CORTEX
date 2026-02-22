// ✅ SMELL-17 FIXED: Interface contract for DI

using CortexLabs.FinTrack.Domain.Entities;
using CortexLabs.FinTrack.Domain.Enums;

namespace CortexLabs.FinTrack.Application.Interfaces;

/// <summary>Contract for report generation operations.</summary>
public interface IReportService
{
    Task<IEnumerable<Report>> GetReportsAsync(int page = 1, int pageSize = 25);
    Task<Report> GenerateAsync(ReportType type, int requestedBy);
}
