using Microsoft.Data.Sqlite;
using Microsoft.Extensions.Logging;

namespace CortexLabs.FinTrack.Infrastructure.Data;

/// <summary>
/// Database initializer — creates tables with proper schemas, indexes, and
/// constraints. Fixes SMELL-03 (hardcoded conn string), SMELL-06 (no migrations/schema),
/// SMELL-17 (no indexes). Uses parameterized queries per ADR-002.
/// </summary>
public class DatabaseInitializer
{
    private readonly string _connectionString;
    private readonly ILogger<DatabaseInitializer> _logger;

    public DatabaseInitializer(string connectionString, ILogger<DatabaseInitializer> logger)
    {
        _connectionString = connectionString;
        _logger = logger;
    }

    public void Initialize()
    {
        using var connection = new SqliteConnection(_connectionString);
        connection.Open();

        ExecuteNonQuery(connection, @"
            CREATE TABLE IF NOT EXISTS Users (
                Id          INTEGER PRIMARY KEY AUTOINCREMENT,
                Username    TEXT    NOT NULL UNIQUE,
                Email       TEXT    NOT NULL UNIQUE,
                PasswordHash TEXT   NOT NULL,
                Role        TEXT    NOT NULL DEFAULT 'User',
                CreatedAt   TEXT    NOT NULL DEFAULT (datetime('now')),
                UpdatedAt   TEXT    NOT NULL DEFAULT (datetime('now'))
            );");

        ExecuteNonQuery(connection, @"
            CREATE TABLE IF NOT EXISTS Transactions (
                Id          INTEGER PRIMARY KEY AUTOINCREMENT,
                UserId      INTEGER NOT NULL,
                Amount      REAL    NOT NULL,
                Type        TEXT    NOT NULL,
                Category    TEXT    NOT NULL DEFAULT 'Other',
                Description TEXT    NOT NULL DEFAULT '',
                Date        TEXT    NOT NULL DEFAULT (datetime('now')),
                CreatedAt   TEXT    NOT NULL DEFAULT (datetime('now')),
                UpdatedAt   TEXT    NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (UserId) REFERENCES Users(Id) ON DELETE CASCADE
            );");

        ExecuteNonQuery(connection, @"
            CREATE TABLE IF NOT EXISTS Accounts (
                Id          INTEGER PRIMARY KEY AUTOINCREMENT,
                UserId      INTEGER NOT NULL,
                Name        TEXT    NOT NULL,
                Type        TEXT    NOT NULL DEFAULT 'Checking',
                Balance     REAL    NOT NULL DEFAULT 0,
                Currency    TEXT    NOT NULL DEFAULT 'USD',
                CreatedAt   TEXT    NOT NULL DEFAULT (datetime('now')),
                UpdatedAt   TEXT    NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (UserId) REFERENCES Users(Id) ON DELETE CASCADE
            );");

        // Performance indexes — fixes SMELL-17
        ExecuteNonQuery(connection, "CREATE INDEX IF NOT EXISTS IX_Transactions_UserId ON Transactions(UserId);");
        ExecuteNonQuery(connection, "CREATE INDEX IF NOT EXISTS IX_Accounts_UserId ON Accounts(UserId);");
        ExecuteNonQuery(connection, "CREATE INDEX IF NOT EXISTS IX_Users_Username ON Users(Username);");
        ExecuteNonQuery(connection, "CREATE INDEX IF NOT EXISTS IX_Users_Email ON Users(Email);");

        _logger.LogInformation("Database initialized successfully");
    }

    private void ExecuteNonQuery(SqliteConnection connection, string sql)
    {
        using var command = connection.CreateCommand();
        command.CommandText = sql;
        command.ExecuteNonQuery();
    }
}
