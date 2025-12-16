using RA.FundingInvoices.Core.DTOs;
using System.Threading.Tasks;

namespace RA.FundingInvoices.Core.Services;

/// <summary>
/// Service interface for funding batch operations.
/// Encapsulates business logic extracted from WCF transactions.
/// </summary>
public interface IFundingBatchService
{
    /// <summary>
    /// Closes a funding batch and creates replenishment invoice with CashInOut.
    /// Extracts logic from XCloseFundingBatch.cs
    /// </summary>
    /// <param name="request">Batch closure request with exclusions and auto-debit settings</param>
    /// <returns>Batch closure response with CashInOut details</returns>
    Task<CloseFundingBatchResponse> CloseAsync(CloseFundingBatchRequest request);

    /// <summary>
    /// Reopens a closed or pending funding batch.
    /// Extracts logic from XReopenFundingBatch.cs
    /// </summary>
    /// <param name="request">Batch reopen request</param>
    /// <returns>Reopened batch response</returns>
    Task<FundingBatchResponse> ReopenAsync(ReopenFundingBatchRequest request);

    /// <summary>
    /// Updates funding batch metadata (description, dates, etc.).
    /// Extracts logic from XUpdateFundingBatch.cs
    /// </summary>
    /// <param name="request">Batch update request</param>
    /// <returns>Updated batch response</returns>
    Task<FundingBatchResponse> UpdateAsync(UpdateFundingBatchRequest request);

    /// <summary>
    /// Creates a new funding batch for a subaccount.
    /// </summary>
    /// <param name="request">Batch creation request</param>
    /// <returns>Created batch response</returns>
    Task<FundingBatchResponse> CreateAsync(CreateFundingBatchRequest request);

    /// <summary>
    /// Retrieves funding batch by ID with related invoices.
    /// </summary>
    /// <param name="batchId">Batch identifier</param>
    /// <returns>Funding batch details or null if not found</returns>
    Task<FundingBatchResponse?> GetByIdAsync(string batchId);

    /// <summary>
    /// Retrieves all batches for a specific subaccount.
    /// </summary>
    /// <param name="subaccountId">Subaccount identifier</param>
    /// <returns>List of funding batches</returns>
    Task<IEnumerable<FundingBatchResponse>> GetBySubaccountIdAsync(string subaccountId);

    /// <summary>
    /// Retrieves open funding batch for a subaccount (used by batch creation logic).
    /// </summary>
    /// <param name="subaccountId">Subaccount identifier</param>
    /// <returns>Open batch or null if none exists</returns>
    Task<FundingBatchResponse?> GetOpenBatchAsync(string subaccountId);
}
