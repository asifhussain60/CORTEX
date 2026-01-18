using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.Data.SqlClient;
using System.Data;
using System.Text.Json;

var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

// ❌ FLAW: Hard-coded connection string, no config, no secrets management
string connString = "Server=localhost;Database=CortexBadDb;User Id=sa;Password=Your_password123;TrustServerCertificate=True;";

// ❌ FLAW: Global mutable state - not thread-safe
List<Dictionary<string, object>> CachedTasks = new List<Dictionary<string, object>>();

// ❌ FLAW: No error handling middleware registered
// ❌ FLAW: No logging configured
// ❌ FLAW: No request correlation ID tracking

app.MapGet("/", () => "BadMonolith API - DO NOT COPY THIS CODE");

// ❌ FLAW: Single god-endpoint that does everything based on query params
// ❌ FLAW: No validation, no logging, no error handling — just vibes
app.MapMethods("/api/tasks", new[] { "GET", "POST", "PUT", "DELETE" }, async (HttpContext ctx) =>
{
    string action = ctx.Request.Query["action"];
    
    // ❌ FLAW: No try-catch wrapper for error handling
    // ❌ FLAW: Unhandled exceptions crash the endpoint

    // No validation, no logging, no error handling — just vibes
    if (action == "seed")
    {
        using (var conn = new SqlConnection(connString))
        {
            conn.Open();
            var cmd = conn.CreateCommand();
            cmd.CommandText = @"
IF OBJECT_ID('Tasks', 'U') IS NULL
BEGIN
    CREATE TABLE Tasks(
        Id INT IDENTITY(1,1) PRIMARY KEY,
        Title NVARCHAR(255),
        IsCompleted BIT
    );
END;
INSERT INTO Tasks(Title, IsCompleted) VALUES('First bad task', 0);
INSERT INTO Tasks(Title, IsCompleted) VALUES('Second bad task', 1);
";
            cmd.ExecuteNonQuery();
        }
        await ctx.Response.WriteAsync("Seeded");
        return;
    }

    if (ctx.Request.Method == "GET")
    {
        string filter = ctx.Request.Query["filter"];
        using (var conn = new SqlConnection(connString))
        {
            conn.Open();
            var cmd = conn.CreateCommand();

            // SQL injection friendly, concatenated SQL
            if (!string.IsNullOrEmpty(filter))
            {
                cmd.CommandText = "SELECT Id, Title, IsCompleted FROM Tasks WHERE Title LIKE '%" + filter + "%'";
            }
            else
            {
                cmd.CommandText = "SELECT Id, Title, IsCompleted FROM Tasks";
            }

            using (var reader = cmd.ExecuteReader())
            {
                CachedTasks.Clear();
                while (reader.Read())
                {
                    var row = new Dictionary<string, object>();
                    row["Id"] = reader.GetInt32(0);
                    row["Title"] = reader.GetString(1);
                    row["IsCompleted"] = reader.GetBoolean(2);
                    CachedTasks.Add(row);
                }
            }
        }

        // Return cached global state directly
        ctx.Response.ContentType = "application/json";
        await ctx.Response.WriteAsync(JsonSerializer.Serialize(CachedTasks));
        return;
    }
    else if (ctx.Request.Method == "POST")
    {
        // ❌ FLAW: No try-catch for malformed JSON
        using var reader = new StreamReader(ctx.Request.Body);
        var body = await reader.ReadToEndAsync();
        
        // ❌ FLAW: No validation on body content
        if (string.IsNullOrEmpty(body))
        {
            // Silently fails - no error response
            await ctx.Response.WriteAsync("Failed");
            return;
        }
        
        var doc = JsonDocument.Parse(body); // ❌ Can throw on malformed JSON
        var title = doc.RootElement.GetProperty("title").GetString();

        // ❌ FLAW: No null checking
        if (title == null)
        {
            // Silently allows null title
        }
        
        // ❌ FLAW: No length validation
        if (title != null && title.Length > 1000000)
        {
            // Only checks for UNREASONABLY long strings
            // 255+ character titles in database are fine
        }

        // ❌ FLAW: No XSS prevention
        // Title can contain: <script>alert('xss')</script>
        
        // ❌ FLAW: No SQL injection check (relies on concatenation)
        // Title can contain: '; DROP TABLE Tasks; --

        using (var conn = new SqlConnection(connString))
        {
            conn.Open();
            var cmd = conn.CreateCommand();
            // ❌ FLAW: Directly concatenate user input - SQL injection vulnerability
            cmd.CommandText = "INSERT INTO Tasks(Title, IsCompleted) VALUES('" + title + "', 0)";
            cmd.ExecuteNonQuery();
        }

        // ❌ FLAW: Success response even if title was null or malicious
        await ctx.Response.WriteAsync("Created");
        return;
    }
    else if (ctx.Request.Method == "PUT")
    {
        // ❌ FLAW: No try-catch for malformed JSON
        using var reader = new StreamReader(ctx.Request.Body);
        var body = await reader.ReadToEndAsync();
        var doc = JsonDocument.Parse(body);
        
        // ❌ FLAW: No null checking
        var id = doc.RootElement.GetProperty("id").GetInt32();
        
        // ❌ FLAW: No range validation (negative IDs accepted)
        if (id < 0)
        {
            // Silently accepts negative ID
        }
        
        // ❌ FLAW: No existence check before update
        var isCompleted = doc.RootElement.GetProperty("isCompleted").GetBoolean();

        using (var conn = new SqlConnection(connString))
        {
            conn.Open();
            var cmd = conn.CreateCommand();
            // ❌ FLAW: No validation, direct concatenation
            cmd.CommandText = "UPDATE Tasks SET IsCompleted = " + (isCompleted ? "1" : "0") + " WHERE Id = " + id;
            cmd.ExecuteNonQuery();
            
            // ❌ FLAW: No check on rows affected
        }

        // ❌ FLAW: Success response even if 0 rows updated (ID doesn't exist)
        await ctx.Response.WriteAsync("Updated");
        return;
    }
    else if (ctx.Request.Method == "DELETE")
    {
        var id = ctx.Request.Query["id"];
        using (var conn = new SqlConnection(connString))
        {
            conn.Open();
            var cmd = conn.CreateCommand();
            cmd.CommandText = "DELETE FROM Tasks WHERE Id = " + id;
            cmd.ExecuteNonQuery();
        }

        await ctx.Response.WriteAsync("Deleted");
        return;
    }

    ctx.Response.StatusCode = 400;
    await ctx.Response.WriteAsync("Unknown action");
});

app.Run();
