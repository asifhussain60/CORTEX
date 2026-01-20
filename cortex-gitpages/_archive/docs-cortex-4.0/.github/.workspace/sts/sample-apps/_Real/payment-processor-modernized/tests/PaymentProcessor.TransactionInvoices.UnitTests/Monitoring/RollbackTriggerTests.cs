using FluentAssertions;
using Microsoft.Extensions.Caching.Memory;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Moq;
using PaymentProcessor.TransactionInvoices.Core.FeatureManagement;
using PaymentProcessor.TransactionInvoices.Core.Monitoring;
using PaymentProcessor.TransactionInvoices.Infrastructure.Monitoring;

namespace PaymentProcessor.TransactionInvoices.UnitTests.Monitoring;

/// <summary>
/// Unit tests for AutomatedRollbackService.
/// Tests rollback trigger logic and circuit breaker pattern.
/// </summary>
public class RollbackTriggerTests
{
    private readonly Mock<IMetricsCollector> _metricsCollectorMock;
    private readonly Mock<IFeatureFlagService> _featureFlagServiceMock;
    private readonly Mock<ILogger<AutomatedRollbackService>> _loggerMock;
    private readonly IConfiguration _configuration;

    public RollbackTriggerTests()
    {
        _metricsCollectorMock = new Mock<IMetricsCollector>();
        _featureFlagServiceMock = new Mock<IFeatureFlagService>();
        _loggerMock = new Mock<ILogger<AutomatedRollbackService>>();

        var configValues = new Dictionary<string, string?>
        {
            ["RollbackThresholds:ErrorRatePercent"] = "0.1",
            ["RollbackThresholds:LatencyMs"] = "200",
            ["RollbackThresholds:SuccessRatePercent"] = "99.9",
            ["RollbackThresholds:EvaluationWindowMinutes"] = "5",
            ["CircuitBreaker:HalfOpenRetrySeconds"] = "60"
        };

        _configuration = new ConfigurationBuilder()
            .AddInMemoryCollection(configValues)
            .Build();
    }

