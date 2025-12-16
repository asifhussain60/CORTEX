using Microsoft.ApplicationInsights;
using Microsoft.ApplicationInsights.DataContracts;
using Microsoft.Extensions.Caching.Memory;
using Microsoft.Extensions.Logging;
using RA.FundingInvoices.Core.Monitoring;
using System.Collections.Concurrent;

namespace RA.FundingInvoices.Infrastructure.Monitoring;

/// <summary>
/// Application Insights implementation of metrics collector.
/// Tracks real-time performance and error metrics for deployment monitoring.
/// </summary>
public class ApplicationInsightsMetricsCollector : IMetricsCollector
{
    private readonly TelemetryClient _telemetryClient;
    private readonly ILogger<ApplicationInsightsMetricsCollector> _logger;
    private readonly IMemoryCache _cache;

    // In-memory storage for recent requests (for calculating error rates)
    private readonly ConcurrentQueue<RequestMetric> _recentRequests = new();
    private readonly TimeSpan _metricsRetention = TimeSpan.FromMinutes(10);

    public ApplicationInsightsMetricsCollector(
        TelemetryClient telemetryClient,
        ILogger<ApplicationInsightsMetricsCollector> logger,
        IMemoryCache cache)
    {
        _telemetryClient = telemetryClient;
        _logger = logger;
        _cache = cache;
    }

    public void RecordSuccess(string dataLayer, string operation, TimeSpan duration)
    {
        var properties = new Dictionary<string, string>
        {
            ["DataLayer"] = dataLayer,
            ["Operation"] = operation,
            ["Status"] = "Success"
        };

        var metrics = new Dictionary<string, double>
        {
            ["DurationMs"] = duration.TotalMilliseconds
        };

        // Track in Application Insights
        _telemetryClient.TrackEvent($"DataLayer.{operation}", properties, metrics);

        // Track response time metric
        _telemetryClient.TrackMetric(
            new MetricTelemetry($"DataLayer.ResponseTime.{dataLayer}", duration.TotalMilliseconds)
            {
                Properties = { ["Operation"] = operation }
            });

        // Store in local queue for rate calculations
        _recentRequests.Enqueue(new RequestMetric
        {
            Timestamp = DateTime.UtcNow,
            DataLayer = dataLayer,
            Operation = operation,
            IsSuccess = true,
            Duration = duration
        });

        CleanupOldMetrics();

        _logger.LogDebug("{DataLayer} {Operation} completed successfully in {Duration}ms",
            dataLayer, operation, duration.TotalMilliseconds);
    }

    public void RecordFailure(string dataLayer, string operation, Exception exception, TimeSpan duration)
    {
        var properties = new Dictionary<string, string>
        {
            ["DataLayer"] = dataLayer,
            ["Operation"] = operation,
            ["Status"] = "Failure",
            ["ExceptionType"] = exception.GetType().Name,
            ["ErrorMessage"] = exception.Message
        };

        var metrics = new Dictionary<string, double>
        {
            ["DurationMs"] = duration.TotalMilliseconds
        };

        // Track in Application Insights
        _telemetryClient.TrackEvent($"DataLayer.{operation}.Error", properties, metrics);

        // Track exception
        _telemetryClient.TrackException(exception, properties);

        // Track error metric
        _telemetryClient.TrackMetric(
            new MetricTelemetry($"DataLayer.ErrorCount.{dataLayer}", 1)
            {
                Properties = { ["Operation"] = operation }
            });

        // Store in local queue
        _recentRequests.Enqueue(new RequestMetric
        {
            Timestamp = DateTime.UtcNow,
            DataLayer = dataLayer,
            Operation = operation,
            IsSuccess = false,
            Duration = duration,
            Exception = exception
        });

        CleanupOldMetrics();

        _logger.LogError(exception, "{DataLayer} {Operation} failed after {Duration}ms",
            dataLayer, operation, duration.TotalMilliseconds);
    }

