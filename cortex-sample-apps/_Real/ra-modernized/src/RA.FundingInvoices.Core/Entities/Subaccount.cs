using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace RA.FundingInvoices.Core.Entities;

/// <summary>
/// Represents a member's reimbursement account (subaccount).
/// Maps to Subaccount table in the database.
/// </summary>
[Table("Subaccount")]
public class Subaccount
{
    /// <summary>
    /// Primary key. Unique identifier for the subaccount.
    /// </summary>
    [Key]
    [Column("SubaccountId")]
    public string SubaccountId { get; set; } = string.Empty;

    /// <summary>
    /// Business account number (human-readable identifier).
    /// </summary>
    [Required]
    [MaxLength(50)]
    [Column("AccountNumber")]
    public string AccountNumber { get; set; } = string.Empty;

    /// <summary>
    /// Type of account (HSA, FSA, HRA, etc.).
    /// </summary>
    [Required]
    [MaxLength(20)]
    [Column("AccountType")]
    public string AccountType { get; set; } = string.Empty;

    /// <summary>
    /// Member ID (foreign key to Member system - PHI).
    /// </summary>
    [Required]
    [MaxLength(50)]
    [Column("MemberId")]
    public string MemberId { get; set; } = string.Empty;

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
    /// Collection of funding invoices associated with this subaccount.
    /// </summary>
    public virtual ICollection<FundingInvoice> FundingInvoices { get; set; } = new List<FundingInvoice>();
}
