// FIX SMELL-7 SMELL-20
namespace CortexLabs.FinTrack.Domain.Entities;
public class Report {
    public int Id { get; set; }
    public string Title { get; set; } = string.Empty;
    public string Content { get; set; } = string.Empty;
    public int GeneratedBy { get; set; }
    public DateTime GeneratedAt { get; set; } = DateTime.UtcNow;
    public ReportType ReportType { get; set; }
}
public enum ReportType { Monthly, Annual, Tax }