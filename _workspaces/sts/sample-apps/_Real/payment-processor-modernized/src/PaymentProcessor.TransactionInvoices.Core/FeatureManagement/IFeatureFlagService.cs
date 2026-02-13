namespace PaymentProcessor.TransactionInvoices.Core.FeatureManagement;

/// <summary>
/// Abstraction for feature flag management.
/// Supports gradual rollout and real-time configuration updates.
/// </summary>
public interface IFeatureFlagService
{
    /// <summary>
    /// Gets the current EF Core traffic percentage (0-100).
    /// Controls gradual rollout: 0% (all Mock) → 100% (all EF Core).
    /// </summary>
    Task<int> GetEFCoreTrafficPercentageAsync(CancellationToken cancellationToken = default);

    /// <summary>
    /// Determines if a specific request should use EF Core data layer.
    /// Uses deterministic routing based on request ID for consistency.
    /// </summary>
    /// <param name="requestId">Unique request identifier for deterministic routing</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>True if request should use EF Core, false for Mock</returns>
    Task<bool> ShouldUseEFCoreAsync(string requestId, CancellationToken cancellationToken = default);

    /// <summary>
    /// Checks if feature flag system is enabled.
    /// When disabled, all traffic uses configured default data layer.
    /// </summary>
    Task<bool> IsFeatureFlagEnabledAsync(CancellationToken cancellationToken = default);

    /// <summary>
    /// Updates the EF Core traffic percentage (admin operation).
    /// Changes apply immediately without API restart.
    /// </summary>
    /// <param name="percentage">New traffic percentage (0-100)</param>
    /// <param name="cancellationToken">Cancellation token</param>
    Task SetEFCoreTrafficPercentageAsync(int percentage, CancellationToken cancellationToken = default);

    /// <summary>
    /// Forces rollback to 0% EF Core traffic (emergency stop).
    /// Used by automated rollback system when errors exceed threshold.
    /// </summary>
    Task RollbackToMockAsync(string reason, CancellationToken cancellationToken = default);
}
