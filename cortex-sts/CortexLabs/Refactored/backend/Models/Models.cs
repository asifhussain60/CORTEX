// ✅ CORTEX Refactored — Domain Models
// ✅ SMELL-7 RESOLVED: Consistent PascalCase naming
// ✅ SMELL-19 RESOLVED: Validation attributes added
// ✅ SMELL-20 RESOLVED: Audit fields added

using System.ComponentModel.DataAnnotations;

namespace CortexLabs.FinTrack.Models;

/// <summary>
/// Transaction entity with proper validation and audit fields
/// </summary>
public class Transaction
{
    public int Id { get; set; }

    [Required]
    [StringLength(500, MinimumLength = 1)]
    public string Description { get; set; } = string.Empty;  // ✅ SMELL-7: PascalCase

    [Range(0.01, 10_000_000)]
    public decimal Amount { get; set; }

    [Required]
    [StringLength(100)]
    public string Category { get; set; } = string.Empty;  // ✅ SMELL-7: PascalCase

    [Required]
    [RegularExpression("^(income|expense)$", ErrorMessage = "Type must be 'income' or 'expense'")]
    public string Type { get; set; } = string.Empty;

    public DateTime Date { get; set; }

    [Required]
    public int UserId { get; set; }

    // ✅ SMELL-20 RESOLVED: Audit fields
    public DateTime CreatedAt { get; set; }
    public DateTime? ModifiedAt { get; set; }
    public string? CreatedBy { get; set; }
    public string? ModifiedBy { get; set; }
    public bool IsDeleted { get; set; } = false;
}

/// <summary>
/// User entity with proper validation
/// </summary>
public class User
{
    public int Id { get; set; }

    [Required]
    [StringLength(50, MinimumLength = 3)]
    public string UserName { get; set; } = string.Empty;  // ✅ SMELL-7: PascalCase

    [Required]
    [EmailAddress]
    [StringLength(100, MinimumLength = 5)]
    public string Email { get; set; } = string.Empty;

    [Required]
    public string PasswordHash { get; set; } = string.Empty;  // ✅ SMELL-7: PascalCase

    [Required]
    [RegularExpression("^(user|admin|moderator)$")]
    public string Role { get; set; } = "user";

    public bool IsActive { get; set; } = true;  // ✅ SMELL-7: PascalCase

    // ✅ SMELL-20 RESOLVED: Audit fields
    public DateTime CreatedAt { get; set; }
    public DateTime? ModifiedAt { get; set; }
    public DateTime? LastLoginAt { get; set; }
}

/// <summary>
/// Account entity
/// </summary>
public class Account
{
    public int Id { get; set; }

    [Required]
    [StringLength(100)]
    public string Name { get; set; } = string.Empty;  // ✅ SMELL-7: PascalCase

    [Range(0, double.MaxValue)]
    public decimal Balance { get; set; }

    [Required]
    public int UserId { get; set; }  // ✅ SMELL-7: PascalCase

    [Required]
    [RegularExpression("^(checking|savings|investment)$")]
    public string AccountType { get; set; } = string.Empty;  // ✅ SMELL-7: PascalCase

    // ✅ SMELL-20 RESOLVED: Audit fields
    public DateTime CreatedAt { get; set; }
    public DateTime? ModifiedAt { get; set; }
    public int Version { get; set; } = 1;  // Optimistic concurrency
}

/// <summary>
/// Report entity
/// </summary>
public class Report
{
    public int Id { get; set; }

    [Required]
    [StringLength(200)]
    public string Title { get; set; } = string.Empty;  // ✅ SMELL-7: PascalCase

    public string Content { get; set; } = string.Empty;

    public int GeneratedBy { get; set; }  // ✅ SMELL-7: PascalCase

    public DateTime GeneratedAt { get; set; }  // ✅ SMELL-7: PascalCase
}

// ✅ SMELL-16 RESOLVED: Removed global mutable AppCache — use DI-scoped services instead
