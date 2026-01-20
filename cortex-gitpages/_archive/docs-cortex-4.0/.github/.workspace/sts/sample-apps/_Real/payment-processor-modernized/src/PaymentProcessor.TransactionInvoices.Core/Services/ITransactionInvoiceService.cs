using PaymentProcessor.TransactionInvoices.Core.DTOs;
using System.Threading.Tasks;

namespace PaymentProcessor.TransactionInvoices.Core.Services;

/// <summary>
/// Service interface for transaction invoice operations.
/// Encapsulates business logic extracted from WCF transactions.
/// </summary>
public interface ITransactionInvoiceService
{
    /// <summary>
    /// Creates a transaction invoice for payroll-based transaction.
    /// Extracts logic from XAddTransactionInvoice.cs
    /// </summary>
    /// <param name="request">Invoice creation request with employer and account details</param>
    /// <returns>Created transaction invoice response</returns>
    Task<TransactionInvoiceResponse> CreateAsync(CreateTransactionInvoiceRequest request);

    /// <summary>
    /// Generates on-demand transaction invoice based on peg amount logic.
    /// Extracts logic from XGenerateTransactionInvoice.cs
    /// </summary>
    /// <param name="request">Invoice generation request with peg amount calculations</param>
    /// <returns>Generated transaction invoice response or "not needed" result</returns>
    Task<GenerateTransactionInvoiceResponse> GenerateAsync(GenerateTransactionInvoiceRequest request);

    /// <summary>
    /// Creates batch transaction invoices for multiple account_categorys.
    /// Extracts logic from Updater_CreatePaymentTransactionInvoices.cs
    /// </summary>
    /// <param name="request">Batch creation request with account_category list</param>
    /// <returns>Batch creation response with success/failure counts</returns>
    Task<BatchTransactionInvoiceResponse> CreateBatchAsync(CreateBatchTransactionInvoiceRequest request);

    /// <summary>
    /// Creates batch transaction invoices for multiple account_categorys (WCF: Updater_CreatePaymentTransactionInvoices).
    /// Processes each account_category individually, handles partial success, and returns detailed results.
    /// </summary>
    /// <param name="dto">Batch invoice creation request with employer ID and account_category list</param>
    /// <returns>Batch invoice result with success/failure counts and failed account_category details</returns>
    Task<BatchInvoiceResultDto> CreateBatchInvoicesAsync(CreateBatchInvoicesDto dto);

    /// <summary>
    /// Generates transaction invoice based on balance vs peg logic (WCF: XGenerateTransactionInvoice).
    /// Only creates invoice if account_category balance is below peg amount.
    /// </summary>
    /// <param name="dto">Generate invoice request with account_category ID and invoice amount</param>
    /// <returns>Generation result indicating if invoice was created or not needed</returns>
    Task<GenerateTransactionInvoiceResultDto> GenerateTransactionInvoiceAsync(GenerateTransactionInvoiceDto dto);

    /// <summary>
    /// Retrieves transaction invoice by ID with related entities.
    /// </summary>
    /// <param name="invoiceId">Invoice identifier</param>
    /// <returns>Transaction invoice details or null if not found</returns>
    Task<TransactionInvoiceResponse?> GetByIdAsync(string invoiceId);

    /// <summary>
    /// Retrieves all transaction invoices for a specific batch.
    /// </summary>
    /// <param name="batchId">Batch identifier</param>
    /// <returns>List of transaction invoices in the batch</returns>
    Task<IEnumerable<TransactionInvoiceResponse>> GetByBatchIdAsync(string batchId);

    /// <summary>
    /// Retrieves all transaction invoices for a specific account_category.
    /// </summary>
    /// <param name="account_categoryId">AccountCategory identifier</param>
    /// <returns>List of transaction invoices for the account_category</returns>
    Task<IEnumerable<TransactionInvoiceResponse>> GetByAccountCategoryIdAsync(string account_categoryId);
}
