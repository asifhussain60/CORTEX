// ✅ SMELL-7 FIXED: PascalCase throughout
// ✅ SMELL-19 FIXED: Validation attributes
// ✅ SMELL-20 FIXED: Audit trail

using System.ComponentModel.DataAnnotations;
using CortexLabs.FinTrack.Domain.Enums;

namespace CortexLabs.FinTrack.Domain.Entities;

/// <summary>A generated financial report.</summary>
public class Report : AuditableEntity
{
    public int Id { get; set; }

    [Required]
    [StringLength(200, MinimumLength = 1)]
    public string Title { get; set; } = string.Empty;

    [Required]
    public string Content { get; set; } = string.Empty;

    [Required]
    public int GeneratedBy { get; set; }

    public DateTime GeneratedAt { get; set; } = DateTime.UtcNow;

    /// <summary>Report type — typed enum (SMELL-15 fixed).</summary>
    [Required]
    public ReportType Type { get; set; } = ReportType.Monthly;
}
