using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace RA.FundingInvoices.Core.Entities;

/// <summary>
/// Represents a batch of funding invoices processed together.
/// Maps to FundingBatch table in the database.
/// </summary>
[Table("FundingBatch")]
public class FundingBatch
{
    /// <summary>
    /// Primary key. Unique identifier for the funding batch.
    /// </summary>
    [Key]
    [Column("BatchId")]
    public string BatchId { get; set; } = string.Empty;

    /// <summary>
    /// Business batch number (human-readable identifier).
    /// </summary>
    [Required]
    [MaxLength(50)]
    [Column("BatchNumber")]
    public string BatchNumber { get; set; } = string.Empty;

    /// <summary>
    /// Date the batch was created/processed.
    /// </summary>
    [Column("BatchDate")]
    public DateTime BatchDate { get; set; } = DateTime.UtcNow;

    /// <summary>
    /// Batch status (Open, Closed, Pending, Completed).
    /// </summary>
    [Required]
    [MaxLength(20)]
    [Column("Status")]
    public string Status { get; set; } = "Open";

    /// <summary>
    /// Total amount for all invoices in this batch.
    /// </summary>
    [Column("TotalAmount", TypeName = "decimal(18,2)")]
    public decimal TotalAmount { get; set; }

    /// <summary>
    /// Number of invoices in this batch.
    /// </summary>
    [Column("InvoiceCount")]
    public int InvoiceCount { get; set; }

    /// <summary>
    /// Optional description or notes for the batch.
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
    /// Collection of funding invoices in this batch.
    /// </summary>
    public virtual ICollection<FundingInvoice> FundingInvoices { get; set; } = new List<FundingInvoice>();

    /// <summary>
    /// Collection of cash in/out transactions associated with this batch.
    /// </summary>
    public virtual ICollection<CashInOut> CashTransactions { get; set; } = new List<CashInOut>();
}
