using CortexLabs.FinTrack.Domain.Entities;
using CortexLabs.FinTrack.Domain.Enums;
using CortexLabs.FinTrack.Domain.Interfaces;
using Microsoft.Data.Sqlite;

namespace CortexLabs.FinTrack.Infrastructure.Repositories;

/// <summary>
/// SQLite transaction repository — fixes SMELL-09 (SQL injection) via parameterized
/// queries, SMELL-02 (implements DI interface). No EF Core — ADR-002.
/// </summary>
public class TransactionRepository : ITransactionRepository
{
    private readonly string _connectionString;

    public TransactionRepository(string connectionString)
    {
        _connectionString = connectionString;
    }

    public async Task<Transaction?> GetByIdAsync(int id)
    {
        await using var connection = new SqliteConnection(_connectionString);
        await connection.OpenAsync();

        await using var command = connection.CreateCommand();
        command.CommandText = "SELECT Id, UserId, Amount, Type, Category, Description, Date, CreatedAt, UpdatedAt FROM Transactions WHERE Id = @Id";
        command.Parameters.AddWithValue("@Id", id);

        await using var reader = await command.ExecuteReaderAsync();
        return await reader.ReadAsync() ? MapFromReader(reader) : null;
    }

    public async Task<IReadOnlyList<Transaction>> GetByUserIdAsync(int userId, int page, int pageSize)
    {
        await using var connection = new SqliteConnection(_connectionString);
        await connection.OpenAsync();

        await using var command = connection.CreateCommand();
        command.CommandText = @"
            SELECT Id, UserId, Amount, Type, Category, Description, Date, CreatedAt, UpdatedAt
            FROM Transactions WHERE UserId = @UserId
            ORDER BY Date DESC LIMIT @Limit OFFSET @Offset";
        command.Parameters.AddWithValue("@UserId", userId);
        command.Parameters.AddWithValue("@Limit", pageSize);
        command.Parameters.AddWithValue("@Offset", (page - 1) * pageSize);

        var transactions = new List<Transaction>();
        await using var reader = await command.ExecuteReaderAsync();
        while (await reader.ReadAsync())
            transactions.Add(MapFromReader(reader));

        return transactions;
    }

    public async Task<IReadOnlyList<Transaction>> GetAllAsync(int page, int pageSize)
    {
        await using var connection = new SqliteConnection(_connectionString);
        await connection.OpenAsync();

        await using var command = connection.CreateCommand();
        command.CommandText = @"
            SELECT Id, UserId, Amount, Type, Category, Description, Date, CreatedAt, UpdatedAt
            FROM Transactions ORDER BY Date DESC LIMIT @Limit OFFSET @Offset";
        command.Parameters.AddWithValue("@Limit", pageSize);
        command.Parameters.AddWithValue("@Offset", (page - 1) * pageSize);

        var transactions = new List<Transaction>();
        await using var reader = await command.ExecuteReaderAsync();
        while (await reader.ReadAsync())
            transactions.Add(MapFromReader(reader));

        return transactions;
    }

    public async Task<int> CreateAsync(Transaction transaction)
    {
        await using var connection = new SqliteConnection(_connectionString);
        await connection.OpenAsync();

        await using var command = connection.CreateCommand();
        command.CommandText = @"
            INSERT INTO Transactions (UserId, Amount, Type, Category, Description, Date, CreatedAt, UpdatedAt)
            VALUES (@UserId, @Amount, @Type, @Category, @Description, @Date, @CreatedAt, @UpdatedAt);
            SELECT last_insert_rowid();";
        command.Parameters.AddWithValue("@UserId", transaction.UserId);
        command.Parameters.AddWithValue("@Amount", (double)transaction.Amount);
        command.Parameters.AddWithValue("@Type", transaction.Type.ToString());
        command.Parameters.AddWithValue("@Category", transaction.Category.ToString());
        command.Parameters.AddWithValue("@Description", transaction.Description);
        command.Parameters.AddWithValue("@Date", transaction.Date.ToString("o"));
        command.Parameters.AddWithValue("@CreatedAt", transaction.CreatedAt.ToString("o"));
        command.Parameters.AddWithValue("@UpdatedAt", transaction.UpdatedAt.ToString("o"));

        var result = await command.ExecuteScalarAsync();
        return Convert.ToInt32(result);
    }

