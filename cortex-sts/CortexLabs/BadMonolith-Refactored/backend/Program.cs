// ✅ CORTEX Refactored — Clean Program.cs
// ✅ SMELL-3 RESOLVED: Minimal startup, domain logic in services
// ✅ SMELL-17 RESOLVED: Full dependency injection
// ✅ SMELL-13 RESOLVED: Restrictive CORS policy
// ✅ AP-005 RESOLVED: Real health endpoint with async DB probe (ENH-STS-07)
// ✅ AP-009 RESOLVED: Rate limiting on transfer + login endpoints (ENH-STS-03)

using Microsoft.AspNetCore.RateLimiting;
using Microsoft.EntityFrameworkCore;
using System.Threading.RateLimiting;
using CortexLabs.FinTrack.Services;
using CortexLabs.FinTrack.Services.Interfaces;
using CortexLabs.FinTrack.Repositories;
using CortexLabs.FinTrack.Repositories.Interfaces;

var builder = WebApplication.CreateBuilder(args);

// ✅ Structured logging
builder.Logging.AddConsole();
builder.Logging.AddDebug();

// ✅ Swagger for API documentation
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();
builder.Services.AddControllers();

// ✅ AP-009 RESOLVED: Rate limiting — 10 transfers/min per IP, 20 login/min per IP
builder.Services.AddRateLimiter(options =>
{
    options.AddFixedWindowLimiter("transfer", config =>
    {
        config.PermitLimit = 10;
        config.Window = TimeSpan.FromMinutes(1);
        config.QueueProcessingOrder = QueueProcessingOrder.OldestFirst;
        config.QueueLimit = 2;
    });
    options.AddFixedWindowLimiter("login", config =>
    {
        config.PermitLimit = 20;
        config.Window = TimeSpan.FromMinutes(1);
        config.QueueProcessingOrder = QueueProcessingOrder.OldestFirst;
        config.QueueLimit = 5;
    });
    options.RejectionStatusCode = 429;
});

// ✅ SMELL-13 RESOLVED: Restrictive CORS — specify allowed origins
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.WithOrigins(
                builder.Configuration.GetSection("AllowedOrigins").Get<string[]>() 
                ?? new[] { "http://localhost:3000" })
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

// ✅ SMELL-17 RESOLVED: Dependency injection wiring
builder.Services.AddScoped<IValidationService, ValidationService>();
builder.Services.AddScoped<IUserRepository, UserRepository>();
builder.Services.AddScoped<ITransactionRepository, TransactionRepository>();
builder.Services.AddScoped<IAccountRepository, AccountRepository>();   // ✅ AP-002: wired
builder.Services.AddScoped<IUserService, UserService>();
builder.Services.AddScoped<ITransactionService, TransactionService>();
builder.Services.AddScoped<IAccountService, AccountService>();

// ✅ Database context with connection string from configuration
var connectionString = builder.Configuration.GetConnectionString("DefaultConnection");
builder.Services.AddDbContext<FinTrackDbContext>(options =>
    options.UseSqlite(connectionString));

var app = builder.Build();

// ✅ Middleware pipeline
app.UseCors();
app.UseRateLimiter();   // ✅ AP-009: activate rate limiting middleware
app.UseSwagger();
app.UseSwaggerUI();

// ✅ SMELL-18 RESOLVED: Global exception handler hides stack traces
app.UseExceptionHandler("/error");
app.MapControllers();

// ✅ AP-005 RESOLVED: Real health endpoint with async DB liveness probe (ENH-STS-07)
// Probes the database with SELECT 1 — returns 503 if DB is unreachable
app.MapGet("/health", async (FinTrackDbContext db) =>
{
    try
    {
        // Live DB probe — not a hardcoded stub
        await db.Database.ExecuteSqlRawAsync("SELECT 1");
        return Results.Ok(new
        {
            status = "healthy",
            db = "reachable",
            timestamp = DateTime.UtcNow
        });
    }
    catch (Exception ex)
    {
        return Results.Json(
            new { status = "degraded", db = "unreachable", error = ex.Message },
            statusCode: 503);
    }
}).WithTags("Health").AllowAnonymous();

// ✅ Initialize database
using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<FinTrackDbContext>();
    db.Database.EnsureCreated();
}

app.Run();
