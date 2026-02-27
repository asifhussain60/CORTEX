// FIX SMELL-7 SMELL-15 SMELL-19 SMELL-20
using System.ComponentModel.DataAnnotations;
namespace CortexLabs.FinTrack.Domain.Entities;
public class Transaction {
    public int Id { get; set; }
    [Required, MaxLength(500)] public string Description { get; set; } = string.Empty;
    [Range(0.01, double.MaxValue)] public decimal Amount { get; set; }
    [MaxLength(100)] public string CategoryName { get; set; } = string.Empty;
    public TransactionType Type { get; set; }
    public DateTime Date { get; set; }
    public int UserId { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime ModifiedAt { get; set; } = DateTime.UtcNow;
    public bool IsDeleted { get; set; }
}
public enum TransactionType { Income, Expense, Transfer }