    public void RecordConnectionPoolMetrics(int activeConnections, int idleConnections, int totalConnections)
    {
        _telemetryClient.TrackMetric("Database.ConnectionPool.Active", activeConnections);
        _telemetryClient.TrackMetric("Database.ConnectionPool.Idle", idleConnections);
        _telemetryClient.TrackMetric("Database.ConnectionPool.Total", totalConnections);

        var utilizationPercentage = totalConnections > 0
            ? (double)activeConnections / totalConnections * 100
            : 0;

        _telemetryClient.TrackMetric("Database.ConnectionPool.UtilizationPercent", utilizationPercentage);

        _logger.LogDebug("Connection pool: {Active}/{Total} active ({Utilization}% utilization)",
            activeConnections, totalConnections, utilizationPercentage);
    }

    public Task<double> GetErrorRateAsync(string dataLayer, CancellationToken cancellationToken = default)
    {
        var now = DateTime.UtcNow;
        var oneMinuteAgo = now.AddMinutes(-1);

        var recentMetrics = _recentRequests
            .Where(m => m.Timestamp >= oneMinuteAgo && m.DataLayer == dataLayer)
            .ToList();

        if (!recentMetrics.Any())
        {
            return Task.FromResult(0.0);
        }

        var errorCount = recentMetrics.Count(m => !m.IsSuccess);
        var totalCount = recentMetrics.Count;

        var errorRate = (double)errorCount / totalCount * 100;

        return Task.FromResult(errorRate);
    }

    public Task<double> GetAverageResponseTimeAsync(string dataLayer, int minutes, CancellationToken cancellationToken = default)
    {
        var cutoff = DateTime.UtcNow.AddMinutes(-minutes);

        var recentMetrics = _recentRequests
            .Where(m => m.Timestamp >= cutoff && m.DataLayer == dataLayer && m.IsSuccess)
            .ToList();

        if (!recentMetrics.Any())
        {
            return Task.FromResult(0.0);
        }

        var averageMs = recentMetrics.Average(m => m.Duration.TotalMilliseconds);

        return Task.FromResult(averageMs);
    }

    public Task<double> GetSuccessRateAsync(string dataLayer, int minutes, CancellationToken cancellationToken = default)
    {
        var cutoff = DateTime.UtcNow.AddMinutes(-minutes);

        var recentMetrics = _recentRequests
            .Where(m => m.Timestamp >= cutoff && m.DataLayer == dataLayer)
            .ToList();

        if (!recentMetrics.Any())
        {
            return Task.FromResult(100.0); // No data = assume success
        }

        var successCount = recentMetrics.Count(m => m.IsSuccess);
        var totalCount = recentMetrics.Count;

        var successRate = (double)successCount / totalCount * 100;

        return Task.FromResult(successRate);
    }

    public void TrackMetric(string metricName, double value, IDictionary<string, string>? properties = null)
    {
        var telemetry = new MetricTelemetry(metricName, value);

        if (properties != null)
        {
            foreach (var prop in properties)
            {
                telemetry.Properties[prop.Key] = prop.Value;
            }
        }

        _telemetryClient.TrackMetric(telemetry);
    }

    public void TrackEvent(string eventName, IDictionary<string, string>? properties = null)
    {
        _telemetryClient.TrackEvent(eventName, properties);
    }

    private void CleanupOldMetrics()
    {
        var cutoff = DateTime.UtcNow - _metricsRetention;

        while (_recentRequests.TryPeek(out var oldest) && oldest.Timestamp < cutoff)
        {
            _recentRequests.TryDequeue(out _);
        }
    }

    private class RequestMetric
    {
        public DateTime Timestamp { get; init; }
        public required string DataLayer { get; init; }
        public required string Operation { get; init; }
        public bool IsSuccess { get; init; }
        public TimeSpan Duration { get; init; }
        public Exception? Exception { get; init; }
    }
}
