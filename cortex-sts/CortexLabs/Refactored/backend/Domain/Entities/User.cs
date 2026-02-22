// ✅ SMELL-7 FIXED: PascalCase throughout
// ✅ SMELL-19 FIXED: Validation attributes
// ✅ SMELL-20 FIXED: Audit trail

using System.ComponentModel.DataAnnotations;

namespace CortexLabs.FinTrack.Domain.Entities;

/// <summary>A user of the FinTrack application.</summary>
public class User : AuditableEntity
{
    public int Id { get; set; }

    [Required]
    [StringLength(50, MinimumLength = 3)]
    public string UserName { get; set; } = string.Empty;

    [Required]
    [EmailAddress]
    [StringLength(200, MinimumLength = 5)]
    public string Email { get; set; } = string.Empty;

    /// <summary>BCrypt hash of the user password — NEVER plaintext (SMELL-2 fixed).</summary>
    [Required]
    public string PasswordHash { get; set; } = string.Empty;

    [Required]
    [StringLength(20)]
    public string Role { get; set; } = "user";

    public bool IsActive { get; set; } = true;
}
