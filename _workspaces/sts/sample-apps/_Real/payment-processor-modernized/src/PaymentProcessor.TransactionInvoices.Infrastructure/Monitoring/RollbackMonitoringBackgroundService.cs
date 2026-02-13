using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using PaymentProcessor.TransactionInvoices.Core.Monitoring;

namespace PaymentProcessor.TransactionInvoices.Infrastructure.Monitoring;

/// <summary>
/// Background service that continuously monitors metrics and triggers rollback.
/// Runs every N seconds to check rollback conditions.
/// </summary>
public class RollbackMonitoringBackgroundService : BackgroundService
{
    private readonly IRollbackTrigger _rollbackTrigger;
    private readonly ILogger<RollbackMonitoringBackgroundService> _logger;
    private readonly IConfiguration _configuration;
    private readonly TimeSpan _checkInterval;

    public RollbackMonitoringBackgroundService(
        IRollbackTrigger rollbackTrigger,
        ILogger<RollbackMonitoringBackgroundService> logger,
        IConfiguration configuration)
    {
        _rollbackTrigger = rollbackTrigger;
        _logger = logger;
        _configuration = configuration;

        var checkIntervalSeconds = configuration.GetValue<int>("RollbackMonitoring:CheckIntervalSeconds", 30);
        _checkInterval = TimeSpan.FromSeconds(checkIntervalSeconds);
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        var isEnabled = _configuration.GetValue<bool>("RollbackMonitoring:Enabled", true);

        if (!isEnabled)
        {
            _logger.LogInformation("Rollback monitoring is disabled");
            return;
        }

        _logger.LogInformation("Rollback monitoring started (check interval: {Interval} seconds)",
            _checkInterval.TotalSeconds);

        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                await CheckRollbackConditionsAsync(stoppingToken);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error in rollback monitoring loop");
            }

            await Task.Delay(_checkInterval, stoppingToken);
        }

        _logger.LogInformation("Rollback monitoring stopped");
    }

    private async Task CheckRollbackConditionsAsync(CancellationToken cancellationToken)
    {
        try
        {
            var decision = await _rollbackTrigger.ShouldRollbackAsync("EFCore", cancellationToken);

            if (decision.ShouldRollback)
            {
                _logger.LogCritical("AUTOMATED ROLLBACK TRIGGERED: {Reason}", decision.Reason);

                var metricsLog = string.Join(", ",
                    decision.Metrics.Select(m => $"{m.Key}={m.Value:F2}"));

                _logger.LogCritical("Current metrics: {Metrics}", metricsLog);

                // Rollback is handled by AutomatedRollbackService.ShouldRollbackAsync
                // which calls featureFlagService.RollbackToMockAsync()
            }
            else
            {
                var circuitState = await _rollbackTrigger.GetCircuitBreakerStateAsync(cancellationToken);

                _logger.LogDebug("Rollback check passed - Circuit: {CircuitState}, Metrics: {Metrics}",
                    circuitState,
                    string.Join(", ", decision.Metrics.Select(m => $"{m.Key}={m.Value:F2}")));
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to check rollback conditions");
        }
    }
}
