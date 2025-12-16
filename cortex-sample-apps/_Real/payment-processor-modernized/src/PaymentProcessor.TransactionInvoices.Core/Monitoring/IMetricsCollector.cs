namespace PaymentProcessor.TransactionInvoices.Core.Monitoring;

/// <summary>
/// Abstraction for metrics collection and monitoring.
/// Tracks data layer performance, errors, and health metrics.
/// </summary>
public interface IMetricsCollector
{
    /// <summary>
    /// Records a successful request with execution details.
    /// </summary>
    void RecordSuccess(string dataLayer, string operation, TimeSpan duration);

    /// <summary>
    /// Records a failed request with error details.
    /// </summary>
    void RecordFailure(string dataLayer, string operation, Exception exception, TimeSpan duration);

    /// <summary>
    /// Records database connection pool metrics.
    /// </summary>
    void RecordConnectionPoolMetrics(int activeConnections, int idleConnections, int totalConnections);

    /// <summary>
    /// Gets current error rate (errors per minute).
    /// </summary>
    Task<double> GetErrorRateAsync(string dataLayer, CancellationToken cancellationToken = default);

    /// <summary>
    /// Gets average response time (milliseconds) over last N minutes.
    /// </summary>
    Task<double> GetAverageResponseTimeAsync(string dataLayer, int minutes, CancellationToken cancellationToken = default);

    /// <summary>
    /// Gets success rate (percentage) over last N minutes.
    /// </summary>
    Task<double> GetSuccessRateAsync(string dataLayer, int minutes, CancellationToken cancellationToken = default);

    /// <summary>
    /// Tracks custom metric for Application Insights dashboards.
    /// </summary>
    void TrackMetric(string metricName, double value, IDictionary<string, string>? properties = null);

    /// <summary>
    /// Tracks custom event for audit trail.
    /// </summary>
    void TrackEvent(string eventName, IDictionary<string, string>? properties = null);
}
