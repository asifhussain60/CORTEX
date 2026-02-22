// FIX SMELL-17: Service interface — Program.cs injects IReportService
// FIX SMELL-5: Dependency inversion
// FIX SMELL-15: enum ReportType replaces magic strings
using CortexLabs.FinTrack.Domain.Entities;

namespace CortexLabs.FinTrack.Application.Interfaces;

public interface IReportService
{
    Task<Report> GenerateAsync(ReportType type, int userId, CancellationToken ct = default);
}