    [Fact]
    public async Task ShouldRollbackAsync_ErrorRateExceedsThreshold_TriggersRollback()
    {
        // Arrange
        _metricsCollectorMock
            .Setup(m => m.GetErrorRateAsync("EFCore", It.IsAny<CancellationToken>()))
            .ReturnsAsync(0.5); // 0.5% error rate (exceeds 0.1% threshold)

        _metricsCollectorMock
            .Setup(m => m.GetAverageResponseTimeAsync("EFCore", It.IsAny<int>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(100); // Latency OK

        _metricsCollectorMock
            .Setup(m => m.GetSuccessRateAsync("EFCore", It.IsAny<int>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(99.95); // Success rate OK

        var service = new AutomatedRollbackService(
            _metricsCollectorMock.Object,
            _featureFlagServiceMock.Object,
            _loggerMock.Object,
            _configuration);

        // Act
        var decision = await service.ShouldRollbackAsync("EFCore");

        // Assert
        decision.ShouldRollback.Should().BeTrue();
        decision.Reason.Should().Contain("Error rate");
        decision.Metrics["ErrorRate"].Should().Be(0.5);

        // Verify feature flag service was called to trigger rollback
        _featureFlagServiceMock.Verify(
            f => f.RollbackToMockAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()),
            Times.Once);
    }

    [Fact]
    public async Task ShouldRollbackAsync_LatencyExceedsThreshold_TriggersRollback()
    {
        // Arrange
        _metricsCollectorMock
            .Setup(m => m.GetErrorRateAsync("EFCore", It.IsAny<CancellationToken>()))
            .ReturnsAsync(0.05); // Error rate OK

        _metricsCollectorMock
            .Setup(m => m.GetAverageResponseTimeAsync("EFCore", It.IsAny<int>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(250); // 250ms exceeds 200ms threshold

        _metricsCollectorMock
            .Setup(m => m.GetSuccessRateAsync("EFCore", It.IsAny<int>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(99.95); // Success rate OK

        var service = new AutomatedRollbackService(
            _metricsCollectorMock.Object,
            _featureFlagServiceMock.Object,
            _loggerMock.Object,
            _configuration);

        // Act
        var decision = await service.ShouldRollbackAsync("EFCore");

        // Assert
        decision.ShouldRollback.Should().BeTrue();
        decision.Reason.Should().Contain("latency");
        decision.Metrics["AvgLatencyMs"].Should().Be(250);
    }

    [Fact]
    public async Task ShouldRollbackAsync_SuccessRateBelowThreshold_TriggersRollback()
    {
        // Arrange
        _metricsCollectorMock
            .Setup(m => m.GetErrorRateAsync("EFCore", It.IsAny<CancellationToken>()))
            .ReturnsAsync(0.05); // Error rate OK

        _metricsCollectorMock
            .Setup(m => m.GetAverageResponseTimeAsync("EFCore", It.IsAny<int>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(100); // Latency OK

        _metricsCollectorMock
            .Setup(m => m.GetSuccessRateAsync("EFCore", It.IsAny<int>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(99.5); // Below 99.9% threshold

        var service = new AutomatedRollbackService(
            _metricsCollectorMock.Object,
            _featureFlagServiceMock.Object,
            _loggerMock.Object,
            _configuration);

        // Act
        var decision = await service.ShouldRollbackAsync("EFCore");

        // Assert
        decision.ShouldRollback.Should().BeTrue();
        decision.Reason.Should().Contain("Success rate");
        decision.Metrics["SuccessRate"].Should().Be(99.5);
    }

    [Fact]
    public async Task ShouldRollbackAsync_AllMetricsHealthy_DoesNotTriggerRollback()
    {
        // Arrange
        _metricsCollectorMock
            .Setup(m => m.GetErrorRateAsync("EFCore", It.IsAny<CancellationToken>()))
            .ReturnsAsync(0.05); // Below 0.1%

        _metricsCollectorMock
            .Setup(m => m.GetAverageResponseTimeAsync("EFCore", It.IsAny<int>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(150); // Below 200ms

        _metricsCollectorMock
            .Setup(m => m.GetSuccessRateAsync("EFCore", It.IsAny<int>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(99.95); // Above 99.9%

        var service = new AutomatedRollbackService(
            _metricsCollectorMock.Object,
            _featureFlagServiceMock.Object,
            _loggerMock.Object,
            _configuration);

        // Act
        var decision = await service.ShouldRollbackAsync("EFCore");

        // Assert
        decision.ShouldRollback.Should().BeFalse();
        decision.Reason.Should().BeNull();

        // Verify rollback was NOT triggered
        _featureFlagServiceMock.Verify(
            f => f.RollbackToMockAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()),
            Times.Never);
    }

    [Fact]
    public async Task GetCircuitBreakerStateAsync_InitialState_IsClosed()
    {
        // Arrange
        var service = new AutomatedRollbackService(
            _metricsCollectorMock.Object,
            _featureFlagServiceMock.Object,
            _loggerMock.Object,
            _configuration);

        // Act
        var state = await service.GetCircuitBreakerStateAsync();

        // Assert
        state.Should().Be(CircuitBreakerState.Closed);
    }

    [Fact]
    public async Task OpenCircuitBreakerAsync_OpensCircuit_AndTriggersRollback()
    {
        // Arrange
        var service = new AutomatedRollbackService(
            _metricsCollectorMock.Object,
            _featureFlagServiceMock.Object,
            _loggerMock.Object,
            _configuration);

        // Act
        await service.OpenCircuitBreakerAsync("Manual circuit break for testing");

        // Assert
        var state = await service.GetCircuitBreakerStateAsync();
        state.Should().Be(CircuitBreakerState.Open);

        // Verify rollback was triggered
        _featureFlagServiceMock.Verify(
            f => f.RollbackToMockAsync("Manual circuit break for testing", It.IsAny<CancellationToken>()),
            Times.Once);

        // Verify critical log
        _loggerMock.Verify(
            x => x.Log(
                LogLevel.Critical,
                It.IsAny<EventId>(),
                It.Is<It.IsAnyType>((v, t) => v.ToString()!.Contains("CIRCUIT BREAKER OPENED")),
                It.IsAny<Exception>(),
                It.IsAny<Func<It.IsAnyType, Exception?, string>>()),
            Times.Once);
    }

    [Fact]
    public async Task OpenCircuitBreakerAsync_AlreadyOpen_DoesNotTriggerAgain()
    {
        // Arrange
        var service = new AutomatedRollbackService(
            _metricsCollectorMock.Object,
            _featureFlagServiceMock.Object,
            _loggerMock.Object,
            _configuration);

        // Act - Open circuit twice
        await service.OpenCircuitBreakerAsync("First open");
        await service.OpenCircuitBreakerAsync("Second open");

        // Assert - Rollback only called once
        _featureFlagServiceMock.Verify(
            f => f.RollbackToMockAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()),
            Times.Once); // Only first time
    }

    [Fact]
    public async Task ResetCircuitBreakerAsync_ClosesCircuit()
    {
        // Arrange
        var service = new AutomatedRollbackService(
            _metricsCollectorMock.Object,
            _featureFlagServiceMock.Object,
            _loggerMock.Object,
            _configuration);

        await service.OpenCircuitBreakerAsync("Test open");

        // Act
        await service.ResetCircuitBreakerAsync();

        // Assert
        var state = await service.GetCircuitBreakerStateAsync();
        state.Should().Be(CircuitBreakerState.Closed);

        // Verify info log
        _loggerMock.Verify(
            x => x.Log(
                LogLevel.Information,
                It.IsAny<EventId>(),
                It.Is<It.IsAnyType>((v, t) => v.ToString()!.Contains("RESET")),
                It.IsAny<Exception>(),
                It.IsAny<Func<It.IsAnyType, Exception?, string>>()),
            Times.Once);
    }

    [Fact]
    public async Task ShouldRollbackAsync_CircuitOpen_ReturnsRollbackDecision()
    {
        // Arrange
        var service = new AutomatedRollbackService(
            _metricsCollectorMock.Object,
            _featureFlagServiceMock.Object,
            _loggerMock.Object,
            _configuration);

        await service.OpenCircuitBreakerAsync("Manual open");

        // Act
        var decision = await service.ShouldRollbackAsync("EFCore");

        // Assert
        decision.ShouldRollback.Should().BeTrue();
        decision.Reason.Should().Contain("Circuit breaker is OPEN");
    }

    [Fact]
    public async Task ShouldRollbackAsync_MetricsException_TriggersRollbackForSafety()
    {
        // Arrange
        _metricsCollectorMock
            .Setup(m => m.GetErrorRateAsync("EFCore", It.IsAny<CancellationToken>()))
            .ThrowsAsync(new InvalidOperationException("Metrics failed"));

        var service = new AutomatedRollbackService(
            _metricsCollectorMock.Object,
            _featureFlagServiceMock.Object,
            _loggerMock.Object,
            _configuration);

        // Act
        var decision = await service.ShouldRollbackAsync("EFCore");

        // Assert - On error, err on side of caution
        decision.ShouldRollback.Should().BeTrue();
        decision.Reason.Should().Contain("Failed to evaluate metrics");
    }

    [Fact]
    public void Constructor_LoadsThresholdsFromConfiguration()
    {
        // Act
        var service = new AutomatedRollbackService(
            _metricsCollectorMock.Object,
            _featureFlagServiceMock.Object,
            _loggerMock.Object,
            _configuration);

        // Assert - Constructor should not throw
        service.Should().NotBeNull();
    }
}
