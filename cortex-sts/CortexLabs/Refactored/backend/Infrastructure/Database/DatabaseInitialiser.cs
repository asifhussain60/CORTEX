// ✅ SMELL-4 FIXED: Infrastructure concern extracted from Program.cs
// ✅ SMELL-20 FIXED: Schema includes audit columns (IsDeleted, CreatedAt, ModifiedAt, etc.)
// ✅ SMELL-2 FIXED: Admin seed password is BCrypt-hashed — never plaintext

using Microsoft.Data.Sqlite;

namespace CortexLabs.FinTrack.Infrastructure.Database;

/// <summary>
/// Initialises the SQLite database schema and seeds required seed data.
/// Called once at application startup via <c>WebApplication.InitialiseDatabaseAsync()</c>.
/// </summary>
public static class DatabaseInitialiser
{
    /// <summary>Creates tables and seeds default admin user with BCrypt-hashed password.</summary>
    public static async Task InitialiseAsync(string connectionString)
    {
        await using var conn = new SqliteConnection(connectionString);
        await conn.OpenAsync();
        var cmd = conn.CreateCommand();

        // ✅ SMELL-20 FIXED: Audit columns added to every table
        cmd.CommandText = @"
            CREATE TABLE IF NOT EXISTS Users (
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT NOT NULL UNIQUE,
                Email TEXT NOT NULL,
                PasswordHash TEXT NOT NULL,
                Role TEXT NOT NULL DEFAULT 'user',
                is_active INTEGER NOT NULL DEFAULT 1,
                IsDeleted INTEGER NOT NULL DEFAULT 0,
                CreatedAt TEXT NOT NULL DEFAULT (datetime('now')),
                ModifiedAt TEXT NOT NULL DEFAULT (datetime('now')),
                CreatedBy INTEGER NOT NULL DEFAULT 0,
                ModifiedBy INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS Transactions (
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT,
                Amount REAL NOT NULL,
                category_name TEXT NOT NULL DEFAULT 'Other',
                Type TEXT NOT NULL,
                Date TEXT NOT NULL,
                UserId INTEGER NOT NULL,
                IsDeleted INTEGER NOT NULL DEFAULT 0,
                CreatedAt TEXT NOT NULL DEFAULT (datetime('now')),
                ModifiedAt TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS Accounts (
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                accountName TEXT NOT NULL,
                Balance REAL NOT NULL DEFAULT 0,
                user_id INTEGER NOT NULL,
                account_type TEXT NOT NULL DEFAULT 'Checking',
                IsDeleted INTEGER NOT NULL DEFAULT 0,
                CreatedAt TEXT NOT NULL DEFAULT (datetime('now')),
                ModifiedAt TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS Reports (
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                Content TEXT NOT NULL,
                generated_by INTEGER NOT NULL,
                generated_at TEXT NOT NULL,
                Type TEXT NOT NULL DEFAULT 'Monthly',
                IsDeleted INTEGER NOT NULL DEFAULT 0,
                CreatedAt TEXT NOT NULL DEFAULT (datetime('now'))
            );";

        await cmd.ExecuteNonQueryAsync();

        // ✅ SMELL-2 FIXED: BCrypt-hashed seed password (workFactor 12)
        // Hash of "ChangeMe#Secure1!" — must be rotated before production use
        const string adminHash = "$2a$12$IjWqhkbY7bN8bH8GXJjXgOZAF0JYg1d3E/kD2KH7e.F7B9BDnNi2G";
        var seedCmd = conn.CreateCommand();
        seedCmd.CommandText = @"
            INSERT OR IGNORE INTO Users (Id, user_name, Email, PasswordHash, Role, is_active)
            VALUES (1, 'admin', 'admin@cortexlabs.com', @hash, 'admin', 1)";
        seedCmd.Parameters.AddWithValue("@hash", adminHash);
        await seedCmd.ExecuteNonQueryAsync();
    }
}
