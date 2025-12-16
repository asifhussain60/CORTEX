namespace PaymentProcessor.TransactionInvoices.Core.Interfaces;

/// <summary>
/// Repository interface for TransactionBatch entity.
/// Manages batch operations for transaction invoice processing.
/// </summary>
public interface ITransactionBatchRepository
{
    /// <summary>
    /// Retrieves a transaction batch by its unique identifier.
    /// </summary>
    /// <param name="batchId">The unique batch identifier.</param>
    /// <returns>The transaction batch if found; otherwise, null.</returns>
    Task<TransactionBatch?> GetByIdAsync(string batchId);

    /// <summary>
    /// Retrieves all transaction batches.
    /// </summary>
    /// <returns>Collection of all transaction batches.</returns>
    Task<IEnumerable<TransactionBatch>> GetAllAsync();

    /// <summary>
    /// Retrieves transaction batches by status.
    /// </summary>
    /// <param name="status">The batch status (e.g., "Pending", "Processing", "Completed").</param>
    /// <returns>Collection of batches with the specified status.</returns>
    Task<IEnumerable<TransactionBatch>> GetByStatusAsync(string status);

    /// <summary>
    /// Retrieves transaction batches created within a date range.
    /// </summary>
    /// <param name="startDate">Start date (inclusive).</param>
    /// <param name="endDate">End date (inclusive).</param>
    /// <returns>Collection of batches created within the date range.</returns>
    Task<IEnumerable<TransactionBatch>> GetByDateRangeAsync(DateTime startDate, DateTime endDate);

    /// <summary>
    /// Creates a new transaction batch.
    /// </summary>
    /// <param name="batch">The batch to create.</param>
    /// <returns>The created batch with generated ID.</returns>
    Task<TransactionBatch> CreateAsync(TransactionBatch batch);

    /// <summary>
    /// Updates an existing transaction batch.
    /// </summary>
    /// <param name="batch">The batch with updated values.</param>
    /// <returns>The updated batch.</returns>
    Task<TransactionBatch> UpdateAsync(TransactionBatch batch);

    /// <summary>
    /// Updates the status of a transaction batch.
    /// </summary>
    /// <param name="batchId">The batch identifier.</param>
    /// <param name="newStatus">The new status.</param>
    /// <returns>The updated batch.</returns>
    Task<TransactionBatch> UpdateStatusAsync(string batchId, string newStatus);

    /// <summary>
    /// Deletes a transaction batch by its identifier.
    /// </summary>
    /// <param name="batchId">The batch identifier to delete.</param>
    /// <returns>True if deleted; otherwise, false.</returns>
    Task<bool> DeleteAsync(string batchId);
}

// TODO: Phase 2 - Define TransactionBatch entity class
public class TransactionBatch
{
    public string BatchId { get; set; } = string.Empty;
    public string EmployerId { get; set; } = string.Empty;
    public DateTime CreatedDate { get; set; }
    public DateTime? ProcessedDate { get; set; }
    public string Status { get; set; } = "Pending";
    public int TotalInvoices { get; set; }
    public decimal TotalAmount { get; set; }
}
