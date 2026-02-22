// ✅ SMELL-17 FIXED: Interface contract for DI

namespace CortexLabs.FinTrack.Application.Interfaces;

/// <summary>Contract for analytics summary computations.</summary>
public interface IAnalyticsService
{
    Task<AnalyticsSummary> GetSummaryAsync();
}

/// <summary>Immutable analytics snapshot.</summary>
public record AnalyticsSummary(
    decimal TotalIncome,
    decimal TotalExpenses,
    decimal NetPosition,
    decimal AverageTransaction,
    string TopCategory,
    string HealthScore,
    int TransactionCount
);
