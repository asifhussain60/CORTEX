namespace PaymentProcessor.TransactionInvoices.Core.Monitoring;

/// <summary>
/// Defines thresholds and conditions that trigger automated rollback.
/// </summary>
public interface IRollbackTrigger
{
    /// <summary>
    /// Checks if rollback should be triggered based on current metrics.
    /// </summary>
    /// <param name="dataLayer">Data layer to check (EFCore or Mock)</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Rollback decision with reason if triggered</returns>
    Task<RollbackDecision> ShouldRollbackAsync(string dataLayer, CancellationToken cancellationToken = default);

    /// <summary>
    /// Gets current circuit breaker state.
    /// </summary>
    Task<CircuitBreakerState> GetCircuitBreakerStateAsync(CancellationToken cancellationToken = default);

    /// <summary>
    /// Manually opens circuit breaker (emergency stop).
    /// </summary>
    Task OpenCircuitBreakerAsync(string reason, CancellationToken cancellationToken = default);

    /// <summary>
    /// Resets circuit breaker after recovery.
    /// </summary>
    Task ResetCircuitBreakerAsync(CancellationToken cancellationToken = default);
}

public class RollbackDecision
{
    public bool ShouldRollback { get; init; }
    public string? Reason { get; init; }
    public Dictionary<string, double> Metrics { get; init; } = new();
}

public enum CircuitBreakerState
{
    Closed,      // Normal operation
    Open,        // Circuit broken, all requests fail-fast
    HalfOpen     // Testing if system recovered
}
