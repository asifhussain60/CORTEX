using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace RA.FundingInvoices.Core.Entities;

/// <summary>
/// Represents a cash in/out transaction for funding batches.
/// Maps to CashInOut table in the database.
/// </summary>
[Table("CashInOut")]
public class CashInOut
{
    /// <summary>
    /// Primary key. Unique identifier for the transaction.
    /// </summary>
    [Key]
    [Column("TransactionId")]
    public string TransactionId { get; set; } = string.Empty;

    /// <summary>
    /// Foreign key to FundingBatch. The batch this transaction is associated with.
    /// </summary>
    [Required]
    [Column("BatchId")]
    public string BatchId { get; set; } = string.Empty;

    /// <summary>
    /// Transaction type (CashIn, CashOut, Adjustment, Reversal).
    /// </summary>
    [Required]
    [MaxLength(20)]
    [Column("TransactionType")]
    public string TransactionType { get; set; } = string.Empty;

    /// <summary>
    /// Transaction amount in USD (positive for CashIn, negative for CashOut).
    /// </summary>
    [Column("Amount", TypeName = "decimal(18,2)")]
    public decimal Amount { get; set; }

    /// <summary>
    /// Date/time the transaction was processed.
    /// </summary>
    [Column("TransactionDate")]
    public DateTime TransactionDate { get; set; } = DateTime.UtcNow;

    /// <summary>
    /// Transaction status (Pending, Completed, Failed, Reversed).
    /// </summary>
    [Required]
    [MaxLength(20)]
    [Column("Status")]
    public string Status { get; set; } = "Pending";

    /// <summary>
    /// Optional reference number (check number, wire transfer ID, etc.).
    /// </summary>
    [MaxLength(100)]
    [Column("ReferenceNumber")]
    public string? ReferenceNumber { get; set; }

    /// <summary>
    /// Optional description or notes for the transaction.
    /// </summary>
    [MaxLength(500)]
    [Column("Description")]
    public string? Description { get; set; }

    /// <summary>
    /// HIPAA audit field: User who created the record.
    /// </summary>
    [Required]
    [MaxLength(100)]
    [Column("CreatedBy")]
    public string CreatedBy { get; set; } = string.Empty;

    /// <summary>
    /// HIPAA audit field: Timestamp when record was created.
    /// </summary>
    [Column("CreatedDate")]
    public DateTime CreatedDate { get; set; } = DateTime.UtcNow;

    /// <summary>
    /// HIPAA audit field: User who last modified the record.
    /// </summary>
    [MaxLength(100)]
    [Column("ModifiedBy")]
    public string? ModifiedBy { get; set; }

    /// <summary>
    /// HIPAA audit field: Timestamp when record was last modified.
    /// </summary>
    [Column("ModifiedDate")]
    public DateTime? ModifiedDate { get; set; }

    // Navigation properties
    /// <summary>
    /// Navigation property to the associated funding batch.
    /// </summary>
    public virtual FundingBatch? FundingBatch { get; set; }
}
