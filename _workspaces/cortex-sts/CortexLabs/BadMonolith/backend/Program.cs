// ❌ SMELL-3: God class — Program.cs handles Users, Transactions, Accounts, Reports,
//    Auth, Admin, Health, Analytics — 6+ domains in ONE file (500+ LOC)
// ❌ SMELL-9: No API versioning — endpoints are /api/users not /api/v1/users
// ❌ SMELL-11: No structured logging, no OpenTelemetry, no correlation IDs
// ❌ SMELL-13: CORS wildcard — AllowAnyOrigin()
// ❌ SMELL-16: Global mutable state via AppCache
// ❌ SMELL-17: No dependency injection for services

using Microsoft.Data.Sqlite;
using CortexLabs.FinTrack.Models;
using CortexLabs.FinTrack.Services;
using System.Text.Json;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// ❌ SMELL-13: CORS wildcard — allows any origin, any method, any header
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.AllowAnyOrigin()  // ❌ SECURITY: Any website can call this API
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

var app = builder.Build();

app.UseCors();
app.UseSwagger();
app.UseSwaggerUI();

// ❌ SMELL-17: Direct instantiation — not registered in DI container
var userService = new UserService();
var transactionService = new TransactionService();
transactionService.SetUserService(userService); // ❌ SMELL-5: Manual wiring of circular dep

// ❌ SMELL-2: Hardcoded connection string fallback
var connectionString = builder.Configuration.GetConnectionString("DefaultConnection")
    ?? "Data Source=fintrack.db";

