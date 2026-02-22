using CortexLabs.FinTrack.Domain.Entities;
using CortexLabs.FinTrack.Domain.Enums;
using CortexLabs.FinTrack.Domain.Interfaces;
using Microsoft.Data.Sqlite;

namespace CortexLabs.FinTrack.Infrastructure.Repositories;

/// <summary>
/// SQLite account repository — fixes SMELL-09 (SQL injection) via parameterized
/// queries, SMELL-02 (implements DI interface). No EF Core — ADR-002.
/// </summary>
public class AccountRepository : IAccountRepository
{
    private readonly string _connectionString;

    public AccountRepository(string connectionString)
    {
        _connectionString = connectionString;
    }

    public async Task<Account?> GetByIdAsync(int id)
    {
        await using var connection = new SqliteConnection(_connectionString);
        await connection.OpenAsync();

        await using var command = connection.CreateCommand();
        command.CommandText = "SELECT Id, UserId, Name, Type, Balance, Currency, CreatedAt, UpdatedAt FROM Accounts WHERE Id = @Id";
        command.Parameters.AddWithValue("@Id", id);

        await using var reader = await command.ExecuteReaderAsync();
        return await reader.ReadAsync() ? MapFromReader(reader) : null;
    }

    public async Task<IReadOnlyList<Account>> GetByUserIdAsync(int userId)
    {
        await using var connection = new SqliteConnection(_connectionString);
        await connection.OpenAsync();

        await using var command = connection.CreateCommand();
        command.CommandText = "SELECT Id, UserId, Name, Type, Balance, Currency, CreatedAt, UpdatedAt FROM Accounts WHERE UserId = @UserId ORDER BY Name";
        command.Parameters.AddWithValue("@UserId", userId);

        var accounts = new List<Account>();
        await using var reader = await command.ExecuteReaderAsync();
        while (await reader.ReadAsync())
            accounts.Add(MapFromReader(reader));

        return accounts;
    }

    public async Task<IReadOnlyList<Account>> GetAllAsync(int page, int pageSize)
    {
        await using var connection = new SqliteConnection(_connectionString);
        await connection.OpenAsync();

        await using var command = connection.CreateCommand();
        command.CommandText = "SELECT Id, UserId, Name, Type, Balance, Currency, CreatedAt, UpdatedAt FROM Accounts ORDER BY Id LIMIT @Limit OFFSET @Offset";
        command.Parameters.AddWithValue("@Limit", pageSize);
        command.Parameters.AddWithValue("@Offset", (page - 1) * pageSize);

        var accounts = new List<Account>();
        await using var reader = await command.ExecuteReaderAsync();
        while (await reader.ReadAsync())
            accounts.Add(MapFromReader(reader));

        return accounts;
    }

    public async Task<int> CreateAsync(Account account)
    {
        await using var connection = new SqliteConnection(_connectionString);
        await connection.OpenAsync();

        await using var command = connection.CreateCommand();
        command.CommandText = @"
            INSERT INTO Accounts (UserId, Name, Type, Balance, Currency, CreatedAt, UpdatedAt)
            VALUES (@UserId, @Name, @Type, @Balance, @Currency, @CreatedAt, @UpdatedAt);
            SELECT last_insert_rowid();";
        command.Parameters.AddWithValue("@UserId", account.UserId);
        command.Parameters.AddWithValue("@Name", account.Name);
        command.Parameters.AddWithValue("@Type", account.Type.ToString());
        command.Parameters.AddWithValue("@Balance", (double)account.Balance);
        command.Parameters.AddWithValue("@Currency", account.Currency);
        command.Parameters.AddWithValue("@CreatedAt", account.CreatedAt.ToString("o"));
        command.Parameters.AddWithValue("@UpdatedAt", account.UpdatedAt.ToString("o"));

        var result = await command.ExecuteScalarAsync();
        return Convert.ToInt32(result);
    }

    public async Task<bool> UpdateAsync(Account account)
    {
        await using var connection = new SqliteConnection(_connectionString);
        await connection.OpenAsync();

        await using var command = connection.CreateCommand();
        command.CommandText = @"
            UPDATE Accounts SET UserId = @UserId, Name = @Name, Type = @Type,
            Balance = @Balance, Currency = @Currency, UpdatedAt = @UpdatedAt
            WHERE Id = @Id";
        command.Parameters.AddWithValue("@Id", account.Id);
        command.Parameters.AddWithValue("@UserId", account.UserId);
        command.Parameters.AddWithValue("@Name", account.Name);
        command.Parameters.AddWithValue("@Type", account.Type.ToString());
        command.Parameters.AddWithValue("@Balance", (double)account.Balance);
        command.Parameters.AddWithValue("@Currency", account.Currency);
        command.Parameters.AddWithValue("@UpdatedAt", DateTime.UtcNow.ToString("o"));

        return await command.ExecuteNonQueryAsync() > 0;
    }

    public async Task<bool> DeleteAsync(int id)
    {
        await using var connection = new SqliteConnection(_connectionString);
        await connection.OpenAsync();

        await using var command = connection.CreateCommand();
        command.CommandText = "DELETE FROM Accounts WHERE Id = @Id";
        command.Parameters.AddWithValue("@Id", id);

        return await command.ExecuteNonQueryAsync() > 0;
    }

    public async Task<int> GetCountAsync()
    {
        await using var connection = new SqliteConnection(_connectionString);
        await connection.OpenAsync();

        await using var command = connection.CreateCommand();
        command.CommandText = "SELECT COUNT(*) FROM Accounts";

        return Convert.ToInt32(await command.ExecuteScalarAsync());
    }

    private static Account MapFromReader(SqliteDataReader reader) => new()
    {
        Id = reader.GetInt32(0),
        UserId = reader.GetInt32(1),
        Name = reader.GetString(2),
        Type = Enum.Parse<AccountType>(reader.GetString(3)),
        Balance = (decimal)reader.GetDouble(4),
        Currency = reader.GetString(5),
        CreatedAt = DateTime.Parse(reader.GetString(6)),
        UpdatedAt = DateTime.Parse(reader.GetString(7))
    };
}
