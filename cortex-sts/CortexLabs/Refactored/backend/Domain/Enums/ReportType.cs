// ✅ SMELL-15 FIXED: Magic strings replaced with enum
namespace CortexLabs.FinTrack.Domain.Enums;

/// <summary>Report type supported by the reporting service.</summary>
public enum ReportType
{
    Monthly,
    Annual,
    Tax,
    Custom
}
