using FluentAssertions;
using Microsoft.ApplicationInsights;
using Microsoft.ApplicationInsights.Extensibility;
using Microsoft.Extensions.Caching.Memory;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Moq;
using RA.FundingInvoices.Core.FeatureManagement;
using RA.FundingInvoices.Core.Monitoring;
using RA.FundingInvoices.Infrastructure.FeatureManagement;
using RA.FundingInvoices.Infrastructure.Monitoring;

namespace RA.FundingInvoices.IntegrationTests.Monitoring;

/// <summary>
/// Integration tests for automated rollback infrastructure.
/// Tests end-to-end rollback scenarios with real services.
/// </summary>
public class RollbackIntegrationTests : IDisposable
{
    private readonly ServiceProvider _serviceProvider;
    private readonly IMetricsCollector _metricsCollector;
    private readonly IRollbackTrigger _rollbackTrigger;

    public RollbackIntegrationTests()
    {
        var services = new ServiceCollection();

        // Build configuration
        var configValues = new Dictionary<string, string?>
        {
            ["RollbackThresholds:ErrorRatePercent"] = "1.0",
            ["RollbackThresholds:LatencyMs"] = "500",
            ["RollbackThresholds:SuccessRatePercent"] = "99.0",
            ["RollbackThresholds:EvaluationWindowMinutes"] = "5",
            ["CircuitBreaker:HalfOpenRetrySeconds"] = "60",
            ["AzureAppConfiguration:ConnectionString"] = "Endpoint=https://test.azconfig.io;Id=test;Secret=fake",
            ["FeatureFlags:DataLayerRollout:Enabled"] = "true",
            ["FeatureFlags:DataLayerRollout:EFCorePercentage"] = "100"
        };

        var configuration = new ConfigurationBuilder()
            .AddInMemoryCollection(configValues)
            .Build();

        // Configure Application Insights
        var telemetryConfig = new TelemetryConfiguration
        {
            ConnectionString = "InstrumentationKey=00000000-0000-0000-0000-000000000000"
        };

        // Register services
        services.AddSingleton<IConfiguration>(configuration);
        services.AddSingleton(telemetryConfig);
        services.AddSingleton<TelemetryClient>();
        services.AddLogging(builder => builder.AddConsole().SetMinimumLevel(LogLevel.Debug));
        services.AddMemoryCache();
        services.AddSingleton<IMetricsCollector, ApplicationInsightsMetricsCollector>();
        services.AddSingleton<IFeatureFlagService, AzureAppConfigurationFeatureFlagService>();
        services.AddSingleton<IRollbackTrigger, AutomatedRollbackService>();

        _serviceProvider = services.BuildServiceProvider();
        _metricsCollector = _serviceProvider.GetRequiredService<IMetricsCollector>();
        _rollbackTrigger = _serviceProvider.GetRequiredService<IRollbackTrigger>();
    }

    [Fact]
    public async Task EndToEnd_HighErrorRate_TriggersAutomatedRollback()
    {
        // Arrange - Simulate 50 failures, 50 successes (50% error rate, exceeds 1% threshold)
        for (int i = 0; i < 50; i++)
        {
            _metricsCollector.RecordSuccess("EFCore", "GetInvoice", TimeSpan.FromMilliseconds(100));
            _metricsCollector.RecordFailure("EFCore", "GetInvoice", new Exception("Test error"), TimeSpan.FromMilliseconds(150));
        }

        // Act
        var decision = await _rollbackTrigger.ShouldRollbackAsync("EFCore");

        // Assert
        decision.ShouldRollback.Should().BeTrue();
        decision.Reason.Should().Contain("Error rate");
        decision.Metrics.Should().ContainKey("ErrorRate");
        decision.Metrics["ErrorRate"].Should().Be(50.0);
    }

    [Fact]
    public async Task EndToEnd_HighLatency_TriggersAutomatedRollback()
    {
        // Arrange - Simulate operations with latency exceeding threshold
        for (int i = 0; i < 20; i++)
        {
            _metricsCollector.RecordSuccess("EFCore", "GetInvoice", TimeSpan.FromMilliseconds(600)); // Exceeds 500ms
        }

        // Act
        var decision = await _rollbackTrigger.ShouldRollbackAsync("EFCore");

        // Assert
        decision.ShouldRollback.Should().BeTrue();
        decision.Reason.Should().Contain("latency");
        decision.Metrics["AvgLatencyMs"].Should().BeGreaterThan(500);
    }

    [Fact]
    public async Task EndToEnd_LowSuccessRate_TriggersAutomatedRollback()
    {
        // Arrange - 95 successes, 5 failures = 95% success (below 99% threshold)
        for (int i = 0; i < 95; i++)
        {
            _metricsCollector.RecordSuccess("EFCore", "CreateInvoice", TimeSpan.FromMilliseconds(100));
        }

        for (int i = 0; i < 5; i++)
        {
            _metricsCollector.RecordFailure("EFCore", "CreateInvoice", new Exception("Test"), TimeSpan.FromMilliseconds(100));
        }

        // Act
        var decision = await _rollbackTrigger.ShouldRollbackAsync("EFCore");

        // Assert
        decision.ShouldRollback.Should().BeTrue();
        decision.Reason.Should().Contain("Success rate");
        decision.Metrics["SuccessRate"].Should().Be(95.0);
    }

    [Fact]
    public async Task EndToEnd_CircuitBreakerOpen_BlocksTraffic()
    {
        // Act - Manually open circuit breaker
        await _rollbackTrigger.OpenCircuitBreakerAsync("Integration test - manual open");

        // Assert
        var state = await _rollbackTrigger.GetCircuitBreakerStateAsync();
        state.Should().Be(CircuitBreakerState.Open);

        var decision = await _rollbackTrigger.ShouldRollbackAsync("EFCore");
        decision.ShouldRollback.Should().BeTrue();
        decision.Reason.Should().Contain("Circuit breaker is OPEN");
    }

    [Fact]
    public async Task EndToEnd_CircuitBreakerReset_AllowsTraffic()
    {
        // Arrange - Open then reset circuit
        await _rollbackTrigger.OpenCircuitBreakerAsync("Test");
        await _rollbackTrigger.ResetCircuitBreakerAsync();

        // Record healthy metrics
        for (int i = 0; i < 100; i++)
        {
            _metricsCollector.RecordSuccess("EFCore", "Test", TimeSpan.FromMilliseconds(50));
        }

        // Act
        var state = await _rollbackTrigger.GetCircuitBreakerStateAsync();
        var decision = await _rollbackTrigger.ShouldRollbackAsync("EFCore");

        // Assert
        state.Should().Be(CircuitBreakerState.Closed);
        decision.ShouldRollback.Should().BeFalse();
    }

    public void Dispose()
    {
        _serviceProvider?.Dispose();
    }
}
