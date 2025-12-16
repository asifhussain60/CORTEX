using System;

namespace PaymentProcessor.TransactionInvoices.Core.DTOs;

/// <summary>
/// Request to create a transaction invoice (payroll-based transaction).
/// Maps to XAddTransactionInvoice WCF transaction.
/// </summary>
public class CreateTransactionInvoiceRequest
{
    /// <summary>
    /// Employer identifier who is transaction the account.
    /// </summary>
    public string EmployerId { get; set; } = string.Empty;

    /// <summary>
    /// AccountCategory identifier to fund.
    /// </summary>
    public string AccountCategoryId { get; set; } = string.Empty;

    /// <summary>
    /// Payment plan identifier.
    /// </summary>
    public string PaymentPlanId { get; set; } = string.Empty;

    /// <summary>
    /// Employer transaction default amount (ER contribution).
    /// </summary>
    public decimal EmployerTransactionDefault { get; set; }

    /// <summary>
    /// Employee transaction default amount (EE contribution).
    /// </summary>
    public decimal EmployeeTransactionDefault { get; set; }

    /// <summary>
    /// Effective date for the transaction invoice.
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
    /// Whether to update the transaction template.
    /// </summary>
    public bool UpdateTemplate { get; set; }

    /// <summary>
    /// User creating the invoice (for audit trail).
    /// </summary>
    public string CreatedBy { get; set; } = string.Empty;
}

/// <summary>
/// Request to generate an on-demand transaction invoice based on peg amount logic.
/// Maps to XGenerateTransactionInvoice WCF transaction.
/// </summary>
public class GenerateTransactionInvoiceRequest
{
    /// <summary>
    /// AccountCategory identifier to generate invoice for.
    /// </summary>
    public string AccountCategoryId { get; set; } = string.Empty;

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
/// Request to create batch transaction invoices for multiple account_categorys.
/// Maps to Updater_CreatePaymentTransactionInvoices logic.
/// </summary>
public class CreateBatchTransactionInvoiceRequest
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
/// Response for transaction invoice operations.
/// </summary>
public class TransactionInvoiceResponse
{
    public string InvoiceId { get; set; } = string.Empty;
    public string BatchId { get; set; } = string.Empty;
    public string AccountCategoryId { get; set; } = string.Empty;
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
public class GenerateTransactionInvoiceResponse
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
    public TransactionInvoiceResponse? Invoice { get; set; }

    /// <summary>
    /// Payment ID (if auto-debit was triggered).
    /// </summary>
    public string? PaymentId { get; set; }
}

/// <summary>
/// Response for batch transaction invoice creation.
/// </summary>
public class BatchTransactionInvoiceResponse
{
    /// <summary>
    /// Total account_categorys processed.
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
    /// Skipped account_categorys (already processed today).
    /// </summary>
    public int SkippedCount { get; set; }

    /// <summary>
    /// Detailed results per account_category.
    /// </summary>
    public List<AccountCategoryProcessingResult> Results { get; set; } = new();
}

/// <summary>
/// Individual account_category processing result.
/// </summary>
public class AccountCategoryProcessingResult
{
    public string AccountCategoryId { get; set; } = string.Empty;
    public string EmployerId { get; set; } = string.Empty;
    public bool Success { get; set; }
    public string? ErrorMessage { get; set; }
    public string? CashInOutId { get; set; }
    public decimal? Amount { get; set; }
}
