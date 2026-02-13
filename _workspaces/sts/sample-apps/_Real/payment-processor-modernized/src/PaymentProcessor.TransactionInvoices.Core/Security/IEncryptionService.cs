namespace PaymentProcessor.TransactionInvoices.Core.Security;

/// <summary>
/// Abstraction for field-level encryption operations.
/// Supports GDPR/ISO27001 compliance with AES-256-GCM encryption.
/// </summary>
public interface IEncryptionService
{
    /// <summary>
    /// Encrypts plaintext data using AES-256-GCM encryption.
    /// </summary>
    /// <param name="plaintext">Data to encrypt (SSN, account numbers, names, etc.)</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Base64-encoded ciphertext suitable for database storage</returns>
    Task<string> EncryptAsync(string plaintext, CancellationToken cancellationToken = default);

    /// <summary>
    /// Decrypts ciphertext using AES-256-GCM encryption.
    /// </summary>
    /// <param name="ciphertext">Base64-encoded encrypted data from database</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Original plaintext value</returns>
    Task<string> DecryptAsync(string ciphertext, CancellationToken cancellationToken = default);

    /// <summary>
    /// Encrypts multiple values in parallel for batch operations.
    /// </summary>
    /// <param name="plaintexts">Collection of values to encrypt</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Base64-encoded ciphertexts in same order as input</returns>
    Task<IEnumerable<string>> EncryptBatchAsync(
        IEnumerable<string> plaintexts,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Decrypts multiple values in parallel for batch operations.
    /// </summary>
    /// <param name="ciphertexts">Collection of encrypted values</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Plaintext values in same order as input</returns>
    Task<IEnumerable<string>> DecryptBatchAsync(
        IEnumerable<string> ciphertexts,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Validates that the encryption service can access the encryption key.
    /// Used for health checks and startup validation.
    /// </summary>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>True if encryption key is accessible, false otherwise</returns>
    Task<bool> ValidateKeyAccessAsync(CancellationToken cancellationToken = default);
}
