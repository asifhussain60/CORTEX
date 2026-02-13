using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using RA.FundingInvoices.Core.FeatureManagement;
using RA.FundingInvoices.Core.Monitoring;

namespace RA.FundingInvoices.Infrastructure.Monitoring;

/// <summary>
/// Automated rollback service with circuit breaker pattern.
/// Monitors metrics and triggers rollback when thresholds exceeded.
/// </summary>
public class AutomatedRollbackService : IRollbackTrigger
{
    private readonly IMetricsCollector _metricsCollector;
    private readonly IFeatureFlagService _featureFlagService;
    private readonly ILogger<AutomatedRollbackService> _logger;
    private readonly IConfiguration _configuration;

    private CircuitBreakerState _circuitState = CircuitBreakerState.Closed;
    private DateTime? _circuitOpenedAt;
    private readonly TimeSpan _halfOpenRetryDelay;

    // Thresholds from configuration
    private readonly double _errorRateThreshold;
    private readonly double _latencyThresholdMs;
    private readonly double _successRateThreshold;
    private readonly int _evaluationWindowMinutes;

    public AutomatedRollbackService(
        IMetricsCollector metricsCollector,
        IFeatureFlagService featureFlagService,
        ILogger<AutomatedRollbackService> logger,
        IConfiguration configuration)
    {
        _metricsCollector = metricsCollector;
        _featureFlagService = featureFlagService;
        _logger = logger;
        _configuration = configuration;

        // Load thresholds from configuration
        _errorRateThreshold = configuration.GetValue<double>("RollbackThresholds:ErrorRatePercent", 0.1);
        _latencyThresholdMs = configuration.GetValue<double>("RollbackThresholds:LatencyMs", 200);
        _successRateThreshold = configuration.GetValue<double>("RollbackThresholds:SuccessRatePercent", 99.9);
        _evaluationWindowMinutes = configuration.GetValue<int>("RollbackThresholds:EvaluationWindowMinutes", 5);
        
        var halfOpenRetrySeconds = configuration.GetValue<int>("CircuitBreaker:HalfOpenRetrySeconds", 60);
        _halfOpenRetryDelay = TimeSpan.FromSeconds(halfOpenRetrySeconds);
    }

    public async Task<RollbackDecision> ShouldRollbackAsync(string dataLayer, CancellationToken cancellationToken = default)
    {
        // If circuit is open, always rollback
        if (_circuitState == CircuitBreakerState.Open)
        {
            // Check if we should transition to half-open
            if (_circuitOpenedAt.HasValue &&
                DateTime.UtcNow - _circuitOpenedAt.Value >= _halfOpenRetryDelay)
            {
                _logger.LogInformation("Circuit breaker transitioning to HalfOpen state");
                _circuitState = CircuitBreakerState.HalfOpen;
            }
            else
            {
                return new RollbackDecision
                {
                    ShouldRollback = true,
                    Reason = "Circuit breaker is OPEN"
                };
            }
        }

        var metrics = new Dictionary<string, double>();

        try
        {
            // Get current metrics
            var errorRate = await _metricsCollector.GetErrorRateAsync(dataLayer, cancellationToken);
            var avgLatency = await _metricsCollector.GetAverageResponseTimeAsync(
                dataLayer, _evaluationWindowMinutes, cancellationToken);
            var successRate = await _metricsCollector.GetSuccessRateAsync(
                dataLayer, _evaluationWindowMinutes, cancellationToken);

            metrics["ErrorRate"] = errorRate;
            metrics["AvgLatencyMs"] = avgLatency;
            metrics["SuccessRate"] = successRate;

            // Check thresholds
            if (errorRate > _errorRateThreshold)
            {
                _logger.LogWarning("Error rate threshold exceeded: {ErrorRate}% > {Threshold}%",
                    errorRate, _errorRateThreshold);

                await OpenCircuitBreakerAsync($"Error rate {errorRate:F2}% exceeds threshold {_errorRateThreshold}%",
                    cancellationToken);

                return new RollbackDecision
                {
                    ShouldRollback = true,
                    Reason = $"Error rate {errorRate:F2}% exceeds threshold {_errorRateThreshold}%",
                    Metrics = metrics
                };
            }

            if (avgLatency > _latencyThresholdMs)
            {
                _logger.LogWarning("Latency threshold exceeded: {Latency}ms > {Threshold}ms",
                    avgLatency, _latencyThresholdMs);

                await OpenCircuitBreakerAsync($"Average latency {avgLatency:F0}ms exceeds threshold {_latencyThresholdMs}ms",
                    cancellationToken);

                return new RollbackDecision
                {
                    ShouldRollback = true,
                    Reason = $"Average latency {avgLatency:F0}ms exceeds threshold {_latencyThresholdMs}ms",
                    Metrics = metrics
                };
            }

            if (successRate < _successRateThreshold)
            {
                _logger.LogWarning("Success rate below threshold: {SuccessRate}% < {Threshold}%",
                    successRate, _successRateThreshold);

                await OpenCircuitBreakerAsync($"Success rate {successRate:F2}% below threshold {_successRateThreshold}%",
                    cancellationToken);

                return new RollbackDecision
                {
                    ShouldRollback = true,
                    Reason = $"Success rate {successRate:F2}% below threshold {_successRateThreshold}%",
                    Metrics = metrics
                };
            }

            // All metrics healthy - close circuit if half-open
            if (_circuitState == CircuitBreakerState.HalfOpen)
            {
                _logger.LogInformation("Metrics healthy in HalfOpen state, closing circuit breaker");
                await ResetCircuitBreakerAsync(cancellationToken);
            }

            return new RollbackDecision
            {
                ShouldRollback = false,
                Metrics = metrics
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error evaluating rollback triggers");

            // On error, err on side of caution
            return new RollbackDecision
            {
                ShouldRollback = true,
                Reason = $"Failed to evaluate metrics: {ex.Message}",
                Metrics = metrics
            };
        }
    }

    public Task<CircuitBreakerState> GetCircuitBreakerStateAsync(CancellationToken cancellationToken = default)
    {
        return Task.FromResult(_circuitState);
    }

    public async Task OpenCircuitBreakerAsync(string reason, CancellationToken cancellationToken = default)
    {
        if (_circuitState == CircuitBreakerState.Open)
        {
            return; // Already open
        }

        _logger.LogCritical("CIRCUIT BREAKER OPENED: {Reason}", reason);

        _circuitState = CircuitBreakerState.Open;
        _circuitOpenedAt = DateTime.UtcNow;

        // Trigger immediate rollback
        await _featureFlagService.RollbackToMockAsync(reason, cancellationToken);

        // Track event for Application Insights
        _metricsCollector.TrackEvent("CircuitBreaker.Opened", new Dictionary<string, string>
        {
            ["Reason"] = reason,
            ["Timestamp"] = DateTime.UtcNow.ToString("O")
        });
    }

    public Task ResetCircuitBreakerAsync(CancellationToken cancellationToken = default)
    {
        if (_circuitState == CircuitBreakerState.Closed)
        {
            return Task.CompletedTask; // Already closed
        }

        _logger.LogInformation("Circuit breaker RESET to Closed state");

        _circuitState = CircuitBreakerState.Closed;
        _circuitOpenedAt = null;

        _metricsCollector.TrackEvent("CircuitBreaker.Closed", new Dictionary<string, string>
        {
            ["Timestamp"] = DateTime.UtcNow.ToString("O")
        });

        return Task.CompletedTask;
    }
}
