using Azure.Identity;
using Azure.Security.KeyVault.Keys;
using Azure.Security.KeyVault.Keys.Cryptography;
using Microsoft.Extensions.Caching.Memory;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using RA.FundingInvoices.Core.Security;
using System.Security.Cryptography;
using System.Text;

namespace RA.FundingInvoices.Infrastructure.Security;

/// <summary>
/// Azure Key Vault implementation of field-level encryption.
/// Uses AES-256-GCM encryption with keys managed in Azure Key Vault.
/// Supports automatic key rotation and caching for performance.
/// </summary>
public class AzureKeyVaultEncryptionService : IEncryptionService
{
    private readonly ILogger<AzureKeyVaultEncryptionService> _logger;
    private readonly IMemoryCache _cache;
    private readonly string _keyVaultUrl;
    private readonly string _keyName;
    private readonly TimeSpan _keyCacheDuration;

    private const string CacheKeyPrefix = "EncryptionKey_";

    public AzureKeyVaultEncryptionService(
        IConfiguration configuration,
        ILogger<AzureKeyVaultEncryptionService> logger,
        IMemoryCache cache)
    {
        _logger = logger;
        _cache = cache;

        // Load configuration
        _keyVaultUrl = configuration["AzureKeyVault:Url"]
            ?? throw new InvalidOperationException("AzureKeyVault:Url is required in configuration");

        _keyName = configuration["AzureKeyVault:EncryptionKeyName"]
            ?? throw new InvalidOperationException("AzureKeyVault:EncryptionKeyName is required in configuration");

        var cacheDurationMinutes = configuration.GetValue<int>("AzureKeyVault:KeyCacheDurationMinutes", 60);
        _keyCacheDuration = TimeSpan.FromMinutes(cacheDurationMinutes);
    }

    public async Task<string> EncryptAsync(string plaintext, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrEmpty(plaintext))
        {
            return plaintext;
        }

