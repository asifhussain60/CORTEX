using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace PaymentProcessor.TransactionInvoices.Core.Entities;

/// <summary>
/// Represents a customer's payment account (account_category).
/// Maps to AccountCategory table in the database.
/// </summary>
[Table("AccountCategory")]
public class AccountCategory
{
    /// <summary>
    /// Primary key. Unique identifier for the account_category.
    /// </summary>
    [Key]
    [Column("AccountCategoryId")]
    public string AccountCategoryId { get; set; } = string.Empty;

    /// <summary>
    /// Business account number (human-readable identifier).
    /// </summary>
    [Required]
    [MaxLength(50)]
    [Column("AccountNumber")]
    public string AccountNumber { get; set; } = string.Empty;

    /// <summary>
    /// Type of account (AccountTypeA, AccountTypeB, AccountTypeC, etc.).
    /// </summary>
    [Required]
    [MaxLength(20)]
    [Column("AccountType")]
    public string AccountType { get; set; } = string.Empty;

    /// <summary>
    /// Customer ID (foreign key to Customer system - PII).
    /// </summary>
    [Required]
    [MaxLength(50)]
    [Column("CustomerId")]
    public string CustomerId { get; set; } = string.Empty;

    /// <summary>
    /// Current account balance in USD.
    /// </summary>
    [Column("Balance", TypeName = "decimal(18,2)")]
    public decimal Balance { get; set; }

    /// <summary>
    /// Account status (Active, Inactive, Suspended, Closed).
    /// </summary>
    [Required]
    [MaxLength(20)]
    [Column("Status")]
    public string Status { get; set; } = "Active";

    /// <summary>
    /// Date the account was opened.
    /// </summary>
    [Column("OpenedDate")]
    public DateTime OpenedDate { get; set; } = DateTime.UtcNow;

    /// <summary>
    /// Date the account was closed (if applicable).
    /// </summary>
    [Column("ClosedDate")]
    public DateTime? ClosedDate { get; set; }

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
    /// Collection of transaction invoices associated with this account_category.
    /// </summary>
    public virtual ICollection<TransactionInvoice> TransactionInvoices { get; set; } = new List<TransactionInvoice>();
}
