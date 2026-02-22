// FIX SMELL-1: ALL queries use SqliteParameter — zero SQL injection
// FIX SMELL-16: no global mutable state (AppCache removed)
// FIX SMELL-8: dead NotificationService removed — clean class
using Microsoft.Data.Sqlite;
using CortexLabs.FinTrack.Domain.Entities;
using CortexLabs.FinTrack.Domain.Interfaces;

namespace CortexLabs.FinTrack.Infrastructure.Repositories;

public class UserRepository : IUserRepository
{
    private readonly string _connectionString;

    public UserRepository(string connectionString)
    {
        _connectionString = connectionString;
    }

    private SqliteConnection OpenConnection()
    {
        var conn = new SqliteConnection(_connectionString);
        conn.Open();
        return conn;
    }

    public async Task<User?> GetByIdAsync(int id, CancellationToken ct = default)
    {
        using var conn = OpenConnection();
        using var cmd = conn.CreateCommand();
        // FIX SMELL-1: parameterized query
        cmd.CommandText = "SELECT Id,UserName,Email,PasswordHash,Role,IsActive,CreatedAt,ModifiedAt FROM Users WHERE Id=@id AND IsDeleted=0";
        cmd.Parameters.AddWithValue("@id", id);
        using var r = await cmd.ExecuteReaderAsync(ct);
        return r.Read() ? MapUser(r) : null;
    }

    public async Task<User?> GetByUsernameAsync(string username, CancellationToken ct = default)
    {
        using var conn = OpenConnection();
        using var cmd = conn.CreateCommand();
        cmd.CommandText = "SELECT Id,UserName,Email,PasswordHash,Role,IsActive,CreatedAt,ModifiedAt FROM Users WHERE UserName=@u AND IsDeleted=0";
        cmd.Parameters.AddWithValue("@u", username);
        using var r = await cmd.ExecuteReaderAsync(ct);
        return r.Read() ? MapUser(r) : null;
    }

    public async Task<IReadOnlyList<User>> GetPagedAsync(int page, int pageSize, CancellationToken ct = default)
    {
        // FIX SMELL-6: LIMIT + OFFSET pagination
        using var conn = OpenConnection();
        using var cmd = conn.CreateCommand();
        cmd.CommandText = "SELECT Id,UserName,Email,PasswordHash,Role,IsActive,CreatedAt,ModifiedAt FROM Users WHERE IsDeleted=0 ORDER BY Id LIMIT @limit OFFSET @offset";
        cmd.Parameters.AddWithValue("@limit", pageSize);
        cmd.Parameters.AddWithValue("@offset", (page - 1) * pageSize);
        using var r = await cmd.ExecuteReaderAsync(ct);
        var list = new List<User>();
        while (r.Read()) list.Add(MapUser(r));
        return list;
    }

    public async Task<User> CreateAsync(User user, CancellationToken ct = default)
    {
        // FIX SMELL-2: password MUST be a hash — never plaintext
        using var conn = OpenConnection();
        using var cmd = conn.CreateCommand();
        cmd.CommandText = "INSERT INTO Users (UserName,Email,PasswordHash,Role,IsActive,IsDeleted,CreatedAt,ModifiedAt) VALUES (@u,@e,@ph,@r,1,0,@ca,@ma); SELECT last_insert_rowid();";
        cmd.Parameters.AddWithValue("@u", user.UserName);
        cmd.Parameters.AddWithValue("@e", user.Email);
        cmd.Parameters.AddWithValue("@ph", user.PasswordHash);
        cmd.Parameters.AddWithValue("@r", user.Role);
        cmd.Parameters.AddWithValue("@ca", user.CreatedAt.ToString("o"));
        cmd.Parameters.AddWithValue("@ma", user.ModifiedAt.ToString("o"));
        var id = await cmd.ExecuteScalarAsync(ct);
        user.Id = Convert.ToInt32(id);
        return user;
    }

    public async Task UpdateAsync(User user, CancellationToken ct = default)
    {
        using var conn = OpenConnection();
        using var cmd = conn.CreateCommand();
        cmd.CommandText = "UPDATE Users SET Email=@e,Role=@r,IsActive=@a,ModifiedAt=@ma WHERE Id=@id";
        cmd.Parameters.AddWithValue("@e", user.Email);
        cmd.Parameters.AddWithValue("@r", user.Role);
        cmd.Parameters.AddWithValue("@a", user.IsActive ? 1 : 0);
        cmd.Parameters.AddWithValue("@ma", DateTime.UtcNow.ToString("o"));
        cmd.Parameters.AddWithValue("@id", user.Id);
        await cmd.ExecuteNonQueryAsync(ct);
    }

    public async Task SoftDeleteAsync(int id, CancellationToken ct = default)
    {
        // FIX SMELL-18: soft delete — audit trail preserved
        using var conn = OpenConnection();
        using var cmd = conn.CreateCommand();
        cmd.CommandText = "UPDATE Users SET IsDeleted=1,ModifiedAt=@ma WHERE Id=@id";
        cmd.Parameters.AddWithValue("@ma", DateTime.UtcNow.ToString("o"));
        cmd.Parameters.AddWithValue("@id", id);
        await cmd.ExecuteNonQueryAsync(ct);
    }

    private static User MapUser(System.Data.Common.DbDataReader r) => new()
    {
        Id = r.GetInt32(0), UserName = r.GetString(1), Email = r.GetString(2),
        PasswordHash = r.GetString(3), Role = r.GetString(4),
        IsActive = r.GetInt32(5) == 1,
    };
}