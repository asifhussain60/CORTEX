using Azure.Data.AppConfiguration;
using Azure.Identity;
using Microsoft.Extensions.Caching.Memory;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using PaymentProcessor.TransactionInvoices.Core.FeatureManagement;
using System.Security.Cryptography;
using System.Text;

namespace PaymentProcessor.TransactionInvoices.Infrastructure.FeatureManagement;

/// <summary>
/// Azure App Configuration implementation of feature flag service.
/// Supports real-time configuration updates with local caching.
/// </summary>
public class AzureAppConfigurationFeatureFlagService : IFeatureFlagService
{
    private readonly ILogger<AzureAppConfigurationFeatureFlagService> _logger;
    private readonly IMemoryCache _cache;
    private readonly IConfiguration _configuration;
    private readonly string _appConfigConnectionString;
    private readonly TimeSpan _cacheDuration;

    private const string FeatureFlagEnabledKey = "FeatureFlags:DataLayerRollout:Enabled";
    private const string TrafficPercentageKey = "FeatureFlags:DataLayerRollout:EFCorePercentage";
    private const string CacheKeyPrefix = "FeatureFlag_";

    public AzureAppConfigurationFeatureFlagService(
        IConfiguration configuration,
        ILogger<AzureAppConfigurationFeatureFlagService> logger,
        IMemoryCache cache)
    {
        _configuration = configuration;
        _logger = logger;
        _cache = cache;

        // Get App Configuration connection string
        _appConfigConnectionString = configuration["AzureAppConfiguration:ConnectionString"]
            ?? throw new InvalidOperationException("AzureAppConfiguration:ConnectionString is required");

        var cacheDurationSeconds = configuration.GetValue<int>("AzureAppConfiguration:CacheDurationSeconds", 30);
        _cacheDuration = TimeSpan.FromSeconds(cacheDurationSeconds);
    }

    public async Task<bool> IsFeatureFlagEnabledAsync(CancellationToken cancellationToken = default)
    {
        var cacheKey = $"{CacheKeyPrefix}{FeatureFlagEnabledKey}";

        if (_cache.TryGetValue(cacheKey, out bool cachedValue))
        {
            return cachedValue;
        }

        try
        {
            var client = new ConfigurationClient(_appConfigConnectionString);
            var setting = await client.GetConfigurationSettingAsync(FeatureFlagEnabledKey, cancellationToken: cancellationToken);
            
            var isEnabled = bool.TryParse(setting.Value.Value, out var result) && result;

            _cache.Set(cacheKey, isEnabled, _cacheDuration);

            return isEnabled;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to retrieve feature flag enabled status from Azure App Configuration");
            
            // Fallback to local configuration
            return _configuration.GetValue<bool>(FeatureFlagEnabledKey, false);
        }
    }

    public async Task<int> GetEFCoreTrafficPercentageAsync(CancellationToken cancellationToken = default)
    {
        var cacheKey = $"{CacheKeyPrefix}{TrafficPercentageKey}";

        if (_cache.TryGetValue(cacheKey, out int cachedPercentage))
        {
            return cachedPercentage;
        }

        try
        {
            var client = new ConfigurationClient(_appConfigConnectionString);
            var setting = await client.GetConfigurationSettingAsync(TrafficPercentageKey, cancellationToken: cancellationToken);
            
            var percentage = int.TryParse(setting.Value.Value, out var result) ? result : 0;
            percentage = Math.Clamp(percentage, 0, 100);

            _cache.Set(cacheKey, percentage, _cacheDuration);

            _logger.LogInformation("EF Core traffic percentage retrieved: {Percentage}%", percentage);

            return percentage;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to retrieve traffic percentage from Azure App Configuration");
            
            // Fallback to local configuration
            return _configuration.GetValue<int>(TrafficPercentageKey, 0);
        }
    }

    public async Task<bool> ShouldUseEFCoreAsync(string requestId, CancellationToken cancellationToken = default)
    {
        var isEnabled = await IsFeatureFlagEnabledAsync(cancellationToken);
        
        if (!isEnabled)
        {
            return false; // Feature flag disabled, use Mock
        }

        var percentage = await GetEFCoreTrafficPercentageAsync(cancellationToken);

        if (percentage == 0)
        {
            return false; // 0% rollout, use Mock
        }

        if (percentage == 100)
        {
            return true; // 100% rollout, use EF Core
        }

        // Deterministic routing: hash request ID to get consistent routing
        var hash = ComputeHash(requestId);
        var bucket = hash % 100; // 0-99

        return bucket < percentage;
    }

    public async Task SetEFCoreTrafficPercentageAsync(int percentage, CancellationToken cancellationToken = default)
    {
        if (percentage < 0 || percentage > 100)
        {
            throw new ArgumentOutOfRangeException(nameof(percentage), "Percentage must be between 0 and 100");
        }

        try
        {
            var client = new ConfigurationClient(_appConfigConnectionString);
            
            await client.SetConfigurationSettingAsync(
                new ConfigurationSetting(TrafficPercentageKey, percentage.ToString()),
                cancellationToken: cancellationToken);

            // Invalidate cache
            _cache.Remove($"{CacheKeyPrefix}{TrafficPercentageKey}");

            _logger.LogWarning("EF Core traffic percentage updated to {Percentage}% by admin", percentage);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to update traffic percentage in Azure App Configuration");
            throw;
        }
    }

    public async Task RollbackToMockAsync(string reason, CancellationToken cancellationToken = default)
    {
        _logger.LogCritical("EMERGENCY ROLLBACK: Setting EF Core traffic to 0%. Reason: {Reason}", reason);

        await SetEFCoreTrafficPercentageAsync(0, cancellationToken);

        // Also disable feature flag
        try
        {
            var client = new ConfigurationClient(_appConfigConnectionString);
            
            await client.SetConfigurationSettingAsync(
                new ConfigurationSetting(FeatureFlagEnabledKey, "false"),
                cancellationToken: cancellationToken);

            _cache.Remove($"{CacheKeyPrefix}{FeatureFlagEnabledKey}");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to disable feature flag during rollback");
        }
    }

    private static int ComputeHash(string input)
    {
        using var sha256 = SHA256.Create();
        var hashBytes = sha256.ComputeHash(Encoding.UTF8.GetBytes(input));
        
        // Take first 4 bytes and convert to int
        return Math.Abs(BitConverter.ToInt32(hashBytes, 0));
    }
}
