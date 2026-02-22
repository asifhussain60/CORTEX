// FIX SMELL-1: parameterized SQL
// FIX SMELL-4: atomic transfer wrapped in SQLite transaction
using Microsoft.Data.Sqlite;
using CortexLabs.FinTrack.Domain.Entities;
using CortexLabs.FinTrack.Domain.Interfaces;

namespace CortexLabs.FinTrack.Infrastructure.Repositories;

public class AccountRepository : IAccountRepository
{
    private readonly string _connectionString;
    public AccountRepository(string connectionString) => _connectionString = connectionString;

    public async Task<Account?> GetByIdAsync(int id, CancellationToken ct = default)
    {
        using var conn = new SqliteConnection(_connectionString); conn.Open();
        using var cmd = conn.CreateCommand();
        cmd.CommandText = "SELECT * FROM Accounts WHERE Id=@id";
        cmd.Parameters.AddWithValue("@id", id);
        using var r = await cmd.ExecuteReaderAsync(ct);
        return r.Read() ? MapAccount(r) : null;
    }

    public async Task<IReadOnlyList<Account>> GetByUserAsync(int userId, CancellationToken ct = default)
    {
        using var conn = new SqliteConnection(_connectionString); conn.Open();
        using var cmd = conn.CreateCommand();
        cmd.CommandText = "SELECT * FROM Accounts WHERE UserId=@uid";
        cmd.Parameters.AddWithValue("@uid", userId);
        using var r = await cmd.ExecuteReaderAsync(ct);
        var list = new List<Account>();
        while (r.Read()) list.Add(MapAccount(r));
        return list;
    }

    // FIX: atomic transfer — both debits in one SQLite transaction
    public async Task TransferAsync(int fromId, int toId, decimal amount, CancellationToken ct = default)
    {
        using var conn = new SqliteConnection(_connectionString); conn.Open();
        using var tx = conn.BeginTransaction();
        try
        {
            using var cmd1 = conn.CreateCommand();
            cmd1.Transaction = tx;
            cmd1.CommandText = "UPDATE Accounts SET Balance=Balance-@amt WHERE Id=@from";
            cmd1.Parameters.AddWithValue("@amt", (double)amount);
            cmd1.Parameters.AddWithValue("@from", fromId);
            await cmd1.ExecuteNonQueryAsync(ct);

            using var cmd2 = conn.CreateCommand();
            cmd2.Transaction = tx;
            cmd2.CommandText = "UPDATE Accounts SET Balance=Balance+@amt WHERE Id=@to";
            cmd2.Parameters.AddWithValue("@amt", (double)amount);
            cmd2.Parameters.AddWithValue("@to", toId);
            await cmd2.ExecuteNonQueryAsync(ct);

            tx.Commit();
        }
        catch
        {
            tx.Rollback();
            throw;
        }
    }

    public async Task UpdateAsync(Account account, CancellationToken ct = default)
    {
        using var conn = new SqliteConnection(_connectionString); conn.Open();
        using var cmd = conn.CreateCommand();
        cmd.CommandText = "UPDATE Accounts SET Balance=@b,ModifiedAt=@ma WHERE Id=@id";
        cmd.Parameters.AddWithValue("@b", (double)account.Balance);
        cmd.Parameters.AddWithValue("@ma", DateTime.UtcNow.ToString("o"));
        cmd.Parameters.AddWithValue("@id", account.Id);
        await cmd.ExecuteNonQueryAsync(ct);
    }

    private static Account MapAccount(System.Data.Common.DbDataReader r) => new()
    {
        Id = r.GetInt32(0), AccountName = r.IsDBNull(1)?"":r.GetString(1),
        Balance = (decimal)r.GetDouble(2), UserId = r.GetInt32(3),
    };
}