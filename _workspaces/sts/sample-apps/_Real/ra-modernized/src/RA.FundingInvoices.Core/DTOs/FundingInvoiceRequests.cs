using System;

namespace RA.FundingInvoices.Core.DTOs;

/// <summary>
/// Request to create a funding invoice (payroll-based funding).
/// Maps to XAddFundingInvoice WCF transaction.
/// </summary>
public class CreateFundingInvoiceRequest
{
    /// <summary>
    /// Employer identifier who is funding the account.
    /// </summary>
    public string EmployerId { get; set; } = string.Empty;

    /// <summary>
    /// Subaccount identifier to fund.
    /// </summary>
    public string SubaccountId { get; set; } = string.Empty;

    /// <summary>
    /// Reimbursement plan identifier.
    /// </summary>
    public string ReimbursementPlanId { get; set; } = string.Empty;

    /// <summary>
    /// Employer funding default amount (ER contribution).
    /// </summary>
    public decimal EmployerFundingDefault { get; set; }

    /// <summary>
    /// Employee funding default amount (EE contribution).
    /// </summary>
    public decimal EmployeeFundingDefault { get; set; }

    /// <summary>
    /// Effective date for the funding invoice.
    /// </summary>
    public DateTime EffectiveDate { get; set; } = DateTime.UtcNow;

    /// <summary>
    /// Invoice description template.
    /// </summary>
    public string InvoiceDescription { get; set; } = string.Empty;

    /// <summary>
    /// Whether this is an LSA (Limited Spending Account) plan.
    /// </summary>
    public bool IsLSA { get; set; }

    /// <summary>
    /// Whether to update the funding template.
    /// </summary>
    public bool UpdateTemplate { get; set; }

    /// <summary>
    /// User creating the invoice (for audit trail).
    /// </summary>
    public string CreatedBy { get; set; } = string.Empty;
}

/// <summary>
/// Request to generate an on-demand funding invoice based on peg amount logic.
/// Maps to XGenerateFundingInvoice WCF transaction.
/// </summary>
public class GenerateFundingInvoiceRequest
{
    /// <summary>
    /// Subaccount identifier to generate invoice for.
    /// </summary>
    public string SubaccountId { get; set; } = string.Empty;

    /// <summary>
    /// Invoice amount to generate.
    /// </summary>
    public decimal InvoiceAmount { get; set; }

    /// <summary>
    /// Invoice date (must be today or later).
    /// </summary>
    public DateTime InvoiceDate { get; set; } = DateTime.UtcNow;

    /// <summary>
    /// User creating the invoice (for audit trail).
    /// </summary>
    public string CreatedBy { get; set; } = string.Empty;
}

/// <summary>
/// Request to create batch funding invoices for multiple subaccounts.
/// Maps to Updater_CreateRAFundingInvoices logic.
/// </summary>
public class CreateBatchFundingInvoiceRequest
{
    /// <summary>
    /// List of employer IDs to process (empty = all employers).
    /// </summary>
    public List<string> EmployerIds { get; set; } = new();

    /// <summary>
    /// User creating the batch (for audit trail).
    /// </summary>
    public string CreatedBy { get; set; } = string.Empty;
}

/// <summary>
/// Response for funding invoice operations.
/// </summary>
public class FundingInvoiceResponse
{
    public string InvoiceId { get; set; } = string.Empty;
    public string BatchId { get; set; } = string.Empty;
    public string SubaccountId { get; set; } = string.Empty;
    public string InvoiceNumber { get; set; } = string.Empty;
    public decimal Amount { get; set; }
    public string Status { get; set; } = string.Empty;
    public string? Description { get; set; }
    public DateTime InvoiceDate { get; set; }
    public DateTime? DueDate { get; set; }
    public DateTime CreatedDate { get; set; }
    public string CreatedBy { get; set; } = string.Empty;
}

/// <summary>
/// Response for on-demand invoice generation.
/// </summary>
public class GenerateFundingInvoiceResponse
{
    /// <summary>
    /// Result status ("invoice created" or "invoice not needed").
    /// </summary>
    public string Result { get; set; } = string.Empty;

    /// <summary>
    /// Created CashInOut ID (if invoice was created).
    /// </summary>
    public string? CashInOutId { get; set; }

    /// <summary>
    /// Created invoice details (if applicable).
    /// </summary>
    public FundingInvoiceResponse? Invoice { get; set; }

    /// <summary>
    /// Payment ID (if auto-debit was triggered).
    /// </summary>
    public string? PaymentId { get; set; }
}

/// <summary>
/// Response for batch funding invoice creation.
/// </summary>
public class BatchFundingInvoiceResponse
{
    /// <summary>
    /// Total subaccounts processed.
    /// </summary>
    public int TotalProcessed { get; set; }

    /// <summary>
    /// Successfully created invoices count.
    /// </summary>
    public int SuccessCount { get; set; }

    /// <summary>
    /// Failed invoice creations count.
    /// </summary>
    public int FailureCount { get; set; }

    /// <summary>
    /// Skipped subaccounts (already processed today).
    /// </summary>
    public int SkippedCount { get; set; }

    /// <summary>
    /// Detailed results per subaccount.
    /// </summary>
    public List<SubaccountProcessingResult> Results { get; set; } = new();
}

/// <summary>
/// Individual subaccount processing result.
/// </summary>
public class SubaccountProcessingResult
{
    public string SubaccountId { get; set; } = string.Empty;
    public string EmployerId { get; set; } = string.Empty;
    public bool Success { get; set; }
    public string? ErrorMessage { get; set; }
    public string? CashInOutId { get; set; }
    public decimal? Amount { get; set; }
}
