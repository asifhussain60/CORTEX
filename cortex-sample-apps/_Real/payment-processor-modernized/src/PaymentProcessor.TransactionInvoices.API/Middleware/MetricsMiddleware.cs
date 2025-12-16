using PaymentProcessor.TransactionInvoices.Core.FeatureManagement;
using PaymentProcessor.TransactionInvoices.Core.Monitoring;
using System.Diagnostics;

namespace PaymentProcessor.TransactionInvoices.API.Middleware;

/// <summary>
/// Middleware for collecting request/response metrics.
/// Tracks data layer performance for rollout monitoring.
/// </summary>
public class MetricsMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<MetricsMiddleware> _logger;

    public MetricsMiddleware(
        RequestDelegate next,
        ILogger<MetricsMiddleware> logger)
    {
        _next = next;
        _logger = logger;
    }

    public async Task InvokeAsync(
        HttpContext context,
        IMetricsCollector metricsCollector,
        IFeatureFlagService featureFlagService)
    {
        var requestId = context.TraceIdentifier;
        var stopwatch = Stopwatch.StartNew();
        var operation = $"{context.Request.Method} {context.Request.Path}";

        // Determine which data layer will be used
        var useEFCore = await featureFlagService.ShouldUseEFCoreAsync(requestId);
        var dataLayer = useEFCore ? "EFCore" : "Mock";

        // Store in HttpContext for downstream usage
        context.Items["DataLayer"] = dataLayer;
        context.Items["RequestId"] = requestId;

        try
        {
            await _next(context);

            stopwatch.Stop();

            // Record success if no exception and 2xx/3xx status code
            if (context.Response.StatusCode < 400)
            {
                metricsCollector.RecordSuccess(dataLayer, operation, stopwatch.Elapsed);
            }
            else
            {
                // Client/server errors still recorded as failures
                metricsCollector.RecordFailure(
                    dataLayer,
                    operation,
                    new HttpRequestException($"HTTP {context.Response.StatusCode}"),
                    stopwatch.Elapsed);
            }
        }
        catch (Exception ex)
        {
            stopwatch.Stop();

            metricsCollector.RecordFailure(dataLayer, operation, ex, stopwatch.Elapsed);

            _logger.LogError(ex, "{DataLayer} request failed: {Operation}", dataLayer, operation);

            throw; // Re-throw to let global exception handler deal with it
        }
    }
}
