namespace PaymentProcessor.TransactionInvoices.Core.Interfaces;

/// <summary>
/// Repository interface for CashInOut entity.
/// Tracks cash-in and cash-out transactions for transaction invoices.
/// </summary>
public interface ICashInOutRepository
{
    /// <summary>
    /// Retrieves a cash transaction by its unique identifier.
    /// </summary>
    /// <param name="transactionId">The unique transaction identifier.</param>
    /// <returns>The cash transaction if found; otherwise, null.</returns>
    Task<CashInOut?> GetByIdAsync(string transactionId);

    /// <summary>
    /// Retrieves all cash transactions.
    /// </summary>
    /// <returns>Collection of all cash transactions.</returns>
    Task<IEnumerable<CashInOut>> GetAllAsync();

    /// <summary>
    /// Retrieves cash transactions by invoice identifier.
    /// </summary>
    /// <param name="invoiceId">The invoice identifier.</param>
    /// <returns>Collection of transactions for the specified invoice.</returns>
    Task<IEnumerable<CashInOut>> GetByInvoiceIdAsync(string invoiceId);

    /// <summary>
    /// Retrieves cash transactions by account_category identifier.
    /// </summary>
    /// <param name="account_categoryId">The account_category identifier.</param>
    /// <returns>Collection of transactions for the specified account_category.</returns>
    Task<IEnumerable<CashInOut>> GetByAccountCategoryIdAsync(string account_categoryId);

    /// <summary>
    /// Retrieves cash transactions by transaction type.
    /// </summary>
    /// <param name="transactionType">The transaction type (e.g., "CashIn", "CashOut").</param>
    /// <returns>Collection of transactions with the specified type.</returns>
    Task<IEnumerable<CashInOut>> GetByTransactionTypeAsync(string transactionType);

    /// <summary>
    /// Creates a new cash transaction.
    /// </summary>
    /// <param name="transaction">The transaction to create.</param>
    /// <returns>The created transaction.</returns>
    Task<CashInOut> CreateAsync(CashInOut transaction);

    /// <summary>
    /// Updates an existing cash transaction.
    /// </summary>
    /// <param name="transaction">The transaction with updated values.</param>
    /// <returns>The updated transaction.</returns>
    Task<CashInOut> UpdateAsync(CashInOut transaction);

    /// <summary>
    /// Deletes a cash transaction by its identifier.
    /// </summary>
    /// <param name="transactionId">The transaction identifier to delete.</param>
    /// <returns>True if deleted; otherwise, false.</returns>
    Task<bool> DeleteAsync(string transactionId);
}

// TODO: Phase 2 - Define CashInOut entity class
public class CashInOut
{
    public string TransactionId { get; set; } = string.Empty;
    public string InvoiceId { get; set; } = string.Empty;
    public string AccountCategoryId { get; set; } = string.Empty;
    public string TransactionType { get; set; } = string.Empty;
    public decimal Amount { get; set; }
    public DateTime TransactionDate { get; set; }
    public string Status { get; set; } = string.Empty;
}
