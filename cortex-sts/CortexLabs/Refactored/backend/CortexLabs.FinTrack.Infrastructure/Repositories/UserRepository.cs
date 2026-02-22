using CortexLabs.FinTrack.Domain.Entities;
using CortexLabs.FinTrack.Domain.Enums;
using CortexLabs.FinTrack.Domain.Interfaces;
using Microsoft.Data.Sqlite;

namespace CortexLabs.FinTrack.Infrastructure.Repositories;

/// <summary>
/// SQLite user repository — fixes SMELL-09 (SQL injection) via parameterized queries,
/// SMELL-02 (implements DI interface), SMELL-03 (connection from config).
/// No EF Core — uses Microsoft.Data.Sqlite directly per ADR-002.
/// </summary>
public class UserRepository : IUserRepository
{
    private readonly string _connectionString;

    public UserRepository(string connectionString)
    {
        _connectionString = connectionString;
    }

    public async Task<User?> GetByIdAsync(int id)
    {
        await using var connection = new SqliteConnection(_connectionString);
        await connection.OpenAsync();

        await using var command = connection.CreateCommand();
        command.CommandText = "SELECT Id, Username, Email, PasswordHash, Role, CreatedAt, UpdatedAt FROM Users WHERE Id = @Id";
        command.Parameters.AddWithValue("@Id", id);

        await using var reader = await command.ExecuteReaderAsync();
        return await reader.ReadAsync() ? MapFromReader(reader) : null;
    }

    public async Task<User?> GetByUsernameAsync(string username)
    {
        await using var connection = new SqliteConnection(_connectionString);
        await connection.OpenAsync();

        await using var command = connection.CreateCommand();
        command.CommandText = "SELECT Id, Username, Email, PasswordHash, Role, CreatedAt, UpdatedAt FROM Users WHERE Username = @Username";
        command.Parameters.AddWithValue("@Username", username);

        await using var reader = await command.ExecuteReaderAsync();
        return await reader.ReadAsync() ? MapFromReader(reader) : null;
    }

    public async Task<User?> GetByEmailAsync(string email)
    {
        await using var connection = new SqliteConnection(_connectionString);
        await connection.OpenAsync();

        await using var command = connection.CreateCommand();
        command.CommandText = "SELECT Id, Username, Email, PasswordHash, Role, CreatedAt, UpdatedAt FROM Users WHERE Email = @Email";
        command.Parameters.AddWithValue("@Email", email);

        await using var reader = await command.ExecuteReaderAsync();
        return await reader.ReadAsync() ? MapFromReader(reader) : null;
    }

    public async Task<IReadOnlyList<User>> GetAllAsync(int page, int pageSize)
    {
        await using var connection = new SqliteConnection(_connectionString);
        await connection.OpenAsync();

        await using var command = connection.CreateCommand();
        command.CommandText = "SELECT Id, Username, Email, PasswordHash, Role, CreatedAt, UpdatedAt FROM Users ORDER BY Id LIMIT @Limit OFFSET @Offset";
        command.Parameters.AddWithValue("@Limit", pageSize);
        command.Parameters.AddWithValue("@Offset", (page - 1) * pageSize);

        var users = new List<User>();
        await using var reader = await command.ExecuteReaderAsync();
        while (await reader.ReadAsync())
            users.Add(MapFromReader(reader));

        return users;
    }

    public async Task<int> CreateAsync(User user)
    {
        await using var connection = new SqliteConnection(_connectionString);
        await connection.OpenAsync();

        await using var command = connection.CreateCommand();
        command.CommandText = @"
            INSERT INTO Users (Username, Email, PasswordHash, Role, CreatedAt, UpdatedAt)
            VALUES (@Username, @Email, @PasswordHash, @Role, @CreatedAt, @UpdatedAt);
            SELECT last_insert_rowid();";
        command.Parameters.AddWithValue("@Username", user.Username);
        command.Parameters.AddWithValue("@Email", user.Email);
        command.Parameters.AddWithValue("@PasswordHash", user.PasswordHash);
        command.Parameters.AddWithValue("@Role", user.Role.ToString());
        command.Parameters.AddWithValue("@CreatedAt", user.CreatedAt.ToString("o"));
        command.Parameters.AddWithValue("@UpdatedAt", user.UpdatedAt.ToString("o"));

        var result = await command.ExecuteScalarAsync();
        return Convert.ToInt32(result);
    }

    public async Task<bool> UpdateAsync(User user)
    {
        await using var connection = new SqliteConnection(_connectionString);
        await connection.OpenAsync();

        await using var command = connection.CreateCommand();
        command.CommandText = @"
            UPDATE Users SET Username = @Username, Email = @Email,
            PasswordHash = @PasswordHash, Role = @Role, UpdatedAt = @UpdatedAt
            WHERE Id = @Id";
        command.Parameters.AddWithValue("@Id", user.Id);
        command.Parameters.AddWithValue("@Username", user.Username);
        command.Parameters.AddWithValue("@Email", user.Email);
        command.Parameters.AddWithValue("@PasswordHash", user.PasswordHash);
        command.Parameters.AddWithValue("@Role", user.Role.ToString());
        command.Parameters.AddWithValue("@UpdatedAt", DateTime.UtcNow.ToString("o"));

        return await command.ExecuteNonQueryAsync() > 0;
    }

    public async Task<bool> DeleteAsync(int id)
    {
        await using var connection = new SqliteConnection(_connectionString);
        await connection.OpenAsync();

        await using var command = connection.CreateCommand();
        command.CommandText = "DELETE FROM Users WHERE Id = @Id";
        command.Parameters.AddWithValue("@Id", id);

        return await command.ExecuteNonQueryAsync() > 0;
    }

    public async Task<int> GetCountAsync()
    {
        await using var connection = new SqliteConnection(_connectionString);
        await connection.OpenAsync();

        await using var command = connection.CreateCommand();
        command.CommandText = "SELECT COUNT(*) FROM Users";

        var result = await command.ExecuteScalarAsync();
        return Convert.ToInt32(result);
    }

    private static User MapFromReader(SqliteDataReader reader) => new()
    {
        Id = reader.GetInt32(0),
        Username = reader.GetString(1),
        Email = reader.GetString(2),
        PasswordHash = reader.GetString(3),
        Role = Enum.Parse<UserRole>(reader.GetString(4)),
        CreatedAt = DateTime.Parse(reader.GetString(5)),
        UpdatedAt = DateTime.Parse(reader.GetString(6))
    };
}
