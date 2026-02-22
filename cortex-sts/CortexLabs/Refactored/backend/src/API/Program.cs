// FIX SMELL-3: Program.cs is ONLY bootstrapping — no domain logic
// FIX SMELL-9: /api/v1/ versioned routes
// FIX SMELL-13: CORS configured from appsettings — no wildcard
// FIX SMELL-17: all services registered and injected via interface (not concrete type)
// FIX SMELL-18: RFC 7807 ProblemDetails middleware — no stack traces to clients
// FIX SMELL-2: no secrets in code — IConfiguration only
using CortexLabs.FinTrack.Application.Interfaces;
using CortexLabs.FinTrack.Application.Services;
using CortexLabs.FinTrack.Infrastructure.Repositories;
using CortexLabs.FinTrack.Domain.Interfaces;

var builder = WebApplication.CreateBuilder(args);

// FIX SMELL-13: CORS from config — not a wildcard
var allowedOrigins = builder.Configuration.GetSection("Cors:AllowedOrigins").Get<string[]>()
    ?? ["http://localhost:3000"];
builder.Services.AddCors(opt => opt.AddDefaultPolicy(p =>
    p.WithOrigins(allowedOrigins).AllowAnyMethod().AllowAnyHeader()));

builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// FIX SMELL-18: RFC 7807 ProblemDetails — no stack traces in responses
builder.Services.AddProblemDetails();

// FIX SMELL-2: connection string from config (user-secrets / env var in prod)
var connectionString = builder.Configuration.GetConnectionString("DefaultConnection")
    ?? throw new InvalidOperationException("Connection string 'DefaultConnection' is required.");

// FIX SMELL-17: interface → implementation (never concrete type alone — DEFECT-5 resolved)
builder.Services.AddScoped<IUserRepository>(_ => new UserRepository(connectionString));
builder.Services.AddScoped<ITransactionRepository>(_ => new TransactionRepository(connectionString));
builder.Services.AddScoped<IAccountRepository>(_ => new AccountRepository(connectionString));
builder.Services.AddScoped<IUserService, UserService>();
builder.Services.AddScoped<ITransactionService, TransactionService>();
builder.Services.AddScoped<IAccountService, AccountService>();
builder.Services.AddScoped<IAnalyticsService, AnalyticsService>();
builder.Services.AddScoped<IReportService, ReportService>();

var app = builder.Build();
app.UseCors();
app.UseExceptionHandler(); // FIX SMELL-18: handles exceptions via ProblemDetails
app.UseSwagger();
app.UseSwaggerUI();

// FIX SMELL-9: /api/v1/ versioned prefix on all routes
var api = app.MapGroup("/api/v1");

// Users — injected via IUserService (interface, not concrete UserService)
api.MapGet("/users", async (IUserService svc, int page = 1, int pageSize = 20) =>
    Results.Ok(await svc.GetPagedAsync(page, pageSize)));
api.MapGet("/users/search", async (IUserService svc, string username) =>
    await svc.SearchByUsernameAsync(username) is { } u ? Results.Ok(u) : Results.NotFound());
api.MapPost("/users", async (IUserService svc, CortexLabs.FinTrack.Domain.Entities.User user) =>
{
    var created = await svc.CreateAsync(user);
    return Results.Created($"/api/v1/users/{created.Id}", created);
});
api.MapDelete("/users/{id:int}", async (IUserService svc, int id) =>
{
    await svc.SoftDeleteAsync(id);
    return Results.NoContent();
});

// Transactions — injected via ITransactionService
api.MapGet("/transactions", async (ITransactionService svc, int userId, int page = 1, int pageSize = 50) =>
    Results.Ok(await svc.GetByUserAsync(userId, page, pageSize)));
api.MapGet("/transactions/search", async (ITransactionService svc, string? category, DateTime? dateFrom, int page = 1) =>
    Results.Ok(await svc.SearchAsync(category, dateFrom, page)));
api.MapPost("/transactions", async (ITransactionService svc, CortexLabs.FinTrack.Domain.Entities.Transaction tx) =>
{
    var created = await svc.CreateAsync(tx);
    return Results.Created($"/api/v1/transactions/{created.Id}", created);
});

// Accounts — injected via IAccountService
api.MapGet("/accounts", async (IAccountService svc, int userId) =>
    Results.Ok(await svc.GetByUserAsync(userId)));
api.MapPost("/accounts/transfer", async (IAccountService svc, int fromId, int toId, decimal amount) =>
{
    await svc.TransferAsync(fromId, toId, amount);
    return Results.Ok(new { Message = "Transfer complete", FromId = fromId, ToId = toId, Amount = amount });
});

// Analytics — injected via IAnalyticsService
api.MapGet("/analytics/summary", async (IAnalyticsService svc, int userId) =>
    Results.Ok(await svc.GetSummaryAsync(userId)));

// Reports — injected via IReportService
api.MapPost("/reports/generate", async (IReportService svc, CortexLabs.FinTrack.Domain.Entities.ReportType type, int userId) =>
    Results.Ok(await svc.GenerateAsync(type, userId)));

// Health — FIX SMELL-11: real DB probe, not hardcoded stub
api.MapGet("/health", async (IConfiguration config) =>
{
    try
    {
        using var conn = new Microsoft.Data.Sqlite.SqliteConnection(
            config.GetConnectionString("DefaultConnection"));
        await conn.OpenAsync();
        return Results.Ok(new { Status = "healthy", Timestamp = DateTime.UtcNow });
    }
    catch (Exception ex)
    {
        return Results.Ok(new { Status = "degraded", Error = ex.Message, Timestamp = DateTime.UtcNow });
    }
});

app.Run();