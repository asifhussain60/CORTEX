using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace RA.FundingInvoices.Core.Entities;

/// <summary>
/// Represents a funding invoice entity for reimbursement accounts.
/// Maps to FundingInvoice table in the database.
/// </summary>
[Table("FundingInvoice")]
public class FundingInvoice
{
    /// <summary>
    /// Primary key. Unique identifier for the funding invoice.
    /// </summary>
    [Key]
    [Column("InvoiceId")]
    public string InvoiceId { get; set; } = string.Empty;

    /// <summary>
    /// Foreign key to FundingBatch. The batch this invoice belongs to.
    /// </summary>
    [Required]
    [Column("BatchId")]
    public string BatchId { get; set; } = string.Empty;

    /// <summary>
    /// Foreign key to Subaccount. The subaccount this invoice is for.
    /// </summary>
    [Required]
    [Column("SubaccountId")]
    public string SubaccountId { get; set; } = string.Empty;

    /// <summary>
    /// Business invoice number (human-readable identifier).
    /// </summary>
    [Required]
    [MaxLength(50)]
    [Column("InvoiceNumber")]
    public string InvoiceNumber { get; set; } = string.Empty;

    /// <summary>
    /// Invoice amount in USD.
    /// </summary>
    [Column("Amount", TypeName = "decimal(18,2)")]
    public decimal Amount { get; set; }

    /// <summary>
    /// Invoice status (Pending, Approved, Rejected, Paid).
    /// </summary>
    [Required]
    [MaxLength(20)]
    [Column("Status")]
    public string Status { get; set; } = "Pending";

    /// <summary>
    /// Optional description or notes for the invoice.
    /// </summary>
    [MaxLength(500)]
    [Column("Description")]
    public string? Description { get; set; }

    /// <summary>
    /// Date the invoice was issued.
    /// </summary>
    [Column("InvoiceDate")]
    public DateTime InvoiceDate { get; set; } = DateTime.UtcNow;

    /// <summary>
    /// Date the invoice is due for payment.
    /// </summary>
    [Column("DueDate")]
    public DateTime? DueDate { get; set; }

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
    /// Navigation property to the parent funding batch.
    /// </summary>
    public virtual FundingBatch? FundingBatch { get; set; }

    /// <summary>
    /// Navigation property to the associated subaccount.
    /// </summary>
    public virtual Subaccount? Subaccount { get; set; }
}
