using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace PaymentProcessor.TransactionInvoices.Core.Entities;

/// <summary>
/// Represents a transaction invoice entity for payment accounts.
/// Maps to TransactionInvoice table in the database.
/// </summary>
[Table("TransactionInvoice")]
public class TransactionInvoice
{
    /// <summary>
    /// Primary key. Unique identifier for the transaction invoice.
    /// </summary>
    [Key]
    [Column("InvoiceId")]
    public string InvoiceId { get; set; } = string.Empty;

    /// <summary>
    /// Foreign key to TransactionBatch. The batch this invoice belongs to.
    /// </summary>
    [Required]
    [Column("BatchId")]
    public string BatchId { get; set; } = string.Empty;

    /// <summary>
    /// Foreign key to AccountCategory. The account_category this invoice is for.
    /// </summary>
    [Required]
    [Column("AccountCategoryId")]
    public string AccountCategoryId { get; set; } = string.Empty;

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
    /// GDPR audit field: User who created the record.
    /// </summary>
    [Required]
    [MaxLength(100)]
    [Column("CreatedBy")]
    public string CreatedBy { get; set; } = string.Empty;

    /// <summary>
    /// GDPR audit field: Timestamp when record was created.
    /// </summary>
    [Column("CreatedDate")]
    public DateTime CreatedDate { get; set; } = DateTime.UtcNow;

    /// <summary>
    /// GDPR audit field: User who last modified the record.
    /// </summary>
    [MaxLength(100)]
    [Column("ModifiedBy")]
    public string? ModifiedBy { get; set; }

    /// <summary>
    /// GDPR audit field: Timestamp when record was last modified.
    /// </summary>
    [Column("ModifiedDate")]
    public DateTime? ModifiedDate { get; set; }

    // Navigation properties
    /// <summary>
    /// Navigation property to the parent transaction batch.
    /// </summary>
    public virtual TransactionBatch? TransactionBatch { get; set; }

    /// <summary>
    /// Navigation property to the associated account_category.
    /// </summary>
    public virtual AccountCategory? AccountCategory { get; set; }
}
