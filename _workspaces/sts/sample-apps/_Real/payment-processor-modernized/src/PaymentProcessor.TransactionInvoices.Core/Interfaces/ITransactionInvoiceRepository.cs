namespace PaymentProcessor.TransactionInvoices.Core.Interfaces;

/// <summary>
/// Repository interface for TransactionInvoice entity.
/// Supports both Mock (in-memory) and EF Core (database) implementations.
/// </summary>
public interface ITransactionInvoiceRepository
{
    /// <summary>
    /// Retrieves a transaction invoice by its unique identifier.
    /// </summary>
    /// <param name="invoiceId">The unique invoice identifier.</param>
    /// <returns>The transaction invoice if found; otherwise, null.</returns>
    Task<TransactionInvoice?> GetByIdAsync(string invoiceId);

    /// <summary>
    /// Retrieves all transaction invoices (use with caution in production).
    /// </summary>
    /// <returns>Collection of all transaction invoices.</returns>
    Task<IEnumerable<TransactionInvoice>> GetAllAsync();

    /// <summary>
    /// Retrieves transaction invoices by batch identifier.
    /// </summary>
    /// <param name="batchId">The batch identifier.</param>
    /// <returns>Collection of invoices in the specified batch.</returns>
    Task<IEnumerable<TransactionInvoice>> GetByBatchIdAsync(string batchId);

    /// <summary>
    /// Retrieves transaction invoices by account_category identifier.
    /// </summary>
    /// <param name="account_categoryId">The account_category identifier.</param>
    /// <returns>Collection of invoices for the specified account_category.</returns>
    Task<IEnumerable<TransactionInvoice>> GetByAccountCategoryIdAsync(string account_categoryId);

    /// <summary>
    /// Retrieves transaction invoices created within a date range.
    /// </summary>
    /// <param name="startDate">Start date (inclusive).</param>
    /// <param name="endDate">End date (inclusive).</param>
    /// <returns>Collection of invoices created within the date range.</returns>
    Task<IEnumerable<TransactionInvoice>> GetByDateRangeAsync(DateTime startDate, DateTime endDate);

    /// <summary>
    /// Creates a new transaction invoice.
    /// </summary>
    /// <param name="invoice">The invoice to create.</param>
    /// <returns>The created invoice with generated ID.</returns>
    Task<TransactionInvoice> CreateAsync(TransactionInvoice invoice);

    /// <summary>
    /// Updates an existing transaction invoice.
    /// </summary>
    /// <param name="invoice">The invoice with updated values.</param>
    /// <returns>The updated invoice.</returns>
    Task<TransactionInvoice> UpdateAsync(TransactionInvoice invoice);

    /// <summary>
    /// Deletes a transaction invoice by its identifier.
    /// </summary>
    /// <param name="invoiceId">The invoice identifier to delete.</param>
    /// <returns>True if deleted; otherwise, false.</returns>
    Task<bool> DeleteAsync(string invoiceId);

    /// <summary>
    /// Checks if a transaction invoice exists.
    /// </summary>
    /// <param name="invoiceId">The invoice identifier.</param>
    /// <returns>True if exists; otherwise, false.</returns>
    Task<bool> ExistsAsync(string invoiceId);
}

// TODO: Phase 2 - Define TransactionInvoice entity class
public class TransactionInvoice
{
    public string InvoiceId { get; set; } = string.Empty;
    public string BatchId { get; set; } = string.Empty;
    public string AccountCategoryId { get; set; } = string.Empty;
    public decimal Amount { get; set; }
    public DateTime CreatedDate { get; set; }
    public DateTime? ProcessedDate { get; set; }
    public string Status { get; set; } = string.Empty;
}
