// ✅ SMELL-7 FIXED: PascalCase throughout — no snake_case, no camelCase
// ✅ SMELL-19 FIXED: Validation attributes ([Required], [StringLength], [Range])
// ✅ SMELL-20 FIXED: Inherits AuditableEntity for full audit trail

using System.ComponentModel.DataAnnotations;
using CortexLabs.FinTrack.Domain.Enums;

namespace CortexLabs.FinTrack.Domain.Entities;

/// <summary>A single financial transaction belonging to a user.</summary>
public class Transaction : AuditableEntity
{
    public int Id { get; set; }

    [Required(ErrorMessage = "Description is required.")]
    [StringLength(500, MinimumLength = 1, ErrorMessage = "Description must be 1–500 characters.")]
    public string Description { get; set; } = string.Empty;

    [Required]
    [Range(0.01, 1_000_000, ErrorMessage = "Amount must be between 0.01 and 1,000,000.")]
    public decimal Amount { get; set; }

    /// <summary>Transaction category — typed enum, not magic string (SMELL-15 fixed).</summary>
    public TransactionCategory Category { get; set; } = TransactionCategory.Other;

    /// <summary>Income or Expense — typed enum, not magic string (SMELL-15 fixed).</summary>
    [Required]
    public TransactionType Type { get; set; }

    [Required]
    public DateOnly Date { get; set; }

    [Required]
    public int UserId { get; set; }

    // Pagination support (SMELL-6 fixed via query-side paging, retained here for clarity)
    public int? PageNumber { get; set; }
    public int? PageSize { get; set; }
}
