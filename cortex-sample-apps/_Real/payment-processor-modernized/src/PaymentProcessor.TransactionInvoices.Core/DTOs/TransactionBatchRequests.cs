using System;

namespace PaymentProcessor.TransactionInvoices.Core.DTOs;

/// <summary>
/// Request to close a transaction batch and create replenishment invoice.
/// Maps to XCloseTransactionBatch WCF transaction.
/// </summary>
public class CloseTransactionBatchRequest
{
    /// <summary>
    /// Transaction batch identifier to close.
    /// </summary>
    public string BatchId { get; set; } = string.Empty;

    /// <summary>
    /// List of transaction batch invoice IDs to exclude from closure.
    /// </summary>
    public List<string> ExcludedInvoiceIds { get; set; } = new();

    /// <summary>
    /// User closing the batch (for audit trail).
    /// </summary>
    public string ClosedBy { get; set; } = string.Empty;
}

/// <summary>
/// Request to reopen a closed or pending transaction batch.
/// Maps to XReopenTransactionBatch WCF transaction.
/// </summary>
public class ReopenTransactionBatchRequest
{
    /// <summary>
    /// Transaction batch identifier to reopen.
    /// </summary>
    public string BatchId { get; set; } = string.Empty;

    /// <summary>
    /// User reopening the batch (for audit trail).
    /// </summary>
    public string ReopenedBy { get; set; } = string.Empty;
}

/// <summary>
/// Request to update transaction batch metadata.
/// Maps to XUpdateTransactionBatch WCF transaction.
/// </summary>
public class UpdateTransactionBatchRequest
{
    /// <summary>
    /// Transaction batch identifier to update.
    /// </summary>
    public string BatchId { get; set; } = string.Empty;

    /// <summary>
    /// New batch status (Open, Pending, Closed, Reopened).
    /// </summary>
    public string? Status { get; set; }

    /// <summary>
    /// New batch description.
    /// </summary>
    public string? Description { get; set; }

    /// <summary>
    /// Associated CashInOut reference (set during closure).
    /// </summary>
    public string? TransactionCashInOutRef { get; set; }

    /// <summary>
    /// User updating the batch (for audit trail).
    /// </summary>
    public string ModifiedBy { get; set; } = string.Empty;
}

/// <summary>
/// Request to create a new transaction batch.
/// </summary>
public class CreateTransactionBatchRequest
{
    /// <summary>
    /// AccountCategory identifier for the batch.
    /// </summary>
    public string AccountCategoryId { get; set; } = string.Empty;

    /// <summary>
    /// Initial batch status (defaults to Open).
    /// </summary>
    public string Status { get; set; } = "Open";

    /// <summary>
    /// Batch description.
    /// </summary>
    public string? Description { get; set; }

    /// <summary>
    /// User creating the batch (for audit trail).
    /// </summary>
    public string CreatedBy { get; set; } = string.Empty;
}

/// <summary>
/// Response for batch closure operation.
/// </summary>
public class CloseTransactionBatchResponse
{
    /// <summary>
    /// Closed batch details.
    /// </summary>
    public TransactionBatchResponse Batch { get; set; } = new();

    /// <summary>
    /// Created CashInOut ID.
    /// </summary>
    public string CashInOutId { get; set; } = string.Empty;

    /// <summary>
    /// CashInOut amount (replenishment invoice amount).
    /// </summary>
    public decimal CashInOutAmount { get; set; }

    /// <summary>
    /// Payment ID (if auto-debit was triggered).
    /// </summary>
    public string? PaymentId { get; set; }

    /// <summary>
    /// Whether auto-debit was processed.
    /// </summary>
    public bool AutoDebitProcessed { get; set; }
}

/// <summary>
/// Response for transaction batch operations.
/// </summary>
public class TransactionBatchResponse
{
    public string BatchId { get; set; } = string.Empty;
    public string AccountCategoryId { get; set; } = string.Empty;
    public string Status { get; set; } = string.Empty;
    public string? Description { get; set; }
    public string? TransactionCashInOutId { get; set; }
    public DateTime CreatedDate { get; set; }
    public string CreatedBy { get; set; } = string.Empty;
    public DateTime? ModifiedDate { get; set; }
    public string? ModifiedBy { get; set; }

    /// <summary>
    /// Number of invoices in this batch.
    /// </summary>
    public int InvoiceCount { get; set; }

    /// <summary>
    /// Total amount of all invoices in batch.
    /// </summary>
    public decimal TotalAmount { get; set; }
}
