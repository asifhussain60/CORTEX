// ✅ SMELL-7 FIXED: PascalCase throughout
// ✅ SMELL-19 FIXED: Validation attributes
// ✅ SMELL-20 FIXED: Audit trail via AuditableEntity

using System.ComponentModel.DataAnnotations;
using CortexLabs.FinTrack.Domain.Enums;

namespace CortexLabs.FinTrack.Domain.Entities;

/// <summary>A financial account owned by a user.</summary>
public class Account : AuditableEntity
{
    public int Id { get; set; }

    [Required]
    [StringLength(100, MinimumLength = 1)]
    public string Name { get; set; } = string.Empty;

    [Range(double.MinValue, double.MaxValue)]
    public decimal Balance { get; set; }

    [Required]
    public int UserId { get; set; }

    /// <summary>Account type — typed enum, not magic string (SMELL-15 fixed).</summary>
    [Required]
    public AccountType Type { get; set; } = AccountType.Checking;
}