// ── DATABASE INITIALIZATION (inline, no migrations) ──────────────────────────
// ❌ SMELL-4: Infrastructure concern mixed into application startup
using (var connection = new SqliteConnection(connectionString))
{
    connection.Open();
    var cmd = connection.CreateCommand();
    cmd.CommandText = @"
        CREATE TABLE IF NOT EXISTS Users (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            Email TEXT,
            password_hash TEXT,
            Role TEXT DEFAULT 'user',
            is_active INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS Transactions (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT,
            Amount REAL,
            category_name TEXT,
            Type TEXT,
            Date TEXT,
            UserId INTEGER
        );
        CREATE TABLE IF NOT EXISTS Accounts (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            accountName TEXT,
            Balance REAL,
            user_id INTEGER,
            account_type TEXT
        );
        CREATE TABLE IF NOT EXISTS Reports (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            Content TEXT,
            generated_by INTEGER,
            generated_at TEXT
        );

        -- Seed default admin user with plaintext password
        INSERT OR IGNORE INTO Users (Id, user_name, Email, password_hash, Role, is_active)
        VALUES (1, 'admin', 'admin@cortexlabs.com', 'P@ssw0rd123!', 'admin', 1);

        -- Seed demo data
        INSERT OR IGNORE INTO Users (Id, user_name, Email, password_hash, Role, is_active)
        VALUES (2, 'john.doe', 'john@cortexlabs.com', 'password123', 'user', 1);
    ";
    cmd.ExecuteNonQuery();
}

// ══════════════════════════════════════════════════════════════════════════════
// ❌ SMELL-3: ALL ENDPOINTS IN ONE FILE — 6 DOMAINS MIXED TOGETHER
// ══════════════════════════════════════════════════════════════════════════════

// ── USERS DOMAIN ─────────────────────────────────────────────────────────────

// ❌ SMELL-9: No API versioning (/api/users instead of /api/v1/users)
// ❌ SMELL-6: No pagination — returns ALL users
app.MapGet("/api/users", () =>
{
    // ❌ SMELL-16: Incrementing global mutable state
    AppCache.TotalRequestCount++;

    using var connection = new SqliteConnection(connectionString);
    connection.Open();
    var cmd = connection.CreateCommand();
    cmd.CommandText = "SELECT * FROM Users"; // ❌ SMELL-6: No LIMIT, no OFFSET
    var reader = cmd.ExecuteReader();

    var users = new List<object>();
    while (reader.Read())
    {
        users.Add(new
        {
            Id = reader.GetInt32(0),
            UserName = reader.GetString(1),
            Email = reader.GetString(2),
            // ❌ SMELL-2: Exposing password hash in API response!
            PasswordHash = reader.GetString(3),
            Role = reader.GetString(4),
            IsActive = reader.GetInt32(5) == 1
        });
    }
    return Results.Ok(users);
});

// ❌ SMELL-1: SQL injection via string concatenation
app.MapGet("/api/users/search", (string username) =>
{
    AppCache.TotalRequestCount++;
    using var connection = new SqliteConnection(connectionString);
    connection.Open();
    var cmd = connection.CreateCommand();
    // ❌ SMELL-1: CRITICAL — SQL injection! Attacker can pass: ' OR '1'='1
    cmd.CommandText = $"SELECT * FROM Users WHERE user_name = '{username}'";
    var reader = cmd.ExecuteReader();

    var users = new List<object>();
    while (reader.Read())
    {
        users.Add(new
        {
            Id = reader.GetInt32(0),
            UserName = reader.GetString(1),
            Email = reader.GetString(2)
        });
    }
    return Results.Ok(users);
});

app.MapPost("/api/users", (User user) =>
{
    AppCache.TotalRequestCount++;

    // ❌ SMELL-10: Duplicate validation — same logic as UserService.ValidateEmail()
    if (string.IsNullOrEmpty(user.Email))
        return Results.BadRequest("Email required");
    if (!user.Email.Contains("@"))
        return Results.BadRequest("Invalid email");
    if (user.Email.Length < 5) // ❌ SMELL-15: Magic number
        return Results.BadRequest("Email too short");
    if (user.Email.Length > 100) // ❌ SMELL-15: Magic number
        return Results.BadRequest("Email too long");

    using var connection = new SqliteConnection(connectionString);
    connection.Open();
    var cmd = connection.CreateCommand();
    // ❌ SMELL-1: SQL injection in INSERT
    cmd.CommandText = $"INSERT INTO Users (user_name, Email, password_hash, Role, is_active) VALUES ('{user.user_name}', '{user.Email}', '{user.password_hash}', '{user.Role}', 1)";

    try
    {
        cmd.ExecuteNonQuery();
        return Results.Created($"/api/users/{user.Id}", user);
    }
    catch (Exception ex)
    {
        // ❌ SMELL-18: Stack trace exposed to client
        return Results.Problem(
            detail: ex.ToString(),
            statusCode: 500,
            title: "Internal Server Error"
        );
    }
});

// ── TRANSACTIONS DOMAIN ──────────────────────────────────────────────────────

app.MapGet("/api/transactions", () =>
{
    AppCache.TotalRequestCount++;
    using var connection = new SqliteConnection(connectionString);
    connection.Open();
    var cmd = connection.CreateCommand();
    cmd.CommandText = "SELECT * FROM Transactions"; // ❌ SMELL-6: No pagination
    var reader = cmd.ExecuteReader();

    var transactions = new List<Transaction>();
    while (reader.Read())
    {
        var tx = new Transaction
        {
            Id = reader.GetInt32(0),
            description = reader.IsDBNull(1) ? "" : reader.GetString(1),
            Amount = (decimal)reader.GetDouble(2),
            category_name = reader.IsDBNull(3) ? "" : reader.GetString(3),
            Type = reader.IsDBNull(4) ? "" : reader.GetString(4),
            Date = DateTime.Parse(reader.GetString(5)),
            UserId = reader.GetInt32(6)
        };
        transactions.Add(tx);
    }

    // ❌ SMELL-16: Storing in global mutable state
    AppCache.RecentTransactions = transactions;

    return Results.Ok(transactions);
});

// ❌ SMELL-1: SQL injection in transaction search
app.MapGet("/api/transactions/search", (string category, string dateFrom) =>
{
    AppCache.TotalRequestCount++;
    using var connection = new SqliteConnection(connectionString);
    connection.Open();
    var cmd = connection.CreateCommand();
    // ❌ SMELL-1: SQL injection — both parameters are unsanitized
    cmd.CommandText = $"SELECT * FROM Transactions WHERE category_name = '{category}' AND Date >= '{dateFrom}'";
    var reader = cmd.ExecuteReader();

    var results = new List<object>();
    while (reader.Read())
    {
        results.Add(new
        {
            Id = reader.GetInt32(0),
            Description = reader.IsDBNull(1) ? "" : reader.GetString(1),
            Amount = reader.GetDouble(2),
            Category = reader.IsDBNull(3) ? "" : reader.GetString(3)
        });
    }
    return Results.Ok(results);
});

app.MapPost("/api/transactions", (Transaction tx) =>
{
    AppCache.TotalRequestCount++;

    // ❌ SMELL-19: No model validation — accepts negative amounts, empty descriptions
    // ❌ SMELL-4: Business logic inline — categorization should be in domain service
    if (string.IsNullOrEmpty(tx.category_name))
    {
        // ❌ SMELL-15: Magic numbers for auto-categorization
        if (tx.Amount > 10000) tx.category_name = "large_purchase";
        else if (tx.Amount > 1000) tx.category_name = "medium_purchase";
        else tx.category_name = "other";
    }

    using var connection = new SqliteConnection(connectionString);
    connection.Open();
    var cmd = connection.CreateCommand();
    // ❌ SMELL-1: SQL injection in INSERT
    cmd.CommandText = $"INSERT INTO Transactions (description, Amount, category_name, Type, Date, UserId) VALUES ('{tx.description}', {tx.Amount}, '{tx.category_name}', '{tx.Type}', '{tx.Date:yyyy-MM-dd}', {tx.UserId})";

    try
    {
        cmd.ExecuteNonQuery();

        // ❌ SMELL-16: Mutating global cache
        AppCache.RecentTransactions.Add(tx);

        return Results.Created($"/api/transactions/{tx.Id}", tx);
    }
    catch (Exception ex)
    {
        // ❌ SMELL-18: Full stack trace exposed
        AppCache.LastError = DateTime.Now;
        AppCache.LastErrorMessage = ex.ToString();
        return Results.Problem(detail: ex.ToString(), statusCode: 500);
    }
});

// ── ACCOUNTS DOMAIN ──────────────────────────────────────────────────────────

app.MapGet("/api/accounts", () =>
{
    AppCache.TotalRequestCount++;
    using var connection = new SqliteConnection(connectionString);
    connection.Open();
    var cmd = connection.CreateCommand();
    cmd.CommandText = "SELECT * FROM Accounts"; // ❌ SMELL-6: No pagination
    var reader = cmd.ExecuteReader();

    var accounts = new List<object>();
    while (reader.Read())
    {
        accounts.Add(new
        {
            Id = reader.GetInt32(0),
            Name = reader.IsDBNull(1) ? "" : reader.GetString(1),
            Balance = reader.GetDouble(2),
            UserId = reader.GetInt32(3),
            Type = reader.IsDBNull(4) ? "" : reader.GetString(4)
        });
    }
    return Results.Ok(accounts);
});

// ❌ SMELL-4: Business logic (transfer) embedded directly in endpoint
app.MapPost("/api/accounts/transfer", (int fromId, int toId, decimal amount) =>
{
    AppCache.TotalRequestCount++;

    // ❌ SMELL-19: No validation — allows negative transfers, self-transfers
    // ❌ SMELL-15: No minimum/maximum transfer limits defined

    using var connection = new SqliteConnection(connectionString);
    connection.Open();

    // ❌ SMELL-1: SQL injection
    var cmd1 = connection.CreateCommand();
    cmd1.CommandText = $"UPDATE Accounts SET Balance = Balance - {amount} WHERE Id = {fromId}";
    cmd1.ExecuteNonQuery();

    var cmd2 = connection.CreateCommand();
    cmd2.CommandText = $"UPDATE Accounts SET Balance = Balance + {amount} WHERE Id = {toId}";
    cmd2.ExecuteNonQuery();

    // ❌ No transaction wrapping — if cmd2 fails, cmd1 already committed!
    // ❌ No overdraft check — balance can go negative

    return Results.Ok(new { Message = "Transfer complete", From = fromId, To = toId, Amount = amount });
});

// ── REPORTS DOMAIN ───────────────────────────────────────────────────────────

app.MapGet("/api/reports", () =>
{
    AppCache.TotalRequestCount++;
    using var connection = new SqliteConnection(connectionString);
    connection.Open();
    var cmd = connection.CreateCommand();
    cmd.CommandText = "SELECT * FROM Reports"; // ❌ SMELL-6: No pagination
    var reader = cmd.ExecuteReader();

    var reports = new List<object>();
    while (reader.Read())
    {
        reports.Add(new
        {
            Id = reader.GetInt32(0),
            Title = reader.IsDBNull(1) ? "" : reader.GetString(1),
            Content = reader.IsDBNull(2) ? "" : reader.GetString(2),
            GeneratedBy = reader.GetInt32(3),
            GeneratedAt = reader.GetString(4)
        });
    }
    return Results.Ok(reports);
});

// ❌ SMELL-4: Report generation logic inline in endpoint — no service layer
app.MapPost("/api/reports/generate", (string reportType, int userId) =>
{
    AppCache.TotalRequestCount++;

    // ❌ SMELL-11: Console.WriteLine instead of ILogger
    Console.WriteLine($"Generating {reportType} report for user {userId}");

    string content = "";
    // ❌ SMELL-15: Magic strings for report types
    if (reportType == "monthly")
    {
        content = "Monthly financial summary... (placeholder)";
    }
    else if (reportType == "annual")
    {
        content = "Annual financial summary... (placeholder)";
    }
    else if (reportType == "tax")
    {
        content = "Tax report... (placeholder)";
    }
    else
    {
        content = "Unknown report type";
    }

    using var connection = new SqliteConnection(connectionString);
    connection.Open();
    var cmd = connection.CreateCommand();
    // ❌ SMELL-1: SQL injection
    cmd.CommandText = $"INSERT INTO Reports (title, Content, generated_by, generated_at) VALUES ('{reportType} Report', '{content}', {userId}, '{DateTime.Now}')";
    cmd.ExecuteNonQuery();

    return Results.Ok(new { Message = $"{reportType} report generated", Content = content });
});

// ── AUTH DOMAIN (inline, no middleware) ───────────────────────────────────────

// ❌ SMELL-2: Credentials checked against hardcoded config values
// ❌ SMELL-18: No rate limiting — brute force possible
app.MapPost("/api/auth/login", (string username, string password) =>
{
    AppCache.TotalRequestCount++;

    var adminUser = builder.Configuration["AdminCredentials:Username"];
    var adminPass = builder.Configuration["AdminCredentials:Password"];

    // ❌ SMELL-2: Comparing against hardcoded admin credentials
    if (username == adminUser && password == adminPass)
    {
        // ❌ SMELL-2: JWT secret from config (which is hardcoded in appsettings.json)
        var token = $"fake-jwt-{username}-{DateTime.Now.Ticks}";
        return Results.Ok(new { Token = token, Role = "admin" });
    }

    // Check database
    using var connection = new SqliteConnection(connectionString);
    connection.Open();
    var cmd = connection.CreateCommand();
    // ❌ SMELL-1: SQL injection in login — attacker can bypass auth!
    cmd.CommandText = $"SELECT * FROM Users WHERE user_name = '{username}' AND password_hash = '{password}'";
    var reader = cmd.ExecuteReader();

    if (reader.Read())
    {
        var token = $"fake-jwt-{username}-{DateTime.Now.Ticks}";
        // ❌ SMELL-11: No audit log for login events
        Console.WriteLine($"User {username} logged in at {DateTime.Now}");
        return Results.Ok(new { Token = token, Role = reader.GetString(4) });
    }

    // ❌ SMELL-18: Reveals whether username exists — information disclosure
    return Results.Unauthorized();
});

// ── ADMIN DOMAIN ─────────────────────────────────────────────────────────────

// ❌ SMELL-18: No authentication middleware — anyone can access admin endpoints
app.MapGet("/api/admin/stats", () =>
{
    // ❌ SMELL-16: Reading from global mutable state
    return Results.Ok(new
    {
        TotalRequests = AppCache.TotalRequestCount,
        CachedTransactions = AppCache.RecentTransactions.Count,
        LastError = AppCache.LastError,
        LastErrorMessage = AppCache.LastErrorMessage,
        // ❌ SMELL-2: Exposing internal configuration
        ConnectionString = connectionString,
        JwtSecret = builder.Configuration["JwtSettings:Secret"],
        SmtpPassword = builder.Configuration["SmtpSettings:Password"]
    });
});

// ❌ SMELL-1: SQL injection in admin delete
app.MapDelete("/api/admin/users/{id}", (int id) =>
{
    AppCache.TotalRequestCount++;
    using var connection = new SqliteConnection(connectionString);
    connection.Open();
    var cmd = connection.CreateCommand();
    // Hard delete — no soft delete, no audit trail
    cmd.CommandText = $"DELETE FROM Users WHERE Id = {id}";
    var rows = cmd.ExecuteNonQuery();

    Console.WriteLine($"Admin deleted user {id}"); // ❌ SMELL-11: No structured logging
    return Results.Ok(new { Deleted = rows > 0 });
});

// ── ANALYTICS DOMAIN ─────────────────────────────────────────────────────────

// ❌ SMELL-4: Heavy computation inline in endpoint
app.MapGet("/api/analytics/summary", () =>
{
    AppCache.TotalRequestCount++;

    using var connection = new SqliteConnection(connectionString);
    connection.Open();

    // ❌ SMELL-6: Loading ALL data to compute analytics in-memory
    var cmd = connection.CreateCommand();
    cmd.CommandText = "SELECT * FROM Transactions";
    var reader = cmd.ExecuteReader();

    var transactions = new List<Transaction>();
    while (reader.Read())
    {
        transactions.Add(new Transaction
        {
            Id = reader.GetInt32(0),
            description = reader.IsDBNull(1) ? "" : reader.GetString(1),
            Amount = (decimal)reader.GetDouble(2),
            category_name = reader.IsDBNull(3) ? "" : reader.GetString(3),
            Type = reader.IsDBNull(4) ? "" : reader.GetString(4),
            Date = DateTime.Parse(reader.GetString(5)),
            UserId = reader.GetInt32(6)
        });
    }

    // ❌ SMELL-4: Analytics computation inline — should be a separate analytics service
    var totalIncome = transactions.Where(t => t.Type == "income").Sum(t => t.Amount);
    var totalExpenses = transactions.Where(t => t.Type == "expense").Sum(t => t.Amount);
    var avgTransaction = transactions.Any() ? transactions.Average(t => t.Amount) : 0;
    var topCategory = transactions
        .GroupBy(t => t.category_name)
        .OrderByDescending(g => g.Count())
        .FirstOrDefault()?.Key ?? "none";

    // ❌ SMELL-15: Magic numbers for thresholds
    var healthScore = totalIncome > totalExpenses ? "healthy" : "warning";
    if (totalExpenses > totalIncome * 1.5m) healthScore = "critical"; // ❌ SMELL-15: 1.5 magic number

    return Results.Ok(new
    {
        TotalIncome = totalIncome,
        TotalExpenses = totalExpenses,
        NetPosition = totalIncome - totalExpenses,
        AverageTransaction = avgTransaction,
        TopCategory = topCategory,
        HealthScore = healthScore,
        TransactionCount = transactions.Count
    });
});

// ── HEALTH ENDPOINT ──────────────────────────────────────────────────────────

app.MapGet("/api/health", () =>
{
    // ❌ SMELL-11: No real health check — always returns OK even if DB is down
    return Results.Ok(new
    {
        Status = "healthy",
        Timestamp = DateTime.Now,
        // ❌ SMELL-2: Exposing environment details
        Environment = Environment.GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT"),
        MachineName = Environment.MachineName,
        DotNetVersion = Environment.Version.ToString()
    });
});

// ── GLOBAL ERROR HANDLER ─────────────────────────────────────────────────────

// ❌ SMELL-18: Catch-all that exposes stack traces
app.Use(async (context, next) =>
{
    try
    {
        await next(context);
    }
    catch (Exception ex)
    {
        // ❌ SMELL-11: Console instead of structured logging
        Console.WriteLine($"UNHANDLED ERROR: {ex}");
        // ❌ SMELL-18: Full exception details sent to client
        context.Response.StatusCode = 500;
        await context.Response.WriteAsJsonAsync(new
        {
            Error = ex.Message,
            StackTrace = ex.StackTrace,
            InnerException = ex.InnerException?.Message
        });
    }
});

// ❌ SMELL-8: Dead code — these methods are defined but never called
static decimal CalculateTax(decimal income, string state)
{
    // ❌ SMELL-15: Magic numbers for tax rates
    if (state == "CA") return income * 0.13m;
    if (state == "NY") return income * 0.12m;
    if (state == "TX") return income * 0.0m;
    return income * 0.10m;
}

static string FormatCurrency(decimal amount)
{
    return $"${amount:F2}"; // ❌ SMELL-15: Hardcoded USD — no localization
}

static bool IsWeekend(DateTime date)
{
    return date.DayOfWeek == DayOfWeek.Saturday || date.DayOfWeek == DayOfWeek.Sunday;
}

app.Run();
