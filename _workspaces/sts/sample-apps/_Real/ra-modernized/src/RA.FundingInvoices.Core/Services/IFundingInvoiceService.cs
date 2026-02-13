using RA.FundingInvoices.Core.DTOs;
using System.Threading.Tasks;

namespace RA.FundingInvoices.Core.Services;

/// <summary>
/// Service interface for funding invoice operations.
/// Encapsulates business logic extracted from WCF transactions.
/// </summary>
public interface IFundingInvoiceService
{
    /// <summary>
    /// Creates a funding invoice for payroll-based funding.
    /// Extracts logic from XAddFundingInvoice.cs
    /// </summary>
    /// <param name="request">Invoice creation request with employer and account details</param>
    /// <returns>Created funding invoice response</returns>
    Task<FundingInvoiceResponse> CreateAsync(CreateFundingInvoiceRequest request);

    /// <summary>
    /// Generates on-demand funding invoice based on peg amount logic.
    /// Extracts logic from XGenerateFundingInvoice.cs
    /// </summary>
    /// <param name="request">Invoice generation request with peg amount calculations</param>
    /// <returns>Generated funding invoice response or "not needed" result</returns>
    Task<GenerateFundingInvoiceResponse> GenerateAsync(GenerateFundingInvoiceRequest request);

    /// <summary>
    /// Creates batch funding invoices for multiple subaccounts.
    /// Extracts logic from Updater_CreateRAFundingInvoices.cs
    /// </summary>
    /// <param name="request">Batch creation request with subaccount list</param>
    /// <returns>Batch creation response with success/failure counts</returns>
    Task<BatchFundingInvoiceResponse> CreateBatchAsync(CreateBatchFundingInvoiceRequest request);

    /// <summary>
    /// Creates batch funding invoices for multiple subaccounts (WCF: Updater_CreateRAFundingInvoices).
    /// Processes each subaccount individually, handles partial success, and returns detailed results.
    /// </summary>
    /// <param name="dto">Batch invoice creation request with employer ID and subaccount list</param>
    /// <returns>Batch invoice result with success/failure counts and failed subaccount details</returns>
    Task<BatchInvoiceResultDto> CreateBatchInvoicesAsync(CreateBatchInvoicesDto dto);

    /// <summary>
    /// Generates funding invoice based on balance vs peg logic (WCF: XGenerateFundingInvoice).
    /// Only creates invoice if subaccount balance is below peg amount.
    /// </summary>
    /// <param name="dto">Generate invoice request with subaccount ID and invoice amount</param>
    /// <returns>Generation result indicating if invoice was created or not needed</returns>
    Task<GenerateFundingInvoiceResultDto> GenerateFundingInvoiceAsync(GenerateFundingInvoiceDto dto);

    /// <summary>
    /// Retrieves funding invoice by ID with related entities.
    /// </summary>
    /// <param name="invoiceId">Invoice identifier</param>
    /// <returns>Funding invoice details or null if not found</returns>
    Task<FundingInvoiceResponse?> GetByIdAsync(string invoiceId);

    /// <summary>
    /// Retrieves all funding invoices for a specific batch.
    /// </summary>
    /// <param name="batchId">Batch identifier</param>
    /// <returns>List of funding invoices in the batch</returns>
    Task<IEnumerable<FundingInvoiceResponse>> GetByBatchIdAsync(string batchId);

    /// <summary>
    /// Retrieves all funding invoices for a specific subaccount.
    /// </summary>
    /// <param name="subaccountId">Subaccount identifier</param>
    /// <returns>List of funding invoices for the subaccount</returns>
    Task<IEnumerable<FundingInvoiceResponse>> GetBySubaccountIdAsync(string subaccountId);
}
