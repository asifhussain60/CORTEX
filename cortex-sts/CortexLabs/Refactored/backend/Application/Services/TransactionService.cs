// ✅ SMELL-1 FIXED: Parameterized queries throughout
// ✅ SMELL-5 FIXED: No circular dependency — TransactionService is self-contained
// ✅ SMELL-6 FIXED: LIMIT/OFFSET pagination
// ✅ SMELL-11 FIXED: ILogger<T> structured logging
// ✅ SMELL-15 FIXED: Constants replace magic numbers; enums replace magic strings
// ✅ SMELL-17 FIXED: DI via constructor injection

using CortexLabs.FinTrack.Application.Interfaces;
using CortexLabs.FinTrack.Domain.Entities;
using CortexLabs.FinTrack.Domain.Enums;
using Microsoft.Data.Sqlite;
using Microsoft.Extensions.Logging;

namespace CortexLabs.FinTrack.Application.Services;

/// <summary>
/// Manages transaction CRUD and categorisation without dependency on UserService
/// (circular dependency eliminated — SMELL-5 fix).
/// </summary>
public sealed class TransactionService : ITransactionService
{
    private readonly string _connectionString;
    private readonly ILogger<TransactionService> _logger;

    // ✅ SMELL-15 FIXED: Named constants for categorisation thresholds
    private const decimal LargePurchaseThreshold = 10_000m;
    private const decimal MediumPurchaseThreshold = 1_000m;

    public TransactionService(IConfiguration configuration, ILogger<TransactionService> logger)
    {
        _connectionString = configuration.GetConnectionString("DefaultConnection")
            ?? throw new InvalidOperationException("DefaultConnection is required.");
        _logger = logger;
    }

    /// <inheritdoc/>
    public async Task<IEnumerable<Transaction>> GetTransactionsAsync(int page = 1, int pageSize = 25)
    {
        var offset = (page - 1) * pageSize;
        var results = new List<Transaction>();

        await using var conn = new SqliteConnection(_connectionString);
        await conn.OpenAsync();
        var cmd = conn.CreateCommand();
        // ✅ SMELL-6 FIXED: Paginated
        cmd.CommandText = "SELECT Id, description, Amount, category_name, Type, Date, UserId FROM Transactions LIMIT @limit OFFSET @offset";
        cmd.Parameters.AddWithValue("@limit", pageSize);
        cmd.Parameters.AddWithValue("@offset", offset);

        await using var reader = await cmd.ExecuteReaderAsync();
        while (await reader.ReadAsync())
        {
            results.Add(MapTransaction(reader));
        }

        _logger.LogInformation("Retrieved {Count} transactions (page {Page})", results.Count, page);
        return results;
    }

    /// <inheritdoc/>
    public async Task<IEnumerable<Transaction>> SearchAsync(
        TransactionCategory? category, DateOnly? from, int page = 1, int pageSize = 25)
    {
        var offset = (page - 1) * pageSize;
        var results = new List<Transaction>();

        await using var conn = new SqliteConnection(_connectionString);
        await conn.OpenAsync();
        var cmd = conn.CreateCommand();

        // ✅ SMELL-1 FIXED: Parameterized search — no string interpolation
        var sql = "SELECT Id, description, Amount, category_name, Type, Date, UserId FROM Transactions WHERE 1=1";
        if (category.HasValue)
        {
            sql += " AND category_name = @category";
            cmd.Parameters.AddWithValue("@category", category.Value.ToString());
        }
        if (from.HasValue)
        {
            sql += " AND Date >= @from";
            cmd.Parameters.AddWithValue("@from", from.Value.ToString("yyyy-MM-dd"));
        }
        sql += " LIMIT @limit OFFSET @offset";
        cmd.Parameters.AddWithValue("@limit", pageSize);
        cmd.Parameters.AddWithValue("@offset", offset);
        cmd.CommandText = sql;

        await using var reader = await cmd.ExecuteReaderAsync();
        while (await reader.ReadAsync())
        {
            results.Add(MapTransaction(reader));
        }

        return results;
    }

    /// <inheritdoc/>
    public async Task<Transaction> CreateAsync(Transaction transaction)
    {
        if (transaction.Category == TransactionCategory.Other && !string.IsNullOrEmpty(transaction.Description))
        {
            transaction.Category = await AutoCategoriseAsync(transaction.Amount, transaction.Description);
        }

        await using var conn = new SqliteConnection(_connectionString);
        await conn.OpenAsync();
        var cmd = conn.CreateCommand();
        // ✅ SMELL-1 FIXED: All values parameterized
        cmd.CommandText = @"
            INSERT INTO Transactions (description, Amount, category_name, Type, Date, UserId)
            VALUES (@desc, @amount, @cat, @type, @date, @userId)
            RETURNING Id";
        cmd.Parameters.AddWithValue("@desc", transaction.Description);
        cmd.Parameters.AddWithValue("@amount", (double)transaction.Amount);
        cmd.Parameters.AddWithValue("@cat", transaction.Category.ToString());
        cmd.Parameters.AddWithValue("@type", transaction.Type.ToString());
        cmd.Parameters.AddWithValue("@date", transaction.Date.ToString("yyyy-MM-dd"));
        cmd.Parameters.AddWithValue("@userId", transaction.UserId);

        var id = (long)(await cmd.ExecuteScalarAsync())!;
        transaction.Id = (int)id;

        _logger.LogInformation("Created transaction {TransactionId} for user {UserId}", transaction.Id, transaction.UserId);
        return transaction;
    }

    /// <inheritdoc/>
    public Task<TransactionCategory> AutoCategoriseAsync(decimal amount, string description)
    {
        // ✅ SMELL-15 FIXED: Named constants, not magic numbers
        // ✅ SMELL-15 FIXED: Enum values, not magic strings
        var lower = description.ToLowerInvariant();
        var category = amount switch
        {
            > LargePurchaseThreshold => TransactionCategory.LargePurchase,
            > MediumPurchaseThreshold => TransactionCategory.MediumPurchase,
            _ when lower.Contains("grocery") || lower.Contains("supermarket") => TransactionCategory.Food,
            _ when lower.Contains("gas") || lower.Contains("transport") || lower.Contains("uber") => TransactionCategory.Transport,
            _ when lower.Contains("netflix") || lower.Contains("spotify") || lower.Contains("cinema") => TransactionCategory.Entertainment,
            _ => TransactionCategory.Other
        };

        return Task.FromResult(category);
    }

    private static Transaction MapTransaction(SqliteDataReader r) => new()
    {
        Id = r.GetInt32(0),
        Description = r.IsDBNull(1) ? string.Empty : r.GetString(1),
        Amount = (decimal)r.GetDouble(2),
        Category = Enum.TryParse<TransactionCategory>(r.IsDBNull(3) ? "Other" : r.GetString(3), out var cat)
            ? cat : TransactionCategory.Other,
        Type = Enum.TryParse<TransactionType>(r.IsDBNull(4) ? "Expense" : r.GetString(4), out var t)
            ? t : TransactionType.Expense,
        Date = DateOnly.TryParse(r.GetString(5), out var d) ? d : DateOnly.FromDateTime(DateTime.UtcNow),
        UserId = r.GetInt32(6)
    };
}
