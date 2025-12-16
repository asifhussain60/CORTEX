using PaymentProcessor.TransactionInvoices.Core.DTOs;
using System.Threading.Tasks;

namespace PaymentProcessor.TransactionInvoices.Core.Services;

/// <summary>
/// Service interface for transaction batch operations.
/// Encapsulates business logic extracted from WCF transactions.
/// </summary>
public interface ITransactionBatchService
{
    /// <summary>
    /// Closes a transaction batch and creates replenishment invoice with CashInOut.
    /// Extracts logic from XCloseTransactionBatch.cs
    /// </summary>
    /// <param name="request">Batch closure request with exclusions and auto-debit settings</param>
    /// <returns>Batch closure response with CashInOut details</returns>
    Task<CloseTransactionBatchResponse> CloseAsync(CloseTransactionBatchRequest request);

    /// <summary>
    /// Reopens a closed or pending transaction batch.
    /// Extracts logic from XReopenTransactionBatch.cs
    /// </summary>
    /// <param name="request">Batch reopen request</param>
    /// <returns>Reopened batch response</returns>
    Task<TransactionBatchResponse> ReopenAsync(ReopenTransactionBatchRequest request);

    /// <summary>
    /// Updates transaction batch metadata (description, dates, etc.).
    /// Extracts logic from XUpdateTransactionBatch.cs
    /// </summary>
    /// <param name="request">Batch update request</param>
    /// <returns>Updated batch response</returns>
    Task<TransactionBatchResponse> UpdateAsync(UpdateTransactionBatchRequest request);

    /// <summary>
    /// Creates a new transaction batch for a account_category.
    /// </summary>
    /// <param name="request">Batch creation request</param>
    /// <returns>Created batch response</returns>
    Task<TransactionBatchResponse> CreateAsync(CreateTransactionBatchRequest request);

    /// <summary>
    /// Retrieves transaction batch by ID with related invoices.
    /// </summary>
    /// <param name="batchId">Batch identifier</param>
    /// <returns>Transaction batch details or null if not found</returns>
    Task<TransactionBatchResponse?> GetByIdAsync(string batchId);

    /// <summary>
    /// Retrieves all batches for a specific account_category.
    /// </summary>
    /// <param name="account_categoryId">AccountCategory identifier</param>
    /// <returns>List of transaction batches</returns>
    Task<IEnumerable<TransactionBatchResponse>> GetByAccountCategoryIdAsync(string account_categoryId);

    /// <summary>
    /// Retrieves open transaction batch for a account_category (used by batch creation logic).
    /// </summary>
    /// <param name="account_categoryId">AccountCategory identifier</param>
    /// <returns>Open batch or null if none exists</returns>
    Task<TransactionBatchResponse?> GetOpenBatchAsync(string account_categoryId);
}
