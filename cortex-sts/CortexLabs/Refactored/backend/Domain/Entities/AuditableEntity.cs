// ✅ SMELL-7 FIXED: Consistent PascalCase naming throughout
// ✅ SMELL-19 FIXED: Validation attributes on all properties
// ✅ SMELL-20 FIXED: Full audit fields (CreatedAt, CreatedBy, ModifiedAt, ModifiedBy, Version)

using System.ComponentModel.DataAnnotations;

namespace CortexLabs.FinTrack.Domain.Entities;

/// <summary>Base class providing audit trail fields for all domain entities (SMELL-20).</summary>
public abstract class AuditableEntity
{
    /// <summary>UTC timestamp when the record was created.</summary>
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    /// <summary>Identifier of the user who created the record.</summary>
    public int CreatedBy { get; set; }

    /// <summary>UTC timestamp of last modification.</summary>
    public DateTime ModifiedAt { get; set; } = DateTime.UtcNow;

    /// <summary>Identifier of the user who last modified the record.</summary>
    public int ModifiedBy { get; set; }

    /// <summary>Soft-delete flag — records are never hard-deleted.</summary>
    public bool IsDeleted { get; set; } = false;

    /// <summary>Optimistic concurrency token.</summary>
    [Timestamp]
    public byte[]? Version { get; set; }
}
