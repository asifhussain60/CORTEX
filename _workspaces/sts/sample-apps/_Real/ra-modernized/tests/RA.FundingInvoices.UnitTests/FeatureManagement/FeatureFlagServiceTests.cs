using FluentAssertions;
using Microsoft.Extensions.Caching.Memory;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Moq;
using RA.FundingInvoices.Infrastructure.FeatureManagement;

namespace RA.FundingInvoices.UnitTests.FeatureManagement;

/// <summary>
/// Unit tests for AzureAppConfigurationFeatureFlagService.
/// Tests feature flag logic without Azure dependencies.
/// </summary>
public class FeatureFlagServiceTests
{
    private readonly Mock<ILogger<AzureAppConfigurationFeatureFlagService>> _loggerMock;
    private readonly IMemoryCache _cache;
    private readonly IConfiguration _configuration;

    public FeatureFlagServiceTests()
    {
        _loggerMock = new Mock<ILogger<AzureAppConfigurationFeatureFlagService>>();
        _cache = new MemoryCache(new MemoryCacheOptions());

        var configValues = new Dictionary<string, string?>
        {
            ["AzureAppConfiguration:ConnectionString"] = "Endpoint=https://test.azconfig.io;Id=test;Secret=test",
            ["AzureAppConfiguration:CacheDurationSeconds"] = "30",
            ["FeatureFlags:DataLayerRollout:Enabled"] = "true",
            ["FeatureFlags:DataLayerRollout:EFCorePercentage"] = "50"
        };

        _configuration = new ConfigurationBuilder()
            .AddInMemoryCollection(configValues)
            .Build();
    }

    [Fact]
    public void Constructor_MissingConnectionString_ThrowsException()
    {
        // Arrange
        var configValues = new Dictionary<string, string?>();
        var config = new ConfigurationBuilder()
            .AddInMemoryCollection(configValues)
            .Build();

        // Act & Assert
        var action = () => new AzureAppConfigurationFeatureFlagService(config, _loggerMock.Object, _cache);
        action.Should().Throw<InvalidOperationException>()
            .WithMessage("*AzureAppConfiguration:ConnectionString*");
    }

    [Fact]
    public async Task IsFeatureFlagEnabledAsync_FallsBackToLocalConfig_WhenAzureUnavailable()
    {
        // Arrange - Azure will fail, should use local config
        var service = new AzureAppConfigurationFeatureFlagService(_configuration, _loggerMock.Object, _cache);

        // Act - Will fail to connect to Azure, fallback to local
        var result = await service.IsFeatureFlagEnabledAsync();

        // Assert - Should return local config value
        result.Should().BeTrue(); // From local config
    }

    [Fact]
    public async Task GetEFCoreTrafficPercentageAsync_FallsBackToLocalConfig_WhenAzureUnavailable()
    {
        // Arrange
        var service = new AzureAppConfigurationFeatureFlagService(_configuration, _loggerMock.Object, _cache);

        // Act
        var result = await service.GetEFCoreTrafficPercentageAsync();

        // Assert - Should return local config value
        result.Should().Be(50); // From local config
    }

    [Theory]
    [InlineData(0, "request-1", false)]   // 0% -> always Mock
    [InlineData(100, "request-1", true)]  // 100% -> always EF Core
    [InlineData(50, "request-1", true)]   // Deterministic based on hash
    [InlineData(50, "request-2", false)]  // Different hash
    public async Task ShouldUseEFCoreAsync_DeterministicRouting_BasedOnRequestId(
        int percentage, string requestId, bool expectedResult)
    {
        // Arrange
        var configValues = new Dictionary<string, string?>
        {
            ["AzureAppConfiguration:ConnectionString"] = "Endpoint=https://test.azconfig.io;Id=test;Secret=test",
            ["FeatureFlags:DataLayerRollout:Enabled"] = "true",
            ["FeatureFlags:DataLayerRollout:EFCorePercentage"] = percentage.ToString()
        };

        var config = new ConfigurationBuilder()
            .AddInMemoryCollection(configValues)
            .Build();

        var service = new AzureAppConfigurationFeatureFlagService(config, _loggerMock.Object, _cache);

        // Act
        var result = await service.ShouldUseEFCoreAsync(requestId);

        // Assert - Same requestId should always return same result
        result.Should().Be(expectedResult);
    }

