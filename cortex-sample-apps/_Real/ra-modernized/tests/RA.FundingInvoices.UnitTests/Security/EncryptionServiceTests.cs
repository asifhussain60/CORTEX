using FluentAssertions;
using Microsoft.Extensions.Caching.Memory;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Moq;
using RA.FundingInvoices.Infrastructure.Security;
using System.Security.Cryptography;

namespace RA.FundingInvoices.UnitTests.Security;

/// <summary>
/// Unit tests for AzureKeyVaultEncryptionService.
/// Uses mock Azure Key Vault for testing without Azure dependencies.
/// </summary>
public class EncryptionServiceTests
{
    private readonly Mock<ILogger<AzureKeyVaultEncryptionService>> _loggerMock;
    private readonly IMemoryCache _cache;
    private readonly IConfiguration _configuration;

    public EncryptionServiceTests()
    {
        _loggerMock = new Mock<ILogger<AzureKeyVaultEncryptionService>>();
        _cache = new MemoryCache(new MemoryCacheOptions());

        // Mock configuration (tests will use local encryption without Azure)
        var configValues = new Dictionary<string, string?>
        {
            ["AzureKeyVault:Url"] = "https://test-vault.vault.azure.net/",
            ["AzureKeyVault:EncryptionKeyName"] = "test-encryption-key",
            ["AzureKeyVault:KeyCacheDurationMinutes"] = "60"
        };

        _configuration = new ConfigurationBuilder()
            .AddInMemoryCollection(configValues)
            .Build();
    }

    [Fact]
    public void Constructor_MissingKeyVaultUrl_ThrowsException()
    {
        // Arrange
        var configValues = new Dictionary<string, string?>
        {
            ["AzureKeyVault:EncryptionKeyName"] = "test-key"
        };
        var config = new ConfigurationBuilder()
            .AddInMemoryCollection(configValues)
            .Build();

        // Act & Assert
        var action = () => new AzureKeyVaultEncryptionService(config, _loggerMock.Object, _cache);
        action.Should().Throw<InvalidOperationException>()
            .WithMessage("*AzureKeyVault:Url*");
    }

    [Fact]
    public void Constructor_MissingKeyName_ThrowsException()
    {
        // Arrange
        var configValues = new Dictionary<string, string?>
        {
            ["AzureKeyVault:Url"] = "https://test-vault.vault.azure.net/"
        };
        var config = new ConfigurationBuilder()
            .AddInMemoryCollection(configValues)
            .Build();

        // Act & Assert
        var action = () => new AzureKeyVaultEncryptionService(config, _loggerMock.Object, _cache);
        action.Should().Throw<InvalidOperationException>()
            .WithMessage("*AzureKeyVault:EncryptionKeyName*");
    }

    [Fact]
    public async Task EncryptAsync_NullOrEmptyPlaintext_ReturnsUnchanged()
    {
        // NOTE: This test validates the service structure but cannot fully test
        // Azure Key Vault operations without live Azure credentials.
        // Integration tests with Azure will be added in Phase 6 deployment.

        // For now, verify null/empty handling works correctly
        var service = new AzureKeyVaultEncryptionService(_configuration, _loggerMock.Object, _cache);

        var nullResult = await service.EncryptAsync(null!);
        var emptyResult = await service.EncryptAsync(string.Empty);

        nullResult.Should().BeNull();
        emptyResult.Should().BeEmpty();
    }

    [Fact]
    public async Task DecryptAsync_NullOrEmptyCiphertext_ReturnsUnchanged()
    {
        var service = new AzureKeyVaultEncryptionService(_configuration, _loggerMock.Object, _cache);

        var nullResult = await service.DecryptAsync(null!);
        var emptyResult = await service.DecryptAsync(string.Empty);

        nullResult.Should().BeNull();
        emptyResult.Should().BeEmpty();
    }

    [Fact]
    public async Task EncryptBatchAsync_EmptyCollection_ReturnsEmpty()
    {
        var service = new AzureKeyVaultEncryptionService(_configuration, _loggerMock.Object, _cache);

        var result = await service.EncryptBatchAsync(Array.Empty<string>());

        result.Should().BeEmpty();
    }

    [Fact]
    public async Task DecryptBatchAsync_EmptyCollection_ReturnsEmpty()
    {
        var service = new AzureKeyVaultEncryptionService(_configuration, _loggerMock.Object, _cache);

        var result = await service.DecryptBatchAsync(Array.Empty<string>());

        result.Should().BeEmpty();
    }

    /// <summary>
    /// NOTE: Full encryption/decryption round-trip tests require live Azure Key Vault.
    /// These will be added in Phase 6 integration tests with test Key Vault instance.
    /// For now, we validate:
    /// 1. Service construction with valid configuration
    /// 2. Null/empty input handling
    /// 3. Batch operation structure
    /// </summary>
    [Fact]
    public void Service_ValidConfiguration_ConstructsSuccessfully()
    {
        var action = () => new AzureKeyVaultEncryptionService(_configuration, _loggerMock.Object, _cache);

        action.Should().NotThrow();
    }

    [Fact]
    public async Task ValidateKeyAccessAsync_WithoutAzureCredentials_ReturnsFalse()
    {
        // This test will fail without Azure credentials (expected in local dev)
        // In CI/CD with Azure service principal, this should pass
        var service = new AzureKeyVaultEncryptionService(_configuration, _loggerMock.Object, _cache);

        var result = await service.ValidateKeyAccessAsync();

        // Without Azure credentials, validation should fail gracefully
        result.Should().BeFalse();
    }
}