    public async Task<bool> UpdateAsync(Transaction transaction)
    {
        await using var connection = new SqliteConnection(_connectionString);
        await connection.OpenAsync();

        await using var command = connection.CreateCommand();
        command.CommandText = @"
            UPDATE Transactions SET UserId = @UserId, Amount = @Amount, Type = @Type,
            Category = @Category, Description = @Description, Date = @Date, UpdatedAt = @UpdatedAt
            WHERE Id = @Id";
        command.Parameters.AddWithValue("@Id", transaction.Id);
        command.Parameters.AddWithValue("@UserId", transaction.UserId);
        command.Parameters.AddWithValue("@Amount", (double)transaction.Amount);
        command.Parameters.AddWithValue("@Type", transaction.Type.ToString());
        command.Parameters.AddWithValue("@Category", transaction.Category.ToString());
        command.Parameters.AddWithValue("@Description", transaction.Description);
        command.Parameters.AddWithValue("@Date", transaction.Date.ToString("o"));
        command.Parameters.AddWithValue("@UpdatedAt", DateTime.UtcNow.ToString("o"));

        return await command.ExecuteNonQueryAsync() > 0;
    }

    public async Task<bool> DeleteAsync(int id)
    {
        await using var connection = new SqliteConnection(_connectionString);
        await connection.OpenAsync();

        await using var command = connection.CreateCommand();
        command.CommandText = "DELETE FROM Transactions WHERE Id = @Id";
        command.Parameters.AddWithValue("@Id", id);

        return await command.ExecuteNonQueryAsync() > 0;
    }

    public async Task<int> GetCountAsync()
    {
        await using var connection = new SqliteConnection(_connectionString);
        await connection.OpenAsync();

        await using var command = connection.CreateCommand();
        command.CommandText = "SELECT COUNT(*) FROM Transactions";

        return Convert.ToInt32(await command.ExecuteScalarAsync());
    }

    public async Task<int> GetCountByUserIdAsync(int userId)
    {
        await using var connection = new SqliteConnection(_connectionString);
        await connection.OpenAsync();

        await using var command = connection.CreateCommand();
        command.CommandText = "SELECT COUNT(*) FROM Transactions WHERE UserId = @UserId";
        command.Parameters.AddWithValue("@UserId", userId);

        return Convert.ToInt32(await command.ExecuteScalarAsync());
    }

    public async Task<decimal> GetTotalByUserIdAsync(int userId)
    {
        await using var connection = new SqliteConnection(_connectionString);
        await connection.OpenAsync();

        await using var command = connection.CreateCommand();
        command.CommandText = "SELECT COALESCE(SUM(Amount), 0) FROM Transactions WHERE UserId = @UserId";
        command.Parameters.AddWithValue("@UserId", userId);

        var result = await command.ExecuteScalarAsync();
        return Convert.ToDecimal(result);
    }

    private static Transaction MapFromReader(SqliteDataReader reader) => new()
    {
        Id = reader.GetInt32(0),
        UserId = reader.GetInt32(1),
        Amount = (decimal)reader.GetDouble(2),
        Type = Enum.Parse<TransactionType>(reader.GetString(3)),
        Category = Enum.Parse<TransactionCategory>(reader.GetString(4)),
        Description = reader.GetString(5),
        Date = DateTime.Parse(reader.GetString(6)),
        CreatedAt = DateTime.Parse(reader.GetString(7)),
        UpdatedAt = DateTime.Parse(reader.GetString(8))
    };
}
