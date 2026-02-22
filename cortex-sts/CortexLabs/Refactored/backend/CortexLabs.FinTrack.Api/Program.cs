using CortexLabs.FinTrack.Api.Endpoints;
using CortexLabs.FinTrack.Api.Middleware;
using CortexLabs.FinTrack.Application.Services;
using CortexLabs.FinTrack.Domain.Interfaces;
using CortexLabs.FinTrack.Infrastructure.Data;
using CortexLabs.FinTrack.Infrastructure.Repositories;

// ─────────────────────────────────────────────────────────────
//  CortexLabs FinTrack API — Clean Architecture entry point
//  Fixes: SMELL-01 (God Class → <60 LOC), SMELL-02 (DI),
//         SMELL-03 (config from appsettings), SMELL-08 (CORS),
//         SMELL-10 (error handling middleware)
// ─────────────────────────────────────────────────────────────

var builder = WebApplication.CreateBuilder(args);

// Configuration
var connectionString = builder.Configuration.GetConnectionString("Default")
    ?? "Data Source=fintrack.db";
var allowedOrigins = builder.Configuration.GetSection("AllowedOrigins").Get<string[]>()
    ?? new[] { "http://localhost:3000" };

// DI — Repositories (SMELL-02 fix)
builder.Services.AddSingleton<IUserRepository>(_ => new UserRepository(connectionString));
builder.Services.AddSingleton<ITransactionRepository>(_ => new TransactionRepository(connectionString));
builder.Services.AddSingleton<IAccountRepository>(_ => new AccountRepository(connectionString));

// DI — Application Services
builder.Services.AddScoped<UserService>();
builder.Services.AddScoped<TransactionService>();
builder.Services.AddScoped<AccountService>();
builder.Services.AddScoped<ReportService>();

// CORS (SMELL-08 fix)
builder.Services.AddCors(options =>
    options.AddDefaultPolicy(policy =>
        policy.WithOrigins(allowedOrigins)
              .AllowAnyMethod()
              .AllowAnyHeader()));

// Swagger
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

// Initialize database
var dbInit = new DatabaseInitializer(
    connectionString,
    app.Services.GetRequiredService<ILogger<DatabaseInitializer>>());
dbInit.Initialize();

// Middleware pipeline
app.UseMiddleware<ErrorHandlingMiddleware>();
app.UseMiddleware<RequestLoggingMiddleware>();
app.UseCors();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

// Map endpoint groups (thin — each group is its own file)
app.MapUserEndpoints();
app.MapTransactionEndpoints();
app.MapAccountEndpoints();
app.MapReportEndpoints();
app.MapHealthEndpoints();

app.Run();
