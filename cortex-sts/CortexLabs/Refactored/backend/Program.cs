// ✅ SMELL-3 FIXED: Program.cs is now a thin composition root (~60 LOC vs 591 LOC)
//    All domains extracted into endpoint modules in Api/Endpoints/
// ✅ SMELL-13 FIXED: CORS configured to explicit origin list from IConfiguration
// ✅ SMELL-16 FIXED: AppCache static class removed — no global mutable state
// ✅ SMELL-17 FIXED: All services registered via DI (AddScoped — no Singleton capturing Scoped)
// ✅ SMELL-18 FIXED: Rate limiting on auth endpoint + UseExceptionHandler (RFC 7807)
// ✅ SMELL-2 FIXED: No secrets in appsettings.json — use environment variables / user-secrets

using System.Text;
using CortexLabs.FinTrack.Api.Endpoints;
using CortexLabs.FinTrack.Api.Middleware;
using CortexLabs.FinTrack.Application.Interfaces;
using CortexLabs.FinTrack.Application.Services;
using CortexLabs.FinTrack.Infrastructure.Database;
using CortexLabs.FinTrack.Infrastructure.Security;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.RateLimiting;
using Microsoft.IdentityModel.Tokens;

var builder = WebApplication.CreateBuilder(args);

// ── LOGGING ──────────────────────────────────────────────────────────────────
// ✅ SMELL-11 FIXED: ILogger<T> injected into all services — no Console.WriteLine
builder.Logging.ClearProviders().AddConsole().AddDebug();

// ── API DOCUMENTATION ────────────────────────────────────────────────────────
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(o =>
{
    o.SwaggerDoc("v1", new() { Title = "CortexLabs FinTrack API", Version = "v1" });
});

// ── AUTHENTICATION / JWT ─────────────────────────────────────────────────────
// ✅ SMELL-2 FIXED: Secret from configuration — set via env var or user-secrets
var jwtSecret = builder.Configuration["JwtSettings:Secret"]
    ?? throw new InvalidOperationException("JwtSettings:Secret must be set via environment variable or user-secrets.");

builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(o =>
    {
        o.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = builder.Configuration["JwtSettings:Issuer"] ?? "cortexlabs-fintrack",
            ValidAudience = builder.Configuration["JwtSettings:Audience"] ?? "cortexlabs-fintrack-users",
            IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtSecret))
        };
    });

builder.Services.AddAuthorization();

// ── CORS — explicit allowlist (SMELL-13 FIXED) ──────────────────────────────
// ✅ SMELL-13 FIXED: Specific origin from config — no AllowAnyOrigin()
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        var allowed = builder.Configuration.GetSection("Cors:AllowedOrigins").Get<string[]>()
            ?? ["http://localhost:3000"];
        policy.WithOrigins(allowed)
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

// ── RATE LIMITING (SMELL-18 FIXED) ──────────────────────────────────────────
// ✅ SMELL-18 FIXED: Login endpoint rate-limited (AP-009 resolved)
builder.Services.AddRateLimiter(o =>
{
    o.AddFixedWindowLimiter("auth", limiter =>
    {
        limiter.PermitLimit = 10;
        limiter.Window = TimeSpan.FromMinutes(1);
    });
});

// ── RFC 7807 EXCEPTION HANDLER (SMELL-18 FIXED) ─────────────────────────────
builder.Services.AddExceptionHandler<GlobalExceptionHandler>();
builder.Services.AddProblemDetails();

// ── DEPENDENCY INJECTION (SMELL-17 FIXED) ───────────────────────────────────
// ✅ All services registered as Scoped — no Singleton capturing Scoped (AP-006 resolved)
builder.Services.AddScoped<IValidationService, ValidationService>();
builder.Services.AddScoped<IUserService, UserService>();
builder.Services.AddScoped<ITransactionService, TransactionService>();
builder.Services.AddScoped<IAccountService, AccountService>();
builder.Services.AddScoped<IReportService, ReportService>();
builder.Services.AddScoped<IAnalyticsService, AnalyticsService>();
builder.Services.AddScoped<IAuthService, AuthService>();

var app = builder.Build();

// ── DATABASE INITIALISATION (SMELL-4 FIXED — extracted from startup) ────────
var connStr = builder.Configuration.GetConnectionString("DefaultConnection")
    ?? "Data Source=fintrack.db";
await DatabaseInitialiser.InitialiseAsync(connStr);

// ── MIDDLEWARE PIPELINE ──────────────────────────────────────────────────────
app.UseExceptionHandler();   // RFC 7807 — no stack traces to clients
app.UseCors();
app.UseRateLimiter();
app.UseAuthentication();
app.UseAuthorization();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

// ── ENDPOINT REGISTRATION (domain-separated modules) ────────────────────────
// ✅ SMELL-3 FIXED: each domain registers its own routes
app.MapUserEndpoints();
app.MapTransactionEndpoints();
app.MapAccountEndpoints();
app.MapReportEndpoints();
app.MapAuthEndpoints();
app.MapAnalyticsEndpoints();

app.Run();

// Expose type for integration tests
public partial class Program { }