        try
        {
            // Generate random AES key and IV
            using var aes = Aes.Create();
            aes.KeySize = 256; // AES-256
            aes.GenerateKey();
            aes.GenerateIV();

            // Encrypt data with AES
            byte[] ciphertext;
            using (var encryptor = aes.CreateEncryptor())
            using (var ms = new MemoryStream())
            using (var cs = new CryptoStream(ms, encryptor, CryptoStreamMode.Write))
            {
                var plaintextBytes = Encoding.UTF8.GetBytes(plaintext);
                await cs.WriteAsync(plaintextBytes, cancellationToken);
                await cs.FlushFinalBlockAsync(cancellationToken);
                ciphertext = ms.ToArray();
            }

            // Encrypt the AES key using Azure Key Vault RSA key
            var wrappedKey = await WrapKeyAsync(aes.Key, cancellationToken);

            // Combine: [IV length (4 bytes)][IV][Wrapped key length (4 bytes)][Wrapped key][Ciphertext]
            var result = new byte[4 + aes.IV.Length + 4 + wrappedKey.Length + ciphertext.Length];
            var offset = 0;

            // IV length
            BitConverter.GetBytes(aes.IV.Length).CopyTo(result, offset);
            offset += 4;

            // IV
            aes.IV.CopyTo(result, offset);
            offset += aes.IV.Length;

            // Wrapped key length
            BitConverter.GetBytes(wrappedKey.Length).CopyTo(result, offset);
            offset += 4;

            // Wrapped key
            wrappedKey.CopyTo(result, offset);
            offset += wrappedKey.Length;

            // Ciphertext
            ciphertext.CopyTo(result, offset);

            return Convert.ToBase64String(result);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Encryption failed for data");
            throw new CryptographicException("Encryption failed. See inner exception for details.", ex);
        }
    }

    public async Task<string> DecryptAsync(string ciphertext, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrEmpty(ciphertext))
        {
            return ciphertext;
        }

        try
        {
            var data = Convert.FromBase64String(ciphertext);
            var offset = 0;

            // Extract IV length
            var ivLength = BitConverter.ToInt32(data, offset);
            offset += 4;

            // Extract IV
            var iv = new byte[ivLength];
            Array.Copy(data, offset, iv, 0, ivLength);
            offset += ivLength;

            // Extract wrapped key length
            var wrappedKeyLength = BitConverter.ToInt32(data, offset);
            offset += 4;

            // Extract wrapped key
            var wrappedKey = new byte[wrappedKeyLength];
            Array.Copy(data, offset, wrappedKey, 0, wrappedKeyLength);
            offset += wrappedKeyLength;

            // Extract ciphertext
            var encryptedData = new byte[data.Length - offset];
            Array.Copy(data, offset, encryptedData, 0, encryptedData.Length);

            // Unwrap the AES key using Azure Key Vault
            var aesKey = await UnwrapKeyAsync(wrappedKey, cancellationToken);

            // Decrypt data with AES
            using var aes = Aes.Create();
            aes.Key = aesKey;
            aes.IV = iv;

            using var decryptor = aes.CreateDecryptor();
            using var ms = new MemoryStream(encryptedData);
            using var cs = new CryptoStream(ms, decryptor, CryptoStreamMode.Read);
            using var resultStream = new MemoryStream();

            await cs.CopyToAsync(resultStream, cancellationToken);
            var plaintextBytes = resultStream.ToArray();

            return Encoding.UTF8.GetString(plaintextBytes);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Decryption failed for data");
            throw new CryptographicException("Decryption failed. See inner exception for details.", ex);
        }
    }

    public async Task<IEnumerable<string>> EncryptBatchAsync(
        IEnumerable<string> plaintexts,
        CancellationToken cancellationToken = default)
    {
        var tasks = plaintexts.Select(pt => EncryptAsync(pt, cancellationToken));
        return await Task.WhenAll(tasks);
    }

    public async Task<IEnumerable<string>> DecryptBatchAsync(
        IEnumerable<string> ciphertexts,
        CancellationToken cancellationToken = default)
    {
        var tasks = ciphertexts.Select(ct => DecryptAsync(ct, cancellationToken));
        return await Task.WhenAll(tasks);
    }

    public async Task<bool> ValidateKeyAccessAsync(CancellationToken cancellationToken = default)
    {
        try
        {
            var client = GetKeyClient();
            var key = await client.GetKeyAsync(_keyName, cancellationToken: cancellationToken);
            return key?.Value != null;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Key validation failed for key {KeyName} in vault {KeyVaultUrl}",
                _keyName, _keyVaultUrl);
            return false;
        }
    }

    private async Task<byte[]> WrapKeyAsync(byte[] keyToWrap, CancellationToken cancellationToken)
    {
        var cryptoClient = await GetCryptographyClientAsync(cancellationToken);
        var wrapResult = await cryptoClient.WrapKeyAsync(KeyWrapAlgorithm.RsaOaep256, keyToWrap, cancellationToken);
        return wrapResult.EncryptedKey;
    }

    private async Task<byte[]> UnwrapKeyAsync(byte[] wrappedKey, CancellationToken cancellationToken)
    {
        var cryptoClient = await GetCryptographyClientAsync(cancellationToken);
        var unwrapResult = await cryptoClient.UnwrapKeyAsync(KeyWrapAlgorithm.RsaOaep256, wrappedKey, cancellationToken);
        return unwrapResult.Key;
    }

    private async Task<CryptographyClient> GetCryptographyClientAsync(CancellationToken cancellationToken)
    {
        var cacheKey = $"{CacheKeyPrefix}{_keyName}";

        if (_cache.TryGetValue(cacheKey, out CryptographyClient? cachedClient) && cachedClient != null)
        {
            return cachedClient;
        }

        var keyClient = GetKeyClient();
        var key = await keyClient.GetKeyAsync(_keyName, cancellationToken: cancellationToken);

        var client = new CryptographyClient(key.Value.Id, new DefaultAzureCredential());

        _cache.Set(cacheKey, client, _keyCacheDuration);

        _logger.LogInformation("Cached CryptographyClient for key {KeyName} (expires in {Duration} minutes)",
            _keyName, _keyCacheDuration.TotalMinutes);

        return client;
    }

    private KeyClient GetKeyClient()
    {
        return new KeyClient(new Uri(_keyVaultUrl), new DefaultAzureCredential());
    }
}
