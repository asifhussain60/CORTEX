namespace RA.FundingInvoices.Core.Interfaces;

/// <summary>
/// Repository interface for FundingBatch entity.
/// Manages batch operations for funding invoice processing.
/// </summary>
public interface IFundingBatchRepository
{
    /// <summary>
    /// Retrieves a funding batch by its unique identifier.
    /// </summary>
    /// <param name="batchId">The unique batch identifier.</param>
    /// <returns>The funding batch if found; otherwise, null.</returns>
    Task<FundingBatch?> GetByIdAsync(string batchId);

    /// <summary>
    /// Retrieves all funding batches.
    /// </summary>
    /// <returns>Collection of all funding batches.</returns>
    Task<IEnumerable<FundingBatch>> GetAllAsync();

    /// <summary>
    /// Retrieves funding batches by status.
    /// </summary>
    /// <param name="status">The batch status (e.g., "Pending", "Processing", "Completed").</param>
    /// <returns>Collection of batches with the specified status.</returns>
    Task<IEnumerable<FundingBatch>> GetByStatusAsync(string status);

    /// <summary>
    /// Retrieves funding batches created within a date range.
    /// </summary>
    /// <param name="startDate">Start date (inclusive).</param>
    /// <param name="endDate">End date (inclusive).</param>
    /// <returns>Collection of batches created within the date range.</returns>
    Task<IEnumerable<FundingBatch>> GetByDateRangeAsync(DateTime startDate, DateTime endDate);

    /// <summary>
    /// Creates a new funding batch.
    /// </summary>
    /// <param name="batch">The batch to create.</param>
    /// <returns>The created batch with generated ID.</returns>
    Task<FundingBatch> CreateAsync(FundingBatch batch);

    /// <summary>
    /// Updates an existing funding batch.
    /// </summary>
    /// <param name="batch">The batch with updated values.</param>
    /// <returns>The updated batch.</returns>
    Task<FundingBatch> UpdateAsync(FundingBatch batch);

    /// <summary>
    /// Updates the status of a funding batch.
    /// </summary>
    /// <param name="batchId">The batch identifier.</param>
    /// <param name="newStatus">The new status.</param>
    /// <returns>The updated batch.</returns>
    Task<FundingBatch> UpdateStatusAsync(string batchId, string newStatus);

    /// <summary>
    /// Deletes a funding batch by its identifier.
    /// </summary>
    /// <param name="batchId">The batch identifier to delete.</param>
    /// <returns>True if deleted; otherwise, false.</returns>
    Task<bool> DeleteAsync(string batchId);
}

// TODO: Phase 2 - Define FundingBatch entity class
public class FundingBatch
{
    public string BatchId { get; set; } = string.Empty;
    public string EmployerId { get; set; } = string.Empty;
    public DateTime CreatedDate { get; set; }
    public DateTime? ProcessedDate { get; set; }
    public string Status { get; set; } = "Pending";
    public int TotalInvoices { get; set; }
    public decimal TotalAmount { get; set; }
}
