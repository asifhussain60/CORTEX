using Microsoft.ApplicationInsights.Extensibility;
using Microsoft.EntityFrameworkCore;
using RA.FundingInvoices.API.Middleware;
using RA.FundingInvoices.Core.FeatureManagement;
using RA.FundingInvoices.Core.Interfaces;
using RA.FundingInvoices.Core.Monitoring;
using RA.FundingInvoices.Core.Security;
using RA.FundingInvoices.Infrastructure.FeatureManagement;
using RA.FundingInvoices.Infrastructure.Mock;
using RA.FundingInvoices.Infrastructure.Monitoring;
using RA.FundingInvoices.Infrastructure.Persistence;
using RA.FundingInvoices.Infrastructure.Persistence.Repositories;
using RA.FundingInvoices.Infrastructure.Security;
using RA.FundingInvoices.Infrastructure.EFCore;
using RA.FundingInvoices.Core.Services;
using RA.FundingInvoices.Infrastructure.Services;
using RA.FundingInvoices.Core.Adapters;
using RA.FundingInvoices.Infrastructure.Adapters;
using RA.FundingInvoices.Core.DTOs;
using RA.FundingInvoices.Core.Validators;
using FluentValidation;
using Serilog;

var builder = WebApplication.CreateBuilder(args);

// Configure Serilog
Log.Logger = new LoggerConfiguration()
    .ReadFrom.Configuration(builder.Configuration)
    .Enrich.FromLogContext()
    .WriteTo.Console()
    .WriteTo.File("logs/ra-funding-invoices-.log", rollingInterval: RollingInterval.Day)
    .CreateLogger();

builder.Host.UseSerilog();

// Add services to the container
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();

// Add Application Insights for monitoring
builder.Services.AddApplicationInsightsTelemetry(options =>
{
    options.ConnectionString = builder.Configuration["ApplicationInsights:ConnectionString"];
});

// Add memory cache (used by encryption, feature flags, monitoring)
builder.Services.AddMemoryCache();

// Add security services (HIPAA/SOC2 compliance)
builder.Services.AddSingleton<IEncryptionService, AzureKeyVaultEncryptionService>();

// Add feature management services (Phase 6)
builder.Services.AddSingleton<IFeatureFlagService, AzureAppConfigurationFeatureFlagService>();
builder.Services.AddSingleton<DataLayerRouter>();

// Add monitoring services (Phase 6)
builder.Services.AddSingleton<IMetricsCollector, ApplicationInsightsMetricsCollector>();
builder.Services.AddSingleton<IRollbackTrigger, AutomatedRollbackService>();

// Add rollback monitoring background service
builder.Services.AddHostedService<RollbackMonitoringBackgroundService>();

builder.Services.AddSwaggerGen(options =>
{
    options.SwaggerDoc("v1", new Microsoft.OpenApi.Models.OpenApiInfo
    {
        Title = "RA Funding Invoices API",
        Version = "v1",
        Description = "Modernized REST API for RA Funding Invoices (migrated from WCF)",
        Contact = new Microsoft.OpenApi.Models.OpenApiContact
        {
            Name = "Platform Team",
            Email = "platform@example.com"
        }
    });

    // Include XML comments for Swagger documentation
    var xmlFile = $"{System.Reflection.Assembly.GetExecutingAssembly().GetName().Name}.xml";
    var xmlPath = Path.Combine(AppContext.BaseDirectory, xmlFile);
    if (File.Exists(xmlPath))
    {
        options.IncludeXmlComments(xmlPath);
    }

    // Add response examples and schemas
    options.EnableAnnotations();
});

// Configure data layer with keyed services for feature flag routing
// Register both Mock AND EF Core implementations (Phase 6 gradual rollout)

// Mock repositories (keyed as "Mock")
builder.Services.AddKeyedSingleton<IFundingInvoiceRepository, MockFundingInvoiceRepository>("Mock");
builder.Services.AddKeyedSingleton<IFundingBatchRepository, MockFundingBatchRepository>("Mock");
builder.Services.AddKeyedSingleton<ISubaccountRepository, MockSubaccountRepository>("Mock");
builder.Services.AddKeyedSingleton<ICashInOutRepository, MockCashInOutRepository>("Mock");
builder.Services.AddKeyedSingleton<IUnitOfWork, MockUnitOfWork>("Mock");

