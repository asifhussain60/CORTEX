using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using RA.FundingInvoices.Core.FeatureManagement;
using RA.FundingInvoices.Core.Interfaces;

namespace RA.FundingInvoices.Infrastructure.FeatureManagement;

/// <summary>
/// Routes data layer requests between Mock and EF Core implementations.
/// Supports gradual rollout with deterministic routing per request.
/// </summary>
public class DataLayerRouter
{
    private readonly IFeatureFlagService _featureFlagService;
    private readonly IServiceProvider _serviceProvider;
    private readonly ILogger<DataLayerRouter> _logger;

    public DataLayerRouter(
        IFeatureFlagService featureFlagService,
        IServiceProvider serviceProvider,
        ILogger<DataLayerRouter> logger)
    {
        _featureFlagService = featureFlagService;
        _serviceProvider = serviceProvider;
        _logger = logger;
    }

    /// <summary>
    /// Gets the appropriate repository implementation based on feature flag.
    /// </summary>
    public async Task<T> GetRepositoryAsync<T>(string requestId, CancellationToken cancellationToken = default) where T : class
    {
        var useEFCore = await _featureFlagService.ShouldUseEFCoreAsync(requestId, cancellationToken);

        var repositoryType = typeof(T).Name;

        if (useEFCore)
        {
            _logger.LogDebug("Routing {RepositoryType} to EF Core implementation for request {RequestId}", 
                repositoryType, requestId);
            
            return _serviceProvider.GetRequiredKeyedService<T>("EFCore");
        }
        else
        {
            _logger.LogDebug("Routing {RepositoryType} to Mock implementation for request {RequestId}", 
                repositoryType, requestId);
            
            return _serviceProvider.GetRequiredKeyedService<T>("Mock");
        }
    }

    /// <summary>
    /// Gets the appropriate Unit of Work implementation based on feature flag.
    /// </summary>
    public async Task<IUnitOfWork> GetUnitOfWorkAsync(string requestId, CancellationToken cancellationToken = default)
    {
        var useEFCore = await _featureFlagService.ShouldUseEFCoreAsync(requestId, cancellationToken);

        if (useEFCore)
        {
            _logger.LogDebug("Routing UnitOfWork to EF Core implementation for request {RequestId}", requestId);
            return _serviceProvider.GetRequiredKeyedService<IUnitOfWork>("EFCore");
        }
        else
        {
            _logger.LogDebug("Routing UnitOfWork to Mock implementation for request {RequestId}", requestId);
            return _serviceProvider.GetRequiredKeyedService<IUnitOfWork>("Mock");
        }
    }

    /// <summary>
    /// Determines if current request should use EF Core (for middleware).
    /// </summary>
    public async Task<bool> ShouldUseEFCoreAsync(string requestId, CancellationToken cancellationToken = default)
    {
        return await _featureFlagService.ShouldUseEFCoreAsync(requestId, cancellationToken);
    }
}
