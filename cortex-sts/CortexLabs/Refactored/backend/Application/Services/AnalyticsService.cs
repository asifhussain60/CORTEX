// ✅ SMELL-6 FIXED: DB-side aggregation — no more loading all rows in-memory
// ✅ SMELL-11 FIXED: ILogger<T>
// ✅ SMELL-15 FIXED: Named constants for health thresholds; enums for type labels
// ✅ SMELL-17 FIXED: DI via constructor injection

using CortexLabs.FinTrack.Application.Interfaces;
using CortexLabs.FinTrack.Domain.Enums;
using Microsoft.Data.Sqlite;
using Microsoft.Extensions.Logging;

namespace CortexLabs.FinTrack.Application.Services;

/// <summary>
/// Computes financial analytics using DB aggregation (not in-memory full-table scan).
/// Addresses SMELL-6 performance issue.
/// </summary>
public sealed class AnalyticsService : IAnalyticsService
{
    private readonly string _connectionString;
    private readonly ILogger<AnalyticsService> _logger;

    // ✅ SMELL-15 FIXED: Named constant for health threshold
    private const decimal CriticalExpenseRatio = 1.5m;

    public AnalyticsService(IConfiguration configuration, ILogger<AnalyticsService> logger)
    {
        _connectionString = configuration.GetConnectionString("DefaultConnection")
            ?? throw new InvalidOperationException("DefaultConnection is required.");
        _logger = logger;
    }

    /// <inheritdoc/>
    public async Task<AnalyticsSummary> GetSummaryAsync()
    {
        await using var conn = new SqliteConnection(_connectionString);
        await conn.OpenAsync();

        // ✅ SMELL-6 FIXED: DB-side aggregation — SUM/AVG/GROUP BY pushed to SQLite
        var aggCmd = conn.CreateCommand();
        aggCmd.CommandText = @"
            SELECT
                COALESCE(SUM(CASE WHEN Type = @income THEN Amount ELSE 0 END), 0) AS TotalIncome,
                COALESCE(SUM(CASE WHEN Type = @expense THEN Amount ELSE 0 END), 0) AS TotalExpenses,
                COALESCE(AVG(Amount), 0) AS AvgTransaction,
                COUNT(*) AS TxCount
            FROM Transactions";
        aggCmd.Parameters.AddWithValue("@income", TransactionType.Income.ToString());
        aggCmd.Parameters.AddWithValue("@expense", TransactionType.Expense.ToString());

        decimal totalIncome = 0, totalExpenses = 0, avgTx = 0;
        int txCount = 0;

        await using (var r = await aggCmd.ExecuteReaderAsync())
        {
            if (await r.ReadAsync())
            {
                totalIncome = (decimal)r.GetDouble(0);
                totalExpenses = (decimal)r.GetDouble(1);
                avgTx = (decimal)r.GetDouble(2);
                txCount = r.GetInt32(3);
            }
        }

        var topCmd = conn.CreateCommand();
        topCmd.CommandText = @"
            SELECT category_name, COUNT(*) AS cnt
            FROM Transactions
            WHERE Type = @expense
            GROUP BY category_name
            ORDER BY cnt DESC
            LIMIT 1";
        topCmd.Parameters.AddWithValue("@expense", TransactionType.Expense.ToString());

        var topCategory = "none";
        await using (var r = await topCmd.ExecuteReaderAsync())
        {
            if (await r.ReadAsync()) topCategory = r.GetString(0);
        }

        var healthScore = totalIncome > totalExpenses ? "Healthy"
            : totalExpenses > totalIncome * CriticalExpenseRatio ? "Critical"
            : "Warning";

        _logger.LogInformation("Analytics summary: Income={Income:C} Expenses={Expenses:C} Health={Health}",
            totalIncome, totalExpenses, healthScore);

        return new AnalyticsSummary(totalIncome, totalExpenses, totalIncome - totalExpenses,
            avgTx, topCategory, healthScore, txCount);
    }
}
