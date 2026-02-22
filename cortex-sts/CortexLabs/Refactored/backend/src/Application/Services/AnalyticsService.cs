// FIX SMELL-3 (analytics extracted from god class), SMELL-4, SMELL-6, SMELL-15
using CortexLabs.FinTrack.Domain.Entities;
using CortexLabs.FinTrack.Domain.Interfaces;
using Microsoft.Extensions.Logging;

namespace CortexLabs.FinTrack.Application.Services;

public class AnalyticsService
{
    private readonly ITransactionRepository _txRepo;
    private readonly ILogger<AnalyticsService> _logger;
    // FIX SMELL-15: named constants replace magic numbers
    private const decimal CriticalExpenseRatio = 1.5m;
    private const string HealthScoreHealthy = "healthy";
    private const string HealthScoreWarning = "warning";
    private const string HealthScoreCritical = "critical";

    public AnalyticsService(ITransactionRepository txRepo, ILogger<AnalyticsService> logger)
    {
        _txRepo = txRepo;
        _logger = logger;
    }

    public async Task<AnalyticsSummary> GetSummaryAsync(int userId, int page = 1, int pageSize = 1000, CancellationToken ct = default)
    {
        // FIX SMELL-6: paginated query — no "SELECT * FROM Transactions" full load
        var transactions = await _txRepo.GetByUserAsync(userId, page, pageSize, ct);
        _logger.LogInformation("Computing analytics for userId={UserId} txCount={Count}", userId, transactions.Count);
        return ComputeSummary(transactions);
    }

    private static AnalyticsSummary ComputeSummary(IReadOnlyList<Transaction> transactions)
    {
        var income = transactions.Where(t => t.Type == TransactionType.Income).Sum(t => t.Amount);
        var expenses = transactions.Where(t => t.Type == TransactionType.Expense).Sum(t => t.Amount);
        var avg = transactions.Any() ? transactions.Average(t => t.Amount) : 0m;
        var topCategory = transactions.GroupBy(t => t.CategoryName).OrderByDescending(g => g.Count()).FirstOrDefault()?.Key ?? "none";
        var health = income > expenses ? HealthScoreHealthy
            : expenses > income * CriticalExpenseRatio ? HealthScoreCritical
            : HealthScoreWarning;
        return new AnalyticsSummary(income, expenses, income - expenses, avg, topCategory, health, transactions.Count);
    }
}

public record AnalyticsSummary(decimal TotalIncome, decimal TotalExpenses, decimal NetPosition,
    decimal AverageTransaction, string TopCategory, string HealthScore, int TransactionCount);