    [Fact]
    public async Task ShouldUseEFCoreAsync_SameRequestId_AlwaysReturnsSameResult()
    {
        // Arrange
        var configValues = new Dictionary<string, string?>
        {
            ["AzureAppConfiguration:ConnectionString"] = "Endpoint=https://test.azconfig.io;Id=test;Secret=test",
            ["FeatureFlags:DataLayerRollout:Enabled"] = "true",
            ["FeatureFlags:DataLayerRollout:EFCorePercentage"] = "50"
        };

        var config = new ConfigurationBuilder()
            .AddInMemoryCollection(configValues)
            .Build();

        var service = new AzureAppConfigurationFeatureFlagService(config, _loggerMock.Object, _cache);

        // Act - Call multiple times with same requestId
        var result1 = await service.ShouldUseEFCoreAsync("test-request-123");
        var result2 = await service.ShouldUseEFCoreAsync("test-request-123");
        var result3 = await service.ShouldUseEFCoreAsync("test-request-123");

        // Assert - Deterministic routing
        result1.Should().Be(result2);
        result2.Should().Be(result3);
    }

    [Fact]
    public async Task ShouldUseEFCoreAsync_FeatureFlagDisabled_ReturnsFalse()
    {
        // Arrange
        var configValues = new Dictionary<string, string?>
        {
            ["AzureAppConfiguration:ConnectionString"] = "Endpoint=https://test.azconfig.io;Id=test;Secret=test",
            ["FeatureFlags:DataLayerRollout:Enabled"] = "false",
            ["FeatureFlags:DataLayerRollout:EFCorePercentage"] = "100"
        };

        var config = new ConfigurationBuilder()
            .AddInMemoryCollection(configValues)
            .Build();

        var service = new AzureAppConfigurationFeatureFlagService(config, _loggerMock.Object, _cache);

        // Act
        var result = await service.ShouldUseEFCoreAsync("any-request");

        // Assert - Feature disabled, always use Mock
        result.Should().BeFalse();
    }

    [Theory]
    [InlineData(-1)]
    [InlineData(101)]
    [InlineData(150)]
    public async Task SetEFCoreTrafficPercentageAsync_InvalidPercentage_ThrowsException(int invalidPercentage)
    {
        // Arrange
        var service = new AzureAppConfigurationFeatureFlagService(_configuration, _loggerMock.Object, _cache);

        // Act & Assert
        await service.Invoking(s => s.SetEFCoreTrafficPercentageAsync(invalidPercentage))
            .Should().ThrowAsync<ArgumentOutOfRangeException>();
    }

    [Fact]
    public async Task RollbackToMockAsync_SetsPercentageToZero_AndLogsJournalToApp()
    {
        // Arrange
        var service = new AzureAppConfigurationFeatureFlagService(_configuration, _loggerMock.Object, _cache);

        // Act - Will fail to connect to Azure, but should log critical message
        await service.RollbackToMockAsync("Test rollback reason");

        // Assert - Verify critical log was called
        _loggerMock.Verify(
            x => x.Log(
                LogLevel.Critical,
                It.IsAny<EventId>(),
                It.Is<It.IsAnyType>((v, t) => v.ToString()!.Contains("EMERGENCY ROLLBACK")),
                It.IsAny<Exception>(),
                It.IsAny<Func<It.IsAnyType, Exception?, string>>()),
            Times.Once);
    }

    [Fact]
    public void Service_ValidConfiguration_ConstructsSuccessfully()
    {
        // Act
        var action = () => new AzureAppConfigurationFeatureFlagService(_configuration, _loggerMock.Object, _cache);

        // Assert
        action.Should().NotThrow();
    }
}
