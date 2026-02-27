// FIX SMELL-17: Service interface — Program.cs injects IAnalyticsService
// FIX SMELL-5: Dependency inversion
using CortexLabs.FinTrack.Application.Services;

namespace CortexLabs.FinTrack.Application.Interfaces;

public interface IAnalyticsService
{
    // FIX SMELL-6: paginated analytics — no full-table scan
    Task<AnalyticsSummary> GetSummaryAsync(int userId, int page = 1, int pageSize = 1000, CancellationToken ct = default);
}
