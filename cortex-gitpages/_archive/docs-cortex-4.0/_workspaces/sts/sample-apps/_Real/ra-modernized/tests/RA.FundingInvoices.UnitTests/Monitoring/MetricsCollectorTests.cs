using FluentAssertions;
using Microsoft.ApplicationInsights;
using Microsoft.ApplicationInsights.Extensibility;
using Microsoft.Extensions.Caching.Memory;
using Microsoft.Extensions.Logging;
using Moq;
using RA.FundingInvoices.Infrastructure.Monitoring;

namespace RA.FundingInvoices.UnitTests.Monitoring;

/// <summary>
/// Unit tests for ApplicationInsightsMetricsCollector.
/// Tests metrics collection logic without Application Insights dependency.
/// </summary>
public class MetricsCollectorTests
{
    private readonly TelemetryClient _telemetryClient;
    private readonly Mock<ILogger<ApplicationInsightsMetricsCollector>> _loggerMock;
    private readonly IMemoryCache _cache;

    public MetricsCollectorTests()
    {
        // Create TelemetryClient with in-memory configuration
        var config = new TelemetryConfiguration
        {
            ConnectionString = "InstrumentationKey=00000000-0000-0000-0000-000000000000"
        };
        _telemetryClient = new TelemetryClient(config);
        
        _loggerMock = new Mock<ILogger<ApplicationInsightsMetricsCollector>>();
        _cache = new MemoryCache(new MemoryCacheOptions());
    }

    [Fact]
    public void RecordSuccess_TracksEventAndMetric()
    {
        // Arrange
        var collector = new ApplicationInsightsMetricsCollector(_telemetryClient, _loggerMock.Object, _cache);

        // Act
        collector.RecordSuccess("Mock", "GetInvoice", TimeSpan.FromMilliseconds(50));

        // Assert - Verify debug log was called
        _loggerMock.Verify(
            x => x.Log(
                LogLevel.Debug,
                It.IsAny<EventId>(),
                It.Is<It.IsAnyType>((v, t) => v.ToString()!.Contains("completed successfully")),
                It.IsAny<Exception>(),
                It.IsAny<Func<It.IsAnyType, Exception?, string>>()),
            Times.Once);
    }

    [Fact]
    public void RecordFailure_TracksExceptionAndErrorMetric()
    {
        // Arrange
        var collector = new ApplicationInsightsMetricsCollector(_telemetryClient, _loggerMock.Object, _cache);
        var exception = new InvalidOperationException("Test error");

        // Act
        collector.RecordFailure("EFCore", "GetInvoice", exception, TimeSpan.FromMilliseconds(100));

        // Assert - Verify error log was called
        _loggerMock.Verify(
            x => x.Log(
                LogLevel.Error,
                It.IsAny<EventId>(),
                It.Is<It.IsAnyType>((v, t) => v.ToString()!.Contains("failed")),
                exception,
                It.IsAny<Func<It.IsAnyType, Exception?, string>>()),
            Times.Once);
    }

    [Fact]
    public void RecordConnectionPoolMetrics_TracksAllPoolMetrics()
    {
        // Arrange
        var collector = new ApplicationInsightsMetricsCollector(_telemetryClient, _loggerMock.Object, _cache);

        // Act
        collector.RecordConnectionPoolMetrics(activeConnections: 5, idleConnections: 3, totalConnections: 8);

        // Assert - Verify debug log was called with utilization
        _loggerMock.Verify(
            x => x.Log(
                LogLevel.Debug,
                It.IsAny<EventId>(),
                It.Is<It.IsAnyType>((v, t) => v.ToString()!.Contains("Connection pool")),
                It.IsAny<Exception>(),
                It.IsAny<Func<It.IsAnyType, Exception?, string>>()),
            Times.Once);
    }

    [Fact]
    public async Task GetErrorRateAsync_NoRecentMetrics_ReturnsZero()
    {
        // Arrange
        var collector = new ApplicationInsightsMetricsCollector(_telemetryClient, _loggerMock.Object, _cache);

        // Act
        var errorRate = await collector.GetErrorRateAsync("Mock");

        // Assert
        errorRate.Should().Be(0.0);
    }

    [Fact]
    public async Task GetErrorRateAsync_CalculatesCorrectPercentage()
    {
        // Arrange
        var collector = new ApplicationInsightsMetricsCollector(_telemetryClient, _loggerMock.Object, _cache);

        // Record 7 successes and 3 failures (30% error rate)
        for (int i = 0; i < 7; i++)
        {
            collector.RecordSuccess("Mock", "GetInvoice", TimeSpan.FromMilliseconds(50));
        }

        for (int i = 0; i < 3; i++)
        {
            collector.RecordFailure("Mock", "GetInvoice", new Exception("Test"), TimeSpan.FromMilliseconds(100));
        }

        // Act
        var errorRate = await collector.GetErrorRateAsync("Mock");

        // Assert - 3 errors out of 10 total = 30%
        errorRate.Should().Be(30.0);
    }

    [Fact]
    public async Task GetAverageResponseTimeAsync_NoRecentMetrics_ReturnsZero()
    {
        // Arrange
        var collector = new ApplicationInsightsMetricsCollector(_telemetryClient, _loggerMock.Object, _cache);

        // Act
        var avgTime = await collector.GetAverageResponseTimeAsync("Mock", minutes: 5);

        // Assert
        avgTime.Should().Be(0.0);
    }

    [Fact]
    public async Task GetAverageResponseTimeAsync_CalculatesCorrectAverage()
    {
        // Arrange
        var collector = new ApplicationInsightsMetricsCollector(_telemetryClient, _loggerMock.Object, _cache);

        // Record metrics with different durations
        collector.RecordSuccess("Mock", "GetInvoice", TimeSpan.FromMilliseconds(50));
        collector.RecordSuccess("Mock", "GetInvoice", TimeSpan.FromMilliseconds(100));
        collector.RecordSuccess("Mock", "GetInvoice", TimeSpan.FromMilliseconds(150));

        // Act
        var avgTime = await collector.GetAverageResponseTimeAsync("Mock", minutes: 5);

        // Assert - Average of 50, 100, 150 = 100ms
        avgTime.Should().Be(100.0);
    }

    [Fact]
    public async Task GetSuccessRateAsync_NoRecentMetrics_Returns100Percent()
    {
        // Arrange
        var collector = new ApplicationInsightsMetricsCollector(_telemetryClient, _loggerMock.Object, _cache);

        // Act
        var successRate = await collector.GetSuccessRateAsync("Mock", minutes: 5);

        // Assert - No data = assume success
        successRate.Should().Be(100.0);
    }

    [Fact]
    public async Task GetSuccessRateAsync_CalculatesCorrectPercentage()
    {
        // Arrange
        var collector = new ApplicationInsightsMetricsCollector(_telemetryClient, _loggerMock.Object, _cache);

        // Record 9 successes and 1 failure (90% success rate)
        for (int i = 0; i < 9; i++)
        {
            collector.RecordSuccess("EFCore", "GetInvoice", TimeSpan.FromMilliseconds(50));
        }

        collector.RecordFailure("EFCore", "GetInvoice", new Exception("Test"), TimeSpan.FromMilliseconds(100));

        // Act
        var successRate = await collector.GetSuccessRateAsync("EFCore", minutes: 5);

        // Assert - 9 success out of 10 total = 90%
        successRate.Should().Be(90.0);
    }
}
