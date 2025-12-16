using FluentAssertions;
using Microsoft.Extensions.Caching.Memory;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using PaymentProcessor.TransactionInvoices.Core.FeatureManagement;
using PaymentProcessor.TransactionInvoices.Infrastructure.FeatureManagement;

namespace PaymentProcessor.TransactionInvoices.IntegrationTests.FeatureManagement;

/// <summary>
/// Integration tests for feature flag infrastructure.
/// Tests end-to-end feature flag scenarios with fallback mechanisms.
/// </summary>
public class FeatureFlagIntegrationTests : IDisposable
{
    private readonly ServiceProvider _serviceProvider;
    private readonly IFeatureFlagService _service;

    public FeatureFlagIntegrationTests()
    {
        var services = new ServiceCollection();

        // Build configuration
        var configValues = new Dictionary<string, string?>
        {
            ["AzureAppConfiguration:ConnectionString"] = "Endpoint=https://test-integration.azconfig.io;Id=test;Secret=fake",
            ["AzureAppConfiguration:CacheDurationSeconds"] = "5",
            ["FeatureFlags:DataLayerRollout:Enabled"] = "true",
            ["FeatureFlags:DataLayerRollout:EFCorePercentage"] = "75"
        };

        var configuration = new ConfigurationBuilder()
            .AddInMemoryCollection(configValues)
            .Build();

        // Register services
        services.AddSingleton<IConfiguration>(configuration);
        services.AddLogging(builder => builder.AddConsole().SetMinimumLevel(LogLevel.Debug));
        services.AddMemoryCache();
        services.AddSingleton<IFeatureFlagService, AzureAppConfigurationFeatureFlagService>();

        _serviceProvider = services.BuildServiceProvider();
        _service = _serviceProvider.GetRequiredService<IFeatureFlagService>();
    }

    [Fact]
    public async Task EndToEnd_FeatureFlagEvaluation_FallsBackToLocalConfig()
    {
        // Act - Azure will fail, fallback to local config
        var isEnabled = await _service.IsFeatureFlagEnabledAsync();
        var percentage = await _service.GetEFCoreTrafficPercentageAsync();

        // Assert - Should use local configuration
        isEnabled.Should().BeTrue();
        percentage.Should().Be(75);
    }

    [Fact]
    public async Task EndToEnd_DeterministicRouting_ConsistentAcrossMultipleCalls()
    {
        // Arrange
        var requestId = Guid.NewGuid().ToString();

        // Act - Call 10 times
        var results = new List<bool>();
        for (int i = 0; i < 10; i++)
        {
            var result = await _service.ShouldUseEFCoreAsync(requestId);
            results.Add(result);
        }

        // Assert - All results should be identical
        results.Should().OnlyHaveUniqueItems().And.HaveCount(1);
    }

    [Fact]
    public async Task EndToEnd_TrafficDistribution_ApproximatelyMatchesPercentage()
    {
        // Arrange - Set to 50% traffic
        var configValues = new Dictionary<string, string?>
        {
            ["AzureAppConfiguration:ConnectionString"] = "Endpoint=https://test.azconfig.io;Id=test;Secret=fake",
            ["FeatureFlags:DataLayerRollout:Enabled"] = "true",
            ["FeatureFlags:DataLayerRollout:EFCorePercentage"] = "50"
        };

        var config = new ConfigurationBuilder()
            .AddInMemoryCollection(configValues)
            .Build();

        var services = new ServiceCollection();
        services.AddSingleton<IConfiguration>(config);
        services.AddLogging();
        services.AddMemoryCache();
        services.AddSingleton<IFeatureFlagService, AzureAppConfigurationFeatureFlagService>();

        var provider = services.BuildServiceProvider();
        var service = provider.GetRequiredService<IFeatureFlagService>();

        // Act - Simulate 1000 unique requests
        var efCoreCount = 0;
        for (int i = 0; i < 1000; i++)
        {
            var requestId = $"request-{i}";
            var useEfCore = await service.ShouldUseEFCoreAsync(requestId);
            if (useEfCore) efCoreCount++;
        }

        // Assert - Should be approximately 50% (allow 5% variance)
        var actualPercentage = (efCoreCount / 1000.0) * 100;
        actualPercentage.Should().BeInRange(45, 55);
    }

    [Fact]
    public async Task EndToEnd_EmergencyRollback_UpdatesConfigurationAndClearsCache()
    {
        // Act - Trigger emergency rollback
        await _service.RollbackToMockAsync("Integration test rollback");

        // Wait briefly for potential async updates
        await Task.Delay(100);

        // Assert - Subsequent calls should route to Mock
        var result = await _service.ShouldUseEFCoreAsync("any-request");
        result.Should().BeFalse(); // After rollback, should use Mock
    }

    [Fact]
    public async Task EndToEnd_ConcurrentRequests_AllSucceed()
    {
        // Arrange
        var tasks = new List<Task<bool>>();

        // Act - Simulate 50 concurrent requests
        for (int i = 0; i < 50; i++)
        {
            var requestId = $"concurrent-{i}";
            tasks.Add(_service.ShouldUseEFCoreAsync(requestId));
        }

        var results = await Task.WhenAll(tasks);

        // Assert - All should complete successfully
        results.Should().HaveCount(50);
        results.Should().NotContainNulls();
    }

    public void Dispose()
    {
        _serviceProvider?.Dispose();
    }
}