// Seed mock data on startup
builder.Services.AddSingleton<MockDataSeeder>();

// EF Core repositories (keyed as "EFCore")
var connectionString = builder.Configuration.GetConnectionString("FundingInvoicesDb");
builder.Services.AddDbContext<FundingInvoicesDbContext>(options =>
    options.UseSqlServer(connectionString, sqlOptions =>
    {
        sqlOptions.EnableRetryOnFailure(
            maxRetryCount: 3,
            maxRetryDelay: TimeSpan.FromSeconds(5),
            errorNumbersToAdd: null);
    }));

builder.Services.AddKeyedScoped<IFundingInvoiceRepository, RA.FundingInvoices.Infrastructure.EFCore.Repositories.EFCoreFundingInvoiceRepository>("EFCore");
builder.Services.AddKeyedScoped<IFundingBatchRepository, RA.FundingInvoices.Infrastructure.EFCore.Repositories.EFCoreFundingBatchRepository>("EFCore");
builder.Services.AddKeyedScoped<ISubaccountRepository, RA.FundingInvoices.Infrastructure.EFCore.Repositories.EFCoreSubaccountRepository>("EFCore");
builder.Services.AddKeyedScoped<ICashInOutRepository, RA.FundingInvoices.Infrastructure.EFCore.Repositories.EFCoreCashInOutRepository>("EFCore");
builder.Services.AddKeyedScoped<IUnitOfWork, RA.FundingInvoices.Infrastructure.EFCore.Repositories.EFCoreUnitOfWork>("EFCore");

Log.Information("Data layer configured: Both Mock and EF Core (gradual rollout enabled)");

// Phase 3: Register business logic services
builder.Services.AddScoped<IFundingInvoiceService, FundingInvoiceService>();
builder.Services.AddScoped<IFundingBatchService, FundingBatchService>();

// Phase 3: Register external service adapters
builder.Services.AddSingleton<IReimbursementPlanAdapter, MockReimbursementPlanAdapter>();

// Phase 3: Register FluentValidation validators
builder.Services.AddScoped<IValidator<CreateFundingInvoiceRequest>, CreateFundingInvoiceRequestValidator>();
builder.Services.AddScoped<IValidator<GenerateFundingInvoiceRequest>, GenerateFundingInvoiceRequestValidator>();
builder.Services.AddScoped<IValidator<CreateBatchFundingInvoiceRequest>, CreateBatchFundingInvoiceRequestValidator>();
builder.Services.AddScoped<IValidator<CloseFundingBatchRequest>, CloseFundingBatchRequestValidator>();
builder.Services.AddScoped<IValidator<ReopenFundingBatchRequest>, ReopenFundingBatchRequestValidator>();
builder.Services.AddScoped<IValidator<UpdateFundingBatchRequest>, UpdateFundingBatchRequestValidator>();
builder.Services.AddScoped<IValidator<CreateFundingBatchRequest>, CreateFundingBatchRequestValidator>();

Log.Information("Service layer configured: FundingInvoiceService, FundingBatchService, validators registered");

var app = builder.Build();

// Seed mock data (always seed for testing, even during gradual rollout)
var seeder = app.Services.GetRequiredService<MockDataSeeder>();
seeder.SeedData();
Log.Information("Mock data seeded: 100+ test scenarios");

// Configure the HTTP request pipeline
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();

// Phase 6: Metrics collection middleware (before all other middleware)
app.UseMiddleware<MetricsMiddleware>();

// Phase 4: Global exception handling (RFC 7807 ProblemDetails)
app.UseMiddleware<ProblemDetailsMiddleware>();

// HIPAA/SOC2 Security Middleware
app.UseMiddleware<DataEncryptionMiddleware>();  // Field-level encryption (before audit logging)
app.UseMiddleware<AuditLoggingMiddleware>();     // Audit logging with PHI redaction

app.UseAuthorization();

app.MapControllers();

Log.Information("RA Funding Invoices API starting...");

app.Run();

Log.CloseAndFlush();
