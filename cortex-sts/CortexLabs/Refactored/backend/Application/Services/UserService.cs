// ✅ SMELL-1 FIXED: Parameterized queries via SqliteParameter — no string concatenation
// ✅ SMELL-6 FIXED: LIMIT/OFFSET pagination on all queries
// ✅ SMELL-11 FIXED: ILogger<T> structured logging — no Console.WriteLine
// ✅ SMELL-17 FIXED: Constructor-injected via DI (AddScoped in Program.cs)

using CortexLabs.FinTrack.Application.Interfaces;
using CortexLabs.FinTrack.Domain.Entities;
using Microsoft.Data.Sqlite;
using Microsoft.Extensions.Logging;

namespace CortexLabs.FinTrack.Application.Services;

/// <summary>Manages user CRUD operations via parameterised SQL (SMELL-1 fix).</summary>
public sealed class UserService : IUserService
{
    private readonly string _connectionString;
    private readonly ILogger<UserService> _logger;

    public UserService(IConfiguration configuration, ILogger<UserService> logger)
    {
        _connectionString = configuration.GetConnectionString("DefaultConnection")
            ?? throw new InvalidOperationException("DefaultConnection is required.");
        _logger = logger;
    }

    /// <inheritdoc/>
    public async Task<IEnumerable<User>> GetUsersAsync(int page = 1, int pageSize = 25)
    {
        // ✅ SMELL-6 FIXED: LIMIT + OFFSET pagination
        var offset = (page - 1) * pageSize;
        var users = new List<User>();

        await using var conn = new SqliteConnection(_connectionString);
        await conn.OpenAsync();
        var cmd = conn.CreateCommand();
        cmd.CommandText = "SELECT Id, user_name, Email, Role, is_active FROM Users WHERE IsDeleted = 0 LIMIT @limit OFFSET @offset";
        cmd.Parameters.AddWithValue("@limit", pageSize);
        cmd.Parameters.AddWithValue("@offset", offset);

        await using var reader = await cmd.ExecuteReaderAsync();
        while (await reader.ReadAsync())
        {
            users.Add(MapUser(reader));
        }

        _logger.LogInformation("Retrieved {Count} users (page {Page})", users.Count, page);
        return users;
    }

    /// <inheritdoc/>
    public async Task<User?> GetByIdAsync(int id)
    {
        await using var conn = new SqliteConnection(_connectionString);
        await conn.OpenAsync();
        var cmd = conn.CreateCommand();
        // ✅ SMELL-1 FIXED: @id parameter — no string interpolation
        cmd.CommandText = "SELECT Id, user_name, Email, Role, is_active FROM Users WHERE Id = @id AND IsDeleted = 0";
        cmd.Parameters.AddWithValue("@id", id);

        await using var reader = await cmd.ExecuteReaderAsync();
        return await reader.ReadAsync() ? MapUser(reader) : null;
    }

    /// <inheritdoc/>
    public async Task<User?> FindByUsernameAsync(string username)
    {
        await using var conn = new SqliteConnection(_connectionString);
        await conn.OpenAsync();
        var cmd = conn.CreateCommand();
        // ✅ SMELL-1 FIXED: parameterized query
        cmd.CommandText = "SELECT Id, user_name, Email, PasswordHash, Role, is_active FROM Users WHERE user_name = @username AND IsDeleted = 0";
        cmd.Parameters.AddWithValue("@username", username);

        await using var reader = await cmd.ExecuteReaderAsync();
        if (!await reader.ReadAsync()) return null;

        return new User
        {
            Id = reader.GetInt32(0),
            UserName = reader.GetString(1),
            Email = reader.GetString(2),
            PasswordHash = reader.GetString(3),
            Role = reader.GetString(4),
            IsActive = reader.GetInt32(5) == 1
        };
    }

    /// <inheritdoc/>
    public async Task<User> CreateAsync(User user)
    {
        await using var conn = new SqliteConnection(_connectionString);
        await conn.OpenAsync();
        var cmd = conn.CreateCommand();
        // ✅ SMELL-1 FIXED: All parameters bound — no string interpolation
        cmd.CommandText = @"
            INSERT INTO Users (user_name, Email, PasswordHash, Role, is_active, IsDeleted, CreatedAt, ModifiedAt)
            VALUES (@username, @email, @hash, @role, 1, 0, @now, @now)
            RETURNING Id";
        cmd.Parameters.AddWithValue("@username", user.UserName);
        cmd.Parameters.AddWithValue("@email", user.Email);
        cmd.Parameters.AddWithValue("@hash", user.PasswordHash);
        cmd.Parameters.AddWithValue("@role", user.Role);
        cmd.Parameters.AddWithValue("@now", DateTime.UtcNow.ToString("o"));

        var id = (long)(await cmd.ExecuteScalarAsync())!;
        user.Id = (int)id;

        _logger.LogInformation("Created user {UserId} ({Username})", user.Id, user.UserName);
        return user;
    }

    /// <inheritdoc/>
    public async Task<bool> DeleteAsync(int id, int deletedBy)
    {
        // ✅ Soft-delete — records are never hard-deleted (audit trail preserved)
        await using var conn = new SqliteConnection(_connectionString);
        await conn.OpenAsync();
        var cmd = conn.CreateCommand();
        cmd.CommandText = "UPDATE Users SET IsDeleted = 1, ModifiedAt = @now, ModifiedBy = @by WHERE Id = @id";
        cmd.Parameters.AddWithValue("@now", DateTime.UtcNow.ToString("o"));
        cmd.Parameters.AddWithValue("@by", deletedBy);
        cmd.Parameters.AddWithValue("@id", id);

        var rows = await cmd.ExecuteNonQueryAsync();
        _logger.LogInformation("User {UserId} soft-deleted by {ActorId}", id, deletedBy);
        return rows > 0;
    }

    private static User MapUser(SqliteDataReader r) => new()
    {
        Id = r.GetInt32(0),
        UserName = r.GetString(1),
        Email = r.GetString(2),
        Role = r.GetString(3),
        IsActive = r.GetInt32(4) == 1
    };
}
