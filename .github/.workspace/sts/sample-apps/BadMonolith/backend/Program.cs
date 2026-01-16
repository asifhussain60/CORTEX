using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.Data.SqlClient;
using System.Data;
using System.Text.Json;

var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

// Hard-coded connection string, no config, no secrets management
string connString = "Server=localhost;Database=CortexBadDb;User Id=sa;Password=Your_password123;TrustServerCertificate=True;";

// Global mutable state
List<Dictionary<string, object>> CachedTasks = new List<Dictionary<string, object>>();

app.MapGet("/", () => "BadMonolith API - DO NOT COPY THIS CODE");

// Single god-endpoint that does everything based on query params
app.MapMethods("/api/tasks", new[] { "GET", "POST", "PUT", "DELETE" }, async (HttpContext ctx) =>
{
    string action = ctx.Request.Query["action"];

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
        // Ram all logic into one method
        using var reader = new StreamReader(ctx.Request.Body);
        var body = await reader.ReadToEndAsync();
        var doc = JsonDocument.Parse(body);
        var title = doc.RootElement.GetProperty("title").GetString();

        using (var conn = new SqlConnection(connString))
        {
            conn.Open();
            var cmd = conn.CreateCommand();
            cmd.CommandText = "INSERT INTO Tasks(Title, IsCompleted) VALUES('" + title + "', 0)";
            cmd.ExecuteNonQuery();
        }

        await ctx.Response.WriteAsync("Created");
        return;
    }
    else if (ctx.Request.Method == "PUT")
    {
        using var reader = new StreamReader(ctx.Request.Body);
        var body = await reader.ReadToEndAsync();
        var doc = JsonDocument.Parse(body);
        var id = doc.RootElement.GetProperty("id").GetInt32();
        var isCompleted = doc.RootElement.GetProperty("isCompleted").GetBoolean();

        using (var conn = new SqlConnection(connString))
        {
            conn.Open();
            var cmd = conn.CreateCommand();
            cmd.CommandText = "UPDATE Tasks SET IsCompleted = " + (isCompleted ? "1" : "0") + " WHERE Id = " + id;
            cmd.ExecuteNonQuery();
        }

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
