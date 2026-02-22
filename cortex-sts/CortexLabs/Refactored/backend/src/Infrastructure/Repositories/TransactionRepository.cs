// FIX SMELL-1: parameterized SQL throughout
// FIX SMELL-6: LIMIT/OFFSET pagination
using Microsoft.Data.Sqlite;
using CortexLabs.FinTrack.Domain.Entities;
using CortexLabs.FinTrack.Domain.Interfaces;

namespace CortexLabs.FinTrack.Infrastructure.Repositories;

public class TransactionRepository : ITransactionRepository
{
    private readonly string _connectionString;
    public TransactionRepository(string connectionString) => _connectionString = connectionString;

    public async Task<Transaction?> GetByIdAsync(int id, CancellationToken ct = default)
    {
        using var conn = new SqliteConnection(_connectionString); conn.Open();
        using var cmd = conn.CreateCommand();
        cmd.CommandText = "SELECT * FROM Transactions WHERE Id=@id";
        cmd.Parameters.AddWithValue("@id", id);
        using var r = await cmd.ExecuteReaderAsync(ct);
        return r.Read() ? MapTx(r) : null;
    }

    public async Task<IReadOnlyList<Transaction>> GetByUserAsync(int userId, int page, int pageSize, CancellationToken ct = default)
    {
        using var conn = new SqliteConnection(_connectionString); conn.Open();
        using var cmd = conn.CreateCommand();
        cmd.CommandText = "SELECT * FROM Transactions WHERE UserId=@uid ORDER BY Date DESC LIMIT @limit OFFSET @offset";
        cmd.Parameters.AddWithValue("@uid", userId);
        cmd.Parameters.AddWithValue("@limit", pageSize);
        cmd.Parameters.AddWithValue("@offset", (page-1)*pageSize);
        using var r = await cmd.ExecuteReaderAsync(ct);
        var list = new List<Transaction>();
        while (r.Read()) list.Add(MapTx(r));
        return list;
    }

    public async Task<IReadOnlyList<Transaction>> SearchAsync(string? category, DateTime? dateFrom, int page, int pageSize, CancellationToken ct = default)
    {
        using var conn = new SqliteConnection(_connectionString); conn.Open();
        using var cmd = conn.CreateCommand();
        cmd.CommandText = "SELECT * FROM Transactions WHERE (@cat IS NULL OR CategoryName=@cat) AND (@df IS NULL OR Date>=@df) LIMIT @limit OFFSET @offset";
        cmd.Parameters.AddWithValue("@cat", (object?)category ?? DBNull.Value);
        cmd.Parameters.AddWithValue("@df", dateFrom.HasValue ? (object)dateFrom.Value.ToString("yyyy-MM-dd") : DBNull.Value);
        cmd.Parameters.AddWithValue("@limit", pageSize);
        cmd.Parameters.AddWithValue("@offset", (page-1)*pageSize);
        using var r = await cmd.ExecuteReaderAsync(ct);
        var list = new List<Transaction>();
        while (r.Read()) list.Add(MapTx(r));
        return list;
    }

    public async Task<Transaction> CreateAsync(Transaction tx, CancellationToken ct = default)
    {
        using var conn = new SqliteConnection(_connectionString); conn.Open();
        using var cmd = conn.CreateCommand();
        cmd.CommandText = "INSERT INTO Transactions (Description,Amount,CategoryName,Type,Date,UserId,CreatedAt,ModifiedAt) VALUES (@d,@a,@c,@t,@dt,@uid,@ca,@ma); SELECT last_insert_rowid();";
        cmd.Parameters.AddWithValue("@d", tx.Description);
        cmd.Parameters.AddWithValue("@a", (double)tx.Amount);
        cmd.Parameters.AddWithValue("@c", tx.CategoryName);
        cmd.Parameters.AddWithValue("@t", tx.Type.ToString());
        cmd.Parameters.AddWithValue("@dt", tx.Date.ToString("yyyy-MM-dd"));
        cmd.Parameters.AddWithValue("@uid", tx.UserId);
        cmd.Parameters.AddWithValue("@ca", DateTime.UtcNow.ToString("o"));
        cmd.Parameters.AddWithValue("@ma", DateTime.UtcNow.ToString("o"));
        var id = await cmd.ExecuteScalarAsync(ct);
        tx.Id = Convert.ToInt32(id);
        return tx;
    }

    private static Transaction MapTx(System.Data.Common.DbDataReader r) => new()
    {
        Id = r.GetInt32(0), Description = r.IsDBNull(1)?"":r.GetString(1),
        Amount = (decimal)r.GetDouble(2), CategoryName = r.IsDBNull(3)?"":r.GetString(3),
        Type = Enum.TryParse<TransactionType>(r.IsDBNull(4)?"Income":r.GetString(4), out var t)?t:TransactionType.Expense,
        Date = DateTime.Parse(r.GetString(5)), UserId = r.GetInt32(6),
    };
}