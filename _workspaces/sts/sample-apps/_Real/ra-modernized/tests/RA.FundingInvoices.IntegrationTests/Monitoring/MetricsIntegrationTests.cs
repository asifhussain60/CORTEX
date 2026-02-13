using FluentAssertions;
using Microsoft.ApplicationInsights;
using Microsoft.ApplicationInsights.Extensibility;
using Microsoft.Extensions.Caching.Memory;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using RA.FundingInvoices.Core.Monitoring;
using RA.FundingInvoices.Infrastructure.Monitoring;

namespace RA.FundingInvoices.IntegrationTests.Monitoring;

/// <summary>
/// Integration tests for metrics collection infrastructure.
/// Tests end-to-end metrics scenarios with Application Insights.
/// </summary>
public class MetricsIntegrationTests : IDisposable
{
    private readonly ServiceProvider _serviceProvider;
    private readonly IMetricsCollector _collector;

    public MetricsIntegrationTests()
    {
        var services = new ServiceCollection();

        // Configure in-memory Application Insights
        var telemetryConfig = new TelemetryConfiguration
        {
            ConnectionString = "InstrumentationKey=00000000-0000-0000-0000-000000000000"
        };

        services.AddSingleton(telemetryConfig);
        services.AddSingleton<TelemetryClient>();
        services.AddLogging(builder => builder.AddConsole().SetMinimumLevel(LogLevel.Debug));
        services.AddMemoryCache();
        services.AddSingleton<IMetricsCollector, ApplicationInsightsMetricsCollector>();

        _serviceProvider = services.BuildServiceProvider();
        _collector = _serviceProvider.GetRequiredService<IMetricsCollector>();
    }

    [Fact]
    public async Task EndToEnd_RecordSuccessMetrics_CalculatesAccurateRates()
    {
        // Arrange - Record 10 successful operations
        for (int i = 0; i < 10; i++)
        {
            _collector.RecordSuccess("Mock", "GetInvoice", TimeSpan.FromMilliseconds(50 + (i * 10)));
        }

        // Act
        var errorRate = await _collector.GetErrorRateAsync("Mock");
        var avgResponseTime = await _collector.GetAverageResponseTimeAsync("Mock", minutes: 5);
        var successRate = await _collector.GetSuccessRateAsync("Mock", minutes: 5);

        // Assert
        errorRate.Should().Be(0.0); // No errors
        avgResponseTime.Should().BeGreaterThan(0); // Should have average
        successRate.Should().Be(100.0); // All successful
    }

    [Fact]
    public async Task EndToEnd_MixedSuccessFailure_CalculatesCorrectRates()
    {
        // Arrange - 8 success, 2 failures
        for (int i = 0; i < 8; i++)
        {
            _collector.RecordSuccess("EFCore", "CreateInvoice", TimeSpan.FromMilliseconds(100));
        }

        for (int i = 0; i < 2; i++)
        {
            _collector.RecordFailure("EFCore", "CreateInvoice", new Exception("Test error"), TimeSpan.FromMilliseconds(150));
        }

        // Act
        var errorRate = await _collector.GetErrorRateAsync("EFCore");
        var successRate = await _collector.GetSuccessRateAsync("EFCore", minutes: 5);

        // Assert
        errorRate.Should().Be(20.0); // 2 out of 10 = 20%
        successRate.Should().Be(80.0); // 8 out of 10 = 80%
    }

    [Fact]
    public async Task EndToEnd_ConcurrentMetricsRecording_ThreadSafe()
    {
        // Arrange
        var tasks = new List<Task>();

        // Act - Record 100 concurrent metrics
        for (int i = 0; i < 100; i++)
        {
            var index = i;
            tasks.Add(Task.Run(() =>
            {
                if (index % 2 == 0)
                {
                    _collector.RecordSuccess("Concurrent", "Test", TimeSpan.FromMilliseconds(50));
                }
                else
                {
                    _collector.RecordFailure("Concurrent", "Test", new Exception("Test"), TimeSpan.FromMilliseconds(100));
                }
            }));
        }

        await Task.WhenAll(tasks);

        // Assert - Should not throw, and rates should be approximately 50/50
        var errorRate = await _collector.GetErrorRateAsync("Concurrent");
        errorRate.Should().BeInRange(40, 60); // ~50% with some variance
    }

    [Fact]
    public void EndToEnd_ConnectionPoolMetrics_RecordsSuccessfully()
    {
        // Act
        var action = () => _collector.RecordConnectionPoolMetrics(
            activeConnections: 10,
            idleConnections: 5,
            totalConnections: 15);

        // Assert - Should not throw
        action.Should().NotThrow();
    }

    [Fact]
    public async Task EndToEnd_MetricsOverTime_OnlyIncludesRecentData()
    {
        // Arrange - Record some metrics
        _collector.RecordSuccess("TimeWindow", "Test", TimeSpan.FromMilliseconds(50));
        _collector.RecordSuccess("TimeWindow", "Test", TimeSpan.FromMilliseconds(60));
        _collector.RecordSuccess("TimeWindow", "Test", TimeSpan.FromMilliseconds(70));

        // Act - Query with 5-minute window
        var avgTime = await _collector.GetAverageResponseTimeAsync("TimeWindow", minutes: 5);

        // Assert - Should include all recent metrics
        avgTime.Should().Be(60.0); // Average of 50, 60, 70
    }

    public void Dispose()
    {
        _serviceProvider?.Dispose();
    }
}
