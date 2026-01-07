using Microsoft.ApplicationInsights.Extensibility;
using Microsoft.EntityFrameworkCore;
using PaymentProcessor.TransactionInvoices.API.Middleware;
using PaymentProcessor.TransactionInvoices.Core.FeatureManagement;
using PaymentProcessor.TransactionInvoices.Core.Interfaces;
using PaymentProcessor.TransactionInvoices.Core.Monitoring;
using PaymentProcessor.TransactionInvoices.Core.Security;
using PaymentProcessor.TransactionInvoices.Infrastructure.FeatureManagement;
using PaymentProcessor.TransactionInvoices.Infrastructure.Mock;
using PaymentProcessor.TransactionInvoices.Infrastructure.Monitoring;
using PaymentProcessor.TransactionInvoices.Infrastructure.Persistence;
using PaymentProcessor.TransactionInvoices.Infrastructure.Persistence.Repositories;
using PaymentProcessor.TransactionInvoices.Infrastructure.Security;
using PaymentProcessor.TransactionInvoices.Infrastructure.EFCore;
using PaymentProcessor.TransactionInvoices.Core.Services;
using PaymentProcessor.TransactionInvoices.Infrastructure.Services;
using PaymentProcessor.TransactionInvoices.Core.Adapters;
using PaymentProcessor.TransactionInvoices.Infrastructure.Adapters;
using PaymentProcessor.TransactionInvoices.Core.DTOs;
using PaymentProcessor.TransactionInvoices.Core.Validators;
using FluentValidation;
using Serilog;

var builder = WebApplication.CreateBuilder(args);

// Configure Serilog
Log.Logger = new LoggerConfiguration()
    .ReadFrom.Configuration(builder.Configuration)
    .Enrich.FromLogContext()
    .WriteTo.Console()
    .WriteTo.File("logs/ra-transaction-invoices-.log", rollingInterval: RollingInterval.Day)
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

// Add security services (GDPR/ISO27001 compliance)
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
        Title = "PaymentProcessor Transaction Invoices API",
        Version = "v1",
        Description = "Modernized REST API for PaymentProcessor Transaction Invoices (migrated from WCF)",
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
builder.Services.AddKeyedSingleton<ITransactionInvoiceRepository, MockTransactionInvoiceRepository>("Mock");
builder.Services.AddKeyedSingleton<ITransactionBatchRepository, MockTransactionBatchRepository>("Mock");
builder.Services.AddKeyedSingleton<IAccountCategoryRepository, MockAccountCategoryRepository>("Mock");
builder.Services.AddKeyedSingleton<ICashInOutRepository, MockCashInOutRepository>("Mock");
builder.Services.AddKeyedSingleton<IUnitOfWork, MockUnitOfWork>("Mock");

// Seed mock data on startup
builder.Services.AddSingleton<MockDataSeeder>();

// EF Core repositories (keyed as "EFCore")
var connectionString = builder.Configuration.GetConnectionString("TransactionInvoicesDb");
builder.Services.AddDbContext<TransactionInvoicesDbContext>(options =>
    options.UseSqlServer(connectionString, sqlOptions =>
    {
        sqlOptions.EnableRetryOnFailure(
            maxRetryCount: 3,
            maxRetryDelay: TimeSpan.FromSeconds(5),
            errorNumbersToAdd: null);
    }));

builder.Services.AddKeyedScoped<ITransactionInvoiceRepository, PaymentProcessor.TransactionInvoices.Infrastructure.EFCore.Repositories.EFCoreTransactionInvoiceRepository>("EFCore");
builder.Services.AddKeyedScoped<ITransactionBatchRepository, PaymentProcessor.TransactionInvoices.Infrastructure.EFCore.Repositories.EFCoreTransactionBatchRepository>("EFCore");
builder.Services.AddKeyedScoped<IAccountCategoryRepository, PaymentProcessor.TransactionInvoices.Infrastructure.EFCore.Repositories.EFCoreAccountCategoryRepository>("EFCore");
builder.Services.AddKeyedScoped<ICashInOutRepository, PaymentProcessor.TransactionInvoices.Infrastructure.EFCore.Repositories.EFCoreCashInOutRepository>("EFCore");
builder.Services.AddKeyedScoped<IUnitOfWork, PaymentProcessor.TransactionInvoices.Infrastructure.EFCore.Repositories.EFCoreUnitOfWork>("EFCore");

Log.Information("Data layer configured: Both Mock and EF Core (gradual rollout enabled)");

// Phase 3: Register business logic services
builder.Services.AddScoped<ITransactionInvoiceService, TransactionInvoiceService>();
builder.Services.AddScoped<ITransactionBatchService, TransactionBatchService>();

// Phase 3: Register external service adapters
builder.Services.AddSingleton<IPaymentPlanAdapter, MockPaymentPlanAdapter>();

// Phase 3: Register FluentValidation validators
builder.Services.AddScoped<IValidator<CreateTransactionInvoiceRequest>, CreateTransactionInvoiceRequestValidator>();
builder.Services.AddScoped<IValidator<GenerateTransactionInvoiceRequest>, GenerateTransactionInvoiceRequestValidator>();
builder.Services.AddScoped<IValidator<CreateBatchTransactionInvoiceRequest>, CreateBatchTransactionInvoiceRequestValidator>();
builder.Services.AddScoped<IValidator<CloseTransactionBatchRequest>, CloseTransactionBatchRequestValidator>();
builder.Services.AddScoped<IValidator<ReopenTransactionBatchRequest>, ReopenTransactionBatchRequestValidator>();
builder.Services.AddScoped<IValidator<UpdateTransactionBatchRequest>, UpdateTransactionBatchRequestValidator>();
builder.Services.AddScoped<IValidator<CreateTransactionBatchRequest>, CreateTransactionBatchRequestValidator>();

Log.Information("Service layer configured: TransactionInvoiceService, TransactionBatchService, validators registered");

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

// GDPR/ISO27001 Security Middleware
app.UseMiddleware<DataEncryptionMiddleware>();  // Field-level encryption (before audit logging)
app.UseMiddleware<AuditLoggingMiddleware>();     // Audit logging with PII redaction

app.UseAuthorization();

app.MapControllers();

Log.Information("PaymentProcessor Transaction Invoices API starting...");

app.Run();

Log.CloseAndFlush();
