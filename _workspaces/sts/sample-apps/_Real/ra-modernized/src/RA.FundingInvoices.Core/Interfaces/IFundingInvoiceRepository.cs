namespace RA.FundingInvoices.Core.Interfaces;

/// <summary>
/// Repository interface for FundingInvoice entity.
/// Supports both Mock (in-memory) and EF Core (database) implementations.
/// </summary>
public interface IFundingInvoiceRepository
{
    /// <summary>
    /// Retrieves a funding invoice by its unique identifier.
    /// </summary>
    /// <param name="invoiceId">The unique invoice identifier.</param>
    /// <returns>The funding invoice if found; otherwise, null.</returns>
    Task<FundingInvoice?> GetByIdAsync(string invoiceId);

    /// <summary>
    /// Retrieves all funding invoices (use with caution in production).
    /// </summary>
    /// <returns>Collection of all funding invoices.</returns>
    Task<IEnumerable<FundingInvoice>> GetAllAsync();

    /// <summary>
    /// Retrieves funding invoices by batch identifier.
    /// </summary>
    /// <param name="batchId">The batch identifier.</param>
    /// <returns>Collection of invoices in the specified batch.</returns>
    Task<IEnumerable<FundingInvoice>> GetByBatchIdAsync(string batchId);

    /// <summary>
    /// Retrieves funding invoices by subaccount identifier.
    /// </summary>
    /// <param name="subaccountId">The subaccount identifier.</param>
    /// <returns>Collection of invoices for the specified subaccount.</returns>
    Task<IEnumerable<FundingInvoice>> GetBySubaccountIdAsync(string subaccountId);

    /// <summary>
    /// Retrieves funding invoices created within a date range.
    /// </summary>
    /// <param name="startDate">Start date (inclusive).</param>
    /// <param name="endDate">End date (inclusive).</param>
    /// <returns>Collection of invoices created within the date range.</returns>
    Task<IEnumerable<FundingInvoice>> GetByDateRangeAsync(DateTime startDate, DateTime endDate);

    /// <summary>
    /// Creates a new funding invoice.
    /// </summary>
    /// <param name="invoice">The invoice to create.</param>
    /// <returns>The created invoice with generated ID.</returns>
    Task<FundingInvoice> CreateAsync(FundingInvoice invoice);

    /// <summary>
    /// Updates an existing funding invoice.
    /// </summary>
    /// <param name="invoice">The invoice with updated values.</param>
    /// <returns>The updated invoice.</returns>
    Task<FundingInvoice> UpdateAsync(FundingInvoice invoice);

    /// <summary>
    /// Deletes a funding invoice by its identifier.
    /// </summary>
    /// <param name="invoiceId">The invoice identifier to delete.</param>
    /// <returns>True if deleted; otherwise, false.</returns>
    Task<bool> DeleteAsync(string invoiceId);

    /// <summary>
    /// Checks if a funding invoice exists.
    /// </summary>
    /// <param name="invoiceId">The invoice identifier.</param>
    /// <returns>True if exists; otherwise, false.</returns>
    Task<bool> ExistsAsync(string invoiceId);
}

// TODO: Phase 2 - Define FundingInvoice entity class
public class FundingInvoice
{
    public string InvoiceId { get; set; } = string.Empty;
    public string BatchId { get; set; } = string.Empty;
    public string SubaccountId { get; set; } = string.Empty;
    public decimal Amount { get; set; }
    public DateTime CreatedDate { get; set; }
    public DateTime? ProcessedDate { get; set; }
    public string Status { get; set; } = string.Empty;
}
